from sqlalchemy.orm import Session
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from core.prompts import STORY_PROMPT
from models.story import Story, StoryNode
from core.models import StoryLLMResponse, StoryNodeLLM


class StoryGenerator:
    @classmethod
    def _get_llm(cls):
        return ChatOpenAI(model="gpt-4-turbo")

    @classmethod
    def generate_story(cls, db: Session, session_id: str, theme: str = "fantasy") -> Story:
        llm = cls._get_llm()
        story_parser = PydanticOutputParser(pydantic_object=StoryLLMResponse)

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", STORY_PROMPT),
                ("human", "Create the story with this theme: {theme}"),
            ]
        ).partial(format_instructions=story_parser.get_format_instructions())

        prompt_value = prompt.invoke({"theme": theme})

        raw_response = llm.invoke(prompt_value)
        response_text = raw_response.content if hasattr(raw_response, "content") else str(raw_response)

        story_structure: StoryLLMResponse = story_parser.parse(response_text)

        story_db = Story(title=story_structure.title, session_id=session_id)
        db.add(story_db)
        db.flush()  

        root_node_data = story_structure.rootNode
        if isinstance(root_node_data, dict):
            root_node_data = StoryNodeLLM.model_validate(root_node_data)

        cls._process_story_node(db, story_db.id, root_node_data, is_root=True)

        db.commit()
        db.refresh(story_db)
        return story_db

    @classmethod
    def _process_story_node(
        cls,
        db: Session,
        story_id: int,
        node_data: StoryNodeLLM,
        is_root: bool = False,
    ) -> StoryNode:
        node = StoryNode(
            story_id=story_id,
            content=node_data.content,
            is_root=is_root,
            is_ending=node_data.isEnding,
            is_winning_ending=node_data.isWinningEnding,
            options=[],  
        )
        db.add(node)
        db.flush()  

        if (not node.is_ending) and node_data.options:
            options_list = []

            for option_data in node_data.options:
                next_node_data = option_data.nextNode
                if isinstance(next_node_data, dict):
                    next_node_data = StoryNodeLLM.model_validate(next_node_data)

                child_node = cls._process_story_node(db, story_id, next_node_data, is_root=False)

                options_list.append(
                    {
                        "text": option_data.text,
                        "node_id": child_node.id,
                    }
                )

            node.options = options_list
            db.flush()

        return node

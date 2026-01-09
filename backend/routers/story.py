import uuid
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Cookie, Response, BackgroundTasks
from sqlalchemy.orm import Session

from db.database import get_db, SessionLocal
from models.story import Story, StoryNode
from models.job import StoryJob
from schemas.story import (
    CompleteStoryResponse,
    CompleteStoryNodeResponse,
    CreateStoryRequest,
)
from schemas.job import StoryJobResponse
from core.story_generator import StoryGenerator


router = APIRouter(prefix="/stories", tags=["stories"])


def get_session_id(session_id: Optional[str] = Cookie(None)) -> str:
    return session_id or str(uuid.uuid4())


@router.post("/create", response_model=StoryJobResponse)
def create_story(
    request: CreateStoryRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db),
):
    """
    Creates a StoryJob immediately (so polling /jobs/{job_id} won't 404),
    then runs the heavy story generation in a background task.
    """
    response.set_cookie(key="session_id", value=session_id, httponly=True)

    job_id = str(uuid.uuid4())

    job = StoryJob(
        job_id=job_id,
        session_id=session_id,
        theme=request.theme,
        status="processing",
        created_at=datetime.now() if hasattr(StoryJob, "created_at") else None,  # safe if column doesn't exist
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(generate_story_task, job_id, request.theme, session_id)

    return job


def generate_story_task(job_id: str, theme: str, session_id: str) -> None:
    """
    Background task:
    - Opens its own SessionLocal (never use the request session in BackgroundTasks)
    - Generates and persists the story
    - Updates the job with story_id + completed status
    """
    db = SessionLocal()
    try:
        job = db.query(StoryJob).filter(StoryJob.job_id == job_id).first()
        if not job:
            return

        try:
            job.status = "processing"
            db.commit()

            story = StoryGenerator.generate_story(db, session_id, theme)

            
            db.flush()
            db.commit()
            db.refresh(story)

            if not getattr(story, "id", None):
                raise Exception("Story was generated but has no id. Commit/refresh failed.")

            job.story_id = story.id
            job.status = "completed"
            job.completed_at = datetime.now()
            job.error = None
            db.commit()

        except Exception as e:
            job.status = "failed"
            job.completed_at = datetime.now()
            job.error = str(e)
            db.commit()

    finally:
        db.close()


@router.get("/{story_id}/complete", response_model=CompleteStoryResponse)
def get_complete_story(story_id: int, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    return build_complete_story_response(db, story)


def build_complete_story_response(db: Session, story: Story) -> CompleteStoryResponse:
    nodes = db.query(StoryNode).filter(StoryNode.story_id == story.id).all()

    node_dict: dict[int, CompleteStoryNodeResponse] = {}
    for node in nodes:
        node_dict[node.id] = CompleteStoryNodeResponse(
            id=node.id,
            content=node.content,
            is_ending=node.is_ending,
            is_winning_ending=node.is_winning_ending,
            options=node.options or [],
        )

    root_node = next((n for n in nodes if getattr(n, "is_root", False)), None)
    if not root_node:
        raise HTTPException(status_code=500, detail="Story root node not found")

    return CompleteStoryResponse(
        id=story.id,
        title=story.title,
        session_id=story.session_id,
        created_at=story.created_at,
        root_node=node_dict[root_node.id],
        all_nodes=node_dict,
    )

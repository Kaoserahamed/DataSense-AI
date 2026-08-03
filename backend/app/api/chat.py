from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

from app.database.connection import get_db
from app.repositories.dataset_repository import DatasetRepository
from app.services.dataset_service import DatasetService
from app.services.chat_service import ChatService
from app.models.chat import ChatHistory

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat with Data"])


class ChatRequest(BaseModel):
    dataset_id: int
    question: str
    save_history: bool = True


class ChatResponse(BaseModel):
    answer: str
    code: Optional[str] = None
    result: Optional[Any] = None
    result_type: Optional[str] = None
    chart_config: Optional[Dict[str, Any]] = None
    visualization: Optional[Dict[str, Any]] = None
    transformation_action: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ChatHistoryResponse(BaseModel):
    id: int
    dataset_id: int
    question: str
    answer: str
    code: Optional[str]
    created_at: str


@router.post("/ask", response_model=ChatResponse)
def ask_question(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Ask a natural language question about a dataset
    """
    try:
        # Get dataset
        dataset_repo = DatasetRepository(db)
        dataset = dataset_repo.get_by_id(request.dataset_id)
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        # Load dataframe
        df = DatasetService.load_dataframe(dataset.file_path, dataset.file_type)
        
        # Process question
        result = ChatService.chat_with_data(
            df=df,
            question=request.question,
            dataset_name=dataset.name,
            dataset_id=request.dataset_id
        )
        
        # Save to history if requested
        if request.save_history and not result.get("error"):
            try:
                history = ChatHistory(
                    dataset_id=request.dataset_id,
                    question=request.question,
                    answer=result.get("answer", ""),
                    code=result.get("code")
                )
                db.add(history)
                db.commit()
            except Exception as history_error:
                db.rollback()
                logger.warning(
                    f"Chat history save failed: {str(history_error)}",
                    exc_info=True,
                )
        
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing chat question: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/history/{dataset_id}", response_model=List[ChatHistoryResponse])
def get_chat_history(dataset_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """
    Get chat history for a dataset (ordered oldest to newest)
    """
    try:
        history = db.query(ChatHistory)\
            .filter(ChatHistory.dataset_id == dataset_id)\
            .order_by(ChatHistory.created_at.asc())\
            .limit(limit)\
            .all()
        
        return [
            ChatHistoryResponse(
                id=h.id,
                dataset_id=h.dataset_id,
                question=h.question,
                answer=h.answer,
                code=h.code,
                created_at=h.created_at.isoformat()
            )
            for h in history
        ]
        
    except Exception as e:
        logger.error(f"Error fetching chat history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/history/{chat_id}")
def delete_chat_history(chat_id: int, db: Session = Depends(get_db)):
    """
    Delete a chat history item
    """
    try:
        history = db.query(ChatHistory).filter(ChatHistory.id == chat_id).first()
        
        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat history not found"
            )
        
        db.delete(history)
        db.commit()
        
        return {"message": "Chat history deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

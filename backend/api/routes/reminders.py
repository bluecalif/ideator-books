"""Reminders API - 복습 큐 관리"""
from fastapi import APIRouter, HTTPException, Depends, status
from backend.core.database import get_supabase_admin
from backend.models.schemas import ReminderToggle, ReminderResponse
from supabase import Client
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/reminders", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def toggle_reminder(
    reminder_data: ReminderToggle,
    supabase: Client = Depends(get_supabase_admin)
):
    """
    Reminder on/off 토글
    
    - artifact_id와 user_id로 unique constraint
    - active=True: reminder 생성 또는 활성화
    - active=False: reminder 비활성화
    
    **참고**: 현재 user_id는 임시 UUID 사용 (Phase 2.4 인증 구현 후 실제 사용자로 변경)
    """
    try:
        # Artifact 존재 확인
        artifact_result = supabase.table("artifacts") \
            .select("id") \
            .eq("id", reminder_data.artifact_id) \
            .execute()
        
        if not artifact_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artifact {reminder_data.artifact_id}를 찾을 수 없습니다"
            )
        
        # 임시 user_id (TODO: Phase 2.4에서 실제 인증 구현)
        temp_user_id = "00000000-0000-0000-0000-000000000001"
        
        # 기존 Reminder 확인
        existing_result = supabase.table("reminders") \
            .select("*") \
            .eq("user_id", temp_user_id) \
            .eq("artifact_id", reminder_data.artifact_id) \
            .execute()
        
        if existing_result.data:
            # 기존 reminder 업데이트
            reminder = existing_result.data[0]
            update_result = supabase.table("reminders") \
                .update({"active": reminder_data.active}) \
                .eq("id", reminder["id"]) \
                .execute()
            
            if not update_result.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Reminder 업데이트 실패"
                )
            
            reminder = update_result.data[0]
            logger.info(f"[REMINDER] Updated reminder {reminder['id']} active={reminder_data.active}")
        
        else:
            # 새 reminder 생성
            if not reminder_data.active:
                # active=False로 생성 요청은 무시
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Reminder가 존재하지 않습니다. active=True로 먼저 생성해주세요"
                )
            
            create_result = supabase.table("reminders").insert({
                "user_id": temp_user_id,
                "artifact_id": reminder_data.artifact_id,
                "active": True,
                "schedule": None  # TODO: 스케줄링 로직 추가
            }).execute()
            
            if not create_result.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Reminder 생성 실패"
                )
            
            reminder = create_result.data[0]
            logger.info(f"[REMINDER] Created reminder {reminder['id']} for artifact {reminder_data.artifact_id}")
        
        return ReminderResponse(
            id=reminder["id"],
            user_id=reminder["user_id"],
            artifact_id=reminder["artifact_id"],
            schedule=reminder.get("schedule"),
            active=reminder["active"],
            created_at=reminder["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR] Failed to toggle reminder: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reminder 토글 실패: {str(e)}"
        )


"""Authentication and Authorization"""
from fastapi import HTTPException, status, Header, Depends
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def verify_supabase_token(token: str) -> dict:
    """
    Supabase JWT 토큰 검증
    
    Args:
        token: JWT 토큰 (Bearer 제거된 상태)
    
    Returns:
        dict: 사용자 정보 {user_id, email}
    
    Raises:
        HTTPException: 토큰이 유효하지 않은 경우
    
    TODO: Phase 3에서 Supabase Auth와 통합하여 실제 검증 구현
    """
    try:
        # TODO: Supabase Auth SDK로 실제 토큰 검증
        # from supabase import create_client
        # supabase = create_client(url, key)
        # user = supabase.auth.get_user(token)
        
        # 현재는 Skeleton 구현 (임시)
        logger.warning("[AUTH] Token verification not implemented yet (using test user)")
        
        # 임시: 토큰이 있으면 테스트 사용자 반환
        if token and len(token) > 10:
            return {
                "user_id": "00000000-0000-0000-0000-000000000001",
                "email": "test@ideator-books.dev"
            }
        else:
            raise ValueError("Invalid token format")
        
    except Exception as e:
        logger.error(f"[AUTH] Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(authorization: str = Header(None)) -> str:
    """
    현재 사용자 ID 추출 (FastAPI Dependency)
    
    Args:
        authorization: Authorization 헤더 (Bearer {token})
    
    Returns:
        str: 사용자 ID (UUID)
    
    Raises:
        HTTPException: 인증 실패 시
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Bearer 접두사 제거
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format (must be 'Bearer <token>')",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.replace("Bearer ", "")
    
    # 토큰 검증
    user_info = verify_supabase_token(token)
    
    return user_info["user_id"]


async def require_auth(user_id: str = Depends(get_current_user)) -> str:
    """
    인증 필수 Dependency (비동기)
    
    사용법:
        @router.get("/protected")
        async def protected_route(user_id: str = Depends(require_auth)):
            # user_id를 사용하여 사용자 데이터 처리
            pass
    
    Args:
        user_id: get_current_user에서 추출된 사용자 ID
    
    Returns:
        str: 사용자 ID
    """
    return user_id


def get_optional_user(authorization: str = Header(None)) -> Optional[str]:
    """
    선택적 인증 (토큰이 있으면 검증, 없으면 None 반환)
    
    Args:
        authorization: Authorization 헤더
    
    Returns:
        Optional[str]: 사용자 ID 또는 None
    """
    if not authorization:
        return None
    
    try:
        if authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
            user_info = verify_supabase_token(token)
            return user_info["user_id"]
        else:
            return None
    except HTTPException:
        # 인증 실패 시 None 반환 (에러 발생시키지 않음)
        return None


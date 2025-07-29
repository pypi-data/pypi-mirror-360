"""Session management for WebSocket connections."""

import uuid
import logging
import jwt
from typing import Dict, Optional, Set, Any
from dataclasses import dataclass
from datetime import datetime

from client.conversation import ConversationManager
from tallyfy.core import TallyfySDK
from tallyfy.models import TallyfyError

logger = logging.getLogger(__name__)


@dataclass
class UserSession:
    """Represents a user session with conversation history and credentials."""
    session_id: str
    user_id: Optional[str]
    conversation: ConversationManager
    created_at: datetime
    last_activity: datetime
    api_key: Optional[str] = None
    org_id: Optional[str] = None
    
    def update_activity(self) -> None:
        """Update the last activity timestamp."""
        self.last_activity = datetime.now()
    
    def has_credentials(self) -> bool:
        """Check if session has valid credentials."""
        return bool(self.api_key and self.org_id)
    
    def get_credentials(self) -> Dict[str, str]:
        """Get credentials as dictionary."""
        return {
            "api_key": self.api_key or "",
            "org_id": self.org_id or "",
            "user_id": self.user_id or ""
        }


class SessionManager:
    """Manages user sessions for WebSocket connections."""
    
    def __init__(self):
        self._sessions: Dict[str, UserSession] = {}
        self._active_connections: Set[str] = set()
    
    def _extract_user_id_from_jwt(self, api_key: str) -> Optional[str]:
        """Extract user ID from JWT token without verification."""
        try:
            # Decode JWT without verification (since we're just extracting the payload)
            decoded = jwt.decode(api_key, options={"verify_signature": False})
            return decoded.get("sub")
        except Exception as e:
            logger.warning(f"Failed to extract user ID from JWT: {str(e)}")
            return None
    
    def create_session(self, user_id: Optional[str] = None) -> str:
        """Create a new user session and return session ID."""
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        session = UserSession(
            session_id=session_id,
            user_id=user_id,
            conversation=ConversationManager(),
            created_at=now,
            last_activity=now
        )
        
        self._sessions[session_id] = session
        self._active_connections.add(session_id)
        
        logger.info(f"Created new session: {session_id} for user: {user_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get a session by ID."""
        session = self._sessions.get(session_id)
        if session:
            session.update_activity()
        return session
    
    def remove_session(self, session_id: str) -> bool:
        """Remove a session by ID."""
        if session_id in self._sessions:
            session = self._sessions.pop(session_id)
            self._active_connections.discard(session_id)
            logger.info(f"Removed session: {session_id} for user: {session.user_id}")
            return True
        return False
    
    def get_conversation(self, session_id: str) -> Optional[ConversationManager]:
        """Get conversation manager for a session."""
        session = self.get_session(session_id)
        return session.conversation if session else None
    
    def clear_conversation(self, session_id: str) -> bool:
        """Clear conversation history for a session."""
        conversation = self.get_conversation(session_id)
        if conversation:
            conversation.clear()
            logger.info(f"Cleared conversation for session: {session_id}")
            return True
        return False
    
    def set_credentials(self, session_id: str, api_key: str, org_id: str) -> bool:
        """Set credentials for a session after verifying them with Tallyfy API."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        # Extract user ID from JWT token
        user_id = self._extract_user_id_from_jwt(api_key)
        
        # Verify credentials by attempting to get current user info
        sdk = None
        try:
            sdk = TallyfySDK(api_key)
            user_info = sdk.users.get_current_user_info(org_id)
            
            if user_info:
                # Credentials are valid, set them in the session
                session.api_key = api_key
                session.org_id = org_id
                session.user_id = user_id
                logger.info(f"Set and verified credentials for session: {session_id}, user_id: {user_id}")
                return True
            else:
                logger.warning(f"Failed to verify credentials for session: {session_id} - user info not found")
                return False
                
        except TallyfyError as e:
            logger.warning(f"Failed to verify credentials for session: {session_id} - {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error verifying credentials for session: {session_id} - {str(e)}")
            return False
        finally:
            # Clean up SDK resources
            if sdk is not None:
                sdk.close()
    
    def get_credentials(self, session_id: str) -> Optional[Dict[str, str]]:
        """Get credentials for a session."""
        session = self.get_session(session_id)
        if session and session.has_credentials():
            return session.get_credentials()
        return None
    
    def validate_session_credentials(self, session_id: str) -> bool:
        """Validate that a session has valid credentials."""
        session = self.get_session(session_id)
        return session.has_credentials() if session else False
    
    def verify_session_credentials(self, session_id: str) -> bool:
        """Re-verify session credentials against Tallyfy API."""
        session = self.get_session(session_id)
        if not session or not session.has_credentials():
            return False
        
        sdk = None
        try:
            sdk = TallyfySDK(session.api_key)
            user_info = sdk.users.get_current_user_info(session.org_id)
            return user_info is not None
        except (TallyfyError, Exception) as e:
            logger.warning(f"Failed to re-verify credentials for session: {session_id} - {str(e)}")
            return False
        finally:
            if sdk is not None:
                sdk.close()
    def get_all_sessions_info(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed information about all sessions."""
        sessions_info = {}
        
        for session_id, session in self._sessions.items():
            sessions_info[session_id] = {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "has_credentials": session.has_credentials(),
                "is_active": session_id in self._active_connections,
                "conversation_length": session.conversation.get_history() if session.conversation else []
            }
        
        return sessions_info

    def get_active_sessions_count(self) -> int:
        """Get the number of active sessions."""
        return len(self._active_connections)
    
    def get_session_stats(self) -> Dict[str, int]:
        """Get session statistics."""
        return {
            "total_sessions": len(self._sessions),
            "active_connections": len(self._active_connections),
        }

    def cleanup_inactive_sessions(self, max_idle_minutes: int = 60) -> int:
        """Remove sessions that have been inactive for too long."""
        cutoff_time = datetime.now().timestamp() - (max_idle_minutes * 60)
        inactive_sessions = []
        
        for session_id, session in self._sessions.items():
            if session.last_activity.timestamp() < cutoff_time:
                inactive_sessions.append(session_id)
        
        for session_id in inactive_sessions:
            self.remove_session(session_id)
        
        if inactive_sessions:
            logger.info(f"Cleaned up {len(inactive_sessions)} inactive sessions")
        
        return len(inactive_sessions)
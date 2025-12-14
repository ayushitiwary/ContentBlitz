from typing import List, Dict, Any
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
import json
from datetime import datetime


class ConversationMemory:
    """Manages conversation history and context across multiple turns"""

    def __init__(self):
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )
        self.session_data: Dict[str, Any] = {
            "brand_voice": None,
            "current_project": None,
            "user_preferences": {},
            "session_start": datetime.now().isoformat()
        }

    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        if role == "user":
            self.memory.chat_memory.add_user_message(content)
        else:
            self.memory.chat_memory.add_ai_message(content)

    def get_history(self) -> List[BaseMessage]:
        """Get conversation history"""
        return self.memory.chat_memory.messages

    def get_history_string(self, last_n: int = 5) -> str:
        """Get formatted conversation history"""
        messages = self.get_history()[-last_n:]
        history_str = []
        for msg in messages:
            role = "User" if isinstance(msg, HumanMessage) else "Assistant"
            history_str.append(f"{role}: {msg.content}")
        return "\n".join(history_str)

    def set_brand_voice(self, brand_voice: str):
        """Store brand voice guidelines"""
        self.session_data["brand_voice"] = brand_voice

    def get_brand_voice(self) -> str:
        """Retrieve brand voice guidelines"""
        return self.session_data.get("brand_voice", "")

    def set_user_preference(self, key: str, value: Any):
        """Store user preference"""
        self.session_data["user_preferences"][key] = value

    def get_user_preference(self, key: str, default=None):
        """Get user preference"""
        return self.session_data["user_preferences"].get(key, default)

    def set_current_project(self, project_info: Dict):
        """Set current project context"""
        self.session_data["current_project"] = project_info

    def get_current_project(self) -> Dict:
        """Get current project context"""
        return self.session_data.get("current_project", {})

    def clear(self):
        """Clear conversation history"""
        self.memory.clear()
        self.session_data = {
            "brand_voice": None,
            "current_project": None,
            "user_preferences": {},
            "session_start": datetime.now().isoformat()
        }

    def export_session(self) -> str:
        """Export session data as JSON"""
        messages = []
        for msg in self.get_history():
            messages.append({
                "role": "user" if isinstance(msg, HumanMessage) else "assistant",
                "content": msg.content
            })

        export_data = {
            "messages": messages,
            "session_data": self.session_data
        }
        return json.dumps(export_data, indent=2)


# Singleton instance
conversation_memory = ConversationMemory()


from typing import List, Dict, Optional
from core.vector_store import vector_store
from config.settings import settings
import uuid


class BrandVoice:
    """Manages brand voice training and consistency"""

    def __init__(self):
        self.brand_guidelines: Dict[str, str] = {}
        self.examples: List[str] = []

    def add_brand_guideline(self, category: str, guideline: str):
        """Add brand voice guideline"""
        self.brand_guidelines[category] = guideline

    def add_example_content(self, content: str):
        """Add example content that represents the brand voice"""
        self.examples.append(content)
        # Store in vector database
        doc_id = f"brand_voice_{uuid.uuid4()}"
        vector_store.add_brand_voice_example(content, doc_id)

    def get_brand_voice_prompt(self) -> str:
        """Generate a prompt section for brand voice consistency"""
        prompt_parts = []

        if self.brand_guidelines:
            prompt_parts.append("## Brand Voice Guidelines:")
            for category, guideline in self.brand_guidelines.items():
                prompt_parts.append(f"- {category}: {guideline}")

        # Retrieve examples from vector store
        examples = vector_store.get_brand_voice_examples(n_examples=3)
        if examples:
            prompt_parts.append("\n## Brand Voice Examples:")
            for i, example in enumerate(examples, 1):
                prompt_parts.append(f"\nExample {i}:\n{example}")

        if prompt_parts:
            return "\n".join(prompt_parts)
        return ""

    def train_from_content(self, content_samples: List[str]):
        """Train brand voice from multiple content samples"""
        for content in content_samples:
            self.add_example_content(content)

    def get_tone_analysis(self) -> Dict[str, str]:
        """Analyze and return brand tone characteristics"""
        return {
            "formality": self.brand_guidelines.get("formality", "balanced"),
            "emotion": self.brand_guidelines.get("emotion", "professional"),
            "voice": self.brand_guidelines.get("voice", "active"),
            "perspective": self.brand_guidelines.get("perspective", "second person")
        }


# Singleton instance
brand_voice = BrandVoice()


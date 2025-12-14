from typing import Dict, Any
from langchain_openai import ChatOpenAI, OpenAI
from langchain.prompts import ChatPromptTemplate
from config.settings import settings
from core.brand_voice import brand_voice
from openai import OpenAI as OpenAIClient
import base64
import requests
from io import BytesIO
from PIL import Image


class ImageAgent:
    """Agent specialized in image generation and optimization"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.model_name,
            temperature=settings.temperature,
            openai_api_key=settings.openai_api_key
        )
        self.client = OpenAIClient(api_key=settings.openai_api_key)

    def generate_image_prompt(self, content_context: str, image_purpose: str) -> str:
        """Generate an optimized DALL-E prompt based on content context"""
        brand_voice_context = brand_voice.get_brand_voice_prompt()

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at creating DALL-E image prompts.
Create detailed, specific prompts that will generate high-quality, professional images.

{brand_voice}"""),
            ("user", """Create a DALL-E 3 image prompt for:

Content Context: {content_context}
Image Purpose: {image_purpose}

Generate a detailed prompt that:
1. Describes the scene/subject clearly
2. Specifies style (professional, modern, minimalist, etc.)
3. Includes composition details
4. Mentions color palette if relevant
5. Ensures brand appropriateness

Provide ONLY the prompt text, no explanation.""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "content_context": content_context,
            "image_purpose": image_purpose,
            "brand_voice": brand_voice_context
        })

        return response.content.strip()

    def generate_image(
        self,
        prompt: str = None,
        content_context: str = None,
        image_purpose: str = "blog header",
        size: str = "1024x1024",
        quality: str = "standard"
    ) -> Dict[str, Any]:
        """Generate an image using DALL-E 3

        Args:
            prompt: Direct prompt (if not provided, will generate from context)
            content_context: Context to generate prompt from
            image_purpose: Purpose of the image
            size: Image size (1024x1024, 1792x1024, 1024x1792)
            quality: standard or hd
        """
        # Generate prompt if not provided
        if not prompt and content_context:
            prompt = self.generate_image_prompt(content_context, image_purpose)
        elif not prompt:
            raise ValueError("Either prompt or content_context must be provided")

        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                n=1,
            )

            image_url = response.data[0].url
            revised_prompt = response.data[0].revised_prompt

            return {
                "image_url": image_url,
                "original_prompt": prompt,
                "revised_prompt": revised_prompt,
                "size": size,
                "quality": quality,
                "metadata": {
                    "purpose": image_purpose,
                    "content_context": content_context
                }
            }
        except Exception as e:
            return {
                "error": str(e),
                "original_prompt": prompt
            }

    def suggest_image_ideas(self, content: str, num_suggestions: int = 3) -> Dict[str, Any]:
        """Suggest image ideas for given content"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a visual content strategist. Suggest compelling image ideas for content."),
            ("user", """Based on this content, suggest {num_suggestions} image ideas:

Content:
{content}

For each suggestion provide:
1. Image concept/subject
2. Purpose (header, inline, social media, etc.)
3. Style recommendations
4. Key visual elements
5. Why it works for this content""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "content": content[:2000],  # Limit for efficiency
            "num_suggestions": num_suggestions
        })

        return {
            "suggestions": response.content
        }

    def generate_social_media_visuals(
        self,
        content_summary: str,
        platform: str = "linkedin"
    ) -> Dict[str, Any]:
        """Generate platform-specific social media visuals"""
        # Platform-specific sizes
        sizes = {
            "linkedin": "1024x1024",  # Square post
            "instagram": "1024x1024",  # Square
            "twitter": "1024x1024",    # Square
            "facebook": "1024x1024"    # Square
        }

        size = sizes.get(platform.lower(), "1024x1024")

        # Generate optimized prompt for social media
        prompt = self.generate_image_prompt(
            content_summary,
            f"{platform} social media post"
        )

        return self.generate_image(
            prompt=prompt,
            content_context=content_summary,
            image_purpose=f"{platform} post",
            size=size
        )

    def create_blog_header_image(self, blog_title: str, blog_summary: str) -> Dict[str, Any]:
        """Create a header image for a blog post"""
        context = f"Blog Title: {blog_title}\nSummary: {blog_summary}"

        return self.generate_image(
            content_context=context,
            image_purpose="blog header image",
            size="1792x1024",  # Wider format for blog headers
            quality="hd"
        )


# Singleton instance
image_agent = ImageAgent()


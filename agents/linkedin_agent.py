from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from config.settings import settings
from core.brand_voice import brand_voice
from core.memory import conversation_memory


class LinkedInAgent:
    """Agent specialized in creating LinkedIn posts and professional content"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.model_name,
            temperature=settings.temperature,
            openai_api_key=settings.openai_api_key
        )

    def generate_linkedin_post(
        self,
        topic: str,
        post_type: str = "thought_leadership",
        research_data: str = "",
        include_hashtags: bool = True
    ) -> Dict[str, Any]:
        """Generate an engaging LinkedIn post

        Args:
            topic: Main topic/message
            post_type: thought_leadership, announcement, story, tip, question
            research_data: Supporting research or data
            include_hashtags: Whether to include relevant hashtags
        """
        brand_voice_context = brand_voice.get_brand_voice_prompt()
        conversation_context = conversation_memory.get_history_string(last_n=3)

        post_type_guidance = {
            "thought_leadership": "Share insights, perspectives, and industry analysis",
            "announcement": "Announce news, updates, or achievements professionally",
            "story": "Tell a compelling personal or business story with lessons",
            "tip": "Provide actionable advice and practical tips",
            "question": "Ask thought-provoking questions to drive engagement"
        }

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a LinkedIn content expert who creates engaging, professional posts that drive engagement.

Your LinkedIn posts should:
- Start with a compelling hook
- Be conversational yet professional
- Include line breaks for readability
- Tell stories or provide value
- End with engagement prompts
- Stay under 3000 characters
- Use emojis sparingly and professionally

{brand_voice}

Post Type Guidance: {post_guidance}

Recent conversation context:
{conversation_context}"""),
            ("user", """Create a LinkedIn post about:

Topic: {topic}
Post Type: {post_type}

Research/Background:
{research_data}

Include hashtags: {include_hashtags}

Generate a complete LinkedIn post with:
1. Attention-grabbing hook
2. Main content with proper line breaks
3. Clear value or message
4. Engagement prompt
5. Relevant hashtags (if requested)""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "topic": topic,
            "post_type": post_type,
            "research_data": research_data or "No research data provided",
            "include_hashtags": str(include_hashtags),
            "brand_voice": brand_voice_context,
            "post_guidance": post_type_guidance.get(post_type, ""),
            "conversation_context": conversation_context or "No previous context"
        })

        return {
            "content": response.content,
            "metadata": {
                "topic": topic,
                "post_type": post_type,
                "char_count": len(response.content)
            }
        }

    def generate_carousel_content(self, topic: str, num_slides: int = 5) -> Dict[str, Any]:
        """Generate content for a LinkedIn carousel post"""
        brand_voice_context = brand_voice.get_brand_voice_prompt()

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a LinkedIn carousel expert. Create engaging slide-by-slide content.

{brand_voice}"""),
            ("user", """Create LinkedIn carousel content about:

Topic: {topic}
Number of Slides: {num_slides}

For each slide provide:
- Slide number and title
- Main text/points (concise, visual-friendly)
- Design suggestions

Slide 1 should be attention-grabbing title slide.
Last slide should be CTA/conclusion.""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "topic": topic,
            "num_slides": num_slides,
            "brand_voice": brand_voice_context
        })

        return {
            "content": response.content,
            "metadata": {
                "topic": topic,
                "num_slides": num_slides
            }
        }

    def optimize_engagement(self, post_content: str) -> Dict[str, Any]:
        """Analyze and optimize LinkedIn post for engagement"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a LinkedIn engagement expert. Analyze posts and provide optimization tips."),
            ("user", """Analyze this LinkedIn post for engagement potential:

{content}

Provide:
1. Engagement score (1-10) with explanation
2. Hook effectiveness
3. Readability analysis
4. Call-to-action strength
5. Specific improvements to increase engagement
6. Hashtag recommendations
7. Best posting time suggestions""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "content": post_content
        })

        return {
            "analysis": response.content,
            "original_post": post_content
        }

    def generate_multiple_variations(self, topic: str, num_variations: int = 3) -> List[str]:
        """Generate multiple variations of a LinkedIn post"""
        variations = []

        post_types = ["thought_leadership", "story", "tip"]
        for i in range(min(num_variations, len(post_types))):
            result = self.generate_linkedin_post(topic, post_type=post_types[i])
            variations.append(result["content"])

        return variations


# Singleton instance
linkedin_agent = LinkedInAgent()


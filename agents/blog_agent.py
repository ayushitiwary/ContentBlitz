from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from config.settings import settings
from core.brand_voice import brand_voice
from core.memory import conversation_memory


class BlogAgent:
    """Agent specialized in creating long-form blog content"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.model_name,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            openai_api_key=settings.openai_api_key
        )

    def generate_blog_outline(self, topic: str, keywords: list, research_data: str = "") -> str:
        """Generate a structured blog outline"""
        brand_voice_context = brand_voice.get_brand_voice_prompt()

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert content strategist and blog writer.
Create a comprehensive blog outline that is engaging, well-structured, and SEO-optimized.

{brand_voice}"""),
            ("user", """Create a detailed blog outline for the following:

Topic: {topic}
Target Keywords: {keywords}

Research Context:
{research_data}

Provide:
1. Compelling title (with keyword)
2. Meta description
3. Introduction hook
4. Main sections with H2/H3 structure
5. Key points for each section
6. Conclusion strategy
7. Call-to-action suggestions""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "topic": topic,
            "keywords": ", ".join(keywords),
            "research_data": research_data or "No research data provided",
            "brand_voice": brand_voice_context
        })

        return response.content

    def write_blog_post(
        self,
        topic: str,
        keywords: list,
        research_data: str = "",
        outline: Optional[str] = None,
        target_length: str = "1500-2000 words"
    ) -> Dict[str, Any]:
        """Generate a complete blog post"""
        brand_voice_context = brand_voice.get_brand_voice_prompt()
        conversation_context = conversation_memory.get_history_string(last_n=3)

        # If no outline provided, generate one first
        if not outline:
            outline = self.generate_blog_outline(topic, keywords, research_data)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert blog writer who creates engaging, informative, and SEO-optimized content.

Your content should:
- Be well-researched and authoritative
- Include natural keyword integration
- Use clear headings and structure
- Be engaging and readable
- Include examples and actionable insights
- Follow SEO best practices

{brand_voice}

Recent conversation context:
{conversation_context}"""),
            ("user", """Write a complete blog post based on the following:

Topic: {topic}
Target Keywords: {keywords}
Target Length: {target_length}

Outline:
{outline}

Research Data:
{research_data}

Please write the full blog post with:
1. Engaging title
2. Meta description (150-160 characters)
3. Full article content with proper headings
4. Natural keyword integration
5. Clear conclusion with CTA""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "topic": topic,
            "keywords": ", ".join(keywords),
            "target_length": target_length,
            "outline": outline,
            "research_data": research_data or "No research data provided",
            "brand_voice": brand_voice_context,
            "conversation_context": conversation_context or "No previous context"
        })

        return {
            "content": response.content,
            "outline": outline,
            "metadata": {
                "topic": topic,
                "keywords": keywords,
                "target_length": target_length
            }
        }

    def optimize_for_seo(self, content: str, keywords: list) -> Dict[str, Any]:
        """Analyze and optimize blog content for SEO"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an SEO expert. Analyze content and provide optimization recommendations."),
            ("user", """Analyze this blog content for SEO:

Content:
{content}

Target Keywords: {keywords}

Provide:
1. Keyword density analysis
2. Readability score assessment
3. SEO strengths
4. Areas for improvement
5. Specific optimization suggestions
6. Internal linking opportunities
7. Meta tags recommendations""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "content": content[:3000],  # Limit for token efficiency
            "keywords": ", ".join(keywords)
        })

        return {
            "analysis": response.content,
            "keywords": keywords
        }


# Singleton instance
blog_agent = BlogAgent()

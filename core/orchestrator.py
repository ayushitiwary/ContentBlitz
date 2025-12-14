from typing import Dict, Any, List
from agents.router_agent import router_agent
from agents.research_agent import research_agent
from agents.blog_agent import blog_agent
from agents.linkedin_agent import linkedin_agent
from agents.image_agent import image_agent
from core.memory import conversation_memory
from core.brand_voice import brand_voice
from core.vector_store import vector_store
import uuid


class ContentOrchestrator:
    """Main orchestrator that coordinates multiple agents to fulfill content creation requests"""

    def __init__(self):
        self.router = router_agent
        self.research = research_agent
        self.blog = blog_agent
        self.linkedin = linkedin_agent
        self.image = image_agent

    def process_request(self, user_query: str, user_preferences: Dict = None) -> Dict[str, Any]:
        """Process a user request through the appropriate agent workflow"""
        # Add to conversation memory
        conversation_memory.add_message("user", user_query)

        # Route the query
        routing = self.router.route_query(user_query)

        # Execute the workflow
        result = self._execute_workflow(user_query, routing, user_preferences or {})

        # Add result to conversation memory
        summary = self._create_result_summary(result)
        conversation_memory.add_message("assistant", summary)

        return result

    def _execute_workflow(
        self,
        query: str,
        routing: Dict[str, Any],
        preferences: Dict
    ) -> Dict[str, Any]:
        """Execute the agent workflow based on routing decision"""
        result = {
            "routing": routing,
            "outputs": {}
        }

        # Step 1: Conduct research if needed
        research_data = ""
        if routing.get("requires_research", False):
            research_result = self.research.conduct_research(query)
            result["outputs"]["research"] = research_result
            research_data = research_result["summary"]

            # Store research in vector database
            vector_store.store_research(
                topic=query,
                content=research_data,
                source="serper_api",
                doc_id=f"research_{uuid.uuid4()}"
            )

        # Step 2: Execute primary agent
        primary_agent = routing.get("primary_agent")

        if primary_agent == "blog_agent":
            result["outputs"]["blog"] = self._create_blog_content(
                query, research_data, preferences
            )

        elif primary_agent == "linkedin_agent":
            result["outputs"]["linkedin"] = self._create_linkedin_content(
                query, research_data, preferences
            )

        elif primary_agent == "image_agent":
            result["outputs"]["image"] = self._create_image_content(
                query, preferences
            )

        elif primary_agent == "research_agent":
            # Research already done above
            pass

        # Step 3: Execute secondary agents if needed
        for secondary in routing.get("secondary_agents", []):
            if secondary == "image_agent" and "blog" in result["outputs"]:
                # Generate blog header image
                blog_content = result["outputs"]["blog"]["content"]
                # Extract title from content (simple approach)
                title = query
                result["outputs"]["blog_image"] = self.image.create_blog_header_image(
                    title, blog_content[:500]
                )

        return result

    def _create_blog_content(
        self,
        query: str,
        research_data: str,
        preferences: Dict
    ) -> Dict[str, Any]:
        """Create blog content with the blog agent"""
        keywords = preferences.get("keywords", [query])
        target_length = preferences.get("target_length", "1500-2000 words")

        # Generate blog post
        blog_result = self.blog.write_blog_post(
            topic=query,
            keywords=keywords,
            research_data=research_data,
            target_length=target_length
        )

        # Optionally run SEO optimization
        if preferences.get("seo_analysis", True):
            seo_result = self.blog.optimize_for_seo(
                blog_result["content"],
                keywords
            )
            blog_result["seo_analysis"] = seo_result

        return blog_result

    def _create_linkedin_content(
        self,
        query: str,
        research_data: str,
        preferences: Dict
    ) -> Dict[str, Any]:
        """Create LinkedIn content with the LinkedIn agent"""
        post_type = preferences.get("post_type", "thought_leadership")
        include_hashtags = preferences.get("include_hashtags", True)

        linkedin_result = self.linkedin.generate_linkedin_post(
            topic=query,
            post_type=post_type,
            research_data=research_data,
            include_hashtags=include_hashtags
        )

        # Optionally analyze engagement
        if preferences.get("engagement_analysis", True):
            engagement = self.linkedin.optimize_engagement(
                linkedin_result["content"]
            )
            linkedin_result["engagement_analysis"] = engagement

        return linkedin_result

    def _create_image_content(
        self,
        query: str,
        preferences: Dict
    ) -> Dict[str, Any]:
        """Create image content with the image agent"""
        size = preferences.get("size", "1024x1024")
        quality = preferences.get("quality", "standard")

        return self.image.generate_image(
            content_context=query,
            image_purpose=preferences.get("purpose", "general"),
            size=size,
            quality=quality
        )

    def _create_result_summary(self, result: Dict[str, Any]) -> str:
        """Create a summary of results for conversation memory"""
        outputs = result.get("outputs", {})
        summary_parts = []

        if "research" in outputs:
            summary_parts.append("Completed research on the topic")
        if "blog" in outputs:
            summary_parts.append("Generated blog post")
        if "linkedin" in outputs:
            summary_parts.append("Created LinkedIn post")
        if "image" in outputs:
            summary_parts.append("Generated image")

        return " | ".join(summary_parts) if summary_parts else "Processed request"

    def create_content_campaign(
        self,
        topic: str,
        include_blog: bool = True,
        include_linkedin: bool = True,
        include_images: bool = True,
        preferences: Dict = None
    ) -> Dict[str, Any]:
        """Create a complete content campaign with multiple content types"""
        preferences = preferences or {}
        campaign_result = {
            "topic": topic,
            "campaign_outputs": {}
        }

        # Conduct research once
        research_result = self.research.conduct_research(topic)
        research_data = research_result["summary"]
        campaign_result["research"] = research_result

        # Generate blog if requested
        if include_blog:
            campaign_result["campaign_outputs"]["blog"] = self._create_blog_content(
                topic, research_data, preferences
            )

        # Generate LinkedIn post if requested
        if include_linkedin:
            campaign_result["campaign_outputs"]["linkedin"] = self._create_linkedin_content(
                topic, research_data, preferences
            )

        # Generate images if requested
        if include_images:
            images = {}
            if include_blog:
                images["blog_header"] = self.image.create_blog_header_image(
                    topic, research_data[:500]
                )
            if include_linkedin:
                images["linkedin_visual"] = self.image.generate_social_media_visuals(
                    research_data[:500], "linkedin"
                )
            campaign_result["campaign_outputs"]["images"] = images

        return campaign_result


# Singleton instance
orchestrator = ContentOrchestrator()


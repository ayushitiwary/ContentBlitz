from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from config.settings import settings
from core.memory import conversation_memory


class RouterAgent:
    """Intelligent query routing agent that directs requests to appropriate specialized agents"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.model_name,
            temperature=0.1,  # Low temperature for consistent routing
            openai_api_key=settings.openai_api_key
        )

    def route_query(self, user_query: str) -> Dict[str, Any]:
        """Route user query to appropriate agent(s)"""
        conversation_context = conversation_memory.get_history_string(last_n=2)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an intelligent routing assistant for a content creation system.
Analyze user requests and determine which agent(s) should handle them.

Available agents:
- research_agent: Web research, data gathering, fact-checking, trend analysis
- blog_agent: Blog posts, articles, long-form content, SEO optimization
- linkedin_agent: LinkedIn posts, professional content, carousels, engagement optimization
- image_agent: Image generation, visual content, graphics, social media visuals

You must respond in this EXACT JSON format:
{{
    "primary_agent": "agent_name",
    "secondary_agents": ["agent_name"],
    "requires_research": true/false,
    "content_type": "blog/linkedin/image/research",
    "reasoning": "brief explanation"
}}"""),
            ("user", """User Query: {query}

Recent conversation:
{conversation_context}

Route this query to the appropriate agent(s).""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "query": user_query,
            "conversation_context": conversation_context or "No previous context"
        })

        # Parse the response
        import json
        try:
            # Extract JSON from response
            content = response.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            routing = json.loads(content)
            return routing
        except:
            # Fallback parsing based on keywords
            query_lower = user_query.lower()
            if any(word in query_lower for word in ["blog", "article", "write", "post" ]):
                if "linkedin" in query_lower:
                    return {
                        "primary_agent": "linkedin_agent",
                        "secondary_agents": [],
                        "requires_research": "research" in query_lower,
                        "content_type": "linkedin",
                        "reasoning": "Detected LinkedIn content request"
                    }
                else:
                    return {
                        "primary_agent": "blog_agent",
                        "secondary_agents": [],
                        "requires_research": True,
                        "content_type": "blog",
                        "reasoning": "Detected blog content request"
                    }
            elif any(word in query_lower for word in ["image", "visual", "graphic", "picture"]):
                return {
                    "primary_agent": "image_agent",
                    "secondary_agents": [],
                    "requires_research": False,
                    "content_type": "image",
                    "reasoning": "Detected image generation request"
                }
            elif any(word in query_lower for word in ["research", "find", "search", "analyze"]):
                return {
                    "primary_agent": "research_agent",
                    "secondary_agents": [],
                    "requires_research": True,
                    "content_type": "research",
                    "reasoning": "Detected research request"
                }
            else:
                return {
                    "primary_agent": "blog_agent",
                    "secondary_agents": [],
                    "requires_research": True,
                    "content_type": "general",
                    "reasoning": "Default routing"
                }

    def suggest_workflow(self, user_goal: str) -> Dict[str, Any]:
        """Suggest a multi-step workflow for complex content creation goals"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a content strategy expert. Design efficient workflows for content creation.

Available agents:
- research_agent: Research and data gathering
- blog_agent: Long-form content creation
- linkedin_agent: Professional social content
- image_agent: Visual content generation

Create step-by-step workflows."""),
            ("user", """User Goal: {goal}

Design an optimal workflow with:
1. Ordered steps
2. Which agent handles each step
3. What output each step produces
4. How outputs connect to next steps
5. Estimated time for each step""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "goal": user_goal
        })

        return {
            "workflow": response.content,
            "goal": user_goal
        }


# Singleton instance
router_agent = RouterAgent()

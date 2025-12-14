from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from config.settings import settings
from core.brand_voice import brand_voice
import requests
import json


class ResearchAgent:
    """Agent specialized in web research and data gathering"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.model_name,
            temperature=0.3,  # Lower temperature for factual research
            openai_api_key=settings.openai_api_key
        )

    def search_web(self, query: str, num_results: int = 5) -> List[Dict]:
        """Search the web using Serper API"""
        if not settings.serper_api_key:
            return []

        url = "https://google.serper.dev/search"
        payload = json.dumps({
            "q": query,
            "num": num_results
        })
        headers = {
            'X-API-KEY': settings.serper_api_key,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get('organic', [])[:num_results]:
                results.append({
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', '')
                })
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def conduct_research(self, topic: str, context: str = "") -> Dict[str, Any]:
        """Conduct comprehensive research on a topic"""
        # Search the web
        search_results = self.search_web(topic, num_results=5)

        # Synthesize research findings
        search_context = "\n\n".join([
            f"Source: {r['title']}\nURL: {r['link']}\nContent: {r['snippet']}"
            for r in search_results
        ])

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a research expert specializing in content marketing research.
Your job is to analyze search results and synthesize key insights, statistics, trends, and actionable information.

Provide:
1. Key insights and findings
2. Relevant statistics and data points
3. Current trends
4. Expert quotes or authoritative sources
5. Actionable recommendations

Format your research in a clear, structured manner."""),
            ("user", """Topic: {topic}

Additional Context: {context}

Search Results:
{search_results}

Please provide a comprehensive research summary.""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "topic": topic,
            "context": context or "No additional context provided",
            "search_results": search_context or "No search results available. Provide insights based on your knowledge."
        })

        return {
            "topic": topic,
            "summary": response.content,
            "sources": search_results,
            "raw_search_data": search_context
        }

    def quick_fact_check(self, claim: str) -> Dict[str, Any]:
        """Quick fact checking for content verification"""
        search_results = self.search_web(f"fact check {claim}", num_results=3)

        search_context = "\n\n".join([
            f"{r['title']}: {r['snippet']}"
            for r in search_results
        ])

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a fact-checking expert. Verify claims based on search results and provide a confidence level."),
            ("user", """Claim: {claim}

Search Results:
{search_results}

Please verify this claim and provide:
1. Verification status (Verified/Unverified/Partially True/False)
2. Confidence level (High/Medium/Low)
3. Explanation with sources""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "claim": claim,
            "search_results": search_context or "No results found"
        })

        return {
            "claim": claim,
            "analysis": response.content,
            "sources": search_results
        }


# Singleton instance
research_agent = ResearchAgent()


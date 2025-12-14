# ContentBlitz 🚀

An intelligent multi-agent content marketing assistant that automates research, writing, and optimization to deliver timely, tailored, platform-ready content at scale.

## Features

- **Multi-Agent Architecture**: Specialized agents for Research, Blog Writing, LinkedIn Posts, and Image Generation
- **Intelligent Query Routing**: Automatically routes requests to the appropriate agent
- **Multi-Turn Conversation Memory**: Maintains context across interactions
- **Brand Voice Consistency**: Learns and applies your brand voice across all content
- **Multi-Format Content Generation**: Blogs, social posts, visuals, and research summaries
- **SEO Optimization**: Content optimized for search engines
- **Platform-Specific Publishing**: Content tailored for different platforms

## Architecture

```
├── agents/
│   ├── research_agent.py       # Web research and data gathering
│   ├── blog_agent.py           # Long-form blog content creation
│   ├── linkedin_agent.py       # LinkedIn post generation
│   ├── image_agent.py          # Image generation and optimization
│   └── router_agent.py         # Intelligent query routing
├── core/
│   ├── memory.py               # Conversation memory management
│   ├── brand_voice.py          # Brand voice training and consistency
│   ├── vector_store.py         # Vector database for RAG
│   └── orchestrator.py         # Agent orchestration with LangGraph
├── ui/
│   └── app.py                  # Streamlit UI
├── utils/
│   ├── seo_optimizer.py        # SEO optimization utilities
│   └── content_scorer.py       # Content quality scoring
└── config/
    └── settings.py             # Configuration management
```

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your_openai_key
SERPER_API_KEY=your_serper_key  # For web search
```

4. Run the application:
```bash
streamlit run ui/app.py
```

## Usage

1. **Set Up Brand Voice**: Upload sample content or provide brand guidelines
2. **Create Content**: Choose content type and provide requirements
3. **Review & Edit**: Review AI-generated content with quality scores
4. **Export**: Download or publish directly to platforms

## Tech Stack

- **LLM**: OpenAI GPT-4
- **Agent Framework**: LangGraph
- **Vector DB**: ChromaDB
- **Research**: Serper API (Google Search)
- **Image Generation**: DALL-E 3
- **UI**: Streamlit
- **Memory**: LangChain Memory

## License

MIT


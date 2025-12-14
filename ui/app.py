import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from core.orchestrator import orchestrator
from core.memory import conversation_memory
from core.brand_voice import brand_voice
from agents import (
    research_agent,
    blog_agent,
    linkedin_agent,
    image_agent
)
from utils.seo_optimizer import seo_optimizer
from utils.content_scorer import content_scorer
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="ContentBlitz - AI Content Marketing Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding: 0 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = {}
if 'brand_voice_setup' not in st.session_state:
    st.session_state.brand_voice_setup = False

# Header
st.markdown('<h1 class="main-header">🚀 ContentBlitz</h1>', unsafe_allow_html=True)
st.markdown("**Your Intelligent Multi-Agent Content Marketing Assistant**")
st.markdown("---")

# Sidebar - Brand Voice & Settings
with st.sidebar:
    st.header("⚙️ Settings")

    # Brand Voice Section
    st.subheader("🎨 Brand Voice")

    with st.expander("Configure Brand Voice", expanded=not st.session_state.brand_voice_setup):
        st.markdown("**Train your brand voice for consistent content**")

        # Brand guidelines
        formality = st.select_slider(
            "Formality Level",
            options=["Very Casual", "Casual", "Balanced", "Formal", "Very Formal"],
            value="Balanced"
        )

        emotion = st.select_slider(
            "Emotional Tone",
            options=["Enthusiastic", "Professional", "Balanced", "Reserved", "Authoritative"],
            value="Professional"
        )

        # Example content
        example_content = st.text_area(
            "Paste example content that represents your brand voice",
            height=150,
            placeholder="Paste blog posts, social media content, or any text that represents your brand..."
        )

        if st.button("Save Brand Voice"):
            brand_voice.add_brand_guideline("formality", formality)
            brand_voice.add_brand_guideline("emotion", emotion)

            if example_content:
                brand_voice.add_example_content(example_content)

            st.session_state.brand_voice_setup = True
            st.success("✅ Brand voice configured!")

    # Content preferences
    st.subheader("📝 Content Preferences")
    default_keywords = st.text_input("Default Keywords (comma-separated)", "")
    seo_analysis = st.checkbox("Enable SEO Analysis", value=True)
    engagement_analysis = st.checkbox("Enable Engagement Analysis", value=True)

    # Session management
    st.subheader("💾 Session")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear History"):
            conversation_memory.clear()
            st.session_state.conversation_history = []
            st.session_state.generated_content = {}
            st.success("Cleared!")

    with col2:
        if st.button("Export Session"):
            session_data = conversation_memory.export_session()
            st.download_button(
                "Download JSON",
                session_data,
                file_name=f"contentblitz_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

# Main content area with tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Smart Assistant",
    "📝 Blog Writer",
    "💼 LinkedIn Posts",
    "🖼️ Image Generator",
    "🔬 Research Tools"
])

# Tab 1: Smart Assistant
with tab1:
    st.header("Smart Content Assistant")
    st.markdown("Ask anything! The AI will automatically route your request to the right agent.")

    # Chat interface
    user_query = st.text_area(
        "What content do you need?",
        height=100,
        placeholder="Example: Write a blog post about AI in marketing\nExample: Create a LinkedIn post about productivity tips\nExample: Research current trends in content marketing"
    )

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        process_button = st.button("🚀 Generate Content", type="primary", use_container_width=True)
    with col2:
        create_campaign = st.button("📦 Full Campaign", use_container_width=True)

    if process_button and user_query:
        with st.spinner("🤖 Processing your request..."):
            # Set preferences
            preferences = {
                "keywords": [k.strip() for k in default_keywords.split(",") if k.strip()],
                "seo_analysis": seo_analysis,
                "engagement_analysis": engagement_analysis
            }

            # Process request
            result = orchestrator.process_request(user_query, preferences)

            # Display results
            st.success("✅ Content generated successfully!")

            # Show routing info
            with st.expander("🔀 Routing Information"):
                routing = result.get("routing", {})
                st.json(routing)

            # Display outputs
            outputs = result.get("outputs", {})

            if "research" in outputs:
                st.subheader("🔬 Research Results")
                research = outputs["research"]
                st.markdown(research["summary"])

                if research.get("sources"):
                    with st.expander("📚 Sources"):
                        for i, source in enumerate(research["sources"], 1):
                            st.markdown(f"**{i}. [{source['title']}]({source['link']})**")
                            st.markdown(source['snippet'])
                            st.markdown("---")

            if "blog" in outputs:
                st.subheader("📝 Blog Post")
                blog = outputs["blog"]
                st.markdown(blog["content"])

                # SEO Analysis
                if blog.get("seo_analysis"):
                    with st.expander("📊 SEO Analysis"):
                        st.markdown(blog["seo_analysis"]["analysis"])

                # Content Score
                score_result = content_scorer.score_content(blog["content"], "blog")
                with st.expander(f"⭐ Content Quality Score: {score_result['overall_score']}/10 ({score_result['grade']})"):
                    cols = st.columns(len(score_result["dimension_scores"]))
                    for col, (dim, score) in zip(cols, score_result["dimension_scores"].items()):
                        col.metric(dim.replace('_', ' ').title(), f"{score:.1f}/10")

                    st.markdown("**Strengths:**")
                    for strength in score_result["strengths"]:
                        st.markdown(f"✅ {strength}")

                    st.markdown("**Areas for Improvement:**")
                    for improvement in score_result["improvements"]:
                        st.markdown(f"🔸 {improvement}")

                # Download button
                st.download_button(
                    "📥 Download Blog Post",
                    blog["content"],
                    file_name=f"blog_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )

            if "linkedin" in outputs:
                st.subheader("💼 LinkedIn Post")
                linkedin = outputs["linkedin"]
                st.text_area("Generated Post", linkedin["content"], height=300)

                # Character count
                char_count = len(linkedin["content"])
                st.info(f"📏 Character count: {char_count}/3000")

                # Engagement Analysis
                if linkedin.get("engagement_analysis"):
                    with st.expander("📈 Engagement Analysis"):
                        st.markdown(linkedin["engagement_analysis"]["analysis"])

                # Content Score
                score_result = content_scorer.score_content(linkedin["content"], "linkedin")
                with st.expander(f"⭐ Content Quality Score: {score_result['overall_score']}/10 ({score_result['grade']})"):
                    cols = st.columns(len(score_result["dimension_scores"]))
                    for col, (dim, score) in zip(cols, score_result["dimension_scores"].items()):
                        col.metric(dim.replace('_', ' ').title(), f"{score:.1f}/10")

                # Copy button (using download as copy)
                st.download_button(
                    "📋 Copy to Clipboard",
                    linkedin["content"],
                    file_name="linkedin_post.txt",
                    mime="text/plain"
                )

            if "image" in outputs or "blog_image" in outputs:
                st.subheader("🖼️ Generated Images")

                image_data = outputs.get("image") or outputs.get("blog_image")
                if image_data and "image_url" in image_data:
                    st.image(image_data["image_url"], caption="Generated Image")
                    st.markdown(f"**Prompt used:** {image_data.get('revised_prompt', image_data.get('original_prompt'))}")

    if create_campaign and user_query:
        with st.spinner("📦 Creating full content campaign..."):
            preferences = {
                "keywords": [k.strip() for k in default_keywords.split(",") if k.strip()],
                "seo_analysis": seo_analysis,
                "engagement_analysis": engagement_analysis
            }

            campaign = orchestrator.create_content_campaign(
                topic=user_query,
                include_blog=True,
                include_linkedin=True,
                include_images=True,
                preferences=preferences
            )

            st.success("✅ Campaign created successfully!")

            # Display campaign outputs
            st.subheader("📦 Campaign Contents")

            campaign_outputs = campaign.get("campaign_outputs", {})

            # Create download package
            campaign_package = {
                "topic": user_query,
                "created_at": datetime.now().isoformat(),
                "contents": {}
            }

            if "blog" in campaign_outputs:
                st.markdown("### 📝 Blog Post")
                st.markdown(campaign_outputs["blog"]["content"][:500] + "...")
                campaign_package["contents"]["blog"] = campaign_outputs["blog"]["content"]

            if "linkedin" in campaign_outputs:
                st.markdown("### 💼 LinkedIn Post")
                st.text_area("LinkedIn", campaign_outputs["linkedin"]["content"], height=200, key="campaign_linkedin")
                campaign_package["contents"]["linkedin"] = campaign_outputs["linkedin"]["content"]

            if "images" in campaign_outputs:
                st.markdown("### 🖼️ Images")
                cols = st.columns(2)
                for i, (img_type, img_data) in enumerate(campaign_outputs["images"].items()):
                    if "image_url" in img_data:
                        with cols[i % 2]:
                            st.image(img_data["image_url"], caption=img_type.replace('_', ' ').title())

            # Download campaign package
            st.download_button(
                "📥 Download Full Campaign",
                json.dumps(campaign_package, indent=2),
                file_name=f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

# Tab 2: Blog Writer
with tab2:
    st.header("📝 Blog Content Writer")

    col1, col2 = st.columns([2, 1])

    with col1:
        blog_topic = st.text_input("Blog Topic", placeholder="e.g., The Future of AI in Content Marketing")
        blog_keywords = st.text_input("Target Keywords (comma-separated)", placeholder="AI, content marketing, automation")

    with col2:
        blog_length = st.selectbox("Target Length", ["800-1200 words", "1200-1500 words", "1500-2000 words", "2000+ words"])
        include_research = st.checkbox("Include Research", value=True)

    if st.button("Generate Blog Post", type="primary"):
        if blog_topic:
            with st.spinner("✍️ Writing blog post..."):
                keywords = [k.strip() for k in blog_keywords.split(",") if k.strip()]

                # Conduct research if requested
                research_data = ""
                if include_research:
                    research_result = research_agent.conduct_research(blog_topic)
                    research_data = research_result["summary"]

                    with st.expander("🔬 Research Summary"):
                        st.markdown(research_data)

                # Generate blog
                blog_result = blog_agent.write_blog_post(
                    topic=blog_topic,
                    keywords=keywords,
                    research_data=research_data,
                    target_length=blog_length
                )

                st.subheader("Generated Blog Post")
                st.markdown(blog_result["content"])

                # SEO Analysis
                if keywords:
                    seo_analysis = seo_optimizer.analyze_content(blog_result["content"], keywords)

                    with st.expander(f"📊 SEO Score: {seo_analysis['seo_score']}/100"):
                        st.markdown(f"**Word Count:** {seo_analysis['word_count']}")

                        st.markdown("**Keyword Analysis:**")
                        for kw, data in seo_analysis["keyword_analysis"].items():
                            st.markdown(f"- **{kw}**: {data['count']} occurrences ({data['density']}%) - Status: {data['status']}")

                        st.markdown("**Recommendations:**")
                        for rec in seo_analysis["recommendations"]:
                            st.markdown(f"- {rec}")

                # Download
                st.download_button(
                    "📥 Download Blog Post",
                    blog_result["content"],
                    file_name=f"blog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
        else:
            st.warning("Please enter a blog topic")

# Tab 3: LinkedIn Posts
with tab3:
    st.header("💼 LinkedIn Post Generator")

    col1, col2 = st.columns([2, 1])

    with col1:
        linkedin_topic = st.text_input("Post Topic", placeholder="e.g., Lessons learned from scaling a startup")

    with col2:
        post_type = st.selectbox(
            "Post Type",
            ["thought_leadership", "story", "tip", "announcement", "question"]
        )

    include_hashtags = st.checkbox("Include Hashtags", value=True)
    include_research_li = st.checkbox("Research Topic First", value=False)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Generate Post", type="primary", use_container_width=True):
            if linkedin_topic:
                with st.spinner("✍️ Creating LinkedIn post..."):
                    research_data = ""
                    if include_research_li:
                        research_result = research_agent.conduct_research(linkedin_topic)
                        research_data = research_result["summary"]

                    result = linkedin_agent.generate_linkedin_post(
                        topic=linkedin_topic,
                        post_type=post_type,
                        research_data=research_data,
                        include_hashtags=include_hashtags
                    )

                    st.subheader("Generated LinkedIn Post")
                    st.text_area("Post Content", result["content"], height=400)

                    char_count = len(result["content"])
                    st.info(f"📏 Character count: {char_count}/3000")

                    # Engagement analysis
                    engagement = linkedin_agent.optimize_engagement(result["content"])
                    with st.expander("📈 Engagement Analysis"):
                        st.markdown(engagement["analysis"])

                    st.download_button(
                        "📋 Download Post",
                        result["content"],
                        file_name=f"linkedin_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    )
            else:
                st.warning("Please enter a topic")

    with col2:
        if st.button("Generate 3 Variations", use_container_width=True):
            if linkedin_topic:
                with st.spinner("✍️ Creating variations..."):
                    variations = linkedin_agent.generate_multiple_variations(linkedin_topic, 3)

                    for i, var in enumerate(variations, 1):
                        with st.expander(f"Variation {i}"):
                            st.text_area(f"Post {i}", var, height=300, key=f"var_{i}")

# Tab 4: Image Generator
with tab4:
    st.header("🖼️ Image Generator")

    image_purpose = st.selectbox(
        "Image Purpose",
        ["blog header", "social media post", "infographic", "featured image", "general"]
    )

    content_context = st.text_area(
        "Content Context",
        height=100,
        placeholder="Describe what the image should represent..."
    )

    col1, col2 = st.columns(2)
    with col1:
        image_size = st.selectbox("Size", ["1024x1024", "1792x1024", "1024x1792"])
    with col2:
        image_quality = st.selectbox("Quality", ["standard", "hd"])

    if st.button("Generate Image", type="primary"):
        if content_context:
            with st.spinner("🎨 Generating image..."):
                result = image_agent.generate_image(
                    content_context=content_context,
                    image_purpose=image_purpose,
                    size=image_size,
                    quality=image_quality
                )

                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.subheader("Generated Image")
                    st.image(result["image_url"])

                    with st.expander("ℹ️ Generation Details"):
                        st.markdown(f"**Original Prompt:** {result['original_prompt']}")
                        st.markdown(f"**Refined Prompt:** {result['revised_prompt']}")
                        st.markdown(f"**Size:** {result['size']}")
                        st.markdown(f"**Quality:** {result['quality']}")
        else:
            st.warning("Please provide content context")

# Tab 5: Research Tools
with tab5:
    st.header("🔬 Research Tools")

    research_topic = st.text_input("Research Topic", placeholder="e.g., Latest trends in AI marketing")

    if st.button("Conduct Research", type="primary"):
        if research_topic:
            with st.spinner("🔍 Researching..."):
                result = research_agent.conduct_research(research_topic)

                st.subheader("Research Summary")
                st.markdown(result["summary"])

                if result.get("sources"):
                    st.subheader("📚 Sources")
                    for i, source in enumerate(result["sources"], 1):
                        with st.expander(f"{i}. {source['title']}"):
                            st.markdown(f"**URL:** [{source['link']}]({source['link']})")
                            st.markdown(f"**Snippet:** {source['snippet']}")

                st.download_button(
                    "📥 Download Research",
                    result["summary"],
                    file_name=f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                )
        else:
            st.warning("Please enter a research topic")

    st.markdown("---")
    st.subheader("✓ Quick Fact Check")

    claim = st.text_input("Enter a claim to verify", placeholder="e.g., 70% of marketers say AI improves productivity")

    if st.button("Verify Claim"):
        if claim:
            with st.spinner("🔍 Fact checking..."):
                result = research_agent.quick_fact_check(claim)

                st.markdown("### Verification Result")
                st.markdown(result["analysis"])

                if result.get("sources"):
                    with st.expander("📚 Sources"):
                        for source in result["sources"]:
                            st.markdown(f"- [{source['title']}]({source['link']})")
        else:
            st.warning("Please enter a claim to verify")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>ContentBlitz v1.0 | Powered by GPT-4 & Multi-Agent AI</p>
        <p>🚀 Create • 🎯 Optimize • 📊 Analyze • 🌟 Scale</p>
    </div>
    """,
    unsafe_allow_html=True
)


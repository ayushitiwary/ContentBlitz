from typing import Dict, Any
import re
from datetime import datetime


class ContentScorer:
    """Utility for scoring content quality across multiple dimensions"""

    def __init__(self):
        pass

    def score_content(self, content: str, content_type: str = "blog") -> Dict[str, Any]:
        """Score content quality across multiple dimensions"""

        if content_type == "blog":
            return self._score_blog_content(content)
        elif content_type == "linkedin":
            return self._score_linkedin_content(content)
        else:
            return self._score_general_content(content)

    def _score_blog_content(self, content: str) -> Dict[str, Any]:
        """Score blog content quality"""
        scores = {
            "engagement": self._score_engagement(content),
            "structure": self._score_structure(content),
            "clarity": self._score_clarity(content),
            "actionability": self._score_actionability(content),
            "professionalism": self._score_professionalism(content)
        }

        overall = sum(scores.values()) / len(scores)

        return {
            "overall_score": round(overall, 1),
            "dimension_scores": scores,
            "grade": self._get_grade(overall),
            "strengths": self._identify_strengths(scores),
            "improvements": self._identify_improvements(scores),
            "timestamp": datetime.now().isoformat()
        }

    def _score_linkedin_content(self, content: str) -> Dict[str, Any]:
        """Score LinkedIn post quality"""
        scores = {
            "hook_strength": self._score_hook(content),
            "engagement_potential": self._score_linkedin_engagement(content),
            "professionalism": self._score_professionalism(content),
            "call_to_action": self._score_cta(content),
            "formatting": self._score_linkedin_formatting(content)
        }

        overall = sum(scores.values()) / len(scores)

        return {
            "overall_score": round(overall, 1),
            "dimension_scores": scores,
            "grade": self._get_grade(overall),
            "character_count": len(content),
            "strengths": self._identify_strengths(scores),
            "improvements": self._identify_improvements(scores),
            "timestamp": datetime.now().isoformat()
        }

    def _score_general_content(self, content: str) -> Dict[str, Any]:
        """Score general content quality"""
        scores = {
            "clarity": self._score_clarity(content),
            "engagement": self._score_engagement(content),
            "professionalism": self._score_professionalism(content)
        }

        overall = sum(scores.values()) / len(scores)

        return {
            "overall_score": round(overall, 1),
            "dimension_scores": scores,
            "grade": self._get_grade(overall),
            "timestamp": datetime.now().isoformat()
        }

    def _score_engagement(self, content: str) -> float:
        """Score engagement potential (0-10)"""
        score = 5.0  # Base score

        # Check for questions
        if '?' in content:
            score += 1.0

        # Check for storytelling elements
        story_words = ['story', 'experience', 'learned', 'discovered', 'realized']
        if any(word in content.lower() for word in story_words):
            score += 1.0

        # Check for examples
        if 'example' in content.lower() or 'for instance' in content.lower():
            score += 0.5

        # Check for statistics/numbers
        if re.search(r'\d+%|\d+ percent', content):
            score += 1.0

        # Check for emotional words
        emotion_words = ['amazing', 'incredible', 'excited', 'surprised', 'frustrated', 'happy']
        if any(word in content.lower() for word in emotion_words):
            score += 0.5

        return min(10.0, score)

    def _score_structure(self, content: str) -> float:
        """Score content structure (0-10)"""
        score = 5.0

        # Check for headings
        h2_count = len(re.findall(r'^##\s+', content, re.MULTILINE))
        if h2_count >= 3:
            score += 2.0
        elif h2_count >= 2:
            score += 1.0

        # Check for lists
        if re.search(r'^\s*[-*+]\s+', content, re.MULTILINE):
            score += 1.0

        # Check for paragraphs
        paragraphs = content.split('\n\n')
        if len(paragraphs) >= 5:
            score += 1.0

        # Check for introduction and conclusion
        if len(content) > 500:
            if any(word in content[:200].lower() for word in ['introduction', 'in this', 'today']):
                score += 0.5
            if any(word in content[-200:].lower() for word in ['conclusion', 'in summary', 'to wrap up']):
                score += 0.5

        return min(10.0, score)

    def _score_clarity(self, content: str) -> float:
        """Score content clarity (0-10)"""
        score = 7.0  # Base score for reasonable clarity

        # Check average sentence length
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        words = re.findall(r'\b\w+\b', content)

        if sentences:
            avg_sentence_length = len(words) / len(sentences)

            # Penalize very long sentences
            if avg_sentence_length > 25:
                score -= 2.0
            elif avg_sentence_length > 20:
                score -= 1.0

            # Reward concise sentences
            if avg_sentence_length < 15:
                score += 1.0

        # Check for transition words
        transitions = ['however', 'therefore', 'moreover', 'furthermore', 'additionally', 'consequently']
        if any(word in content.lower() for word in transitions):
            score += 1.0

        return min(10.0, max(0.0, score))

    def _score_actionability(self, content: str) -> float:
        """Score actionability of content (0-10)"""
        score = 5.0

        # Check for action verbs
        action_words = ['learn', 'discover', 'implement', 'apply', 'use', 'try', 'start', 'begin']
        action_count = sum(1 for word in action_words if word in content.lower())
        score += min(2.0, action_count * 0.5)

        # Check for step-by-step instructions
        if 'step' in content.lower() or re.search(r'\d+\.', content):
            score += 1.5

        # Check for practical examples
        if 'example' in content.lower() or 'here\'s how' in content.lower():
            score += 1.0

        # Check for calls to action
        cta_words = ['try', 'start', 'download', 'sign up', 'learn more', 'get started']
        if any(word in content.lower() for word in cta_words):
            score += 0.5

        return min(10.0, score)

    def _score_professionalism(self, content: str) -> float:
        """Score professionalism of content (0-10)"""
        score = 8.0  # Start high

        # Check for excessive exclamation marks
        exclamation_count = content.count('!')
        if exclamation_count > 5:
            score -= 2.0
        elif exclamation_count > 3:
            score -= 1.0

        # Check for ALL CAPS (except acronyms)
        caps_words = re.findall(r'\b[A-Z]{4,}\b', content)
        if len(caps_words) > 3:
            score -= 1.0

        # Reward proper formatting
        if re.search(r'^#\s+', content, re.MULTILINE):
            score += 1.0

        return min(10.0, max(0.0, score))

    def _score_hook(self, content: str) -> float:
        """Score the hook/opening of content (0-10)"""
        score = 5.0
        first_line = content.split('\n')[0] if content else ""

        # Check for questions
        if first_line.strip().endswith('?'):
            score += 2.0

        # Check for statistics
        if re.search(r'\d+%', first_line):
            score += 2.0

        # Check for bold statements
        if any(word in first_line.lower() for word in ['never', 'always', 'secret', 'truth']):
            score += 1.0

        # Check length (should be concise)
        if len(first_line) < 100:
            score += 1.0

        return min(10.0, score)

    def _score_linkedin_engagement(self, content: str) -> float:
        """Score LinkedIn-specific engagement potential (0-10)"""
        score = 5.0

        # Check for line breaks (LinkedIn posts need breathing room)
        line_breaks = content.count('\n\n')
        if line_breaks >= 3:
            score += 1.5

        # Check for questions to audience
        if '?' in content:
            score += 1.0

        # Check for personal pronouns (engagement)
        if any(word in content.lower() for word in ['you', 'your', 'we', 'our']):
            score += 1.0

        # Check for hashtags
        if '#' in content:
            score += 0.5

        # Check for @ mentions or engagement prompts
        if any(phrase in content.lower() for phrase in ['what do you think', 'share your', 'comment below']):
            score += 1.0

        return min(10.0, score)

    def _score_cta(self, content: str) -> float:
        """Score call-to-action strength (0-10)"""
        score = 5.0

        cta_phrases = [
            'comment', 'share', 'follow', 'connect', 'reach out',
            'let me know', 'what do you think', 'join', 'learn more'
        ]

        cta_count = sum(1 for phrase in cta_phrases if phrase in content.lower())
        score += min(3.0, cta_count * 1.5)

        # Check if CTA is at the end
        last_section = content[-200:].lower()
        if any(phrase in last_section for phrase in cta_phrases):
            score += 2.0

        return min(10.0, score)

    def _score_linkedin_formatting(self, content: str) -> float:
        """Score LinkedIn formatting (0-10)"""
        score = 5.0

        # Check for proper line breaks
        if '\n\n' in content:
            score += 2.0

        # Check for emojis (moderate use is good)
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            "]+", flags=re.UNICODE)
        emoji_count = len(emoji_pattern.findall(content))

        if 1 <= emoji_count <= 5:
            score += 1.5
        elif emoji_count > 10:
            score -= 1.0

        # Check length
        char_count = len(content)
        if 500 <= char_count <= 2000:
            score += 1.5
        elif char_count > 3000:
            score -= 1.0

        return min(10.0, max(0.0, score))

    def _get_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 9.0:
            return "A+"
        elif score >= 8.5:
            return "A"
        elif score >= 8.0:
            return "A-"
        elif score >= 7.5:
            return "B+"
        elif score >= 7.0:
            return "B"
        elif score >= 6.5:
            return "B-"
        elif score >= 6.0:
            return "C+"
        elif score >= 5.5:
            return "C"
        else:
            return "C-"

    def _identify_strengths(self, scores: Dict[str, float]) -> list:
        """Identify top strengths from scores"""
        strengths = []
        for dimension, score in scores.items():
            if score >= 8.0:
                strengths.append(dimension.replace('_', ' ').title())
        return strengths or ["Good baseline quality"]

    def _identify_improvements(self, scores: Dict[str, float]) -> list:
        """Identify areas for improvement"""
        improvements = []
        for dimension, score in scores.items():
            if score < 6.0:
                improvements.append(f"Improve {dimension.replace('_', ' ')}")
        return improvements or ["Minor refinements only"]


# Singleton instance
content_scorer = ContentScorer()


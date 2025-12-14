from typing import Dict, List, Any
import re
from collections import Counter


class SEOOptimizer:
    """Utility for SEO analysis and optimization"""

    def __init__(self):
        self.ideal_title_length = (50, 60)
        self.ideal_meta_desc_length = (150, 160)
        self.ideal_keyword_density = (1.0, 2.5)  # Percentage

    def analyze_content(self, content: str, keywords: List[str]) -> Dict[str, Any]:
        """Perform comprehensive SEO analysis on content"""
        word_count = self._count_words(content)

        analysis = {
            "word_count": word_count,
            "keyword_analysis": self._analyze_keywords(content, keywords),
            "readability": self._analyze_readability(content),
            "structure": self._analyze_structure(content),
            "recommendations": []
        }

        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis, keywords)
        analysis["seo_score"] = self._calculate_seo_score(analysis)

        return analysis

    def _count_words(self, content: str) -> int:
        """Count words in content"""
        words = re.findall(r'\b\w+\b', content.lower())
        return len(words)

    def _analyze_keywords(self, content: str, keywords: List[str]) -> Dict[str, Any]:
        """Analyze keyword usage and density"""
        content_lower = content.lower()
        words = re.findall(r'\b\w+\b', content_lower)
        total_words = len(words)

        keyword_data = {}
        for keyword in keywords:
            keyword_lower = keyword.lower()
            count = content_lower.count(keyword_lower)
            density = (count / total_words * 100) if total_words > 0 else 0

            # Check keyword placement
            in_first_paragraph = keyword_lower in content_lower[:500]
            in_headings = self._check_keyword_in_headings(content, keyword_lower)

            keyword_data[keyword] = {
                "count": count,
                "density": round(density, 2),
                "in_first_paragraph": in_first_paragraph,
                "in_headings": in_headings,
                "status": self._assess_keyword_usage(density, count)
            }

        return keyword_data

    def _check_keyword_in_headings(self, content: str, keyword: str) -> bool:
        """Check if keyword appears in headings"""
        headings = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)
        return any(keyword in heading.lower() for heading in headings)

    def _assess_keyword_usage(self, density: float, count: int) -> str:
        """Assess keyword usage status"""
        if count == 0:
            return "missing"
        elif density < self.ideal_keyword_density[0]:
            return "too_low"
        elif density > self.ideal_keyword_density[1]:
            return "too_high"
        else:
            return "optimal"

    def _analyze_readability(self, content: str) -> Dict[str, Any]:
        """Analyze content readability"""
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        words = re.findall(r'\b\w+\b', content)

        avg_sentence_length = len(words) / len(sentences) if sentences else 0

        # Simple readability assessment
        if avg_sentence_length < 15:
            readability_level = "easy"
        elif avg_sentence_length < 20:
            readability_level = "moderate"
        else:
            readability_level = "difficult"

        return {
            "sentence_count": len(sentences),
            "avg_sentence_length": round(avg_sentence_length, 1),
            "readability_level": readability_level,
            "paragraph_count": len(content.split('\n\n'))
        }

    def _analyze_structure(self, content: str) -> Dict[str, Any]:
        """Analyze content structure"""
        h1_count = len(re.findall(r'^#\s+', content, re.MULTILINE))
        h2_count = len(re.findall(r'^##\s+', content, re.MULTILINE))
        h3_count = len(re.findall(r'^###\s+', content, re.MULTILINE))

        # Check for lists
        has_lists = bool(re.search(r'^\s*[-*+]\s+', content, re.MULTILINE))

        # Check for links
        link_count = len(re.findall(r'\[.+?\]\(.+?\)', content))

        return {
            "h1_count": h1_count,
            "h2_count": h2_count,
            "h3_count": h3_count,
            "has_lists": has_lists,
            "link_count": link_count,
            "has_proper_hierarchy": h1_count == 1 and h2_count >= 2
        }

    def _generate_recommendations(
        self,
        analysis: Dict[str, Any],
        keywords: List[str]
    ) -> List[str]:
        """Generate SEO recommendations"""
        recommendations = []

        # Word count recommendations
        word_count = analysis["word_count"]
        if word_count < 800:
            recommendations.append("Content is too short. Aim for at least 800 words for better SEO.")

        # Keyword recommendations
        for keyword, data in analysis["keyword_analysis"].items():
            if data["status"] == "missing":
                recommendations.append(f"Keyword '{keyword}' is not present. Add it naturally.")
            elif data["status"] == "too_low":
                recommendations.append(f"Keyword '{keyword}' density is too low. Use it more frequently.")
            elif data["status"] == "too_high":
                recommendations.append(f"Keyword '{keyword}' density is too high. Reduce usage to avoid keyword stuffing.")

            if not data["in_first_paragraph"]:
                recommendations.append(f"Include '{keyword}' in the first paragraph.")

            if not data["in_headings"]:
                recommendations.append(f"Use '{keyword}' in at least one heading.")

        # Structure recommendations
        structure = analysis["structure"]
        if structure["h1_count"] == 0:
            recommendations.append("Add an H1 heading (title).")
        elif structure["h1_count"] > 1:
            recommendations.append("Use only one H1 heading.")

        if structure["h2_count"] < 2:
            recommendations.append("Add more H2 subheadings to improve structure.")

        if not structure["has_lists"]:
            recommendations.append("Consider adding bullet points or lists for better readability.")

        if structure["link_count"] < 2:
            recommendations.append("Add internal and external links to improve SEO.")

        # Readability recommendations
        readability = analysis["readability"]
        if readability["readability_level"] == "difficult":
            recommendations.append("Simplify sentence structure for better readability.")

        return recommendations

    def _calculate_seo_score(self, analysis: Dict[str, Any]) -> int:
        """Calculate overall SEO score (0-100)"""
        score = 100

        # Deduct points for issues
        word_count = analysis["word_count"]
        if word_count < 500:
            score -= 30
        elif word_count < 800:
            score -= 15

        # Keyword issues
        for keyword_data in analysis["keyword_analysis"].values():
            if keyword_data["status"] == "missing":
                score -= 20
            elif keyword_data["status"] != "optimal":
                score -= 10

            if not keyword_data["in_first_paragraph"]:
                score -= 5

        # Structure issues
        structure = analysis["structure"]
        if not structure["has_proper_hierarchy"]:
            score -= 10
        if structure["link_count"] < 2:
            score -= 5

        return max(0, min(100, score))


# Singleton instance
seo_optimizer = SEOOptimizer()


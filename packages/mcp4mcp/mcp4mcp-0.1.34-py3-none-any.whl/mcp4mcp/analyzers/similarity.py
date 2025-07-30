
"""
LLM-powered similarity detection for MCP tools
"""

import json
from typing import List, Dict, Tuple, Optional
from ..models import Tool, SimilarityResult


class ToolSimilarityAnalyzer:
    """Analyzes similarity between MCP tools"""
    
    def __init__(self, similarity_threshold: float = 0.7):
        self.similarity_threshold = similarity_threshold
    
    def analyze_tools(self, tools: Dict[str, Tool]) -> List[SimilarityResult]:
        """Analyze all tools for similarity"""
        results = []
        tool_list = list(tools.values())
        
        # Compare each tool with every other tool
        for i, tool1 in enumerate(tool_list):
            for j, tool2 in enumerate(tool_list[i+1:], i+1):
                similarity = self.calculate_similarity(tool1, tool2)
                
                if similarity >= self.similarity_threshold:
                    result = SimilarityResult(
                        tool1_name=tool1.name,
                        tool2_name=tool2.name,
                        similarity_score=similarity,
                        explanation=self._generate_explanation(tool1, tool2, similarity),
                        recommended_action=self._generate_recommendation(tool1, tool2, similarity)
                    )
                    results.append(result)
        
        return results
    
    def calculate_similarity(self, tool1: Tool, tool2: Tool) -> float:
        """Calculate similarity score between two tools"""
        # Name similarity (30% weight)
        name_sim = self._calculate_name_similarity(tool1.name, tool2.name)
        
        # Description similarity (40% weight)
        desc_sim = self._calculate_description_similarity(tool1.description, tool2.description)
        
        # Parameter similarity (20% weight)
        param_sim = self._calculate_parameter_similarity(tool1.parameters, tool2.parameters)
        
        # Function pattern similarity (10% weight)
        pattern_sim = self._calculate_pattern_similarity(tool1, tool2)
        
        # Weighted average
        total_similarity = (
            name_sim * 0.3 +
            desc_sim * 0.4 +
            param_sim * 0.2 +
            pattern_sim * 0.1
        )
        
        return min(total_similarity, 1.0)
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between tool names"""
        if not name1 or not name2:
            return 0.0
        
        # Convert to lowercase for comparison
        name1 = name1.lower()
        name2 = name2.lower()
        
        # Exact match
        if name1 == name2:
            return 1.0
        
        # Check for common prefixes/suffixes
        prefixes = ["get_", "set_", "update_", "create_", "delete_", "list_", "handle_"]
        suffixes = ["_tool", "_handler", "_processor"]
        
        # Remove common prefixes/suffixes for comparison
        clean_name1 = name1
        clean_name2 = name2
        
        for prefix in prefixes:
            if clean_name1.startswith(prefix):
                clean_name1 = clean_name1[len(prefix):]
            if clean_name2.startswith(prefix):
                clean_name2 = clean_name2[len(prefix):]
        
        for suffix in suffixes:
            if clean_name1.endswith(suffix):
                clean_name1 = clean_name1[:-len(suffix)]
            if clean_name2.endswith(suffix):
                clean_name2 = clean_name2[:-len(suffix)]
        
        # Check if cleaned names are similar
        if clean_name1 == clean_name2:
            return 0.8
        
        # Levenshtein distance-based similarity
        return self._levenshtein_similarity(name1, name2)
    
    def _calculate_description_similarity(self, desc1: str, desc2: str) -> float:
        """Calculate similarity between tool descriptions"""
        if not desc1 or not desc2:
            return 0.0
        
        # Simple keyword-based similarity
        words1 = set(desc1.lower().split())
        words2 = set(desc2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_parameter_similarity(self, params1: List[Dict], params2: List[Dict]) -> float:
        """Calculate similarity between parameter lists"""
        if not params1 and not params2:
            return 1.0
        
        if not params1 or not params2:
            return 0.0
        
        # Extract parameter names
        names1 = set(p.get("name", "") for p in params1)
        names2 = set(p.get("name", "") for p in params2)
        
        if not names1 or not names2:
            return 0.0
        
        intersection = len(names1.intersection(names2))
        union = len(names1.union(names2))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_pattern_similarity(self, tool1: Tool, tool2: Tool) -> float:
        """Calculate similarity based on tool patterns"""
        patterns1 = self._extract_patterns(tool1)
        patterns2 = self._extract_patterns(tool2)
        
        if not patterns1 or not patterns2:
            return 0.0
        
        matches = sum(1 for p in patterns1 if p in patterns2)
        total = len(set(patterns1 + patterns2))
        
        return matches / total if total > 0 else 0.0
    
    def _extract_patterns(self, tool: Tool) -> List[str]:
        """Extract patterns from a tool"""
        patterns = []
        
        # Name patterns
        name = tool.name.lower()
        if name.startswith("get_"):
            patterns.append("getter")
        elif name.startswith("set_"):
            patterns.append("setter")
        elif name.startswith("update_"):
            patterns.append("updater")
        elif name.startswith("create_"):
            patterns.append("creator")
        elif name.startswith("delete_"):
            patterns.append("deleter")
        elif name.startswith("list_"):
            patterns.append("lister")
        
        # Parameter patterns
        if tool.parameters:
            param_count = len(tool.parameters)
            if param_count == 1:
                patterns.append("single_param")
            elif param_count > 3:
                patterns.append("many_params")
        
        # Return type patterns
        if tool.return_type:
            if "list" in tool.return_type.lower():
                patterns.append("returns_list")
            elif "dict" in tool.return_type.lower():
                patterns.append("returns_dict")
        
        return patterns
    
    def _levenshtein_similarity(self, s1: str, s2: str) -> float:
        """Calculate Levenshtein distance-based similarity"""
        if not s1 or not s2:
            return 0.0
        
        # Simple implementation
        len1, len2 = len(s1), len(s2)
        if len1 == 0:
            return 0.0
        if len2 == 0:
            return 0.0
        
        # Create distance matrix
        d = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        
        # Initialize first row and column
        for i in range(len1 + 1):
            d[i][0] = i
        for j in range(len2 + 1):
            d[0][j] = j
        
        # Fill the matrix
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if s1[i-1] == s2[j-1] else 1
                d[i][j] = min(
                    d[i-1][j] + 1,      # deletion
                    d[i][j-1] + 1,      # insertion
                    d[i-1][j-1] + cost  # substitution
                )
        
        # Calculate similarity (1 - normalized distance)
        max_len = max(len1, len2)
        distance = d[len1][len2]
        return 1.0 - (distance / max_len)
    
    def _generate_explanation(self, tool1: Tool, tool2: Tool, similarity: float) -> str:
        """Generate explanation for similarity"""
        reasons = []
        
        # Check name similarity
        if self._calculate_name_similarity(tool1.name, tool2.name) > 0.7:
            reasons.append("similar names")
        
        # Check description similarity
        if self._calculate_description_similarity(tool1.description, tool2.description) > 0.5:
            reasons.append("similar descriptions")
        
        # Check parameter similarity
        if self._calculate_parameter_similarity(tool1.parameters, tool2.parameters) > 0.5:
            reasons.append("similar parameters")
        
        # Check pattern similarity
        if self._calculate_pattern_similarity(tool1, tool2) > 0.5:
            reasons.append("similar patterns")
        
        if not reasons:
            reasons.append("general similarity")
        
        return f"Tools are {similarity:.1%} similar due to: {', '.join(reasons)}"
    
    def _generate_recommendation(self, tool1: Tool, tool2: Tool, similarity: float) -> str:
        """Generate recommendation based on similarity"""
        if similarity > 0.9:
            return "Consider merging these tools as they appear to be duplicates"
        elif similarity > 0.8:
            return "Review these tools for potential consolidation"
        elif similarity > 0.7:
            return "Check if these tools can share common functionality"
        else:
            return "Tools are similar but likely serve different purposes"
    
    def find_potential_duplicates(self, tools: Dict[str, Tool]) -> List[Tuple[str, str, float]]:
        """Find potential duplicate tools"""
        duplicates = []
        
        similarity_results = self.analyze_tools(tools)
        
        for result in similarity_results:
            if result.similarity_score > 0.8:  # High similarity threshold for duplicates
                duplicates.append((
                    result.tool1_name,
                    result.tool2_name,
                    result.similarity_score
                ))
        
        return duplicates
    
    def update_similarity_scores(self, tools: Dict[str, Tool]) -> None:
        """Update similarity scores in tool objects"""
        for tool_name, tool in tools.items():
            for other_name, other_tool in tools.items():
                if tool_name != other_name:
                    similarity = self.calculate_similarity(tool, other_tool)
                    tool.similarity_scores[other_name] = similarity

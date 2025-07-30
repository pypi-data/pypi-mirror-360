"""
CBUAE MCP Server implementation.
"""

import json
from typing import Dict, List, Optional
from fuzzywuzzy import fuzz
from fastmcp import FastMCP
from .data import load_policy_db
from .semantic_search import CBUAESemanticSearch

def create_server() -> FastMCP:
    """Create and configure the CBUAE MCP server."""
    
    # Initialize POLICY_DB
    POLICY_DB = load_policy_db()
    
    # Initialize semantic search
    semantic_search = CBUAESemanticSearch()
    if semantic_search.is_available():
        semantic_search.update_embeddings(POLICY_DB)
    
    # Initialize MCP server
    mcp = FastMCP("CBUAE Policy Agent")
    
    @mcp.tool()
    def query_cbuae_policy(query: str, search_mode: str = "hybrid") -> dict:
        """
        Search CBUAE policies using advanced search capabilities.
        
        Args:
            query: The search query to find relevant policies
            search_mode: Search mode - "fuzzy", "semantic", or "hybrid" (default)
            
        Returns:
            Dictionary containing query results with matching policies
        """
        query_original = query
        query = query.lower().strip()
        
        result = {
            "query": query_original,
            "search_mode": search_mode,
            "results": [],
            "search_info": {}
        }
        
        # Fuzzy search results
        fuzzy_results = []
        if search_mode in ["fuzzy", "hybrid"]:
            for policy_id, policy_data in POLICY_DB.items():
                search_text = f"{policy_id.lower()} {policy_data['category'].lower()} {policy_data['title'].lower()} {policy_data['text'].lower()}"
                fuzzy_score = fuzz.partial_ratio(query, search_text)
                substring_match = any(query in field.lower() for field in [policy_id, policy_data["category"], policy_data["title"], policy_data["text"]])
                
                if substring_match or fuzzy_score > 60:  # Lower threshold for hybrid
                    fuzzy_results.append({
                        "policy_id": policy_id,
                        "title": policy_data["title"],
                        "text": policy_data["text"],
                        "category": policy_data["category"],
                        "fuzzy_score": fuzzy_score,
                        "substring_match": substring_match,
                        "search_type": "fuzzy"
                    })
        
        # Use appropriate search method
        if search_mode == "semantic" and semantic_search.is_available():
            # Pure semantic search
            semantic_results = semantic_search.search(query_original, top_k=10)
            for sem_result in semantic_results:
                policy_id = sem_result['policy_id']
                if policy_id in POLICY_DB:
                    policy_data = POLICY_DB[policy_id]
                    result["results"].append({
                        "policy_id": policy_id,
                        "title": policy_data["title"],
                        "text": policy_data["text"],
                        "category": policy_data["category"],
                        "similarity_score": sem_result['similarity_score'],
                        "search_type": "semantic"
                    })
            result["search_info"]["semantic_available"] = True
            
        elif search_mode == "hybrid" and semantic_search.is_available():
            # Hybrid search
            hybrid_results = semantic_search.hybrid_search(query_original, fuzzy_results, top_k=10)
            for hyb_result in hybrid_results:
                policy_id = hyb_result['policy_id']
                if policy_id in POLICY_DB:
                    policy_data = POLICY_DB[policy_id]
                    result["results"].append({
                        "policy_id": policy_id,
                        "title": policy_data["title"],
                        "text": policy_data["text"],
                        "category": policy_data["category"],
                        "fuzzy_score": hyb_result.get('fuzzy_score', 0),
                        "semantic_score": hyb_result.get('semantic_score', 0),
                        "combined_score": hyb_result.get('combined_score', 0),
                        "search_type": "hybrid"
                    })
            result["search_info"]["semantic_available"] = True
            result["search_info"]["hybrid_used"] = True
            
        else:
            # Fallback to fuzzy search
            result["results"] = fuzzy_results[:10]  # Limit to top 10
            result["search_info"]["semantic_available"] = semantic_search.is_available()
            result["search_info"]["fallback_reason"] = "Semantic search not available" if not semantic_search.is_available() else "Fuzzy search requested"
        
        if not result["results"]:
            return {
                "query": query_original,
                "search_mode": search_mode,
                "error": "No relevant policies found",
                "search_info": result["search_info"]
            }
        
        result["total_results"] = len(result["results"])
        return result
    
    @mcp.tool()
    def analyze_policy_gaps(bank_policy: str, reg_id: str) -> dict:
        """
        Analyze gaps between bank policies and CBUAE regulations.
        
        Args:
            bank_policy: The bank's policy text to analyze
            reg_id: The CBUAE regulation ID to compare against
            
        Returns:
            Dictionary containing identified gaps and recommendations
        """
        bank_policy = bank_policy.lower().strip()
        
        if reg_id not in POLICY_DB:
            return {"error": f"Regulation {reg_id} not found"}
        
        cbuae_policy = POLICY_DB[reg_id]["text"].lower()
        gaps = []
        
        if "customer due diligence" not in bank_policy and "customer due diligence" in cbuae_policy:
            gaps.append("Missing requirement: Enhanced customer due diligence for high-risk clients")
        if "suspicious transaction" not in bank_policy and "suspicious transaction" in cbuae_policy:
            gaps.append("Missing requirement: Suspicious transaction reporting")
        if "capital adequacy ratio" not in bank_policy and "capital adequacy ratio" in cbuae_policy:
            gaps.append("Missing requirement: Minimum Capital Adequacy Ratio of 10.5%")
        
        return {
            "regulation_id": reg_id,
            "gaps": gaps if gaps else ["No significant gaps identified"]
        }
    
    @mcp.tool()
    def list_available_policies() -> dict:
        """
        List all available CBUAE policies in the database.
        
        Returns:
            Dictionary containing all available policies with their IDs, titles, and categories
        """
        policies = []
        for policy_id, policy_data in POLICY_DB.items():
            policies.append({
                "policy_id": policy_id,
                "title": policy_data["title"],
                "category": policy_data["category"]
            })
        
        return {"policies": policies, "total_count": len(policies)}
    
    
    return mcp

def run_server():
    """Entry point for running the CBUAE MCP server."""
    mcp = create_server()
    try:
        mcp.run()
    finally:
        # Clean up resources
        pass
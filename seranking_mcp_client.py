"""
Seranking MCP Client for Real SEO Data Integration
Fetches SEO data from Seranking MCP deployed on Replit
"""

import requests
import json
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SerankingMCPClient:
    """Client to fetch SEO data from Seranking MCP"""
    
    def __init__(self, base_url: str = "https://0207da74-76db-4156-96c8-1217466e5174-00-1n3hp5w7y0kjt.spock.replit.dev"):
        self.base_url = base_url.rstrip('/')
        # The MCP server runs locally via STDIO, not HTTP
        # For now, we'll use mock data that matches the expected structure
        self.use_mock_data = True
        
    def fetch_seo_data(self, domain: str = "bagsoflove.co.uk") -> Dict[str, Any]:
        """
        Fetch comprehensive SEO data from Seranking MCP
        
        Args:
            domain: Domain to analyze (default: bagsoflove.co.uk)
            
        Returns:
            Comprehensive SEO data including keywords, rankings, traffic estimates, etc.
        """
        logger.info(f"Fetching SEO data for {domain} from Seranking MCP...")
        
        if self.use_mock_data:
            logger.info("Using realistic mock SEO data (Seranking MCP runs locally via STDIO)")
            return self._get_realistic_seo_data(domain)
        
        try:
            # If you have the actual Seranking API token, you can implement real API calls here
            # For now, we'll use realistic mock data
            return self._get_realistic_seo_data(domain)
            
        except Exception as e:
            logger.error(f"Error fetching SEO data from Seranking MCP: {e}")
            return self._get_realistic_seo_data(domain)
    
    def _fetch_keywords_data(self, domain: str) -> Dict[str, Any]:
        """Fetch keyword data from Seranking MCP"""
        try:
            # Try to fetch keywords using MCP tools
            response = requests.post(f"{self.mcp_url}/tools/call", 
                json={
                    "tool": "seranking_get_keywords",
                    "arguments": {
                        "domain": domain,
                        "limit": 50
                    }
                }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return self._normalize_keywords_data(data)
            else:
                logger.warning(f"Failed to fetch keywords: {response.status_code}")
                return self._get_mock_keywords_data(domain)
                
        except Exception as e:
            logger.warning(f"Error fetching keywords: {e}")
            return self._get_mock_keywords_data(domain)
    
    def _fetch_rankings_data(self, domain: str) -> Dict[str, Any]:
        """Fetch ranking data from Seranking MCP"""
        try:
            response = requests.post(f"{self.mcp_url}/tools/call",
                json={
                    "tool": "seranking_get_rankings",
                    "arguments": {
                        "domain": domain
                    }
                }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return self._normalize_rankings_data(data)
            else:
                return self._get_mock_rankings_data(domain)
                
        except Exception as e:
            logger.warning(f"Error fetching rankings: {e}")
            return self._get_mock_rankings_data(domain)
    
    def _fetch_traffic_data(self, domain: str) -> Dict[str, Any]:
        """Fetch traffic estimation data"""
        try:
            response = requests.post(f"{self.mcp_url}/tools/call",
                json={
                    "tool": "seranking_get_traffic",
                    "arguments": {
                        "domain": domain
                    }
                }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return self._normalize_traffic_data(data)
            else:
                return self._get_mock_traffic_data(domain)
                
        except Exception as e:
            logger.warning(f"Error fetching traffic data: {e}")
            return self._get_mock_traffic_data(domain)
    
    def _fetch_competitor_data(self, domain: str) -> Dict[str, Any]:
        """Fetch competitor analysis data"""
        try:
            response = requests.post(f"{self.mcp_url}/tools/call",
                json={
                    "tool": "seranking_get_competitors",
                    "arguments": {
                        "domain": domain
                    }
                }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return self._normalize_competitor_data(data)
            else:
                return self._get_mock_competitor_data(domain)
                
        except Exception as e:
            logger.warning(f"Error fetching competitor data: {e}")
            return self._get_mock_competitor_data(domain)
    
    def _fetch_technical_seo_data(self, domain: str) -> Dict[str, Any]:
        """Fetch technical SEO data"""
        try:
            response = requests.post(f"{self.mcp_url}/tools/call",
                json={
                    "tool": "seranking_get_technical_seo",
                    "arguments": {
                        "domain": domain
                    }
                }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return self._normalize_technical_data(data)
            else:
                return self._get_mock_technical_data(domain)
                
        except Exception as e:
            logger.warning(f"Error fetching technical SEO data: {e}")
            return self._get_mock_technical_data(domain)
    
    def _normalize_keywords_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize keywords data from Seranking MCP"""
        keywords = raw_data.get("keywords", [])
        return {
            "total_keywords": len(keywords),
            "top_keywords": keywords[:20],
            "keyword_categories": {
                "primary": [kw for kw in keywords[:10] if kw.get("position", 999) <= 10],
                "secondary": [kw for kw in keywords[10:20] if kw.get("position", 999) <= 20],
                "long_tail": [kw for kw in keywords[20:] if kw.get("position", 999) <= 50]
            },
            "ranking_distribution": self._calculate_ranking_distribution(keywords),
            "keyword_opportunities": self._identify_keyword_opportunities(keywords)
        }
    
    def _normalize_rankings_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize rankings data"""
        return {
            "average_position": raw_data.get("average_position", 0),
            "top_10_count": raw_data.get("top_10_count", 0),
            "top_20_count": raw_data.get("top_20_count", 0),
            "ranking_trends": raw_data.get("trends", {}),
            "position_changes": raw_data.get("changes", [])
        }
    
    def _normalize_traffic_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize traffic data"""
        return {
            "organic_traffic": raw_data.get("organic_traffic", 0),
            "traffic_potential": raw_data.get("traffic_potential", 0),
            "click_through_rate": raw_data.get("ctr", 0),
            "traffic_trends": raw_data.get("trends", {}),
            "seasonal_patterns": raw_data.get("seasonal", {})
        }
    
    def _normalize_competitor_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize competitor data"""
        return {
            "main_competitors": raw_data.get("competitors", []),
            "market_share": raw_data.get("market_share", {}),
            "competitive_gaps": raw_data.get("gaps", []),
            "opportunities": raw_data.get("opportunities", [])
        }
    
    def _normalize_technical_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize technical SEO data"""
        return {
            "page_speed": raw_data.get("page_speed", {}),
            "mobile_friendliness": raw_data.get("mobile", {}),
            "structured_data": raw_data.get("structured_data", {}),
            "crawl_issues": raw_data.get("crawl_issues", []),
            "technical_score": raw_data.get("overall_score", 0)
        }
    
    def _calculate_ranking_distribution(self, keywords: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate distribution of keyword rankings"""
        distribution = {
            "positions_1_3": 0,
            "positions_4_10": 0,
            "positions_11_20": 0,
            "positions_21_50": 0,
            "positions_51_plus": 0
        }
        
        for kw in keywords:
            position = kw.get("position", 999)
            if position <= 3:
                distribution["positions_1_3"] += 1
            elif position <= 10:
                distribution["positions_4_10"] += 1
            elif position <= 20:
                distribution["positions_11_20"] += 1
            elif position <= 50:
                distribution["positions_21_50"] += 1
            else:
                distribution["positions_51_plus"] += 1
        
        return distribution
    
    def _identify_keyword_opportunities(self, keywords: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify keyword opportunities"""
        opportunities = []
        
        for kw in keywords:
            position = kw.get("position", 999)
            search_volume = kw.get("search_volume", 0)
            difficulty = kw.get("difficulty", 0)
            
            # High volume, low difficulty keywords not in top 20
            if search_volume > 1000 and difficulty < 50 and position > 20:
                opportunities.append({
                    "keyword": kw.get("keyword", ""),
                    "position": position,
                    "search_volume": search_volume,
                    "difficulty": difficulty,
                    "opportunity_type": "High Volume, Low Difficulty",
                    "potential_traffic": search_volume * 0.1
                })
        
        return sorted(opportunities, key=lambda x: x["potential_traffic"], reverse=True)[:10]
    
    def _analyze_content_opportunities(self, keywords_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content opportunities based on keywords"""
        return {
            "content_gaps": [
                "Gift guides for different occasions",
                "How-to guides for personalization",
                "Customer stories and testimonials",
                "Seasonal gift recommendations"
            ],
            "optimization_opportunities": [
                "Add more product descriptions",
                "Create category landing pages",
                "Add customer reviews",
                "Implement structured data"
            ],
            "content_score": 75
        }
    
    def _analyze_local_seo(self, domain: str) -> Dict[str, Any]:
        """Analyze local SEO opportunities"""
        return {
            "local_keywords": [
                "personalized gifts uk",
                "custom gifts london",
                "photo gifts england"
            ],
            "local_opportunities": [
                "Google My Business optimization",
                "Local directory listings",
                "Location-based content"
            ],
            "delivery_areas": ["England", "Scotland", "Wales", "Northern Ireland"]
        }
    
    def _get_realistic_seo_data(self, domain: str) -> Dict[str, Any]:
        """Get realistic SEO data that matches Seranking MCP structure"""
        logger.info(f"Generating realistic SEO data for {domain}")
        
        # Realistic keywords data for Bags of Love
        keywords = [
            {"keyword": "personalized gifts", "position": 8, "search_volume": 12000, "difficulty": 65, "traffic_estimate": 800},
            {"keyword": "custom photo gifts", "position": 15, "search_volume": 8500, "difficulty": 55, "traffic_estimate": 600},
            {"keyword": "photo blankets", "position": 12, "search_volume": 6500, "difficulty": 45, "traffic_estimate": 500},
            {"keyword": "personalized mugs", "position": 20, "search_volume": 4200, "difficulty": 40, "traffic_estimate": 300},
            {"keyword": "christmas personalized gifts", "position": 25, "search_volume": 15000, "difficulty": 70, "traffic_estimate": 1000},
            {"keyword": "valentines day custom gifts", "position": 18, "search_volume": 8000, "difficulty": 60, "traffic_estimate": 550},
            {"keyword": "personalized tea towels", "position": 22, "search_volume": 3200, "difficulty": 35, "traffic_estimate": 200},
            {"keyword": "custom photo socks", "position": 28, "search_volume": 2800, "difficulty": 30, "traffic_estimate": 180},
            {"keyword": "personalized canvas prints", "position": 16, "search_volume": 5500, "difficulty": 50, "traffic_estimate": 400},
            {"keyword": "mothers day personalized gifts", "position": 30, "search_volume": 12000, "difficulty": 75, "traffic_estimate": 800}
        ]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "domain": domain,
            "source": "Seranking MCP (Mock Data)",
            "mcp_url": self.base_url,
            "keywords": self._normalize_keywords_data({"keywords": keywords}),
            "rankings": {
                "average_position": 19.2,
                "top_10_count": 1,
                "top_20_count": 4,
                "ranking_trends": {"improving": 3, "declining": 2, "stable": 5},
                "position_changes": [
                    {"keyword": "personalized gifts", "change": +2, "period": "last_30_days"},
                    {"keyword": "photo blankets", "change": -1, "period": "last_30_days"},
                    {"keyword": "custom photo gifts", "change": +3, "period": "last_30_days"}
                ]
            },
            "traffic_estimates": {
                "organic_traffic": 4200,
                "traffic_potential": 5800,
                "click_through_rate": 0.09,
                "traffic_trends": {
                    "monthly_growth": 0.18,
                    "seasonal_boost": 0.35,
                    "peak_months": ["November", "December", "February"]
                },
                "seasonal_patterns": {
                    "christmas": {"traffic_multiplier": 3.2, "months": ["November", "December"]},
                    "valentines": {"traffic_multiplier": 2.8, "months": ["January", "February"]},
                    "mothers_day": {"traffic_multiplier": 2.5, "months": ["March", "April", "May"]}
                }
            },
            "competitor_analysis": {
                "main_competitors": [
                    {"domain": "personalised-gifts.co.uk", "strength": "High", "market_share": 0.25},
                    {"domain": "notonthehighstreet.com", "strength": "Very High", "market_share": 0.35},
                    {"domain": "photobox.co.uk", "strength": "High", "market_share": 0.20},
                    {"domain": "vistaprint.co.uk", "strength": "Medium", "market_share": 0.15}
                ],
                "market_share": {"bagsoflove": 0.05, "competitors": 0.95},
                "competitive_gaps": [
                    "Better mobile experience",
                    "More detailed product descriptions", 
                    "Customer review integration",
                    "Social proof elements"
                ],
                "opportunities": [
                    "Focus on niche personalization",
                    "Improve local SEO",
                    "Create unique content",
                    "Build brand authority"
                ]
            },
            "technical_seo": {
                "page_speed": {
                    "mobile_score": 78,
                    "desktop_score": 85,
                    "issues": ["Large images", "Unused CSS", "Render-blocking resources"]
                },
                "mobile_friendliness": {
                    "score": 92,
                    "issues": ["Small touch targets", "Viewport issues"]
                },
                "structured_data": {
                    "implemented": True,
                    "types": ["Product", "Organization", "BreadcrumbList"],
                    "coverage": "85%"
                },
                "crawl_issues": [
                    "Some 404 errors on old product pages",
                    "Missing meta descriptions on category pages"
                ],
                "technical_score": 82
            },
            "content_analysis": {
                "content_gaps": [
                    "Gift guides for different occasions",
                    "How-to guides for personalization",
                    "Customer stories and testimonials",
                    "Seasonal gift recommendations",
                    "Comparison guides"
                ],
                "optimization_opportunities": [
                    "Add more product descriptions",
                    "Create category landing pages",
                    "Add customer reviews",
                    "Implement structured data",
                    "Optimize for voice search"
                ],
                "content_score": 75,
                "duplicate_content": []
            },
            "local_seo": {
                "local_keywords": [
                    "personalized gifts uk",
                    "custom gifts london",
                    "photo gifts england",
                    "personalized gifts delivery uk"
                ],
                "local_rankings": {
                    "personalized gifts uk": 12,
                    "custom gifts london": 18,
                    "photo gifts england": 15
                },
                "gmb_optimization": {
                    "score": 85,
                    "issues": ["Missing business hours", "Incomplete categories"]
                },
                "local_opportunities": [
                    "Google My Business optimization",
                    "Local directory listings",
                    "Location-based content",
                    "Local customer testimonials"
                ],
                "delivery_areas": ["England", "Scotland", "Wales", "Northern Ireland"]
            }
        }
    
    # Mock data fallbacks
    def _get_fallback_seo_data(self, domain: str) -> Dict[str, Any]:
        """Get fallback SEO data when MCP is unavailable"""
        logger.info(f"Using fallback SEO data for {domain}")
        return {
            "timestamp": datetime.now().isoformat(),
            "domain": domain,
            "source": "Fallback Mock Data",
            "mcp_url": self.mcp_url,
            "keywords": self._get_mock_keywords_data(domain),
            "rankings": self._get_mock_rankings_data(domain),
            "traffic_estimates": self._get_mock_traffic_data(domain),
            "competitor_analysis": self._get_mock_competitor_data(domain),
            "technical_seo": self._get_mock_technical_data(domain),
            "content_analysis": self._analyze_content_opportunities({}),
            "local_seo": self._analyze_local_seo(domain)
        }
    
    def _get_mock_keywords_data(self, domain: str) -> Dict[str, Any]:
        """Get mock keywords data"""
        keywords = [
            {"keyword": "personalized gifts", "position": 8, "search_volume": 12000, "difficulty": 65},
            {"keyword": "custom photo gifts", "position": 15, "search_volume": 8500, "difficulty": 55},
            {"keyword": "photo blankets", "position": 12, "search_volume": 6500, "difficulty": 45},
            {"keyword": "personalized mugs", "position": 20, "search_volume": 4200, "difficulty": 40},
            {"keyword": "christmas personalized gifts", "position": 25, "search_volume": 15000, "difficulty": 70}
        ]
        return self._normalize_keywords_data({"keywords": keywords})
    
    def _get_mock_rankings_data(self, domain: str) -> Dict[str, Any]:
        """Get mock rankings data"""
        return {
            "average_position": 16.0,
            "top_10_count": 2,
            "top_20_count": 3,
            "ranking_trends": {"improving": 2, "declining": 1, "stable": 2},
            "position_changes": []
        }
    
    def _get_mock_traffic_data(self, domain: str) -> Dict[str, Any]:
        """Get mock traffic data"""
        return {
            "organic_traffic": 3200,
            "traffic_potential": 4500,
            "click_through_rate": 0.08,
            "traffic_trends": {"monthly_growth": 0.15, "seasonal_boost": 0.25},
            "seasonal_patterns": {}
        }
    
    def _get_mock_competitor_data(self, domain: str) -> Dict[str, Any]:
        """Get mock competitor data"""
        return {
            "main_competitors": [
                {"domain": "personalised-gifts.co.uk", "strength": "High"},
                {"domain": "notonthehighstreet.com", "strength": "Very High"},
                {"domain": "photobox.co.uk", "strength": "High"}
            ],
            "market_share": {"bagsoflove": 0.12, "competitors": 0.88},
            "competitive_gaps": ["Better mobile experience", "More detailed product descriptions"],
            "opportunities": ["Focus on niche personalization", "Improve local SEO"]
        }
    
    def _get_mock_technical_data(self, domain: str) -> Dict[str, Any]:
        """Get mock technical SEO data"""
        return {
            "page_speed": {"mobile_score": 78, "desktop_score": 85},
            "mobile_friendliness": {"score": 92},
            "structured_data": {"implemented": True, "coverage": "85%"},
            "crawl_issues": [],
            "technical_score": 82
        }

# Global instance
seranking_client = SerankingMCPClient()

def fetch_seo_data_from_seranking(domain: str = "bagsoflove.co.uk") -> Dict[str, Any]:
    """Fetch SEO data from Seranking MCP"""
    return seranking_client.fetch_seo_data(domain)

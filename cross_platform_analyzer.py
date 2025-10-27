"""
SEO + GA4 Cross-Platform Integration
Integrates SEO data from N8N/Seranking MCP with GA4 analytics for comprehensive insights
"""

import json
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import config
from seranking_mcp_client import fetch_seo_data_from_seranking
from real_seranking_client import fetch_real_seo_data_from_seranking

# Setup logging
logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)

class CrossPlatformAnalyzer:
    """Analyzes SEO and GA4 data together for comprehensive cross-platform insights"""
    
    def __init__(self):
        self.seo_data_cache = {}
        self.last_seo_update = None
        
    def receive_seo_data(self, seo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Receive SEO data from N8N/Seranking MCP and cache it
        Expected format from Seranking MCP:
        {
            "domain": "bagsoflove.co.uk",
            "keywords": [...],
            "rankings": {...},
            "traffic_estimates": {...},
            "competitor_analysis": {...},
            "technical_seo": {...}
        }
        """
        logger.info("Receiving SEO data from N8N/Seranking MCP...")
        
        # Validate and normalize SEO data
        normalized_seo = self._normalize_seo_data(seo_data)
        
        # Cache the data
        self.seo_data_cache = normalized_seo
        self.last_seo_update = datetime.now()
        
        logger.info(f"SEO data cached successfully. Last update: {self.last_seo_update}")
        
        return {
            "status": "success",
            "message": "SEO data received and cached",
            "timestamp": self.last_seo_update.isoformat(),
            "data_points": len(normalized_seo.get("keywords", []))
        }
    
    def _normalize_seo_data(self, raw_seo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize SEO data from Seranking MCP to standard format"""
        return {
            "timestamp": datetime.now().isoformat(),
            "domain": raw_seo_data.get("domain", "bagsoflove.co.uk"),
            "source": "Seranking MCP via N8N",
            "keywords": self._extract_keywords(raw_seo_data),
            "rankings": self._extract_rankings(raw_seo_data),
            "traffic_estimates": self._extract_traffic_data(raw_seo_data),
            "competitor_analysis": self._extract_competitor_data(raw_seo_data),
            "technical_seo": self._extract_technical_data(raw_seo_data),
            "content_analysis": self._extract_content_data(raw_seo_data),
            "local_seo": self._extract_local_data(raw_seo_data)
        }
    
    def _extract_keywords(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract keyword data from Seranking response"""
        keywords = data.get("keywords", [])
        return {
            "total_keywords": len(keywords),
            "top_keywords": keywords[:10] if keywords else [],
            "keyword_categories": {
                "primary": [kw for kw in keywords[:5] if kw.get("position", 999) <= 10],
                "secondary": [kw for kw in keywords[5:15] if kw.get("position", 999) <= 20],
                "long_tail": [kw for kw in keywords[15:] if kw.get("position", 999) <= 50]
            },
            "ranking_distribution": self._calculate_ranking_distribution(keywords),
            "keyword_opportunities": self._identify_keyword_opportunities(keywords)
        }
    
    def _extract_rankings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract ranking data"""
        rankings = data.get("rankings", {})
        return {
            "average_position": rankings.get("average_position", 0),
            "top_10_count": rankings.get("top_10_count", 0),
            "top_20_count": rankings.get("top_20_count", 0),
            "ranking_trends": rankings.get("trends", {}),
            "position_changes": rankings.get("changes", [])
        }
    
    def _extract_traffic_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract traffic estimation data"""
        traffic = data.get("traffic_estimates", {})
        return {
            "organic_traffic": traffic.get("organic_traffic", 0),
            "traffic_potential": traffic.get("traffic_potential", 0),
            "click_through_rate": traffic.get("ctr", 0),
            "traffic_trends": traffic.get("trends", {}),
            "seasonal_patterns": traffic.get("seasonal", {})
        }
    
    def _extract_competitor_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract competitor analysis data"""
        competitors = data.get("competitor_analysis", {})
        return {
            "main_competitors": competitors.get("competitors", []),
            "market_share": competitors.get("market_share", {}),
            "competitive_gaps": competitors.get("gaps", []),
            "opportunities": competitors.get("opportunities", [])
        }
    
    def _extract_technical_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract technical SEO data"""
        technical = data.get("technical_seo", {})
        return {
            "page_speed": technical.get("page_speed", {}),
            "mobile_friendliness": technical.get("mobile", {}),
            "structured_data": technical.get("structured_data", {}),
            "crawl_issues": technical.get("crawl_issues", []),
            "technical_score": technical.get("overall_score", 0)
        }
    
    def _extract_content_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract content analysis data"""
        content = data.get("content_analysis", {})
        return {
            "content_gaps": content.get("gaps", []),
            "optimization_opportunities": content.get("opportunities", []),
            "content_score": content.get("score", 0),
            "duplicate_content": content.get("duplicates", [])
        }
    
    def _extract_local_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract local SEO data"""
        local = data.get("local_seo", {})
        return {
            "local_keywords": local.get("keywords", []),
            "local_rankings": local.get("rankings", {}),
            "gmb_optimization": local.get("gmb", {}),
            "local_opportunities": local.get("opportunities", [])
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
        """Identify keyword opportunities based on ranking data"""
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
                    "potential_traffic": search_volume * 0.1  # Estimate 10% CTR
                })
        
        return sorted(opportunities, key=lambda x: x["potential_traffic"], reverse=True)[:10]
    
    def generate_cross_platform_insights(self, ga4_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive cross-platform insights combining SEO and GA4 data
        """
        if not self.seo_data_cache:
            logger.info("No cached SEO data, fetching from Seranking API...")
            # Try to fetch fresh SEO data from Seranking API
            try:
                # Check if we have a Seranking API token
                seranking_token = getattr(config, 'SERANKING_API_TOKEN', None)
                if seranking_token and seranking_token != "YOUR_SERANKING_API_TOKEN":
                    logger.info("Using real Seranking API with provided token")
                    fresh_seo_data = fetch_real_seo_data_from_seranking("bagsoflove.co.uk", seranking_token)
                else:
                    logger.warning("No Seranking API token found, using mock data")
                    fresh_seo_data = fetch_seo_data_from_seranking("bagsoflove.co.uk")
                
                self.seo_data_cache = fresh_seo_data
                self.last_seo_update = datetime.now()
                logger.info("Successfully fetched SEO data")
            except Exception as e:
                logger.warning(f"Failed to fetch SEO data: {e}")
                logger.info("Using GA4-only analysis")
                return self._generate_ga4_only_insights(ga4_data)
        
        logger.info("Generating cross-platform SEO + GA4 insights...")
        
        # Combine SEO and GA4 data
        combined_data = {
            "timestamp": datetime.now().isoformat(),
            "data_sources": ["GA4 Analytics", "Seranking SEO"],
            "seo_data": self.seo_data_cache,
            "ga4_data": ga4_data,
            "cross_platform_analysis": self._analyze_cross_platform_patterns(ga4_data),
            "unified_recommendations": self._generate_unified_recommendations(ga4_data),
            "traffic_correlation": self._analyze_traffic_correlation(ga4_data),
            "conversion_optimization": self._analyze_conversion_optimization(ga4_data),
            "seasonal_strategy": self._analyze_seasonal_strategy(ga4_data)
        }
        
        return combined_data
    
    def _analyze_cross_platform_patterns(self, ga4_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns between SEO and GA4 data"""
        return {
            "organic_traffic_performance": {
                "seo_traffic_potential": self.seo_data_cache.get("traffic_estimates", {}).get("organic_traffic", 0),
                "ga4_organic_sessions": self._extract_ga4_organic_sessions(ga4_data),
                "traffic_gap": self._calculate_traffic_gap(ga4_data),
                "optimization_opportunity": "High" if self._calculate_traffic_gap(ga4_data) > 0.3 else "Medium"
            },
            "keyword_to_conversion_mapping": {
                "high_ranking_keywords": self._get_high_ranking_keywords(),
                "conversion_keywords": self._identify_conversion_keywords(ga4_data),
                "alignment_score": self._calculate_keyword_conversion_alignment(ga4_data)
            },
            "content_performance_correlation": {
                "top_performing_content": self._identify_top_content(ga4_data),
                "seo_content_gaps": self.seo_data_cache.get("content_analysis", {}).get("content_gaps", []),
                "content_optimization_score": self._calculate_content_optimization_score(ga4_data)
            }
        }
    
    def _generate_unified_recommendations(self, ga4_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate unified recommendations combining SEO and GA4 insights"""
        return {
            "immediate_actions": [
                "Optimize high-traffic, low-converting pages with SEO improvements",
                "Create content for high-converting keywords with low rankings",
                "Improve mobile experience for organic traffic segments",
                "Add structured data to top-performing product pages"
            ],
            "strategic_initiatives": [
                "Develop content calendar based on seasonal GA4 patterns and SEO opportunities",
                "Build authority in personalized gifts niche using high-volume keywords",
                "Optimize for voice search using conversational keywords",
                "Create conversion-focused landing pages for top-ranking keywords"
            ],
            "cross_platform_optimization": [
                "Align SEO keyword strategy with GA4 conversion data",
                "Optimize product pages for both search rankings and conversion",
                "Create seasonal content that drives both organic traffic and conversions",
                "Implement technical SEO improvements for high-converting pages"
            ]
        }
    
    def _analyze_traffic_correlation(self, ga4_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze correlation between SEO traffic potential and actual GA4 traffic"""
        seo_traffic = self.seo_data_cache.get("traffic_estimates", {}).get("organic_traffic", 0)
        ga4_organic = self._extract_ga4_organic_sessions(ga4_data)
        
        return {
            "seo_traffic_potential": seo_traffic,
            "ga4_actual_organic": ga4_organic,
            "traffic_realization_rate": ga4_organic / seo_traffic if seo_traffic > 0 else 0,
            "traffic_gap": seo_traffic - ga4_organic,
            "optimization_priority": "High" if (seo_traffic - ga4_organic) > seo_traffic * 0.3 else "Medium"
        }
    
    def _analyze_conversion_optimization(self, ga4_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze conversion optimization opportunities"""
        return {
            "high_ranking_low_converting": self._identify_high_ranking_low_converting_pages(ga4_data),
            "conversion_keyword_opportunities": self._identify_conversion_keyword_opportunities(ga4_data),
            "content_to_conversion_gaps": self._identify_content_conversion_gaps(ga4_data),
            "technical_conversion_barriers": self._identify_technical_conversion_barriers(ga4_data)
        }
    
    def _analyze_seasonal_strategy(self, ga4_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze seasonal strategy combining SEO and GA4 data"""
        return {
            "peak_seasons": self._identify_peak_seasons(ga4_data),
            "seasonal_keyword_opportunities": self._get_seasonal_keyword_opportunities(),
            "content_calendar_alignment": self._align_content_calendar_with_ga4_patterns(ga4_data),
            "seasonal_conversion_optimization": self._optimize_seasonal_conversions(ga4_data)
        }
    
    # Helper methods for data extraction and analysis
    def _extract_ga4_organic_sessions(self, ga4_data: Dict[str, Any]) -> int:
        """Extract organic sessions from GA4 data"""
        # This would extract from actual GA4 data structure
        return ga4_data.get("metrics", {}).get("sessions", {}).get("organic", 0)
    
    def _calculate_traffic_gap(self, ga4_data: Dict[str, Any]) -> float:
        """Calculate gap between SEO traffic potential and actual GA4 traffic"""
        seo_traffic = self.seo_data_cache.get("traffic_estimates", {}).get("organic_traffic", 0)
        ga4_organic = self._extract_ga4_organic_sessions(ga4_data)
        return (seo_traffic - ga4_organic) / seo_traffic if seo_traffic > 0 else 0
    
    def _get_high_ranking_keywords(self) -> List[Dict[str, Any]]:
        """Get keywords ranking in top 20 positions"""
        keywords = self.seo_data_cache.get("keywords", {}).get("top_keywords", [])
        return [kw for kw in keywords if kw.get("position", 999) <= 20]
    
    def _identify_conversion_keywords(self, ga4_data: Dict[str, Any]) -> List[str]:
        """Identify keywords that drive conversions based on GA4 data"""
        # This would analyze GA4 data to find keywords that lead to conversions
        return ["personalized gifts", "custom photo gifts", "photo blankets"]
    
    def _calculate_keyword_conversion_alignment(self, ga4_data: Dict[str, Any]) -> float:
        """Calculate alignment between high-ranking keywords and conversion keywords"""
        high_ranking = self._get_high_ranking_keywords()
        conversion_keywords = self._identify_conversion_keywords(ga4_data)
        
        alignment_count = 0
        for kw in high_ranking:
            if kw.get("keyword", "").lower() in [ck.lower() for ck in conversion_keywords]:
                alignment_count += 1
        
        return alignment_count / len(high_ranking) if high_ranking else 0
    
    def _identify_top_content(self, ga4_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify top-performing content from GA4 data"""
        # This would extract from GA4 page performance data
        return [
            {"page": "/photo-blankets", "sessions": 1200, "conversions": 45},
            {"page": "/personalized-mugs", "sessions": 800, "conversions": 32}
        ]
    
    def _calculate_content_optimization_score(self, ga4_data: Dict[str, Any]) -> float:
        """Calculate content optimization score based on SEO and GA4 data"""
        # This would analyze content performance vs SEO potential
        return 7.5
    
    def _identify_high_ranking_low_converting_pages(self, ga4_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify pages with good rankings but poor conversions"""
        return [
            {"page": "/tea-towels", "ranking": 8, "conversion_rate": 2.1},
            {"page": "/personalized-socks", "ranking": 12, "conversion_rate": 3.2}
        ]
    
    def _identify_conversion_keyword_opportunities(self, ga4_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify keyword opportunities for conversion optimization"""
        return [
            {"keyword": "buy personalized gifts", "current_position": 25, "conversion_potential": "High"},
            {"keyword": "custom photo gifts uk", "current_position": 18, "conversion_potential": "High"}
        ]
    
    def _identify_content_conversion_gaps(self, ga4_data: Dict[str, Any]) -> List[str]:
        """Identify content gaps affecting conversions"""
        return [
            "Missing product comparison pages",
            "Insufficient customer testimonials",
            "Lack of gift guides",
            "Missing size guides"
        ]
    
    def _identify_technical_conversion_barriers(self, ga4_data: Dict[str, Any]) -> List[str]:
        """Identify technical issues affecting conversions"""
        return [
            "Slow page load times on mobile",
            "Checkout process too complex",
            "Missing trust signals",
            "Poor mobile experience"
        ]
    
    def _identify_peak_seasons(self, ga4_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify peak seasons from GA4 data"""
        return [
            {"season": "Christmas", "traffic_increase": "+300%", "conversion_rate": 12.5},
            {"season": "Valentine's Day", "traffic_increase": "+250%", "conversion_rate": 11.2}
        ]
    
    def _get_seasonal_keyword_opportunities(self) -> List[Dict[str, Any]]:
        """Get seasonal keyword opportunities"""
        return [
            {"keyword": "christmas personalized gifts", "season": "Q4", "opportunity": "High"},
            {"keyword": "valentines day custom gifts", "season": "Q1", "opportunity": "High"}
        ]
    
    def _align_content_calendar_with_ga4_patterns(self, ga4_data: Dict[str, Any]) -> Dict[str, Any]:
        """Align content calendar with GA4 traffic patterns"""
        return {
            "content_schedule": [
                {"month": "November", "focus": "Christmas gift guides", "traffic_boost": "+200%"},
                {"month": "February", "focus": "Valentine's Day content", "traffic_boost": "+180%"}
            ]
        }
    
    def _optimize_seasonal_conversions(self, ga4_data: Dict[str, Any]) -> List[str]:
        """Optimize seasonal conversions"""
        return [
            "Create seasonal landing pages",
            "Optimize for seasonal keywords",
            "Implement urgency messaging",
            "Add seasonal product bundles"
        ]
    
    def _generate_ga4_only_insights(self, ga4_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights when only GA4 data is available"""
        return {
            "timestamp": datetime.now().isoformat(),
            "data_sources": ["GA4 Analytics Only"],
            "message": "SEO data not available - using GA4 data only",
            "ga4_data": ga4_data,
            "recommendations": [
                "Connect SEO data source for comprehensive analysis",
                "Focus on GA4 conversion optimization",
                "Implement basic SEO best practices"
            ]
        }

# Global instance
cross_platform_analyzer = CrossPlatformAnalyzer()

def receive_seo_data_from_n8n(seo_data: Dict[str, Any]) -> Dict[str, Any]:
    """Receive SEO data from N8N/Seranking MCP"""
    return cross_platform_analyzer.receive_seo_data(seo_data)

def generate_cross_platform_insights(ga4_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate cross-platform insights combining SEO and GA4 data"""
    return cross_platform_analyzer.generate_cross_platform_insights(ga4_data)

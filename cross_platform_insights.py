"""
Enhanced AI Insights Generator for Cross-Platform SEO + GA4 Analysis
Provides comprehensive insights combining SEO data from Seranking MCP with GA4 analytics
"""

import anthropic
import config
import json
import logging
import time
from typing import Dict, List, Any, Optional
from cross_platform_analyzer import cross_platform_analyzer

# Setup logging
logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)

def generate_cross_platform_insights(
    ga4_data: Dict[str, Any],
    seo_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate comprehensive cross-platform insights combining SEO and GA4 data
    
    Args:
        ga4_data: GA4 analytics data
        seo_data: SEO data from Seranking MCP (optional)
    
    Returns:
        Comprehensive insights combining both data sources
    """
    
    # Check if we have a valid API key
    if not config.ANTHROPIC_API_KEY or config.ANTHROPIC_API_KEY.startswith("sk-ant-api03-test"):
        logger.info("Using mock cross-platform insights (no valid API key)")
        return generate_mock_cross_platform_insights(ga4_data, seo_data)
    
    try:
        # Initialize Claude client
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        
        # Generate cross-platform analysis
        cross_platform_data = cross_platform_analyzer.generate_cross_platform_insights(ga4_data)
        
        # Build comprehensive context for Claude
        context = build_cross_platform_context(cross_platform_data)
        
        logger.info("Generating cross-platform AI insights...")
        start_time = time.time()
        
        # Call Claude API with enhanced prompt
        message = client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=2000,  # Increased for comprehensive analysis
            temperature=0.3,
            messages=[{
                "role": "user",
                "content": context
            }]
        )
        
        # Parse Claude's response
        response_text = message.content[0].text
        insights = parse_cross_platform_response(response_text)
        
        # Add metadata
        insights["metadata"] = {
            "model": config.CLAUDE_MODEL,
            "generation_time": round(time.time() - start_time, 2),
            "data_sources": cross_platform_data.get("data_sources", []),
            "timestamp": time.time(),
            "analysis_type": "cross_platform_seo_ga4"
        }
        
        logger.info(f"Cross-platform AI insights generated in {insights['metadata']['generation_time']} seconds")
        
        return insights
        
    except Exception as e:
        logger.error(f"Error generating cross-platform insights: {e}")
        return generate_mock_cross_platform_insights(ga4_data, seo_data)

def build_cross_platform_context(cross_platform_data: Dict[str, Any]) -> str:
    """Build comprehensive context for cross-platform analysis"""
    
    context = f"""
You are an expert digital marketing analyst specializing in cross-platform SEO and GA4 analytics for e-commerce businesses.

BUSINESS CONTEXT:
- Website: bagsoflove.co.uk
- Business: Personalized gifts and custom photo products
- Target Market: UK consumers seeking unique, personalized gifts
- Products: Photo blankets, personalized mugs, custom canvas prints, photo socks, tea towels

CROSS-PLATFORM DATA ANALYSIS:

GA4 ANALYTICS DATA:
{json.dumps(cross_platform_data.get('ga4_data', {}), indent=2)}

SEO DATA (from Seranking MCP):
{json.dumps(cross_platform_data.get('seo_data', {}), indent=2)}

CROSS-PLATFORM ANALYSIS:
{json.dumps(cross_platform_data.get('cross_platform_analysis', {}), indent=2)}

TRAFFIC CORRELATION:
{json.dumps(cross_platform_data.get('traffic_correlation', {}), indent=2)}

CONVERSION OPTIMIZATION:
{json.dumps(cross_platform_data.get('conversion_optimization', {}), indent=2)}

SEASONAL STRATEGY:
{json.dumps(cross_platform_data.get('seasonal_strategy', {}), indent=2)}

UNIFIED RECOMMENDATIONS:
{json.dumps(cross_platform_data.get('unified_recommendations', {}), indent=2)}

ANALYSIS REQUIREMENTS:

1. CRITICAL CROSS-PLATFORM ISSUE:
   - Identify the most critical issue affecting both SEO and conversion performance
   - Provide specific metrics and impact assessment
   - Explain the cross-platform implications

2. GROWTH OPPORTUNITY:
   - Identify the biggest opportunity combining SEO and GA4 insights
   - Provide specific metrics and potential lift
   - Explain how SEO and GA4 work together for this opportunity

3. UNIFIED ACTION PLAN:
   - Provide 3 priority actions that address both SEO and conversion optimization
   - Include specific metrics and expected impact
   - Explain the cross-platform synergy

4. SEASONAL OPTIMIZATION:
   - Provide seasonal strategy combining SEO keyword trends with GA4 traffic patterns
   - Include specific timing and content recommendations
   - Explain how to maximize both organic traffic and conversions

5. TECHNICAL OPTIMIZATION:
   - Identify technical issues affecting both SEO rankings and conversion rates
   - Provide specific fixes and expected improvements
   - Explain the cross-platform impact

RESPONSE FORMAT:
Return a JSON object with this exact structure:
{{
    "critical_cross_platform_issue": {{
        "title": "Specific issue title",
        "description": "Detailed description of the cross-platform issue",
        "impact": "Specific impact on both SEO and conversions",
        "metrics": {{
            "seo_impact": "Specific SEO metrics affected",
            "conversion_impact": "Specific conversion metrics affected",
            "combined_impact": "Overall business impact"
        }},
        "why": ["Reason 1", "Reason 2", "Reason 3"]
    }},
    "growth_opportunity": {{
        "title": "Specific opportunity title",
        "description": "Detailed description of the cross-platform opportunity",
        "potential_lift": "Specific expected improvement",
        "metrics": {{
            "seo_lift": "Expected SEO improvement",
            "conversion_lift": "Expected conversion improvement",
            "combined_lift": "Overall business lift"
        }},
        "rationale": "Why this opportunity exists",
        "why": ["Reason 1", "Reason 2", "Reason 3"]
    }},
    "unified_action_plan": {{
        "priority_1": "Specific action combining SEO and GA4 optimization",
        "priority_2": "Specific action combining SEO and GA4 optimization", 
        "priority_3": "Specific action combining SEO and GA4 optimization",
        "expected_impact": "Combined expected impact",
        "timeline": "Recommended implementation timeline",
        "cross_platform_synergy": "How SEO and GA4 work together"
    }},
    "seasonal_optimization": {{
        "peak_seasons": ["Season 1", "Season 2"],
        "keyword_strategy": "Seasonal keyword optimization strategy",
        "content_calendar": "Content calendar recommendations",
        "conversion_optimization": "Seasonal conversion optimization",
        "timing": "Specific timing recommendations"
    }},
    "technical_optimization": {{
        "critical_fixes": ["Fix 1", "Fix 2", "Fix 3"],
        "seo_improvements": "Specific SEO technical improvements",
        "conversion_improvements": "Specific conversion technical improvements",
        "expected_impact": "Expected combined impact",
        "implementation_priority": "High/Medium/Low"
    }}
}}

Focus on actionable, specific insights that combine SEO and GA4 data for maximum business impact.
"""
    
    return context

def parse_cross_platform_response(response_text: str) -> Dict[str, Any]:
    """Parse Claude's response for cross-platform insights"""
    try:
        # Extract JSON from response
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No JSON found in response")
        
        json_str = response_text[start_idx:end_idx]
        insights = json.loads(json_str)
        
        # Validate required fields
        required_fields = [
            "critical_cross_platform_issue",
            "growth_opportunity", 
            "unified_action_plan",
            "seasonal_optimization",
            "technical_optimization"
        ]
        
        for field in required_fields:
            if field not in insights:
                logger.warning(f"Missing required field: {field}")
                insights[field] = {"error": "Field not provided"}
        
        return insights
        
    except Exception as e:
        logger.error(f"Error parsing cross-platform response: {e}")
        return generate_mock_cross_platform_insights({}, {})

def generate_mock_cross_platform_insights(ga4_data: Dict[str, Any], seo_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate mock cross-platform insights when API is not available"""
    return {
        "critical_cross_platform_issue": {
            "title": "Mobile Experience Gap Between SEO and Conversions",
            "description": "High mobile search rankings but poor mobile conversion rates indicate technical issues affecting both SEO performance and user experience.",
            "impact": "30% potential revenue loss from mobile traffic",
            "metrics": {
                "seo_impact": "Mobile rankings at risk due to poor user experience signals",
                "conversion_impact": "Mobile conversion rate 40% below desktop",
                "combined_impact": "£50K+ monthly revenue opportunity"
            },
            "why": [
                "Mobile page speed issues affecting rankings",
                "Poor mobile checkout experience",
                "Inconsistent mobile user experience"
            ]
        },
        "growth_opportunity": {
            "title": "Seasonal Keyword + Conversion Optimization",
            "description": "High-volume seasonal keywords with low current rankings present massive opportunity for both organic traffic growth and conversion optimization.",
            "potential_lift": "200% increase in seasonal revenue",
            "metrics": {
                "seo_lift": "Top 10 rankings for 15+ seasonal keywords",
                "conversion_lift": "25% improvement in seasonal conversion rates",
                "combined_lift": "£200K+ additional seasonal revenue"
            },
            "rationale": "Seasonal keywords have high commercial intent and low competition during off-peak periods",
            "why": [
                "Untapped seasonal keyword opportunities",
                "High commercial intent during peak seasons",
                "Competitive advantage through early optimization"
            ]
        },
        "unified_action_plan": {
            "priority_1": "Optimize mobile experience for both SEO rankings and conversion rates",
            "priority_2": "Create seasonal content calendar targeting high-converting keywords",
            "priority_3": "Implement technical SEO improvements on high-converting pages",
            "expected_impact": "50% improvement in mobile conversions, 100% increase in organic traffic",
            "timeline": "3-month implementation with immediate mobile fixes",
            "cross_platform_synergy": "SEO improvements drive qualified traffic, GA4 optimization maximizes conversions"
        },
        "seasonal_optimization": {
            "peak_seasons": ["Christmas (Nov-Dec)", "Valentine's Day (Jan-Feb)", "Mother's Day (Mar-May)"],
            "keyword_strategy": "Target high-volume seasonal keywords with commercial intent",
            "content_calendar": "Create gift guides and seasonal landing pages 2 months before peak seasons",
            "conversion_optimization": "Implement urgency messaging and seasonal product bundles",
            "timeline": "Start optimization 3 months before each peak season"
        },
        "technical_optimization": {
            "critical_fixes": [
                "Improve mobile page speed to under 3 seconds",
                "Optimize checkout process for mobile users",
                "Add structured data for product pages"
            ],
            "seo_improvements": "Core Web Vitals optimization, mobile-first indexing compliance",
            "conversion_improvements": "Streamlined checkout, trust signals, mobile UX optimization",
            "expected_impact": "20% improvement in mobile rankings, 30% increase in mobile conversions",
            "implementation_priority": "High - immediate impact on both SEO and conversions"
        },
        "metadata": {
            "model": "mock-cross-platform",
            "generation_time": 0.1,
            "data_sources": ["GA4 Analytics", "Mock SEO Data"],
            "timestamp": time.time(),
            "analysis_type": "mock_cross_platform_seo_ga4"
        }
    }

# Integration function for main API
def get_cross_platform_insights(ga4_data: Dict[str, Any], seo_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Main function to get cross-platform insights"""
    return generate_cross_platform_insights(ga4_data, seo_data)




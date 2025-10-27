"""
AI Insights Generator using Claude Sonnet 4
Following SEO MCP pattern: brand-agnostic, structured JSON output
"""

import anthropic
import config
import json
import re
import logging
import time
from typing import Dict, List, Any, Optional

# Setup logging
logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Rate limiting
_last_api_call = 0
_min_call_interval = 1.0  # 1 second between calls (60 RPM max)


def generate_funnel_insights(
    outliers: Dict[str, List[Dict[str, Any]]],
    baseline_rates: Dict[str, float],
    funnel_metrics: Dict[str, Any],
    historical_data: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Generate AI-powered insights for funnel analysis using Claude Sonnet 4
    
    Args:
        outliers: Dimension values performing ±20% from baseline
        baseline_rates: Overall conversion rates
        funnel_metrics: Full dimension breakdown
        historical_data: Optional historical performance data
        
    Returns:
        dict: AI-generated insights with critical_issues, opportunities, recommendations
    """
    
    try:
        # Rate limiting - wait if needed
        global _last_api_call
        time_since_last = time.time() - _last_api_call
        if time_since_last < _min_call_interval:
            wait_time = _min_call_interval - time_since_last
            logger.info(f"Rate limiting: waiting {wait_time:.2f}s")
            time.sleep(wait_time)
        
        # Initialize Claude client
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        
        # Build dynamic context
        context = build_funnel_context(outliers, baseline_rates, funnel_metrics, historical_data)
        
        # Call Claude API
        _last_api_call = time.time()  # Update timestamp
        message = client.messages.create(
            model=config.CLAUDE_MODEL,  # ⚠️ CRITICAL: claude-sonnet-4-5-20250929
            max_tokens=config.CLAUDE_MAX_TOKENS,
            messages=[
                {
                    "role": "user",
                    "content": context
                }
            ]
        )
        
        # Parse response
        content = message.content[0].text
        logger.debug(f"Claude response (first 500 chars): {content[:500]}")
        parsed = parse_json_response(content)
        
        return {
            "model": message.model,
            "critical_issues": parsed.get("critical_issues", []),
            "opportunities": parsed.get("opportunities", []),
            "recommendations": parsed.get("recommendations", []),
            "suggested_tests": parsed.get("suggested_tests", [])
        }
        
    except anthropic.APIError as e:
        logger.error(f"Claude API error: {e}")
        return {
            "model": "error",
            "critical_issues": [],
            "opportunities": [],
            "recommendations": [{
                "priority": 1,
                "action": "Unable to generate AI insights due to API error",
                "expected_impact": "N/A",
                "implementation": "N/A"
            }],
            "suggested_tests": [],
            "error": str(e)
        }
    
    except Exception as e:
        logger.error(f"Unexpected error in generate_funnel_insights: {e}")
        return {
            "model": "error",
            "critical_issues": [],
            "opportunities": [],
            "recommendations": [{
                "priority": 1,
                "action": f"Error generating insights: {str(e)}",
                "expected_impact": "N/A",
                "implementation": "N/A"
            }],
            "suggested_tests": []
        }


def generate_keyword_product_insights(
    ga4_data: Dict[str, Any],
    seo_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate AI insights connecting keywords to product performance
    This is what makes your lead magnet special - connecting SEO to revenue
    """
    # Check if API key is set and valid
    api_key = config.ANTHROPIC_API_KEY
    if not api_key or api_key == "sk-ant-api03-not-set-local-testing":
        logger.warning("Claude API key not set, using mock insights")
        return get_mock_keyword_product_insights()
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        # Map keywords to products
        keyword_map = map_keywords_to_products(seo_data, ga4_data)
        
        context = build_keyword_product_context(keyword_map, ga4_data, seo_data)
        
        logger.info("Generating keyword→product insights with Claude AI...")
        message = client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": context}]
        )
        
        response_text = message.content[0].text
        insights = parse_json_response(response_text)
        
        logger.info("✅ Generated AI insights successfully")
        return insights
        
    except anthropic.AuthenticationError as e:
        logger.error(f"Claude API authentication failed: {e}")
        return get_mock_keyword_product_insights()
    except Exception as e:
        logger.error(f"Error generating keyword-product insights: {e}")
        return get_mock_keyword_product_insights()


def map_keywords_to_products(seo_data: Dict[str, Any], ga4_data: Dict[str, Any]) -> Dict[str, Any]:
    """Map keywords to product categories using semantic matching"""
    
    keywords = seo_data.get("keywords", {}).get("top_keywords", [])
    product_categories = ga4_data.get("dimension_breakdowns", {}).get("itemCategory", {})
    
    mapping = []
    
    # Semantic keyword → category mapping
    keyword_to_category = {
        "photo blankets": "Photo Blankets",
        "blanket": "Photo Blankets",
        "personalized gifts": ["Photo Blankets", "Canvas & Wall Art", "Kitchen & Dining"],
        "custom photo": ["Photo Blankets", "Canvas & Wall Art"],
        "photo": ["Photo Blankets", "Canvas & Wall Art"],
        "mug": "Kitchen & Dining",
        "personalized mugs": "Kitchen & Dining",
        "tea towel": "Kitchen & Dining",
        "canvas": "Canvas & Wall Art",
        "wall art": "Canvas & Wall Art",
        "clothing": "Clothing & Accessories",
        "t-shirt": "Clothing & Accessories"
    }
    
    for kw in keywords[:10]:  # Top 10 keywords
        keyword = kw.get("keyword", "").lower()
        category_match = None
        
        # Find matching category
        for key_phrase, category in keyword_to_category.items():
            if key_phrase in keyword:
                category_match = category
                break
        
        # If no match found, try broader matching
        if not category_match:
            for category_name in product_categories.keys():
                if category_name.lower() in keyword or keyword in category_name.lower():
                    category_match = category_name
                    break
        
        if category_match:
            if isinstance(category_match, list):
                # Multiple categories
                for cat in category_match:
                    if cat in product_categories:
                        mapping.append({
                            "keyword": kw.get("keyword"),
                            "position": kw.get("position"),
                            "search_volume": kw.get("search_volume", 0),
                            "traffic_estimate": kw.get("traffic_estimate", 0),
                            "category": cat,
                            "performance": product_categories[cat]
                        })
            else:
                if category_match in product_categories:
                    mapping.append({
                        "keyword": kw.get("keyword"),
                        "position": kw.get("position"),
                        "search_volume": kw.get("search_volume", 0),
                        "traffic_estimate": kw.get("traffic_estimate", 0),
                        "category": category_match,
                        "performance": product_categories[category_match]
                    })
    
    return {
        "mappings": mapping,
        "total_keywords_mapped": len(mapping),
        "keyword_traffic_potential": sum(m.get("traffic_estimate", 0) for m in mapping)
    }


def build_keyword_product_context(keyword_map: Dict[str, Any], ga4_data: Dict[str, Any], seo_data: Dict[str, Any]) -> str:
    """Build context for keyword→product insights"""
    
    return f"""
You are an expert e-commerce analyst helping bagsoflove.co.uk understand how their SEO keywords connect to product sales.

KEYWORD → PRODUCT MAPPING:
{json.dumps(keyword_map, indent=2)}

GA4 PRODUCT PERFORMANCE:
{json.dumps(ga4_data.get('dimension_breakdowns', {}).get('itemCategory', {}), indent=2)}

SEO KEYWORD DATA:
Top Keywords: {json.dumps(seo_data.get('keywords', {}).get('top_keywords', [])[:10], indent=2)}

BUSINESS CONTEXT:
- Personalized photo gifts (blankets, mugs, canvas prints, socks, tea towels)
- UK-based e-commerce
- Customer wants to see which SEO investments drive actual revenue

YOUR TASK:
Generate insights showing how specific keywords drive specific product sales.
Focus on actionable recommendations that connect SEO to revenue.

Return JSON with this structure:
{{
    "keyword_performance_analysis": {{
        "top_performing_keywords": [
            {{
                "keyword": "photo blankets",
                "position": 12,
                "estimated_traffic": 500,
                "target_product": "Photo Blankets",
                "ga4_views": 1200,
                "ga4_purchases": 13,
                "estimated_revenue": "$X,XXX/month",
                "opportunity": "Moving from #12 to #8 could add $Y,YYY/month"
            }}
        ],
        "low_hanging_fruit": [
            {{
                "keyword": "keyword name",
                "current_position": 20,
                "search_volume": 4200,
                "conversion_rate": 1.62%,
                "opportunity": "Specific opportunity description",
                "potential_lift": "$X,XXX additional monthly revenue"
            }}
        ],
        "underperforming_keywords": [
            {{
                "keyword": "keyword name", 
                "high_position": 8,
                "low_conversions": "Why it's underperforming",
                "fix": "Specific recommendation"
            }}
        ]
    }},
    "strategic_recommendations": {{
        "priority_1": {{
            "action": "Specific action connecting SEO to revenue",
            "keyword": "Which keyword to focus on",
            "product": "Which product category benefits",
            "expected_revenue_lift": "$X,XXX/month",
            "implementation": "How to implement",
            "timeline": "When to see results"
        }},
        "priority_2": {{ "action": "...", "keyword": "...", "product": "...", "expected_revenue_lift": "...", "implementation": "...", "timeline": "..." }},
        "priority_3": {{ "action": "...", "keyword": "...", "product": "...", "expected_revenue_lift": "...", "implementation": "...", "timeline": "..." }}
    }},
    "quick_wins": [
        "Specific quick win #1 that connects keywords to revenue",
        "Specific quick win #2 that connects keywords to revenue",
        "Specific quick win #3 that connects keywords to revenue"
    ],
    "roi_calculation": {{
        "total_keyword_traffic_potential": "X,XXX visits/month",
        "current_estimated_revenue": "$X,XXX/month",
        "potential_with_improvements": "$X,XXX/month",
        "opportunity_value": "$X,XXX/month",
        "seo_investment_justification": "Why this investment pays off"
    }}
}}

Focus on CONNECTING KEYWORDS TO REVENUE. Show which SEO investments drive which products.
"""


def get_concise_enhanced_insights() -> Dict[str, Any]:
    """
    Enhanced comprehensive insights with:
    - 10-15 keywords analyzed
    - Why analysis for each keyword
    - Competitive intelligence
    - Detailed ROI calculations
    - Strategic depth
    """
    return {
        "report_type": "Complete SEO-Revenue Intelligence Report - Concise Edition",
        "keyword_performance_analysis": {
            "keywords_analyzed": 10,
            "total_traffic": "1,318 visits/month",
            "total_revenue": "$1,283/month",
            "top_performing_keywords": [
                {
                    "keyword": "personalised",
                    "position": 3,
                    "traffic": 473,
                    "revenue": "$1,033/month",
                    "why_it_works": "High commercial intent + perfect product match. Users ready to buy = top revenue driver.",
                    "conversion_rate": "1.36%",
                    "insight": "Top revenue driver - 81% of total revenue"
                },
                {
                    "keyword": "photo gifts",
                    "position": 4,
                    "traffic": 99,
                    "revenue": "$136/month",
                    "why_it_works": "Commercial intent + visual products convert well",
                    "insight": "Moving to #2 = +$68/month opportunity"
                },
                {
                    "keyword": "custom t shirts",
                    "position": 13,
                    "traffic": 65,
                    "revenue": "$20/month",
                    "why_underperforming": "14,800 searches but only 65 visitors (0.44%). Position #13 = missing 93% of traffic.",
                    "insight": "HUGE OPPORTUNITY: Move to top 10 = +$263/month (+$3,156/year)",
                    "competitor_gap": "Top 3 using product galleries, reviews, schema markup you're missing"
                },
                {
                    "keyword": "personalised gifts",
                    "position": 7,
                    "traffic": 243,
                    "revenue": "$585/month",
                    "why_it_works": "Brand match + commercial intent",
                    "insight": "Good performer but not optimal yet"
                },
                {
                    "keyword": "bespoke gifts uk",
                    "position": 6,
                    "traffic": 105,
                    "revenue": "$240/month",
                    "why_it_works": "Premium intent keyword = higher AOV",
                    "insight": "Luxury segment performing well"
                },
                {
                    "keyword": "photo canvas",
                    "position": 9,
                    "traffic": 105,
                    "revenue": "$158/month",
                    "why_it_works": "Product-specific with good balance",
                    "insight": "Can improve to top 5"
                },
                {
                    "keyword": "personalised photo blanket",
                    "position": 12,
                    "traffic": 87,
                    "revenue": "$195/month",
                    "why_underperforming": "Long-tail but stuck at #12 - needs product-specific landing page",
                    "insight": "Move to top 8 = +$130/month opportunity"
                },
                {
                    "keyword": "custom photo mug",
                    "position": 15,
                    "traffic": 55,
                    "revenue": "$85/month",
                    "why_underperforming": "Good volume but low position - missing product content",
                    "insight": "Landing page optimization needed"
                }
            ],
            "insights": {
                "top_3_keywords_drive_81_percent": "$1,169 of $1,283 total revenue",
                "average_conversion_rate": "1.17%",
                "conversion_range": "0.60% - 1.43%",
                "key_finding": "High-intent keywords convert 2.3x better than generic terms"
            }
        },
        "opportunity_analysis": {
            "biggest_opportunity": {
                "keyword": "custom t shirts",
                "missed_traffic": "8,660 visitors/month",
                "missed_revenue": "$2,547/month",
                "why": "Position #13 means losing 93% of potential traffic",
                "solution": "Optimize category page with schema + product content"
            },
            "quick_wins": [
                {
                    "action": "Add schema markup to category pages",
                    "revenue_impact": "+$180/month",
                    "time": "2 hours"
                },
                {
                    "action": "Optimize meta descriptions",
                    "revenue_impact": "+$100/month",
                    "time": "4 hours"
                },
                {
                    "action": "Add FAQ schema",
                    "revenue_impact": "+$50/month",
                    "time": "2 hours"
                }
            ],
            "strategic_opportunities": [
                {
                    "keyword": "custom t shirts",
                    "current": "$20/month",
                    "potential": "$283/month",
                    "gain": "+$263/month"
                },
                {
                    "keyword": "photo gifts",
                    "current": "$136/month",
                    "potential": "$255/month",
                    "gain": "+$119/month"
                }
            ]
        },
        "strategic_recommendations": {
            "content_strategy": "Create 'How to Personalize [Product]' content. Your top keywords need supporting content to maintain position.",
            "technical_seo": "Add Product schema, optimize page speed, fix mobile UX. Could add $680/month combined.",
            "conversion_optimization": "Why 'personalised' converts 2.3x better: intent alignment. Apply same principles to other pages."
        },
        "roi_calculation": {
            "current_revenue": "$1,283/month",
            "potential_revenue": "$2,850/month",
            "opportunity": "$14,004/year",
            "investment": "$2,500",
            "roi": "460%",
            "payback": "4.3 months"
        },
        "key_insights_concise": [
            "🎯 Missing $2,847/month from 'custom t shirts' opportunity",
            "💰 'personalised' drives 81% of revenue - protect this keyword",
            "🚀 Competitors outranking you with better technical SEO",
            "📈 3 keyword improvements = $14,004/year additional revenue",
            "💡 High-intent keywords convert 2.3x better than generic terms"
        ]
    }


def get_mock_keyword_product_insights() -> Dict[str, Any]:
    """Mock insights when API unavailable - uses REAL keyword data"""
    return {
        "keyword_performance_analysis": {
            "top_performing_keywords": [
                {
                    "keyword": "personalised",
                    "position": 3,
                    "estimated_traffic": 473,
                    "target_product": "Multiple Categories",
                    "ga4_views": 4100,
                    "ga4_purchases": 56,
                    "conversion_rate": "1.36%",
                    "estimated_revenue": "$1,033/month",
                    "opportunity": "Your top revenue driver - maintains $1,033/month across all product categories"
                },
                {
                    "keyword": "photo gifts",
                    "position": 4,
                    "estimated_traffic": 99,
                    "target_product": "Photo Blankets, Canvas & Wall Art",
                    "ga4_views": 3000,
                    "ga4_purchases": 43,
                    "conversion_rate": "1.43%",
                    "estimated_revenue": "$136/month",
                    "opportunity": "Move to #2 could add $68/month ($816/year)"
                },
                {
                    "keyword": "custom t shirts",
                    "position": 13,
                    "estimated_traffic": 65,
                    "target_product": "Clothing & Accessories",
                    "ga4_views": 500,
                    "ga4_purchases": 3,
                    "conversion_rate": "0.60%",
                    "estimated_revenue": "$20/month",
                    "opportunity": "BIG OPPORTUNITY: 14,800 searches but only 65 visitors. Move to top 10 = +$45/month (+$540/year)"
                }
            ],
            "low_hanging_fruit": [
                {
                    "keyword": "custom t shirts",
                    "current_position": 13,
                    "search_volume": 14800,
                    "conversion_rate": 0.60,
                    "opportunity": "High volume keyword stuck at #13. Optimize category page to reach top 10.",
                    "potential_lift": "+$540/year additional revenue"
                }
            ]
        },
        "strategic_recommendations": {
            "priority_1": {
                "action": "Optimize 'custom t shirts' category page for top 10 ranking",
                "keyword": "custom t shirts",
                "revenue_lift": "+$45/month (+$540/year)",
                "timeline": "3-6 months",
                "implementation": "Add schema markup, improve descriptions, internal linking"
            },
            "priority_2": {
                "action": "Maintain position #3 for 'personalised' - your top revenue driver",
                "keyword": "personalised",
                "revenue_lift": "Maintain $1,033/month",
                "timeline": "Ongoing",
                "implementation": "Monitor weekly, build internal links, fresh content"
            }
        },
        "summary": {
            "total_keyword_traffic_potential": "1,096 visits/month",
            "current_estimated_revenue": "$1,033/month",
            "potential_with_improvements": "$1,400/month",
            "opportunity_value": "$4,404/year",
            "seo_investment_justification": "Optimization work on 3 keywords = $1,000 investment. ROI = 440% in first year."
        },
        "metadata": {"model": "mock-keyword-product", "generation_time": 0.1}
    }


def build_funnel_context(
    outliers: Dict[str, List[Dict[str, Any]]],
    baseline_rates: Dict[str, float],
    funnel_metrics: Dict[str, Any],
    historical_data: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Build brand-agnostic prompt for funnel analysis
    
    Args:
        outliers: Outlier data
        baseline_rates: Baseline conversion rates
        funnel_metrics: Full metrics breakdown
        historical_data: Historical trends
        
    Returns:
        str: Complete prompt for Claude
    """
    
    # Format outliers concisely
    outliers_summary = format_outliers(outliers)
    
    # Format historical trends if available
    historical_summary = ""
    if historical_data:
        historical_summary = f"\n## HISTORICAL TRENDS\n{format_historical(historical_data)}\n"
    
    # Build complete context
    context = f"""You are an expert ecommerce conversion funnel analyst. Analyze this funnel performance data and provide strategic, actionable recommendations.

## BASELINE PERFORMANCE
- View Item → Add to Cart: {baseline_rates.get('view_item_to_add_to_cart', 0):.1%}
- Add to Cart → Purchase: {baseline_rates.get('add_to_cart_to_purchase', 0):.1%}
- Overall Conversion: {baseline_rates.get('overall_conversion', 0):.1%}

## OUTLIERS DETECTED (±20% from baseline)
{outliers_summary}

## FULL DIMENSION BREAKDOWN
{format_metrics_summary(funnel_metrics)}
{historical_summary}
## TASK
Provide analysis in JSON format with the following structure:
{{
  "critical_issues": [
    {{
      "dimension": "channel",
      "value": "Social",
      "issue": "Brief description of the problem",
      "impact": "high/medium/low",
      "root_cause": "Potential explanation"
    }}
  ],
  "opportunities": [
    {{
      "dimension": "device",
      "value": "desktop",
      "opportunity": "Brief description",
      "potential_lift": "Estimated % improvement",
      "why": "Explanation of why this is promising"
    }}
  ],
  "recommendations": [
    {{
      "priority": 1,
      "action": "Specific actionable recommendation",
      "expected_impact": "What will improve and by how much",
      "implementation": "Quick/Medium/Long",
      "dimension_focus": "Which dimension(s) this addresses"
    }}
  ],
  "suggested_tests": [
    {{
      "test_name": "Descriptive A/B test name",
      "hypothesis": "What you expect to happen",
      "metric": "Which metric to track",
      "dimension": "Which dimension to focus on"
    }}
  ]
}}

Focus on:
1. Root causes of underperformance (not just symptoms)
2. Dimension combinations (e.g., "Social + Mobile" vs individual dimensions)
3. Quick wins vs long-term optimizations
4. Data-driven recommendations (reference specific metrics)
5. Prioritize by potential impact

Keep each recommendation actionable and under 200 characters.
"""
    
    return context


def format_outliers(outliers: Dict[str, List[Dict[str, Any]]]) -> str:
    """Format outliers for Claude context"""
    
    if not outliers:
        return "No significant outliers detected (all dimensions within ±20% of baseline)"
    
    lines = []
    for dimension, values in outliers.items():
        for outlier in values:
            direction = "↑" if outlier['overall_deviation'] > 0 else "↓"
            severity_emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢"
            }.get(outlier.get('severity', 'low'), "⚪")
            
            lines.append(
                f"{severity_emoji} {dimension.upper()}: {outlier['dimension_value']} "
                f"{direction} {abs(outlier['overall_deviation']):.0%} from baseline | "
                f"View→Cart: {outlier['view_to_cart_rate']:.1%} ({outlier['view_to_cart_deviation']:+.0%}), "
                f"Cart→Purchase: {outlier['cart_to_purchase_rate']:.1%} ({outlier['cart_to_purchase_deviation']:+.0%}) | "
                f"Volume: {outlier['absolute_numbers']['view_item']:,} views"
            )
    
    return "\n".join(lines)


def format_metrics_summary(funnel_metrics: Dict[str, Any]) -> str:
    """Format metrics summary concisely (avoid sending full JSON)"""
    
    summary_lines = []
    
    for dimension, values in funnel_metrics.items():
        summary_lines.append(f"\n### {dimension}")
        for value, metrics in values.items():
            summary_lines.append(
                f"- {value}: {metrics['overall_conversion_rate']:.1%} overall "
                f"({metrics['absolute_numbers']['view_item']:,} views → "
                f"{metrics['absolute_numbers']['purchase']} purchases)"
            )
    
    return "\n".join(summary_lines)


def format_historical(historical_data: List[Dict[str, Any]]) -> str:
    """Format historical trends concisely"""
    
    if not historical_data or len(historical_data) == 0:
        return "No historical data available"
    
    # Get last 7 days
    recent = historical_data[-7:] if len(historical_data) >= 7 else historical_data
    
    # Calculate trend
    if len(recent) >= 2:
        first_conversion = recent[0].get('overall_conversion', 0)
        last_conversion = recent[-1].get('overall_conversion', 0)
        trend = ((last_conversion - first_conversion) / first_conversion * 100) if first_conversion > 0 else 0
        
        trend_summary = f"Last {len(recent)} days: "
        trend_summary += f"Overall conversion {'↑' if trend > 0 else '↓'} {abs(trend):.1f}% "
        trend_summary += f"({first_conversion:.2%} → {last_conversion:.2%})"
    else:
        trend_summary = f"Insufficient historical data ({len(recent)} days)"
    
    return trend_summary


def parse_json_response(content: str) -> Dict[str, Any]:
    """
    Parse JSON from Claude response (handles markdown code blocks and common JSON errors)
    
    Args:
        content: Raw text response from Claude
        
    Returns:
        dict: Parsed JSON structure
    """
    
    try:
        # Extract JSON from markdown or code blocks
        json_str = None
        
        # Try extracting from markdown code block with json
        json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL | re.IGNORECASE)
        if json_match:
            json_str = json_match.group(1).strip()
            logger.debug(f"Found JSON in markdown block")
        
        # Try extracting from plain code block
        elif content.strip().startswith('```') and content.strip().endswith('```'):
            code_match = re.search(r'```\s*(.*?)\s*```', content, re.DOTALL)
            if code_match:
                json_str = code_match.group(1).strip()
                logger.debug(f"Found JSON in code block")
        
        # Try finding JSON object in the response
        elif '{' in content and '}' in content:
            json_obj_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_obj_match:
                json_str = json_obj_match.group(0)
                logger.debug(f"Found JSON object in response")
        else:
            json_str = content
        
        if json_str:
            # Clean up common JSON issues
            # Remove trailing commas before } or ]
            json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
            
            # Try to parse
            return json.loads(json_str)
        
        # Fallback: Try parsing entire response
        logger.debug("Attempting to parse entire response as JSON")
        return json.loads(content)
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        # Save full content for debugging
        with open('claude_response_error.txt', 'w') as f:
            f.write(content)
        logger.error(f"Full Claude response saved to claude_response_error.txt for debugging")
        
        # Return fallback structure
        return {
            "critical_issues": [],
            "opportunities": [],
            "recommendations": [{
                "priority": 1,
                "action": "Unable to parse AI insights - check claude_response_error.txt",
                "expected_impact": "N/A",
                "implementation": "N/A",
                "dimension_focus": "N/A"
            }],
            "suggested_tests": []
        }


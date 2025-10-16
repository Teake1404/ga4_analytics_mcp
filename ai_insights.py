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


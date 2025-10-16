"""
Optimized AI Insights Generator - Fast and Efficient
Reduced prompt size and improved performance for Cloud Run
"""

import anthropic
import config
import json
import logging
import time
from typing import Dict, List, Any, Optional

# Setup logging
logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)

def generate_funnel_insights_fast(
    outliers: Dict[str, List[Dict[str, Any]]],
    baseline_rates: Dict[str, float],
    funnel_metrics: Dict[str, Any],
    historical_data: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Fast AI insights generation with optimized prompt
    """
    
    try:
        # Initialize Claude client
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        
        # Build optimized context (much smaller)
        context = build_optimized_context(outliers, baseline_rates, funnel_metrics)
        
        logger.info("Calling Claude API with optimized prompt...")
        start_time = time.time()
        
        # Call Claude API with timeout
        message = client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=2048,  # Reduced from 4096
            messages=[{
                "role": "user", 
                "content": context
            }]
        )
        
        end_time = time.time()
        logger.info(f"Claude API call completed in {end_time - start_time:.2f} seconds")
        
        # Parse response
        content = message.content[0].text
        parsed = parse_json_response_fast(content)
        
        return {
            "model": message.model,
            "critical_issues": parsed.get("critical_issues", []),
            "opportunities": parsed.get("opportunities", []),
            "recommendations": parsed.get("recommendations", []),
            "suggested_tests": parsed.get("suggested_tests", [])
        }
        
    except Exception as e:
        logger.error(f"AI insights error: {e}")
        return {
            "model": "error",
            "critical_issues": [],
            "opportunities": [],
            "recommendations": [{
                "priority": 1,
                "action": f"AI insights temporarily unavailable: {str(e)[:100]}",
                "expected_impact": "N/A",
                "implementation": "N/A"
            }],
            "suggested_tests": []
        }

def build_optimized_context(
    outliers: Dict[str, List[Dict[str, Any]]],
    baseline_rates: Dict[str, float],
    funnel_metrics: Dict[str, Any]
) -> str:
    """
    Build compact, efficient prompt for Claude
    """
    
    # Get top 3 outliers only
    top_outliers = []
    for dimension, values in outliers.items():
        for outlier in values[:2]:  # Limit to 2 per dimension
            top_outliers.append({
                "dimension": dimension,
                "value": outlier['dimension_value'],
                "deviation": f"{outlier['overall_deviation']:+.0%}",
                "conversion": f"{outlier['overall_conversion_rate']:.1%}"
            })
    
    # Get top performing dimensions
    top_performers = []
    for dimension, values in funnel_metrics.items():
        best_value = max(values.items(), key=lambda x: x[1]['overall_conversion_rate'])
        top_performers.append({
            "dimension": dimension,
            "value": best_value[0],
            "conversion": f"{best_value[1]['overall_conversion_rate']:.1%}"
        })
    
    # Compact context
    context = f"""Analyze this ecommerce funnel data and provide actionable insights in JSON format.

BASELINE: View→Cart {baseline_rates.get('view_item_to_add_to_cart', 0):.1%}, Cart→Purchase {baseline_rates.get('add_to_cart_to_purchase', 0):.1%}, Overall {baseline_rates.get('overall_conversion', 0):.1%}

TOP OUTLIERS: {json.dumps(top_outliers[:5])}
TOP PERFORMERS: {json.dumps(top_performers[:3])}

Return JSON with:
{{
  "critical_issues": [{{"dimension": "x", "value": "y", "issue": "brief", "impact": "high/medium/low"}}],
  "opportunities": [{{"dimension": "x", "value": "y", "opportunity": "brief", "potential_lift": "X%"}}],
  "recommendations": [{{"priority": 1, "action": "specific action", "expected_impact": "what improves", "implementation": "Quick/Medium/Long"}}],
  "suggested_tests": [{{"test_name": "name", "hypothesis": "what you expect", "metric": "conversion_rate"}}]
}}

Focus on top 3 issues and opportunities. Keep responses concise."""
    
    return context

def parse_json_response_fast(content: str) -> Dict[str, Any]:
    """
    Fast JSON parsing with fallback
    """
    try:
        # Try direct JSON parsing first
        if content.strip().startswith('{'):
            return json.loads(content)
        
        # Extract from code blocks
        import re
        json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL | re.IGNORECASE)
        if json_match:
            return json.loads(json_match.group(1).strip())
        
        # Extract JSON object
        json_obj_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_obj_match:
            return json.loads(json_obj_match.group(0))
        
        # Fallback
        return json.loads(content)
        
    except Exception as e:
        logger.error(f"JSON parsing error: {e}")
        return {
            "critical_issues": [],
            "opportunities": [],
            "recommendations": [{
                "priority": 1,
                "action": "Unable to parse AI response",
                "expected_impact": "N/A",
                "implementation": "N/A"
            }],
            "suggested_tests": []
        }


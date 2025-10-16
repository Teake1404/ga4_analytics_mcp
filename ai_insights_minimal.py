"""
Minimal AI Insights - Ultra Fast for Cloud Run
"""

import anthropic
import config
import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

def generate_funnel_insights_minimal(
    outliers: Dict[str, List[Dict[str, Any]]],
    baseline_rates: Dict[str, float],
    funnel_metrics: Dict[str, Any],
    historical_data: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Ultra-minimal AI insights - just the essentials
    """
    
    try:
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        
        # Super minimal prompt
        prompt = f"""Analyze funnel data: baseline {baseline_rates.get('overall_conversion', 0):.1%} conversion.
        
Return JSON:
{{"critical_issues":[{{"issue":"top issue","impact":"high"}}],"opportunities":[{{"opportunity":"top opportunity","potential_lift":"20%"}}],"recommendations":[{{"priority":1,"action":"key action","expected_impact":"improvement"}}],"suggested_tests":[{{"test_name":"A/B test","hypothesis":"expected result"}}]}}"""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",  # Use faster model
            max_tokens=1000,  # Very small
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = message.content[0].text
        
        # Simple JSON extraction
        if '{' in content and '}' in content:
            start = content.find('{')
            end = content.rfind('}') + 1
            json_str = content[start:end]
            parsed = json.loads(json_str)
        else:
            raise Exception("No JSON found in response")
        
        return {
            "model": message.model,
            "critical_issues": parsed.get("critical_issues", []),
            "opportunities": parsed.get("opportunities", []),
            "recommendations": parsed.get("recommendations", []),
            "suggested_tests": parsed.get("suggested_tests", [])
        }
        
    except Exception as e:
        logger.error(f"Minimal AI error: {e}")
        # Return fallback insights
        return {
            "model": "fallback",
            "critical_issues": [{"issue": "Mobile conversion below average", "impact": "high"}],
            "opportunities": [{"opportunity": "Optimize mobile checkout", "potential_lift": "25%"}],
            "recommendations": [{"priority": 1, "action": "Improve mobile UX", "expected_impact": "Higher mobile conversion"}],
            "suggested_tests": [{"test_name": "Mobile checkout test", "hypothesis": "Simplified flow increases conversion"}]
        }


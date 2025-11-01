"""
Streamlined AI Insights Generator - Specific, Actionable Insights
Focuses on critical issues and growth opportunities with specific metrics and impact
"""

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
import config
import json
import logging
import time
from typing import Dict, List, Any, Optional

# Setup logging
logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)

def generate_streamlined_insights(
    outliers: Dict[str, List[Dict[str, Any]]],
    baseline_rates: Dict[str, float],
    funnel_metrics: Dict[str, Any],
    historical_data: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Generate streamlined, specific AI insights focused on critical issues and growth opportunities
    
    Returns insights in the format:
    - Critical Issue: Specific problem with metrics and impact
    - Growth Opportunity: Specific opportunity with potential lift
    - Recommended Action: Priority actions with expected impact
    """
    
    # Check if we have a valid API key and anthropic module, otherwise use mock insights
    if not HAS_ANTHROPIC or not hasattr(config, 'ANTHROPIC_API_KEY') or not config.ANTHROPIC_API_KEY or config.ANTHROPIC_API_KEY.startswith("sk-ant-api03-test"):
        logger.info("Using mock streamlined insights (no valid API key or anthropic module)")
        return generate_mock_streamlined_insights(outliers, baseline_rates, funnel_metrics)
    
    try:
        # Initialize Claude client
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        
        # Build streamlined context
        context = build_streamlined_context(outliers, baseline_rates, funnel_metrics)
        
        logger.info("Generating streamlined AI insights...")
        start_time = time.time()
        
        # Call Claude API
        message = client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=1500,  # Reduced for faster response
            messages=[{
                "role": "user", 
                "content": context
            }]
        )
        
        end_time = time.time()
        logger.info(f"Streamlined AI insights generated in {end_time - start_time:.2f} seconds")
        
        # Parse response
        content = message.content[0].text
        parsed = parse_streamlined_response(content)
        
        return {
            "model": message.model,
            "critical_issue": parsed.get("critical_issue", {}),
            "growth_opportunity": parsed.get("growth_opportunity", {}),
            "recommended_action": parsed.get("recommended_action", {}),
            "ready_to_scale": parsed.get("ready_to_scale", {})
        }
        
    except Exception as e:
        logger.error(f"Streamlined AI insights error: {e}")
        # Fallback to mock insights if API fails
        return generate_mock_streamlined_insights(outliers, baseline_rates, funnel_metrics)

def generate_mock_streamlined_insights(
    outliers: Dict[str, List[Dict[str, Any]]],
    baseline_rates: Dict[str, float],
    funnel_metrics: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate realistic mock streamlined insights based on the data
    """
    
    # Find the worst performing outlier (critical issue)
    worst_outlier = None
    worst_deviation = float('inf')
    
    for dimension, values in outliers.items():
        for outlier in values:
            if outlier['overall_deviation'] < worst_deviation:
                worst_deviation = outlier['overall_deviation']
                worst_outlier = outlier
    
    # Find the best performing outlier (growth opportunity)
    best_outlier = None
    best_deviation = float('-inf')
    
    for dimension, values in outliers.items():
        for outlier in values:
            if outlier['overall_deviation'] > best_deviation:
                best_deviation = outlier['overall_deviation']
                best_outlier = outlier
    
    # Generate insights based on the data
    if worst_outlier and worst_outlier['dimension_value'] == 'tablet':
        critical_issue = {
            "title": "Tablet Revenue Leak",
            "description": f"Tablet users add to cart at {worst_outlier['view_to_cart_rate']:.1%} (above average) but only {worst_outlier['cart_to_purchase_rate']:.1%} complete purchase - a {abs(worst_outlier['overall_deviation']):.0%} drop-off suggesting serious checkout UX problems on smaller screens.",
            "impact": f"Fixing this could recover 4-5 monthly purchases from your tablet traffic alone.",
            "expected_recovery": "4-5 monthly purchases",
            "why": [
                "Tablet users add to cart but don't complete purchase",
                "Checkout forms not optimized for tablet screens",
                "Payment flow has touch/gesture issues on tablets"
            ]
        }
    else:
        critical_issue = {
            "title": "Critical Conversion Issue",
            "description": f"{worst_outlier['dimension_value'] if worst_outlier else 'Unknown'} users are underperforming by {abs(worst_deviation):.0%} from baseline conversion rates.",
            "impact": "Addressing this could significantly improve overall conversion performance.",
            "expected_recovery": "15-25% conversion improvement",
            "why": [
                f"{worst_outlier['dimension_value'] if worst_outlier else 'Unknown'} segment underperforms significantly",
                "Poor user experience or targeting issues",
                "Addressing root cause unlocks conversion gains"
            ]
        }
    
    if best_outlier and 'email' in best_outlier['dimension_value'].lower():
        growth_opportunity = {
            "title": "Email Channel Overperformance",
            "description": f"Your email traffic converts at {best_outlier['overall_conversion_rate']:.1%} ({best_deviation:+.0%} above baseline) but only represents 8% of total traffic.",
            "potential_lift": "3x email traffic could add 24+ monthly purchases with minimal acquisition cost.",
            "rationale": "Email users are highly engaged and convert significantly above average",
            "why": [
                "Email traffic is desktop-dominant and product-specific",
                "Email campaigns target high-intent users perfectly",
                "Users have already shown interest and are ready to convert"
            ]
        }
    else:
        growth_opportunity = {
            "title": "High-Performing Segment",
            "description": f"{best_outlier['dimension_value'] if best_outlier else 'Unknown'} segment converts at {best_outlier['overall_conversion_rate']:.1%} ({best_deviation:+.0%} above baseline).",
            "potential_lift": f"Scaling this segment could increase conversions by {best_deviation:.0%}.",
            "rationale": "This segment shows exceptional conversion performance",
            "why": [
                f"{best_outlier['dimension_value'] if best_outlier else 'Unknown'} segment shows exceptional performance",
                "Better targeting or user experience drives results",
                "Scaling this segment boosts overall conversions"
            ]
        }
    
    return {
        "model": "mock-streamlined",
        "critical_issue": critical_issue,
        "growth_opportunity": growth_opportunity,
        "recommended_action": {
            "priority_1": "Emergency tablet checkout audit - test payment forms and mobile optimization",
            "priority_2": "Scale email acquisition via exit-intent popups and content upgrades",
            "expected_impact": "Recover tablet revenue + scale high-converting email channel"
        },
        "ready_to_scale": {
            "cta": "Book a Discovery Call",
            "description": "Ready to see this with your actual GA4 data?"
        }
    }

def build_streamlined_context(
    outliers: Dict[str, List[Dict[str, Any]]],
    baseline_rates: Dict[str, float],
    funnel_metrics: Dict[str, Any]
) -> str:
    """
    Build focused context for streamlined insights
    """
    
    # Get the worst performing outlier (critical issue)
    worst_outlier = None
    worst_deviation = float('inf')
    
    for dimension, values in outliers.items():
        for outlier in values:
            if outlier['overall_deviation'] < worst_deviation:
                worst_deviation = outlier['overall_deviation']
                worst_outlier = {
                    "dimension": dimension,
                    "value": outlier['dimension_value'],
                    "conversion_rate": outlier['overall_conversion_rate'],
                    "deviation": outlier['overall_deviation'],
                    "volume": outlier['absolute_numbers']['view_item'],
                    "cart_rate": outlier['view_to_cart_rate'],
                    "purchase_rate": outlier['cart_to_purchase_rate']
                }
    
    # Get the best performing outlier (growth opportunity)
    best_outlier = None
    best_deviation = float('-inf')
    
    for dimension, values in outliers.items():
        for outlier in values:
            if outlier['overall_deviation'] > best_deviation:
                best_deviation = outlier['overall_deviation']
                best_outlier = {
                    "dimension": dimension,
                    "value": outlier['dimension_value'],
                    "conversion_rate": outlier['overall_conversion_rate'],
                    "deviation": outlier['overall_deviation'],
                    "volume": outlier['absolute_numbers']['view_item'],
                    "cart_rate": outlier['view_to_cart_rate'],
                    "purchase_rate": outlier['cart_to_purchase_rate']
                }
    
    # Get channel performance for growth opportunity
    channel_performance = {}
    if 'sessionDefaultChannelGroup' in funnel_metrics:
        for channel, metrics in funnel_metrics['sessionDefaultChannelGroup'].items():
            channel_performance[channel] = {
                "conversion_rate": metrics['overall_conversion_rate'],
                "volume": metrics['absolute_numbers']['view_item'],
                "deviation": ((metrics['overall_conversion_rate'] - baseline_rates['overall_conversion']) / baseline_rates['overall_conversion']) * 100
            }
    
    context = f"""You are an expert ecommerce conversion analyst. Analyze this data and provide ONE critical issue and ONE growth opportunity with specific metrics, actionable recommendations, and data-driven root-cause analysis by connecting dots across dimensions.

BASELINE PERFORMANCE:
- View Item → Add to Cart: {baseline_rates.get('view_item_to_add_to_cart', 0):.1%}
- Add to Cart → Purchase: {baseline_rates.get('add_to_cart_to_purchase', 0):.1%}
- Overall Conversion: {baseline_rates.get('overall_conversion', 0):.1%}

WORST PERFORMER (Critical Issue):
{json.dumps(worst_outlier) if worst_outlier else "None"}

BEST PERFORMER (Growth Opportunity):
{json.dumps(best_outlier) if best_outlier else "None"}

CHANNEL PERFORMANCE:
{json.dumps(channel_performance)}

Return JSON in this EXACT format:
{{
  "critical_issue": {{
    "title": "Specific problem name (e.g., 'Sports Category Cart-to-Purchase Collapse')",
    "description": "Simple sentence with specific metrics (e.g., 'Sports category has 8% cart addition rate but only 7.5% purchase rate from cart (vs 8.7% baseline). This 14% worse purchase completion suggests severe checkout friction specific to Sports products.')",
    "impact": "Expected impact with specific numbers (e.g., 'Fixing checkout friction could recover 3-4 additional purchases monthly (120%+ lift).')",
    "expected_recovery": "Specific recovery potential (e.g., '3-4 additional purchases monthly')",
                "why": ["Sports traffic comes from Social (52% below baseline)", "Mobile-heavy users struggle with sizing requirements", "Product pages lack mobile-optimized specifications"]
  }},
  "growth_opportunity": {{
    "title": "Specific opportunity name (e.g., 'Email Channel Revenue Multiplier')",
    "description": "Simple sentence with specific metrics (e.g., 'Email converts at 2.4% (85% above baseline) with 21.4% cart rate and 11.21% purchase rate. This is your highest-converting channel but only 500 sessions (10-12% of total).')",
    "potential_lift": "Specific potential with numbers (e.g., 'Doubling email traffic could add 12 monthly purchases; tripling could add 24+.')",
    "rationale": "Why this is promising (e.g., 'Email users are highly engaged and convert 82% above average')",
                "why": ["Email users arrive with product-specific intent", "Desktop-dominant traffic has higher purchase completion", "Pre-qualified users ready to convert"]
  }},
  "recommended_action": {{
    "priority_1": "Specific first action with concrete impact (e.g., 'Sports Category Emergency Audit: Analyze device breakdown and Social channel overlap. Add size guides and trust signals in checkout.')",
    "priority_2": "Specific second action with concrete impact (e.g., 'Email List Growth Blitz: Implement exit-intent popups and content upgrades. Target 50% email list growth in 30 days.')",
    "expected_impact": "What will improve (e.g., 'Recover tablet revenue + scale high-converting email channel')"
  }},
  "ready_to_scale": {{
    "cta": "Book a Discovery Call",
    "description": "Ready to see this with your actual GA4 data?"
  }}
}}

            Focus on:
            1. Root causes of underperformance (not just symptoms)
            2. Dimension combinations (e.g., "Social + Mobile" vs individual dimensions)
            3. Quick wins vs long-term optimizations
            4. Data-driven recommendations (reference specific metrics)
            5. Prioritize by potential impact
            6. Connect dots across dimensions to explain WHY (channel + device + category/browser/resolution correlations)
            7. Use concrete numbers: "120%+ lift", "24+ purchases", "50% growth in 30 days"
            8. Write scannable content: short sentences, bullet points, clear hierarchy
            9. Make impact measurable and specific
            10. For "why" fields: provide as arrays of 2-3 concise bullet points (max 80 characters each), not long paragraphs
            11. Each bullet should be a complete, scannable insight that stands alone
"""

    return context

def parse_streamlined_response(content: str) -> Dict[str, Any]:
    """
    Parse streamlined JSON response
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
        logger.error(f"Streamlined JSON parsing error: {e}")
        return {
            "critical_issue": {
                "title": "Analysis Error",
                "description": "Unable to parse AI response",
                "impact": "N/A",
                "expected_recovery": "N/A"
            },
            "growth_opportunity": {
                "title": "Analysis Error",
                "description": "Unable to parse AI response", 
                "potential_lift": "N/A",
                "rationale": "N/A"
            },
            "recommended_action": {
                "priority_1": "Contact support",
                "priority_2": "Check system status",
                "expected_impact": "N/A"
            },
            "ready_to_scale": {
                "cta": "Book a Discovery Call",
                "description": "Ready to see this with your actual GA4 data?"
            }
        }

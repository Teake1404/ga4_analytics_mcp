"""
Flask API for GA4 Funnel Analysis MCP
Following SEO MCP pattern: stateless, dynamic configuration, Cloud Run ready
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import asyncio
import logging
import os
import json
from datetime import datetime
import config
import mock_ga4_data
import funnel_analysis
import ai_insights
from ai_insights_minimal import generate_funnel_insights_minimal
from cache_manager import cache_manager, batch_processor
from ga4_auth import get_ga4_client, is_ga4_authenticated, get_ga4_auth_url, exchange_ga4_code

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


@app.route('/', methods=['GET'])
def index():
    """Serve demo page or health check"""
    return send_file('demo.html')


@app.route('/api', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        "service": "GA4 Funnel Analysis MCP",
        "status": "running",
        "version": "1.0.0",
        "data_source": "mock" if config.USE_MOCK_DATA else "ga4",
        "endpoints": {
            "/": "GET - Demo page",
            "/api/funnel-analysis": "POST - Generate funnel analysis report (6 dimensions: channel, device, browser, resolution, product, category)",
            "/api/health": "GET - Health check"
        }
    })


@app.route('/api/health', methods=['GET'])
def health():
    """Detailed health check"""
    try:
        config.validate_config()
        config_status = "ok"
    except ValueError as e:
        config_status = str(e)
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "config_status": config_status,
        "claude_model": config.CLAUDE_MODEL,
        "use_mock_data": config.USE_MOCK_DATA,
        "ga4_authenticated": is_ga4_authenticated()
    })


@app.route('/api/ga4/auth/url', methods=['GET'])
def get_ga4_auth_url_endpoint():
    """Get GA4 OAuth2 authorization URL"""
    try:
        auth_url = get_ga4_auth_url()
        return jsonify({
            "success": True,
            "auth_url": auth_url,
            "instructions": "Visit this URL to authorize GA4 access. After authorization, you'll get a code to exchange for tokens."
        })
    except Exception as e:
        logger.error(f"Error generating GA4 auth URL: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/ga4/auth/callback', methods=['POST'])
def ga4_auth_callback():
    """Handle GA4 OAuth2 callback and exchange code for tokens"""
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({
                "success": False,
                "error": "Authorization code is required"
            }), 400
        
        result = exchange_ga4_code(data['code'])
        
        if result['success']:
            return jsonify({
                "success": True,
                "message": "GA4 authentication successful",
                "authenticated": True
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to exchange authorization code"
            }), 400
            
    except Exception as e:
        logger.error(f"Error in GA4 auth callback: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/ga4/auth/status', methods=['GET'])
def ga4_auth_status():
    """Check GA4 authentication status"""
    return jsonify({
        "authenticated": is_ga4_authenticated(),
        "use_mock_data": config.USE_MOCK_DATA,
        "message": "Use mock data" if config.USE_MOCK_DATA else ("GA4 authenticated" if is_ga4_authenticated() else "GA4 authentication required")
    })


@app.route('/api/generate-report', methods=['POST'])
def generate_html_report():
    """
    Generate complete HTML report with visualizations
    
    This endpoint:
    1. Runs funnel analysis
    2. Generates visualizations
    3. Returns complete HTML report
    
    Perfect for n8n → Email/Slack workflows
    """
    
    try:
        # Get the analysis data
        data = request.get_json()
        
        # Run funnel analysis (reuse existing endpoint logic)
        # ... implementation here ...
        
        # For now, return simple HTML with embedded charts
        html_report = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>GA4 Funnel Analysis Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .metric { display: inline-block; margin: 10px; padding: 15px; 
                         background: #f0f0f0; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1>🎯 GA4 Funnel Analysis Report</h1>
            <div class="metrics">
                <div class="metric">
                    <h3>Conversion Rate</h3>
                    <p>1.32%</p>
                </div>
                <!-- More metrics here -->
            </div>
            <!-- Embedded visualizations -->
        </body>
        </html>
        """
        
        return html_report, 200, {'Content-Type': 'text/html'}
        
    except Exception as e:
        logger.error(f"Error generating HTML report: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/funnel-analysis', methods=['POST'])
def funnel_analysis_endpoint():
    """
    Main funnel analysis endpoint
    
    Request body:
    {
        "property_id": "123456789",  # Optional (for mock mode)
        "date_range": "last_30_days",
        "funnel_steps": ["view_item", "add_to_cart", "purchase"],
        "dimensions": ["sessionDefaultChannelGroup", "deviceCategory", "browser"],
        "baseline_rates": {  # Optional override
            "view_item_to_add_to_cart": 0.152,
            "add_to_cart_to_purchase": 0.087,
            "overall_conversion": 0.0132
        },
        "historical_data": []  # Optional from n8n Data Table
    }
    
    Returns:
    {
        "success": true,
        "timestamp": "ISO-8601",
        "data_provider": "mock" or "ga4",
        "data": {
            "funnel_metrics": {...},
            "outliers": {...},
            "baseline_rates": {...}
        },
        "insights": {
            "model": "claude-sonnet-4-5-20250929",
            "critical_issues": [...],
            "opportunities": [...],
            "recommendations": [...]
        },
        "summary": {...}
    }
    """
    
    try:
        # ============================================================================
        # 1. Get dynamic config from request
        # ============================================================================
        
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is required"
            }), 400
        
        property_id = data.get('property_id', config.GA4_PROPERTY_ID)
        date_range = data.get('date_range', config.DEFAULT_DATE_RANGE)
        funnel_steps = data.get('funnel_steps', config.DEFAULT_FUNNEL_STEPS)
        dimensions = data.get('dimensions', config.DEFAULT_DIMENSIONS)
        baseline_rates_override = data.get('baseline_rates', None)
        historical_data = data.get('historical_data', [])
        
        logger.info(f"Funnel analysis request: property_id={property_id}, dimensions={dimensions}")
        
        # ============================================================================
        # 2. Check cache first (avoid redundant AI calls)
        # ============================================================================
        
        cache_key = cache_manager.generate_cache_key({
            'dimensions': dimensions,
            'property_id': property_id,
            'date_range': date_range,
            'baseline_rates': baseline_rates_override
        })
        
        cached_insights = cache_manager.get_cached_insights(cache_key)
        
        # ============================================================================
        # 3. Batch process historical data (optimize for 54 MB storage)
        # ============================================================================
        
        if historical_data and len(historical_data) > 100:
            logger.info(f"Batch processing {len(historical_data)} historical records")
            # Summarize old data to save space
            historical_data = batch_processor.summarize_historical_data(
                historical_data, 
                keep_last_n_days=30
            )
            logger.info(f"Summarized to {len(historical_data)} records")
        
        # ============================================================================
        # 4. Fetch funnel data (mock or real GA4)
        # ============================================================================
        
        if config.USE_MOCK_DATA or not is_ga4_authenticated():
            logger.info("Using pre-generated mock GA4 data (USE_MOCK_DATA=true or not authenticated)")
            try:
                # Load pre-generated mock data
                with open('pre_generated_mock_data.json', 'r') as f:
                    funnel_data = json.load(f)
                logger.info("Loaded pre-generated mock data successfully")
            except FileNotFoundError:
                logger.warning("Pre-generated data not found, generating fresh mock data")
                funnel_data = mock_ga4_data.generate_mock_funnel_data(
                    funnel_steps=funnel_steps,
                    dimensions=dimensions,
                    date_range=date_range,
                    property_id=property_id
                )
            data_provider = "mock"
        else:
            logger.info("Using real GA4 API")
            try:
                ga4_client = get_ga4_client(property_id)
                ga4_response = ga4_client.run_funnel_report(
                    date_range=date_range,
                    dimensions=dimensions,
                    funnel_steps=funnel_steps
                )
                
                if ga4_response['success']:
                    funnel_data = ga4_response['data']
                    data_provider = "ga4"
                    logger.info(f"Successfully fetched GA4 data with {len(funnel_data.get('dimension_breakdowns', {}))} dimensions")
                else:
                    logger.warning(f"GA4 API failed: {ga4_response.get('error')}. Falling back to mock data.")
                    funnel_data = mock_ga4_data.generate_mock_funnel_data(
                        funnel_steps=funnel_steps,
                        dimensions=dimensions,
                        date_range=date_range,
                        property_id=property_id
                    )
                    data_provider = "mock"
                    
            except Exception as e:
                logger.error(f"GA4 API error: {e}. Falling back to mock data.")
                funnel_data = mock_ga4_data.generate_mock_funnel_data(
                    funnel_steps=funnel_steps,
                    dimensions=dimensions,
                    date_range=date_range,
                    property_id=property_id
                )
                data_provider = "mock"
        
        # ============================================================================
        # 3. Calculate funnel metrics
        # ============================================================================
        
        funnel_metrics = funnel_analysis.calculate_funnel_metrics(funnel_data)
        logger.info(f"Calculated metrics for {len(funnel_metrics)} dimensions")
        
        # ============================================================================
        # 4. Get baseline rates (use override or calculate from data)
        # ============================================================================
        
        if baseline_rates_override:
            baseline_rates = baseline_rates_override
            logger.info("Using provided baseline rates")
        else:
            baseline_rates = funnel_data.get("overall_baseline", 
                funnel_analysis.calculate_baseline_from_data(funnel_data)
            )
            logger.info("Using calculated baseline rates")
        
        # ============================================================================
        # 5. Detect outliers
        # ============================================================================
        
        outliers = funnel_analysis.detect_funnel_outliers(
            funnel_metrics,
            baseline_rates,
            threshold=config.OUTLIER_THRESHOLD
        )
        
        outlier_count = sum(len(v) for v in outliers.values())
        logger.info(f"Detected {outlier_count} outliers across {len(outliers)} dimensions")
        
        # ============================================================================
        # 6. Generate AI insights (use cache if available)
        # ============================================================================
        
        if cached_insights:
            insights = cached_insights
            logger.info(f"Using cached AI insights (saved API call)")
        else:
            logger.info("Generating AI insights with optimized processing...")
            # Use full AI insights by default for better demo experience
            if os.getenv("DISABLE_AI", "false").lower() == "true":
                # Return basic insights without AI processing
                insights = {
                    "model": "basic",
                    "recommendations": [
                        {"action": "Optimize mobile checkout flow", "impact": "high", "effort": "medium"},
                        {"action": "Improve tablet user experience", "impact": "high", "effort": "high"},
                        {"action": "Fix Chrome browser compatibility", "impact": "medium", "effort": "low"}
                    ],
                    "critical_issues": [
                        {"issue": "Low tablet conversion rate", "impact": "critical", "affected_users": "15%"},
                        {"issue": "Chrome checkout failures", "impact": "high", "affected_users": "25%"}
                    ],
                    "opportunities": [
                        {"opportunity": "Mobile optimization potential", "potential_impact": "20% conversion increase"},
                        {"opportunity": "Browser compatibility improvements", "potential_impact": "15% conversion increase"}
                    ]
                }
            else:
                # Use full AI insights for rich, detailed analysis
                insights = ai_insights.generate_funnel_insights(
                    outliers=outliers,
                    baseline_rates=baseline_rates,
                    funnel_metrics=funnel_metrics,
                    historical_data=historical_data
                )
            logger.info(f"Generated AI insights using {insights.get('model', 'unknown')}")
            
            # Cache the insights
            cache_manager.save_insights(cache_key, insights)
        
        # Optimize insights for n8n Data Table storage
        optimized_insights = cache_manager.prepare_for_n8n_storage(insights)
        
        # ============================================================================
        # 7. Get summary metrics
        # ============================================================================
        
        top_opportunities = funnel_analysis.get_top_opportunities(outliers, limit=3)
        critical_issues = funnel_analysis.get_critical_issues(outliers, limit=3)
        
        # ============================================================================
        # 8. Calculate storage usage and cache stats
        # ============================================================================
        
        cache_stats = cache_manager.get_cache_stats()
        
        summary = {
            "dimensions_analyzed": len(funnel_metrics),
            "total_outliers": outlier_count,
            "critical_issues_count": len(critical_issues),
            "opportunities_count": len(top_opportunities),
            "data_points": sum(
                m["absolute_numbers"]["view_item"] 
                for dim in funnel_metrics.values() 
                for m in dim.values()
            ),
            "date_range": date_range,
            "cache_used": cached_insights is not None,
            "cache_key": cache_key[:8] + "...",  # First 8 chars for debugging
            "cache_stats": cache_stats,
            "historical_records_processed": len(historical_data) if historical_data else 0
        }
        
        # ============================================================================
        # 8. Return structured response
        # ============================================================================
        
        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "data_provider": data_provider,
            "data": {
                "funnel_metrics": funnel_metrics,
                "outliers": outliers,
                "baseline_rates": baseline_rates,
                "top_opportunities": top_opportunities,
                "critical_issues": critical_issues
            },
            "insights": insights,
            "insights_optimized": optimized_insights,  # For n8n Data Table storage
            "summary": summary,
            "metadata": funnel_data.get("metadata", {}),
            "storage_optimization": {
                "original_size_kb": round(len(json.dumps(insights)) / 1024, 2),
                "optimized_size_kb": round(len(json.dumps(optimized_insights)) / 1024, 2),
                "savings_percent": round((1 - len(json.dumps(optimized_insights)) / len(json.dumps(insights))) * 100, 1)
            }
        })
        
    except Exception as e:
        logger.error(f"Error in funnel_analysis_endpoint: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500




# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "available_endpoints": [
            "/api/funnel-analysis",
            "/api/health"
        ]
    }), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "message": str(e)
    }), 500


if __name__ == '__main__':
    # Validate configuration on startup
    try:
        config.validate_config()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.warning(f"Configuration validation failed: {e}")
    
    # Run Flask app
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)


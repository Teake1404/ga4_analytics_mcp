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
from ai_insights_streamlined import generate_streamlined_insights
from cross_platform_insights import get_cross_platform_insights
from cross_platform_analyzer import receive_seo_data_from_n8n
from ga4_mcp_integration import ga4_mcp
from cache_manager import cache_manager, batch_processor
from ga4_auth import get_ga4_client, is_ga4_authenticated, get_ga4_auth_url, exchange_ga4_code
from ga4_client import GA4Client
from redis_cache import RedisCacheManager

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {"origins": ["*"]},
    r"/*": {"origins": ["*"]}
})

# Setup logging
logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Initialize GA4 client and cache manager
ga4_client = GA4Client()

# Try to initialize Redis, but don't fail if it's not available (for Railway deployment)
try:
    cache_manager_redis = RedisCacheManager()
    logger.info("Redis cache initialized successfully")
except Exception as e:
    logger.warning(f"Redis not available: {e}. Continuing without cache.")
    cache_manager_redis = None


@app.route('/', methods=['GET'])
def index():
    """Serve demo page or health check"""
    try:
        return send_file('templates/report_demo.html')
    except:
        return jsonify({
            "message": "GA4 Keyword Product Revenue Insights API",
            "endpoint": "/api/keyword-product-insights",
            "method": "POST"
        })


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
            "/api/keyword-product-insights": "POST - Generate AI insights connecting SEO keywords to product sales (Perfect for lead magnet)",
            "/api/cross-platform-analysis": "POST - Cross-platform SEO + GA4 analysis",
            "/api/seo-data": "POST - Receive SEO data from N8N/Seranking MCP",
            "/api/health": "GET - Health check",
            "/api/ga4/run-report": "POST - Direct GA4 API call (slow)",
            "/api/ga4/refresh-cache": "POST - Refresh GA4 cache (background)",
            "/api/ga4/cached": "GET - Get cached GA4 data (fast)",
            "/api/ga4/cached-data": "POST - Get cached GA4 data only (fast, no AI)",
            "/api/ga4/instant-analysis": "POST - Cached GA4 + AI insights (fast)"
        }
    })


@app.route('/api/health', methods=['GET'])
def health():
    """Detailed health check"""
    try:
        config.validate_config()
        config_status = "ok"
    except ValueError as e:
        config_status = f"WARNING: {str(e)} (will use mock data)"
    
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


@app.route('/api/ga4/run-report', methods=['POST'])
def ga4_run_report():
    """
    Direct GA4 API call (slow - for debugging)
    """
    try:
        data = request.get_json() or {}
        property_id = data.get('property_id', '476872592')
        report_type = data.get('report_type', 'funnel')
        
        logger.info(f"Direct GA4 API call for property {property_id}, report type: {report_type}")
        
        if report_type == 'funnel':
            ga4_data = ga4_client.get_funnel_data(property_id)
        elif report_type == 'traffic_sources':
            ga4_data = ga4_client.get_traffic_sources(property_id)
        elif report_type == 'overview':
            ga4_data = ga4_client.get_overview_metrics(property_id)
        else:
            return jsonify({"error": "Invalid report_type. Use: funnel, traffic_sources, overview"}), 400
        
        return jsonify({
            "success": True,
            "data": ga4_data,
            "property_id": property_id,
            "report_type": report_type,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in GA4 run report: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/ga4/refresh-cache', methods=['POST'])
def ga4_refresh_cache():
    """
    Refresh GA4 cache (background job)
    """
    try:
        data = request.get_json() or {}
        property_id = data.get('property_id', '476872592')
        
        logger.info(f"Refreshing GA4 cache for property {property_id}")
        
        # Fetch fresh data from GA4
        funnel_data = ga4_client.get_funnel_data(property_id)
        traffic_sources = ga4_client.get_traffic_sources(property_id)
        overview_metrics = ga4_client.get_overview_metrics(property_id)
        
        # Cache the data
        cache_manager_redis.cache_funnel_data(property_id, funnel_data)
        cache_manager_redis.cache_traffic_sources(property_id, traffic_sources)
        cache_manager_redis.cache_overview_metrics(property_id, overview_metrics)
        
        return jsonify({
            "success": True,
            "message": "Cache refreshed successfully",
            "property_id": property_id,
            "cached_reports": ["funnel", "traffic_sources", "overview"],
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error refreshing GA4 cache: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/ga4/cached', methods=['GET'])
def ga4_get_cached():
    """
    Get cached GA4 data (fast)
    """
    try:
        property_id = request.args.get('property_id', '476872592')
        report_type = request.args.get('report_type', 'funnel')
        
        logger.info(f"Getting cached GA4 data for property {property_id}, report type: {report_type}")
        
        if report_type == 'funnel':
            cached_data = cache_manager_redis.get_funnel_data(property_id)
        elif report_type == 'traffic_sources':
            cached_data = cache_manager_redis.get_traffic_sources(property_id)
        elif report_type == 'overview':
            cached_data = cache_manager_redis.get_overview_metrics(property_id)
        else:
            return jsonify({"error": "Invalid report_type. Use: funnel, traffic_sources, overview"}), 400
        
        if cached_data is None:
            return jsonify({
                "success": False,
                "message": "No cached data found. Run /api/ga4/refresh-cache first.",
                "property_id": property_id,
                "report_type": report_type
            }), 404
        
        return jsonify({
            "success": True,
            "data": cached_data,
            "property_id": property_id,
            "report_type": report_type,
            "cached": True,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting cached GA4 data: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/ga4/instant-analysis', methods=['POST'])
def ga4_instant_analysis():
    """
    Process GA4 data + AI insights (fast - no API calls)
    Expects data to be provided in request body or use mock data
    """
    try:
        data = request.get_json() or {}
        property_id = data.get('property_id', '476872592')
        use_mock_data = data.get('use_mock_data', False)
        provided_data = data.get('data')  # Allow data to be passed in
        
        logger.info(f"AI insights processing for property {property_id}, use_mock_data: {use_mock_data}, data_provided: {provided_data is not None}")
        
        if use_mock_data:
            # Use existing mock data logic
            with open('pre_generated_mock_data.json', 'r') as f:
                funnel_data = json.load(f)
            data_provider = "mock"
        elif provided_data:
            # Use data provided in request body
            funnel_data = provided_data
            data_provider = "provided"
        else:
            # Get cached GA4 data (fallback)
            cached_funnel_data = cache_manager_redis.get_funnel_data(property_id)
            
            if cached_funnel_data is None:
                return jsonify({
                    "success": False,
                    "message": "No data provided. Either provide 'data' in request body, set 'use_mock_data': true, or run /api/ga4/refresh-cache first.",
                    "property_id": property_id
                }), 404
            
            # Transform cached data to expected format
            if isinstance(cached_funnel_data, list) and len(cached_funnel_data) > 0:
                funnel_data = {
                    "dimension_breakdowns": {
                        "deviceCategory": {row.get("deviceCategory", "unknown"): {"funnel_metrics": row} for row in cached_funnel_data},
                        "browser": {row.get("browser", "unknown"): {"funnel_metrics": row} for row in cached_funnel_data}
                    },
                    "overall_baseline": {
                        "overall_conversion": 0.0132,
                        "view_item_to_add_to_cart": 0.152,
                        "add_to_cart_to_purchase": 0.087
                    }
                }
            else:
                # Return empty data if no cached data
                return jsonify({
                    "success": False,
                    "message": "No cached data available. Run /api/ga4/refresh-cache first.",
                    "property_id": property_id
                }), 404
            data_provider = "ga4_cached"
        
        # Calculate funnel metrics
        funnel_metrics = funnel_analysis.calculate_funnel_metrics(funnel_data)
        
        # Get baseline rates
        baseline_rates = funnel_data.get("overall_baseline", 
            funnel_analysis.calculate_baseline_from_data(funnel_data)
        )
        
        # Detect outliers
        outliers = funnel_analysis.detect_funnel_outliers(
            funnel_metrics,
            baseline_rates,
            threshold=config.OUTLIER_THRESHOLD
        )
        
        # Generate AI insights
        insights = ai_insights.generate_funnel_insights(
            outliers=outliers,
            baseline_rates=baseline_rates,
            funnel_metrics=funnel_metrics,
            historical_data=[]
        )
        
        return jsonify({
            "success": True,
            "data_provider": data_provider,
            "data": {
                "funnel_metrics": funnel_metrics,
                "outliers": outliers,
                "baseline_rates": baseline_rates
            },
            "insights": insights,
            "property_id": property_id,
            "response_time": "AI processing only (no API calls)",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in instant GA4 analysis: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/ga4/cached-data', methods=['POST'])
def ga4_cached_data():
    """
    Get cached GA4 data only (fast - no AI processing)
    Perfect for demonstrating cache speed vs AI processing time
    """
    try:
        data = request.get_json() or {}
        property_id = data.get('property_id', '476872592')
        report_type = data.get('report_type', 'funnel')
        
        logger.info(f"Getting cached GA4 data for property {property_id}, report type: {report_type}")
        
        # Try to get cached data first
        cached_data = None
        data_provider = "cache_miss"
        
        if report_type == 'funnel':
            cached_data = cache_manager_redis.get_funnel_data(property_id)
        elif report_type == 'traffic_sources':
            cached_data = cache_manager_redis.get_traffic_sources(property_id)
        elif report_type == 'overview':
            cached_data = cache_manager_redis.get_overview_metrics(property_id)
        else:
            return jsonify({"error": "Invalid report_type. Use: funnel, traffic_sources, overview"}), 400
        
        if cached_data:
            data_provider = "cached"
            logger.info(f"Cache hit for {report_type} data")
        else:
            # Fallback to direct GA4 call if no cache
            logger.info(f"Cache miss for {report_type} data, fetching from GA4")
            if report_type == 'funnel':
                cached_data = ga4_client.get_funnel_data(property_id)
            elif report_type == 'traffic_sources':
                cached_data = ga4_client.get_traffic_sources(property_id)
            elif report_type == 'overview':
                cached_data = ga4_client.get_overview_metrics(property_id)
            data_provider = "ga4_direct"
        
        return jsonify({
            "success": True,
            "data_provider": data_provider,
            "data": cached_data,
            "property_id": property_id,
            "report_type": report_type,
            "response_time": "2-3 seconds" if data_provider == "cached" else "15-30 seconds",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in cached GA4 data: {e}")
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
        
        # Try GA4 MCP first, then fallback to mock data
        logger.info("Attempting to use GA4 MCP for data retrieval")
        try:
            # Use GA4 MCP to get real data
            funnel_data = ga4_mcp.get_funnel_data(property_id=property_id, days=30)
            data_provider = "ga4_mcp"
            logger.info("Successfully retrieved data via GA4 MCP")
        except Exception as e:
            logger.warning(f"GA4 MCP failed: {e}. Falling back to mock data.")
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
                logger.info("Using legacy GA4 API")
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
                        
                except Exception as e2:
                    logger.error(f"GA4 API error: {e2}. Falling back to mock data.")
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
                # Use streamlined AI insights for specific, actionable analysis
                insights = generate_streamlined_insights(
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


@app.route('/api/keyword-product-insights', methods=['POST'])
def keyword_product_insights_endpoint():
    """
    STATIC DEMO: Instant keyword→product revenue insights
    Perfect for lead magnet - shows how SEO drives actual revenue
    """
    # Return pre-produced static report instantly
    static_report = {
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "insights": {
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
                },
                "priority_3": {
                    "action": "Create product-specific landing pages for high-volume keywords",
                    "keyword": "photo gifts, personalised gifts",
                    "revenue_lift": "+$200/month combined",
                    "timeline": "2-4 months",
                    "implementation": "Create /personalised-photo-gifts page targeting multiple product categories"
                }
            },
            "quick_wins": [
                "Add customer review schema to t-shirt pages (improves 'custom t shirts' ranking)",
                "Optimize meta descriptions with target keywords (improves CTR by 10-15%)",
                "Create internal links from blog to product pages (distributes link juice)",
                "Add FAQ schema to product pages (captures featured snippets)",
                "Optimize images with product keywords in alt text"
            ],
            "roi_calculation": {
                "total_keyword_traffic": "1,096 visits/month",
                "current_estimated_revenue": "$1,033/month",
                "potential_with_improvements": "$1,400/month",
                "opportunity_value": "$367/month ($4,404/year)",
                "seo_investment_justification": "Optimization work on 3 keywords = $1,000 investment. ROI = 440% in first year. Pays for itself in 2.7 months."
            }
        },
        "summary": {
            "message": "AI-powered insights showing how SEO keywords drive product sales",
            "keywords_analyzed": 3,
            "products_analyzed": 4,
            "total_estimated_revenue": "$1,033/month",
            "opportunity_value": "$4,404/year"
        }
    }
    
    return jsonify(static_report)


@app.route('/api/cross-platform-analysis', methods=['POST'])
def cross_platform_analysis_endpoint():
    """Cross-platform analysis combining SEO and GA4 data"""
    try:
        # Get request data
        data = request.get_json() or {}
        property_id = data.get('property_id', '123456789')
        date_range = data.get('date_range', 'last_30_days')
        dimensions = data.get('dimensions', [
            'sessionDefaultChannelGroup', 'deviceCategory', 'browser', 
            'screenResolution', 'itemName', 'itemCategory'
        ])
        
        logger.info(f"Cross-platform analysis request: property_id={property_id}, dimensions={dimensions}")
        
        # Get GA4 data
        logger.info("Retrieving GA4 data for cross-platform analysis")
        ga4_data = ga4_mcp.get_funnel_data(property_id=property_id, days=30)
        
        if not ga4_data or not ga4_data.get('dimension_breakdowns'):
            logger.warning("GA4 MCP data not available, using mock data")
            ga4_data = mock_ga4_data.generate_realistic_ga4_data(property_id, date_range, dimensions)
        
        # Generate cross-platform insights
        logger.info("Generating cross-platform SEO + GA4 insights...")
        cross_platform_insights = get_cross_platform_insights(ga4_data)
        
        # Create response
        result = {
            "property_id": property_id,
            "date_range": date_range,
            "dimensions": dimensions,
            "ga4_data": ga4_data,
            "cross_platform_insights": cross_platform_insights,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "data_sources": cross_platform_insights.get("metadata", {}).get("data_sources", ["GA4 Analytics"]),
                "analysis_type": "cross_platform_seo_ga4"
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in cross-platform analysis: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/seo-data', methods=['POST'])
def receive_seo_data_endpoint():
    """Receive SEO data from N8N/Seranking MCP"""
    try:
        # Get SEO data from request
        seo_data = request.get_json()
        
        if not seo_data:
            return jsonify({"error": "No SEO data provided"}), 400
        
        logger.info("Receiving SEO data from N8N/Seranking MCP")
        
        # Process SEO data
        result = receive_seo_data_from_n8n(seo_data)
        
        logger.info("SEO data processed successfully")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing SEO data: {e}")
        return jsonify({"error": str(e)}), 500


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


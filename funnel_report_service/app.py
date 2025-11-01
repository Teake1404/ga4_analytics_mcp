"""
Standalone Funnel Report Service
Uses EXACT same HTML/CSS/JavaScript from previously deployed demo.html
"""

from flask import Flask, jsonify
from flask_cors import CORS
import logging
import os
import json
import funnel_analysis
import mock_ga4_data
import config
import ai_insights_streamlined

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


@app.route('/', methods=['GET'])
def index():
    """Serve exact same report as previously deployed version using demo.html template"""
    try:
        default_dimensions = [
            "sessionDefaultChannelGroup", "deviceCategory", "browser",
            "screenResolution", "itemName", "itemCategory"
        ]

        funnel_data = mock_ga4_data.generate_mock_funnel_data(
            funnel_steps=["view_item", "add_to_cart", "purchase"],
            dimensions=default_dimensions,
            date_range="last_30_days",
            property_id="123456789"
        )

        funnel_metrics = funnel_analysis.calculate_funnel_metrics(funnel_data)
        baseline_rates = funnel_data.get(
            "overall_baseline",
            funnel_analysis.calculate_baseline_from_data(funnel_data)
        )
        outliers = funnel_analysis.detect_funnel_outliers(
            funnel_metrics, baseline_rates, threshold=config.OUTLIER_THRESHOLD
        )

        # Generate streamlined insights
        insights = ai_insights_streamlined.generate_streamlined_insights(
            outliers, baseline_rates, funnel_metrics
        )

        # Prepare data in exact format expected by demo.html
        # Convert all data to JSON-serializable format
        def make_json_serializable(obj):
            if isinstance(obj, dict):
                return {k: make_json_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_json_serializable(item) for item in obj]
            elif isinstance(obj, (int, float, str, bool, type(None))):
                return obj
            else:
                return str(obj)
        
        report_data = {
            "success": True,
            "data": {
                "funnel_metrics": make_json_serializable(funnel_metrics),
                "outliers": make_json_serializable(outliers),
                "baseline_rates": make_json_serializable(baseline_rates)
            },
            "insights": make_json_serializable(insights)
        }

        # Read the exact demo.html template
        template_path = os.path.join(os.path.dirname(__file__), 'demo_template.html')
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                html_template = f.read()
        except FileNotFoundError:
            logger.error(f"Template file not found: {template_path}")
            return jsonify({"error": "Template file not found"}), 500
        
        # Inject data and auto-run
        # Replace the button click with auto-execution
        data_json = json.dumps(report_data, default=str).replace('</script>', '<\\/script>')  # Escape script tags
        
        # Hide the demo button and auto-run the analysis
        html_template = html_template.replace(
            '<div class="demo-section">',
            f'''<script>
                // Auto-run with data
                var reportData = {data_json};
                window.addEventListener('DOMContentLoaded', function() {{
                    displayResults(reportData);
                    document.getElementById('loading').style.display = 'none';
                }});
            </script>
            <div class="demo-section" style="display:none;">'''
        )
        
        return html_template, 200, {"Content-Type": "text/html"}
        
    except Exception as e:
        logger.error(f"Error rendering funnel report page: {e}", exc_info=True)
        return jsonify({"error": str(e), "message": "Error generating funnel report"}), 500


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "Funnel Report Service", "data_source": "mock"})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

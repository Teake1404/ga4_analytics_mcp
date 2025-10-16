"""
Report Generator Service (Service #2)
Hosts interactive HTML reports with unique shareable URLs
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import logging
import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any
import report_generator_simple as report_generator

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# In-memory storage for reports (use Redis/Cloud Storage in production)
reports_storage = {}

# Report expiration (7 days)
REPORT_EXPIRATION_DAYS = 7


@app.route('/', methods=['GET'])
def index():
    """Service info"""
    return jsonify({
        "service": "GA4 Report Generator",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "/api/generate-report": "POST - Generate report and return URL",
            "/report/{id}": "GET - View report by ID",
            "/api/reports": "GET - List all active reports",
            "/api/health": "GET - Health check"
        }
    })


@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    active_reports = len([r for r in reports_storage.values() if not is_expired(r)])
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_reports": active_reports,
        "total_reports": len(reports_storage)
    })


@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """
    Generate interactive HTML report and return shareable URL
    
    Request body:
    {
        "analysis_data": { ... },  # JSON from AI Insights API
        "expires_in_days": 7       # Optional, default 7
    }
    
    Returns:
    {
        "success": true,
        "report_id": "20251014-abc123",
        "report_url": "https://ga4-reports.run.app/report/20251014-abc123",
        "expires_at": "2025-10-21T09:00:00Z"
    }
    """
    
    try:
        data = request.get_json()
        
        if not data or 'analysis_data' not in data:
            return jsonify({
                "success": False,
                "error": "analysis_data is required"
            }), 400
        
        analysis_data = data['analysis_data']
        expires_in_days = data.get('expires_in_days', REPORT_EXPIRATION_DAYS)
        
        # Generate unique report ID
        date_str = datetime.now().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4())[:8]
        report_id = f"{date_str}-{unique_id}"
        
        # Generate HTML report (client-side rendering = fast!)
        html_report = report_generator.generate_simple_report(analysis_data)
        
        # Calculate expiration
        expires_at = datetime.now() + timedelta(days=expires_in_days)
        
        # Store report
        reports_storage[report_id] = {
            'html': html_report,
            'created_at': datetime.now().isoformat(),
            'expires_at': expires_at.isoformat(),
            'analysis_data': analysis_data,
            'access_count': 0
        }
        
        # Clean up expired reports
        cleanup_expired_reports()
        
        # Build report URL
        base_url = request.host_url.rstrip('/')
        report_url = f"{base_url}/report/{report_id}"
        
        logger.info(f"Generated report: {report_id}, expires: {expires_at}")
        
        return jsonify({
            "success": True,
            "report_id": report_id,
            "report_url": report_url,
            "expires_at": expires_at.isoformat(),
            "created_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating report: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/report/<report_id>', methods=['GET'])
def view_report(report_id):
    """
    Serve HTML report by ID
    
    This is what clients click on from Slack/Email
    """
    
    if report_id not in reports_storage:
        return """
        <html>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>❌ Report Not Found</h1>
            <p>This report doesn't exist or has expired.</p>
            <p>Reports are automatically deleted after 7 days.</p>
        </body>
        </html>
        """, 404
    
    report = reports_storage[report_id]
    
    # Check if expired
    if is_expired(report):
        del reports_storage[report_id]
        return """
        <html>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>⏰ Report Expired</h1>
            <p>This report has expired and is no longer available.</p>
            <p>Reports are kept for 7 days after creation.</p>
        </body>
        </html>
        """, 410
    
    # Increment access count
    report['access_count'] += 1
    
    logger.info(f"Serving report: {report_id}, access count: {report['access_count']}")
    
    return report['html'], 200, {'Content-Type': 'text/html'}


@app.route('/api/reports', methods=['GET'])
def list_reports():
    """List all active reports"""
    
    active_reports = []
    
    for report_id, report in reports_storage.items():
        if not is_expired(report):
            active_reports.append({
                'report_id': report_id,
                'created_at': report['created_at'],
                'expires_at': report['expires_at'],
                'access_count': report['access_count']
            })
    
    return jsonify({
        "success": True,
        "total_active_reports": len(active_reports),
        "reports": sorted(active_reports, key=lambda x: x['created_at'], reverse=True)
    })


def is_expired(report: Dict[str, Any]) -> bool:
    """Check if report is expired"""
    expires_at = datetime.fromisoformat(report['expires_at'])
    return datetime.now() > expires_at


def cleanup_expired_reports():
    """Remove expired reports from storage"""
    expired_ids = [
        report_id for report_id, report in reports_storage.items()
        if is_expired(report)
    ]
    
    for report_id in expired_ids:
        del reports_storage[report_id]
        logger.info(f"Cleaned up expired report: {report_id}")
    
    if expired_ids:
        logger.info(f"Removed {len(expired_ids)} expired reports")


# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "available_endpoints": [
            "/api/generate-report",
            "/report/{id}",
            "/api/reports",
            "/api/health"
        ]
    }), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8081))
    app.run(host='0.0.0.0', port=port, debug=False)


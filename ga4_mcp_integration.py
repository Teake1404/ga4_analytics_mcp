"""
GA4 Direct API Integration Module
Uses GA4 Data API directly (similar to official MCP but without MCP server)
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Import GA4 APIs directly
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.admin_v1beta import AnalyticsAdminServiceClient

logger = logging.getLogger(__name__)

class GA4MCPIntegration:
    """Integration class for GA4 Data API with our AI insights"""
    
    def __init__(self):
        self.data_client = None
        self.admin_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize GA4 clients"""
        try:
            # Initialize clients with Application Default Credentials
            self.data_client = BetaAnalyticsDataClient()
            self.admin_client = AnalyticsAdminServiceClient()
            logger.info("GA4 API clients initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GA4 API clients: {e}")
            self.data_client = None
            self.admin_client = None
    
    def get_property_id(self, property_name: str = None) -> Optional[str]:
        """Get property ID from property name or use default"""
        try:
            if not self.admin_client:
                return None
                
            # Get account summaries
            accounts = self.admin_client.list_account_summaries()
            
            for account in accounts:
                for property in account.property_summaries:
                    if property_name and property_name.lower() in property.display_name.lower():
                        return property.property
                    elif not property_name:  # Use first property if no name specified
                        return property.property
            
            return None
        except Exception as e:
            logger.error(f"Error getting property ID: {e}")
            return None
    
    def get_funnel_data(self, property_id: str = None, days: int = 30) -> Dict[str, Any]:
        """Get funnel data using official GA4 MCP"""
        try:
            if not self.data_client:
                logger.warning("GA4 data client not available, using mock data")
                return self._get_mock_funnel_data()
            
            if not property_id:
                property_id = self.get_property_id()
                if not property_id:
                    logger.warning("No property ID available, using mock data")
                    return self._get_mock_funnel_data()
            
            # Define date range
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # Get funnel data - view_item, add_to_cart, purchase events
            funnel_data = self._run_funnel_report(property_id, start_date, end_date)
            
            return funnel_data
            
        except Exception as e:
            logger.error(f"Error getting funnel data: {e}")
            return self._get_mock_funnel_data()
    
    def _run_funnel_report(self, property_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Run funnel report using GA4 Data API"""
        try:
            # Define the request
            request = {
                "property": f"properties/{property_id}",
                "date_ranges": [{"start_date": start_date, "end_date": end_date}],
                "dimensions": [
                    {"name": "sessionDefaultChannelGroup"},
                    {"name": "deviceCategory"},
                    {"name": "browser"},
                    {"name": "screenResolution"},
                    {"name": "itemName"},
                    {"name": "itemCategory"}
                ],
                "metrics": [
                    {"name": "sessions"},
                    {"name": "totalUsers"},
                    {"name": "eventCount"}
                ],
                "dimension_filter": {
                    "filter": {
                        "field_name": "eventName",
                        "string_filter": {
                            "match_type": "EXACT",
                            "value": "view_item"
                        }
                    }
                }
            }
            
            # Run the report
            response = self.data_client.run_report(request)
            
            # Process the response
            processed_data = self._process_ga4_response(response)
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error running funnel report: {e}")
            return self._get_mock_funnel_data()
    
    def _process_ga4_response(self, response) -> Dict[str, Any]:
        """Process GA4 API response into our expected format"""
        try:
            processed_data = {
                "dimensions": {},
                "metrics": {},
                "baseline_rates": {},
                "outliers": {}
            }
            
            # Process rows from GA4 response
            for row in response.rows:
                # Extract dimension values
                dimensions = {}
                for i, dimension in enumerate(response.dimension_headers):
                    dimensions[dimension.name] = row.dimension_values[i].value
                
                # Extract metric values
                metrics = {}
                for i, metric in enumerate(response.metric_headers):
                    metrics[metric.name] = float(row.metric_values[i].value)
                
                # Store the data
                dimension_key = f"{dimensions.get('sessionDefaultChannelGroup', 'Unknown')}_{dimensions.get('deviceCategory', 'Unknown')}"
                processed_data["dimensions"][dimension_key] = {
                    "dimensions": dimensions,
                    "metrics": metrics
                }
            
            # Calculate baseline rates and outliers
            processed_data = self._calculate_baseline_and_outliers(processed_data)
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error processing GA4 response: {e}")
            return self._get_mock_funnel_data()
    
    def _calculate_baseline_and_outliers(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate baseline rates and identify outliers"""
        try:
            # Calculate overall baseline rates
            total_sessions = sum(row["metrics"].get("sessions", 0) for row in data["dimensions"].values())
            total_events = sum(row["metrics"].get("eventCount", 0) for row in data["dimensions"].values())
            
            baseline_conversion_rate = (total_events / total_sessions * 100) if total_sessions > 0 else 0
            
            data["baseline_rates"] = {
                "overall_conversion_rate": baseline_conversion_rate,
                "total_sessions": total_sessions,
                "total_events": total_events
            }
            
            # Identify outliers (simplified logic)
            outliers = {}
            for dimension, row in data["dimensions"].items():
                sessions = row["metrics"].get("sessions", 0)
                events = row["metrics"].get("eventCount", 0)
                conversion_rate = (events / sessions * 100) if sessions > 0 else 0
                
                # Consider outlier if conversion rate is significantly different from baseline
                if abs(conversion_rate - baseline_conversion_rate) > baseline_conversion_rate * 0.3:
                    outliers[dimension] = {
                        "conversion_rate": conversion_rate,
                        "deviation": conversion_rate - baseline_conversion_rate,
                        "sessions": sessions,
                        "events": events
                    }
            
            data["outliers"] = outliers
            
            return data
            
        except Exception as e:
            logger.error(f"Error calculating baseline and outliers: {e}")
            return data
    
    def _get_mock_funnel_data(self) -> Dict[str, Any]:
        """Fallback to mock data if GA4 API fails"""
        try:
            with open('pre_generated_mock_data.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading mock data: {e}")
            return {
                "dimensions": {},
                "metrics": {},
                "baseline_rates": {"overall_conversion_rate": 1.32},
                "outliers": {}
            }
    
    def get_property_details(self, property_id: str = None) -> Dict[str, Any]:
        """Get property details using GA4 MCP"""
        try:
            if not self.admin_client or not property_id:
                return {"error": "Admin client not available or no property ID"}
            
            # Get property details
            property_details = self.admin_client.get_property(name=f"properties/{property_id}")
            
            return {
                "display_name": property_details.display_name,
                "time_zone": property_details.time_zone,
                "create_time": property_details.create_time.isoformat(),
                "update_time": property_details.update_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting property details: {e}")
            return {"error": str(e)}
    
    def get_custom_dimensions(self, property_id: str = None) -> List[Dict[str, Any]]:
        """Get custom dimensions using GA4 MCP"""
        try:
            if not self.admin_client or not property_id:
                return []
            
            # Get custom dimensions
            custom_dimensions = self.admin_client.list_custom_dimensions(parent=f"properties/{property_id}")
            
            dimensions = []
            for dimension in custom_dimensions:
                dimensions.append({
                    "name": dimension.display_name,
                    "parameter_name": dimension.parameter_name,
                    "scope": dimension.scope.name,
                    "description": dimension.description
                })
            
            return dimensions
            
        except Exception as e:
            logger.error(f"Error getting custom dimensions: {e}")
            return []

# Global instance
ga4_mcp = GA4MCPIntegration()

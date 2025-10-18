"""
GA4 Client with Service Account Authentication
Handles direct Google Analytics Data API calls
"""
import json
import os
from typing import List, Dict, Any, Optional
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest, 
    DateRange, 
    Metric, 
    Dimension,
    Filter,
    FilterExpression
)
from google.oauth2 import service_account
import logging

logger = logging.getLogger(__name__)

class GA4Client:
    def __init__(self):
        """Initialize GA4 client with service account credentials"""
        self.client = self._get_client()
    
    def _get_client(self) -> BetaAnalyticsDataClient:
        """Get authenticated GA4 client"""
        try:
            # Try environment variable first (for Cloud Run)
            sa_json = os.getenv("GA4_SA_JSON")
            if sa_json:
                credentials = service_account.Credentials.from_service_account_info(
                    json.loads(sa_json),
                    scopes=["https://www.googleapis.com/auth/analytics.readonly"]
                )
            else:
                # Fallback to file path
                credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
                if not credentials_path:
                    raise ValueError("Either GA4_SA_JSON or GOOGLE_APPLICATION_CREDENTIALS must be set")
                
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path,
                    scopes=["https://www.googleapis.com/auth/analytics.readonly"]
                )
            
            return BetaAnalyticsDataClient(credentials=credentials)
        except Exception as e:
            logger.error(f"Failed to initialize GA4 client: {e}")
            raise
    
    def get_funnel_data(self, property_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get funnel data using event-based approach
        Returns data suitable for AI analysis
        """
        try:
            request = RunReportRequest(
                property=f"properties/{property_id}",
                date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
                dimensions=[
                    Dimension(name="eventName"),
                    Dimension(name="deviceCategory"),
                    Dimension(name="browser"),
                    Dimension(name="date")
                ],
                metrics=[
                    Metric(name="eventCount"),
                    Metric(name="sessions"),
                    Metric(name="screenPageViews"),
                    Metric(name="totalUsers")
                ],
                dimension_filter=FilterExpression(
                    filter=Filter(
                        field_name="eventName",
                        in_list_filter=Filter.InListFilter(
                            values=["purchase", "add_to_cart", "begin_checkout"]
                        )
                    )
                ),
                keep_empty_rows=False
            )
            
            response = self.client.run_report(request)
            
            # Convert to list of dictionaries
            rows = []
            for row in response.rows:
                row_data = {}
                
                # Add dimensions
                for i, dimension in enumerate(response.dimension_headers):
                    row_data[dimension.name] = row.dimension_values[i].value
                
                # Add metrics
                for i, metric in enumerate(response.metric_headers):
                    row_data[metric.name] = row.metric_values[i].value
                
                rows.append(row_data)
            
            # Transform to funnel format
            return self._transform_to_funnel_format(rows)
            
        except Exception as e:
            logger.error(f"Failed to get funnel data: {e}")
            raise
    
    def _transform_to_funnel_format(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform event-based data to funnel format
        Maps events to funnel metrics
        """
        # Group by deviceCategory, browser, date
        grouped = {}
        
        for row in rows:
            key = f"{row.get('deviceCategory', 'unknown')}_{row.get('browser', 'unknown')}_{row.get('date', 'unknown')}"
            
            if key not in grouped:
                grouped[key] = {
                    'deviceCategory': row.get('deviceCategory', 'unknown'),
                    'browser': row.get('browser', 'unknown'),
                    'date': row.get('date', 'unknown'),
                    'sessions': int(row.get('sessions', 0)),
                    'screenPageViews': int(row.get('screenPageViews', 0)),
                    'totalUsers': int(row.get('totalUsers', 0)),
                    'purchases': 0,
                    'addToCarts': 0,
                    'checkouts': 0
                }
            
            # Map events to funnel metrics
            event_name = row.get('eventName', '')
            event_count = int(row.get('eventCount', 0))
            
            if event_name == 'purchase':
                grouped[key]['purchases'] = event_count
            elif event_name == 'add_to_cart':
                grouped[key]['addToCarts'] = event_count
            elif event_name == 'begin_checkout':
                grouped[key]['checkouts'] = event_count
        
        return list(grouped.values())
    
    def get_traffic_sources(self, property_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get traffic source data"""
        try:
            request = RunReportRequest(
                property=f"properties/{property_id}",
                date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
                dimensions=[
                    Dimension(name="sessionDefaultChannelGroup"),
                    Dimension(name="deviceCategory")
                ],
                metrics=[
                    Metric(name="sessions"),
                    Metric(name="screenPageViews"),
                    Metric(name="totalUsers")
                ],
                keep_empty_rows=False
            )
            
            response = self.client.run_report(request)
            
            rows = []
            for row in response.rows:
                row_data = {}
                
                for i, dimension in enumerate(response.dimension_headers):
                    row_data[dimension.name] = row.dimension_values[i].value
                
                for i, metric in enumerate(response.metric_headers):
                    row_data[metric.name] = row.metric_values[i].value
                
                rows.append(row_data)
            
            return rows
            
        except Exception as e:
            logger.error(f"Failed to get traffic sources: {e}")
            raise
    
    def get_overview_metrics(self, property_id: str, days: int = 30) -> Dict[str, Any]:
        """Get overall property metrics"""
        try:
            request = RunReportRequest(
                property=f"properties/{property_id}",
                date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
                metrics=[
                    Metric(name="totalUsers"),
                    Metric(name="sessions"),
                    Metric(name="screenPageViews"),
                    Metric(name="bounceRate"),
                    Metric(name="averageSessionDuration")
                ],
                keep_empty_rows=False
            )
            
            response = self.client.run_report(request)
            
            if not response.rows:
                return {}
            
            # Get first row (aggregated data)
            row = response.rows[0]
            metrics = {}
            
            for i, metric in enumerate(response.metric_headers):
                metrics[metric.name] = row.metric_values[i].value
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get overview metrics: {e}")
            raise


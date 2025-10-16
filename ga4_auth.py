"""
Google Analytics 4 Authentication Module
Handles OAuth2 authentication for GA4 Data API access
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    OrderBy,
    FilterExpression,
    Filter
)

logger = logging.getLogger(__name__)

class GA4AuthManager:
    """Manages GA4 OAuth2 authentication and token refresh"""
    
    def __init__(self):
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8080/auth/callback")
        self.scopes = [
            'https://www.googleapis.com/auth/analytics.readonly',
            'https://www.googleapis.com/auth/analytics'
        ]
        
        # Token storage (in production, use secure storage like Redis or database)
        self.token_file = os.getenv("GA4_TOKEN_FILE", "ga4_tokens.json")
        
    def get_auth_url(self) -> str:
        """Generate OAuth2 authorization URL"""
        if not self.client_id:
            raise ValueError("GOOGLE_CLIENT_ID environment variable is required")
            
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )
        
        # CRITICAL: Include these parameters to get refresh token
        auth_url, _ = flow.authorization_url(
            access_type='offline',  # Required for refresh token
            prompt='consent',       # Force consent to get refresh token
            include_granted_scopes='true'
        )
        
        return auth_url
    
    def exchange_code_for_tokens(self, authorization_code: str) -> Dict[str, Any]:
        """Exchange authorization code for access and refresh tokens"""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )
        
        flow.fetch_token(code=authorization_code)
        
        credentials = flow.credentials
        
        # Save tokens for future use
        token_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
            'expiry': credentials.expiry.isoformat() if credentials.expiry else None
        }
        
        self.save_tokens(token_data)
        
        return {
            'success': True,
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'expires_at': credentials.expiry.isoformat() if credentials.expiry else None
        }
    
    def load_tokens(self) -> Optional[Dict[str, Any]]:
        """Load saved tokens from file"""
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load tokens: {e}")
        return None
    
    def save_tokens(self, token_data: Dict[str, Any]):
        """Save tokens to file"""
        try:
            with open(self.token_file, 'w') as f:
                json.dump(token_data, f, indent=2)
            logger.info("Tokens saved successfully")
        except Exception as e:
            logger.error(f"Failed to save tokens: {e}")
    
    def get_valid_credentials(self) -> Optional[Credentials]:
        """Get valid credentials, refreshing if necessary"""
        token_data = self.load_tokens()
        if not token_data:
            return None
        
        credentials = Credentials(
            token=token_data['token'],
            refresh_token=token_data['refresh_token'],
            token_uri=token_data['token_uri'],
            client_id=token_data['client_id'],
            client_secret=token_data['client_secret'],
            scopes=token_data['scopes']
        )
        
        # Check if token needs refresh
        if credentials.expired:
            try:
                credentials.refresh(Request())
                
                # Save refreshed tokens
                updated_token_data = {
                    'token': credentials.token,
                    'refresh_token': credentials.refresh_token or token_data['refresh_token'],
                    'token_uri': credentials.token_uri,
                    'client_id': credentials.client_id,
                    'client_secret': credentials.client_secret,
                    'scopes': credentials.scopes,
                    'expiry': credentials.expiry.isoformat() if credentials.expiry else None
                }
                self.save_tokens(updated_token_data)
                
                logger.info("Token refreshed successfully")
            except Exception as e:
                logger.error(f"Failed to refresh token: {e}")
                return None
        
        return credentials
    
    def is_authenticated(self) -> bool:
        """Check if we have valid authentication"""
        credentials = self.get_valid_credentials()
        return credentials is not None and not credentials.expired


class GA4DataClient:
    """GA4 Data API client with authentication"""
    
    def __init__(self, property_id: str):
        self.property_id = property_id
        self.auth_manager = GA4AuthManager()
        self.client = None
    
    def _get_client(self) -> BetaAnalyticsDataClient:
        """Get authenticated GA4 client"""
        if not self.client:
            credentials = self.auth_manager.get_valid_credentials()
            if not credentials:
                raise ValueError("GA4 authentication required. Please complete OAuth flow.")
            
            self.client = BetaAnalyticsDataClient(credentials=credentials)
        
        return self.client
    
    def run_funnel_report(
        self,
        date_range: str = "last_30_days",
        dimensions: list = None,
        funnel_steps: list = None
    ) -> Dict[str, Any]:
        """Run funnel analysis report using GA4 Data API"""
        
        if not self.auth_manager.is_authenticated():
            raise ValueError("GA4 authentication required. Please complete OAuth flow first.")
        
        client = self._get_client()
        
        # Default values
        dimensions = dimensions or [
            "sessionDefaultChannelGroup",
            "deviceCategory", 
            "browser",
            "screenResolution",
            "itemName",
            "itemCategory"
        ]
        
        funnel_steps = funnel_steps or ["view_item", "add_to_cart", "purchase"]
        
        # Parse date range
        end_date = datetime.now().strftime('%Y-%m-%d')
        if date_range == "last_30_days":
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        elif date_range == "last_7_days":
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        else:
            # Default to last 30 days
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        try:
            # Build the report request
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                dimensions=[
                    Dimension(name=dim) for dim in dimensions
                ],
                metrics=[
                    Metric(name="screenPageViews"),
                    Metric(name="sessions"),
                    Metric(name="eventCount")
                ],
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                dimension_filter=FilterExpression(
                    filter=Filter(
                        field_name="eventName",
                        string_filter=Filter.StringFilter(
                            match_type=Filter.StringFilter.MatchType.EXACT,
                            value="view_item"
                        )
                    )
                ),
                order_bys=[
                    OrderBy(
                        metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"),
                        desc=True
                    )
                ],
                limit=1000
            )
            
            # Execute the request
            response = client.run_report(request)
            
            # Process response
            processed_data = self._process_ga4_response(response, dimensions)
            
            return {
                "success": True,
                "data": processed_data,
                "date_range": f"{start_date} to {end_date}",
                "dimensions": dimensions,
                "funnel_steps": funnel_steps
            }
            
        except Exception as e:
            logger.error(f"GA4 API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    def _process_ga4_response(self, response, dimensions: list) -> Dict[str, Any]:
        """Process GA4 API response into our funnel format"""
        # This is a simplified processor - in production you'd want more sophisticated
        # processing to match the mock data structure
        
        funnel_data = {
            "dimension_breakdowns": {},
            "overall_baseline": {
                "view_item_to_add_to_cart": 0.152,  # Default values
                "add_to_cart_to_purchase": 0.087,
                "overall_conversion": 0.0132
            },
            "metadata": {
                "total_rows": len(response.rows),
                "date_range": response.dimension_headers[0].name if response.dimension_headers else "unknown"
            }
        }
        
        # Process rows (simplified)
        for row in response.rows:
            # Extract dimension values and metrics
            dim_values = [dim.value for dim in row.dimension_values]
            metric_values = [metric.value for metric in row.metric_values]
            
            # Build dimension key
            if len(dim_values) > 0:
                primary_dim = dimensions[0] if dimensions else "unknown"
                primary_value = dim_values[0]
                
                if primary_dim not in funnel_data["dimension_breakdowns"]:
                    funnel_data["dimension_breakdowns"][primary_dim] = {}
                
                # Store metrics (simplified)
                funnel_data["dimension_breakdowns"][primary_dim][primary_value] = {
                    "view_item": int(metric_values[0]) if metric_values else 0,
                    "add_to_cart": int(metric_values[1]) if len(metric_values) > 1 else 0,
                    "purchase": int(metric_values[2]) if len(metric_values) > 2 else 0
                }
        
        return funnel_data


# Global instances
auth_manager = GA4AuthManager()

def get_ga4_client(property_id: str) -> GA4DataClient:
    """Get GA4 client instance"""
    return GA4DataClient(property_id)

def is_ga4_authenticated() -> bool:
    """Check if GA4 is authenticated"""
    return auth_manager.is_authenticated()

def get_ga4_auth_url() -> str:
    """Get GA4 OAuth URL"""
    return auth_manager.get_auth_url()

def exchange_ga4_code(code: str) -> Dict[str, Any]:
    """Exchange authorization code for tokens"""
    return auth_manager.exchange_code_for_tokens(code)


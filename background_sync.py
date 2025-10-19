"""
Background Sync Service for GA4 Cache Refresh
Runs scheduled jobs to keep GA4 data fresh in Redis cache
"""
import schedule
import time
import logging
import requests
import os
from datetime import datetime
import threading

logger = logging.getLogger(__name__)

class BackgroundSyncService:
    def __init__(self, api_base_url: str = None):
        """
        Initialize background sync service
        
        Args:
            api_base_url: Base URL of the API (for self-calling)
        """
        self.api_base_url = api_base_url or os.getenv("API_BASE_URL", "http://localhost:8080")
        self.running = False
        self.sync_thread = None
        
    def sync_ga4_cache(self, property_id: str = "476872592"):
        """
        Sync GA4 cache by calling the refresh endpoint
        """
        try:
            url = f"{self.api_base_url}/api/ga4/refresh-cache"
            payload = {"property_id": property_id}
            
            logger.info(f"Starting GA4 cache sync for property {property_id}")
            
            response = requests.post(url, json=payload, timeout=300)  # 5 min timeout
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Cache sync successful: {result.get('message')}")
                return True
            else:
                logger.error(f"Cache sync failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error during cache sync: {e}")
            return False
    
    def start_scheduler(self, property_id: str = "476872592", interval_minutes: int = 120):
        """
        Start the background scheduler
        
        Args:
            property_id: GA4 property ID to sync
            interval_minutes: Sync interval in minutes
        """
        if self.running:
            logger.warning("Background sync is already running")
            return
        
        # Schedule the sync job
        schedule.every(interval_minutes).minutes.do(
            self.sync_ga4_cache, 
            property_id=property_id
        )
        
        # Run initial sync
        logger.info(f"Running initial GA4 cache sync for property {property_id}")
        self.sync_ga4_cache(property_id)
        
        # Start the scheduler in a separate thread
        self.running = True
        self.sync_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.sync_thread.start()
        
        logger.info(f"Background sync started - refreshing every {interval_minutes} minutes")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)
    
    def stop_scheduler(self):
        """Stop the background scheduler"""
        if not self.running:
            return
        
        self.running = False
        schedule.clear()
        
        if self.sync_thread and self.sync_thread.is_alive():
            self.sync_thread.join(timeout=5)
        
        logger.info("Background sync stopped")
    
    def get_sync_status(self):
        """Get current sync status"""
        return {
            "running": self.running,
            "next_sync": schedule.next_run().isoformat() if schedule.jobs else None,
            "api_base_url": self.api_base_url,
            "timestamp": datetime.now().isoformat()
        }


# Global sync service instance
sync_service = BackgroundSyncService()


def start_background_sync(property_id: str = "476872592", interval_minutes: int = 120):
    """Start background sync service"""
    sync_service.start_scheduler(property_id, interval_minutes)


def stop_background_sync():
    """Stop background sync service"""
    sync_service.stop_scheduler()


def get_sync_status():
    """Get sync service status"""
    return sync_service.get_sync_status()


# CLI usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="GA4 Background Sync Service")
    parser.add_argument("--property-id", default="476872592", help="GA4 Property ID")
    parser.add_argument("--interval", type=int, default=120, help="Sync interval in minutes")
    parser.add_argument("--api-url", help="API base URL")
    parser.add_argument("--once", action="store_true", help="Run sync once and exit")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if args.api_url:
        sync_service.api_base_url = args.api_url
    
    if args.once:
        # Run once and exit
        success = sync_service.sync_ga4_cache(args.property_id)
        exit(0 if success else 1)
    else:
        # Start continuous sync
        try:
            sync_service.start_scheduler(args.property_id, args.interval)
            
            # Keep running
            while True:
                time.sleep(60)
                
        except KeyboardInterrupt:
            logger.info("Shutting down background sync...")
            sync_service.stop_scheduler()


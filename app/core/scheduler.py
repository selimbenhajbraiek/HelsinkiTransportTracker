from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
import logging
import atexit

from app.core.config import settings
from app.services.digitransit_service import DigitransitService
from app.services.data_services import DataService

logger = logging.getLogger(__name__)

# Create scheduler
scheduler = BackgroundScheduler()

def collect_vehicle_data():
    """Collect and store vehicle data from Digitransit API"""
    try:
        logger.info("Collecting vehicle data")
        digitransit_service = DigitransitService()
        data_service = DataService()
        
        vehicles = digitransit_service.get_vehicles()
        if vehicles:
            data_service.store_vehicle_data(vehicles)
            logger.info(f"Stored {len(vehicles)} vehicle records")
    except Exception as e:
        logger.error(f"Error collecting vehicle data: {str(e)}")

def cleanup_old_data():
    """Clean up old data from the database"""
    try:
        logger.info("Cleaning up old data")
        data_service = DataService()
        cutoff_date = datetime.now() - timedelta(days=settings.DATA_RETENTION_DAYS)
        deleted_count = data_service.delete_old_data(cutoff_date)
        logger.info(f"Deleted {deleted_count} old records")
    except Exception as e:
        logger.error(f"Error cleaning up old data: {str(e)}")

def start_scheduler():
    """Start the scheduler with the defined jobs"""
    # Add jobs
    scheduler.add_job(
        func=collect_vehicle_data,
        trigger=IntervalTrigger(seconds=settings.VEHICLE_COLLECTION_INTERVAL),
        id="collect_vehicle_data",
        replace_existing=True
    )
    
    scheduler.add_job(
        func=cleanup_old_data,
        trigger=IntervalTrigger(seconds=settings.CLEANUP_INTERVAL),
        id="cleanup_old_data",
        replace_existing=True
    )
    
    # Start the scheduler if not already running
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")
        
        # Shut down the scheduler when exiting the app
        atexit.register(lambda: scheduler.shutdown())
    else:
        logger.info("Scheduler already running")
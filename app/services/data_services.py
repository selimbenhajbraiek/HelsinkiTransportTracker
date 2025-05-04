from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
import logging
from models import db, Vehicle as DBVehicle, Position as DBPosition
from models import TransportStats as DBTransportStats, VehicleMode
from app.models.transport import Vehicle, Position, TransportStats, TransportCount
import json

logger = logging.getLogger(__name__)

class DataService:
    def __init__(self):
        """Initialize Data Service"""
        logger.info("Initializing Data Service")
    
    def store_vehicle_data(self, vehicles: List[Vehicle]):
        """Store vehicle data in PostgreSQL database"""
        try:
            for vehicle_data in vehicles:
                # Check if vehicle already exists
                vehicle = DBVehicle.query.filter_by(vehicle_id=vehicle_data.id).first()
                
                if not vehicle:
                    # Create new vehicle
                    vehicle = DBVehicle(
                        vehicle_id=vehicle_data.id,
                        route_id=vehicle_data.route_id,
                        trip_id=vehicle_data.trip_id,
                        mode=vehicle_data.mode.value,
                        speed=vehicle_data.speed,
                        heading=vehicle_data.heading,
                        vehicle_number=vehicle_data.vehicle_number,
                        operator_id=vehicle_data.operator_id,
                        timestamp=vehicle_data.timestamp
                    )
                    
                    # Create position
                    position = DBPosition(
                        lat=vehicle_data.position.lat,
                        lng=vehicle_data.position.lng
                    )
                    
                    # Associate position with vehicle
                    vehicle.position = position
                    
                    # Add to database
                    db.session.add(vehicle)
                else:
                    # Update existing vehicle
                    vehicle.route_id = vehicle_data.route_id
                    vehicle.trip_id = vehicle_data.trip_id
                    vehicle.mode = vehicle_data.mode.value
                    vehicle.speed = vehicle_data.speed
                    vehicle.heading = vehicle_data.heading
                    vehicle.timestamp = vehicle_data.timestamp
                    
                    # Update position
                    if vehicle.position:
                        vehicle.position.lat = vehicle_data.position.lat
                        vehicle.position.lng = vehicle_data.position.lng
                    else:
                        position = DBPosition(
                            lat=vehicle_data.position.lat,
                            lng=vehicle_data.position.lng
                        )
                        vehicle.position = position
            
            # Commit all changes
            db.session.commit()
            
            # Update statistics
            self._update_hourly_stats(vehicles)
            self._update_type_stats(vehicles)
            
            return len(vehicles)
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error storing vehicle data: {str(e)}")
            raise
    
    def _update_hourly_stats(self, vehicles: List[Vehicle]):
        """Update hourly vehicle count statistics"""
        try:
            hour = datetime.now().replace(minute=0, second=0, microsecond=0)
            
            # Get or create hourly stats
            hourly_stats = DBTransportStats.query.filter_by(
                category="hourly",
                timestamp=hour
            ).first()
            
            if not hourly_stats:
                hourly_stats = DBTransportStats(
                    timestamp=hour,
                    category="hourly",
                    count=len(vehicles),
                    details={"modes": {}}
                )
                db.session.add(hourly_stats)
            else:
                hourly_stats.count += len(vehicles)
            
            # Update vehicle counts by mode
            for vehicle in vehicles:
                mode = vehicle.mode.value
                details = hourly_stats.details or {"modes": {}}
                
                if "modes" not in details:
                    details["modes"] = {}
                
                if mode in details["modes"]:
                    details["modes"][mode] += 1
                else:
                    details["modes"][mode] = 1
                
                hourly_stats.details = details
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating hourly stats: {str(e)}")
            
    def _update_type_stats(self, vehicles: List[Vehicle]):
        """Update vehicle type statistics"""
        try:
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Count vehicles by type
            type_counts = {}
            for vehicle in vehicles:
                mode = vehicle.mode.value
                if mode in type_counts:
                    type_counts[mode] += 1
                else:
                    type_counts[mode] = 1
            
            # Update stats for each type
            for mode, count in type_counts.items():
                type_stats = DBTransportStats.query.filter_by(
                    category="type",
                    timestamp=today,
                    details={"mode": mode}
                ).first()
                
                if not type_stats:
                    type_stats = DBTransportStats(
                        timestamp=today,
                        category="type",
                        count=count,
                        details={"mode": mode}
                    )
                    db.session.add(type_stats)
                else:
                    type_stats.count += count
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating type stats: {str(e)}")
    
    def delete_old_data(self, cutoff_date: datetime) -> int:
        """Delete data older than the cutoff date"""
        try:
            # Delete old vehicles and related positions
            old_vehicles = DBVehicle.query.filter(DBVehicle.timestamp < cutoff_date).all()
            
            # Count for return
            deleted_count = len(old_vehicles)
            
            # Delete related positions first
            for vehicle in old_vehicles:
                if vehicle.position:
                    db.session.delete(vehicle.position)
            
            # Then delete vehicles
            for vehicle in old_vehicles:
                db.session.delete(vehicle)
            
            # Delete old stats
            old_stats = DBTransportStats.query.filter(DBTransportStats.timestamp < cutoff_date).all()
            deleted_count += len(old_stats)
            
            for stat in old_stats:
                db.session.delete(stat)
            
            db.session.commit()
            return deleted_count
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting old data: {str(e)}")
            raise
    
    def get_hourly_stats(self, date_str: Optional[str] = None) -> List[TransportCount]:
        """Get hourly transport statistics"""
        try:
            if date_str:
                date = datetime.strptime(date_str, "%Y-%m-%d")
                start_time = date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_time = date.replace(hour=23, minute=59, second=59, microsecond=999999)
            else:
                # Default to today
                now = datetime.now()
                start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
                end_time = now
            
            # Query hourly stats
            stats_db = DBTransportStats.query.filter(
                DBTransportStats.category == "hourly",
                DBTransportStats.timestamp >= start_time,
                DBTransportStats.timestamp <= end_time
            ).order_by(DBTransportStats.timestamp).all()
            
            # Convert to TransportCount objects
            result = []
            for stat in stats_db:
                result.append(TransportCount(
                    timestamp=stat.timestamp,
                    category=f"hour-{stat.timestamp.hour}",
                    count=stat.count,
                    details=stat.details
                ))
            
            return result
        except Exception as e:
            logger.error(f"Error fetching hourly stats: {str(e)}")
            raise
    
    def get_daily_stats(self, 
                       start_date_str: Optional[str] = None,
                       end_date_str: Optional[str] = None) -> List[TransportCount]:
        """Get daily transport statistics"""
        try:
            if start_date_str:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            else:
                # Default to 7 days ago
                start_date = datetime.now() - datetime(days=7)
            
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            if end_date_str:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            else:
                # Default to today
                end_date = datetime.now()
            
            # Aggregate hourly stats into daily stats
            daily_stats = {}
            
            # Query hourly stats
            hourly_stats = DBTransportStats.query.filter(
                DBTransportStats.category == "hourly",
                DBTransportStats.timestamp >= start_date,
                DBTransportStats.timestamp <= end_date
            ).order_by(DBTransportStats.timestamp).all()
            
            # Aggregate by day
            for stat in hourly_stats:
                day_key = stat.timestamp.strftime("%Y-%m-%d")
                if day_key in daily_stats:
                    daily_stats[day_key]["count"] += stat.count
                    
                    # Aggregate modes
                    if stat.details and "modes" in stat.details:
                        for mode, mode_count in stat.details["modes"].items():
                            if mode in daily_stats[day_key]["details"]["modes"]:
                                daily_stats[day_key]["details"]["modes"][mode] += mode_count
                            else:
                                daily_stats[day_key]["details"]["modes"][mode] = mode_count
                else:
                    daily_stats[day_key] = {
                        "timestamp": stat.timestamp.replace(hour=0, minute=0, second=0, microsecond=0),
                        "count": stat.count,
                        "details": {"modes": {}}
                    }
                    
                    if stat.details and "modes" in stat.details:
                        daily_stats[day_key]["details"]["modes"] = stat.details["modes"].copy()
            
            # Convert to TransportCount objects
            result = []
            for day_key, data in daily_stats.items():
                result.append(TransportCount(
                    timestamp=data["timestamp"],
                    category=f"day-{day_key}",
                    count=data["count"],
                    details=data["details"]
                ))
            
            # Sort by timestamp
            result.sort(key=lambda x: x.timestamp)
            
            return result
        except Exception as e:
            logger.error(f"Error fetching daily stats: {str(e)}")
            raise
    
    def get_stats_by_type(self) -> List[TransportCount]:
        """Get transport statistics by vehicle type"""
        try:
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Query type stats
            stats_db = DBTransportStats.query.filter(
                DBTransportStats.category == "type",
                DBTransportStats.timestamp >= today
            ).all()
            
            # Convert to TransportCount objects
            result = []
            for stat in stats_db:
                if stat.details and "mode" in stat.details:
                    result.append(TransportCount(
                        timestamp=stat.timestamp,
                        category=f"type-{stat.details['mode']}",
                        count=stat.count,
                        details={"mode": stat.details["mode"]}
                    ))
            
            return result
        except Exception as e:
            logger.error(f"Error fetching stats by type: {str(e)}")
            raise
    
    def get_stats_by_station(self, limit: int = 10) -> List[TransportCount]:
        """
        Get transport statistics by station
        
        Note: This would require additional processing 
        to match vehicle positions with stations.
        For now, this is a simplified implementation.
        """
        try:
            # In a real implementation, this would calculate counts of vehicles
            # visiting each station or calculate passenger numbers
            # For now, we'll return a simple placeholder
            
            # Simulated data
            stations = [
                {"id": "HSL:1070129", "name": "Central Railway Station", "count": 1845},
                {"id": "HSL:1130146", "name": "Pasila", "count": 1253},
                {"id": "HSL:1150108", "name": "Itäkeskus", "count": 1087},
                {"id": "HSL:1030423", "name": "Kamppi", "count": 954},
                {"id": "HSL:1230101", "name": "Leppävaara", "count": 823},
                {"id": "HSL:1291106", "name": "Tikkurila", "count": 742},
                {"id": "HSL:1301106", "name": "Malmi", "count": 621},
                {"id": "HSL:1401110", "name": "Myyrmäki", "count": 543},
                {"id": "HSL:1431134", "name": "Espoo Centre", "count": 489},
                {"id": "HSL:1173123", "name": "Herttoniemi", "count": 412}
            ]
            
            # Only return the requested number of stations
            stations = stations[:limit]
            
            # Create timestamp for today
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Convert to TransportCount objects
            result = []
            for station in stations:
                result.append(TransportCount(
                    timestamp=today,
                    category=f"station-{station['id']}",
                    count=station["count"],
                    details={"name": station["name"], "id": station["id"]}
                ))
            
            return result
        except Exception as e:
            logger.error(f"Error fetching stats by station: {str(e)}")
            raise
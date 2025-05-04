from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class VehicleMode(str, Enum):
    """Vehicle mode/type enum"""
    BUS = "BUS"
    TRAM = "TRAM"
    TRAIN = "TRAIN"
    SUBWAY = "SUBWAY"
    FERRY = "FERRY"

class Position(BaseModel):
    """Vehicle position model"""
    lat: float
    lng: float
    
    def to_dict(self):
        return {
            "lat": self.lat,
            "lng": self.lng
        }

class Vehicle(BaseModel):
    """Vehicle model"""
    id: str
    route_id: Optional[str] = None
    trip_id: Optional[str] = None
    mode: VehicleMode
    position: Position
    speed: Optional[float] = None
    heading: Optional[int] = None
    vehicle_number: Optional[str] = None
    operator_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    def to_dict(self):
        return {
            "id": self.id,
            "route_id": self.route_id,
            "trip_id": self.trip_id,
            "mode": self.mode.value,
            "position": self.position.to_dict(),
            "speed": self.speed,
            "heading": self.heading,
            "vehicle_number": self.vehicle_number,
            "operator_id": self.operator_id,
            "timestamp": self.timestamp.isoformat()
        }

class Station(BaseModel):
    """Station/stop model"""
    id: str
    name: str
    code: Optional[str] = None
    position: Position
    routes: Optional[List[str]] = None
    platform_code: Optional[str] = None
    description: Optional[str] = None
    zone_id: Optional[str] = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "position": self.position.to_dict(),
            "routes": self.routes,
            "platform_code": self.platform_code,
            "description": self.description,
            "zone_id": self.zone_id
        }

class RoutePattern(BaseModel):
    """Route pattern model"""
    id: str
    name: Optional[str] = None
    stops: List[str] = []
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "stops": self.stops
        }

class Route(BaseModel):
    """Transport route model"""
    id: str
    short_name: str
    long_name: Optional[str] = None
    mode: VehicleMode
    operator_id: Optional[str] = None
    patterns: List[RoutePattern] = []
    color: Optional[str] = None
    text_color: Optional[str] = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "short_name": self.short_name,
            "long_name": self.long_name,
            "mode": self.mode.value,
            "operator_id": self.operator_id,
            "patterns": [p.to_dict() for p in self.patterns],
            "color": self.color,
            "text_color": self.text_color
        }

class TransportStats(BaseModel):
    """Transport statistics model"""
    total_vehicles: int
    vehicles_by_mode: Dict[VehicleMode, int]
    busiest_routes: List[Dict[str, Any]]
    busiest_stops: List[Dict[str, Any]]
    peak_hours: List[Dict[str, Any]]
    
    def to_dict(self):
        return {
            "total_vehicles": self.total_vehicles,
            "vehicles_by_mode": {k.value: v for k, v in self.vehicles_by_mode.items()},
            "busiest_routes": self.busiest_routes,
            "busiest_stops": self.busiest_stops,
            "peak_hours": self.peak_hours
        }

class TransportCount(BaseModel):
    """Transport count model for time-series data"""
    timestamp: datetime
    category: str  # Can be hour, date, type, station, etc.
    count: int
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "category": self.category,
            "count": self.count,
            "details": self.details
        }
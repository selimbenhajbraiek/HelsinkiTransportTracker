from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

db = SQLAlchemy()

# Vehicle mode/type enum
class VehicleMode(enum.Enum):
    BUS = "BUS"
    TRAM = "TRAM"
    TRAIN = "TRAIN"
    SUBWAY = "SUBWAY"
    FERRY = "FERRY"

# Vehicle position model
class Position(db.Model):
    __tablename__ = 'positions'
    
    id = Column(Integer, primary_key=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    
    # Relationships
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=True)
    station_id = Column(Integer, ForeignKey('stations.id'), nullable=True)

# Vehicle model
class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = Column(Integer, primary_key=True)
    vehicle_id = Column(String(50), unique=True, nullable=False)
    route_id = Column(String(50), nullable=True)
    trip_id = Column(String(50), nullable=True)
    mode = Column(Enum(VehicleMode), nullable=False)
    speed = Column(Float, nullable=True)
    heading = Column(Integer, nullable=True)
    vehicle_number = Column(String(50), nullable=True)
    operator_id = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.now)
    
    # Relationships
    position = relationship("Position", backref="vehicle", uselist=False, foreign_keys=[Position.vehicle_id])

# Station/stop model
class Station(db.Model):
    __tablename__ = 'stations'
    
    id = Column(Integer, primary_key=True)
    station_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=True)
    platform_code = Column(String(50), nullable=True)
    description = Column(String(255), nullable=True)
    zone_id = Column(String(50), nullable=True)
    
    # Relationships
    position = relationship("Position", backref="station", uselist=False, foreign_keys=[Position.station_id])
    routes = relationship("StationRoute", backref="station")

# Route pattern model
class RoutePattern(db.Model):
    __tablename__ = 'route_patterns'
    
    id = Column(Integer, primary_key=True)
    pattern_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=True)
    
    # Relationships
    route_id = Column(Integer, ForeignKey('routes.id'), nullable=False)
    stops = relationship("PatternStop", backref="pattern")

# Pattern-Stop association
class PatternStop(db.Model):
    __tablename__ = 'pattern_stops'
    
    id = Column(Integer, primary_key=True)
    pattern_id = Column(Integer, ForeignKey('route_patterns.id'), nullable=False)
    station_id = Column(Integer, ForeignKey('stations.id'), nullable=False)
    stop_sequence = Column(Integer, nullable=False)

# Station-Route association
class StationRoute(db.Model):
    __tablename__ = 'station_routes'
    
    id = Column(Integer, primary_key=True)
    station_id = Column(Integer, ForeignKey('stations.id'), nullable=False)
    route_id = Column(Integer, ForeignKey('routes.id'), nullable=False)

# Transport route model
class Route(db.Model):
    __tablename__ = 'routes'
    
    id = Column(Integer, primary_key=True)
    route_id = Column(String(50), unique=True, nullable=False)
    short_name = Column(String(50), nullable=False)
    long_name = Column(String(100), nullable=True)
    mode = Column(Enum(VehicleMode), nullable=False)
    operator_id = Column(String(50), nullable=True)
    color = Column(String(10), nullable=True)
    text_color = Column(String(10), nullable=True)
    
    # Relationships
    patterns = relationship("RoutePattern", backref="route")
    stations = relationship("StationRoute", backref="route")

# Transport statistics model for aggregated data
class TransportStats(db.Model):
    __tablename__ = 'transport_stats'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now)
    category = Column(String(50), nullable=False)  # 'hourly', 'daily', 'type', 'station'
    count = Column(Integer, nullable=False)
    details = Column(JSON, nullable=True)  # Store any additional structured data
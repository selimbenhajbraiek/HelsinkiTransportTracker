from flask import Blueprint, jsonify, request
from models import db, Vehicle, Station, Route, VehicleMode, TransportStats
from app.services.digitransit_service import DigitransitService
from app.services.data_services import DataService
from datetime import datetime, timedelta
import json

# Create blueprint
api = Blueprint('api', __name__)

# Services will be initialized lazily on demand
_digitransit_service = None
_data_service = None

def get_digitransit_service():
    global _digitransit_service
    if _digitransit_service is None:
        _digitransit_service = DigitransitService()
    return _digitransit_service

def get_data_service():
    global _data_service
    if _data_service is None:
        _data_service = DataService()
    return _data_service

@api.route('/vehicles', methods=['GET'])
def get_vehicles():
    """Get all currently active vehicles"""
    try:
        service = get_digitransit_service()
        vehicles = service.get_vehicles()
        return jsonify([v.to_dict() for v in vehicles])
    except Exception as e:
        return jsonify({"error": f"Error fetching vehicles: {str(e)}"}), 500

@api.route('/stations', methods=['GET'])
def get_stations():
    """Get all stations"""
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        service = get_digitransit_service()
        stations = service.get_stations(limit, offset)
        return jsonify([s.to_dict() for s in stations])
    except Exception as e:
        return jsonify({"error": f"Error fetching stations: {str(e)}"}), 500

@api.route('/station/<station_id>', methods=['GET'])
def get_station(station_id):
    """Get details of a specific station"""
    try:
        service = get_digitransit_service()
        station = service.get_station_by_id(station_id)
        if not station:
            return jsonify({"error": f"Station with ID {station_id} not found"}), 404
        return jsonify(station.to_dict())
    except Exception as e:
        return jsonify({"error": f"Error fetching station: {str(e)}"}), 500

@api.route('/stations/search', methods=['GET'])
def search_stations():
    """Search for stations by name"""
    try:
        query = request.args.get('query', '')
        if not query:
            return jsonify({"error": "Search query is required"}), 400
            
        service = get_digitransit_service()
        stations = service.search_stations(query)
        return jsonify([s.to_dict() for s in stations])
    except Exception as e:
        return jsonify({"error": f"Error searching stations: {str(e)}"}), 500

@api.route('/routes', methods=['GET'])
def get_routes():
    """Get all routes"""
    try:
        service = get_digitransit_service()
        routes = service.get_routes()
        return jsonify([r.to_dict() for r in routes])
    except Exception as e:
        return jsonify({"error": f"Error fetching routes: {str(e)}"}), 500

@api.route('/route/<route_id>', methods=['GET'])
def get_route(route_id):
    """Get details of a specific route"""
    try:
        service = get_digitransit_service()
        route = service.get_route_by_id(route_id)
        if not route:
            return jsonify({"error": f"Route with ID {route_id} not found"}), 404
        return jsonify(route.to_dict())
    except Exception as e:
        return jsonify({"error": f"Error fetching route: {str(e)}"}), 500

@api.route('/stats/hourly', methods=['GET'])
def get_hourly_stats():
    """Get hourly transport activity stats"""
    try:
        date_str = request.args.get('date')
        
        service = get_data_service()
        stats = service.get_hourly_stats(date_str)
        return jsonify([s.to_dict() for s in stats])
    except Exception as e:
        return jsonify({"error": f"Error fetching hourly stats: {str(e)}"}), 500

@api.route('/stats/daily', methods=['GET'])
def get_daily_stats():
    """Get daily transport activity stats"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        service = get_data_service()
        stats = service.get_daily_stats(start_date, end_date)
        return jsonify([s.to_dict() for s in stats])
    except Exception as e:
        return jsonify({"error": f"Error fetching daily stats: {str(e)}"}), 500

@api.route('/stats/by_type', methods=['GET'])
def get_stats_by_type():
    """Get transport activity stats by vehicle type"""
    try:
        service = get_data_service()
        stats = service.get_stats_by_type()
        return jsonify([s.to_dict() for s in stats])
    except Exception as e:
        return jsonify({"error": f"Error fetching stats by type: {str(e)}"}), 500

@api.route('/stats/by_station', methods=['GET'])
def get_stats_by_station():
    """Get transport activity stats by station"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        service = get_data_service()
        stats = service.get_stats_by_station(limit)
        return jsonify([s.to_dict() for s in stats])
    except Exception as e:
        return jsonify({"error": f"Error fetching stats by station: {str(e)}"}), 500
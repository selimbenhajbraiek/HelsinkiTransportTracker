from typing import List, Optional, Dict, Any
import logging
from app.api.graphql_client import GraphQLClient
from app.models.transport import Vehicle, Position, Station, Route, RoutePattern, VehicleMode

logger = logging.getLogger(__name__)

class DigitransitService:
    def __init__(self):
        """Initialize Digitransit Service with GraphQL client"""
        self.client = GraphQLClient()
        logger.info("Initialized Digitransit Service")

    def get_vehicles(self) -> List[Vehicle]:
        """Get all active vehicles"""
        query = """
        {
          vehicles {
            id
            trip {
              route {
                id
                shortName
                longName
                mode
              }
              id
            }
            position {
              latitude
              longitude
            }
            speed
            heading
            vehicleNumber
            operatorId
          }
        }
        """
        
        try:
            result = self.client.execute_query(query)
            vehicles_data = result.get("vehicles", [])
            
            vehicles = []
            for vehicle_data in vehicles_data:
                try:
                    # Get route info if available
                    route_id = None
                    trip_id = None
                    mode = VehicleMode.BUS  # Default mode
                    
                    if vehicle_data.get("trip") and vehicle_data["trip"].get("route"):
                        route_data = vehicle_data["trip"]["route"]
                        route_id = route_data.get("id")
                        
                        # Map mode string to enum
                        mode_str = route_data.get("mode", "BUS").upper()
                        try:
                            mode = VehicleMode(mode_str)
                        except ValueError:
                            logger.warning(f"Unknown vehicle mode: {mode_str}, defaulting to BUS")
                            mode = VehicleMode.BUS
                    
                        trip_id = vehicle_data["trip"].get("id")
                    
                    # Create position
                    position = None
                    if vehicle_data.get("position"):
                        position = Position(
                            lat=vehicle_data["position"].get("latitude"),
                            lng=vehicle_data["position"].get("longitude")
                        )
                    else:
                        # Skip vehicles without position
                        continue
                    
                    # Create vehicle
                    vehicle = Vehicle(
                        id=vehicle_data.get("id"),
                        route_id=route_id,
                        trip_id=trip_id,
                        mode=mode,
                        position=position,
                        speed=vehicle_data.get("speed"),
                        heading=vehicle_data.get("heading"),
                        vehicle_number=vehicle_data.get("vehicleNumber"),
                        operator_id=vehicle_data.get("operatorId")
                    )
                    
                    vehicles.append(vehicle)
                except Exception as e:
                    logger.error(f"Error processing vehicle data: {str(e)}")
                    continue
            
            return vehicles
        except Exception as e:
            logger.error(f"Error fetching vehicles: {str(e)}")
            raise
    
    def get_stations(self, limit: int = 100, offset: int = 0) -> List[Station]:
        """Get stations/stops"""
        query = """
        query Stops($limit: Int, $offset: Int) {
          stops(limit: $limit, skip: $offset) {
            id
            name
            code
            lat
            lon
            routes {
              id
            }
            platformCode
            desc
            zoneId
          }
        }
        """
        
        variables = {
            "limit": limit,
            "offset": offset
        }
        
        try:
            result = self.client.execute_query(query, variables)
            stops_data = result.get("stops", [])
            
            stations = []
            for stop_data in stops_data:
                try:
                    # Extract route IDs
                    routes = []
                    if stop_data.get("routes"):
                        routes = [r.get("id") for r in stop_data["routes"] if r.get("id")]
                    
                    # Create position
                    position = Position(
                        lat=stop_data.get("lat", 0.0),
                        lng=stop_data.get("lon", 0.0)
                    )
                    
                    # Create station
                    station = Station(
                        id=stop_data.get("id"),
                        name=stop_data.get("name", "Unknown"),
                        code=stop_data.get("code"),
                        position=position,
                        routes=routes,
                        platform_code=stop_data.get("platformCode"),
                        description=stop_data.get("desc"),
                        zone_id=stop_data.get("zoneId")
                    )
                    
                    stations.append(station)
                except Exception as e:
                    logger.error(f"Error processing station data: {str(e)}")
                    continue
            
            return stations
        except Exception as e:
            logger.error(f"Error fetching stations: {str(e)}")
            raise
    
    def get_station_by_id(self, station_id: str) -> Optional[Station]:
        """Get a specific station by ID"""
        query = """
        query Stop($id: String!) {
          stop(id: $id) {
            id
            name
            code
            lat
            lon
            routes {
              id
            }
            platformCode
            desc
            zoneId
          }
        }
        """
        
        variables = {
            "id": station_id
        }
        
        try:
            result = self.client.execute_query(query, variables)
            stop_data = result.get("stop")
            
            if not stop_data:
                return None
            
            # Extract route IDs
            routes = []
            if stop_data.get("routes"):
                routes = [r.get("id") for r in stop_data["routes"] if r.get("id")]
            
            # Create position
            position = Position(
                lat=stop_data.get("lat", 0.0),
                lng=stop_data.get("lon", 0.0)
            )
            
            # Create station
            station = Station(
                id=stop_data.get("id"),
                name=stop_data.get("name", "Unknown"),
                code=stop_data.get("code"),
                position=position,
                routes=routes,
                platform_code=stop_data.get("platformCode"),
                description=stop_data.get("desc"),
                zone_id=stop_data.get("zoneId")
            )
            
            return station
        except Exception as e:
            logger.error(f"Error fetching station by ID: {str(e)}")
            raise
    
    def search_stations(self, query_text: str) -> List[Station]:
        """Search for stations by name"""
        query = """
        query StopsByName($name: String!) {
          stops(name: $name) {
            id
            name
            code
            lat
            lon
            routes {
              id
            }
            platformCode
            desc
            zoneId
          }
        }
        """
        
        variables = {
            "name": query_text
        }
        
        try:
            result = self.client.execute_query(query, variables)
            stops_data = result.get("stops", [])
            
            stations = []
            for stop_data in stops_data:
                try:
                    # Extract route IDs
                    routes = []
                    if stop_data.get("routes"):
                        routes = [r.get("id") for r in stop_data["routes"] if r.get("id")]
                    
                    # Create position
                    position = Position(
                        lat=stop_data.get("lat", 0.0),
                        lng=stop_data.get("lon", 0.0)
                    )
                    
                    # Create station
                    station = Station(
                        id=stop_data.get("id"),
                        name=stop_data.get("name", "Unknown"),
                        code=stop_data.get("code"),
                        position=position,
                        routes=routes,
                        platform_code=stop_data.get("platformCode"),
                        description=stop_data.get("desc"),
                        zone_id=stop_data.get("zoneId")
                    )
                    
                    stations.append(station)
                except Exception as e:
                    logger.error(f"Error processing station data: {str(e)}")
                    continue
            
            return stations
        except Exception as e:
            logger.error(f"Error searching for stations: {str(e)}")
            raise
    
    def get_routes(self) -> List[Route]:
        """Get all routes"""
        query = """
        {
          routes {
            id
            shortName
            longName
            mode
            operatorId
            patterns {
              id
              name
              stops {
                id
              }
            }
            color
            textColor
          }
        }
        """
        
        try:
            result = self.client.execute_query(query)
            routes_data = result.get("routes", [])
            
            routes = []
            for route_data in routes_data:
                try:
                    # Map mode string to enum
                    mode_str = route_data.get("mode", "BUS").upper()
                    try:
                        mode = VehicleMode(mode_str)
                    except ValueError:
                        logger.warning(f"Unknown vehicle mode: {mode_str}, defaulting to BUS")
                        mode = VehicleMode.BUS
                    
                    # Process patterns
                    patterns = []
                    if route_data.get("patterns"):
                        for pattern_data in route_data["patterns"]:
                            stops = []
                            if pattern_data.get("stops"):
                                stops = [s.get("id") for s in pattern_data["stops"] if s.get("id")]
                            
                            pattern = RoutePattern(
                                id=pattern_data.get("id"),
                                name=pattern_data.get("name"),
                                stops=stops
                            )
                            
                            patterns.append(pattern)
                    
                    # Create route
                    route = Route(
                        id=route_data.get("id"),
                        short_name=route_data.get("shortName", ""),
                        long_name=route_data.get("longName"),
                        mode=mode,
                        operator_id=route_data.get("operatorId"),
                        patterns=patterns,
                        color=route_data.get("color"),
                        text_color=route_data.get("textColor")
                    )
                    
                    routes.append(route)
                except Exception as e:
                    logger.error(f"Error processing route data: {str(e)}")
                    continue
            
            return routes
        except Exception as e:
            logger.error(f"Error fetching routes: {str(e)}")
            raise
    
    def get_route_by_id(self, route_id: str) -> Optional[Route]:
        """Get a specific route by ID"""
        query = """
        query Route($id: String!) {
          route(id: $id) {
            id
            shortName
            longName
            mode
            operatorId
            patterns {
              id
              name
              stops {
                id
              }
            }
            color
            textColor
          }
        }
        """
        
        variables = {
            "id": route_id
        }
        
        try:
            result = self.client.execute_query(query, variables)
            route_data = result.get("route")
            
            if not route_data:
                return None
            
            # Map mode string to enum
            mode_str = route_data.get("mode", "BUS").upper()
            try:
                mode = VehicleMode(mode_str)
            except ValueError:
                logger.warning(f"Unknown vehicle mode: {mode_str}, defaulting to BUS")
                mode = VehicleMode.BUS
            
            # Process patterns
            patterns = []
            if route_data.get("patterns"):
                for pattern_data in route_data["patterns"]:
                    stops = []
                    if pattern_data.get("stops"):
                        stops = [s.get("id") for s in pattern_data["stops"] if s.get("id")]
                    
                    pattern = RoutePattern(
                        id=pattern_data.get("id"),
                        name=pattern_data.get("name"),
                        stops=stops
                    )
                    
                    patterns.append(pattern)
            
            # Create route
            route = Route(
                id=route_data.get("id"),
                short_name=route_data.get("shortName", ""),
                long_name=route_data.get("longName"),
                mode=mode,
                operator_id=route_data.get("operatorId"),
                patterns=patterns,
                color=route_data.get("color"),
                text_color=route_data.get("textColor")
            )
            
            return route
        except Exception as e:
            logger.error(f"Error fetching route by ID: {str(e)}")
            raise
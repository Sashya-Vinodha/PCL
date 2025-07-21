import requests
import time
from typing import Dict, List, Optional, Tuple
import logging
from config import (
    MAPBOX_ACCESS_TOKEN, 
    MAPBOX_BASE_URL, 
    CITY_COORDINATES, 
    REQUEST_TIMEOUT, 
    MAX_RETRIES, 
    ERROR_MESSAGES
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_route_data(start: str, end: str) -> Dict:
    """
    Get route data between two cities using Mapbox Directions API.
    
    Args:
        start (str): Starting city name
        end (str): Destination city name
    
    Returns:
        Dict: Route information containing distance, time, and coordinates
              or error message if request fails
    
    Example:
        >>> get_route_data("chennai", "madurai")
        {
            "distance": 458.2,
            "time": 412,
            "coordinates": [[80.2707, 13.0827], [78.1198, 9.9252]]
        }
    """
    try:
        # Normalize city names to lowercase
        start_city = start.lower().strip()
        end_city = end.lower().strip()
        
        # Validate cities exist in our database
        if start_city not in CITY_COORDINATES:
            logger.error(f"Start city '{start}' not found in database")
            return {"error": f"{ERROR_MESSAGES['invalid_city']}: {start}"}
        
        if end_city not in CITY_COORDINATES:
            logger.error(f"End city '{end}' not found in database")
            return {"error": f"{ERROR_MESSAGES['invalid_city']}: {end}"}
        
        # Get coordinates for start and end cities
        start_coords = CITY_COORDINATES[start_city]
        end_coords = CITY_COORDINATES[end_city]
        
        logger.info(f"Getting route from {start} {start_coords} to {end} {end_coords}")
        
        # Make API call to Mapbox
        route_data = _call_mapbox_api(start_coords, end_coords)
        
        if "error" in route_data:
            return route_data
        
        # Format and return the response
        return {
            "distance": route_data["distance"],
            "time": route_data["time"],
            "coordinates": route_data["coordinates"]
        }
        
    except Exception as e:
        logger.error(f"Unexpected error in get_route_data: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}


def _call_mapbox_api(start_coords: List[float], end_coords: List[float]) -> Dict:
    """
    Make API call to Mapbox Directions API with retry logic.
    
    Args:
        start_coords (List[float]): [longitude, latitude] of start point
        end_coords (List[float]): [longitude, latitude] of end point
    
    Returns:
        Dict: Processed route data or error message
    """
    # Construct the API URL
    coordinates = f"{start_coords[0]},{start_coords[1]};{end_coords[0]},{end_coords[1]}"
    url = f"{MAPBOX_BASE_URL}/{coordinates}"
    
    params = {
        "access_token": MAPBOX_ACCESS_TOKEN,
        "geometries": "geojson",
        "overview": "simplified",
        "steps": "false"
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Making API call to Mapbox (attempt {attempt + 1}/{MAX_RETRIES})")
            
            response = requests.get(
                url, 
                params=params, 
                timeout=REQUEST_TIMEOUT
            )
            
            # Check if request was successful
            if response.status_code == 200:
                return _process_mapbox_response(response.json())
            elif response.status_code == 401:
                logger.error("Invalid Mapbox access token")
                return {"error": "Invalid API access token"}
            elif response.status_code == 422:
                logger.error("Invalid coordinates or route not possible")
                return {"error": "Route not possible between these locations"}
            else:
                logger.error(f"Mapbox API returned status {response.status_code}: {response.text}")
                if attempt == MAX_RETRIES - 1:
                    return {"error": f"{ERROR_MESSAGES['api_error']}: HTTP {response.status_code}"}
        
        except requests.exceptions.Timeout:
            logger.warning(f"Request timeout on attempt {attempt + 1}")
            if attempt == MAX_RETRIES - 1:
                return {"error": ERROR_MESSAGES['timeout_error']}
        
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection error on attempt {attempt + 1}")
            if attempt == MAX_RETRIES - 1:
                return {"error": ERROR_MESSAGES['network_error']}
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error on attempt {attempt + 1}: {str(e)}")
            if attempt == MAX_RETRIES - 1:
                return {"error": f"{ERROR_MESSAGES['api_error']}: {str(e)}"}
        
        # Wait before retrying
        if attempt < MAX_RETRIES - 1:
            time.sleep(1)
    
    return {"error": ERROR_MESSAGES['api_error']}


def _process_mapbox_response(response_data: Dict) -> Dict:
    """
    Process the raw Mapbox API response and extract relevant information.
    
    Args:
        response_data (Dict): Raw response from Mapbox API
    
    Returns:
        Dict: Processed route data
    """
    try:
        if not response_data.get("routes"):
            logger.error("No routes found in Mapbox response")
            return {"error": "No routes found"}
        
        route = response_data["routes"][0]
        
        # Extract distance (convert from meters to kilometers)
        distance_km = round(route["distance"] / 1000, 1)
        
        # Extract duration (convert from seconds to minutes)
        duration_minutes = round(route["duration"] / 60)
        
        # Extract coordinates from geometry
        coordinates = route["geometry"]["coordinates"]
        
        # Simplify coordinates if there are too many points (keep every 10th point)
        if len(coordinates) > 100:
            step = len(coordinates) // 50
            coordinates = coordinates[::step]
        
        logger.info(f"Route processed: {distance_km}km, {duration_minutes}min, {len(coordinates)} points")
        
        return {
            "distance": distance_km,
            "time": duration_minutes,
            "coordinates": coordinates
        }
        
    except KeyError as e:
        logger.error(f"Missing key in Mapbox response: {str(e)}")
        return {"error": f"{ERROR_MESSAGES['invalid_response']}: missing {str(e)}"}
    
    except Exception as e:
        logger.error(f"Error processing Mapbox response: {str(e)}")
        return {"error": f"{ERROR_MESSAGES['invalid_response']}: {str(e)}"}


def get_available_cities() -> List[str]:
    """
    Get list of available cities for route planning.
    
    Returns:
        List[str]: List of available city names
    """
    return list(CITY_COORDINATES.keys())


def get_city_coordinates(city: str) -> Optional[List[float]]:
    """
    Get coordinates for a specific city.
    
    Args:
        city (str): City name
    
    Returns:
        Optional[List[float]]: [longitude, latitude] or None if city not found
    """
    return CITY_COORDINATES.get(city.lower().strip())


def validate_cities(start: str, end: str) -> Tuple[bool, str]:
    """
    Validate that both start and end cities exist in our database.
    
    Args:
        start (str): Starting city name
        end (str): Destination city name
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    start_city = start.lower().strip()
    end_city = end.lower().strip()
    
    if start_city not in CITY_COORDINATES:
        return False, f"Start city '{start}' not found. Available cities: {', '.join(get_available_cities())}"
    
    if end_city not in CITY_COORDINATES:
        return False, f"End city '{end}' not found. Available cities: {', '.join(get_available_cities())}"
    
    if start_city == end_city:
        return False, "Start and end cities cannot be the same"
    
    return True, ""


# Example usage and testing
if __name__ == "__main__":
    # Test the API with some example cities
    print("Testing Route API...")
    print(f"Available cities: {get_available_cities()}")
    
    # Test valid route
    result = get_route_data("chennai", "madurai")
    print(f"\nRoute from Chennai to Madurai: {result}")
    
    # Test invalid city
    result = get_route_data("chennai", "invalid_city")
    print(f"\nRoute with invalid city: {result}")
    
    # Test city validation
    is_valid, error = validate_cities("chennai", "madurai")
    print(f"\nValidation result: {is_valid}, error: {error}")
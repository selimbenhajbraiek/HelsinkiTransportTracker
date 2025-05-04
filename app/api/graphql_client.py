import aiohttp
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class GraphQLClient:
    def __init__(self):
        """Initialize GraphQL client for the Digitransit API"""
        self.api_url = settings.DIGITRANSIT_API_URL
        self.api_key = settings.DIGITRANSIT_API_KEY
        self.headers = {
            "Content-Type": "application/json",
            "digitransit-subscription-key": self.api_key
        }
    
    async def execute_query(self, query_str, variables=None):
        """Execute a GraphQL query"""
        payload = {
            "query": query_str
        }
        
        if variables:
            payload["variables"] = variables
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=self.api_url,
                    headers=self.headers,
                    data=json.dumps(payload)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    if "errors" in data:
                        logger.error(f"GraphQL query error: {data['errors']}")
                        raise Exception(f"GraphQL error: {data['errors'][0]['message']}")
                        
                    return data.get("data")
                    
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error: {str(e)}")
            raise Exception(f"HTTP error: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error executing GraphQL query: {str(e)}")
            raise Exception(f"Error executing GraphQL query: {str(e)}")
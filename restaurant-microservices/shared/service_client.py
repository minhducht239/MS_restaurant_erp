"""
Service Client for inter-service communication
"""
import requests
import os
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ServiceClient:
    """
    HTTP client for communication between microservices.
    Handles authentication, retries, and error handling.
    """
    
    # Service URL mapping
    SERVICES = {
        'auth': os.environ.get('AUTH_SERVICE_URL', 'http://auth-service:8000'),
        'menu': os.environ.get('MENU_SERVICE_URL', 'http://menu-service:8000'),
        'billing': os.environ.get('BILLING_SERVICE_URL', 'http://billing-service:8000'),
        'customer': os.environ.get('CUSTOMER_SERVICE_URL', 'http://customer-service:8000'),
        'table': os.environ.get('TABLE_SERVICE_URL', 'http://table-service:8000'),
        'staff': os.environ.get('STAFF_SERVICE_URL', 'http://staff-service:8000'),
        'reservation': os.environ.get('RESERVATION_SERVICE_URL', 'http://reservation-service:8000'),
        'dashboard': os.environ.get('DASHBOARD_SERVICE_URL', 'http://dashboard-service:8000'),
    }
    
    def __init__(self, service_name: str, timeout: int = 30):
        self.service_name = service_name
        self.base_url = self.SERVICES.get(service_name)
        self.timeout = timeout
        self.service_key = os.environ.get('SERVICE_SECRET_KEY', 'default-service-key')
        
        if not self.base_url:
            raise ValueError(f"Unknown service: {service_name}")
    
    def _get_headers(self, auth_token: Optional[str] = None) -> Dict[str, str]:
        """Build request headers"""
        headers = {
            'Content-Type': 'application/json',
            'X-Service-Key': self.service_key,
        }
        
        if auth_token:
            headers['Authorization'] = f'Bearer {auth_token}'
            
        return headers
    
    def get(self, endpoint: str, params: Optional[Dict] = None, 
            auth_token: Optional[str] = None) -> Dict[str, Any]:
        """Make GET request to service"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.get(
                url,
                params=params,
                headers=self._get_headers(auth_token),
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling {self.service_name}: {str(e)}")
            raise ServiceException(f"Service {self.service_name} unavailable: {str(e)}")
    
    def post(self, endpoint: str, data: Optional[Dict] = None,
             auth_token: Optional[str] = None) -> Dict[str, Any]:
        """Make POST request to service"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.post(
                url,
                json=data,
                headers=self._get_headers(auth_token),
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling {self.service_name}: {str(e)}")
            raise ServiceException(f"Service {self.service_name} unavailable: {str(e)}")
    
    def put(self, endpoint: str, data: Optional[Dict] = None,
            auth_token: Optional[str] = None) -> Dict[str, Any]:
        """Make PUT request to service"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.put(
                url,
                json=data,
                headers=self._get_headers(auth_token),
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling {self.service_name}: {str(e)}")
            raise ServiceException(f"Service {self.service_name} unavailable: {str(e)}")
    
    def delete(self, endpoint: str, auth_token: Optional[str] = None) -> bool:
        """Make DELETE request to service"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.delete(
                url,
                headers=self._get_headers(auth_token),
                timeout=self.timeout
            )
            response.raise_for_status()
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling {self.service_name}: {str(e)}")
            raise ServiceException(f"Service {self.service_name} unavailable: {str(e)}")


class ServiceException(Exception):
    """Exception for service communication errors"""
    pass

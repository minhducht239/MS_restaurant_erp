"""
Custom exception handler for REST framework
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from .exceptions import ServiceException
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Customize the response data
        custom_response_data = {
            'success': False,
            'error': {
                'code': response.status_code,
                'message': str(exc),
                'detail': response.data
            }
        }
        response.data = custom_response_data
        return response
    
    # Handle custom ServiceException
    if isinstance(exc, ServiceException):
        logger.error(f"ServiceException: {exc.message}")
        return Response({
            'success': False,
            'error': {
                'code': exc.status_code,
                'message': exc.message
            }
        }, status=exc.status_code)
    
    # Handle unexpected exceptions
    logger.exception(f"Unexpected error: {str(exc)}")
    return Response({
        'success': False,
        'error': {
            'code': 500,
            'message': 'Internal server error',
            'detail': str(exc) if context.get('request') and context['request'].user.is_staff else None
        }
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework.response import Response
from drf_spectacular.utils import OpenApiExample

def api_response(success, message, data=None, status_code=200, error_details=None):
    """
    A utility function to return API responses in a consistent format.
    success: Whether the request was successful or not.
    message: A message to be displayed in the response.
    data: Any data to be returned (optional).
    status_code: HTTP status code (default is 200).
    error_details: Detailed error information (optional, for error responses).
    """
    if success:
        return Response({
            'success': success,
            'message': message,
            'data': data,
            'status_code': status_code
        }, status=status_code)
    else:
        return Response({
            'success': success,
            'message': message,
            'data': error_details or {},  # Provide error details if available
            'status_code': status_code
        }, status=status_code)

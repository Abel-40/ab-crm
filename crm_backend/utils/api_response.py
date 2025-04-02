from rest_framework.response import Response

def api_response(message, status_code, success, data=None, errors=None):
    response = {
        "data": data,
        "message": message,
        "statusCode": status_code,
        "success": success,
        
    }
    if errors:
        response["errors"] = errors  # Include errors if available
    return Response(response, status=status_code)

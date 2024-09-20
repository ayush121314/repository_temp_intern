# logging_middleware.py
import logging

# Configure logging settings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class RequestLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log the request method and URL
        logging.info(f"Received request: {request.method} {request.get_full_path()}")

        # Process the request
        response = self.get_response(request)

        return response

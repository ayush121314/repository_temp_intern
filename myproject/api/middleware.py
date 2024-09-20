from django.http import HttpResponseForbidden

class RestrictAccessMiddleware:
    """
    Middleware to restrict access based on certain conditions.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Define your condition for restricting access
        # Example: Restrict access if user is not authenticated
      
        
        # Restrict access to /admin/ for non-staff users
        # if request.path.startswith('/admin/'):
        #     if not request.user.is_staff:
        #         return HttpResponseForbidden("Access restricted. Admins only.")

        # Allow the request to proceed if the condition is met
        return self.get_response(request)

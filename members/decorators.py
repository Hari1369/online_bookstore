# from functools import wraps

# from django.core.exceptions import PermissionDenied
# from django.http import JsonResponse
# from django.shortcuts import redirect


# def _admin_only(api):
#     def decorator(view):
#         @wraps(view)
#         def wrapper(request, *args, **kwargs):
#             user = request.user

#             # Not logged in
#             if not user.is_authenticated:
#                 if api:
#                     return JsonResponse({"error": "Please log in."}, status=401)
#                 return redirect("login")

#             # Logged in but not an admin (customer or normal staff)
#             if not user.is_superuser:
#                 if api:
#                     return JsonResponse({"error": "Admin access required."}, status=403)
#                 raise PermissionDenied  # shows the 403 Forbidden page

#             return view(request, *args, **kwargs)
#         return wrapper
#     return decorator


# # For normal pages: anonymous -> login page, non-admin -> 403 page
# admin_required = _admin_only(api=False)

# # For fetch()/JSON endpoints: returns 401 / 403 JSON instead of redirecting
# admin_api_required = _admin_only(api=True)


from functools import wraps
 
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
 
 
def _login_only(api):
    """Any logged-in user (customer, staff or admin)."""
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if api:
                    return JsonResponse(
                        {"error": "Please log in.", "login_url": reverse("login")},
                        status=401,
                    )
                return redirect("login")
            return view(request, *args, **kwargs)
        return wrapper
    return decorator
 
 
def _admin_only(api):
    """Superusers only."""
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            user = request.user
 
            # Not logged in
            if not user.is_authenticated:
                if api:
                    return JsonResponse(
                        {"error": "Please log in.", "login_url": reverse("login")},
                        status=401,
                    )
                return redirect("login")
 
            # Logged in but not an admin (customer or normal staff)
            if not user.is_superuser:
                if api:
                    return JsonResponse({"error": "Admin access required."}, status=403)
                raise PermissionDenied  # shows the 403 Forbidden page
 
            return view(request, *args, **kwargs)
        return wrapper
    return decorator
 
 
# Normal pages: anonymous -> login page
login_required_page = _login_only(api=False)
# fetch()/JSON endpoints: anonymous -> 401 JSON
login_required_api = _login_only(api=True)
 
# Admin-only versions (403 for customers / normal staff)
admin_required = _admin_only(api=False)
admin_api_required = _admin_only(api=True)
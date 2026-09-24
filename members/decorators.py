"""
Access-control helpers for the members app.

"Admin" here means a Django *superuser* (is_superuser=True).
Normal customers and normal staff (is_staff=True only) are NOT admins.
"""
from functools import wraps

from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import redirect


def _admin_only(api):
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            user = request.user

            # Not logged in
            if not user.is_authenticated:
                if api:
                    return JsonResponse({"error": "Please log in."}, status=401)
                return redirect("login")

            # Logged in but not an admin (customer or normal staff)
            if not user.is_superuser:
                if api:
                    return JsonResponse({"error": "Admin access required."}, status=403)
                raise PermissionDenied  # shows the 403 Forbidden page

            return view(request, *args, **kwargs)
        return wrapper
    return decorator


# For normal pages: anonymous -> login page, non-admin -> 403 page
admin_required = _admin_only(api=False)

# For fetch()/JSON endpoints: returns 401 / 403 JSON instead of redirecting
admin_api_required = _admin_only(api=True)

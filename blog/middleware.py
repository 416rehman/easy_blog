from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy


class RestrictInactiveUsersMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and (not request.path.startswith('/activate') and not request.path.startswith('/auth/logout')):
            if not request.user.is_email_verified:
                return redirect(reverse('inactive_view'))
        response = self.get_response(request)
        return response

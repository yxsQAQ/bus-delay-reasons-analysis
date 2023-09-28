from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse, redirect


class AuthMiddleware(MiddlewareMixin):
    """Middleware"""

    def process_request(self, request):

        # 0. Exclude pages that can be accessed without login
        if request.path_info in ['/login/', '/img/code/']:
            return

        # 1. Read the session information of the current visiting user. If it exists, it means the user is already logged in, so continue the request.
        info_dict = request.session.get('info')
        if info_dict:
            return

        # 2. If not logged in, redirect to the login page
        return redirect('/login/')

        # If the method does not return a value, the request continues.
        # If the method returns an HttpResponse, render, or redirect, further execution is halted.

    def process_response(self, request, response):

        return response




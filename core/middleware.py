from django.conf import settings


class SiteURLMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Store the current site URL in the request
        request.site_url = f"{request.scheme}://{request.get_host()}"

        # Continue processing the request
        response = self.get_response(request)
        return response

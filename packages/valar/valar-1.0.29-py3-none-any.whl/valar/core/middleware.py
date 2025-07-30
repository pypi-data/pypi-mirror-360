from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin
from response import ValarResponse


class Middleware(MiddlewareMixin):
    @staticmethod
    def process_response(request: HttpRequest, response: ValarResponse):
        headers = response.headers
        if type(response)==ValarResponse:
            message, code = response.message, response.code
            headers['valar_message'] = message
            headers['valar_code'] = code

        keys = ['client','auth','uid']
        for key in keys:
            value = request.headers.get(key)
            if value:
                headers[key] = value
        return response
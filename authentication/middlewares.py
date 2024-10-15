import jwt
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class CheckTokenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        token = request.headers.get('Authorization')
        exclude_target_url = [reverse('login'), reverse('register')]
        if request.path.startswith('/api/v1/') and request.path not in exclude_target_url:
            if token is None or len(token.split()) != 2 or token.split()[0] != "Bearer":
                return JsonResponse({'result': '', 'error': 'Unauthorized'}, status=401)
            try:
                jwt.decode(token.split()[1], settings.SECRET_KEY, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return JsonResponse({'result': '', 'error': 'Token has expired'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'result': '', 'error': 'Invalid token'}, status=401)
            return

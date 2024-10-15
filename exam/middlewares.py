import jwt
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class RoleBasedMiddleware(MiddlewareMixin):
    def process_request(self, request):
        token = request.headers.get('Authorization')
        target_url = [reverse('create_test'), reverse('create_question'), reverse('create_question')]

        if request.method != 'GET' and request.path.startswith('/api/v1/') and request.path in target_url:
            payload = jwt.decode(token.split()[1], settings.SECRET_KEY, algorithms=['HS256'])
            role = payload.get('role')
            if role != 2:
                return JsonResponse({'result': '', 'error': 'Permission denied'}, status=403)

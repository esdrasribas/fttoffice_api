from django.http import HttpResponseForbidden

class BlockIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        blocked_ips = ['']  # Adicione os IPs que deseja bloquear aqui

        ip = request.META.get('REMOTE_ADDR')
        if ip in blocked_ips:
            return HttpResponseForbidden('Acesso negado.')

        response = self.get_response(request)
        return response

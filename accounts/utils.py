
def get_client_ip(group, request):
    django_request = getattr(request, '_request', request)
    return django_request.META.get('REMOTE_ADDR', '')
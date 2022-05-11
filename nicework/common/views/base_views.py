from django.shortcuts import render, redirect

import logging
logger = logging.getLogger(__name__)


# Create your views here.
def index(request):
    user_ip = get_client_ip(request)
    logger.info("접속 PC 외부 IP : " + str(user_ip))
    context = {}
    return render(request, 'common/index.html', context)


def page_not_found(request, exception):
    return render(request, 'common/404.html', {})

def server_error(request, *args, **argv):
    return render(request, 'common/500.html', {})

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
from django.shortcuts import render, redirect


# Create your views here.
def index(request):
    context = {}
    return render(request, 'common/index.html', context)


def page_not_found(request, exception):
    return render(request, 'common/404.html', {})

def server_error(request, *args, **argv):
    return render(request, 'common/500.html', {})
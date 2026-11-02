from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('prijava')
        if not request.user.je_admin:
            messages.error(request, "Dostop zavrnjen: Ta stran je namenjena le administratorjem.")
            return redirect('domov')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def ucitelj_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('prijava')
        if not (request.user.je_ucitelj or request.user.je_admin):
            messages.error(request, "Dostop zavrnjen: Ta stran je namenjena le učiteljem.")
            return redirect('domov')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def ucenec_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('prijava')
        if not (request.user.je_ucenec or request.user.je_admin):
            messages.error(request, "Dostop zavrnjen: Ta stran je namenjena le učencem.")
            return redirect('domov')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


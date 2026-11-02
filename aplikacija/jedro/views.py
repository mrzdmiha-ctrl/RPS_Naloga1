from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PrijavaForm, RegistracijaUcencaForm, UrediProfilForm
from .models import Uporabnik

def domov_pogled(request):
    """Glavna vstopna točka – preusmeri na portal glede na vlogo uporabnika."""
    if request.user.is_authenticated:
        if request.user.je_admin:
            return redirect('admin_nadzorna_plosca')
        elif request.user.je_ucitelj:
            return redirect('ucitelj_nadzorna_plosca')
        elif request.user.je_ucenec:
            return redirect('ucenec_nadzorna_plosca')
    return render(request, 'domov.html')

def prijava_pogled(request):
    """Prijava uporabnika v sistem."""
    if request.user.is_authenticated:
        return redirect('domov')

    if request.method == 'POST':
        form = PrijavaForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Dobrodošli, {user.polno_ime}!")
            return redirect('domov')
        else:
            messages.error(request, "Napačno uporabniško ime ali geslo.")
    else:
        form = PrijavaForm()

    return render(request, 'prijava.html', {'form': form})

def odjava_pogled(request):
    """Odjava uporabnika."""
    logout(request)
    messages.info(request, "Uspešno ste se odjavili iz sistema.")
    return redirect('prijava')

def registracija_pogled(request):
    """Registracija novega učenca."""
    if request.user.is_authenticated:
        return redirect('domov')

    if request.method == 'POST':
        form = RegistracijaUcencaForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Registracija uspešna! Dobrodošli v e-učilnici, {user.polno_ime}.")
            return redirect('ucenec_nadzorna_plosca')
        else:
            messages.error(request, "Prosimo, popravite napake v obrazcu.")
    else:
        form = RegistracijaUcencaForm()

    return render(request, 'registracija.html', {'form': form})

@login_required
def profil_pogled(request):
    """Urejanje lastnega profila uporabnika."""
    if request.method == 'POST':
        form = UrediProfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Vaš profil je bil uspešno posodobljen.")
            return redirect('profil')
        else:
            messages.error(request, "Pri shranjevanju profila je prišlo do napake.")
    else:
        form = UrediProfilForm(instance=request.user)

    return render(request, 'profil.html', {'form': form})


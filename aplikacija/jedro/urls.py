from django.urls import path
from . import views

urlpatterns = [
    path('', views.domov_pogled, name='domov'),
    path('prijava/', views.prijava_pogled, name='prijava'),
    path('odjava/', views.odjava_pogled, name='odjava'),
    path('registracija/', views.registracija_pogled, name='registracija'),
    path('profil/', views.profil_pogled, name='profil'),
]


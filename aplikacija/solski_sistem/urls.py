from django.urls import path
from . import views

urlpatterns = [
    # Administrator
    path('admin-portal/', views.admin_nadzorna_plosca, name='admin_nadzorna_plosca'),
    path('admin-portal/predmeti/', views.admin_predmeti_seznam, name='admin_predmeti_seznam'),
    path('admin-portal/predmeti/dodaj/', views.admin_predmet_ustvari, name='admin_predmet_ustvari'),
    path('admin-portal/predmeti/<int:pk>/uredi/', views.admin_predmet_uredi, name='admin_predmet_uredi'),
    path('admin-portal/predmeti/<int:pk>/izbrisi/', views.admin_predmet_izbrisi, name='admin_predmet_izbrisi'),
    
    path('admin-portal/ucitelji/', views.admin_ucitelji_seznam, name='admin_ucitelji_seznam'),
    path('admin-portal/ucitelji/dodaj/', views.admin_ucitelj_ustvari, name='admin_ucitelj_ustvari'),
    path('admin-portal/ucitelji/<int:pk>/uredi/', views.admin_ucitelj_uredi, name='admin_ucitelj_uredi'),
    path('admin-portal/ucitelji/<int:pk>/izbrisi/', views.admin_ucitelj_izbrisi, name='admin_ucitelj_izbrisi'),

    path('admin-portal/ucenci/', views.admin_ucenci_seznam, name='admin_ucenci_seznam'),
    path('admin-portal/ucenci/dodaj/', views.admin_ucenec_ustvari, name='admin_ucenec_ustvari'),
    path('admin-portal/ucenci/<int:pk>/uredi/', views.admin_ucenec_uredi, name='admin_ucenec_uredi'),
    path('admin-portal/ucenci/<int:pk>/izbrisi/', views.admin_ucenec_izbrisi, name='admin_ucenec_izbrisi'),

    # Učitelj
    path('ucitelj/', views.ucitelj_nadzorna_plosca, name='ucitelj_nadzorna_plosca'),
    path('ucitelj/predmet/<int:pk>/', views.ucitelj_predmet_detajli, name='ucitelj_predmet_detajli'),
    path('ucitelj/predmet/<int:predmet_id>/gradivo/dodaj/', views.ucitelj_gradivo_dodaj, name='ucitelj_gradivo_dodaj'),
    path('ucitelj/gradivo/<int:pk>/izbrisi/', views.ucitelj_gradivo_izbrisi, name='ucitelj_gradivo_izbrisi'),
    path('ucitelj/predmet/<int:predmet_id>/naloga/dodaj/', views.ucitelj_naloga_dodaj, name='ucitelj_naloga_dodaj'),
    path('ucitelj/naloga/<int:naloga_id>/oddaje/', views.ucitelj_oddaje_pregled, name='ucitelj_oddaje_pregled'),

    # Učenec
    path('ucenec/', views.ucenec_nadzorna_plosca, name='ucenec_nadzorna_plosca'),
    path('ucenec/predmeti/', views.ucenec_moji_predmeti, name='ucenec_moji_predmeti'),
    path('ucenec/predmet/<int:pk>/gradiva/', views.ucenec_predmet_gradiva, name='ucenec_predmet_gradiva'),
    path('ucenec/naloga/<int:naloga_id>/oddaj/', views.ucenec_naloga_oddaja, name='ucenec_naloga_oddaja'),
]


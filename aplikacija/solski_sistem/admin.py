from django.contrib import admin
from .models import Predmet, Gradivo, Naloga, OddajaNaloge

@admin.register(Predmet)
class PredmetAdmin(admin.ModelAdmin):
    list_display = ('naziv', 'koda', 'letnik', 'st_uciteljev', 'st_ucencev', 'ustvarjeno_ob')
    search_fields = ('naziv', 'koda', 'opis')
    list_filter = ('letnik',)
    filter_horizontal = ('ucitelji', 'ucenci')

@admin.register(Gradivo)
class GradivoAdmin(admin.ModelAdmin):
    list_display = ('naslov', 'predmet', 'avtor', 'datoteka', 'nalozeno_ob')
    search_fields = ('naslov', 'opis', 'predmet__naziv')
    list_filter = ('predmet', 'nalozeno_ob')

@admin.register(Naloga)
class NalogaAdmin(admin.ModelAdmin):
    list_display = ('naslov', 'predmet', 'avtor', 'rok_oddaje', 'st_oddaj', 'ustvarjeno_ob')
    search_fields = ('naslov', 'navodila', 'predmet__naziv')
    list_filter = ('predmet', 'rok_oddaje')

@admin.register(OddajaNaloge)
class OddajaNalogeAdmin(admin.ModelAdmin):
    list_display = ('naloga', 'ucenec', 'datoteka', 'oddano_ob')
    search_fields = ('ucenec__first_name', 'ucenec__last_name', 'ucenec__username', 'naloga__naslov')
    list_filter = ('naloga__predmet', 'oddano_ob')


import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from jedro.decorators import admin_required, ucitelj_required, ucenec_required
from jedro.models import Uporabnik
from .models import Predmet, Gradivo, Naloga, OddajaNaloge
from .forms import (
    PredmetForm, UciteljAdminForm, UcenecAdminForm,
    GradivoForm, NalogaForm, OddajaNalogeForm
)

# ==========================================
# 1. ADMINISTRATOR POGLEDI
# ==========================================

@admin_required
def admin_nadzorna_plosca(request):
    """Glavna administratorska nadzorna plošča s statistiko."""
    st_predmetov = Predmet.objects.count()
    st_uciteljev = Uporabnik.objects.filter(vloga=Uporabnik.Vloga.UCITELJ).count()
    st_ucencev = Uporabnik.objects.filter(vloga=Uporabnik.Vloga.UCENEC).count()
    st_gradiv = Gradivo.objects.count()
    st_nalog = Naloga.objects.count()
    st_oddaj = OddajaNaloge.objects.count()

    zadnji_predmeti = Predmet.objects.order_by('-ustvarjeno_ob')[:5]
    zadnje_oddaje = OddajaNaloge.objects.select_related('ucenec', 'naloga').order_by('-oddano_ob')[:5]

    kontekst = {
        'st_predmetov': st_predmetov,
        'st_uciteljev': st_uciteljev,
        'st_ucencev': st_ucencev,
        'st_gradiv': st_gradiv,
        'st_nalog': st_nalog,
        'st_oddaj': st_oddaj,
        'zadnji_predmeti': zadnji_predmeti,
        'zadnje_oddaje': zadnje_oddaje,
    }
    return render(request, 'admin_portal/index.html', kontekst)

# --- PREDMETI (CRUD) ---

@admin_required
def admin_predmeti_seznam(request):
    poizvedba = request.GET.get('q', '').strip()
    predmeti = Predmet.objects.annotate(
        st_uciteljev_count=Count('ucitelji', distinct=True),
        st_ucencev_count=Count('ucenci', distinct=True)
    )
    if poizvedba:
        predmeti = predmeti.filter(Q(naziv__icontains=poizvedba) | Q(koda__icontains=poizvedba))

    return render(request, 'admin_portal/predmeti_seznam.html', {
        'predmeti': predmeti,
        'poizvedba': poizvedba
    })

@admin_required
def admin_predmet_ustvari(request):
    if request.method == 'POST':
        form = PredmetForm(request.POST)
        if form.is_valid():
            predmet = form.save()
            messages.success(request, f"Predmet '{predmet.naziv}' je bil uspešno ustvarjen.")
            return redirect('admin_predmeti_seznam')
    else:
        form = PredmetForm()
    return render(request, 'admin_portal/predmet_obrazec.html', {'form': form, 'naslov_akcije': 'Dodaj nov predmet'})

@admin_required
def admin_predmet_uredi(request, pk):
    predmet = get_object_or_404(Predmet, pk=pk)
    if request.method == 'POST':
        form = PredmetForm(request.POST, instance=predmet)
        if form.is_valid():
            form.save()
            messages.success(request, f"Predmet '{predmet.naziv}' je bil uspešno posodobljen.")
            return redirect('admin_predmeti_seznam')
    else:
        form = PredmetForm(instance=predmet)
    return render(request, 'admin_portal/predmet_obrazec.html', {'form': form, 'predmet': predmet, 'naslov_akcije': f'Uredi predmet: {predmet.naziv}'})

@admin_required
def admin_predmet_izbrisi(request, pk):
    predmet = get_object_or_404(Predmet, pk=pk)
    if request.method == 'POST':
        naziv = predmet.naziv
        predmet.delete()
        messages.success(request, f"Predmet '{naziv}' je bil uspešno izbrisan.")
        return redirect('admin_predmeti_seznam')
    return render(request, 'admin_portal/potrdi_izbris.html', {
        'objekt': predmet,
        'tip': 'predmet',
        'nazaj_url': 'admin_predmeti_seznam'
    })

# --- UČITELJI (CRUD) ---

@admin_required
def admin_ucitelji_seznam(request):
    poizvedba = request.GET.get('q', '').strip()
    ucitelji = Uporabnik.objects.filter(vloga=Uporabnik.Vloga.UCITELJ).prefetch_related('poucuje_predmete')
    if poizvedba:
        ucitelji = ucitelji.filter(
            Q(first_name__icontains=poizvedba) |
            Q(last_name__icontains=poizvedba) |
            Q(username__icontains=poizvedba) |
            Q(email__icontains=poizvedba)
        )
    return render(request, 'admin_portal/ucitelji_seznam.html', {
        'ucitelji': ucitelji,
        'poizvedba': poizvedba
    })

@admin_required
def admin_ucitelj_ustvari(request):
    if request.method == 'POST':
        form = UciteljAdminForm(request.POST)
        if form.is_valid():
            ucitelj = form.save()
            messages.success(request, f"Učitelj '{ucitelj.polno_ime}' je bil uspešno dodan.")
            return redirect('admin_ucitelji_seznam')
    else:
        form = UciteljAdminForm()
    return render(request, 'admin_portal/ucitelj_obrazec.html', {'form': form, 'naslov_akcije': 'Dodaj novega učitelja'})

@admin_required
def admin_ucitelj_uredi(request, pk):
    ucitelj = get_object_or_404(Uporabnik, pk=pk, vloga=Uporabnik.Vloga.UCITELJ)
    if request.method == 'POST':
        form = UciteljAdminForm(request.POST, instance=ucitelj)
        if form.is_valid():
            form.save()
            messages.success(request, f"Podatki za učitelja '{ucitelj.polno_ime}' so posodobljeni.")
            return redirect('admin_ucitelji_seznam')
    else:
        form = UciteljAdminForm(instance=ucitelj)
    return render(request, 'admin_portal/ucitelj_obrazec.html', {'form': form, 'ucitelj': ucitelj, 'naslov_akcije': f'Uredi učitelja: {ucitelj.polno_ime}'})

@admin_required
def admin_ucitelj_izbrisi(request, pk):
    ucitelj = get_object_or_404(Uporabnik, pk=pk, vloga=Uporabnik.Vloga.UCITELJ)
    if request.method == 'POST':
        ime = ucitelj.polno_ime
        ucitelj.delete()
        messages.success(request, f"Učitelj '{ime}' je bil izbrisan.")
        return redirect('admin_ucitelji_seznam')
    return render(request, 'admin_portal/potrdi_izbris.html', {
        'objekt': ucitelj,
        'tip': 'učitelja',
        'nazaj_url': 'admin_ucitelji_seznam'
    })

# --- UČENCI (CRUD) ---

@admin_required
def admin_ucenci_seznam(request):
    poizvedba = request.GET.get('q', '').strip()
    predmet_id = request.GET.get('predmet', '').strip()
    ucenci = Uporabnik.objects.filter(vloga=Uporabnik.Vloga.UCENEC).prefetch_related('obiskuje_predmete')

    if poizvedba:
        ucenci = ucenci.filter(
            Q(first_name__icontains=poizvedba) |
            Q(last_name__icontains=poizvedba) |
            Q(username__icontains=poizvedba) |
            Q(email__icontains=poizvedba)
        )
    if predmet_id:
        ucenci = ucenci.filter(obiskuje_predmete__id=predmet_id)

    paginator = Paginator(ucenci, 25)
    stran_st = request.GET.get('page')
    ucenci_stran = paginator.get_page(stran_st)

    predmeti = Predmet.objects.all()

    return render(request, 'admin_portal/ucenci_seznam.html', {
        'ucenci': ucenci_stran,
        'predmeti': predmeti,
        'poizvedba': poizvedba,
        'izbran_predmet': predmet_id,
        'skupaj_ucencev': ucenci.count(),
    })

@admin_required
def admin_ucenec_ustvari(request):
    if request.method == 'POST':
        form = UcenecAdminForm(request.POST)
        if form.is_valid():
            ucenec = form.save()
            messages.success(request, f"Učenec '{ucenec.polno_ime}' je bil uspešno ustvarjen.")
            return redirect('admin_ucenci_seznam')
    else:
        form = UcenecAdminForm()
    return render(request, 'admin_portal/ucenec_obrazec.html', {'form': form, 'naslov_akcije': 'Dodaj novega učenca'})

@admin_required
def admin_ucenec_uredi(request, pk):
    ucenec = get_object_or_404(Uporabnik, pk=pk, vloga=Uporabnik.Vloga.UCENEC)
    if request.method == 'POST':
        form = UcenecAdminForm(request.POST, instance=ucenec)
        if form.is_valid():
            form.save()
            messages.success(request, f"Podatki za učenca '{ucenec.polno_ime}' so posodobljeni.")
            return redirect('admin_ucenci_seznam')
    else:
        form = UcenecAdminForm(instance=ucenec)
    return render(request, 'admin_portal/ucenec_obrazec.html', {'form': form, 'ucenec': ucenec, 'naslov_akcije': f'Uredi učenca: {ucenec.polno_ime}'})

@admin_required
def admin_ucenec_izbrisi(request, pk):
    ucenec = get_object_or_404(Uporabnik, pk=pk, vloga=Uporabnik.Vloga.UCENEC)
    if request.method == 'POST':
        ime = ucenec.polno_ime
        ucenec.delete()
        messages.success(request, f"Učenec '{ime}' je bil izbrisan.")
        return redirect('admin_ucenci_seznam')
    return render(request, 'admin_portal/potrdi_izbris.html', {
        'objekt': ucenec,
        'tip': 'učenca',
        'nazaj_url': 'admin_ucenci_seznam'
    })


# ==========================================
# 2. UČITELJ POGLEDI
# ==========================================

@ucitelj_required
def ucitelj_nadzorna_plosca(request):
    """Prikaz predmetov, ki jih učitelj dejansko poučuje."""
    predmeti = request.user.poucuje_predmete.annotate(
        st_gradiv_count=Count('gradiva', distinct=True),
        st_nalog_count=Count('naloge', distinct=True),
        st_ucencev_count=Count('ucenci', distinct=True)
    )
    return render(request, 'ucitelj_portal/index.html', {'predmeti': predmeti})

@ucitelj_required
def ucitelj_predmet_detajli(request, pk):
    """Pregled izbranega predmeta (gradiva, naloge). Samo za predmete, ki jih učitelj poučuje."""
    predmet = get_object_or_404(Predmet, pk=pk)
    if not (request.user.je_admin or predmet in request.user.poucuje_predmete.all()):
        messages.error(request, "Nimate pooblastila za vpogled v ta predmet, saj ga ne poučujete.")
        return redirect('ucitelj_nadzorna_plosca')

    gradiva = predmet.gradiva.select_related('avtor').all()
    naloge = predmet.naloge.prefetch_related('oddaje').all()

    return render(request, 'ucitelj_portal/predmet_detajli.html', {
        'predmet': predmet,
        'gradiva': gradiva,
        'naloge': naloge,
    })

@ucitelj_required
def ucitelj_gradivo_dodaj(request, predmet_id):
    """Nalaganje gradiv za predmet (samo za predmete, ki jih dejansko poučuje)."""
    predmet = get_object_or_404(Predmet, pk=predmet_id)
    if not (request.user.je_admin or predmet in request.user.poucuje_predmete.all()):
        messages.error(request, "Gradiva lahko nalagate le za predmete, ki jih dejansko poučujete.")
        return redirect('ucitelj_nadzorna_plosca')

    if request.method == 'POST':
        form = GradivoForm(request.POST, request.FILES)
        if form.is_valid():
            gradivo = form.save(commit=False)
            gradivo.predmet = predmet
            gradivo.avtor = request.user
            gradivo.save()
            messages.success(request, f"Gradivo '{gradivo.naslov}' je bilo uspešno naloženo.")
            return redirect('ucitelj_predmet_detajli', pk=predmet.pk)
    else:
        form = GradivoForm()

    return render(request, 'ucitelj_portal/gradivo_obrazec.html', {
        'form': form,
        'predmet': predmet,
        'naslov_akcije': f"Naloži novo gradivo za {predmet.naziv}"
    })

@ucitelj_required
def ucitelj_gradivo_izbrisi(request, pk):
    """Brisanje gradiva (samo za predmete, ki jih dejansko poučuje)."""
    gradivo = get_object_or_404(Gradivo, pk=pk)
    predmet = gradivo.predmet
    if not (request.user.je_admin or predmet in request.user.poucuje_predmete.all()):
        messages.error(request, "Brisati smete le gradiva za predmete, ki jih poučujete.")
        return redirect('ucitelj_nadzorna_plosca')

    if request.method == 'POST':
        naslov = gradivo.naslov
        # Izbriši datoteko s strežnika
        if gradivo.datoteka and os.path.isfile(gradivo.datoteka.path):
            try:
                os.remove(gradivo.datoteka.path)
            except OSError:
                pass
        gradivo.delete()
        messages.success(request, f"Gradivo '{naslov}' je bilo izbrisano.")
        return redirect('ucitelj_predmet_detajli', pk=predmet.pk)

    return render(request, 'admin_portal/potrdi_izbris.html', {
        'objekt': gradivo,
        'tip': 'gradivo',
        'nazaj_url': 'ucitelj_predmet_detajli',
        'nazaj_pk': predmet.pk
    })

@ucitelj_required
def ucitelj_naloga_dodaj(request, predmet_id):
    """Ustvarjanje nove naloge pri predmetu."""
    predmet = get_object_or_404(Predmet, pk=predmet_id)
    if not (request.user.je_admin or predmet in request.user.poucuje_predmete.all()):
        messages.error(request, "Naloge lahko ustvarjate le pri predmetih, ki jih poučujete.")
        return redirect('ucitelj_nadzorna_plosca')

    if request.method == 'POST':
        form = NalogaForm(request.POST)
        if form.is_valid():
            naloga = form.save(commit=False)
            naloga.predmet = predmet
            naloga.avtor = request.user
            naloga.save()
            messages.success(request, f"Naloga '{naloga.naslov}' je bila uspešno objavljena.")
            return redirect('ucitelj_predmet_detajli', pk=predmet.pk)
    else:
        form = NalogaForm()

    return render(request, 'ucitelj_portal/naloga_obrazec.html', {
        'form': form,
        'predmet': predmet,
        'naslov_akcije': f"Objavi novo nalogo za {predmet.naziv}"
    })

@ucitelj_required
def ucitelj_oddaje_pregled(request, naloga_id):
    """Pregled nalog, ki so jih učenci oddali pri izbranem predmetu."""
    naloga = get_object_or_404(Naloga, pk=naloga_id)
    predmet = naloga.predmet
    if not (request.user.je_admin or predmet in request.user.poucuje_predmete.all()):
        messages.error(request, "Nimate dostopa do oddaj za ta predmet.")
        return redirect('ucitelj_nadzorna_plosca')

    oddaje = naloga.oddaje.select_related('ucenec').order_by('-oddano_ob')
    return render(request, 'ucitelj_portal/oddaje_seznam.html', {
        'naloga': naloga,
        'predmet': predmet,
        'oddaje': oddaje
    })


# ==========================================
# 3. UČENEC POGLEDI
# ==========================================

@ucenec_required
def ucenec_nadzorna_plosca(request):
    """Nadzorna plošča za učenca z vpisanimi predmeti in aktualnimi nalogami."""
    predmeti = request.user.obiskuje_predmete.annotate(
        st_gradiv_count=Count('gradiva', distinct=True),
        st_nalog_count=Count('naloge', distinct=True)
    )
    # Naloge pri predmetih, ki jih učenec obiskuje
    predmet_ids = predmeti.values_list('id', flat=True)
    odprte_naloge = Naloga.objects.filter(predmet_id__in=predmet_ids).order_by('rok_oddaje', '-ustvarjeno_ob')

    # Dobi slovar id_naloge -> oddaja učenca
    oddaje_ucenca = {
        o.naloga_id: o for o in OddajaNaloge.objects.filter(ucenec=request.user, naloga_id__in=odprte_naloge.values_list('id', flat=True))
    }

    return render(request, 'ucenec_portal/index.html', {
        'predmeti': predmeti,
        'odprte_naloge': odprte_naloge,
        'oddaje_ucenca': oddaje_ucenca,
    })

@ucenec_required
def ucenec_moji_predmeti(request):
    """Pregled seznama predmetov, ki jih učenec obiskuje."""
    predmeti = request.user.obiskuje_predmete.prefetch_related('ucitelji')
    return render(request, 'ucenec_portal/moji_predmeti.html', {'predmeti': predmeti})

@ucenec_required
def ucenec_predmet_gradiva(request, pk):
    """Vpogled v gradiva vsakega predmeta s seznama vpisanih predmetov."""
    predmet = get_object_or_404(Predmet, pk=pk)
    if not (request.user.je_admin or predmet in request.user.obiskuje_predmete.all()):
        messages.error(request, "Vpogled v gradiva je dovoljen le za predmete z vašega seznama vpisanih predmetov.")
        return redirect('ucenec_moji_predmeti')

    gradiva = predmet.gradiva.select_related('avtor').all()
    naloge = predmet.naloge.all()

    # Preveri že oddane naloge tega učenca
    oddaje = {o.naloga_id: o for o in OddajaNaloge.objects.filter(ucenec=request.user, naloga__in=naloge)}

    return render(request, 'ucenec_portal/predmet_gradiva.html', {
        'predmet': predmet,
        'gradiva': gradiva,
        'naloge': naloge,
        'oddaje': oddaje
    })

@ucenec_required
def ucenec_naloga_oddaja(request, naloga_id):
    """
    Oddaja nalog pri predmetih s seznama.
    Zahteve:
    - Shrani datoteko na strežniku pod imenom „Priimek Ime – Naslov naloge“ z ustrezno končnico.
    - Ponovna oddaja naj povozi prejšnjo datoteko, vendar ŠELE potem, ko to potrdi učenec.
    """
    naloga = get_object_or_404(Naloga, pk=naloga_id)
    predmet = naloga.predmet

    if not (request.user.je_admin or predmet in request.user.obiskuje_predmete.all()):
        messages.error(request, "Nalogo lahko oddate le pri predmetih, ki jih obiskujete.")
        return redirect('ucenec_nadzorna_plosca')

    obstojeca_oddaja = OddajaNaloge.objects.filter(naloga=naloga, ucenec=request.user).first()
    ze_oddano = obstojeca_oddaja is not None

    if request.method == 'POST':
        form = OddajaNalogeForm(request.POST, request.FILES, ze_oddano=ze_oddano, instance=obstojeca_oddaja)
        if form.is_valid():
            # Če obstaja stara datoteka in uporabnik oddaja novo, najprej pobrišemo staro s strežnika
            if obstojeca_oddaja and 'datoteka' in request.FILES:
                stara_pot = obstojeca_oddaja.datoteka.path if obstojeca_oddaja.datoteka else None
                if stara_pot and os.path.isfile(stara_pot):
                    try:
                        os.remove(stara_pot)
                    except OSError:
                        pass

            oddaja = form.save(commit=False)
            oddaja.naloga = naloga
            oddaja.ucenec = request.user
            oddaja.save()

            if ze_oddano:
                messages.success(request, f"Naloga je bila uspešno ponovno oddana in posodobljena (datoteka: '{oddaja.ime_datoteke}').")
            else:
                messages.success(request, f"Naloga je bila uspešno oddana (datoteka shranjena kot: '{oddaja.ime_datoteke}').")
            return redirect('ucenec_predmet_gradiva', pk=predmet.pk)
    else:
        form = OddajaNalogeForm(ze_oddano=ze_oddano, instance=obstojeca_oddaja)

    return render(request, 'ucenec_portal/naloga_oddaja.html', {
        'naloga': naloga,
        'predmet': predmet,
        'form': form,
        'obstojeca_oddaja': obstojeca_oddaja,
        'ze_oddano': ze_oddano
    })


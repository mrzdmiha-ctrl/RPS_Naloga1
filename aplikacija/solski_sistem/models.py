import os
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.files.storage import FileSystemStorage

class TocnoImeOverwriteStorage(FileSystemStorage):
    """
    Shrani datoteko z natančnim imenom (ohrani presledke, pomišljaj in šumnike)
    ter ob ponovni oddaji povozi prejšnjo datoteko brez dodajanja naključnih pripon.
    """
    def get_valid_name(self, name):
        dir_name, file_name = os.path.split(name)
        for znak in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
            file_name = file_name.replace(znak, '-')
        return os.path.join(dir_name, file_name) if dir_name else file_name

    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            self.delete(name)
        return name

oddaje_shramba = TocnoImeOverwriteStorage()

def pot_za_oddajo_naloge(instance, filename):
    """
    Sistem mora datoteko na strežniku shraniti pod imenom:
    „Priimek Ime – Naslov naloge“ z ustrezno končnico.
    """
    _, ext = os.path.splitext(filename)
    priimek = instance.ucenec.last_name.strip() if instance.ucenec else "Neznan"
    ime = instance.ucenec.first_name.strip() if instance.ucenec else "Ucenec"
    naslov = instance.naloga.naslov.strip() if instance.naloga else "Naloga"

    # Prepreči težave z neveljavnimi znaki v imenih datotek za OS
    nedovoljeni_znaki = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for znak in nedovoljeni_znaki:
        naslov = naslov.replace(znak, '-')
        priimek = priimek.replace(znak, '')
        ime = ime.replace(znak, '')

    ime_datoteke = f"{priimek} {ime} – {naslov}{ext}"
    return os.path.join('oddaje', ime_datoteke)

class Predmet(models.Model):
    naziv = models.CharField(max_length=120, verbose_name="Naziv predmeta")
    koda = models.CharField(max_length=20, unique=True, verbose_name="Kratica / Koda")
    opis = models.TextField(blank=True, verbose_name="Opis predmeta")
    letnik = models.PositiveSmallIntegerField(default=1, verbose_name="Letnik")
    
    ucitelji = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='poucuje_predmete',
        verbose_name="Učitelji, ki poučujejo ta predmet"
    )
    ucenci = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='obiskuje_predmete',
        verbose_name="Vpisani učenci"
    )
    ustvarjeno_ob = models.DateTimeField(auto_now_add=True, verbose_name="Datum nastanka")

    class Meta:
        verbose_name = "Predmet"
        verbose_name_plural = "Predmeti"
        ordering = ['letnik', 'naziv']

    def __str__(self):
        return f"{self.naziv} ({self.koda})"

    @property
    def st_uciteljev(self):
        return self.ucitelji.count()

    @property
    def st_ucencev(self):
        return self.ucenci.count()

    @property
    def st_gradiv(self):
        return self.gradiva.count()

    @property
    def st_nalog(self):
        return self.naloge.count()

class Gradivo(models.Model):
    predmet = models.ForeignKey(
        Predmet,
        on_delete=models.CASCADE,
        related_name='gradiva',
        verbose_name="Predmet"
    )
    avtor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='nalozena_gradiva',
        verbose_name="Učitelj (avtor)"
    )
    naslov = models.CharField(max_length=150, verbose_name="Naslov gradiva")
    opis = models.TextField(blank=True, verbose_name="Opis gradiva")
    datoteka = models.FileField(upload_to='gradiva/', verbose_name="Datoteka gradiva")
    nalozeno_ob = models.DateTimeField(auto_now_add=True, verbose_name="Naloženo dne")

    class Meta:
        verbose_name = "Gradivo"
        verbose_name_plural = "Gradiva"
        ordering = ['-nalozeno_ob']

    def __str__(self):
        return f"{self.naslov} ({self.predmet.koda})"

    @property
    def ime_datoteke(self):
        return os.path.basename(self.datoteka.name)

class Naloga(models.Model):
    predmet = models.ForeignKey(
        Predmet,
        on_delete=models.CASCADE,
        related_name='naloge',
        verbose_name="Predmet"
    )
    avtor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ustvarjene_naloge',
        verbose_name="Učitelj"
    )
    naslov = models.CharField(max_length=150, verbose_name="Naslov naloge")
    navodila = models.TextField(verbose_name="Navodila za oddajo")
    rok_oddaje = models.DateTimeField(null=True, blank=True, verbose_name="Rok za oddajo")
    ustvarjeno_ob = models.DateTimeField(auto_now_add=True, verbose_name="Ustvarjeno")

    class Meta:
        verbose_name = "Naloga"
        verbose_name_plural = "Naloge"
        ordering = ['-ustvarjeno_ob']

    def __str__(self):
        return f"{self.naslov} - {self.predmet.naziv}"

    @property
    def je_rok_potekel(self):
        if self.rok_oddaje:
            return timezone.now() > self.rok_oddaje
        return False

    @property
    def st_oddaj(self):
        return self.oddaje.count()

class OddajaNaloge(models.Model):
    naloga = models.ForeignKey(
        Naloga,
        on_delete=models.CASCADE,
        related_name='oddaje',
        verbose_name="Naloga"
    )
    ucenec = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='oddane_naloge',
        verbose_name="Učenec"
    )
    datoteka = models.FileField(
        upload_to=pot_za_oddajo_naloge,
        storage=oddaje_shramba,
        verbose_name="Oddana datoteka"
    )
    opomba = models.TextField(blank=True, verbose_name="Opomba učenca ob oddaji")
    oddano_ob = models.DateTimeField(auto_now=True, verbose_name="Čas oddaje")

    class Meta:
        verbose_name = "Oddaja naloge"
        verbose_name_plural = "Oddaje nalog"
        unique_together = ('naloga', 'ucenec')
        ordering = ['-oddano_ob']

    def __str__(self):
        return f"{self.ucenec.priimek_ime} - {self.naloga.naslov}"

    @property
    def ime_datoteke(self):
        return os.path.basename(self.datoteka.name)


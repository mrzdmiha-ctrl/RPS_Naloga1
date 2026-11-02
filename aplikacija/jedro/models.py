from django.db import models
from django.contrib.auth.models import AbstractUser

class Uporabnik(AbstractUser):
    class Vloga(models.TextChoices):
        ADMINISTRATOR = 'ADMIN', 'Administrator'
        UCITELJ = 'UCITELJ', 'Učitelj'
        UCENEC = 'UCENEC', 'Učenec'

    vloga = models.CharField(
        max_length=20,
        choices=Vloga.choices,
        default=Vloga.UCENEC,
        verbose_name="Vloga uporabnika"
    )
    telefon = models.CharField(max_length=30, blank=True, verbose_name="Telefonska številka")
    naslov = models.CharField(max_length=150, blank=True, verbose_name="Naslov bivanja")

    class Meta:
        verbose_name = "Uporabnik"
        verbose_name_plural = "Uporabniki"
        ordering = ['last_name', 'first_name', 'username']

    def __str__(self):
        polno = f"{self.first_name} {self.last_name}".strip()
        if polno:
            return f"{polno} ({self.get_vloga_display()})"
        return f"{self.username} ({self.get_vloga_display()})"

    @property
    def je_admin(self):
        return self.vloga == self.Vloga.ADMINISTRATOR or self.is_superuser

    @property
    def je_ucitelj(self):
        return self.vloga == self.Vloga.UCITELJ

    @property
    def je_ucenec(self):
        return self.vloga == self.Vloga.UCENEC

    @property
    def polno_ime(self):
        polno = f"{self.first_name} {self.last_name}".strip()
        return polno if polno else self.username

    @property
    def priimek_ime(self):
        pi = f"{self.last_name} {self.first_name}".strip()
        return pi if pi else self.username


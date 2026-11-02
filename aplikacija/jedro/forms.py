from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Uporabnik

class PrijavaForm(AuthenticationForm):
    username = forms.CharField(
        label="Uporabniško ime",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vnesite uporabniško ime'})
    )
    password = forms.CharField(
        label="Geslo",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Vnesite geslo'})
    )

class RegistracijaUcencaForm(UserCreationForm):
    first_name = forms.CharField(
        label="Ime",
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vnesite ime'})
    )
    last_name = forms.CharField(
        label="Priimek",
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vnesite priimek'})
    )
    email = forms.EmailField(
        label="E-poštni naslov",
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ime.priimek@sola.si'})
    )

    class Meta:
        model = Uporabnik
        fields = ('username', 'first_name', 'last_name', 'email', 'telefon', 'naslov')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Izberite uporabniško ime'}),
            'telefon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'npr. 041 123 456'}),
            'naslov': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ulica in hišna številka, kraj'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.vloga = Uporabnik.Vloga.UCENEC
        if commit:
            user.save()
        return user

class UrediProfilForm(forms.ModelForm):
    class Meta:
        model = Uporabnik
        fields = ('first_name', 'last_name', 'email', 'telefon', 'naslov')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefon': forms.TextInput(attrs={'class': 'form-control'}),
            'naslov': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'Ime',
            'last_name': 'Priimek',
            'email': 'E-poštni naslov',
            'telefon': 'Telefonska številka',
            'naslov': 'Naslov',
        }


import os
from django import forms
from django.contrib.auth.password_validation import validate_password
from jedro.models import Uporabnik
from .models import Predmet, Gradivo, Naloga, OddajaNaloge

class PredmetForm(forms.ModelForm):
    ucitelji = forms.ModelMultipleChoiceField(
        queryset=Uporabnik.objects.filter(vloga=Uporabnik.Vloga.UCITELJ),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Določi učitelje, ki poučujejo ta predmet"
    )

    class Meta:
        model = Predmet
        fields = ('naziv', 'koda', 'opis', 'letnik', 'ucitelji')
        widgets = {
            'naziv': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'npr. Razvoj programskih sistemov'}),
            'koda': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'npr. RPS'}),
            'opis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Kratek opis predmeta'}),
            'letnik': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['ucitelji'].initial = self.instance.ucitelji.all()

    def save(self, commit=True):
        predmet = super().save(commit=commit)
        if commit:
            predmet.ucitelji.set(self.cleaned_data['ucitelji'])
        else:
            old_save_m2m = self.save_m2m
            def new_save_m2m():
                old_save_m2m()
                predmet.ucitelji.set(self.cleaned_data['ucitelji'])
            self.save_m2m = new_save_m2m
        return predmet

class UciteljAdminForm(forms.ModelForm):
    password = forms.CharField(
        label="Geslo",
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Vnesite geslo (pustite prazno, če ne spreminjate)'})
    )
    predmeti = forms.ModelMultipleChoiceField(
        queryset=Predmet.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Predmeti, ki jih ta učitelj poučuje"
    )

    class Meta:
        model = Uporabnik
        fields = ('username', 'first_name', 'last_name', 'email', 'telefon', 'password')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefon': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['password'].required = True
        else:
            self.fields['predmeti'].initial = self.instance.poucuje_predmete.all()

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.instance.pk and not password:
            raise forms.ValidationError("Geslo je obvezno ob kreiranju učitelja.")
        if password:
            validate_password(password, self.instance)
        return password

    def save(self, commit=True):
        ucitelj = super().save(commit=False)
        ucitelj.vloga = Uporabnik.Vloga.UCITELJ
        password = self.cleaned_data.get('password')
        if password:
            ucitelj.set_password(password)
        if commit:
            ucitelj.save()
            predmeti = self.cleaned_data.get('predmeti', [])
            ucitelj.poucuje_predmete.set(predmeti)
        return ucitelj

class UcenecAdminForm(forms.ModelForm):
    password = forms.CharField(
        label="Geslo",
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Vnesite geslo (pustite prazno, če ne spreminjate)'})
    )
    predmeti = forms.ModelMultipleChoiceField(
        queryset=Predmet.objects.all(),
        required=True,
        widget=forms.CheckboxSelectMultiple,
        label="Predmeti, ki jih učenec obiskuje (obvezno vsaj 2 predmeta)"
    )

    class Meta:
        model = Uporabnik
        fields = ('username', 'first_name', 'last_name', 'email', 'telefon', 'naslov', 'password')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefon': forms.TextInput(attrs={'class': 'form-control'}),
            'naslov': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['password'].required = True
        else:
            self.fields['predmeti'].initial = self.instance.obiskuje_predmete.all()

    def clean_predmeti(self):
        predmeti = self.cleaned_data.get('predmeti')
        if not predmeti or predmeti.count() < 2:
            raise forms.ValidationError("Po navodilih mora vsak učenec obiskovati več kot en predmet (vsaj 2 predmeta).")
        return predmeti

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.instance.pk and not password:
            raise forms.ValidationError("Geslo je obvezno ob kreiranju učenca.")
        if password:
            validate_password(password, self.instance)
        return password

    def save(self, commit=True):
        ucenec = super().save(commit=False)
        ucenec.vloga = Uporabnik.Vloga.UCENEC
        password = self.cleaned_data.get('password')
        if password:
            ucenec.set_password(password)
        if commit:
            ucenec.save()
            predmeti = self.cleaned_data.get('predmeti', [])
            ucenec.obiskuje_predmete.set(predmeti)
        return ucenec

class GradivoForm(forms.ModelForm):
    class Meta:
        model = Gradivo
        fields = ('naslov', 'opis', 'datoteka')
        widgets = {
            'naslov': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'npr. Predavanja 1 - Uvod v Docker'}),
            'opis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Kratek opis gradiva za učence'}),
            'datoteka': forms.FileInput(attrs={'class': 'form-control'}),
        }

class NalogaForm(forms.ModelForm):
    rok_oddaje = forms.DateTimeField(
        required=False,
        label="Rok za oddajo (opcijsko)",
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
    )

    class Meta:
        model = Naloga
        fields = ('naslov', 'navodila', 'rok_oddaje')
        widgets = {
            'naslov': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'npr. Domača naloga 1'}),
            'navodila': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Podrobna navodila za oddajo naloge'}),
        }

class OddajaNalogeForm(forms.ModelForm):
    potrditev_prepisa = forms.BooleanField(
        required=False,
        label="Potrjujem, da želim prepisati predhodno oddano datoteko."
    )

    class Meta:
        model = OddajaNaloge
        fields = ('datoteka', 'opomba')
        widgets = {
            'datoteka': forms.FileInput(attrs={'class': 'form-control'}),
            'opomba': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Opcijska opomba učitelju'}),
        }

    def __init__(self, *args, ze_oddano=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.ze_oddano = ze_oddano
        if ze_oddano:
            self.fields['potrditev_prepisa'].required = True
            self.fields['potrditev_prepisa'].help_text = (
                "To nalogo ste že oddali. Pred ponovno oddajo morate potrditi prepis datoteke."
            )

    def clean(self):
        cleaned_data = super().clean()
        if self.ze_oddano and not cleaned_data.get('potrditev_prepisa'):
            self.add_error('potrditev_prepisa', "Pred ponovno oddajo morate obvezno potrditi prepis prejšnje datoteke.")
        return cleaned_data


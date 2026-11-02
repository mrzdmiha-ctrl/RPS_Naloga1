import os
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from jedro.models import Uporabnik
from .models import Predmet, Gradivo, Naloga, OddajaNaloge

class SolskiSistemTesti(TestCase):
    def setUp(self):
        # Ustvari administratorja
        self.admin = Uporabnik.objects.create_superuser(
            username='admin_test',
            email='admin@test.si',
            password='geslo_admin_123',
            first_name='Admin',
            last_name='Sistemski',
            vloga=Uporabnik.Vloga.ADMINISTRATOR
        )

        # Ustvari učitelja 1 in učitelja 2
        self.ucitelj1 = Uporabnik.objects.create_user(
            username='profesor1',
            email='prof1@test.si',
            password='geslo_prof_123',
            first_name='Tone',
            last_name='Pavček',
            vloga=Uporabnik.Vloga.UCITELJ
        )
        self.ucitelj2 = Uporabnik.objects.create_user(
            username='profesor2',
            email='prof2@test.si',
            password='geslo_prof_123',
            first_name='France',
            last_name='Prešeren',
            vloga=Uporabnik.Vloga.UCITELJ
        )

        # Ustvari učenca
        self.ucenec = Uporabnik.objects.create_user(
            username='dijak1',
            email='dijak1@test.si',
            password='geslo_dijak_123',
            first_name='Janez',
            last_name='Novak',
            vloga=Uporabnik.Vloga.UCENEC
        )

        # Ustvari 2 predmeta
        self.predmet1 = Predmet.objects.create(
            naziv='Razvoj programskih sistemov',
            koda='RPS',
            letnik=3
        )
        self.predmet2 = Predmet.objects.create(
            naziv='Podatkovne baze',
            koda='PB',
            letnik=2
        )

        # Učitelj 1 poučuje oba predmeta, Učitelj 2 poučuje predmet 1 (nekateri predmeti več učiteljev, učitelj več predmetov)
        self.predmet1.ucitelji.set([self.ucitelj1, self.ucitelj2])
        self.predmet2.ucitelji.set([self.ucitelj1])

        # Učenec obiskuje oba predmeta (več kot 1 predmet)
        self.ucenec.obiskuje_predmete.set([self.predmet1, self.predmet2])

        # Naloga pri predmetu 1
        self.naloga = Naloga.objects.create(
            predmet=self.predmet1,
            avtor=self.ucitelj1,
            naslov='Domača naloga 1',
            navodila='Rešite vse naloge in oddajte poročilo.'
        )

    def test_relacije_in_omejitve(self):
        """Preveri relacije med učitelji, predmeti in učenci po navodilih."""
        # Predmet 1 ima 2 učitelja
        self.assertEqual(self.predmet1.ucitelji.count(), 2)
        # Učitelj 1 poučuje 2 predmeta
        self.assertEqual(self.ucitelj1.poucuje_predmete.count(), 2)
        # Učenec obiskuje več kot 1 predmet
        self.assertGreater(self.ucenec.obiskuje_predmete.count(), 1)

    def test_ucenec_oddaja_naloge_in_poimenovanje(self):
        """
        Preveri, da sistem datoteko na strežniku shrani pod imenom
        „Priimek Ime – Naslov naloge“ z ustrezno končnico.
        """
        c = Client()
        c.login(username='dijak1', password='geslo_dijak_123')

        testna_datoteka = SimpleUploadedFile("moje_porocilo.txt", b"Vsebina resitve naloge.")
        url = reverse('ucenec_naloga_oddaja', kwargs={'naloga_id': self.naloga.pk})

        response = c.post(url, {
            'datoteka': testna_datoteka,
            'opomba': 'Prva oddaja'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        oddaja = OddajaNaloge.objects.filter(naloga=self.naloga, ucenec=self.ucenec).first()
        self.assertIsNotNone(oddaja)

        # Preveri poimenovanje datoteke: „Priimek Ime – Naslov naloge.končnica“
        pricakovano_ime = "Novak Janez – Domača naloga 1.txt"
        dejansko_ime = os.path.basename(oddaja.datoteka.name)
        self.assertEqual(dejansko_ime, pricakovano_ime)

    def test_ponovna_oddaja_zahteva_potrditev(self):
        """
        Preveri, da ponovna oddaja zahteva potrditev učenca pred prepisom datoteke.
        """
        c = Client()
        c.login(username='dijak1', password='geslo_dijak_123')

        # 1. Prva oddaja
        datoteka1 = SimpleUploadedFile("resitev1.pdf", b"Prva verzija")
        url = reverse('ucenec_naloga_oddaja', kwargs={'naloga_id': self.naloga.pk})
        c.post(url, {'datoteka': datoteka1}, follow=True)

        # 2. Poskus ponovne oddaje BREZ potrditve prepisa
        datoteka2 = SimpleUploadedFile("resitev2.pdf", b"Druga verzija")
        response = c.post(url, {
            'datoteka': datoteka2,
            'potrditev_prepisa': False
        })
        # Obrazec mora zavrniti oddajo z napako
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('potrditev_prepisa', response.context['form'].errors)

        # 3. Ponovna oddaja Z potrditvijo prepisa
        datoteka3 = SimpleUploadedFile("resitev3.pdf", b"Tretja verzija")
        response_ok = c.post(url, {
            'datoteka': datoteka3,
            'potrditev_prepisa': True
        }, follow=True)
        self.assertEqual(response_ok.status_code, 200)

        # Še vedno mora biti natančno ena oddaja za tega učenca in to nalogo
        oddaje = OddajaNaloge.objects.filter(naloga=self.naloga, ucenec=self.ucenec)
        self.assertEqual(oddaje.count(), 1)
        oddaja = oddaje.first()
        pricakovano_ime = "Novak Janez – Domača naloga 1.pdf"
        self.assertEqual(os.path.basename(oddaja.datoteka.name), pricakovano_ime)

    def test_ucitelj_dostop_do_gradiv(self):
        """Preveri, da učitelj lahko nalaga gradiva le za predmete, ki jih poučuje."""
        c = Client()
        c.login(username='profesor2', password='geslo_prof_123')

        # Profesor 2 poučuje predmet 1, ne pa predmeta 2
        testna_datoteka = SimpleUploadedFile("snov1.pdf", b"Predavanje 1")
        url_dovoljeno = reverse('ucitelj_gradivo_dodaj', kwargs={'predmet_id': self.predmet1.pk})
        res_dovoljeno = c.post(url_dovoljeno, {
            'naslov': 'Predavanje 1',
            'opis': 'Osnove',
            'datoteka': testna_datoteka
        }, follow=True)
        self.assertEqual(res_dovoljeno.status_code, 200)
        self.assertTrue(Gradivo.objects.filter(predmet=self.predmet1, naslov='Predavanje 1').exists())

        # Poskus nalaganja za predmet 2, ki ga ne poučuje
        url_zavrnjeno = reverse('ucitelj_gradivo_dodaj', kwargs={'predmet_id': self.predmet2.pk})
        res_zavrnjeno = c.get(url_zavrnjeno, follow=True)
        # Preusmerjen z opozorilom
        self.assertRedirects(res_zavrnjeno, reverse('ucitelj_nadzorna_plosca'))


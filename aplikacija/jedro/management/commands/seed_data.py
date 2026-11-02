import os
import random
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils import timezone
from jedro.models import Uporabnik
from solski_sistem.models import Predmet, Gradivo, Naloga, OddajaNaloge

class Command(BaseCommand):
    help = "Napolni bazo z zahtevanimi začetnimi podatki (10+ predmetov, 20+ učiteljev, 100+ učencev, gradiva, naloge)."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Pričetek polnjenja baze s podatki..."))

        # 1. Administrator (Superuser)
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@sola.si')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')

        admin_user, created = Uporabnik.objects.get_or_create(
            username=admin_username,
            defaults={
                'first_name': 'Sistemski',
                'last_name': 'Administrator',
                'email': admin_email,
                'vloga': Uporabnik.Vloga.ADMINISTRATOR,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password(admin_password)
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f"Ustvarjen administrator: {admin_username} / {admin_password}"))
        else:
            self.stdout.write(self.style.WARNING(f"Administrator {admin_username} že obstaja."))

        # 2. Predmeti (najmanj 10 zahtevanih -> ustvarimo 12 predmetov)
        predmeti_podatki = [
            ("Razvoj programskih sistemov", "RPS", "Osnove razvoja obsežnih programskih sistemov, kontejnerizacija, CI/CD in orodja.", 3),
            ("Podatkovne baze", "PB", "Relacijski podatkovni modeli, SQL, normalizacija in upravljanje podatkovnih baz.", 2),
            ("Spletno programiranje", "SP", "Sodobne spletne tehnologije, HTML5, CSS3, JavaScript in zaledna ogrodja.", 2),
            ("Računalniška omrežja", "RO", "Mrežni protokoli, TCP/IP, usmerjanje in varnost v omrežjih.", 3),
            ("Matematika", "MAT", "Linearna algebra, diferencialni in integralni račun ter verjetnost.", 1),
            ("Slovenščina", "SLO", "Slovenski jezik, slovnica, esejistika in književnost.", 1),
            ("Angleščina", "ANG", "Strokovna in splošna angleščina za inženirje in razvijalce.", 1),
            ("Fizika", "FIZ", "Klasična mehanika, termodinamika, elektromagnetizem in nihanje.", 2),
            ("Informatika in algoritmi", "ALG", "Podatkovne strukture, časovna zahtevnost in napredni algoritmi.", 1),
            ("Operacijski sistemi", "OS", "Procesi, niti, pomnilniško upravljanje in Linux lupina.", 2),
            ("Informacijska varnost", "IV", "Kriptografija, napadi, varnostne ranljivosti in zaščita sistemov.", 3),
            ("Umetna inteligenca", "UI", "Osnove strojnega učenja, nevronske mreže in podatkovno rudarjenje.", 4),
        ]

        ustvarjeni_predmeti = []
        for naziv, koda, opis, letnik in predmeti_podatki:
            p, created = Predmet.objects.get_or_create(
                koda=koda,
                defaults={'naziv': naziv, 'opis': opis, 'letnik': letnik}
            )
            ustvarjeni_predmeti.append(p)

        self.stdout.write(self.style.SUCCESS(f"Skupno predmetov v bazi: {len(ustvarjeni_predmeti)} (zahteva: vsaj 10)"))

        # 3. Učitelji (najmanj 20 zahtevanih -> ustvarimo 22 učiteljev)
        # Zahteva: "nekateri predmeti morajo imeti več učiteljev, nekateri učitelji pa morajo poučevati več predmetov"
        ucitelji_imena = [
            ("Janez", "Novak", "janez.novak@sola.si"),
            ("Maja", "Horvat", "maja.horvat@sola.si"),
            ("Peter", "Kovač", "peter.kovac@sola.si"),
            ("Ana", "Krajnc", "ana.krajnc@sola.si"),
            ("Marko", "Zupan", "marko.zupan@sola.si"),
            ("Mojca", "Potočnik", "mojca.potocnik@sola.si"),
            ("Luka", "Mlakar", "luka.mlakar@sola.si"),
            ("Nina", "Vidmar", "nina.vidmar@sola.si"),
            ("Andrej", "Kos", "andrej.kos@sola.si"),
            ("Katja", "Golob", "katja.golob@sola.si"),
            ("Boštjan", "Turk", "bostjan.turk@sola.si"),
            ("Simona", "Božič", "simona.bozic@sola.si"),
            ("Matjaž", "Zorko", "matjaz.zorko@sola.si"),
            ("Tanja", "Kralj", "tanja.kralj@sola.si"),
            ("Gregor", "Sever", "gregor.sever@sola.si"),
            ("Irena", "Hribar", "irena.hribar@sola.si"),
            ("Tomaž", "Bizjak", "tomaz.bizjak@sola.si"),
            ("Petra", "Kotnik", "petra.kotnik@sola.si"),
            ("Rok", "Jarc", "rok.jarc@sola.si"),
            ("Eva", "Uršič", "eva.ursic@sola.si"),
            ("Dejan", "Gomboc", "dejan.gomboc@sola.si"),
            ("Barbara", "Rupnik", "barbara.rupnik@sola.si"),
        ]

        ustvarjeni_ucitelji = []
        for i, (ime, priimek, email) in enumerate(ucitelji_imena, start=1):
            username = f"ucitelj{i}"
            u, created = Uporabnik.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': ime,
                    'last_name': priimek,
                    'email': email,
                    'vloga': Uporabnik.Vloga.UCITELJ,
                    'telefon': f"040 {random.randint(100, 999)} {random.randint(100, 999)}",
                }
            )
            if created:
                u.set_password("ucitelj123")
                u.save()
            ustvarjeni_ucitelji.append(u)

        # Dodeljevanje predmetov učiteljem (učitelji poučujejo 1 do 3 predmete, več učiteljev na predmet)
        # Vsakemu predmetu zagotovimo 1 ali 2 učitelja, RPS in PB imata po 3 učitelje
        for idx, u in enumerate(ustvarjeni_ucitelji):
            # Ciklično dodelimo predmete tako, da imajo nekateri več predmetov
            dodeljeni = [ustvarjeni_predmeti[idx % len(ustvarjeni_predmeti)]]
            if idx % 2 == 0:
                dodeljeni.append(ustvarjeni_predmeti[(idx + 3) % len(ustvarjeni_predmeti)])
            if idx % 5 == 0:
                dodeljeni.append(ustvarjeni_predmeti[(idx + 7) % len(ustvarjeni_predmeti)])
            u.poucuje_predmete.set(dodeljeni)

        self.stdout.write(self.style.SUCCESS(f"Skupno učiteljev v bazi: {len(ustvarjeni_ucitelji)} (zahteva: vsaj 20)"))

        # 4. Učenci (najmanj 100 zahtevanih -> ustvarimo 105 učencev)
        # Zahteva: "vsak učenec mora obiskovati več kot en predmet"
        slovenska_imena = [
            "Luka", "Nik", "Filip", "Jakob", "Jan", "Žan", "Tim", "David", "Matic", "Jaka",
            "Mark", "Liam", "Lovro", "Miha", "Gal", "Vid", "Anže", "Aleks", "Tine", "Patrik",
            "Mia", "Hana", "Zala", "Lara", "Sara", "Nika", "Eva", "Ema", "Tjaša", "Manca",
            "Kaja", "Lana", "Ajda", "Lea", "Neža", "Pia", "Zoja", "Julija", "Klara", "Tinkara"
        ]
        slovenski_priimki = [
            "Novak", "Horvat", "Kovačič", "Krajnc", "Zupančič", "Potočnik", "Kovač", "Mlakar",
            "Kos", "Vidmar", "Golob", "Turk", "Kralj", "Božič", "Zorko", "Sever", "Hribar",
            "Bizjak", "Kotnik", "Jarc", "Uršič", "Gomboc", "Rupnik", "Oblak", "Černe", "Rozman"
        ]

        random.seed(42)  # Za ponovljivost podatkov
        ustvarjeni_ucenci = []
        for i in range(1, 106):
            username = f"ucenec{i}"
            ime = random.choice(slovenska_imena)
            priimek = random.choice(slovenski_priimki)
            email = f"{ime.lower()}.{priimek.lower()}{i}@dijak.sola.si"

            ucenec, created = Uporabnik.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': ime,
                    'last_name': priimek,
                    'email': email,
                    'vloga': Uporabnik.Vloga.UCENEC,
                    'telefon': f"051 {random.randint(100, 999)} {random.randint(100, 999)}",
                    'naslov': f"Slovenska ulica {random.randint(1, 120)}, Ljubljana",
                }
            )
            if created:
                ucenec.set_password("ucenec123")
                ucenec.save()

            # Vsak učenec obiskuje od 3 do 5 naključnih predmetov (zahteva: več kot en predmet!)
            st_predmetov = random.randint(3, 5)
            izbrani = random.sample(ustvarjeni_predmeti, st_predmetov)
            ucenec.obiskuje_predmete.set(izbrani)
            ustvarjeni_ucenci.append(ucenec)

        self.stdout.write(self.style.SUCCESS(f"Skupno učencev v bazi: {len(ustvarjeni_ucenci)} (zahteva: vsaj 100)"))

        # 5. Vzorčna gradiva in naloge za vsak predmet
        for p in ustvarjeni_predmeti:
            ucitelji = list(p.ucitelji.all())
            if not ucitelji:
                continue
            nosilec = ucitelji[0]

            # Gradivo
            g_naslov = f"Uvodno učno gradivo in navodila za {p.naziv}"
            if not Gradivo.objects.filter(predmet=p, naslov=g_naslov).exists():
                gradivo = Gradivo(
                    predmet=p,
                    avtor=nosilec,
                    naslov=g_naslov,
                    opis=f"Uvodne prosojnice in literatura pri predmetu {p.naziv}."
                )
                vsebina = f"Gradivo za predmet {p.naziv} ({p.koda})\nAvtor: {nosilec.polno_ime}\nŠolsko leto 2026/2027\n\n1. Uvod\n2. Pregled tem\n3. Priporočena literatura".encode('utf-8')
                gradivo.datoteka.save(f"uvod_{p.koda.lower()}.txt", ContentFile(vsebina), save=True)

            # Naloga
            n_naslov = f"Domača naloga 1 – {p.koda}"
            if not Naloga.objects.filter(predmet=p, naslov=n_naslov).exists():
                naloga = Naloga.objects.create(
                    predmet=p,
                    avtor=nosilec,
                    naslov=n_naslov,
                    navodila=f"Pripravite rešitev praktičnih nalog iz prvega sklopa predmeta {p.naziv}. Oddajte poročilo v formatu PDF ali TXT.",
                    rok_oddaje=timezone.now() + timezone.timedelta(days=14)
                )

                # Ustvarimo še nekaj vzorčnih oddaj učencev s pravilnim poimenovanjem
                # „Priimek Ime – Naslov naloge“ z ustrezno končnico
                vpisani = list(p.ucenci.all()[:3])
                for v_ucenec in vpisani:
                    if not OddajaNaloge.objects.filter(naloga=naloga, ucenec=v_ucenec).exists():
                        oddaja = OddajaNaloge(
                            naloga=naloga,
                            ucenec=v_ucenec,
                            opomba="Oddajam pravočasno po navodilih."
                        )
                        vsebina_oddaje = f"Rešitev naloge {naloga.naslov}\nUčenec: {v_ucenec.polno_ime}\nDatum oddaje: {timezone.now()}\n\nNaloga uspešno rešena.".encode('utf-8')
                        # Shranimo z originalnim imenom, upload_to pot_za_oddajo_naloge bo poskrbel za pravo ime
                        oddaja.datoteka.save("oddaja.txt", ContentFile(vsebina_oddaje), save=True)

        self.stdout.write(self.style.SUCCESS("Uspešno ustvarjena vzorčna gradiva, naloge in oddaje!"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("PRIJAVNI PODATKI ZA TESTIRANJE:"))
        self.stdout.write(self.style.SUCCESS(f"  ADMINISTRATOR: uporabnik '{admin_username}', geslo '{admin_password}'"))
        self.stdout.write(self.style.SUCCESS("  UČITELJI:      uporabniki 'ucitelj1' do 'ucitelj22', geslo 'ucitelj123'"))
        self.stdout.write(self.style.SUCCESS("  UČENCI:        uporabniki 'ucenec1' do 'ucenec105', geslo 'ucenec123'"))
        self.stdout.write(self.style.SUCCESS("=" * 60))


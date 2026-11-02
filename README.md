# E-Šola – Šolski informacijski sistem za delo na daljavo

Sodobna, varna in razširljiva spletna aplikacija za podporo šolskemu delu na daljavo, razvita v okviru predmeta **Razvoj programskih sistemov (RPS)**.

Aplikacija teče v ločenih, medsebojno povezanih Docker vsebnikih ter v celoti izpolnjuje vse tehnične in vsebinske zahteve projektne naloge.

---

## Kazalo vsebine
1. [Utemeljitev izbire orodij in tehnologij](#1-utemeljitev-izbire-orodij-in-tehnologij)
2. [Arhitektura sistema in vsebniki (Docker)](#2-arhitektura-sistema-in-vsebniki-docker)
3. [Vsebinske zahteve in funkcionalnosti](#3-vsebinske-zahteve-in-funkcionalnosti)
   - [Administrator](#administrator)
   - [Učitelj](#učitelj)
   - [Učenec](#učenec)
4. [Struktura podatkovnega modela](#4-struktura-podatkovnega-modela)
5. [Začetni podatki in sejalnik (Seed data)](#5-začetni-podatki-in-sejalnik-seed-data)
6. [Navodila za zagon s sistemom Docker (Priporočeno)](#6-navodila-za-zagon-s-sistemom-docker-priporočeno)
7. [Navodila za lokalni zagon brez Dockerja](#7-navodila-za-lokalni-zagon-brez-dockerja)
8. [Prijavni podatki testnih uporabnikov](#8-prijavni-podatki-testnih-uporabnikov)
9. [Git in GitHub delotok ter sodelovanje v skupini](#9-git-in-github-delotok-ter-sodelovanje-v-skupini)
10. [Produkcijska namestitev na Linux strežnik in HTTPS (Let's Encrypt)](#10-produkcijska-namestitev-na-linux-strežnik-in-https-lets-encrypt)

---

## 1. Utemeljitev izbire orodij in tehnologij

V skladu z navodili projektne naloge smo znotraj posameznih kategorij izbrali sodobna, zanesljiva in industrijsko uveljavljena orodja:

| Kategorija | Izbrano orodje | Utemeljitev izbire |
|---|---|---|
| **Nadzor različic** | **Git & GitHub** | Industrijski standard za sledenje spremembam, vodenje vej (`feature/*`), izdelavo vlečnih zahtevkov (*Pull Requests*), pregled kode (*Code Review*) ter evidentiranje in sledenje napakam prek *GitHub Issues*. |
| **Vsebniki (Kontejnerizacija)** | **Docker & Docker Compose** | Omogoča izolacijo storitev (`baza`, `aplikacija`, `spletni_streznik`) v ločenih, medsebojno povezanih vsebnikih z lastnimi volumni in interno mrežo. Zagotavlja enako delovanje na razvojnih in produkcijskih okoljih (*"works on my machine"* problem rešen). |
| **Operacijski sistem strežnika** | **Linux (Ubuntu Server 24.04 LTS)** | Stabilen, varen in široko podprt strežniški operacijski sistem z odlično podporo za Docker ter minimalno porabo sistemskih virov. |
| **Podatkovna baza (SUPB)** | **PostgreSQL 16 (v ločenem vsebniku)** | Robusten relacijski sistem za upravljanje podatkovnih baz (ACID skladnost, podpora za kompleksne relacije med učitelji, predmeti in učenci, zanesljivo shranjevanje v Docker volumnu). |
| **Razvojno ogrodje** | **Python z Django 5.1** | Vrhunsko spletno ogrodje z vgrajenim zanesljivim ORM, naprednim avtentikacijskim sistemom, zaščito pred CSRF/XSS napadi ter enostavnim seanjem podatkov. |
| **Spletni strežnik / Obrnjeni posrednik** | **Nginx** | Izjemno učinkovit obratni posrednik (*reverse proxy*), ki posreduje klice aplikacijskemu strežniku Gunicorn, samostojno in hitro servira statične ter medijske datoteke ter poskrbi za šifriran prenos HTTPS. |
| **Šifrirana povezava** | **Let's Encrypt (Certbot)** | Avtomatizirana, priznana in brezplačna digitalna potrdila za javno domeno, ki omogočajo varno šifrirano povezavo HTTPS (TLS). |
| **Shranjevanje gesel** | **PBKDF2 z SHA-256 (Django default) / Argon2 / BCrypt** | Gesla se **nikoli ne shranjujejo v čistem besedilu** (*plaintext*). Uporablja se kriptografsko zgoščevanje (hashing) z več deset tisoč iteracijami in naključno soljo (*salt*). |

---

## 2. Arhitektura sistema in vsebniki (Docker)

Sistem je sestavljen iz treh samostojnih storitev, definiranih v `docker-compose.yml`:

```
               [ Odjemalec / Spletni brskalnik ]
                              │
                    Vrata (Port) 80 / 443
                              ▼
         ┌────────────────────────────────────────┐
         │     Vsebnik: spletni_streznik (Nginx)  │
         │  - Reverzni posrednik (reverse proxy)  │
         │  - Serviranje /static/ in /media/      │
         └────────────────────┬───────────────────┘
                              │
                    proxy_pass│ sola_mreza:8000
                              ▼
         ┌────────────────────────────────────────┐
         │     Vsebnik: aplikacija (Django)       │
         │  - WSGI strežnik Gunicorn (3 delavci)  │
         │  - Avtentikacija, poslovna logika      │
         └────────────────────┬───────────────────┘
                              │
                  psycopg / SQL│ sola_mreza:5432
                              ▼
         ┌────────────────────────────────────────┐
         │       Vsebnik: baza (PostgreSQL 16)    │
         │  - Trajni volumen: baza_podatki        │
         └────────────────────────────────────────┘
```

1. **`baza` (`postgres:16-alpine`)**:
   - Skrbi za shranjevanje vseh tabel, relacij in uporabnikov.
   - Podatki se trajno hranijo v volumnu `baza_podatki`.
   - Vsebuje `healthcheck`, s katerim preostale storitve varno počakajo na popolno pripravljenost baze.
2. **`aplikacija` (`python:3.12-slim`)**:
   - Vsebuje celotno Django aplikacijo, ki jo poganja produkcijski WSGI strežnik **Gunicorn**.
   - Skripta `entrypoint.sh` ob zagonu samodejno počaka bazo, izvede migracije, zbere statiko in zažene sejalnik začetnih podatkov (`seed_data`).
3. **`spletni_streznik` (`nginx:alpine`)**:
   - Obrnjeni posrednik, ki posluša na vratih 80 (in pripravljeno 443) ter usmerja zahteve.
   - Statične datoteke (`/static/`) in medijske datoteke (`/media/`) servira neposredno iz skupnih volumnov, kar razbremeni Django aplikacijo.

---

## 3. Vsebinske zahteve in funkcionalnosti

Aplikacija podpira tri ločene vloge z namenskimi uporabniškimi vmesniki in strogim nadzorom pravic:

### Administrator
- **Upravljanje predmetov (najmanj 10):**
  - Vpis novega predmeta (naziv, kratica/koda, opis, letnik).
  - Popravljanje obstoječih podatkov predmeta.
  - Varno brisanje predmeta s potrditvenim dialogom.
- **Upravljanje učiteljev (najmanj 20):**
  - Vpis novih učiteljev, urejanje podatkov in brisanje.
  - **Dodeljevanje predmetov:** Možnost izbire, katere predmete posamezni učitelj poučuje. Sistem omogoča, da imajo nekateri predmeti več učiteljev, posamezni učitelj pa lahko poučuje več predmetov (*Many-to-Many* relacija).
- **Upravljanje učencev (najmanj 100):**
  - Vpis novih učencev, urejanje profilov in brisanje.
  - **Vpis v predmete:** Določanje, katere predmete učenec obiskuje. Sistem z validacijo zagotavlja, da mora vsak učenec obiskovati več kot en predmet (najmanj 2 predmeta).
- **Neposreden vnos v bazo:** Podatke je mogoče vnesti neposredno v bazo prek sejalnika (`seed_data`) ali SQL skript, ne glede na to pa spletna aplikacija omogoča polno CRUD funkcionalnost prek grafičnega vmesnika.

### Učitelj
- **Prikaz predmetov:** Učitelj na svoji nadzorni plošči vidi izključno predmete, ki jih dejansko poučuje.
- **Upravljanje gradiv:**
  - Nalaganje učnih gradiv (datoteke PDF, Word, prosojnice, arhivske datoteke itd.) za izbrani predmet.
  - Brisanje gradiv (samo za predmete, ki jih dejansko poučuje; koda preprečuje nepooblaščeno brisanje tujih gradiv).
- **Objavljanje nalog:** Učitelj lahko za svoje predmete ustvari domače naloge z navodili in rokom za oddajo.
- **Pregledovanje oddanih nalog:** Učitelj ima za vsako nalogo podroben pregled vseh oddaj (ime in priimek učenca, točen čas oddaje, opomba ter neposreden prenos oddane datoteke).

### Učenec
- **Registracija in profil:**
  - Možnost samostojne registracije novega učenca prek spletnega obrazca.
  - Možnost urejanja lastnega profila (ime, priimek, e-pošta, telefonska številka, naslov, geslo).
- **Vpogled v gradiva:**
  - Pregled in prenos vseh naloženih gradiv za predmete, na katere je učenec vpisan.
- **Oddaja nalog:**
  - Možnost oddaje nalog pri predmetih s svojega seznama.
  - **Poimenovanje datoteke na strežniku:** Sistem datoteko na strežniku avtomatsko shrani pod natančno zahtevano obliko:
    `Priimek Ime – Naslov naloge.končnica` (npr. `Novak Janez – Domača naloga 1.pdf`).
  - **Varno prepisovanje prejšnje oddaje:** Če je učenec nalogo že oddal, ga sistem na to opozori. Ponovna oddaja povozi (prepiše) prejšnjo datoteko na strežniku **šele potem, ko učenec to izrecno potrdi s potrditvenim poljem**.

---

## 4. Struktura podatkovnega modela

```
    ┌───────────────────────────────────┐
    │          jedro.Uporabnik          │
    │  (AbstractUser + vloga + profil)  │
    └──────┬─────────────────────┬──────┘
           │ (poučuje)           │ (obiskuje)
           │ ManyToMany          │ ManyToMany
           ▼                     ▼
    ┌───────────────────────────────────┐
    │       solski_sistem.Predmet       │
    │  (naziv, koda, opis, letnik)      │
    └──────┬─────────────────────┬──────┘
           │ 1:N                 │ 1:N
           ▼                     ▼
    ┌─────────────┐       ┌─────────────┐
    │   Gradivo   │       │   Naloga    │
    └─────────────┘       └──────┬──────┘
                                 │ 1:N
                                 ▼
                          ┌─────────────┐
                          │ OddajaNaloge│ (unique: naloga + učenec)
                          └─────────────┘
```

---

## 5. Začetni podatki in sejalnik (Seed data)

Aplikacija vključuje ukaz `python manage.py seed_data`, ki ob prvem zagonu avtomatsko generira bogat nabor podatkov, s čimer v celoti zadosti in preseže zahteve iz navodil:
- **1 Administrator:** uporabniško ime `admin`, geslo `admin123`.
- **12 Predmetov:** RPS, PB, SP, RO, MAT, SLO, ANG, FIZ, ALG, OS, IV, UI (zahteva: vsaj 10).
- **22 Učiteljev:** `ucitelj1` do `ucitelj22`, geslo `ucitelj123` (zahteva: vsaj 20). Učitelji imajo dodeljene predmete, pri čemer imajo nekateri predmeti več učiteljev, nekateri učitelji pa poučujejo več predmetov.
- **105 Učencev:** `ucenec1` do `ucenec105`, geslo `ucenec123` (zahteva: vsaj 100). Vsak učenec je vpisan v 3 do 5 predmetov (zahteva: več kot en predmet).
- **Vzorčna gradiva, naloge in oddaje:** Vsak predmet ima pripravljeno uvodno učno gradivo in nalogo ter vzorčne oddaje učencev s pravilnim poimenovanjem datotek.

---

## 6. Navodila za zagon s sistemom Docker (Priporočeno)

### Predpogoji
- Nameščen [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/macOS) ali Docker Engine + Docker Compose (Linux).

### Koraki za zagon
1. Odprite terminal v mapi projekta (`d:\RPS_Naloga1`).
2. Zaženite ukaz:
   ```bash
   docker compose up --build
   ```
   *(Na sistemu Windows lahko preprosto dvokliknete datoteko `run_docker.bat`)*
3. Docker bo samodejno:
   - Zgradil slike vsebnikov.
   - Zagnal bazo podatkov PostgreSQL 16 in preveril njeno zdravje (`healthcheck`).
   - Zagnal aplikacijo Django ter avtomatsko izvedel migracije, zbral statiko in napolnil bazo s podatki (`seed_data`).
   - Zagnal Nginx spletni strežnik na vratih **80**.
4. Odprite spletni brskalnik in pojdite na:
   **`http://localhost`** (ali `http://127.0.0.1`)

Za zaustavitev pritisnite `Ctrl + C` ali v novem oknu zaženite:
```bash
docker compose down
```

---

## 7. Navodila za lokalni zagon brez Dockerja

Če želite aplikacijo pognati neposredno v lokalnem Python okolju (uporabi se lokalna SQLite baza ali lokalni PostgreSQL):

1. Premaknite se v mapo `aplikacija`:
   ```bash
   cd aplikacija
   ```
2. Ustvarite in aktivirajte virtualno okolje:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux / macOS:
   source venv/bin/activate
   ```
3. Namestite odvisnosti:
   ```bash
   pip install -r requirements.txt
   ```
4. Izvedite migracije in napolnite bazo:
   ```bash
   python manage.py makemigrations jedro solski_sistem
   python manage.py migrate
   python manage.py seed_data
   ```
5. Zaženite razvojni strežnik:
   ```bash
   python manage.py runserver 8000
   ```
6. Aplikacija je dostopna na: **`http://127.0.0.1:8000`**

---

## 8. Prijavni podatki testnih uporabnikov

Za lažje preizkušanje in ocenjevanje so na prijavni strani na voljo gumbi za hiter vnos prijavnih podatkov:

| Vloga | Uporabniško ime | Geslo | Opombe |
|---|---|---|---|
| **Administrator** | `admin` | `admin123` | Popoln dostop do vseh predmetov, učiteljev in učencev. |
| **Učitelj 1** | `ucitelj1` | `ucitelj123` | Profesor Janez Novak (poučuje RPS, RO itd.). |
| **Učitelj 2** | `ucitelj2` | `ucitelj123` | Profesorica Maja Horvat. |
| ... | `ucitelj3` do `ucitelj22` | `ucitelj123` | Preostalih 20 profesorjev. |
| **Učenec 1** | `ucenec1` | `ucenec123` | Vpisan v več predmetov, možnost oddaje nalog. |
| **Učenec 2** | `ucenec2` | `ucenec123` | Vpisan v več predmetov. |
| ... | `ucenec3` do `ucenec105`| `ucenec123` | Preostalih 103 učencev. |

---

## 9. Git in GitHub delotok ter sodelovanje v skupini

V skladu z navodili za sodelovalni razvoj skupina uporablja naslednji standardni delotok:

### Struktura vej (Branching strategy)
- `main` – Stabilna produkcijska veja. Neposredno potiskanje (`push`) na `main` je onemogočeno.
- `develop` – Skupna integracijska veja za tekoče razvoje.
- `feature/<naziv-funkcionalnosti>` – Namenske veje za posamezne naloge (npr. `feature/oddaja-nalog`, `feature/docker-compose`, `feature/crud-predmeti`).

### Delotok za posamezno funkcionalnost
1. Ustvarite novo vejo iz `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/oddaja-nalog
   ```
2. Opravite spremembe in jih potrdite z jasnimi sporočili:
   ```bash
   git add .
   git commit -m "feat: implementirana oddaja nalog s potrditvijo prepisa datoteke"
   ```
3. Potisnite vejo na GitHub:
   ```bash
   git push -u origin feature/oddaja-nalog
   ```
4. Na GitHubu odprite **Pull Request (PR)** proti veji `develop`.
5. Vsaj en drug član skupine mora opraviti **pregled kode (Code Review)** in odobriti PR pred združitvijo (*merge*).
6. Za sledenje hroščem in nalogam se uporabljajo **GitHub Issues** na spletnem vmesniku GitHuba.

---

## 10. Produkcijska namestitev na Linux strežnik in HTTPS (Let's Encrypt)

Za postavitev na javno dostopnem Linux strežniku (npr. Ubuntu Server 24.04 LTS):

1. **Namestitev orodij na strežniku:**
   ```bash
   sudo apt update && sudo apt install -y docker.io docker-compose-v2 certbot
   ```
2. **Kloniranje repozitorija in nastavitev `.env`:**
   ```bash
   git clone <URL_VASEGA_GITHUB_REPOZITORIJA> /opt/sola_is
   cd /opt/sola_is
   cp .env.example .env
   # V .env nastavite DEBUG=False, varno SECRET_KEY in domeno v ALLOWED_HOSTS
   ```
3. **Pridobitev brezplačnega certifikata Let's Encrypt prek Certbot:**
   ```bash
   sudo certbot certonly --standalone -d vasa-domena.si
   ```
4. **Kopiranje certifikatov v mapo `nginx/ssl/`:**
   ```bash
   sudo cp /etc/letsencrypt/live/vasa-domena.si/fullchain.pem nginx/ssl/cert.pem
   sudo cp /etc/letsencrypt/live/vasa-domena.si/privkey.pem nginx/ssl/key.pem
   ```
5. **Vklop SSL v Nginx konfiguraciji:**
   V datoteki `nginx/nginx.conf` odkomentirajte SSL blok (vrata 443) z `ssl_certificate /etc/nginx/ssl/cert.pem;` in `ssl_certificate_key /etc/nginx/ssl/key.pem;`.
6. **Zagon z Docker Compose:**
   ```bash
   docker compose up -d
   ```
Aplikacija je sedaj varno dostopna preko šifriranega protokola HTTPS na vaši javni domeni.


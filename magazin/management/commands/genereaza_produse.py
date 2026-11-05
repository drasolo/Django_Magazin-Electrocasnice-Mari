"""Task-ul bonus din laboratorul 4: comenzi INSERT cu produse aleatoare, dar valide.

Rulare, din folderul proiectului:
    .venv\\Scripts\\python manage.py genereaza_produse --numar 40
    "C:\\Program Files\\PostgreSQL\\18\\bin\\psql.exe" -U magazin -d electrocasnice -f date\\produse_generate.sql

Produsele primesc categorii și branduri care există deja în baza de date, deci întâi
se introduc acestea din admin. Fiecare produs trece prin full_clean() înainte să fie
scris, adică prin aceleași verificări ca formularul din admin: câmpuri, choices,
unicitatea codului de model și constrângerile cu models.Q.
"""

import random
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from magazin.models import Brand, Categorie, Produs

# Specificații plauzibile pentru fiecare fel de categorie. Cheia e un fragment din numele
# categoriei (fără terminație: "cupt" prinde și "Cuptoare", și "Cuptor"). Ordinea contează:
# "Uscătoare de rufe" conține și "rufe", deci "usc" e verificat înaintea lui "rufe".
PROFILURI = [
    ("vase", {
        "prefix": "MV", "nume": ["Mașină de spălat vase {cap} seturi", "Mașină de spălat vase {lat} cm"],
        "pret": (1200, 4500), "latime": [448, 450, 598, 600], "inaltime": (815, 850), "adancime": (550, 600),
        "capacitate": (9, 16), "clase": "ABCDE", "incorporabil": 0.4,
        "taguri": ["AutoOpen", "Program Eco", "Sertar tacâmuri", "Senzor murdărie", "WiFi", "Silențioasă"],
    }),
    ("usc", {
        "prefix": "US", "nume": ["Uscător de rufe {cap} kg"],
        "pret": (1500, 4800), "latime": [595, 596, 600], "inaltime": (845, 850), "adancime": (600, 660),
        "capacitate": (7, 10), "clase": "ABC", "incorporabil": 0.0,
        "taguri": ["Pompă de căldură", "Senzor umiditate", "Anti-șifonare", "WiFi", "Condensare"],
    }),
    ("rufe", {
        "prefix": "MS", "nume": ["Mașină de spălat rufe {cap} kg"],
        "pret": (1100, 4200), "latime": [595, 597, 600], "inaltime": (845, 850), "adancime": (450, 650),
        "capacitate": (6, 11), "clase": "ABC", "incorporabil": 0.1,
        "taguri": ["Inverter", "Abur", "WiFi", "Program rapid", "Încărcare frontală", "Anti-alergii"],
    }),
    ("frigid", {
        "prefix": "FR", "nume": ["Combină frigorifică {cap} l", "Frigider cu o ușă {cap} l"],
        "pret": (1400, 7500), "latime": [550, 595, 600, 700, 912], "inaltime": (1450, 2030), "adancime": (550, 720),
        "capacitate": (220, 640), "clase": "ABCDEF", "incorporabil": 0.2,
        "taguri": ["NoFrost", "Inverter", "WiFi", "Zona fresh", "Dozator apă", "MultiAirflow"],
    }),
    ("cupt", {
        "prefix": "CU", "nume": ["Cuptor electric încorporabil {cap} l"],
        "pret": (900, 5200), "latime": [594, 595, 597], "inaltime": (590, 600), "adancime": (540, 570),
        "capacitate": (65, 80), "clase": "AB", "incorporabil": 1.0,
        "taguri": ["Aer cald", "Abur", "Autocurățare", "Pirolitic", "Sondă carne", "WiFi"],
    }),
    ("plit", {
        "prefix": "PL", "nume": ["Plită cu inducție {lat} cm", "Plită vitroceramică {lat} cm"],
        "pret": (700, 4000), "latime": [300, 590, 600, 800], "inaltime": (44, 60), "adancime": (500, 520),
        "capacitate": None, "clase": "", "incorporabil": 0.9,
        "taguri": ["Inducție", "Bridge", "Touch control", "Booster", "Blocare copii"],
    }),
    ("hot", {
        "prefix": "HO", "nume": ["Hotă decorativă {lat} cm", "Hotă telescopică {lat} cm"],
        "pret": (400, 3500), "latime": [598, 600, 898, 900], "inaltime": (180, 1000), "adancime": (280, 500),
        "capacitate": None, "clase": "ABCD", "incorporabil": 0.3,
        "taguri": ["LED", "Recirculare", "Senzor", "Silențioasă", "Telecomandă"],
    }),
]
# Pentru o categorie cu alt nume decât cele de mai sus
PROFIL_GENERAL = {
    "prefix": "EL", "nume": ["Aparat {lat} cm"],
    "pret": (500, 3000), "latime": [450, 600], "inaltime": (500, 1800), "adancime": (400, 650),
    "capacitate": None, "clase": "ABCD", "incorporabil": 0.2,
    "taguri": ["WiFi", "Eco", "Silențios"],
}
SERII = ["Basic", "Comfort", "Plus", "Premium", "Eco", "Pro"]

# Coloanele din tabel, în ordinea din comanda INSERT. imagine lipsește: rămâne NULL,
# iar site-ul afișează imaginea implicită.
COLOANE = [
    "nume", "cod_model", "categorie_id", "brand_id", "pret", "clasa_energetica",
    "latime", "inaltime", "adancime", "capacitate", "culoare", "incorporabil",
    "garantie_luni", "stoc", "taguri", "data_adaugare",
]


def profil_pentru(categorie):
    nume = categorie.nume.lower()
    for fragment, profil in PROFILURI:
        if fragment in nume:
            return profil
    return PROFIL_GENERAL


def literal_sql(valoare):
    """Valoarea Python scrisă ca literal SQL pentru PostgreSQL."""
    if valoare is None:
        return "NULL"
    if isinstance(valoare, bool):  # înainte de int, pentru că True e și int în Python
        return "TRUE" if valoare else "FALSE"
    if isinstance(valoare, (int, Decimal)):
        return str(valoare)
    if isinstance(valoare, list):
        if not valoare:
            return "'{}'"  # vectorul gol
        return "ARRAY[" + ", ".join(literal_sql(v) for v in valoare) + "]"
    if isinstance(valoare, datetime):
        return f"'{valoare.isoformat()}'"
    # Textul stă între apostrofuri, iar un apostrof din text se scrie dublat
    return "'" + str(valoare).replace("'", "''") + "'"


class Command(BaseCommand):
    help = "Generează comenzi INSERT cu produse aleatoare, dar valide, pentru tabelul de produse."

    def add_arguments(self, parser):
        parser.add_argument("--numar", type=int, default=40, help="Câte produse se generează (implicit 40).")
        parser.add_argument(
            "--fisier",
            default=str(settings.BASE_DIR / "date" / "produse_generate.sql"),
            help="Unde se scriu comenzile (implicit date/produse_generate.sql).",
        )
        parser.add_argument("--seed", type=int, help="Același seed dă aceleași produse.")

    def handle(self, *args, **options):
        if options["seed"] is not None:
            random.seed(options["seed"])

        # Doar categoriile care au deja produse. Așa categoria de test fără produse
        # (cerută de laboratorul 4 pentru meniu) rămâne goală.
        categorii = list(Categorie.objects.filter(produse__isnull=False).distinct())
        branduri = list(Brand.objects.all())
        if not categorii or not branduri:
            raise CommandError("Adaugă întâi din admin branduri și câteva produse, ca să existe categorii cu produse.")

        coduri_folosite = set(Produs.objects.values_list("cod_model", flat=True))
        comenzi = []
        acum = timezone.localtime()
        for _ in range(options["numar"]):
            produs = self.produs_aleator(random.choice(categorii), random.choice(branduri), coduri_folosite)
            # Aceleași verificări ca în formularul din admin. data_adaugare (auto_now_add)
            # nu e editabil, deci full_clean îl sare și îl completăm noi mai jos.
            try:
                produs.full_clean()
            except ValidationError as e:
                raise CommandError(f"Produsul generat {produs.cod_model} nu e valid: {e.messages}")
            produs.data_adaugare = acum - timedelta(days=random.randint(0, 120), minutes=random.randint(0, 1439))
            coduri_folosite.add(produs.cod_model)

            valori = ", ".join(literal_sql(getattr(produs, coloana)) for coloana in COLOANE)
            comenzi.append(f"INSERT INTO {Produs._meta.db_table} ({', '.join(COLOANE)}) VALUES ({valori});")

        fisier = Path(options["fisier"])
        fisier.parent.mkdir(parents=True, exist_ok=True)
        antet = [
            f"-- {len(comenzi)} produse generate de manage.py genereaza_produse, {acum:%d.%m.%Y %H:%M}",
            "-- Dacă o comandă eșuează, tranzacția nu se mai încheie cu COMMIT și nu se salvează nimic.",
            # psql pe Windows citește fișierul în codificarea consolei; așa diacriticele ajung corect
            "SET client_encoding = 'UTF8';",
            "BEGIN;",
        ]
        fisier.write_text("\n".join(antet + comenzi + ["COMMIT;", ""]), encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"Am scris {len(comenzi)} comenzi INSERT în {fisier}"))

    def produs_aleator(self, categorie, brand, coduri_folosite):
        profil = profil_pentru(categorie)
        latime = random.choice(profil["latime"])
        capacitate = random.randint(*profil["capacitate"]) if profil["capacitate"] else None

        cod = None
        while cod is None or cod in coduri_folosite:
            cod = f"{profil['prefix']}-{brand.nume[:2].upper()}-{random.randint(1000, 9999)}"

        # Un sfert dintre produse au stocul sub STOC_MIN, ca marcajul de stoc limitat să apară
        if random.random() < 0.25:
            stoc = random.randint(0, settings.STOC_MIN - 1)
        else:
            stoc = random.randint(settings.STOC_MIN, 40)

        sablon = random.choice(profil["nume"])
        return Produs(
            nume=f"{sablon.format(cap=capacitate, lat=round(latime / 10))} {random.choice(SERII)}",
            cod_model=cod,
            categorie=categorie,
            brand=brand,
            # prețuri care se termină în 9, ca în magazine: 1899, 2459
            pret=Decimal(random.randint(profil["pret"][0] // 10, profil["pret"][1] // 10) * 10 - 1),
            clasa_energetica=random.choice(profil["clase"]) if profil["clase"] else None,
            latime=latime,
            inaltime=random.randint(*profil["inaltime"]),
            adancime=random.randint(*profil["adancime"]),
            capacitate=capacitate,
            culoare=random.choice(Produs.Culoare.values),
            incorporabil=random.random() < profil["incorporabil"],
            garantie_luni=random.choice([24, 24, 24, 36, 60]),
            stoc=stoc,
            taguri=random.sample(profil["taguri"], k=random.randint(1, 3)),
        )

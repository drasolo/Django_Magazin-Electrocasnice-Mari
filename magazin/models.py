from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.urls import reverse

# Modelele urmează diagrama din docs/diagrama.png. Cheile primare (id_categorie,
# id_brand etc.) nu apar aici: Django creează singur câmpul id pentru fiecare model.


class Categorie(models.Model):
    """Grupează produsele: frigidere, mașini de spălat, hote etc."""

    class Unitate(models.TextChoices):
        LITRI = "l", "litri"
        KILOGRAME = "kg", "kilograme"
        SETURI = "seturi", "seturi de vase"

    # Numele e unic pentru că apare în adresa paginii: /magazin/categorii/Hote
    nume = models.CharField(
        max_length=50,
        unique=True,
        error_messages={"unique": "Există deja o categorie cu acest nume."},
    )
    descriere = models.TextField(null=True, blank=True)
    culoare = models.CharField(
        max_length=7,
        default="#1f5f8b",
        help_text="Cod hexazecimal, de exemplu #1f5f8b. Cu el se colorează categoria în paginile cu produse.",
    )
    sigla = models.CharField(
        "siglă",
        max_length=50,
        default="fa-solid fa-plug",
        help_text="Clasele unui icon FontAwesome, de exemplu fa-solid fa-snowflake (lista: fontawesome.com/icons).",
    )
    unitate_capacitate = models.CharField(
        "unitatea capacității",
        max_length=6,
        choices=Unitate.choices,
        null=True,
        blank=True,
        help_text="În ce se măsoară capacitatea produselor din categorie. Gol pentru categoriile fără capacitate, ca hotele.",
    )

    class Meta:
        verbose_name = "categorie"
        verbose_name_plural = "categorii"
        ordering = ["nume"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(culoare__regex=r"^#[0-9A-Fa-f]{6}$"),
                name="categorie_culoare_hex",
                violation_error_message="Culoarea se scrie ca #rrggbb, de exemplu #1f5f8b.",
            ),
        ]

    def __str__(self):
        return self.nume

    def get_absolute_url(self):
        # /magazin/categorii/Frigidere
        return reverse("categorie", args=[self.nume])


class Brand(models.Model):
    """Producătorul aparatelor."""

    nume = models.CharField(
        max_length=50,
        unique=True,
        error_messages={"unique": "Brandul există deja."},
    )
    tara_origine = models.CharField("țara de origine", max_length=50, null=True, blank=True)
    site_oficial = models.URLField(null=True, blank=True)
    an_infiintare = models.PositiveSmallIntegerField("anul înființării", null=True, blank=True)

    class Meta:
        verbose_name = "brand"
        verbose_name_plural = "branduri"
        ordering = ["nume"]
        constraints = [
            # Anul poate lipsi (NULL). Dacă e completat, nu poate fi mai vechi de 1800.
            models.CheckConstraint(
                condition=models.Q(an_infiintare__gte=1800) | models.Q(an_infiintare__isnull=True),
                name="brand_an_infiintare_valid",
                violation_error_message="Anul înființării nu poate fi înainte de 1800.",
            ),
        ]

    def __str__(self):
        return self.nume


class ServiciuAditional(models.Model):
    """Un serviciu care se cumpără împreună cu un produs: livrare, montaj, garanție extinsă."""

    nume = models.CharField(
        max_length=60,
        unique=True,
        error_messages={"unique": "Există deja un serviciu cu acest nume."},
    )
    descriere = models.TextField(null=True, blank=True)
    pret = models.DecimalField("preț (lei)", max_digits=7, decimal_places=2, default=0)
    durata_ore = models.DecimalField(
        "durata (ore)",
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Cât durează la client, de exemplu 1.5. Gol pentru serviciile fără deplasare, ca garanția extinsă.",
    )

    class Meta:
        verbose_name = "serviciu adițional"
        verbose_name_plural = "servicii adiționale"
        constraints = [
            # Prețul poate fi 0 (de exemplu livrarea gratuită), dar nu negativ
            models.CheckConstraint(
                condition=models.Q(pret__gte=0),
                name="serviciu_pret_nenegativ",
                violation_error_message="Prețul serviciului nu poate fi negativ.",
            ),
        ]

    def __str__(self):
        return f"{self.nume} ({self.pret} lei)"


class Produs(models.Model):
    """Aparatul vândut în magazin."""

    class ClasaEnergetica(models.TextChoices):
        A = "A", "A"
        B = "B", "B"
        C = "C", "C"
        D = "D", "D"
        E = "E", "E"
        F = "F", "F"
        G = "G", "G"

    class Culoare(models.TextChoices):
        ALB = "alb", "alb"
        NEGRU = "negru", "negru"
        INOX = "inox", "inox"
        ARGINTIU = "argintiu", "argintiu"
        GRI = "gri", "gri"
        BEJ = "bej", "bej"

    nume = models.CharField(max_length=100)
    cod_model = models.CharField(
        "cod model",
        max_length=30,
        unique=True,
        help_text="Codul producătorului, de pe eticheta aparatului. Două produse nu pot avea același cod.",
        error_messages={"unique": "Există deja un produs cu acest cod de model."},
    )
    # PROTECT: nu poți șterge o categorie sau un brand care mai are produse
    categorie = models.ForeignKey(Categorie, on_delete=models.PROTECT, related_name="produse")
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="produse")
    pret = models.DecimalField("preț (lei)", max_digits=8, decimal_places=2)
    clasa_energetica = models.CharField(
        "clasa energetică",
        max_length=1,
        choices=ClasaEnergetica.choices,
        null=True,
        blank=True,
        help_text="Clasa de pe eticheta energetică UE. Gol pentru produsele fără etichetă, ca plitele.",
    )
    latime = models.PositiveIntegerField("lățime (mm)")
    inaltime = models.PositiveIntegerField("înălțime (mm)")
    adancime = models.PositiveIntegerField("adâncime (mm)")
    capacitate = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="În unitatea categoriei (litri, kilograme sau seturi). Gol dacă produsul nu are capacitate.",
    )
    culoare = models.CharField(max_length=10, choices=Culoare.choices, default=Culoare.ALB)
    incorporabil = models.BooleanField("încorporabil", default=False)
    garantie_luni = models.PositiveSmallIntegerField("garanție (luni)", default=24)
    stoc = models.PositiveIntegerField(
        default=0,
        help_text="Bucăți disponibile. Sub STOC_MIN din settings.py produsul apare cu stoc limitat.",
    )
    # Atributul cu valori multiple din diagramă. ArrayField există doar în PostgreSQL.
    taguri = ArrayField(
        models.CharField(max_length=30),
        default=list,
        blank=True,
        help_text="Cuvinte cheie separate prin virgulă, fără spații după virgulă, de exemplu NoFrost,Inverter,WiFi.",
    )
    imagine = models.ImageField(upload_to="produse/", null=True, blank=True)
    data_adaugare = models.DateTimeField("data adăugării", auto_now_add=True)
    servicii = models.ManyToManyField(
        ServiciuAditional,
        related_name="produse",
        blank=True,
        verbose_name="servicii disponibile",
    )

    class Meta:
        verbose_name = "produs"
        verbose_name_plural = "produse"
        ordering = ["-data_adaugare"]  # cele mai noi primele
        constraints = [
            models.CheckConstraint(
                condition=models.Q(pret__gt=0),
                name="produs_pret_pozitiv",
                violation_error_message="Prețul trebuie să fie mai mare decât 0.",
            ),
            models.CheckConstraint(
                condition=models.Q(latime__gt=0) & models.Q(inaltime__gt=0) & models.Q(adancime__gt=0),
                name="produs_dimensiuni_pozitive",
                violation_error_message="Lățimea, înălțimea și adâncimea trebuie să fie mai mari decât 0.",
            ),
            models.CheckConstraint(
                condition=models.Q(garantie_luni__gte=24) & models.Q(garantie_luni__lte=120),
                name="produs_garantie_24_120",
                violation_error_message="Garanția e între 24 de luni (minimul legal) și 120 de luni.",
            ),
            models.CheckConstraint(
                condition=models.Q(capacitate__gt=0) | models.Q(capacitate__isnull=True),
                name="produs_capacitate_pozitiva",
                violation_error_message="Capacitatea trebuie să fie mai mare decât 0 sau să rămână goală.",
            ),
        ]
        indexes = [
            # Pagina de produse sortează după preț, nume și dată
            models.Index(fields=["pret"], name="produs_pret_idx"),
            models.Index(fields=["nume"], name="produs_nume_idx"),
            models.Index(fields=["-data_adaugare"], name="produs_data_adaugare_idx"),
            # Filtrarea după taguri caută în interiorul vectorului. Pentru ArrayField,
            # PostgreSQL folosește un index GIN, nu unul obișnuit (B-tree).
            GinIndex(fields=["taguri"], name="produs_taguri_gin_idx"),
        ]

    def __str__(self):
        return f"{self.nume} ({self.cod_model})"

    def get_absolute_url(self):
        # /magazin/produse/7. Template-urile și adminul ("Vezi pe site") iau adresa de aici.
        return reverse("produs", args=[self.id])

    def stoc_limitat(self):
        """True dacă stocul a scăzut sub STOC_MIN din settings.py."""
        return self.stoc < settings.STOC_MIN


class Promotie(models.Model):
    """O reducere cu perioadă de valabilitate. Dacă e activă se vede din date, nu se stochează."""

    nume = models.CharField(
        max_length=80,
        unique=True,
        error_messages={"unique": "Există deja o promoție cu acest nume."},
    )
    data_inceput = models.DateField("data de început")
    data_sfarsit = models.DateField("data de sfârșit")
    procent_reducere = models.DecimalField(
        "reducere (%)",
        max_digits=4,
        decimal_places=1,
        help_text="Între 1 și 90. Se aplică la prețul fiecărui produs din promoție.",
    )
    produse = models.ManyToManyField(Produs, related_name="promotii", blank=True)

    class Meta:
        verbose_name = "promoție"
        verbose_name_plural = "promoții"
        ordering = ["-data_inceput"]
        constraints = [
            # F("data_inceput") compară cu alt câmp din același rând
            models.CheckConstraint(
                condition=models.Q(data_sfarsit__gte=models.F("data_inceput")),
                name="promotie_perioada_valida",
                violation_error_message="Promoția nu se poate termina înainte să înceapă.",
            ),
            models.CheckConstraint(
                condition=models.Q(procent_reducere__gte=1) & models.Q(procent_reducere__lte=90),
                name="promotie_procent_1_90",
                # Mesajul trece prin formatarea cu %, deci semnul procent se scrie %%
                violation_error_message="Reducerea e între 1%% și 90%%.",
            ),
        ]
        indexes = [
            # Promoțiile active se caută după perioadă: data_inceput <= azi <= data_sfarsit
            models.Index(fields=["data_inceput", "data_sfarsit"], name="promotie_perioada_idx"),
        ]

    def __str__(self):
        return f"{self.nume} (-{self.procent_reducere}%)"


class DocumentProdus(models.Model):
    """Entitatea slabă: un fișier al unui produs (manual, fișă energetică, certificat de garanție).

    nr e unic doar în cadrul produsului, deci documentul se identifică prin (produs, nr).
    Adminul Django nu acceptă chei primare compuse, așa că păstrăm id-ul tehnic și
    impunem cheia (produs, nr) cu UniqueConstraint.
    """

    class Tip(models.TextChoices):
        MANUAL = "manual", "manual de utilizare"
        FISA_ENERGETICA = "fisa_energetica", "fișă energetică"
        CERTIFICAT_GARANTIE = "certificat_garantie", "certificat de garanție"

    class Limba(models.TextChoices):
        RO = "ro", "română"
        EN = "en", "engleză"
        MULTI = "multi", "mai multe limbi"

    # CASCADE: documentul nu are sens fără produs, deci se șterge odată cu el
    produs = models.ForeignKey(Produs, on_delete=models.CASCADE, related_name="documente")
    nr = models.PositiveSmallIntegerField(
        "nr.",
        help_text="Numărul documentului în cadrul produsului: 1, 2, 3. Alt produs poate avea și el documentul 1.",
    )
    tip = models.CharField(max_length=20, choices=Tip.choices)
    fisier = models.FileField("fișier", upload_to="documente/")
    limba = models.CharField(max_length=5, choices=Limba.choices, default=Limba.RO)

    class Meta:
        verbose_name = "document de produs"
        verbose_name_plural = "documente de produs"
        ordering = ["produs", "nr"]
        constraints = [
            models.UniqueConstraint(
                fields=["produs", "nr"],
                name="document_cheie_produs_nr",
                violation_error_message="Produsul are deja un document cu acest număr.",
            ),
            models.CheckConstraint(
                condition=models.Q(nr__gte=1),
                name="document_nr_pozitiv",
                violation_error_message="Numerotarea documentelor începe de la 1.",
            ),
        ]

    def __str__(self):
        return f"{self.produs.nume}, documentul {self.nr} ({self.get_tip_display()})"

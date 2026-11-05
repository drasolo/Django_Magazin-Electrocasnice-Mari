from collections import Counter
from urllib.parse import urlencode, urlsplit

from django.conf import settings
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from .models import Categorie, Produs

ZILE = ["Luni", "Marți", "Miercuri", "Joi", "Vineri", "Sâmbătă", "Duminică"]
LUNI = [
    "Ianuarie", "Februarie", "Martie", "Aprilie", "Mai", "Iunie",
    "Iulie", "August", "Septembrie", "Octombrie", "Noiembrie", "Decembrie",
]

# Formatele sunt cele din strftime. %A și %B (ziua și luna) le traducem noi,
# iar %-d e ziua din lună fără 0 în față (2, nu 02).
FORMAT_DATA = "%A, %-d %B %Y"  # Joi, 2 Octombrie 2025
FORMAT_ORA = "%H:%M:%S"
FORMAT_DATA_ORA = FORMAT_DATA + ", ora " + FORMAT_ORA


def formateaza_data(moment, format=FORMAT_DATA):
    """Ca moment.strftime(format), dar cu zilele și lunile în română.

    E o funcție separată ca să o refolosim (în Accesare și oriunde mai e
    nevoie), fără să avem aceeași bucată de cod în două locuri.
    """
    # Pe Windows, strftime dă eroare la litere ca ț sau ă. De aceea strftime
    # primește doar semnele {zi} și {luna}, iar numele românești le punem după.
    format = format.replace("%A", "{zi}").replace("%B", "{luna}").replace("%-d", str(moment.day))
    text = moment.strftime(format)
    return text.replace("{zi}", ZILE[moment.weekday()]).replace("{luna}", LUNI[moment.month - 1])


class Accesare:
    """O cerere către o pagină a aplicației. Middleware-ul creează câte una la fiecare cerere."""

    contor = 1  # id-ul următoarei accesări; e comun pentru toată clasa

    def __init__(self, ip_client, url, parametri=None):
        self.id = Accesare.contor
        Accesare.contor += 1
        self.ip_client = ip_client
        self.url = url  # fără query string: http://127.0.0.1:8000/magazin/info
        # Implicit dicționar vid. Nu scriem parametri={} în antet, pentru că acel
        # dicționar s-ar crea o singură dată și ar fi comun tuturor apelurilor.
        # Valorile sunt liste, ca în request.GET.lists(): {"iduri": ["2,3", "5"]}
        self.parametri = parametri if parametri is not None else {}
        self.data = timezone.localtime()  # momentul creării, în ora României

    def lista_parametri(self):
        """Lista de tupluri (nume, valoare); valoarea e None dacă parametrul n-a primit nimic (?a)."""
        rezultat = []
        for nume, valori in self.parametri.items():
            valori = [v for v in valori if v != ""]
            if not valori:
                rezultat.append((nume, None))
            elif len(valori) == 1:
                rezultat.append((nume, valori[0]))
            else:
                rezultat.append((nume, valori))
        return rezultat

    def string_url(self):
        """Tot url-ul, împreună cu query string-ul."""
        if not self.parametri:
            return self.url
        # doseq=True scrie fiecare valoare din listă separat: iduri=2,3&iduri=5
        return self.url + "?" + urlencode(self.parametri, doseq=True, safe=",")

    def pagina(self):
        """Doar pagina din aplicație, fără domeniu și parametri: "/" sau "/info"."""
        cale = urlsplit(self.url).path  # /magazin/info
        radacina = reverse("index")  # /magazin/
        return "/" + cale.removeprefix(radacina)

    def calculeaza_data(self, format=FORMAT_DATA, ce=""):
        """Data accesării, ca text în română.

        ce="zi" dă doar data, ce="timp" doar ora, iar altfel se folosește format.
        """
        if ce == "zi":
            format = FORMAT_DATA
        elif ce == "timp":
            format = FORMAT_ORA
        return formateaza_data(self.data, format)

    def __str__(self):
        # Câmpul poartă numele metodei, iar valoarea e ce returnează metoda
        campuri = [
            ("id", self.id),
            ("ip_client", self.ip_client),
            ("string_url", self.string_url()),
            ("pagina", self.pagina()),
            ("calculeaza_data", self.calculeaza_data(FORMAT_DATA_ORA)),
            ("lista_parametri", self.lista_parametri()),
        ]
        return "\n".join(f"{camp}: {valoare}" for camp, valoare in campuri)


# Toate accesările de la pornirea serverului. Stau în memorie, deci se pierd la repornire.
accesari = []

# Proprietățile pe care le poate cere parametrul tabel din /log
PROPRIETATI = ["id", "ip_client", "url", "parametri", "data"]


def valoare_proprietate(accesare, proprietate):
    if proprietate == "data":
        return accesare.calculeaza_data(FORMAT_DATA_ORA)
    return getattr(accesare, proprietate)


def index(request):
    return render(request, "magazin/index.html")


def info(request):
    # /info?data=zi arată doar data, /info?data=timp doar ora, altfel amândouă
    ce = request.GET.get("data", "")
    return render(request, "magazin/info.html", {
        "data_ora": request.accesare.calculeaza_data(FORMAT_DATA_ORA, ce),
    })


def log(request):
    erori = []
    selectie = accesari

    # ?iduri=2,3&iduri=5 alege accesările după id, în ordinea cerută.
    # Un id repetat apare o singură dată, doar dacă nu avem dubluri=true.
    iduri_cerute = []
    for valoare in request.GET.getlist("iduri"):
        for bucata in valoare.split(","):
            bucata = bucata.strip()
            if bucata.isdigit():
                iduri_cerute.append(int(bucata))
            elif bucata:
                erori.append(f'Id-ul "{bucata}" nu este un număr.')
    if iduri_cerute:
        dubluri = request.GET.get("dubluri", "false") == "true"
        dupa_id = {a.id: a for a in accesari}
        selectie = []
        vazute = set()
        for id_cerut in iduri_cerute:
            if id_cerut in vazute and not dubluri:
                continue
            vazute.add(id_cerut)
            if id_cerut in dupa_id:
                selectie.append(dupa_id[id_cerut])
            else:
                erori.append(f"Nu există accesarea cu id-ul {id_cerut}.")

    # ?ultimele=n păstrează ultimele n accesări
    eroare_ultimele = None
    ultimele = request.GET.get("ultimele")
    if ultimele is not None:
        if not ultimele.isdigit():
            erori.append("Parametrul ultimele trebuie să fie un număr întreg.")
        elif int(ultimele) > len(selectie):
            # se afișează toate, iar mesajul apare la final
            eroare_ultimele = (
                f"Exista doar {len(selectie)} accesari fata de {ultimele} accesari cerute"
            )
        else:
            n = int(ultimele)
            selectie = selectie[len(selectie) - n:]

    # ?tabel=tot sau ?tabel=id,url afișează un tabel în loc de listă
    coloane = []
    tabel = request.GET.get("tabel")
    if tabel == "tot":
        coloane = PROPRIETATI
    elif tabel:
        for coloana in tabel.split(","):
            coloana = coloana.strip()
            if coloana in PROPRIETATI:
                coloane.append(coloana)
            else:
                erori.append(f'Accesările nu au proprietatea "{coloana}".')
    randuri = [[valoare_proprietate(a, c) for c in coloane] for a in selectie]

    # Paginile cea mai accesată și cea mai puțin accesată, dintre cele accesate măcar o dată.
    # most_common() le ordonează descrescător după numărul de accesări.
    numarare = Counter(a.pagina() for a in accesari).most_common()

    return render(request, "magazin/log.html", {
        "selectie": selectie,
        "coloane": coloane,
        "randuri": randuri,
        "erori": erori,
        "eroare_ultimele": eroare_ultimele,
        # ?accesari=nr arată numărul de accesări, ?accesari=detalii data și ora fiecăreia
        "afiseaza_numar": request.GET.get("accesari") == "nr",
        "afiseaza_detalii": request.GET.get("accesari") == "detalii",
        "toate": accesari,
        "nume_parametri": list(request.GET.keys()),
        "cea_mai_accesata": numarare[0][0],
        "cea_mai_putin_accesata": numarare[-1][0],
    })


def accesare(request, id):
    # Ruta e definită cu re_path: /accesare5 ajunge aici cu id="5"
    for a in accesari:
        if a.id == int(id):
            return render(request, "magazin/accesare.html", {"a": a})
    raise Http404(f"Nu există accesarea cu id-ul {id}.")


def despre(request):
    return render(request, "magazin/despre.html")


def istoric(request):
    return render(request, "magazin/istoric.html")


def in_lucru(request, titlu):
    """Paginile din meniu care nu sunt încă implementate."""
    return render(request, "magazin/in_lucru.html", {"titlu": titlu})


def servicii(request):
    return in_lucru(request, "Servicii")


def promotii(request):
    return in_lucru(request, "Promoții")


def contact(request):
    return in_lucru(request, "Contact")


def cos_virtual(request):
    return in_lucru(request, "Coș de cumpărături")


# ---------- Produse și categorii (laboratorul 4) ----------

# Coloanele după care se pot sorta produsele: valoarea din URL -> (eticheta, câmpul din model)
COLOANE_SORTARE = {
    "data": ("data adăugării", "data_adaugare"),
    "pret": ("preț", "pret"),
    "nume": ("nume", "nume"),
    "stoc": ("stoc", "stoc"),
}
# Câte produse din aceeași categorie apar pe pagina unui produs
K_PRODUSE_SIMILARE = 3


def eroare(request, mesaj):
    """Pagina de eroare pentru un produs sau o categorie care nu există (cod 404)."""
    return render(request, "magazin/eroare.html", {"mesaj": mesaj}, status=404)


def lista_produse(request, produse, categorie=None):
    """Filtrarea după taguri, sortarea și paginarea produselor.

    O folosesc și pagina cu toate produsele, și paginile categoriilor: fiecare îi dă
    produsele ei, iar template-ul e același (produse.html). Așa nu scriem codul de două ori.
    """
    # ?tag=NoFrost&tag=WiFi: rămân produsele care au toate tagurile active.
    # dict.fromkeys scoate tagurile repetate și păstrează ordinea lor.
    taguri_active = list(dict.fromkeys(t for t in request.GET.getlist("tag") if t))
    if taguri_active:
        # __contains pe un ArrayField: vectorul produsului conține toate valorile din listă
        produse = produse.filter(taguri__contains=taguri_active)

    # ?coloana=pret&sort=a sortează după o singură coloană: a crescător, d descrescător.
    # Fără parametri, primele sunt cele mai noi produse.
    eroare_sortare = None
    coloana = request.GET.get("coloana", "data")
    if coloana not in COLOANE_SORTARE:
        eroare_sortare = f'Nu se poate sorta după "{coloana}", așa că produsele sunt sortate după data adăugării.'
        coloana = "data"
    sens = request.GET.get("sort", "d" if coloana == "data" else "a")
    if sens not in ("a", "d"):
        sens = "a"
    camp = COLOANE_SORTARE[coloana][1]
    # id-ul departajează produsele cu aceeași valoare, ca un produs să nu apară pe două pagini
    produse = produse.order_by(camp if sens == "a" else "-" + camp, "id")

    # Paginarea se face pe produsele deja filtrate și sortate
    paginator = Paginator(produse.select_related("categorie", "brand"), settings.PROD_PER_PAG)
    # get_page tratează singur ?pagina=abc (dă prima pagină) și ?pagina=999 (dă ultima)
    pagina = paginator.get_page(request.GET.get("pagina"))

    return render(request, "magazin/produse.html", {
        "categorie": categorie,
        "pagina": pagina,
        "taguri_active": taguri_active,
        "coloana": coloana,
        "sens": sens,
        "coloane_sortare": [(cheie, eticheta) for cheie, (eticheta, _) in COLOANE_SORTARE.items()],
        "eroare_sortare": eroare_sortare,
    })


def produse(request):
    return lista_produse(request, Produs.objects.all())


def categorie(request, nume):
    try:
        cat = Categorie.objects.get(nume=nume)
    except Categorie.DoesNotExist:
        return eroare(request, f'Nu există categoria "{nume}".')
    # Doar produsele categoriei, deci și totalurile din paginare sunt ale categoriei
    return lista_produse(request, cat.produse.all(), cat)


def produs(request, id):
    try:
        prod = Produs.objects.select_related("categorie", "brand").get(id=id)
    except Produs.DoesNotExist:
        return eroare(request, f"Nu există produsul cu id-ul {id}.")

    # K produse alese aleator din aceeași categorie. order_by("?") amestecă rândurile în SQL.
    similare = (
        Produs.objects.filter(categorie=prod.categorie)
        .exclude(id=prod.id)
        .order_by("?")[:K_PRODUSE_SIMILARE]
    )
    azi = timezone.localdate()
    return render(request, "magazin/produs.html", {
        "produs": prod,
        "similare": similare,
        "promotii_active": prod.promotii.filter(data_inceput__lte=azi, data_sfarsit__gte=azi),
    })

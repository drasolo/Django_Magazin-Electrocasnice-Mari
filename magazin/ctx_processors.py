from django.conf import settings
from django.db.models import Count

from .models import Categorie


def date_firma(request):
    """Trimite datele firmei din settings.FIRMA către toate template-urile, ca {{ firma }}."""
    return {"firma": settings.FIRMA}


def categorii_meniu(request):
    """Categoriile din meniu, citite din tabel, ca să nu scriem linkurile de mână.

    Apar doar categoriile care au produse. QuerySet-ul e leneș: interogarea rulează
    doar în paginile care îl folosesc (baza.html), nu și în admin.
    order_by e necesar: Django nu aplică Meta.ordering în interogările cu GROUP BY (Count).
    """
    return {
        "categorii_meniu": Categorie.objects.annotate(nr_produse=Count("produse"))
        .filter(nr_produse__gt=0)
        .order_by("nume")
    }

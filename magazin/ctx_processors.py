from django.conf import settings


def date_firma(request):
    """Trimite datele firmei din settings.FIRMA către toate template-urile, ca {{ firma }}."""
    return {"firma": settings.FIRMA}

from django.urls import reverse

from . import views


def get_ip(request):
    # În spatele unui proxy, IP-ul real e ultimul din X-Forwarded-For
    str_lista_ip = request.META.get("HTTP_X_FORWARDED_FOR")
    if str_lista_ip:
        return str_lista_ip.split(",")[-1].strip()
    return request.META.get("REMOTE_ADDR")


class MiddlewareAccesari:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # IP-ul ajunge la funcțiile din views.py și în template-uri (footerul) ca request.ip
        request.ip = get_ip(request)

        # Înregistrăm doar paginile aplicației, nu și /admin. Accesarea se creează
        # înainte de view, ca /log să se vadă și pe sine în listă.
        if request.path.startswith(reverse("index")):
            accesare = views.Accesare(
                ip_client=request.ip,
                url=request.build_absolute_uri(request.path),
                parametri=dict(request.GET.lists()),
            )
            views.accesari.append(accesare)
            request.accesare = accesare
            print(accesare, end="\n\n", flush=True)

        return self.get_response(request)

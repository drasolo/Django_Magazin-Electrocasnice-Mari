from django import template

register = template.Library()


def adresa_cu_taguri(request, taguri):
    """Adresa paginii curente, cu altă listă de taguri active.

    Sortarea rămâne, iar paginarea o ia de la capăt, pentru că se schimbă produsele afișate.
    """
    parametri = request.GET.copy()
    parametri.setlist("tag", taguri)
    parametri.pop("pagina", None)
    return f"{request.path}?{parametri.urlencode()}"


@register.simple_tag(takes_context=True)
def adauga_tag(context, tag):
    """Linkul unui tag din lista de produse: tagul se adaugă la cele active."""
    request = context["request"]
    taguri = request.GET.getlist("tag")
    if tag not in taguri:
        taguri.append(tag)
    return adresa_cu_taguri(request, taguri)


@register.simple_tag(takes_context=True)
def scoate_tag(context, tag):
    """Linkul de pe butonul cu "x": tagul iese din filtrare."""
    request = context["request"]
    return adresa_cu_taguri(request, [t for t in request.GET.getlist("tag") if t != tag])

from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("info", views.info, name="info"),
    path("log", views.log, name="log"),
    # /accesare5: id-ul e lipit de cuvânt, deci folosim o expresie regulată
    re_path(r"^accesare(?P<id>\d+)$", views.accesare, name="accesare"),
    path("despre", views.despre, name="despre"),
    path("istoric", views.istoric, name="istoric"),
    path("produse", views.produse, name="produse"),
    # /produse/7 e pagina unui produs; Produs.get_absolute_url() construiește adresa asta
    path("produse/<int:id>", views.produs, name="produs"),
    # /categorii/Frigidere: numele unic al categoriei, cu spații și diacritice codate în URL
    path("categorii/<str:nume>", views.categorie, name="categorie"),
    path("servicii", views.servicii, name="servicii"),
    path("promotii", views.promotii, name="promotii"),
    path("contact", views.contact, name="contact"),
    path("cos_virtual", views.cos_virtual, name="cos_virtual"),
]

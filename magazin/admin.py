from django.contrib import admin

from .models import Brand, Categorie, DocumentProdus, Produs, Promotie, ServiciuAditional

# În listările din admin, fiecare rând se afișează cu metoda __str__ a modelului.
admin.site.register(Categorie)
admin.site.register(Brand)
admin.site.register(Produs)
admin.site.register(ServiciuAditional)
admin.site.register(Promotie)
admin.site.register(DocumentProdus)

import csv

from django.contrib import admin
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils.html import format_html

from .models import Brand, Categorie, DocumentProdus, Produs, Promotie, ServiciuAditional

# Textele panoului de administrare. Stilul (culori, siglă) e în templates/admin/base_site.html.
admin.site.site_title = "Admin Electrocasnice Mari"  # titlul din tab-ul browserului
admin.site.site_header = "Electrocasnice Mari: administrare"  # textul din antetul paginilor
admin.site.index_title = "Panoul magazinului"  # titlul din pagina principală a adminului
admin.site.site_url = reverse_lazy("index")  # butonul "Vezi site-ul" duce la /magazin/


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ("nume", "culoare_si_sigla", "unitate_capacitate")
    search_fields = ("nume", "descriere")
    search_help_text = "Caută în numele și în descrierea categoriilor."

    @admin.display(description="Culoare și siglă", ordering="culoare")
    def culoare_si_sigla(self, obj):
        # format_html escapează valorile primite, deci nu se poate strica HTML-ul din listă
        return format_html(
            '<span style="color: {}; font-weight: bold;"><i class="{}"></i> {}</span>',
            obj.culoare,
            obj.sigla,
            obj.culoare,
        )


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("nume", "tara_origine", "an_infiintare", "site_oficial")
    search_fields = ("nume", "tara_origine")
    search_help_text = "Caută după numele brandului sau după țara de origine."


@admin.register(ServiciuAditional)
class ServiciuAditionalAdmin(admin.ModelAdmin):
    list_display = ("nume", "pret", "durata_ore")
    search_fields = ("nume", "descriere")
    search_help_text = "Caută în numele și în descrierea serviciilor."


@admin.register(Promotie)
class PromotieAdmin(admin.ModelAdmin):
    list_display = ("nume", "data_inceput", "data_sfarsit", "procent_reducere")
    search_fields = ("nume", "produse__nume")
    search_help_text = "Caută după numele promoției sau după numele unui produs inclus în ea."
    filter_horizontal = ("produse",)  # alegerea produselor cu două liste și căutare


class DocumentProdusInline(admin.TabularInline):
    """Documentele unui produs se adaugă direct din pagina produsului (entitatea slabă)."""

    model = DocumentProdus
    extra = 1


@admin.register(Produs)
class ProdusAdmin(admin.ModelAdmin):
    # Coloanele sunt în altă ordine decât câmpurile din model. tara_brand e un câmp al
    # brandului, adică al entității legate prin relația one-to-many.
    list_display = (
        "cod_model",
        "nume",
        "pret",
        "stoc_colorat",
        "categorie",
        "brand",
        "tara_brand",
        "clasa_energetica",
    )
    list_filter = ("categorie", "brand", "clasa_energetica", "incorporabil")  # filtrele din dreapta
    search_fields = ("nume", "cod_model")
    search_help_text = "Caută după nume sau după codul modelului. Merge și o parte din cod, de exemplu FR-BO."
    ordering = ("pret",)  # în admin, produsele apar de la cel mai ieftin la cel mai scump
    list_per_page = 5
    list_select_related = ("categorie", "brand")  # un singur JOIN, nu câte o interogare pe rând
    filter_horizontal = ("servicii",)
    inlines = [DocumentProdusInline]
    actions = ["exporta_csv", "exporta_json", "marcheaza_epuizat"]

    # Formularul are trei secțiuni. Ultima se poate închide și are doar câmpuri opționale.
    fieldsets = (
        ("Date generale", {
            "fields": ("nume", "cod_model", ("categorie", "brand"), ("pret", "stoc")),
        }),
        ("Specificații", {
            "fields": (
                "clasa_energetica",
                ("latime", "inaltime", "adancime"),
                "culoare",
                "incorporabil",
                "garantie_luni",
            ),
        }),
        ("Opționale", {
            "fields": ("capacitate", "taguri", "imagine", "servicii"),
            "classes": ("collapse",),
            "description": "Câmpuri care pot rămâne goale.",
        }),
    )

    @admin.display(description="Țara brandului", ordering="brand__tara_origine")
    def tara_brand(self, obj):
        # Scris direct ca "brand__tara_origine" în list_display, antetul ar fi "Brand tara origine"
        return obj.brand.tara_origine

    @admin.display(description="Stoc", ordering="stoc")
    def stoc_colorat(self, obj):
        if obj.stoc_limitat():
            return format_html('<b style="color: #b3261e;">{} (limitat)</b>', obj.stoc)
        return format_html('<b style="color: #1d8a6b;">{}</b>', obj.stoc)

    @admin.action(description="Exportă produsele selectate în CSV")
    def exporta_csv(self, request, queryset):
        raspuns = HttpResponse(content_type="text/csv; charset=utf-8")
        raspuns["Content-Disposition"] = 'attachment; filename="produse.csv"'
        raspuns.write("﻿")  # marcajul BOM, ca Excel să afișeze corect diacriticele
        scriitor = csv.writer(raspuns)
        scriitor.writerow(["cod model", "nume", "categorie", "brand", "pret", "stoc", "taguri"])
        for p in queryset.select_related("categorie", "brand"):
            scriitor.writerow([p.cod_model, p.nume, p.categorie.nume, p.brand.nume, p.pret, p.stoc, ",".join(p.taguri)])
        return raspuns

    @admin.action(description="Exportă produsele selectate în JSON")
    def exporta_json(self, request, queryset):
        date = [
            {
                "cod_model": p.cod_model,
                "nume": p.nume,
                "categorie": p.categorie.nume,
                "brand": p.brand.nume,
                "pret": str(p.pret),  # Decimal nu se poate scrie direct în JSON
                "stoc": p.stoc,
                "taguri": p.taguri,
            }
            for p in queryset.select_related("categorie", "brand")
        ]
        # safe=False permite o listă (implicit JsonResponse acceptă doar dicționare)
        raspuns = JsonResponse(date, safe=False, json_dumps_params={"ensure_ascii": False, "indent": 2})
        raspuns["Content-Disposition"] = 'attachment; filename="produse.json"'
        return raspuns

    @admin.action(description="Marchează produsele selectate ca epuizate (stoc 0)")
    def marcheaza_epuizat(self, request, queryset):
        # update() schimbă toate rândurile selectate într-o singură comandă UPDATE
        nr = queryset.update(stoc=0)
        self.message_user(request, f"{nr} produse au acum stocul 0.")


@admin.register(DocumentProdus)
class DocumentProdusAdmin(admin.ModelAdmin):
    # produs__cod_model: un câmp al produsului, scris cu notația __ (relația one-to-many)
    list_display = ("produs", "produs__cod_model", "nr", "tip", "limba")
    list_select_related = ("produs",)
    search_fields = ("produs__nume", "produs__cod_model")
    search_help_text = "Caută după numele sau codul produsului."

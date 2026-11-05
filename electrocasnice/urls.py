from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("magazin/", include("magazin.urls")),
    # http://127.0.0.1:8000/ duce direct la pagina principală a magazinului
    path("", RedirectView.as_view(pattern_name="index")),
]

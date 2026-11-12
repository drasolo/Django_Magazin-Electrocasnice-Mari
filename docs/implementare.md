# Unde e implementată fiecare cerință

Fișierul și linia de început pentru fiecare cerință din laboratoarele 1-4. Când un rând are mai multe fișiere, liniile lor sunt despărțite cu `;`, în ordinea fișierelor.

| Etapă | Cerință | Fișier | Linia |
|---|---|---|---|
| Lab 1 | Aplicația în `INSTALLED_APPS` | `electrocasnice/settings.py` | 54 |
| Lab 1 | Aplicația montată la `/magazin/` | `electrocasnice/urls.py` | 9 |
| Lab 1 | Pagina principală cu descrierea | `magazin/templates/magazin/index.html` | 9 |
| Lab 1 | Data în română (`formateaza_data`, zilele și lunile) | `magazin/views.py` | 13, 26 |
| Lab 1 | Clasa `Accesare` | `magazin/views.py` | 39 |
| Lab 1 | `id` autoincrementat (`contor`) | `magazin/views.py` | 42, 45 |
| Lab 1 | `lista_parametri()` | `magazin/views.py` | 55 |
| Lab 1 | `string_url()` | `magazin/views.py` | 68 |
| Lab 1 | `pagina()` | `magazin/views.py` | 75 |
| Lab 1 | `calculeaza_data(format, ce)` | `magazin/views.py` | 81 |
| Lab 1 | `__str__()` | `magazin/views.py` | 92 |
| Lab 1 | Middleware pentru IP | `magazin/middleware.py` | 6, 20 |
| Lab 1 | O accesare la fiecare cerere, afișată în consolă | `magazin/middleware.py` | 24, 32 |
| Lab 1 | Middleware-ul înregistrat | `electrocasnice/settings.py` | 66 |
| Lab 1 | `/info` și `?data=zi` / `?data=timp` | `magazin/views.py`, `info.html` | 122; 11 |
| Lab 2 T1 | `/log` | `magazin/views.py` | 130 |
| Lab 2 T1 | `iduri` și `dubluri` | `magazin/views.py` | 137 |
| Lab 2 T1 | `ultimele` și mesajul "Exista doar k accesari" | `magazin/views.py` | 160 |
| Lab 2 T1 | `tabel=tot` / `tabel=id,url` | `magazin/views.py`, `log.html` | 175; 14 |
| Lab 2 T1 | Pagina cea mai / cea mai puțin accesată | `magazin/views.py` | 189 |
| Lab 2 T1 | `accesari=nr` / `accesari=detalii`, secțiunea Parametri | `magazin/templates/magazin/log.html` | 46, 53, 65 |
| Lab 2 T1 | Ruta `/accesare<id>` cu `re_path` | `magazin/urls.py`, `views.py` | 10; 207 |
| Lab 2 T2 | `baza.html` cu header, main, footer | `magazin/templates/magazin/baza.html` | 15, 75, 79 |
| Lab 2 T2 | Meniu cu submeniuri, `{% url %}` | `magazin/templates/magazin/baza.html` | 21 |
| Lab 2 T2 | Submeniu spre secțiuni din pagină | `magazin/templates/magazin/baza.html` | 25 |
| Lab 2 T2 | Meniu derulant | `magazin/static/css/nav.css` | 46, 89 |
| Lab 2 T2 | Imagine de fundal și reguli responsive | `magazin/static/css/nav.css` | 33, 187 |
| Lab 2 T2 | IP în footer | `magazin/templates/magazin/baza.html` | 81 |
| Lab 2 T2 | Dicționarul `FIRMA` | `electrocasnice/settings.py` | 159 |
| Lab 2 T2 | Context processor propriu | `magazin/ctx_processors.py`, `settings.py` | 7; 84 |
| Lab 2 T2 | Imagini cu `{% static %}` | `index.html`, `despre.html` | 11; 11 |
| Lab 2 T2 | `in_lucru.html` și view-urile lui | `magazin/views.py` | 223 |
| Lab 2 T3 | Diagrama | `docs/diagrama.drawio`, `docs/diagrama.png` | |
| Lab 3 T1 | Modelele (6) | `magazin/models.py` | 11, 66, 95, 130, 249, 294 |
| Lab 3 T1 | Câmpuri care admit null (10) | `magazin/models.py` | 25, 41, 74, 75, 76, 103, 109, 166, 174, 192 |
| Lab 3 T1 | Câmpuri unice (5) | `magazin/models.py` | 22, 71, 100, 154, 254 |
| Lab 3 T1 | `URLField` (`site_oficial`) | `magazin/models.py` | 75 |
| Lab 3 T1 | Ordonare implicită (5 modele) | `magazin/models.py` | 49, 81, 204, 270, 325 |
| Lab 3 T1 | `choices` (5 câmpuri) | `magazin/models.py` | 40, 165, 178, 318, 320 |
| Lab 3 T1 | `default` (9 câmpuri); `taguri` are și `blank=True` | `magazin/models.py` | 28, 34, 104, 178, 179, 180, 182, 188, 320 |
| Lab 3 T1 | `help_text` (11 câmpuri) | `magazin/models.py` | 29, 35, 43, 111, 155, 168, 176, 183, 190, 263, 316 |
| Lab 3 T1 | `DateTimeField` cu data adăugării | `magazin/models.py` | 193 |
| Lab 3 T1 | Mesaje de eroare proprii (5) | `magazin/models.py` | 23, 72, 101, 156, 255 |
| Lab 3 T1 | Constrângeri cu `models.Q` (10) | `magazin/models.py` | 51, 84, 119, 206, 211, 216, 221, 273, 278, 332 |
| Lab 3 T1 | Indexuri (6 câmpuri, unul GIN pe `taguri`) | `magazin/models.py` | 229-234, 287 |
| Lab 3 T1 | `ImageField` și `FileField` | `magazin/models.py` | 192, 319 |
| Lab 3 T1 | Vectorul `taguri` (`ArrayField`) | `magazin/models.py` | 186 |
| Lab 3 T1 | Entitatea slabă: `CASCADE` și `UniqueConstraint(produs, nr)` | `magazin/models.py` | 313, 327 |
| Lab 3 T2 | `creare_user.sql` | `creare_user.sql` | |
| Lab 3 T2 | `django.contrib.postgres` pentru `ArrayField` | `electrocasnice/settings.py` | 53 |
| Lab 3 T2 | `verbose_name_plural` | `magazin/models.py` | 48, 80, 116, 203, 269, 324 |
| Lab 3 T2 | `__str__` pentru listarea din admin | `magazin/models.py` | 58, 91, 126, 237, 290, 339 |
| Lab 3 T2 | Modelele înregistrate în admin | `magazin/admin.py` | 18, 35, 42, 49, 64, 157 |
| Lab 4 admin | Altă ordine a coloanelor (`list_display`) și a câmpurilor (`fieldsets`) | `magazin/admin.py` | 67, 88 |
| Lab 4 admin | Câmp din entitatea legată one-to-many | `magazin/admin.py` | 109, 159 |
| Lab 4 admin | `@admin.display` și `format_html` | `magazin/admin.py` | 24, 114 |
| Lab 4 admin | `search_fields` și `search_help_text` la toate modelele | `magazin/admin.py` | 20, 37, 44, 51, 78, 161 |
| Lab 4 admin | Ordonare după o coloană (preț crescător) | `magazin/admin.py` | 80 |
| Lab 4 admin | Filtre laterale | `magazin/admin.py` | 77 |
| Lab 4 admin | 5 rânduri pe pagină | `magazin/admin.py` | 81 |
| Lab 4 admin | Secțiuni în formular, una colapsabilă | `magazin/admin.py` | 88, 103 |
| Lab 4 admin | Titlul tab-ului, antetul, titlul paginii principale, "View site" | `magazin/admin.py` | 11-14 |
| Lab 4 admin | Culori, meniul din stânga, sigla din antet | `templates/admin/base_site.html` | 16-22, 26, 47 |
| Lab 4 admin | `templates/` în `DIRS`, ca să fie găsit `base_site.html` | `electrocasnice/settings.py` | 76 |
| Lab 4 admin | Acțiuni: export CSV, export JSON, stoc 0 | `magazin/admin.py` | 85, 120, 131, 150 |
| Lab 4 bonus | Scriptul cu comenzi `INSERT` | `magazin/management/commands/genereaza_produse.py` | 98, 128, 147, 154 |
| Lab 4 QS | Pagina cu toate produsele | `magazin/views.py`, `produse.html` | 305; 53 |
| Lab 4 QS | Chenarul produsului, cu imaginea implicită `imagine_indisponibila.svg` | `magazin/templates/magazin/produs_card.html` | 3, 5 |
| Lab 4 QS | `get_absolute_url()` | `magazin/models.py` | 61, 240 |
| Lab 4 QS | Pagina produsului și pagina de eroare | `magazin/views.py` | 318, 257 |
| Lab 4 QS | "Produse din aceeași categorie", K aleator | `magazin/views.py`, `produs.html` | 254, 328; 71 |
| Lab 4 QS | Sortare după coloană și sens | `magazin/views.py`, `produse.html` | 247, 287; 19 |
| Lab 4 QS | `stoc` și `taguri` | `magazin/models.py` | 181, 186 |
| Lab 4 QS | `STOC_MIN` și `PROD_PER_PAG` | `electrocasnice/settings.py` | 172, 174 |
| Lab 4 QS | Marcajul de stoc limitat | `magazin/models.py`, `stoc.html`, `produse.css` | 244; 4; 135 |
| Lab 4 QS | Tagurile ca linkuri care adaugă un filtru | `magazin/templatetags/magazin_taguri.py`, `produs_card.html`, `produs.html` | 18; 23; 42 |
| Lab 4 QS | Filtrare după toate tagurile active | `magazin/views.py` | 273 |
| Lab 4 QS | Tagurile active, cu "x" | `produse.html`, `magazin_taguri.py` | 43; 28 |
| Lab 4 QS | `Paginator` | `magazin/views.py` | 290, 292 |
| Lab 4 QS | "Pagina X din Y" sus și jos, linkuri care păstrează filtrele | `magazin/templates/magazin/paginare.html` | 5, 9 |
| Lab 4 QS | "Se afișează produsele între k și k+n" | `magazin/templates/magazin/produse.html` | 50 |
| Lab 4 QS | `/categorii/nume_categorie` | `magazin/urls.py`, `views.py` | 17; 309 |
| Lab 4 QS | Același template și cod refolosit (`lista_produse`) | `magazin/views.py` | 262 |
| Lab 4 QS | Meniul "Categorii" din baza de date, doar cu produse | `magazin/ctx_processors.py`, `baza.html` | 12; 44 |
| Lab 4 QS | Culoarea și sigla categoriei în afișaj | `produs_card.html`, `produse.html`, `produse.css` | 3, 9; 9, 10; 9, 87 |
| Lab 4 QS | Numele categoriei e link spre pagina ei | `produs_card.html` | 8 |

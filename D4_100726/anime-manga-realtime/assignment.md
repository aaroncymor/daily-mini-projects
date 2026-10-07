## Project Title

Real-Time Anime & Manga Filter Engine

## Overview & Objective

Build an ultra-responsive, SPA-like web dashboard using Django, HTMX, and Alpine.js. The goal is to master the interaction boundary between Alpine.js (handling client-side state, modal windows, and instant input debounce) and HTMX (handling dynamic backend search filtering, partial DOM swaps, and infinite scroll pagination).

## Tech Stack

* Frontend / CLI: Django Templates + Tailwind CSS (via CDN) + HTMX + Alpine.js
* Backend / Script: Django (Python 3.11+)
* Data / API: Jikan API (MyAnimeList v4) + SQLite

## Key Features (3-4 Hours Scope)

1. HTMX Search-as-you-Type & Dynamic Filter Bar: As the user types or toggles genres/type filters, HTMX automatically triggers server-side queries and swaps out only the content grid without refreshing the page.
2. Alpine.js Client-Side Modal & Card Drawer: Clicking any anime/manga card opens a detailed preview drawer managed instantly by Alpine.js local state, while HTMX dynamically loads the full synopsis into the drawer via AJAX.
3. HTMX Infinite Scroll / Load More: Implement infinite scrolling or a button-triggered "Load More" pattern using `hx-get`, `hx-trigger="revealed"`, and `hx-swap="afterend"`.

## Mock UI & Wireframe

+-----------------------------------------------------------------------+
|  ANIME & MANGA REAL-TIME FILTER ENGINE                                |
+-----------------------------------------------------------------------+
|  SEARCH & FILTERS                                                     |
|  [ Search: Frieren...          ] (hx-get="/search/" hx-trigger="keyup") |
|  Type: [ All | Anime | Manga ]   Genre: [ Action | Fantasy | Sci-Fi ]  |
+-----------------------------------------------------------------------+
|  DYNAMIC RESULTS GRID (Swapped via HTMX)                              |
|  +-----------------------+  +-----------------------+                 |
|  | Frieren: Beyond...    |  | Dungeon Meshi         |                 |
|  | Rating: 9.1           |  | Rating: 8.6           |                 |
|  | [ Quick View ]        |  | [ Quick View ]        |                 |
|  +-----------------------+  +-----------------------+                 |
|                                                               [118;1:3u        |
|  [ Loading More Results... (hx-trigger="revealed") ]                   |
+-----------------------------------------------------------------------+
|  ALPINE.JS MODAL DRAWER (x-data="{ open: false }")                   |
|  +-----------------------------------------------------------------+  |
|  | [X] Close Drawer                                                |  |
|  | Detailed Synopsis (Loaded via hx-get="/detail/123/")            |  |
|  +-----------------------------------------------------------------+  |
+-----------------------------------------------------------------------+

## Helpful APIs, Packages & GitHub References

* Free APIs / SaaS Options:
* Jikan API v4 (`[https://api.jikan.moe/v4/anime](https://api.jikan.moe/v4/anime)` or `[https://api.jikan.moe/v4/manga](https://api.jikan.moe/v4/manga)`)


* Recommended Packages (Python / NPM):
* Python: `django`, `httpx`, `django-htmx`


* GitHub Inspiration & Repositories:
* Search query: `django htmx alpinejs dynamic search` or `htmx infinite scroll django`



## Step-by-Step Implementation Guide

* Step 1: Environment Setup & Boilerplate (15 mins)
* Initialize a Django project (`config`) and app (`catalog`).
* Include HTMX and Alpine.js via CDN in `base.html`.
* Install `django-htmx` to simplify checking `request.htmx` inside Django views.


* Step 2: Core Backend Logic & Partial Templates (60-90 mins)
* Create a view `catalog_index` that serves the main page on regular requests, but returns ONLY partial HTML (`partials/card_grid.html`) when `request.htmx` is True.
* Write a service wrapper using `httpx` to query the Jikan API with search, genre, and page parameters.
* Build a detail endpoint returning a snippet HTML for the Alpine drawer.


* Step 3: Frontend Integration with HTMX & Alpine.js (60 mins)
* Set up the search input using HTMX attributes: `hx-get="{% url 'search' %}" hx-trigger="keyup changed delay:500ms, search" hx-target="#results-grid" hx-swap="outerHTML"`.
* Configure Alpine.js state (`x-data="{ open: false, selectedId: null }"`) on the drawer parent component.
* Connect card clicks to open the Alpine modal while simultaneously triggering HTMX (`hx-get` to fetch details).


* Step 4: Testing & Polish (30 mins)
* Ensure smooth transition indicators using HTMX's `.htmx-request` class to show a quick loading spinner while API fetches take place.
* Style badges and cards cleanly using Tailwind CSS.



## Stretch Goal (If Finished Early)

* Add an Alpine-powered active tag bar that lets users clear individual active filter tags (e.g. `[ Genre: Fantasy X ]`) instantly on the client side, triggering an HTMX refresh automatically.

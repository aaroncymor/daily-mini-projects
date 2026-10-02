Project Title
Anime & Manga Backlog & Chapter Velocity Tracker
Overview & Objective
Build a focused Django web application that allows users to manage their active anime and manga backlogs, calculate reading/watching velocity, and project estimated completion dates. The tool integrates external API metadata so users can track their progress through series and chapters without manual setup.
Tech Stack
Frontend / CLI: Django Templates + Tailwind CSS (via CDN) + HTMX / Alpine.js
Backend / Script: Django (Python 3.11+)
Data / API: Jikan API (Unofficial MyAnimeList API) + SQLite
Key Features (3-4 Hours Scope)
Series Search & Quick-Add: Search anime and manga using the Jikan API and add selected items to your personal watchlist or reading list with preset to[118;1:3utal episode/chapter counts.
Progress & Reading Velocity Estimator: Log current episode or chapter progress; calculate daily velocity (chapters per day) and estimate the completion date.
Interactive Backlog Dashboard: View current active series, overall completion percentage across your list, and velocity metrics.
Mock UI & Wireframe
+-----------------------------------------------------------------------+
|  ANIME & MANGA BACKLOG & VELOCITY TRACKER                             |
+-----------------------------------------------------------------------+
|  [ Search Anime / Manga ] [ Query: One Piece        ] [ Search ]      |
|  Results:                                                             |
|  - One Piece (Manga) - 1100+ Chapters [ + Add to Backlog ]           |
|  - One Piece (Anime) - 1000+ Episodes [ + Add to Backlog ]            |
+-----------------------------------------------------------------------+
YOUR ACTIVE BACKLOG
Title: Chainsaw Man (Manga)
Progress: [ 80 ] / 150 Chapters (53%)
Reading Speed: 5 chapters/day
[ Update Progress ]
-------------------------------------------------------------------
SUMMARY METRICS
Total Tracked Items: 4
Average Reading Pace: 8.2 chapters/day
+-----------------------------------------------------------------------+
Helpful APIs, Packages & GitHub References
Free APIs / SaaS Options:
Jikan API v4 ([https://api.jikan.moe/v4/anime](https://api.jikan.moe/v4/anime) or [https://api.jikan.moe/v4/manga?q=](https://api.jikan.moe/v4/manga?q=){query})
Recommended Packages (Python / NPM):
Python: django, httpx, django-widget-tweaks
GitHub Inspiration & Repositories:
Search query: django myanimelist app or jikan api python client
Step-by-Step Implementation Guide
Step 1: Environment Setup & Boilerplate (15 mins)
Initialize a Django project named config and an app named backlog.
Configure SQLite database and setup static templates with Tailwind CDN.
Step 2: Core Backend Logic / Script Setup (60-90 mins)
Create a BacklogItem Django model storing title, mal_id, media_type (anime/manga), current_progress, total_units, start_date, and target_date.
Implement a view using httpx to fetch query results from Jikan API and map results into Django forms for quick saving.
Write helper functions on the model to calculate daily reading rate and remaining days.
Step 3: Frontend / User Interface / CLI Output (60 mins)
Create standard Django templates (base.html, dashboard.html, search.html).
Integrate inline form updating so users can increment chapter counts directly from the dashboard card.
Step 4: Testing & Polish (30 mins)
Add basic error handling for Jikan API rate limits (Jikan has a 3 requests/sec limit).
Style progress bars and metrics indicators using Tailwind CSS.
Stretch Goal (If Finished Early)
Add an HTMX-powered inline search bar so search results load dynamically without full page refreshes.

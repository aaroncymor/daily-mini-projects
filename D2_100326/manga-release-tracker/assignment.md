## Project Title

Manga Chapter Release Tracker & Notification Service

## Overview & Objective

Build a focused Django application that tracks manga series releases and sends simulated email or webhook notifications when a new chapter is detected. It uses Django's ORM and background task architecture alongside external anime and manga APIs to automate series tracking and user alerts.

## Tech Stack

* Frontend / CLI: Django Templates + Tailwind CSS (via CDN)
* Backend / Script: Django (Python 3.11+)
* Data / API: Jikan API (MyAnimeList v4) + SQLite

## Key Features (3-4 Hours Scope)

1. Series Watchlist & Target Setup: Search manga series via Jikan API and subscribe them to your update watchlist.
2. Automated Chapter Checker: A Django management command (`python manage.py check_updates`) that polls Jikan API for the latest chapter counts and updates database state.
3. Notification Log & Alert Center: Dashboard showing recent chapter releases, last checked timestamps, and a simulated email payload view for newly detected chapters.

## Mock UI & Wireframe

+-----------------------------------------------------------------------+
|  MANGA RELEASE TRACKER & ALERT SERVICE                                |
+-----------------------------------------------------------------------+

| [ Add Manga to Watchlist ] [ Search: Jujutsu Kaisen   ] [ Search ] |
| --- |
| ACTIVE WATCHLIST |
| - Jujutsu Kaisen |
| - Chainsaw Man |
| ------------------------------------------------------------------- |
| RECENT NOTIFICATION LOGS |
| [2026-10-02 08:00] SENT Email to dev@example.com |
| Subject: New Chapter Alert - Chainsaw Man Chapter 175 is out! |
| ------------------------------------------------------------------- |
| [ Run Manual Update Check Now ] |
| +-----------------------------------------------------------------------+ |

## Helpful APIs, Packages & GitHub References

* Free APIs / SaaS Options:
* Jikan API v4 (`[https://api.jikan.moe/v4/manga?q=](https://api.jikan.moe/v4/manga?q=){query}`)


* Recommended Packages (Python / NPM):
* Python: `django`, `httpx`, `rich`


* GitHub Inspiration & Repositories:
* Search query: `django custom management command email notification` or `jikan api manga tracker`



## Step-by-Step Implementation Guide

* Step 1: Environment Setup [118;1:3u& Boilerplate (15 mins)
* Initialize a Django project named `config` and an app named `tracker`.
* Configure SQLite database and basic template layouts with Tailwind CDN.


* Step 2: Core Backend Logic / Script Setup (60-90 mins)
* Create `MangaSubscription` model (storing title, mal_id, current_chapter, last_checked_at) and `NotificationLog` model (storing subject, message_body, sent_at).
* Write a custom Django management command in `tracker/management/commands/check_updates.py` using `httpx` to fetch updated metadata from Jikan API and save notification logs when `current_chapter` increases.


* Step 3: Frontend / User Interface / CLI Output (60 mins)
* Create dashboard views displaying the watchlist table and recent notifications.
* Add a form endpoint that triggers the `check_updates` logic directly from a dashboard button click for fast testing.


* Step 4: Testing & Polish (30 mins)
* Test edge cases, such as handling rate limits (3 requests/sec) from Jikan API using lightweight error handling.
* Format notification logs cleanly with Tailwind badge elements.



## Stretch Goal (If Finished Early)

* Integrate Django's built-in `django.core.mail` backend (using `console.EmailBackend`) to print formatted email alerts straight to your terminal whenever a new chapter is released.

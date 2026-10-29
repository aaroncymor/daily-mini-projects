Ichiban Kuji Real-Time Draw Engine & Inventory TrackerOverview & ObjectiveUpgrade the Ichiban Kuji live draw app into a production-grade HTMX + SSE architecture using Django, django-htmx, and django-stubs. This project focuses on managing edge cases in HTMX Server-Sent Events—specifically handling connection lifecycle management, OOB target isolation, and server-side connection cleanup.The application streams asynchronous ticket draws over text/event-stream. Each event delivers a main draw payload alongside Out-of-Band (hx-swap-oob="true") updates to sync inventory numbers, a live winner ticker, and a status badge across connected clients.Tech StackFrontend / CLI: Django Templates + Tailwind CSS (via CDN) + HTMX 2.x + HTMX SSE Extension (htmx-ext-sse)Backend / Script: Django Async Views (StreamingHttpResponse) + django-htmx + django-stubs (mypy strict mode)Data / API: SQLite / Async Python Generators (asyncio) + Jikan API (for anime figurine metadata)Key Features & SSE Architectural UpgradesExplicit Stream Closing via sse-close: Instead of leaving open EventSource connections hanging indefinitely on completed draws, the backend pushes a final named event (event: kuji-complete) that matches the client's sse-close attribute to gracefully disconnect the browser.Strict Type Safety with django-stubs: Fully typed async request generators using HtmxHttpRequest from django-htmx, ensuring mypy --strict passes with zero type errors.Multi-Target Out-of-Band (OOB) Isolation: Every event frame sends an isolated target HTML payload (current ticket) along with OOB elements to update:Remaining Prize Stock Counts (#prize-inventory)Real-time Winner History Log (#winner-feed with hx-swap-oob="afterbegin")Draw Status Badge & Progress Counter (#draw-status)Mock UI & Wireframe+-----------------------------------------------------------------------+
|  ICHIBAN KUJI LIVE DRAW DASHBOARD                                     |
+-----------------------------------------------------------------------+
|  PRIZE INVENTORY (OOB Target 1):                                      |
|  [ A Prize: Frieren Figure (1 left) ] [ B Prize: Acrylic Stand (3) ]  |
|  PROGRESS (OOB Target 2): [ 18 / 50 Tickets Drawn ]                   |
+-----------------------------------------------------------------------+
|  [ Trigger Draw Sequence ] (hx-post="/kuji/start/" hx-target="#control")|
+-----------------------------------------------------------------------+
|  LIVE DRAW STAGE                                                      |
|  <div hx-ext="sse" sse-connect="/kuji/stream/"                        |sse-swap="kuji-draw" sse-close="kuji-complete">CURRENT TICKET: Ticket #042 ---> WINNER OF "A PRIZE: FRIEREN"!----------------------------------------------------------------LIVE WINNER LOG (OOB Target 3: hx-swap-oob="afterbegin:#winner-feed")- Ticket #042 won A Prize (Frieren Figure)- Ticket #041 won C Prize (Manga Volume)+-----------------------------------------------------------------------+Helpful APIs, Packages & GitHub ReferencesFree APIs / SaaS Options:HTMX SSE Extension ([https://unpkg.com/htmx-ext-sse@2.2.2/sse.js](https://unpkg.com/htmx-ext-sse@2.2.2/sse.js) / CDN for HTMX 2.x)Jikan API v4 ([https://api.jikan.moe/v4/anime](https://api.jikan.moe/v4/anime) for pulling prize artwork and titles)Recommended Packages (Python / NPM):Python: django, django-htmx, django-stubs, mypy, asyncio, httpxGitHub Inspiration & Repositories:Search query: django sse streaminghttpresponse htmx sse-close or django-htmx typed request sseStep-by-Step Implementation GuideStep 1: Project Setup & Static Typing Configuration (15 mins)Initialize a Django project (config) and app (kuji).Configure mypy.ini with django-stubs:Ini, TOML[mypy]
plugins = mypy_django_plugin.main

[mypy_django_plugin]
ignore_missing_model_attributes = True
Include HTMX 2.x and htmx-ext-sse scripts in base.html.Step 2: Build the Strictly Typed Async Generator View (60-90 mins)Implement a typed async streaming view that yields formatted SSE string blocks:Pythonimport asyncio
from typing import AsyncGenerator
from django.http import StreamingHttpResponse
from django_htmx.middleware import HtmxHttpRequest

async def kuji_stream(request: HtmxHttpRequest) -> StreamingHttpResponse:
    async def event_generator() -> AsyncGenerator[str, None]:
        prizes = ["A Prize (Figure)", "B Prize (Acrylic)", "C Prize (Manga)", "D Prize (Badge)"]

        for ticket_no in range(1, 6):
            await asyncio.sleep(2)
            won_prize = prizes[ticket_no % len(prizes)]
            remaining_a = max(0, 2 - (ticket_no // 3))

            # Build main SSE event payload + OOB HTML fragments
            html_payload = f"""
            <div id="current-draw-card" class="p-4 bg-purple-900 text-white font-bold rounded">
                Ticket #{ticket_no:03d} won <span class="text-yellow-400">{won_prize}</span>!
            </div>

            <div id="winner-feed" hx-swap-oob="afterbegin">
                <div class="py-1 border-b border-slate-700 text-sm">
                    Ticket #{ticket_no:03d} claimed {won_prize}
                </div>
            </div>

            <span id="prize-inventory-a" hx-swap-oob="innerHTML">{remaining_a} left</span>
            <span id="drawn-count" hx-swap-oob="innerHTML">{ticket_no} / 5</span>
            """

            # Format to raw SSE lines: 'data: <line>\n'
            formatted_data = "".join([f"data: {line}\n" for line in html_payload.split("\n") if line.strip()])
            yield f"event: kuji-draw\n{formatted_data}\n\n"

        # Emit the closing SSE event to gracefully terminate EventSource on the client
        yield "event: kuji-complete\ndata: <div id='draw-status' class='text-green-400 font-bold'>Draw Complete!</div>\n\n"

    return StreamingHttpResponse(event_generator(), content_type="text/event-stream")
Step 3: Configure Template for SSE & OOB Swaps (60 mins)Set up the template to consume the event stream and auto-close upon draw completion:HTML<div hx-ext="sse" 
     sse-connect="{% url 'kuji_stream' %}" 
     sse-swap="kuji-draw" 
     sse-close="kuji-complete" 
     class="p-6 bg-slate-900 rounded-lg">

    <!-- Primary Swap Target (Updates on every 'kuji-draw' event) -->
    <div id="current-draw-card">
        <p class="text-gray-400">Waiting for live draw to start...</p>
    </div>
</div>

<!-- Out-of-Band (OOB) Targets -->
<div id="winner-feed" class="mt-4 space-y-1"></div>
<p class="text-sm">A-Prizes Left: <span id="prize-inventory-a">2 left</span></p>
<p class="text-sm">Total Drawn: <span id="drawn-count">0 / 5</span></p>
Step 4: Verification & Static Analysis (30 mins)Run mypy . to confirm static type compliance across models and views.Test in browser dev tools (Network tab -> SSE) to confirm that the EventSource connection opens, processes OOB swaps, and terminates cleanly when kuji-complete fires.Stretch Goal (If Finished Early)Implement an Async Abort Signal / Disconnect Listener: Detect when a client closes their browser tab mid-stream and cancel the asyncio sleep task on the server to prevent lingering background tasks.
Project Title
Real-Time Async Job Monitor & Dashboard (with HTMX SSE, OOB, django-htmx, & django-stubs)
Overview & Objective
Build an async task monitoring dashboard in Django where long-running jobs (e.g., data exports, batch processing) report live progress through Server-Sent Events (SSE). Utilizing the HTMX SSE extension (hx-ext="sse"), an async StreamingHttpResponse streams HTML fragments down an open event connection. The streamed response uses HTMX Out-of-Band (OOB) Swaps (hx-swap-oob="true") to concurrently update job progress bars, update an overall system activity log, and bump global counter stats in real time. The entire codebase is strictly typed using django-stubs, mypy, and django-htmx.
Tech Stack
Frontend / CLI: Django Templates + Tailwind CSS (via CDN) + HTMX + HTMX SSE Extension (htmx/ext/sse.js)
Backend / Script: Django (Asynchronous Views / StreamingHttpResponse) + django-htmx + django-stubs (for mypy strict type-checking)
Data / API: SQLite / Async Python generator (asyncio)
Key Features (3-4 Hours Scope)
Strictly Typed Views & Request Handling: Fully type-annotated Django views utilizing HtmxHttpRequest from django-htmx and type hints verified by django-stubs / mypy.
Async SSE Event Streaming Endpoint: An async def view yielding text/event-stream formatted HTML chunks to push real-time updates to the client without WebSockets.
Out-of-Band (OOB) Multi-Target Live Swaps: Each SSE chunk delivers a primary payload (e.g., updating job progress percentage in #job-list) along with OOB elements (hx-swap-oob="true") that dynamically update:
Global System Activity Log (#activity-log)
Completed Tasks Counter (#completed-count)
Active System Load Status (#system-status)
Mock UI & Wireframe
+-----------------------------------------------------------------------+
|  REAL-TIME ASYNC JOB DASHBOARD (HTMX SSE + OOB DEMO)                  |
+-----------------------------------------------------------------------+
|  SYSTEM STATUS (OOB Target 1): [ ACTIVE - 2 JOBS RUNNING ]             |
|  TOTAL COMPLETED JOBS (OOB Target 2): [ 14 ]                          |
+-----------------------------------------------------------------------+
|  [ Launch New Background Job ] (hx-post="/jobs/create/")             |
+-----------------------------------------------------------------------+
ACTIVE JOBS LIST (sse-connect="/jobs/stream/" sse-swap="job-update")
Job #102: Data Export [=========> ] 45% (Running)
Job #103: Batch Report Gen [===================>] 95% (Running)
-------------------------------------------------------------------
LIVE ACTIVITY LOG (OOB Target 3: hx-swap-oob="afterbegin:#activity")
Job #102 reached 45% completion
Job #103 reached 95% completion
+-----------------------------------------------------------------------+
Helpful APIs, Packages & GitHub References
Free APIs / SaaS Options:
HTMX SSE Extension ([https://unpkg.com/htmx-ext-sse@2.2.2/sse.js](https://unpkg.com/htmx-ext-sse@2.2.2/sse.js))
Recommended Packages (Python / NPM):
Python: django, django-htmx, django-stubs, mypy, asyncio
GitHub Inspiration & Repositories:
Search query: django sse streaminghttpresponse htmx or django-htmx mypy typed request
Step-by-Step Implementation Guide
Step 1: Environment Setup & Type Checking Configuration (15 mins)
Initialize a Django project (config) and app (jobs).
Configure mypy.ini or pyproject.toml with django-stubs:
```toml
Ini, TOML
[tool.mypy]
plugins = ["mypy_django_plugin.main"]

[tool.django-stubs]
django_settings_module = "config.settings"
```

Include HTMX and HTMX SSE extension in base.html.

Step 2: Create Typed Django Views with django-htmx (60 mins)
Define type-safe views using django_htmx.middleware.HtmxHttpRequest:

```python
from typing import AsyncGenerator
from django.http import StreamingHttpResponse
from django_htmx.middleware import HtmxHttpRequest

async def job_stream(request: HtmxHttpRequest) -> StreamingHttpResponse:
    async def event_generator() -> AsyncGenerator[str, None]:
        for progress in range(10, 110, 10):
            await asyncio.sleep(1)

            # Primary target payload + OOB Swap payload in event-stream format
            html_chunk = f"""
            <div id="job-101-progress" class="w-full bg-blue-600 h-4 rounded" style="width: {progress}%"></div>

            <div id="activity-log" hx-swap-oob="afterbegin">
                <p class="text-xs text-gray-400">[{progress}%] Job #101 step updated.</p>
            </div>
            <span id="completed-count" hx-swap-oob="innerHTML">{progress // 10}</span>
            """

            # Format strictly for SSE protocol: 'event: <name>\ndata: <payload>\n\n'
            formatted_payload = "".join([f"data: {line}\n" for line in html_chunk.split("\n") if line.strip()])
            yield f"event: job-update\n{formatted_payload}\n\n"

    return StreamingHttpResponse(event_generator(), content_type="text/event-stream")
```
Step 3: Configure Template SSE Connectors & Out-of-Band Swaps (60 mins)
In your dashboard HTML, install the sse extension on the outer container:

<div hx-ext="sse" sse-connect="{% url 'job_stream' %}" sse-swap="job-update">
    <!-- Primary SSE swap target -->
    <div id="job-101-progress"></div>
</div>

<!-- Out-of-Band targets updated automatically via SSE payload -->
<div id="activity-log"></div>
<p>Completed: <span id="completed-count">0</span></p>
Step 4: Testing & Mypy Static Analysis (30 mins)
Run mypy . to verify that all request parameters, models, and view returns strictly adhere to django-stubs definitions.
Verify in your browser that the SSE stream stays open and correctly updates multiple DOM elements simultaneously via OOB.
Stretch Goal (If Finished Early)
Send a named SSE event event: close when the background task hits 100%, and configure the client-side element with sse-close="close" to close the EventSource connection cleanly from the server.

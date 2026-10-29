import logging
import asyncio
from typing import AsyncGenerator
from django.http import StreamingHttpResponse, HttpRequest, HttpResponse
from django_htmx.middleware import HtmxDetails
from django.shortcuts import render


logger = logging.getLogger(__name__)

# Create your views here.
class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails

def index(request: HtmxHttpRequest) -> HttpResponse:
    return render(request, "kuji/index.html")


async def kuji_stream(request: HtmxHttpRequest) -> StreamingHttpResponse:
    async def event_generator() -> AsyncGenerator[str, None]:
        prizes = [
            "A Prize (Figure)", "B Prize (Acrylic)", "C Prize (Manga)",
            "D Prize (Badge)"
        ]

        try:
            for ticket_no in range(1, 6):
                await asyncio.sleep(2)
                won_prize = prizes[ticket_no % len(prizes)]
                remaining_a = max(0, 2 - (ticket_no // 3))

                status_fragment = ""
                if ticket_no == 5:
                    status_fragment = '<div id="draw-status" hx-swap-oob="innerHTML" class="text-green-400 font-bold">Draw Complete!</div>'

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
                {status_fragment}
                """
                formatted_data = "".join([f"data: {line}\n" for line in html_payload.split("\n") if line.strip()])
                yield f"event: kuji-draw\n{formatted_data}\n\n"

            # Emit the closing SSE event to gracefully terminate EventSource on the client
            # close-only: body is irrelevant, so keep it minimal
            yield "event: kuji-complete\ndata: done\n\n"
        except asyncio.CancelledError:
            # Client closed the tab / EventSource mid-stream.
            logger.info("kuji_stream: client disconnected, aborting draw")
            raise
        finally:
            # Runs on normal completion AND on cancellation — do teardown here
            # (close DB connections, release a lock, decrement an active-viewers counter, etc.)
            logger.info("kuji_stream: generator cleanup complete")

    return StreamingHttpResponse(event_generator(), content_type="text/event-stream")
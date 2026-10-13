import asyncio
from django.http import StreamingHttpResponse
from django.template.loader import render_to_string
from django.shortcuts import render


# Create your views here.
async def sse_progress_stream(request):
    async def event_generator():
        for percent in range(0, 101, 10):
            # Render HTML partial to string
            html_content = render_to_string(
                'realtime/partials/progress_bar.html',
                {'percent': percent}
            )

            clean_html = html_content.replace('\n', '')

            # Format according to sse protocol standard:
            # event: <event_name>\n
            # data: <data_payload>\n\n
            yield f"event: progress_update\ndata: {clean_html}\n\n"
            await asyncio.sleep(1)
    response = StreamingHttpResponse(
        event_generator(),
        content_type="text/event-stream"
    )

    # Prevent caching proxy middleware from buffering the stream
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'  # for nginx
    return response


def index(request, *args, **kwargs):
    return render(request, 'realtime/index.html', {})

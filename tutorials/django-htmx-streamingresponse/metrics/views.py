import time
from django.db.models import Count, Sum
from django.http import StreamingHttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import SaleEvent


def _stats():
    agg = SaleEvent.objects.aggregate(total=Count("id"), revenue=Sum("amount"))
    return {"total": agg["total"] or 0, "revenue": agg["revenue"] or 0}


# Create your views here.
def dashboard(request):
    sales = SaleEvent.objects.all()
    return render(request, "metrics/dashboard.html", {"sales": sales, **_stats()})


def sales_table(request):
    qs = SaleEvent.objects.all()
    region = request.GET.get("region")
    product = request.GET.get("product")
    if region:
        qs = qs.filter(region=region)

    if product:
        qs = qs.filter(product__icontains=product)

    return render(request, "metrics/partials/table.html", {"sales": qs})


def edit_row(request, pk):
    sale = get_object_or_404(SaleEvent, pk=pk)
    if request.method == "POST":
        sale.product = request.POST.get("product", sale.product)
        sale.amount = request.POST.get("amount", sale.amount)
        sale.save()
        # One response, two targets: morph the row back to read-only AND
        # refresh the stats panel via htmx 4's <hx-partial>.
        return render(request, "metrics/partials/save_response.html", {"sale": sale, **_stats()})
    # Cancel returns the read-only row without saving.
    if request.GET.get("cancel"):
        return render(request, "metrics/partials/row.html", {"sale": sale})
    return render(request, "metrics/partials/row_edit.html", {"sale": sale})


def activity_stream(request):
    started = timezone.now()  # only stream sales added after this stream opened

    def event_generator():
        seen_ids = set()
        # Yield immediately so the HTTP headers flush and the stream is
        # established right away. Without a first chunk, the connection
        # stalls (no headers sent) and htmx aborts the fetch.
        yield "<!-- activity stream connected -->\n"
        for _ in range(30):  # poll for 60 seconds (1 minute)
            new_sales = (
                SaleEvent.objects
                .filter(created_at__gte=started)
                .exclude(pk__in=seen_ids)
                .order_by("created_at")
            )
            for sale in new_sales:
                seen_ids.add(sale.pk)
                yield f'<li id="event-{sale.pk}">{sale.product} sold in {sale.region} for ${sale.amount}</li>\n'
            # Sleep once per POLL (outside the row loop), so an empty poll
            # still waits 1s instead of hammering the DB in a tight loop.
            time.sleep(1)
    return StreamingHttpResponse(event_generator(), content_type="text/html")

Good questions — all three hit the core of what makes this demo work. Let me break them down.

## 1. `activity_stream` — you're right, it's not *true* real-time

Here's the current code:

```python
def activity_stream(request):
    def event_generator():
        seen_ids = set()
        for _ in range(30):  # poll for 30 seconds
            new_sales = SaleEvent.objects.exclude(pk__in=seen_ids).order_by("-created_at")
            for sale in new_sales:
                seen_ids.add(sale.pk)
                yield f'<li id="event-{sale.pk}">{sale.product} sold in {sale.region} for ${sale.amount}</li>\n'
                time.sleep(1)
    return StreamingHttpResponse(event_generator(), content_type="text/html")
```

**Layman version:** Imagine you've ordered food and, instead of the kitchen calling you when it's ready, the waiter walks back to your table once a second carrying whatever's ready *right now* — and keeps doing that for 30 seconds. You're not being *pushed* updates the instant they happen; the kitchen is just repeatedly checking and handing over anything new.

**What's actually happening:**
- `StreamingHttpResponse` doesn't build one big response and send it. It holds the HTTP connection **open** and sends whatever the generator `yield`s, piece by piece.
- The generator runs a loop ~30 times (one loop ≈ 1 second because of `time.sleep(1)`).
- Each iteration, it queries the DB for rows whose `pk` isn't in `seen_ids`, emits each as an `<li>` line, and tracks them so it never resends.
- htmx 4 (Fetch API) reads this stream incrementally — each `<li>` renders the moment it lands.

**So is it real-time?** No — it's **polling on the server side, streamed over one connection on the client side**. It checks the DB every ~1s, so a new sale can lag up to a second before appearing. It also stops after 30 iterations. True real-time push would use WebSockets or SSE; this is a pragmatic "near-real-time" hack that's the whole point of the tutorial — the Fetch rewrite makes one open connection stream usable without extra JS.

> Note: as written, `time.sleep(1)` is inside the `for sale` loop, so it sleeps once *per new row*, not once per poll. If 5 sales arrive at once, they'll stream out ~1s apart.

## 2. `innerMorph` vs `outerMorph`

Both are "smart update" strategies. Morphing diffs the new HTML against what's on the page and only patches what changed — so focus, scroll position, and half-typed input values survive.

**Layman version:** `inner` = redecorate *inside* the box but keep the box. `outer` = replace the box itself (and its contents) with a new one — but carefully, preserving anything still the same.

- **`innerMorph`** → morphs the **children** of the target; the target element itself stays. Used on the filter form: `#sales-table` div stays put, its inner `<table>` gets updated.

- **`outerMorph`** → morphs the target **and** its children (the element can itself be replaced). Used on each row: the `<tr id="row-5">` is swapped for the edit-form version, then back — the element with that id is the unit being replaced.

Rule of thumb: use `innerMorph` when the container is a fixed shell; use `outerMorph` when the element itself is the thing being traded out (a read-only row ↔ an edit row).

## 3. `hx-trigger="intersect once"`

Two modifiers on one trigger:

- **`intersect`** → "fire when this element scrolls into the viewport" (uses the browser's IntersectionObserver).
- **`once`** → "only the first time — then never again."

**Layman version:** "The moment the activity panel becomes visible on screen, fetch the stream — and don't keep re-fetching it every time you scroll past."

It's on `#activity-log`, which sits at the bottom of the dashboard. So the stream doesn't start on page load; it lazy-starts the first time you scroll down to it. `once` is essential here — without it, htmx would fire a new `hx-get` every time the list re-enters view, spawning duplicate streams.

**How it all chains together:** page loads → table + stats render → you scroll → `intersect once` fires one `GET` to `activity_stream` → the open connection drips `<li>`s into `#activity-log` via `beforeend` → meanwhile clicking a row morphs it to an edit form, and saving fires a single POST whose `hx-partial` response updates the row *and* the stats bar at once.

Want me to change the stream to a `sleep`-per-poll (so it's a true once-a-second check) or make it run longer than 30s?
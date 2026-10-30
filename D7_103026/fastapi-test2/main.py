import asyncio
import time
from typing import Dict, AsyncGenerator
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

app = FastAPI(title="Real-Time Analytics & Notification Service")

# Fake DB & Shared Metrics
INVENTORY_STOCK: Dict[str, int] = {"ITEM_A": 100}
METRICS_COUNTER = {"total_processed": 0}


# --- Models ---
class PurchaseRequest(BaseModel):
    item_id: str
    quantity: int = Field(..., gt=0)
    email: str


# --- Helper Background Function ---
def send_confirmation_email_sync(email: str, item_id: str, qty: int):
    """Simulates sending an email via external SMTP (takes 1.5 seconds)."""
    time.sleep(1.5)
    print(f"[EMAIL SENT] Sent receipt to {email} for {qty}x {item_id}")


async def send_confirmation_email(email: str, item_id: str, qty: int):
    await run_in_threadpool(send_confirmation_email_sync, email, item_id, qty)


# --- Middleware ---
@app.middleware("http")
async def log_request_body_middleware(request: Request, call_next):
    """
    BUG ALERT 1: Reading request.body() directly inside middleware.
    What happens to request.stream() for downstream route handlers?
    """
    body = await request.body()
    print(f"[LOG] Request path: {request.url.path} | Payload size: {len(body)} bytes")

    response = await call_next(request)
    return response


# --- Endpoints ---
@app.post("/v1/purchase")
async def process_purchase(payload: PurchaseRequest, background_tasks: BackgroundTasks):
    # Check inventory
    current_stock = INVENTORY_STOCK.get(payload.item_id, 0)
    if current_stock < payload.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    # Simulate async I/O reservation delay
    await asyncio.sleep(0.1)

    # BUG ALERT 2: Non-atomic state updates under async concurrency
    INVENTORY_STOCK[payload.item_id] -= payload.quantity
    METRICS_COUNTER["total_processed"] += 1

    # BUG ALERT 3: How is a synchronous blocking function added to BackgroundTasks correctly?
    # background_tasks.add_task(...)
    # background_tasks.add_task(send_confirmation_email_sync(payload.email, payload.item_id, payload.quantity))
    background_tasks.add_task(send_confirmation_email, payload.email, payload.item_id, payload.quantity)

    return {"status": "SUCCESS", "remaining_stock": INVENTORY_STOCK[payload.item_id]}


@app.get("/v1/live-feed/{item_id}")
async def stream_live_stock(item_id: str):
    """
    Streams live inventory updates via Server-Sent Events (SSE).

    BUG ALERT 4: What happens when the client disconnects prematurely?
    How should generator cleanup and asyncio.CancelledError be handled?
    """
    async def stock_event_generator() -> AsyncGenerator[str, None]:
        while True:
            stock = INVENTORY_STOCK.get(item_id, 0)
            yield f"data: {{\"item_id\": \"{item_id}\", \"stock\": {stock}}}\n\n"
            await asyncio.sleep(1.0)

    return StreamingResponse(stock_event_generator(), media_type="text/event-stream")

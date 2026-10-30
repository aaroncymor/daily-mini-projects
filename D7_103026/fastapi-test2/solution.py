import asyncio
import time
from typing import Dict, AsyncGenerator
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Real-Time Analytics & Notification Service")

# Fake DB, Shared Metrics & Mutex
INVENTORY_STOCK: Dict[str, int] = {"ITEM_A": 100}
METRICS_COUNTER = {"total_processed": 0}
stock_lock = asyncio.Lock()


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


# --- Middleware ---
@app.middleware("http")
async def log_request_body_middleware(request: Request, call_next):
    """
    Bug #1: Middleware Consuming Request Stream
    Calling await request.body() reads the internal ASGI byte stream into memory once.
    When downstream route handlers (or Pydantic body parsers) attempt to consume
    request.stream(), the stream is already exhausted, resulting in request hangs
    or 422 Unprocessable Entity.

    Fix: You must cache/replace the request receive channel or reset request._body:
    """
    # 1. Read request body bytes
    body = await request.body()
    print(f"[LOG] Request path: {request.url.path} | Payload size: {len(body)} bytes")

    # 2. Reset the receive channel stream for downstream route handlers
    async def receive():
        return {"type": "http.request", "body": body}

    request = Request(request.scope, receive=receive)
    return await call_next(request)


# --- Endpoints ---
@app.post("/v1/purchase")
async def process_purchase(payload: PurchaseRequest, background_tasks: BackgroundTasks):
    """
    Bug #2: Race Conditions & Non-Atomic Checks
    Between reading current_stock and executing
    INVENTORY_STOCK[payload.item_id] -= payload.quantity, the await asyncio.sleep(0.1)
    pause yields control back to the event loop. If multiple concurrent requests
    hit the endpoint during this gap, multiple tasks pass the stock check
    before any inventory is subtracted, leading to overselling (negative inventory).

    Fix: Protect critical state mutation blocks using an asyncio.Lock():
    """
    # Atomic critical section guarded by Lock
    async with stock_lock:
        current_stock = INVENTORY_STOCK.get(payload.item_id, 0)
        if current_stock < payload.quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock")

        await asyncio.sleep(0.1)

        INVENTORY_STOCK[payload.item_id] -= payload.quantity
        METRICS_COUNTER["total_processed"] += 1
        remaining_stock = INVENTORY_STOCK[payload.item_id]

    # Bug #3: Background Tasks Signature
    # Starlette automatically offloads synchronous functions in BackgroundTasks to a thread pool
    # Pass the function reference directly:
    background_tasks.add_task(
        send_confirmation_email_sync, payload.email, payload.item_id, payload.quantity
    )

    return {"status": "SUCCESS", "remaining_stock": remaining_stock}


@app.get("/v1/live-feed/{item_id}")
async def stream_live_stock(item_id: str, request: Request):
    """
    Bug #4: SSE Generator Unhandled Cancellation
    When an HTTP/SSE client disconnects prematurely, Starlette cancels the
    underlying generator task. If asyncio.CancelledError is not caught inside
    the generator function, lingering references or connection pools fail to
    clean up, and error logs get flooded with unhandled cancellation exceptions.

    Fix: Wrap the generator loop in a try...except asyncio.CancelledError block or monitor await request.is_disconnected()
    """
    async def stock_event_generator() -> AsyncGenerator[str, None]:
        try:
            while True:
                if await request.is_disconnected():
                    print(f"[SSE] Client disconnected early from item {item_id}")
                    break

                stock = INVENTORY_STOCK.get(item_id, 0)
                yield f"data: {{\"item_id\": \"{item_id}\", \"stock\": {stock}}}\n\n"
                await asyncio.sleep(1.0)
        except asyncio.CancelledError:
            print(f"[SSE] Stream task cancelled for item {item_id}")
            raise

    return StreamingResponse(stock_event_generator(), media_type="text/event-stream")

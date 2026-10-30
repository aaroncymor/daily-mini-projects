### **Difficulty Level:** Expert

Here is a second high-frequency interview scenario focusing on **Middleware, Async Race Conditions, Background Tasks, and Streaming/Server-Sent Events (SSE)**.

---

### **Context & Scenario**

You are reviewing an **Async Live Stock/Crypto Tracker & Notification Service**.

The code below has **4 critical architectural bugs**:

1. **Shared State Mutation / Race Condition:** Dynamic request tracking updates a shared mutable dictionary without concurrency guards during asynchronous yields/pauses.
2. **Background Task Memory Leak & Scope Error:** A background task function is invoked incorrectly, causing context drops or thread execution issues.
3. **ASGI Middleware Request Body Consumption:** A custom logging middleware reads `request.body()` directly, causing subsequent route handlers to hang or fail with empty request payloads.
4. **Unhandled Generator Cancellation in Event Streaming:** An SSE (Server-Sent Event) generator endpoint fails to catch `asyncio.CancelledError` when clients disconnect, leaving orphaned tasks hanging in memory.

---

### **Setup Instructions**

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install required dependencies
pip install fastapi uvicorn pydantic

# 3. Run the application
uvicorn main:app --reload

```

---

### **Starter Code (`main.py`)**

```python
import asyncio
import time
from typing import Dict, AsyncGenerator
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException, status
from fastapi.responses import StreamingResponse
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
    background_tasks.add_task(send_confirmation_email_sync(payload.email, payload.item_id, payload.quantity))

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

```

---

### **Tasks & Requirements**

1. **Fix Middleware Body Consumption:**
* Modify `log_request_body_middleware` so that reading the request body in middleware does not consume the stream, allowing `process_purchase` to parse `PurchaseRequest` without hanging or throwing `422 Unprocessable Entity`.


2. **Async Concurrency & Atomic Operations:**
* Prevent race conditions on `INVENTORY_STOCK` when multiple concurrent requests hit `/v1/purchase`. Use an `asyncio.Lock` or atomic state pattern.


3. **Background Task Execution:**
* Fix `background_tasks.add_task(...)` so `send_confirmation_email_sync` runs asynchronously in the background thread pool after returning the HTTP response, rather than executing synchronously during the route handler pass.


4. **SSE Generator Cancellation Handling:**
* Handle client disconnects gracefully inside `stock_event_generator` by catching `asyncio.CancelledError` or monitoring `request.is_disconnected()` to ensure background tasks and resources are cleaned up cleanly.



---

Take your time to analyze and refactor the code! Reply with your updated [118;1:3uimplementation or breakdown when you are ready.

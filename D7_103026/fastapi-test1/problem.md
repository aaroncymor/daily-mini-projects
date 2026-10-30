Difficulty Level: Expert
Here is an interview-grade FastAPI problem designed to test senior/full-stack concepts commonly asked during technical screening rounds: async behavior, dependency injection, exception handlers, and custom middleware/event loop safety.

Context & Scenario
You are reviewing a mini backend service responsible for managing Order Processing with Rate-Limiting & Idempotency Check.

The code below has 4 critical issues/bugs commonly encountered in production FastAPI apps:

An async blocking call bottleneck (thread pool / event loop starvation).

A broken Dependency Injection implementation for rate-limiting context across routes.

Incorrect Pydantic v2 validation / custom error response payload structure.

A missing exception handler or state leakage issue.

Setup Instructions
Bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install required dependencies
pip install fastapi uvicorn pydantic

# 3. Run the starter code
uvicorn main:app --reload
Starter Code (main.py)
Python
import asyncio
import time
from typing import Dict, Optional
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Order Execution Service")

# Fake DB / Cache storage
PROCESSED_ORDERS: Dict[str, dict] = {}
RATE_LIMIT_STORE: Dict[str, int] = {}


# --- Models ---
class OrderPayload(BaseModel):
    idempotency_key: str = Field(..., min_length=8)
    user_id: int
    amount: float = Field(..., gt=0)
    items: list[str]


class OrderResponse(BaseModel):
    order_id: str
    status: str
    amount: float


# --- Slow Legacy Payment Gateway SDK (Simulated) ---
def legacy_payment_gateway_sync_charge(user_id: int, amount: float) -> bool:
    """Simulates a blocking synchronous legacy library call (takes 2 seconds)."""
    time.sleep(2.0)
    return True


# --- Dependencies ---
class RateLimiter:
    def __init__(self, max_requests: int = 5):
        self.max_requests = max_requests

    # BUG ALERT: Check how dependencies are invoked & state is evaluated per-request
    async def __call__(self, request: Request):
        client_ip = request.client.host if request.client else "unknown"
        current_count = RATE_LIMIT_STORE.get(client_ip, 0)

        if current_count >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        RATE_LIMIT_STORE[client_ip] = current_count + 1


# --- Custom Exception ---
class PaymentGatewayError(Exception):
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code


# TODO: Register custom exception handler for PaymentGatewayError
# It should return a HTTP 502 Bad Gateway with JSON: {"error_code": code, "detail": message}


# --- Endpoint ---
@app.post(
    "/v1/orders/process",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(max_requests=3))]
)
async def process_order(payload: OrderPayload):
    # 1. Idempotency Check
    if payload.idempotency_key in PROCESSED_ORDERS:
        existing = PROCESSED_ORDERS[payload.idempotency_key]
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"order_id": existing["order_id"], "status": "DUPLICATE", "amount": existing["amount"]}
        )

    # 2. Synchronous Payment Gateway Execution
    # BUG ALERT: Calling blocking synchronous I/O directly inside an async def endpoint block!
    success = legacy_payment_gateway_sync_charge(payload.user_id, payload.amount)

    if not success:
        raise PaymentGatewayError(message="Transaction rejected by upstream provider", code="PAYMENT_REJECTED")

    # 3. Store Order
    order_data = {
        "order_id": f"ORD-{payload.idempotency_key[:6].upper()}",
        "status": "COMPLETED",
        "amount": payload.amount
    }
    PROCESSED_ORDERS[payload.idempotency_key] = order_data

    return order_data
Tasks & Requirements
Event Loop Non-Blocking Execution:

Modify the execution of legacy_payment_gateway_sync_charge so that high concurrency traffic to /v1/orders/process does not block the main Asyncio Event Loop. (Hint: FastAPI's thread pool executor or concurrency utilities).

Fix Return Type Contract / Response Model:

Resolving duplicate idempotency keys currently breaks response typing when returning JSONResponse vs OrderResponse. Ensure returning duplicate order responses strictly satisfies OpenAPI schema/types without validation bypass warnings.

Global Custom Exception Handler:

Implement @app.exception_handler(PaymentGatewayError) to handle upstream payment failures gracefully and output a structured 502 Bad Gateway response.

Rate Limiter Fix:

Ensure rate limit tracking uses standard FastAPI dependency injection practices or request state handling.

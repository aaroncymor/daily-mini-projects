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
async def legacy_payment_gateway_sync_charge(user_id: int, amount: float) -> bool:
    """Simulates a blocking synchronous legacy library call (takes 2 seconds)."""
    await asyncio.sleep(1.0)
    return False


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
        print("RATE LIMIT STORE...", RATE_LIMIT_STORE)


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
    # ANSWER: I turned the legacy code into asynchronous
    success = await legacy_payment_gateway_sync_charge(payload.user_id, payload.amount)

    if not success:
        # ANSWER: I return JSONResponse instead of the class PaymentGatewayError
        # Because I can put key value pairs for error code and message and
        # also the status code
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"error_code": "PAYMENT_REJECTED", "message": "Transaction failed."}
        )

    # 3. Store Order
    order_data = {
        "order_id": f"ORD-{payload.idempotency_key[:6].upper()}",
        "status": "COMPLETED",
        "amount": payload.amount
    }
    PROCESSED_ORDERS[payload.idempotency_key] = order_data
    return order_data

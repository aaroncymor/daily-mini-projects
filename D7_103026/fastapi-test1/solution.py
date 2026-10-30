import asyncio
import time
from collections import defaultdict
from typing import Dict, List
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Order Execution Service")

# Fake DB / Cache storage
PROCESSED_ORDERS: Dict[str, dict] = {}


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


# --- Legacy Sync SDK (Unchanged) ---
def legacy_payment_gateway_sync_charge(user_id: int, amount: float) -> bool:
    time.sleep(1.0)  # Blocking I/O
    return True


# --- Exceptions & Handlers ---
class PaymentGatewayError(Exception):
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code


@app.exception_handler(PaymentGatewayError)
async def payment_gateway_exception_handler(request: Request, exc: PaymentGatewayError):
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"error_code": exc.code, "message": exc.message}
    )


# --- Sliding-Window Rate Limiter ---
class RateLimiter:
    def __init__(self, max_requests: int = 3, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)

    async def __call__(self, request: Request):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # Clear expired timestamps
        self.requests[client_ip] = [
            ts for ts in self.requests[client_ip]
            if now - ts < self.window_seconds
        ]

        if len(self.requests[client_ip]) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        self.requests[client_ip].append(now)


# --- Endpoint ---
@app.post(
    "/v1/orders/process",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(max_requests=3, window_seconds=60))]
)
async def process_order(payload: OrderPayload):
    # 1. Idempotency Check
    if payload.idempotency_key in PROCESSED_ORDERS:
        return PROCESSED_ORDERS[payload.idempotency_key]

    # 2. Non-blocking Execution of Sync Payment Gateway
    success = await run_in_threadpool(
        legacy_payment_gateway_sync_charge, payload.user_id, payload.amount
    )

    if not success:
        raise PaymentGatewayError(
            message="Transaction failed.",
            code="PAYMENT_REJECTED"
        )

    # 3. Store Order
    order_data = {
        "order_id": f"ORD-{payload.idempotency_key[:6].upper()}",
        "status": "COMPLETED",
        "amount": payload.amount
    }
    PROCESSED_ORDERS[payload.idempotency_key] = order_data
    return order_data

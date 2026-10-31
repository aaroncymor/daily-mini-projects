### **Difficulty Level:** Expert

Here is a third technical challenge focusing on **OAuth2/JWT Security, Custom ASGI Middleware, Database Connection Lifecycles, and Async Context Managers**.

---

### **Context & Scenario**

You are reviewing a high-throughput **Microservice API Gateway & Auth Service**.

The starter code below contains **4 critical bugs/vulnerabilities**:

1. **Unsafe Async Database/Resource Initialization:** Database connection pools are created at module import time rather than managing lifecycle events safely via `lifespan` context managers.
2. **JWT / Dependency Injection Scope Leakage:** Global state or mutable defaults in auth dependencies cause token context to bleed across concurrent user requests.
3. **ASGI Scope Mutation in Middleware:** A custom header-injecting middleware mutates the raw ASGI `scope` tuple in an invalid way, causing downstream crashes on HTTP response streaming.
4. **Incorrect Query Parameter Validation for Pagination:** Complex query parameters with Pydantic models are defined incorrectly on a `GET` endpoint, causing FastAPI to expect them in the HTTP request body instead of the query string.

---

### **Setup Instructions**

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install required dependencies
pip install fastapi uvicorn pydantic pyjwt

# 3. Run the application
uvicorn main:app --reload

```

---

### **Starter Code (`main.py`)**

```python
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Optional
import jwt
from fastapi import FastAPI, Depends, HTTPException, Request, Header, status
from pydantic import BaseModel, Field

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"

# Simulated Global Database Pool Connection
class DatabasePool:
    def __init__(self):
        self.is_connected = False

    async def connect(self):
        await asyncio.sleep(0.1)
        self.is_connected = True
        print("[DB] Connected to database pool.")

    async def disconnect(self):
        self.is_connected = False
        print("[DB] Disconnected from database pool.")

# BUG ALERT 1: Initializing async resources globally at module import time
db_pool = DatabasePool()
asyncio.run(db_pool.connect())  # Crash/Issue when imported by Uvicorn workers!


# --- Models ---
class UserProfile(BaseModel):
    user_id: int
    role: str


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)


# --- Dependencies ---
class AuthBearer:
    def __init__(self):
        # BUG ALERT 2: Mutable instance state shared across all requests
        self.current_user: Optional[UserProfile] = None

    async def __call__(self, authorization: str = Header(...)) -> UserProfile:
        try:
            token = authorization.split(" ")[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            # Mutating shared instance attribute!
            self.current_user = UserProfile(user_id=payload["sub"], role=payload["role"])
            return self.current_user
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid authorization token")


auth_dependency = AuthBearer()


# --- ASGI Middleware ---
# BUG ALERT 3: Incorrectly mutating ASGI scope directly
class CustomHeaderMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Mutating scope['headers'] directly with invalid tuple structure
            scope["headers"].append(("x-gateway-processed", "true"))
        await self.app(scope, receive, send)


app = FastAPI(title="Gateway Service")
app.add_middleware(CustomHeaderMiddleware)


# --- Endpoints ---

# BUG ALERT 4: GET endpoint trying to use a Pydantic model directly as query params
@app.get("/v1/items")
async def list_items(
    pagination: PaginationParams,
    user: UserProfile = Depends(auth_dependency)
):
    if not db_pool.is_connected:
        raise HTTPException(status_code=500, detail="Database connection offline")

    return {
        "user_id": user.user_id,
        "page": pagination.page,
        "page_size": pagination.page_size,
        "items": [f"Item_{i}" for i in range(pagination.page_size)]
    }

```

---

### **Tasks & Requirements**

1. **Fix Application Lifespan (`@asynccontextmanager`):**
* Replace the top-level `asyncio.run(db_pool.connect())` with FastAPI's modern `lifespan` context manager so `db_pool.connect()` and `db_pool.disconnect()` run safely within Uvicorn's event loop lifecycle.


2. **Fix Dependency State Leakage:**
* Refactor `AuthBearer` so decoding tokens does not store user state on a shared singleton instance, preventing request context leaks across concurrent users.


3. **Fix ASGI Scope Header Mutation:**
* Modify `CustomHeaderMiddleware` to ensure header keys/values added to `scope["headers"]` follow the ASGI specification (byte strings, e.g., `(b"x-gateway-processed", b"true")`).


4. **Pydantic Model as GET Query Parameters:**
* Fix `list_items` so that `PaginationParams` correctly parses parameters from the URL query string (`/v1/items?page=1&page_size=10`) rather than expecting an HTTP request body. *(Hint: `Depends()`).*



---

Take your t[118;1:3uime to analyze and submit your code solution when ready!

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import models, schemas, security
from app.database import Base, engine, get_db


# Create database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI Auth + SQLite Demo")


# OAuthPasswordBearer tells FastAPI that the token comes from /login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# --- DEPENDENCY: Get Current Authenticated User ---
def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(
            token, security.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = (
        db.query(models.User)
        .filter(models.User.username == token_data.username)
        .first()
    )
    if not user:
        raise credentials_exception

    return user


# --- 1. REGISTER USER ---
@app.post(
    "/register",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if username or email already exists
    existing_user = (
        db.query(
            (models.User.username == user_in.username)
            | (models.User.email == user_in.email)
        )
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    # Hash password & save user
    db_user = models.User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=security.hash_password(user_in.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


# --- 2. LOGIN (Generates JWT) ---
@app.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = (
        db.query(models.User)
        .filter(models.User.username == form_data.username)
        .first()
    )
    if not user or not security.verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# --- 3. PROTECTED ROUTE ---
@app.get("/users/me", response_model=schemas.UserResponse)
def read_current_user(current_user: models.User = Depends(get_current_user)):
    return current_user

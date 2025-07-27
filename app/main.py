from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import asyncio

from .auth import authenticate_user, create_access_token, get_current_user, get_api_key
from .config import settings
from .db import create_engine, get_sessionmaker, init_db
from . import cache

app = FastAPI(title="PI Classifier API", openapi_url="/api/v1/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1024)

limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda r, e: JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"}))
app.add_middleware(SlowAPIMiddleware)


engine = create_engine()
SessionLocal = get_sessionmaker(engine)


@app.on_event("startup")
async def startup_event() -> None:
    await init_db(engine)


async def get_db():
    async with SessionLocal() as session:
        yield session


class TextIn(BaseModel):
    text: str


class TextOut(BaseModel):
    label: str
    score: float


@app.post("/api/v1/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    token = create_access_token({"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}


@app.get("/api/v1/models")
async def models(current_user: dict = Depends(get_current_user)):
    return ["pi-base-model"]


async def fake_classify(text: str) -> TextOut:
    key = cache.text_key("classify", text)
    cached = await cache.cache_get(key)
    if cached:
        return TextOut(**cached)
    await asyncio.sleep(0.1)
    result = TextOut(label="PI", score=0.9)
    await cache.cache_set(key, result.dict(), ttl=settings.classification_ttl)
    return result


from fastapi import Request


@app.post("/api/v1/classify/text", response_model=TextOut)
@limiter.limit(settings.rate_limit)
async def classify_text(request: Request, payload: TextIn, api_key: str = Depends(get_api_key)):
    return await fake_classify(payload.text)


@app.post("/api/v1/classify/batch", response_model=list[TextOut])
@limiter.limit(settings.rate_limit)
async def classify_batch(request: Request, payload: list[TextIn], api_key: str = Depends(get_api_key)):
    results = []
    for item in payload:
        results.append(await fake_classify(item.text))
    return results

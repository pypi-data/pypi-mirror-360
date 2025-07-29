from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict

# Router imports

app: FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]: ...
async def root() -> Dict[str, str]: ...

__all__ = ["app"]

from fastapi import FastAPI
from typing import AsyncIterator, Dict

# Router imports

app: FastAPI

async def lifespan(app: FastAPI) -> AsyncIterator[None]: ...
async def root() -> Dict[str, str]: ...

__all__ = ["app"]

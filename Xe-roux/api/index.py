"""Serverless entry point for Xe-roux FastAPI backend when deployed on Vercel.

Vercel looks for a Python module that exposes a top-level variable named ``app``.
This file simply imports the already configured FastAPI instance from ``app.main``
and re-exports it so that the Vercel Python runtime can serve it as a
Serverless Function.

To run locally for debugging:
    uvicorn api.index:app --reload --port 8000
"""

from app.main import app  # noqa: F401  # re-export for Vercel
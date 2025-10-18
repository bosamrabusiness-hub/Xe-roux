"""Vercel entrypoint for FastAPI backend.

This tiny wrapper allows Vercel's Python runtime to locate and serve the
main FastAPI application contained in the monorepo under ``Xe-roux/app``.

Vercel detects the ``api`` directory as the default place for Serverless
Functions (similar to Next.js conventions). By exposing a module-level
``app`` variable that is an ASGI application, Vercel will automatically
launch the FastAPI app using its internal ASGI server.
"""
from __future__ import annotations

import pathlib
import sys
from typing import TYPE_CHECKING

# ----------------------------------------------------------------------------
# Ensure the backend package path is importable
# ----------------------------------------------------------------------------
ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent  # repository root
BACKEND_DIR = ROOT_DIR / "Xe-roux"
if BACKEND_DIR.exists():
    sys.path.append(str(BACKEND_DIR))

# Now we can import the FastAPI "app" instance from the backend package.
try:
    from app.main import app  # type: ignore
except ModuleNotFoundError as exc:  # pragma: no cover
    # Give a helpful error if the import fails during deployment.
    raise RuntimeError(
        "Could not import FastAPI application from Xe-roux/app/main.py. "
        "Ensure the path is correct and all dependencies are installed."
    ) from exc

if TYPE_CHECKING:  # pragma: no cover
    # Provide type hint for editors & static analysers
    from fastapi import FastAPI

    assert isinstance(app, FastAPI)
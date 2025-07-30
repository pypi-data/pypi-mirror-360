"""Unified server combining MCP and FastAPI functionality.

This server provides:
- MCP tools at /mcp/ endpoint (log_step, ask_question, end_session)
- REST API endpoints at /api/v1/*
- Shared JWT authentication for both interfaces
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.config import settings

# Import the pre-configured MCP server
from servers.mcp.server import mcp

# Import FastAPI routers
from servers.fastapi.routers import agent_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the MCP app with streamable-http transport
mcp_app = mcp.http_app(path="/")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Combined lifespan for both MCP and FastAPI functionality."""
    # Use the MCP app's lifespan to ensure proper initialization
    async with mcp_app.lifespan(app):
        logger.info("Unified server starting up")
        logger.info("MCP endpoints available at: /mcp/")
        logger.info("REST API endpoints available at: /api/v1/*")
        yield
        logger.info("Shutting down unified server")


# Create FastAPI app with MCP's lifespan
app = FastAPI(
    title="Agent Dashboard Unified Server",
    description="Combined MCP and REST API for agent monitoring and interaction",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent_router, prefix="/api/v1")
app.mount("/mcp", mcp_app)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Agent Dashboard Unified Server",
        "version": "1.0.0",
        "endpoints": {
            "mcp": "/mcp/ (MCP tools via Streamable HTTP)",
            "api": "/api/v1/* (REST API endpoints)",
            "docs": "/docs (API documentation)",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "server": "unified"}


def main():
    """Run the unified server."""
    import uvicorn

    # Log configuration for debugging
    logger.info(f"Starting unified server on port: {settings.mcp_server_port}")
    logger.info("Database URL configured.")
    logger.info(
        f"JWT public key configured: {'Yes' if settings.jwt_public_key else 'No'}"
    )

    try:
        uvicorn.run(
            "servers.app:app",
            host="0.0.0.0",
            port=settings.mcp_server_port,
            reload=settings.environment == "development",
        )
    except Exception as e:
        logger.error(f"Failed to start unified server: {e}")
        raise


if __name__ == "__main__":
    main()

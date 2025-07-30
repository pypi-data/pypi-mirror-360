from fastapi import FastAPI, HTTPException, Depends, Security
import logging
import argparse
from contextlib import asynccontextmanager
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Annotated
import socket

from pi_inference_scheduler import env

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_host_info() -> tuple[str, str]:
    hostname: str = socket.gethostname()
    ip_address: str = socket.gethostbyname(hostname)
    return hostname, ip_address


hostname, ip = get_host_info()
print(f"Hostname: {hostname}")
print(f"IP Address: {ip}")

# Add security scheme
security = HTTPBearer()


# Add authentication dependency
async def verify_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Security(security)],
) -> str:
    """
    Verify the authentication token.

    Parameters:
    - credentials (HTTPAuthorizationCredentials): The credentials containing the bearer token

    Returns:
    - str: The verified token

    Raises:
    - HTTPException: If the token is invalid
    """
    if env.AUTH_TOKEN == "":
        return credentials.credentials
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized. Please provide a valid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if credentials.credentials != env.TOPLOCVALIDATOR_AUTH_TOKEN:
        raise HTTPException(
            status_code=403,
            detail="Forbidden. The authentication token is incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    yield
    # Shutdown

app = FastAPI(lifespan=lifespan)


@app.get("/", tags=["Health Check"])
async def root(token: Annotated[str, Depends(verify_token)]):
    """
    Root endpoint to check if the server is running.
    """
    return "OK"


def main():
    """Entry point for the CLI command."""
    parser = argparse.ArgumentParser(description="Scheduler Server")
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the server on (default: 8000)",
    )
    args = parser.parse_args()

    # Print args table using rich
    from rich.table import Table
    from rich.console import Console

    console = Console()
    table = Table(title="Server Configuration")
    table.add_column("Parameter", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Port", str(args.port))
    console.print(table)

    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main()

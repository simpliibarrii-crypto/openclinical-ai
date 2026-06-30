"""CLI entry point for OpenClinical AI runtime.

Provides commands for starting the server, listing models, and checking health.
"""

import typer
import uvicorn

from runtime.config import settings

app = typer.Typer(
    name="openclinical",
    help="OpenClinical AI — sovereign clinical AI runtime",
    add_completion=False,
)


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Bind address"),
    port: int = typer.Option(8000, help="Bind port"),
    reload: bool = typer.Option(False, help="Enable auto-reload for development"),
    log_level: str = typer.Option("info", help="Log level"),
):
    """Start the OpenClinical AI runtime server."""
    typer.echo(f"Starting OpenClinical AI runtime on {host}:{port}")
    uvicorn.run(
        "runtime.server:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
    )


@app.command()
def health(
    url: str = typer.Option("http://localhost:8000", help="Server URL"),
):
    """Check runtime health."""
    import httpx

    try:
        resp = httpx.get(f"{url}/health", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        typer.echo(f"Status:   {data['status']}")
        typer.echo(f"Version:  {data['version']}")
        typer.echo(f"Models:   {data['models_loaded']}")
        typer.echo(f"Tenants:  {data['tenants']}")
        typer.echo(f"Uptime:   {data['uptime_seconds']:.1f}s")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

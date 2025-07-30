import click
from .core import (
    main_logic,
    discover_logic,
    show_status,
    stop_cluster_tunnel,
    stop_all_tunnels
)

@click.group()
def cli():
    """kubetap: tap into private Kubernetes clusters via bastion tunnels."""
    pass

# -------- GKE commands --------
@cli.group()
def gke():
    """Google Kubernetes Engine (GKE) operations"""
    pass

@gke.command()
def discover():
    """Discover GKE clusters across projects"""
    discover_logic()

@gke.command()
@click.argument("cluster")
def start(cluster):
    """Start tunnel to a GKE cluster"""
    main_logic(cluster)

@gke.command()
@click.argument("cluster")
def stop(cluster):
    """Stop tunnel to a GKE cluster"""
    stop_cluster_tunnel(cluster)

@gke.command(name="stop-all")
def stop_all():
    """Stop all active GKE tunnels"""
    stop_all_tunnels()

@gke.command()
def status():
    """Check GKE tunnel status"""
    show_status()

# -------- AWS EKS --------
@cli.group()
def eks():
    """Amazon EKS operations"""
    pass

@eks.command()
def discover():
    click.secho("🚧 EKS support not yet implemented.", fg="yellow")

@eks.command()
@click.argument("cluster")
def start(cluster):
    click.secho("🚧 EKS support not yet implemented.", fg="yellow")

# -------- Azure AKS --------
@cli.group()
def aks():
    """Azure AKS operations"""
    pass

@aks.command()
def discover():
    click.secho("🚧 AKS support not yet implemented.", fg="yellow")

@aks.command()
@click.argument("cluster")
def start(cluster):
    click.secho("🚧 AKS support not yet implemented.", fg="yellow")

# -------- Utility --------
@cli.command()
def server():
    """Run the local kubetap API server."""
    from .server import run_server
    run_server()

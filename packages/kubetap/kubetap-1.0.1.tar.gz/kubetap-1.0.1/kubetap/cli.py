import click
from .core import (
    main_logic,
    discover_logic,
    show_status,
    stop_cluster_tunnel,
    stop_all_tunnels,
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
@click.argument("cluster", required=False)
@click.option("--last", is_flag=True, help="Reuse the last-used cluster")
def start(cluster, last):
    """Start tunnel to a GKE cluster"""
    if last:
        cluster = "--last"
    main_logic(cluster)

@gke.command()
@click.argument("cluster", required=False)
@click.option("--last", is_flag=True, help="Reuse the last-used cluster")
def stop(cluster, last):
    """Stop tunnel to a GKE cluster"""
    if last:
        cluster = "--last"
    stop_cluster_tunnel(cluster)

@gke.command(name="stop-all")
def stop_all():
    """Stop all active GKE tunnels"""
    stop_all_tunnels()

@gke.command()
def status():
    """Check GKE tunnel status"""
    show_status()

import os
import sys
import yaml
import json
import time
import signal
import subprocess
import psutil
from rich.console import Console
from rich.table import Table
from shutil import which

KUBETAP_DIR = os.path.expanduser("~/.kubetap")
os.makedirs(KUBETAP_DIR, exist_ok=True)

CONFIG_FILE = os.path.join(KUBETAP_DIR, "ssh-tunnel-config.yaml")
PORT_MAP_FILE = os.path.join(KUBETAP_DIR, "cluster-port-map.yaml")
PID_MAP_FILE = os.path.join(KUBETAP_DIR, "tunnel-pids.yaml")
CLIENT_CONFIG_FILE = os.path.join(KUBETAP_DIR, "jump-config.yaml")
BASE_PORT = 7443

console = Console()

def load_yaml_file(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    return {}

def save_yaml_file(path, data):
    with open(path, "w") as f:
        yaml.dump(data, f)

def load_client_config():
    config = load_yaml_file(CLIENT_CONFIG_FILE)
    required_keys = ("project", "zone", "bastion")

    if all(k in config for k in required_keys):
        console.print("[cyan]🧭 Current jump host:[/cyan]")
        console.print(f"  [bold]Project:[/bold] {config['project']}")
        console.print(f"  [bold]Zone:   [/bold] {config['zone']}")
        console.print(f"  [bold]Bastion:[/bold] {config['bastion']}")
        return config

    console.print("[yellow]⚠️ Jump host is not configured or incomplete.[/yellow]")
    answer = input("Would you like to set up a jump host now? (y/n): ").strip().lower()
    if answer != "y":
        console.print("[red]❌ Missing configuration. Exiting.[/red]")
        sys.exit(1)

    # Suggest gcloud helpers
    console.print("\n[blue]💡 Tip: Use the following gcloud commands to find values:[/blue]")
    console.print("  • [green]gcloud projects list[/green] → list all accessible project IDs")
    console.print("  • [green]gcloud compute zones list[/green] → list available zones")
    console.print("  • [green]gcloud compute instances list --project=YOUR_PROJECT_ID[/green] → list VMs (bastions)\n")

    # Collect input
    config["project"] = input("Enter the GCP project ID: ").strip()
    config["zone"] = input("Enter the GCP zone (e.g. europe-west1-c): ").strip()
    config["bastion"] = input("Enter the bastion VM name: ").strip()

    # Save
    save_yaml_file(CLIENT_CONFIG_FILE, config)
    console.print("[green]✅ Jump host configuration saved.[/green]\n")
    return config


def check_tool_exists(tool):
    return which(tool) is not None

def ensure_prerequisites():
    missing = [t for t in ["gcloud", "ssh", "nc"] if not check_tool_exists(t)]
    if missing:
        console.print(f"[red]❌ Missing required tools: {', '.join(missing)}[/red]")
        sys.exit(1)

def check_gcloud_auth():
    try:
        result = subprocess.run(
            ["gcloud", "auth", "list", "--format=value(account)"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=True,
            text=True,
        )
        if not result.stdout.strip():
            raise Exception("No gcloud accounts found.")
    except Exception:
        console.print("[red]❌ You are not authenticated with gcloud.[/red]")
        console.print("[yellow]👉 Run [bold]gcloud auth login[/bold] in another terminal.[/yellow]")
        input("Press ENTER to continue after logging in...")

def get_all_projects():
    result = subprocess.run(
        ["gcloud", "projects", "list", "--format=value(projectId)"],
        stdout=subprocess.PIPE,
        text=True,
        check=True
    )
    return result.stdout.strip().splitlines()

def get_clusters(project):
    result = subprocess.run([
        "gcloud", "container", "clusters", "list",
        f"--project={project}",
        "--format=json"
    ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    return json.loads(result.stdout) if result.returncode == 0 and result.stdout.strip() else []

def is_cluster_accessible(name, location, project):
    result = subprocess.run([
        "gcloud", "container", "clusters", "describe", name,
        f"--region={location}",
        f"--project={project}"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.returncode == 0

def assign_ports(clusters, port_map):
    next_port = max(port_map.values(), default=BASE_PORT - 1) + 1
    updated = False
    for cluster_id in clusters:
        if cluster_id not in port_map:
            port_map[cluster_id] = next_port
            next_port += 1
            updated = True
    if updated:
        save_yaml_file(PORT_MAP_FILE, port_map)

def discover_clusters():
    ensure_prerequisites()
    check_gcloud_auth()

    console.print("[bold blue]🔍 Discovering GKE clusters...[/bold blue]")

    port_map = load_yaml_file(PORT_MAP_FILE)
    tunnel_config = {"clusters": {}}
    client_config = load_client_config()
    tunnel_config.update(client_config)

    all_projects = get_all_projects()

    for project in all_projects:
        clusters = get_clusters(project)
        if not clusters:
            continue

        for cluster in clusters:
            name = cluster["name"]
            location = cluster["location"]
            endpoint = cluster["endpoint"]
            cluster_id = f"gke_{project}_{location}_{name}"

            if not is_cluster_accessible(name, location, project):
                console.print(f"[yellow]⚠️ Skipping inaccessible cluster:[/yellow] {cluster_id}")
                continue

            assign_ports([cluster_id], port_map)
            tunnel_config["clusters"][cluster_id] = {
                "port": port_map[cluster_id],
                "ip": endpoint
            }

            console.print(f"[green]✅ Found:[/green] {cluster_id} ({endpoint})")

    save_yaml_file(CONFIG_FILE, tunnel_config)
    console.print("\n[bold green]✅ Discovery complete![/bold green] Use 'kubetap gke start <cluster>' to open a tunnel.")
    console.print("[cyan]🧠 Use 'kubetap gke status' to check tunnel states.[/cyan]")

def find_ssh_child_pid(parent_pid):
    try:
        parent = psutil.Process(parent_pid)
        for child in parent.children(recursive=True):
            if child.name() == "ssh":
                return child.pid
    except Exception:
        return None

def start_cluster_tunnel(cluster):
    config = load_yaml_file(CONFIG_FILE)
    clusters = config.get("clusters", {})
    if cluster not in clusters:
        console.print(f"[red]Unknown cluster: {cluster}[/red]")
        return

    info = clusters[cluster]
    port, ip = info["port"], info["ip"]
    bastion = config["bastion"]
    project = config["project"]
    zone = config["zone"]

    console.print(f"[blue]🔌 Starting tunnel for '{cluster}' on port {port}...[/blue]")

    cmd = [
        "gcloud", "compute", "ssh", bastion,
        f"--project={project}",
        f"--zone={zone}",
        "--",
        "-N", f"-L{port}:{ip}:443"
    ]

    try:
        proc = subprocess.Popen(cmd)
        time.sleep(2)
        ssh_pid = find_ssh_child_pid(proc.pid)
        pid_map = load_yaml_file(PID_MAP_FILE)
        pid_map[cluster] = ssh_pid or proc.pid
        save_yaml_file(PID_MAP_FILE, pid_map)
        console.print(f"[green]✅ Tunnel started: localhost:{port} → {ip}:443 (PID {pid_map[cluster]})[/green]")
    except Exception as e:
        console.print(f"[red]❌ Failed to start tunnel: {e}[/red]")

def stop_cluster_tunnel(cluster):
    pid_map = load_yaml_file(PID_MAP_FILE)

    if cluster not in pid_map:
        console.print(f"[yellow]⚠️ No tunnel running for cluster: {cluster}[/yellow]")
        return

    pid = pid_map[cluster]
    try:
        p = psutil.Process(pid)
        p.terminate()
        p.wait(timeout=5)
        console.print(f"[green]🛑 Tunnel to '{cluster}' (PID {pid}) stopped.[/green]")
        del pid_map[cluster]
        save_yaml_file(PID_MAP_FILE, pid_map)
    except psutil.NoSuchProcess:
        console.print(f"[red]❌ No such process with PID {pid}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Failed to stop tunnel: {e}[/red]")

def stop_all_tunnels():
    pid_map = load_yaml_file(PID_MAP_FILE)
    if not pid_map:
        console.print("[yellow]⚠️ No tunnels currently running.[/yellow]")
        return

    for cluster, pid in pid_map.items():
        try:
            p = psutil.Process(pid)
            p.terminate()
            p.wait(timeout=5)
            console.print(f"[green]🛑 Stopped tunnel: {cluster} (PID {pid})[/green]")
        except psutil.NoSuchProcess:
            console.print(f"[red]❌ No process found for: {cluster} (PID {pid})[/red]")
        except Exception as e:
            console.print(f"[red]❌ Error stopping {cluster}: {e}[/red]")

    save_yaml_file(PID_MAP_FILE, {})

def is_port_open(port):
    result = subprocess.run(["nc", "-z", "localhost", str(port)],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    return result.returncode == 0

def show_status():
    config = load_yaml_file(CONFIG_FILE)
    table = Table(title="GKE Tunnel Status")
    table.add_column("Cluster")
    table.add_column("Port", justify="right")
    table.add_column("Status")

    for name, info in config.get("clusters", {}).items():
        port = info["port"]
        ip = info["ip"]
        if is_port_open(port):
            status = "[green]🟢 Open"
        else:
            status = f"[red]🔴 Closed (can't reach {ip}:443)"
        table.add_row(name, str(port), status)

    console.print(table)

def main_logic(cluster):
    start_cluster_tunnel(cluster)

def discover_logic():
    discover_clusters()

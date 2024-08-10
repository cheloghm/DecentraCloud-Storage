import click
import requests
import json
import os
import sys
import subprocess
import geocoder  # Import geocoder for region detection
from dotenv import load_dotenv

# Add the parent directory to the system path to find the utils module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.utils import check_storage, create_and_secure_storage  # Import the storage check and allocation functions

# Load environment variables from .env file
load_dotenv()

BASE_URL = os.getenv('BASE_URL')  # Use BASE_URL from the environment variable

@click.group()
def cli():
    pass

@cli.command()
@click.option('--email', prompt='Your email', help='The email to register the node.')
@click.option('--password', prompt='Your password', hide_input=True, confirmation_prompt=True, help='The password to register the node.')
@click.option('--storage', prompt='Storage space (in GB)', help='The amount of storage space to allocate.', default=5)
@click.option('--nodename', prompt='Node name', help='The name of the node.')
def register(email, password, storage, nodename):
    """Register the storage node with the central server."""
    if BASE_URL is None:
        click.echo("BASE_URL environment variable is not set.")
        return

    try:
        # Get country and city information
        g = geocoder.ip('me')
        country = g.country
        city = g.city

        if not country or not city:
            click.echo("Failed to retrieve location information. Ensure you're connected to the internet.")
            return

        # Register the node with the central server first
        node_data = {
            'email': email,
            'password': password,
            'storage': int(storage),
            'nodeName': nodename,
            'country': country,
            'city': city
        }
        headers = {
            'Content-Type': 'application/json'
        }

        register_response = requests.post(f"{BASE_URL}/Nodes/register", json=node_data, headers=headers, verify=False)

        if register_response.status_code == 200:
            click.echo("Node registered successfully!")
            node_config = register_response.json()
            with open('node_config.json', 'w') as f:
                json.dump(node_config, f)
        else:
            click.echo(f"Failed to register node. Status code: {register_response.status_code}. Response: {register_response.text}")
            return

        # Proceed with storage check and Kubernetes setup only if registration is successful
        # Check for at least 10GB of available storage
        free_storage = check_storage(10)
        click.echo(f"Free storage space: {free_storage}GB")

        if int(storage) < 5:
            click.echo("Storage allocation must be at least 5GB.")
            return
        
        # Create and secure the specified storage space
        create_and_secure_storage(int(storage))
        click.echo(f"Allocated and secured {storage}GB of storage.")
        
        # Run the Kubernetes and container runtime installation script
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../scripts/install_k8s_components.sh')
        subprocess.run(['bash', script_path], check=True)
        click.echo("Kubernetes components and container runtime installed.")
        
    except Exception as e:
        click.echo(str(e))
        return

@cli.command()
@click.argument('action', type=click.Choice(['start', 'stop', 'scale', 'rbac', 'netpol'], case_sensitive=False))
def manage(action):
    """Manage Kubernetes cluster operations."""
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../scripts/manage_k8s_cluster.sh')
    try:
        subprocess.run(['bash', script_path, action], check=True)
        click.echo(f"Kubernetes cluster action '{action}' executed successfully.")
    except subprocess.CalledProcessError as e:
        click.echo(f"Failed to execute action '{action}': {e}")

@cli.command()
@click.option('--nodename', prompt='Node name', help='The name of the node.')
@click.option('--email', prompt='Your email', help='The email associated with the node.')
@click.option('--password', prompt='Your password', hide_input=True, help='The password to authenticate the node.')
def login(nodename, email, password):
    """Authenticate the storage node with the central server."""
    if BASE_URL is None:
        click.echo("BASE_URL environment variable is not set.")
        return

    # Function to find the port where the node is running
    def find_node_port():
        import psutil  # Import psutil within the function to avoid import errors if not used
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == psutil.CONN_LISTEN and conn.laddr.port != 80:
                p = psutil.Process(conn.pid)
                if "node" in p.name().lower() and conn.laddr.ip == '0.0.0.0':
                    return conn.laddr.port
        return None

    port = find_node_port()
    if port is None:
        click.echo("Could not find the running port for the node.")
        return

    endpoint = f"https://localhost:{port}"
    click.echo(f"Node endpoint: {endpoint}")

    # Authenticate node
    login_data = {
        'nodeName': nodename,
        'email': email,
        'password': password,
        'endpoint': endpoint
    }
    headers = {
        'Content-Type': 'application/json'
    }
    click.echo(f"Sending login data: {json.dumps(login_data)}")  # Debugging line
    try:
        login_response = requests.post(f"{BASE_URL}/Nodes/login", json=login_data, headers=headers, verify=False)

        if login_response.status_code == 200:
            click.echo("Node authenticated successfully!")
            node_config = login_response.json()
            with open('node_config.json', 'w') as f:
                json.dump(node_config, f)
        else:
            click.echo(f"Failed to authenticate node. Status code: {login_response.status_code}. Response: {login_response.text}")
    except Exception as e:
        click.echo(f"An error occurred during authentication: {str(e)}")

if __name__ == '__main__':
    cli()

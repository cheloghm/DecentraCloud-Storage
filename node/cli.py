import click
import requests
import json
import os
import sys
import subprocess
import geocoder
from dotenv import load_dotenv

# Add the parent directory to the system path to find the utils module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.utils import check_storage, create_and_secure_storage  # Import the storage check and allocation functions

# Load environment variables from .env file
load_dotenv()

BASE_URL = os.getenv('BASE_URL')  # Use BASE_URL from the environment variable

NODE_CONFIG_PATH = 'node_config.json'  # Path to store node configuration

def check_k8s_components():
    """Check if Kubernetes components are installed."""
    try:
        subprocess.run(['kubeadm', 'version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(['kubelet', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(['kubectl', 'version', '--client'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        click.echo("Kubernetes components are already installed.")
    except FileNotFoundError:
        return False
    except subprocess.CalledProcessError:
        return False
    return True

@click.group()
def cli():
    pass

def verify_node_with_server(email, nodename):
    """Verify if the node name is available with the central server."""
    node_verification_data = {
        'email': email,
        'nodeName': nodename
    }

    try:
        verification_response = requests.post(f"{BASE_URL}/Nodes/verify", json=node_verification_data, verify=False)
        if verification_response.status_code == 400:
            click.echo(f"Node already exists. Please authenticate or choose a different name.")
            return False
        elif verification_response.status_code != 200:
            click.echo(f"Failed to verify node. Status code: {verification_response.status_code}. Response: {verification_response.text}")
            return False
        return True
    except Exception as e:
        click.echo(f"An error occurred during node verification: {str(e)}")
        return False

def load_node_config():
    """Load the node configuration if it exists and is valid."""
    if os.path.exists(NODE_CONFIG_PATH):
        try:
            with open(NODE_CONFIG_PATH, 'r') as f:
                node_config = json.load(f)
                return node_config if node_config else None
        except json.JSONDecodeError:
            click.echo("Node configuration file is empty or corrupted.")
            return None
    return None

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

    node_config = load_node_config()

    if node_config:
        click.echo("Node already exists locally. Please authenticate or register a new node.")
        click.echo(f"If you forgot your password, visit www.decentracloud.com/forgot-password to change it.")
        click.echo(f"Then authenticate the node using: python3 node/cli.py login --nodename {nodename} --email {email} --password [new password] --url [public url]")
        return

    # Verify with the central server if the node name is available
    if not verify_node_with_server(email, nodename):
        # Prompt the user for a new node name
        new_nodename = click.prompt("Node name already exists. Please enter a different node name", type=str)
        if not verify_node_with_server(email, new_nodename):
            click.echo("Node name verification failed. Aborting registration.")
            return
        nodename = new_nodename

    try:
        # Get country and city information
        g = geocoder.ip('me')
        country = g.country
        city = g.city

        if not country or not city:
            click.echo("Failed to retrieve location information. Ensure you're connected to the internet.")
            return

        # Register the node with the central server
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
            with open(NODE_CONFIG_PATH, 'w') as f:
                json.dump(node_config, f)
        else:
            click.echo(f"Failed to register node. Status code: {register_response.status_code}. Response: {register_response.text}")
            return

        # Proceed with storage check and Kubernetes setup only if registration is successful
        free_storage = check_storage(10)
        click.echo(f"Free storage space: {free_storage}GB")

        if int(storage) < 5:
            click.echo("Storage allocation must be at least 5GB.")
            return
        
        # Create and secure the specified storage space
        create_and_secure_storage(int(storage))
        click.echo(f"Allocated and secured {storage}GB of storage.")
        
        # Install Kubernetes components if not already installed
        if not check_k8s_components():
            click.echo("Installing Kubernetes components...")
            install_k8s_components()
        else:
            click.echo("Kubernetes components are already installed.")
        
    except Exception as e:
        click.echo(str(e))
        return

def install_k8s_components():
    """Install Kubernetes components."""
    try:
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../Scripts/install_kubernetes.sh')
        subprocess.run(['bash', script_path], check=True)
        click.echo("Kubernetes components and container runtime installed.")
    except subprocess.CalledProcessError as e:
        click.echo(f"Failed to install Kubernetes components: {e}")

@cli.command()
@click.argument('action', type=click.Choice(['start', 'stop', 'scale', 'rbac', 'netpol'], case_sensitive=False))
def manage(action):
    """Manage Kubernetes cluster operations."""
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../Scripts/manage_cluster.sh')
    try:
        subprocess.run(['bash', script_path, action], check=True)
        click.echo(f"Kubernetes cluster action '{action}' executed successfully.")
    except subprocess.CalledProcessError as e:
        click.echo(f"Failed to execute action '{action}': {e}")

@cli.command()
@click.option('--nodename', prompt='Node name', help='The name of the node.')
@click.option('--email', prompt='Your email', help='The email associated with the node.')
@click.option('--password', prompt='Your password', hide_input=True, help='The password to authenticate the node.')
@click.option('--url', prompt='Node URL', help='The public URL for the Storage Node.')
def login(nodename, email, password, url):
    """Authenticate the storage node with the central server."""
    if BASE_URL is None:
        click.echo("BASE_URL environment variable is not set.")
        return

    # Use the provided public URL
    endpoint = url
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
            with open(NODE_CONFIG_PATH, 'w') as f:
                json.dump(node_config, f)
        else:
            click.echo(f"Failed to authenticate node. Status code: {login_response.status_code}. Response: {login_response.text}")
    except Exception as e:
        click.echo(f"An error occurred during authentication: {str(e)}")

if __name__ == '__main__':
    cli()

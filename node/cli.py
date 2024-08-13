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

from utils.utils import check_storage, create_and_secure_storage

# Load environment variables from .env file
load_dotenv()

BASE_URL = os.getenv('BASE_URL')  # Use BASE_URL from the environment variable

NODE_CONFIG_PATH = 'node_config.json'  # Path to store node configuration

@click.group()
def cli():
    pass

def check_k8s_components():
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

    if os.path.exists(NODE_CONFIG_PATH):
        click.echo("Node already exists locally. Verifying with central server...")
        with open(NODE_CONFIG_PATH, 'r') as f:
            node_config = json.load(f)

        try:
            # Check if the node exists on the central server
            response = requests.post(f"{BASE_URL}/Nodes/verify", json=node_config, headers={'Content-Type': 'application/json'}, verify=False)

            if response.status_code == 200:
                click.echo("Node verified on central server. No need to re-register.")
                return

            elif response.status_code == 404:
                click.echo("Node not found on central server. Re-registering...")
                register_node(email, password, storage, nodename)
                return

            else:
                click.echo(f"Unexpected response from server: {response.status_code}. Response: {response.text}")
                return

        except Exception as e:
            click.echo(f"Failed to verify node with central server: {str(e)}")
            return

    else:
        # If node_config.json doesn't exist, register the node
        register_node(email, password, storage, nodename)

def register_node(email, password, storage, nodename):
    """Function to register the node with the central server."""
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
            with open(NODE_CONFIG_PATH, 'w') as f:
                json.dump(node_config, f)
        elif register_response.status_code == 409:
            click.echo("Node already exists on the central server. Please visit www.decentracloud.com/forgot-password to change your password and then authenticate the node using the login command.")
        else:
            click.echo(f"Failed to register node. Status code: {register_response.status_code}. Response: {register_response.text}")
            return

        # Proceed with storage check and Kubernetes setup only if registration is successful
        free_storage = check_storage(10)
        click.echo(f"Free storage space: {free_storage}GB")

        if int(storage) < 5:
            click.echo("Storage allocation must be at least 5GB.")
            return
        
        create_and_secure_storage(int(storage))
        click.echo(f"Allocated and secured {storage}GB of storage.")
        
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

    endpoint = url
    click.echo(f"Node endpoint: {endpoint}")

    login_data = {
        'nodeName': nodename,
        'email': email,
        'password': password,
        'endpoint': endpoint
    }
    headers = {
        'Content-Type': 'application/json'
    }
    click.echo(f"Sending login data: {json.dumps(login_data)}")
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

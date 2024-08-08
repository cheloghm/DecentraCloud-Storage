import os
import platform
import shutil
import subprocess

def check_storage(min_required_gb):
    total, used, free = shutil.disk_usage("/")
    free_gb = free // (2**30)
    if free_gb < min_required_gb:
        raise Exception(f"Not enough free storage space. At least {min_required_gb}GB required, but only {free_gb}GB available.")
    return free_gb

def create_and_secure_storage(storage_gb, node_dir='node_storage'):
    if not os.path.exists(node_dir):
        os.makedirs(node_dir, exist_ok=True)

    # Check if enough storage is available
    free_gb = check_storage(storage_gb)
    if free_gb < storage_gb:
        raise Exception(f"Not enough free storage space to allocate {storage_gb}GB.")

    secure_storage(node_dir)

def secure_storage(directory):
    if platform.system() == 'Windows':
        # Remove inherited permissions
        subprocess.check_call(['icacls', directory, '/inheritance:r'])
        # Grant full control to the current user
        subprocess.check_call(['icacls', directory, '/grant:r', f'{os.getenv("USERNAME")}:(OI)(CI)F'])
        # Deny read access to everyone else
        subprocess.check_call(['icacls', directory, '/deny', 'Everyone:(OI)(CI)R'])
    else:
        # Full access to the owner only
        subprocess.check_call(['chmod', '700', directory])

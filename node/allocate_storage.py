import os
import subprocess

def create_storage_partition(storage_gb, storage_path="/mnt/storage_node"):
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)
    command = f"dd if=/dev/zero of={storage_path}/storage_node.img bs=1G count={storage_gb}"
    subprocess.run(command, shell=True, check=True)
    command = f"mkfs.ext4 {storage_path}/storage_node.img"
    subprocess.run(command, shell=True, check=True)
    command = f"mount -o loop {storage_path}/storage_node.img {storage_path}"
    subprocess.run(command, shell=True, check=True)
    command = f"chmod 700 {storage_path}"
    subprocess.run(command, shell=True, check=True)
    print(f"Storage allocated and secured at {storage_path}")

if __name__ == "__main__":
    storage_gb = 40  # 200GB for production
    create_storage_partition(storage_gb)

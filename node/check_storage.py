import os
import shutil

def check_storage(min_storage_gb):
    total, used, free = shutil.disk_usage("/")
    free_gb = free // (2**30)
    if free_gb < min_storage_gb:
        print(f"Error: Not enough storage. Available: {free_gb}GB, Required: {min_storage_gb}GB")
        return False
    return True

def prompt_storage_allocation(min_allocation_gb, software_allocation_gb):
    allocated_storage = int(input(f"Enter storage allocation for node (minimum {min_allocation_gb}GB): "))
    if allocated_storage < min_allocation_gb:
        print(f"Error: Allocation must be at least {min_allocation_gb}GB")
        return False
    total_allocation = allocated_storage + software_allocation_gb
    if not check_storage(total_allocation):
        print(f"Error: Not enough storage for allocation. Required: {total_allocation}GB")
        return False
    return allocated_storage

if __name__ == "__main__":
    min_allocation_gb = 40  # 200GB for production
    software_allocation_gb = 10  # For software
    if prompt_storage_allocation(min_allocation_gb, software_allocation_gb):
        print("Storage check and allocation successful")
    else:
        print("Storage check and allocation failed")

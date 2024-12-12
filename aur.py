import requests
import os
import subprocess

AUR_BASE_URL = "https://aur.archlinux.org/rpc/?v=5"

def search_aur(package_name):
    response = requests.get(f"{AUR_BASE_URL}&type=search&arg={package_name}")
    if response.status_code == 200:
        results = response.json().get('results', [])
        packages = [
            {"name": pkg["Name"], "desc": pkg["Description"], "source": "aur"}
            for pkg in results
        ]
        return packages
    else:
        print("Error: Failed to fetch data from AUR.")
        return []

def install_aur(package_name):
    aur_url = f"https://aur.archlinux.org/{package_name}.git"
    clone_dir = f"/tmp/{package_name}"
    try:
        print(f"Cloning {package_name} from AUR...")
        subprocess.run(["git", "clone", aur_url, clone_dir], check=True)
        os.chdir(clone_dir)
        print("Building package...")
        subprocess.run(["makepkg", "-si"], check=True)
    except subprocess.CalledProcessError:
        print(f"Error: Failed to install {package_name} from AUR.")
    finally:
        if os.path.exists(clone_dir):
            subprocess.run(["rm", "-rf", clone_dir])

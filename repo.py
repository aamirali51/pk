import subprocess

def search_repo(package_name):
    try:
        result = subprocess.run(["pacman", "-Ss", package_name], capture_output=True, text=True, check=True)
        packages = []
        for line in result.stdout.splitlines():
            if line.startswith(" "):
                continue  # Skip detailed package info
            parts = line.split()
            packages.append({
                "name": parts[0].split("/")[1],  # Extract package name
                "desc": " ".join(parts[1:]),  # Description
                "source": "repo"
            })
        return packages
    except subprocess.CalledProcessError:
        print(f"No package found for {package_name} in official repositories.")
        return []

def install_repo(package_name):
    try:
        subprocess.run(["sudo", "pacman", "-S", package_name], check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"Failed to install {package_name}.")
        return False

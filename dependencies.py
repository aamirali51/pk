import subprocess
import logging

# Configure logging for debugging and diagnostics
logging.basicConfig(
    filename="pk.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def install_package(pkg):
    """Install a package using pacman."""
    try:
        print(f"Installing {pkg['name']}...")
        logging.info(f"Installing package: {pkg['name']}")
        subprocess.run(["sudo", "pacman", "-S", pkg['name'], "--noconfirm"], check=True)
        print(f"{pkg['name']} installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {pkg['name']}: {e}")
        logging.error(f"Failed to install {pkg['name']}: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        logging.error(f"Unexpected error during installation: {e}")

def handle_dependency_conflict(pkg1, pkg2):
    """Handle dependency conflicts intelligently."""
    print(f"Conflict detected between {pkg1['name']} and {pkg2['name']}.")
    print(f"{pkg1['name']}: {pkg1.get('version', 'unknown')} from {pkg1.get('source', 'repo')}")
    print(f"{pkg2['name']}: {pkg2.get('version', 'unknown')} from {pkg2.get('source', 'repo')}")

    choice = input("Do you want to remove the existing package and install the new one? (Y/n): ")
    if choice.lower() == 'y':
        try:
            print(f"Removing {pkg1['name']}...")
            subprocess.run(["sudo", "pacman", "-R", pkg1['name'], "--noconfirm"], check=True)
            install_package(pkg2)
        except subprocess.CalledProcessError as e:
            print(f"Failed to remove {pkg1['name']}: {e}")
            logging.error(f"Failed to remove {pkg1['name']}: {e}")
    else:
        print("Installation aborted.")
        logging.info("Installation aborted by user.")

def suggest_additional_packages(pkg_name):
    """Suggest additional packages based on dynamic metadata."""
    try:
        print(f"Fetching suggestions for {pkg_name}...")
        logging.info(f"Fetching suggestions for {pkg_name}")
        # Simulated suggestions (can integrate with AUR or metadata sources)
        recommended = {
            "vim": ["vim-plugin", "vim-airline"],
            "python": ["python-pip", "python-virtualenv"]
        }
        if pkg_name in recommended:
            print(f"Suggested additional packages for {pkg_name}:")
            for idx, rec_pkg in enumerate(recommended[pkg_name], 1):
                print(f"{idx}. {rec_pkg}")

            choice = input("Select packages to install (e.g., 1 2 or leave blank to skip): ").strip()
            if choice:
                selected = [recommended[pkg_name][int(idx) - 1] for idx in choice.split()]
                for rec_pkg in selected:
                    install_package({"name": rec_pkg})
        else:
            print(f"No additional packages suggested for {pkg_name}.")
            logging.info(f"No additional packages suggested for {pkg_name}.")
    except Exception as e:
        print(f"Error suggesting packages: {e}")
        logging.error(f"Error suggesting packages for {pkg_name}: {e}")

def show_dependency_tree(pkg_name):
    """Show the actual dependency tree for a package."""
    try:
        print(f"Fetching dependency tree for {pkg_name}...")
        subprocess.run(["pactree", pkg_name], check=True)
    except FileNotFoundError:
        print("Error: 'pactree' is not installed. Install it with 'sudo pacman -S pactree'.")
        logging.error("'pactree' is not installed.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to fetch dependency tree for {pkg_name}: {e}")
        logging.error(f"Failed to fetch dependency tree for {pkg_name}: {e}")

def check_cyclic_dependencies(pkg):
    """Check for cyclic dependencies using a combination of manual checks and tools."""
    print(f"Checking for cyclic dependencies in {pkg['name']}...")
    logging.info(f"Checking for cyclic dependencies in {pkg['name']}")

    # Manual detection logic
    visited = set()
    stack = set()

    def detect_cycle(package):
        visited.add(package['name'])
        stack.add(package['name'])
        for dep in package.get("dependencies", []):
            if dep['name'] not in visited:
                if detect_cycle(dep):
                    return True
            elif dep['name'] in stack:
                return True
        stack.remove(package['name'])
        return False

    if detect_cycle(pkg):
        print(f"Cyclic dependency detected for package {pkg['name']}.")
        logging.warning(f"Cyclic dependency detected for package {pkg['name']}.")
        choice = input("Do you want to skip installation of this package? (Y/n): ")
        if choice.lower() == 'y':
            print(f"Skipping {pkg['name']}.")
            logging.info(f"Skipped installation of {pkg['name']}.")
        else:
            print(f"Package {pkg['name']} installed with potential cyclic dependency.")
            logging.warning(f"Installed {pkg['name']} despite cyclic dependency.")

    # Check using pactree
    try:
        subprocess.run(["pactree", "-c", pkg['name']], check=True)
    except FileNotFoundError:
        print("Error: 'pactree' is not installed. Install it with 'sudo pacman -S pactree'.")
        logging.error("'pactree' is not installed.")
    except subprocess.CalledProcessError:
        print(f"Failed to verify cyclic dependencies for {pkg['name']}.")
        logging.error(f"Failed to verify cyclic dependencies for {pkg['name']}.")
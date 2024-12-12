#!/usr/bin/env python3

import sys
import os
import argparse
from colorama import Fore, Style
import subprocess
import importlib.util
import threading
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# Add /usr/share/pk to sys.path to locate aur.py and repo.py
sys.path.append("/usr/share/pk")

# Dynamically load dependencies.py from /usr/share/pk
module_path = "/usr/share/pk/dependencies.py"
spec = importlib.util.spec_from_file_location("dependencies", module_path)
dependencies = importlib.util.module_from_spec(spec)
sys.modules["dependencies"] = dependencies
spec.loader.exec_module(dependencies)

# Now you can use the imported functions
handle_dependency_conflict = dependencies.handle_dependency_conflict
suggest_additional_packages = dependencies.suggest_additional_packages
show_dependency_tree = dependencies.show_dependency_tree
check_cyclic_dependencies = dependencies.check_cyclic_dependencies

# Import search and install functions from aur.py and repo.py
from aur import search_aur, install_aur
from repo import search_repo, install_repo

# Pacman lock for thread safety
pacman_lock = threading.Lock()

def safely_remove_lock():
    """Remove the pacman lock file if no pacman process is running."""
    if os.path.exists("/var/lib/pacman/db.lck"):
        try:
            print(Fore.YELLOW + "Checking for active pacman process..." + Style.RESET_ALL)
            result = subprocess.run(["pgrep", "pacman"], capture_output=True, text=True)
            if not result.stdout.strip():  # No pacman process running
                os.remove("/var/lib/pacman/db.lck")
                print(Fore.GREEN + "Pacman lock file removed safely." + Style.RESET_ALL)
            else:
                print(Fore.RED + "Another pacman process is running. Aborting." + Style.RESET_ALL)
                return False
        except Exception as e:
            print(Fore.RED + f"Failed to handle pacman lock: {e}" + Style.RESET_ALL)
            return False
    return True

def handle_remove(names):
    """Handle the removal of multiple packages."""
    print(Fore.GREEN + f"\nRemoving packages: {', '.join(names)}..." + Style.RESET_ALL)
    with pacman_lock:
        if not safely_remove_lock():
            return
        for name in names:
            try:
                print(Fore.YELLOW + f"Removing {name}..." + Style.RESET_ALL)
                subprocess.run(["sudo", "pacman", "-R", name, "--noconfirm"], check=True)
                print(Fore.GREEN + f"Successfully removed {name}" + Style.RESET_ALL)
            except subprocess.CalledProcessError as e:
                print(Fore.RED + f"Failed to remove {name}: {e}" + Style.RESET_ALL)

def print_header():
    """Print a styled header for the application."""
    print(Fore.CYAN + Style.BRIGHT + "PK - A Lightweight Package Manager" + Style.RESET_ALL)
    print(Fore.CYAN + "=" * 40 + Style.RESET_ALL)

def print_package(pkg, index):
    """Print a formatted package listing."""
    print(Fore.YELLOW + f"{index + 1}. {pkg['name']} - {pkg['desc']} ({pkg['source']})" + Style.RESET_ALL)

def handle_search(name):
    """Handle searching for packages."""
    print(Fore.GREEN + f"\nSearching for '{name}' in official repositories..." + Style.RESET_ALL)
    repo_results = search_repo(name)
    print(Fore.GREEN + f"\nSearching for '{name}' in AUR..." + Style.RESET_ALL)
    aur_results = search_aur(name)
    combined_results = repo_results + aur_results
    if combined_results:
        print(Fore.GREEN + "\nSearch results:" + Style.RESET_ALL)
        for i, pkg in enumerate(combined_results):
            print_package(pkg, i)
        try:
            print(Fore.GREEN + "\nEnter the package number(s) to install (e.g., 1 2 3 or 1,2,3):" + Style.RESET_ALL)
            choice = input("Your choice: ").strip()
            if not choice:
                print(Fore.RED + "No selection made. Aborting." + Style.RESET_ALL)
                return
            selected_indices = [int(x.strip()) - 1 for x in choice.replace(",", " ").split()]
            selected_packages = [combined_results[i] for i in selected_indices if 0 <= i < len(combined_results)]
            if not selected_packages:
                print(Fore.RED + "No valid selections. Aborting." + Style.RESET_ALL)
                return
            print(Fore.BLUE + "Installing selected packages..." + Style.RESET_ALL)
            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(install_package, pkg) for pkg in selected_packages]
                for future in futures:
                    future.result()
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter valid package numbers." + Style.RESET_ALL)
        except IndexError:
            print(Fore.RED + "One or more selected numbers are out of range." + Style.RESET_ALL)
        except KeyboardInterrupt:
            print(Fore.RED + "\nCanceled by user." + Style.RESET_ALL)
            sys.exit(1)  # Optional: Exit after canceling
    else:
        print(Fore.RED + "No packages found." + Style.RESET_ALL)

def install_package(pkg):
    """Install a package from either repo or AUR."""
    if pkg["source"] == "repo":
        install_repo(pkg["name"])
    else:
        install_aur(pkg["name"])

def handle_install(names):
    """Handle the installation of multiple packages."""
    print(Fore.GREEN + f"\nInstalling packages: {', '.join(names)}..." + Style.RESET_ALL)
    with pacman_lock:
        if not safely_remove_lock():
            return
        total_packages = len(names)
        # Download packages first using tqdm for better UI
        with tqdm(total=total_packages, desc="Downloading packages", dynamic_ncols=True, colour="green") as download_bar:
            for name in names:
                # Simulate download process, as pacman doesn't expose download progress directly
                download_bar.set_postfix_str(f"Downloading {name}")
                download_bar.update(1)

        # Then install them one by one with a progress bar
        with tqdm(total=total_packages, desc="Installing packages", dynamic_ncols=True, colour="blue") as install_bar:
            for idx, name in enumerate(names):
                install_package({"name": name, "source": "repo"})
                install_bar.set_postfix_str(f"Installing {name}")
                install_bar.update(1)
                tqdm.write(Fore.GREEN + f"Successfully installed {name}" + Style.RESET_ALL)

def handle_update():
    """Handle the update of packages."""
    print(Fore.GREEN + "Updating packages..." + Style.RESET_ALL)
    try:
        subprocess.run(["sudo", "pacman", "-Syu"], check=True)
        print(Fore.GREEN + "Update completed." + Style.RESET_ALL)
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"An error occurred during the update: {e}" + Style.RESET_ALL)

def main():
    """Main function."""
    if len(sys.argv) == 1:
        print(Fore.CYAN + "Usage: pk <command> [options]" + Style.RESET_ALL)
        print(Fore.CYAN + "Available commands:" + Style.RESET_ALL)
        print(Fore.CYAN + "  i <package(s)>   Install one or more packages" + Style.RESET_ALL)
        print(Fore.CYAN + "  s <package_name>  Search for packages" + Style.RESET_ALL)
        print(Fore.CYAN + "  u                 Update installed packages" + Style.RESET_ALL)
        print(Fore.CYAN + "  r <package(s)>   Remove one or more packages" + Style.RESET_ALL)
        print(Fore.CYAN + "  -h                Show this help message" + Style.RESET_ALL)
        sys.exit(0)

    command = sys.argv[1]

    if command == "s":
        handle_search(" ".join(sys.argv[2:]))
    elif command == "i":
        handle_install(sys.argv[2:])
    elif command == "u":
        handle_update()
    elif command == "r":
        handle_remove(sys.argv[2:])
    elif command == "-h" or command == "--help":
        main()
    else:
        print(Fore.RED + "Invalid command. Use pk -h for help." + Style.RESET_ALL)

if __name__ == "__main__":
    main()

#!/usr/bin/env python

import argparse
import subprocess

# Functions for search, install, update, and remove packages

# Search
def search_packages(query):
    try:
        subprocess.run(['dnf', 'search', query], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while searching for packages: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# Install
def install_package(package_name):
    # Execute dnf install command with the package name and the --assumeyes flag for non-interactive installation
    install_command = ['sudo', 'dnf', 'install', '-y', package_name]
    subprocess.run(install_command)

    # Check if the installation was successful
    if subprocess.run(['sudo', 'dnf', 'list', package_name], capture_output=True).returncode == 0:
        print(f"Package '{package_name}' installed successfully.")

        # Resolve package dependencies
        resolve_command = ['sudo', 'dnf', 'repoquery', '--requires', package_name]
        output = subprocess.check_output(resolve_command).decode('utf-8')

        # Split the output into a list of dependency package names
        dependency_packages = output.strip().split('\n')

        # Install the required dependency packages
        if dependency_packages:
            print("Installing package dependencies...")
            install_command = ['sudo', 'dnf', 'install', '-y'] + dependency_packages
            subprocess.run(install_command)
            print("Package dependencies installed successfully.")
    else:
        print(f"Failed to install package '{package_name}'.")



# Update
def update_packages():
    try:
        subprocess.run(['sudo', 'dnf', 'upgrade', '-y'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while updating packages: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# Remove
def remove_package(package_name):
    try:
        subprocess.run(['sudo', 'dnf', 'remove', '-y', package_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while removing the package: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# Repository Management
def add_repository(repo_name, repo_url):
    subprocess.run(['sudo', 'dnf', 'config-manager', '--add-repo', repo_url])
    print(f"Repository '{repo_name}' added successfully.")

def remove_repository(repo_name):
    subprocess.run(['sudo', 'dnf', 'config-manager', '--disable', repo_name])
    print(f"Repository '{repo_name}' removed successfully.")

def update_repositories():
    subprocess.run(['sudo', 'dnf', 'makecache'])
    print("Repositories updated successfully.")


# Interactive mode
def interactive_mode():
    print("Interactive Mode")
    print("Enter 'help' for available commands. Enter 'exit' to quit.")

    while True:
        user_input = input(">>> ").strip().lower()

        if user_input == 'help':
            print("Available commands:")
            print(" - search <query>")
            print(" - install <package_name>")
            print(" - update")
            print(" - remove <package_name>")
            print(" - addrepo <repo_name> <repo_url>")
            print(" - removerepo <repo_name>")
            print(" - updaterepos")
            print(" - exit")
        elif user_input.startswith('search'):
            query = user_input.split(' ', 1)[1]
            search_packages(query)
        elif user_input.startswith('install'):
            package_name = user_input.split(' ', 1)[1]
            install_package(package_name)
        elif user_input == 'update':
            update_packages()
        elif user_input.startswith('remove'):
            package_name = user_input.split(' ', 1)[1]
            remove_package(package_name)
        elif user_input.startswith('addrepo'):
            inputs = user_input.split(' ', 2)
            if len(inputs) == 3:
                repo_name = inputs[1]
                repo_url = inputs[2]
                add_repository(repo_name, repo_url)
            else:
                print("Invalid command. Usage: addrepo <repo_name> <repo_url>")
        elif user_input.startswith('removerepo'):
            repo_name = user_input.split(' ', 1)[1]
            remove_repository(repo_name)
        elif user_input == 'updaterepos':
            update_repositories()
        elif user_input == 'exit':
            break
        else:
            print("Invalid command. Enter 'help' for available commands.")

    print("Exiting Interactive Mode")



parser = argparse.ArgumentParser(description='Fedora Package Management v1')
parser.add_argument('operation', choices=['search', 'install', 'update', 'remove'], nargs='?', help='Package operation')
parser.add_argument('--package', help='Package name')
parser.add_argument('--query', help='Search query')
parser.add_argument('--repo-name', help='Repository name')
parser.add_argument('--repo-url', help='Repository URL')

args = parser.parse_args()

if args.operation == 'search':
    search_packages(args.query)
elif args.operation == 'install':
    install_package(args.package)
elif args.operation == 'update':
    update_packages()
elif args.operation == 'remove':
    remove_package(args.package)
elif args.operation == 'add-repo':
    add_repository(args.repo_name, args.repo_url)
elif args.operation == 'remove-repo':
    remove_repository(args.repo_name)
elif args.operation == 'update-repos':
    update_repositories()
else:
    interactive_mode()

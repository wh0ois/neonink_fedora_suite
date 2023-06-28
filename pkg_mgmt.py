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
    try:
        subprocess.run(['sudo', 'dnf', 'install', '-y', package_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing the package: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


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


parser = argparse.ArgumentParser(description='Fedora Package Management v1')
parser.add_argument('operation', choices=['search', 'install', 'update', 'remove'], help='Package operation')
parser.add_argument('--package', help='Package name')
parser.add_argument('--query', help='Search query')

args = parser.parse_args()

if args.operation == 'search':
    search_packages(args.query)
elif args.operation == 'install':
    install_package(args.package)
elif args.operation == 'update':
    update_packages()
elif args.operation == 'remove':
    remove_package(args.package)

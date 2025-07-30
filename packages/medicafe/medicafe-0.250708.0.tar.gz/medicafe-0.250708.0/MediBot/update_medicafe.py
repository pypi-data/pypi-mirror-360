#update_medicafe.py
import subprocess, sys, requests, time, pkg_resources, platform

def get_installed_version(package):
    try:
        process = subprocess.Popen(
            [sys.executable, '-m', 'pip', 'show', package],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            for line in stdout.decode().splitlines():
                if line.startswith("Version:"):
                    return line.split(":", 1)[1].strip()
        return None
    except Exception as e:
        print("Error retrieving installed version: {}".format(e))
        return None

def get_latest_version(package, retries=3, delay=1):
    """
    Fetch the latest version of the specified package from PyPI with retries.
    """
    for attempt in range(1, retries + 1):
        try:
            response = requests.get("https://pypi.org/pypi/{}/json".format(package), timeout=10)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()
            latest_version = data['info']['version']
            
            # Print the version with attempt information
            if attempt == 1:
                print("Latest available version: {}".format(latest_version))
            else:
                print("Latest available version: {} ({} attempt)".format(latest_version, attempt))
            
            # Check if the latest version is different from the current version
            current_version = get_installed_version(package)
            if current_version and compare_versions(latest_version, current_version) == 0:
                # If the versions are the same, perform a second request
                time.sleep(delay)
                response = requests.get("https://pypi.org/pypi/{}/json".format(package), timeout=10)
                response.raise_for_status()
                data = response.json()
                latest_version = data['info']['version']
            
            return latest_version  # Return the version after the check
        except requests.RequestException as e:
            print("Attempt {}: Error fetching latest version: {}".format(attempt, e))
            if attempt < retries:
                print("Retrying in {} seconds...".format(delay))
                time.sleep(delay)
    return None

def check_internet_connection():
    try:
        requests.get("http://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False

def compare_versions(version1, version2):
    v1_parts = list(map(int, version1.split(".")))
    v2_parts = list(map(int, version2.split(".")))
    return (v1_parts > v2_parts) - (v1_parts < v2_parts)

def upgrade_package(package, retries=3, delay=2):  # Updated retries to 3
    """
    Attempts to upgrade the package multiple times with delays in between.
    """
    if not check_internet_connection():
        print("Error: No internet connection detected. Please check your internet connection and try again.")
        time.sleep(3)  # Pause for 3 seconds before exiting
        sys.exit(1)
    
    for attempt in range(1, retries + 1):
        print("Attempt {} to upgrade {}...".format(attempt, package))
        process = subprocess.Popen(
            [
                sys.executable, '-m', 'pip', 'install', '--upgrade',
                package, '--no-cache-dir', '--disable-pip-version-check', '-q'
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            print(stdout.decode().strip())
            new_version = get_installed_version(package)  # Get new version after upgrade
            if compare_versions(new_version, get_latest_version(package)) >= 0:  # Compare versions
                if attempt == 1:
                    print("Upgrade succeeded!")
                else:
                    print("Attempt {}: Upgrade succeeded!".format(attempt))
                time.sleep(delay)
                return True
            else:
                print("Upgrade failed. Current version remains: {}".format(new_version))
                if attempt < retries:
                    print("Retrying in {} seconds...".format(delay))
                    time.sleep(delay)
        else:
            print(stderr.decode().strip())
            print("Attempt {}: Upgrade failed.".format(attempt))
            if attempt < retries:
                print("Retrying in {} seconds...".format(delay))
                time.sleep(delay)
    
    print("Error: All upgrade attempts failed.")
    return False

def ensure_dependencies():
    """Ensure all dependencies listed in setup.py are installed and up-to-date."""
    # Don't try to read requirements.txt as it won't be available after installation
    # Instead, hardcode the same dependencies that are in setup.py
    required_packages = [
        'requests==2.21.0',
        'argparse==1.4.0',
        'tqdm==4.14.0',
        'python-docx==0.8.11',
        'PyYAML==5.2',
        'chardet==3.0.4',
        'msal==1.26.0'
    ]

    # Define problematic packages for Windows XP with Python 3.4
    problematic_packages = ['numpy==1.11.3', 'pandas==0.20.0', 'lxml==4.2.0']
    is_windows_py34 = sys.version_info[:2] == (3, 4) and platform.system() == 'Windows'

    if is_windows_py34:
        print("Detected Windows with Python 3.4")
        print("Please ensure the following packages are installed manually:")
        for pkg in problematic_packages:
            package_name, version = pkg.split('==')
            try:
                installed_version = pkg_resources.get_distribution(package_name).version
                print("{} {} is already installed".format(package_name, installed_version))
                if installed_version != version:
                    print("Note: Installed version ({}) differs from required ({})".format(installed_version, version))
                    print("If you experience issues, consider installing version {} manually".format(version))
            except pkg_resources.DistributionNotFound:
                print("{} is not installed".format(package_name))
                print("Please install {}=={} manually using a pre-compiled wheel".format(package_name, version))
                print("Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/")
                print("Then run: pip install path\\to\\{}-{}-cp34-cp34m-win32.whl".format(package_name, version))
        print("\nContinuing with other dependencies...")
    else:
        # Add problematic packages to the list for non-Windows XP environments
        required_packages.extend(problematic_packages)

    for pkg in required_packages:
        if '==' in pkg:
            package_name, version = pkg.split('==')  # Extract package name and version
        else:
            package_name = pkg
            version = None  # No specific version required

        # Skip problematic packages on Windows XP Python 3.4
        if is_windows_py34 and any(package_name in p for p in problematic_packages):
            continue

        try:
            installed_version = pkg_resources.get_distribution(package_name).version
            if version and installed_version != version:  # Check if installed version matches required version
                print("Current version of {}: {}".format(package_name, installed_version))
                print("Required version of {}: {}".format(package_name, version))
                time.sleep(2)  # Pause for 2 seconds to allow user to read the output
                if not upgrade_package(package_name):  # Attempt to upgrade/downgrade to the required version
                    print("Warning: Failed to upgrade/downgrade {} to version {}.".format(package_name, version))
                    time.sleep(2)  # Pause for 2 seconds after failure message
            elif version and installed_version == version:  # Check if installed version matches required version
                print("All versions match for {}. No changes needed.".format(package_name))
                time.sleep(1)  # Pause for 2 seconds to allow user to read the output
            elif not version:  # If no specific version is required, check for the latest version
                latest_version = get_latest_version(package_name)
                if latest_version and installed_version != latest_version:
                    print("Current version of {}: {}".format(package_name, installed_version))
                    print("Latest version of {}: {}".format(package_name, latest_version))
                    time.sleep(2)  # Pause for 2 seconds to allow user to read the output
                    if not upgrade_package(package_name):
                        print("Warning: Failed to upgrade {}.".format(package_name))
                        time.sleep(2)  # Pause for 2 seconds after failure message
        except pkg_resources.DistributionNotFound:
            print("Package {} is not installed. Attempting to install...".format(package_name))
            time.sleep(2)  # Pause for 2 seconds before attempting installation
            if not upgrade_package(package_name):
                print("Warning: Failed to install {}.".format(package_name))
                time.sleep(2)  # Pause for 2 seconds after failure message

def main():
    # Ensure internet connection before proceeding
    if not check_internet_connection():
        print("Error: No internet connection. Please check your connection and try again.")
        time.sleep(3)  # Pause for 3 seconds before exiting
        sys.exit(1)

    # Ensure all dependencies are met before proceeding
    response = input("Do you want to check dependencies? (yes/no, default/enter is no): ").strip().lower()
    if response in ['yes', 'y']:
        ensure_dependencies()
    else:
        print("Skipping dependency check.")
        time.sleep(3)  # Pause for 3 seconds before proceeding

    package = "medicafe"
    
    current_version = get_installed_version(package)
    if not current_version:
        print("{} is not installed.".format(package))
        time.sleep(3)  # Pause for 3 seconds before exiting
        sys.exit(1)
    
    latest_version = get_latest_version(package)
    if not latest_version:
        print("Could not retrieve the latest version information.")
        time.sleep(3)  # Pause for 3 seconds before exiting
        sys.exit(1)
    
    print("Current version of {}: {}".format(package, current_version))
    print("Latest version of {}: {}".format(package, latest_version))
    
    if compare_versions(latest_version, current_version) > 0:
        print("A newer version is available. Proceeding with upgrade.")
        if upgrade_package(package):
            # Verify upgrade
            time.sleep(3)
            new_version = get_installed_version(package)
            if compare_versions(new_version, latest_version) >= 0:
                print("Upgrade successful. New version: {}".format(new_version))
            else:
                print("Upgrade failed. Current version remains: {}".format(new_version))
                time.sleep(3)  # Pause for 3 seconds before exiting
                sys.exit(1)
        else:
            time.sleep(3)  # Pause for 3 seconds before exiting
            sys.exit(1)
    else:
        print("You already have the latest version installed.")
        time.sleep(3)  # Pause for 3 seconds before exiting
        sys.exit(1)

if __name__ == "__main__":
    main()

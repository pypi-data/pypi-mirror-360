import subprocess

def scan_installed_packages():
    result = subprocess.run(["pip", "freeze"], capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")
    packages = {}
    for line in lines:
        if "==" in line:
            name, version = line.split("==")
            packages[name.lower()] = version
    return packages

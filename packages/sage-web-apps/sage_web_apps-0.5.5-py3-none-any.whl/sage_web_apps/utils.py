
import os
import platform
from typing import Optional
from .constants import SAGE_DOWNLOAD_URLS

def get_sage_download_url(version: str) -> Optional[str]:
    system = platform.system() # Get the system type (Linux, Windows, Darwin)

    if system not in ["Linux", "Windows", "Darwin"]:
        raise ValueError(f"Unsupported system: {system}. Supported systems are Linux, Windows, and Darwin (macOS).")
    
    machine = platform.machine()  # Get the machine architecture (e.g., x86_64, aarch64)
    if machine not in ["x86_64", "aarch64", "AMD64"]:
        raise ValueError(f"Unsupported architecture: {machine}. Supported architectures are x86_64, aarch64, and AMD64.")
    
    if machine == "AMD64":
        machine = "x86_64"

    if version not in SAGE_DOWNLOAD_URLS:
        raise ValueError(f"Unsupported version: {version}. Please check the SAGE_DOWNLOAD_URLS configuration.")
    
    if system.lower() not in SAGE_DOWNLOAD_URLS[version]:
        raise ValueError(f"No download URLs configured for {system} in version {version}. Please check the SAGE_DOWNLOAD_URLS configuration.")
    
    if machine not in SAGE_DOWNLOAD_URLS[version][system.lower()]:
        raise ValueError(f"No download URL configured for {machine} architecture in {system} system for version {version}. Please check the SAGE_DOWNLOAD_URLS configuration.")
    
    sage_download_url = SAGE_DOWNLOAD_URLS[version][system.lower()][machine]

    return sage_download_url


        
def verify_params(params):

    if params["mzml_paths"] is None or not isinstance(params["mzml_paths"], list) or len(params["mzml_paths"]) == 0:
        raise ValueError("mzml_paths must be a list with at least one element.")
    
    for path in params["mzml_paths"]:
        if not os.path.exists(path):
            raise ValueError(f"File {path} does not exist. Please check the file path.")
        
    if params["database"]["fasta"] is not None:
        if not os.path.exists(params["database"]["fasta"]):
            raise ValueError(f"Fasta file {params['database']['fasta']} does not exist. Please check the file path.")
    
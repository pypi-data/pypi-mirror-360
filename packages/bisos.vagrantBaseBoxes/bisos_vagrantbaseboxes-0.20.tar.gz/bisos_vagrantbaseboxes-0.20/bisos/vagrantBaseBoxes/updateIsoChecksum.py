# 
# This file was converted to pything from the bash segment below with AI.
# It has not been tested or used yet.
# ############
#!/bin/bash
# this will update the debian.pkr.hcl file with the current netboot image checksum.
# see https://www.debian.org/CD/verify
# see https://cdimage.debian.org/debian-cd/12.11.0/amd64/iso-cd/
set -eux
iso_url="$(perl -ne '/default\s*=\s*\"(https:.+\.debian\.org.+)\"/ && print $1' <debian.pkr.hcl)"
iso_checksum_url="$(dirname "$iso_url")/SHA256SUMS"
curl -O --silent --show-error "$iso_checksum_url"
curl -O --silent --show-error "$iso_checksum_url.sign"
gpg --keyserver hkp://keyring.debian.org/ --recv-keys 0x64E6EA7D 0x6294BE9B 0x09EA8AC3
gpg --verify SHA256SUMS.sign SHA256SUMS
iso_checksum="$(grep "$(basename "$iso_url")" SHA256SUMS | awk '{print $1}')"
for f in debian*.pkr.hcl; do
    sed -i -E "s,(default\s*=\s*\")(sha256:[a-z0-9]+)(\"),\\1sha256:$iso_checksum\\3,g" "$f"
done
rm SHA256SUMS*
echo 'iso_checksum updated successfully'

###########
from pathlib import Path
import subprocess
import re
import requests
from typing import List

def get_iso_url(file_path: Path) -> str:
    with file_path.open('r') as file:
        content = file.read()
    match = re.search(r'default\s*=\s*"(https:.+\.debian\.org.+)"', content)
    if match:
        return match.group(1)
    raise ValueError("ISO URL not found in the file.")

def download_file(url: str, destination: Path) -> None:
    response = requests.get(url)
    response.raise_for_status()
    destination.write_bytes(response.content)

def verify_signature() -> None:
    keys = ["0x64E6EA7D", "0x6294BE9B", "0x09EA8AC3"]
    for key in keys:
        subprocess.run(["gpg", "--keyserver", "hkp://keyring.debian.org/", "--recv-keys", key], check=True)
    subprocess.run(["gpg", "--verify", "SHA256SUMS.sign", "SHA256SUMS"], check=True)

def get_iso_checksum(iso_url: str) -> str:
    iso_name = Path(iso_url).name
    with open("SHA256SUMS", 'r') as file:
        for line in file:
            if iso_name in line:
                return line.split()[0]
    raise ValueError("ISO checksum not found.")

def update_checksum_in_files(files: List[Path], checksum: str) -> None:
    for file_path in files:
        content = file_path.read_text()
        updated_content = re.sub(r'(default\s*=\s*")(sha256:[a-z0-9]+)(")', f'\\1sha256:{checksum}\\3', content)
        file_path.write_text(updated_content)

def main() -> None:
    debian_file = Path("debian.pkr.hcl")
    iso_url = get_iso_url(debian_file)
    iso_checksum_url = f"{Path(iso_url).parent}/SHA256SUMS"
    
    download_file(iso_checksum_url, Path("SHA256SUMS"))
    download_file(f"{iso_checksum_url}.sign", Path("SHA256SUMS.sign"))
    
    verify_signature()
    
    iso_checksum = get_iso_checksum(iso_url)
    
    hcl_files = list(Path('.').glob('debian*.pkr.hcl'))
    update_checksum_in_files(hcl_files, iso_checksum)
    
    for file in Path('.').glob('SHA256SUMS*'):
        file.unlink()
    
    print('iso_checksum updated successfully')

if __name__ == "__main__":
    main()

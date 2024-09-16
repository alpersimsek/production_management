from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Body, BackgroundTasks
from fastapi.responses import FileResponse
import os
import shutil
import zipfile
import tarfile
import gzip
from pathlib import Path
import logging
from time import sleep
import csv
from scapy.all import rdpcap, wrpcap, Ether, IP, ARP, UDP, TCP, sniff, CookedLinux
import re
import ipaddress
import random

router = APIRouter()

BASE_DIR = "users"
process_progress = {}  # Dictionary to store progress for each task
masking_progress = {}
zip_mask_progress = {}

GDPR_MASK_FILE = "gdpr_map.csv"
GDPR_MAP_DIR = os.path.join(BASE_DIR, "gdpr_map")
GDPR_MAP_PATH = os.path.join(GDPR_MAP_DIR, GDPR_MASK_FILE)


# Private IP address ranges based on RFC 1918
PRIVATE_IP_RANGES = [
    ipaddress.IPv4Network('10.0.0.0/8'),
    ipaddress.IPv4Network('172.16.0.0/12'),
    ipaddress.IPv4Network('192.168.0.0/16')
]

# MAC address starting point for masking
MASKED_MAC_START = "00:00:00:00:00:00"

# Utility function to ensure the directory exists
def ensure_dir(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Create GDPR mask file if not present
def ensure_gdpr_map_file(username: str):
    # Define the path to the GDPR map directory and file
    ensure_dir(GDPR_MAP_DIR)
    
    # Check if the file exists, and if not, create it with headers
    if not os.path.exists(GDPR_MAP_PATH):
        with open(GDPR_MAP_PATH, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write the column headers
            writer.writerow(['TYPE', 'ORIGINAL', 'MASKED'])
    return GDPR_MAP_PATH

# Load the GDPR mask map (original -> masked)
def load_gdpr_map():
    gdpr_map = {}
    highest_ip = ipaddress.IPv4Address('10.0.0.0')  # Start from 10.0.0.0 by default
    highest_mac = MASKED_MAC_START  # Start MAC from 00:00:00:00:00:00

    try:
        with open(GDPR_MAP_PATH, mode='r') as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip header
            for row in reader:
                if len(row) == 3:
                    entry_type, original, masked = row
                    gdpr_map[original] = (entry_type, masked)

                    # Update the highest IP or MAC based on the entry type
                    if entry_type == "IP":
                        try:
                            masked_ip = ipaddress.IPv4Address(masked)
                            if masked_ip > highest_ip:
                                highest_ip = masked_ip
                        except ValueError:
                            pass  # Ignore invalid IP addresses
                    elif entry_type == "MAC":
                        if re.match(r'(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}', masked):
                            if masked > highest_mac:
                                highest_mac = masked
    except FileNotFoundError:
        # Create the file if it does not exist
        ensure_gdpr_map_file()
    return gdpr_map, highest_ip, highest_mac

# Save the updated GDPR map with TYPE, ORIGINAL, and MASKED
def save_gdpr_map(gdpr_map):
    with open(GDPR_MAP_PATH, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['TYPE', 'ORIGINAL', 'MASKED'])  # Write the header with TYPE
        for original, (entry_type, masked) in gdpr_map.items():
            writer.writerow([entry_type, original, masked])

# Check if the string is an IP address
def is_ip_address(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

# Increment an IP address
def increment_ip(ip):
    ip_obj = ipaddress.IPv4Address(ip)
    next_ip = ip_obj + 1
    return str(next_ip)

# Helper function to increment MAC address
def increment_mac(mac_address):
    # Convert MAC address from hex string to int, increment, and convert back to hex string
    mac_int = int(mac_address.replace(':', ''), 16)
    mac_int += 1
    mac_hex = f'{mac_int:012x}'  # 12 hex digits
    return ':'.join(mac_hex[i:i+2] for i in range(0, 12, 2))  # Format back to MAC address

# Check if an IP is within private ranges (RFC 1918)
def is_in_private_ip_range(ip):
    ip_obj = ipaddress.IPv4Address(ip)
    return any(ip_obj in private_range for private_range in PRIVATE_IP_RANGES)


# Function to get the highest masked IP address from the GDPR map
def get_highest_masked_ip(gdpr_map):
    highest_ip = ipaddress.IPv4Address('10.0.0.0')
    for masked in gdpr_map.values():
        try:
            # Ignore MAC addresses and only process valid IP addresses
            masked_ip = ipaddress.IPv4Address(masked)
            if masked_ip > highest_ip:
                highest_ip = masked_ip
        except ValueError:
            # Ignore non-IP values (likely MAC addresses)
            continue
    return highest_ip + 1  # Return the next IP

# Generate a new random private IP address
def generate_new_ip():
    network = random.choice(PRIVATE_IP_RANGES)
    return str(ipaddress.IPv4Address(network.network_address + random.randint(1, network.num_addresses - 2)))


# Main function to mask IP and MAC addresses in a given text
def mask_text_files(text):
    # Load GDPR map and get the highest masked IP and MAC during the load
    gdpr_map, highest_ip, highest_mac = load_gdpr_map()
    new_gdpr_map = {}
    masked_text = text

    # Start masking from the next IP address after the highest one found
    current_ip = highest_ip + 1

    # Start masking from the next MAC address after the highest one found
    current_mac = increment_mac(highest_mac)

    # Start masking from the next username as 'user1', 'user2', etc.
    user_count = sum(1 for value in gdpr_map.values() if value[0] == "USER") + 1 
    # Start user count

    domain_count = sum(1 for value in gdpr_map.values() if value[0] == "DOMAIN") + 1  # Start domain count for uniqueness

    dn_count = sum(1 for value in gdpr_map.values() if value[0] in ["E164", "NATIONAL_DN"]) + 1  # Start DN count


    # Regex patterns to match IPv4 and MAC addresses
    ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
    mac_pattern = re.compile(r'(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}')
    username_pattern = re.compile(r'(?i)(\[?(user(?:name)?\s*:\s*)([A-Za-z0-9_@.]+)\]?)')
    sip_uri_pattern = re.compile(r'(sip[s]?:[A-Za-z0-9_+%.-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})')
    domain_pattern = re.compile(r'\b[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')  # Matches domain-like patterns
    e164_pattern = re.compile(r'\+?\d{10,15}')  # Matches E164 format (+1234567890)
    dn_pattern = re.compile(r'\b\d{7,10}\b')  # Matches national dial numbers
    dn_block_pattern = re.compile(r'\[DN:\s*([\d\s]+)\]')  # Matches [DN: XXXXXXXXXX YYYYYYYYYY]


    # Store all replacements in a set to prevent unnecessary multiple replacements
    replacements = {}

    # Function to mask a DN number and ensure it's in the GDPR map
    def mask_dn(dn):
        nonlocal dn_count
        if dn in gdpr_map:
            return gdpr_map[dn][1]  # Use the existing masked DN
        else:
            # Mask the national DN and save it
            masked_dn = f"000{dn_count}"
            new_gdpr_map[dn] = ("NATIONAL_DN", masked_dn)  # Save with TYPE "NATIONAL_DN"
            dn_count += 1
            return masked_dn

    # Search for IP addresses in the text
    for match in ip_pattern.findall(text):
        if match in gdpr_map:
            # If already masked, use the existing masked IP
            masked_ip = gdpr_map[match][1]  # Retrieve the masked IP from the map
        else:
            # Mask the IP and update the GDPR map
            masked_ip = str(current_ip)
            new_gdpr_map[match] = ("IP", masked_ip)  # Save with TYPE "IP"
            current_ip += 1  # Increment to the next IP

        # Save the replacement to avoid multiple replacements
        replacements[match] = masked_ip

    # Search for MAC addresses in the text
    for match in mac_pattern.findall(text):
        if match in gdpr_map:
            # If already masked, use the existing masked MAC
            masked_mac = gdpr_map[match][1]  # Retrieve the masked MAC from the map
        else:
            # Mask the MAC and update the GDPR map
            masked_mac = current_mac
            new_gdpr_map[match] = ("MAC", masked_mac)  # Save with TYPE "MAC"
            current_mac = increment_mac(current_mac)  # Increment to the next MAC

        # Save the replacement to avoid multiple replacements
        replacements[match] = masked_mac

    # Search for usernames in the text
    for full_match, prefix, username in username_pattern.findall(text):
        if username in gdpr_map:
            # If already masked, use the existing masked username
            masked_username = gdpr_map[username][1]  # Retrieve the masked username from the map
        else:
            # Mask the username and update the GDPR map
            masked_username = f"user{user_count}"
            new_gdpr_map[username] = ("USER", masked_username)  # Save with TYPE "USER"
            user_count += 1  # Increment to the next user number

        # Save the replacement to avoid multiple replacements
        replacements[full_match] = f"{prefix}{masked_username}]"

    # Search for SIP URIs and other unique identifiers
    for match in sip_uri_pattern.findall(text):
        user_part, domain_part = match.split('@')

        # Check if the domain has already been masked
        if domain_part in gdpr_map:
            masked_domain = gdpr_map[domain_part][1]  # Use the existing masked domain
        else:
            # Create a new unique masked domain
            masked_domain = f"masked{domain_count}.com"
            new_gdpr_map[domain_part] = ("DOMAIN", masked_domain)  # Save with TYPE "DOMAIN"
            domain_count += 1  # Increment to the next domain number

        # Create the masked SIP URI
        masked_uri = f"user{user_count}@{masked_domain}"
        new_gdpr_map[match] = ("SIP_URI", masked_uri)  # Save with TYPE "SIP_URI"
        user_count += 1  # Increment to the next user number
        replacements[match] = masked_uri

    # Search for standalone domains in the text
    for domain in domain_pattern.findall(text):
        if domain in gdpr_map:
            masked_domain = gdpr_map[domain][1]  # Use the existing masked domain
        else:
            # Create a new unique masked domain
            masked_domain = f"masked{domain_count}.com"
            new_gdpr_map[domain] = ("DOMAIN", masked_domain)  # Save with TYPE "DOMAIN"
            domain_count += 1  # Increment to the next domain number
        replacements[domain] = masked_domain

    # Search for E164 international numbers
    for e164 in e164_pattern.findall(text):
        if e164 in gdpr_map:
            masked_e164 = gdpr_map[e164][1]  # Use the existing masked E164 number
        else:
            # Mask the E164 number and save it
            masked_e164 = f"+{dn_count}000000000"
            new_gdpr_map[e164] = ("E164", masked_e164)  # Save with TYPE "E164"
            dn_count += 1
        replacements[e164] = masked_e164

    # Search for national dial numbers
    for dn in dn_pattern.findall(text):
        if dn in gdpr_map:
            masked_dn = gdpr_map[dn][1]  # Use the existing masked DN
        else:
            # Mask the national DN and save it
            masked_dn = f"000{dn_count}"
            new_gdpr_map[dn] = ("NATIONAL_DN", masked_dn)  # Save with TYPE "NATIONAL_DN"
            dn_count += 1
        replacements[dn] = masked_dn

    # Search for [DN: XXXXXXXXXX YYYYYYYYYY] format and mask each number within
    for dn_block in dn_block_pattern.findall(text):
        masked_block = []
        dn_list = dn_block.split()  # Split the numbers in the block
        for dn in dn_list:
            masked_dn = mask_dn(dn)
            masked_block.append(masked_dn)

        # Replace the original block with the masked block
        masked_block_str = "[DN: " + " ".join(masked_block) + "]"
        replacements[f"[DN: {dn_block}]"] = masked_block_str


    # Replace all matches (both IPs and MACs) in the text with their masked values
    for original, masked in replacements.items():
        masked_text = masked_text.replace(original, masked)

    # Update the GDPR mask map
    gdpr_map.update(new_gdpr_map)
    save_gdpr_map(gdpr_map)

    return masked_text

# Function to check if a string is a valid MAC address
def is_mac_address(mac):
    return re.match(r'(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}', mac)

# Function to update progress
def update_unzip_progress(unzip_task_id, progress):
    process_progress[unzip_task_id] = progress

# Update progress for masking tasks
def update_mask_task_progress(mask_task_id, progress):
    masking_progress[mask_task_id] = progress

# Update progress for masking tasks
def update_mask_zip_task_progress(zip_mask_task_id, progress):
    zip_mask_progress[zip_mask_task_id] = progress

# Function to extract the initial archive with progress
def unzip_file_with_progress(unzip_task_id, file_path, extract_dir):
    os.makedirs(extract_dir, exist_ok=True)
    file_extract_dir = extract_dir

    total_files = 0
    extracted_files = 0

    try:
        # Handle zip files
        if file_path.endswith('.zip'):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                total_files = len(zip_ref.namelist())
                for file in zip_ref.namelist():
                    zip_ref.extract(file, file_extract_dir)
                    extracted_files += 1
                    update_unzip_progress(unzip_task_id, int((extracted_files / total_files) * 100))
                    sleep(0.1)  # Simulating time taken for extraction
        # Handle tar files
        elif file_path.endswith('.tar') or file_path.endswith('.tar.gz') or file_path.endswith('.tgz'):
            with tarfile.open(file_path, 'r') as tar_ref:
                members = tar_ref.getmembers()
                total_files = len(members)
                for member in members:
                    tar_ref.extract(member, file_extract_dir)
                    extracted_files += 1
                    update_unzip_progress(unzip_task_id, int((extracted_files / total_files) * 100))
                    sleep(0.1)  # Simulating time taken for extraction
        # Handle gzip files
        elif file_path.endswith('.gz'):
            output_file_path = os.path.join(file_extract_dir, Path(file_path).stem)
            with gzip.open(file_path, 'rb') as gz_file:
                with open(output_file_path, 'wb') as out_file:
                    shutil.copyfileobj(gz_file, out_file)
            update_unzip_progress(unzip_task_id, 100)
        else:
            shutil.move(file_path, file_extract_dir)
            update_unzip_progress(unzip_task_id, 100)
    except Exception as e:
        update_unzip_progress(unzip_task_id, -1)  # Indicate failure

    # After initial extraction, handle nested archives
    extract_nested_archives_with_progress(unzip_task_id, file_extract_dir)
    update_unzip_progress(unzip_task_id, 100)  # Final progress update

# Function to extract nested archives with progress
def extract_nested_archives_with_progress(unzip_task_id, directory):
    processed_files = set()

    while True:
        files_extracted = False
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path in processed_files:
                    continue

                try:
                    # Handle nested zip files
                    if file.endswith('.zip'):
                        with zipfile.ZipFile(file_path, 'r') as zip_ref:
                            zip_ref.extractall(root)
                        os.remove(file_path)
                        files_extracted = True
                    # Handle nested tar files
                    elif file.endswith('.tar'):
                        with tarfile.open(file_path, 'r') as tar_ref:
                            tar_ref.extractall(root)
                        os.remove(file_path)
                        files_extracted = True
                    # Handle nested tar.gz files
                    elif file.endswith('.tar.gz') or file.endswith('.tgz'):
                        with tarfile.open(file_path, 'r:gz') as tar_ref:
                            tar_ref.extractall(root)
                        os.remove(file_path)
                        files_extracted = True
                    # Handle nested gzip files
                    elif file.endswith('.gz'):
                        output_file_path = os.path.join(root, file[:-3])
                        with gzip.open(file_path, 'rb') as gz_file:
                            with open(output_file_path, 'wb') as out_file:
                                shutil.copyfileobj(gz_file, out_file)
                        os.remove(file_path)
                        files_extracted = True
                except Exception as e:
                    logging.error(f"Failed to extract {file_path}: {e}")
                    processed_files.add(file_path)  # Mark the file as processed to avoid infinite loop

                processed_files.add(file_path)

        if not files_extracted:
            break

# Utility to detect if the file is a packet file (like PCAP)
def is_packet_file(file_path):
    # Logic to detect if the file is a packet/PCAP file, even without .pcap extension
    try:
        packets = rdpcap(file_path)
        return len(packets) > 0
    except:
        return False

# Function to mask IP and MAC addresses in files
def mask_files_with_progress(mask_task_id, username: str, file_path: str):
    process_path = os.path.join(BASE_DIR, username, "process_zip", file_path)
    processed_dir = os.path.join(BASE_DIR, username, "processed", file_path)

    gdpr_map_path = ensure_gdpr_map_file(username)

    total_files = sum([len(files) for _, _, files in os.walk(process_path)])
    masked_files = 0

    try:
        for root, _, files in os.walk(process_path):
            for file in files:
                file_full_path = os.path.join(root, file)
                if is_packet_file(file_full_path):
                    print("PACKET")
                    mask_packet_file(file_full_path, processed_dir)
                else:
                    print("FILE")
                    mask_text_file(file_full_path, processed_dir)
                masked_files += 1
                update_mask_task_progress(mask_task_id, int((masked_files / total_files) * 100))
    except Exception as e:
        print(e)
        update_mask_task_progress(mask_task_id, -1)  # Indicate failure

    # Final step: archive the masked files (optional)
    # archive_processed_files(username, file_path)
    update_mask_task_progress(mask_task_id, 100)


# Function to safely decode bytes-like objects to string
def safe_decode_bytes(data):
    if isinstance(data, bytes):
        return data.decode('utf-8', errors='ignore')  # Decode to string, ignore errors
    return data

# Function to mask IP addresses using the GDPR map and update the map with TYPE "IP"
def mask_ip_packet(ip_address, gdpr_map, current_ip):
    if ip_address in gdpr_map:
        return gdpr_map[ip_address][1]  # Return the masked IP from the map
    else:
        masked_ip = str(current_ip)
        gdpr_map[ip_address] = ("IP", masked_ip)  # Save with TYPE "IP"
        return masked_ip

# Function to mask MAC addresses using the GDPR map and update the map with TYPE "MAC"
def mask_mac_packet(mac_address, gdpr_map, current_mac):
    if mac_address in gdpr_map:
        return gdpr_map[mac_address][1]  # Return the masked MAC from the map
    else:
        masked_mac = current_mac
        gdpr_map[mac_address] = ("MAC", masked_mac)  # Save with TYPE "MAC"
        return masked_mac

# Function to mask a packet file (PCAP or packet-like files) and save to the processed directory
def mask_packet_file(file_path, output_dir):
    packets = rdpcap(file_path)

    gdpr_map, highest_ip, highest_mac = load_gdpr_map()
    
    # Process each packet in the file
    for packet in packets:
        try:
            # Mask MAC addresses in the Ethernet layer, if present
            if packet.haslayer(Ether):
                if Ether in packet:
                    if is_mac_address(safe_decode_bytes(packet[Ether].src)):
                        packet[Ether].src = mask_mac_packet(safe_decode_bytes(packet[Ether].src), gdpr_map, highest_mac)
                        highest_mac = increment_mac(highest_mac)  # Increment the MAC
                    if is_mac_address(safe_decode_bytes(packet[Ether].dst)):
                        packet[Ether].dst = mask_mac_packet(safe_decode_bytes(packet[Ether].dst), gdpr_map, highest_mac)
                        highest_mac = increment_mac(highest_mac)

            # Mask IP addresses in the IP layer, if present
            if packet.haslayer(IP):
                if IP in packet:
                    if is_ip_address(safe_decode_bytes(packet[IP].src)):
                        packet[IP].src = mask_ip_packet(safe_decode_bytes(packet[IP].src), gdpr_map, highest_ip)
                        highest_ip += 1  # Increment the IP
                    if is_ip_address(safe_decode_bytes(packet[IP].dst)):
                        packet[IP].dst = mask_ip_packet(safe_decode_bytes(packet[IP].dst), gdpr_map, highest_ip)
                        highest_ip += 1

            # Mask MAC and IP addresses in the ARP layer, if present
            if packet.haslayer(ARP):
                if ARP in packet:
                    if is_mac_address(safe_decode_bytes(packet[ARP].hwsrc)):
                        packet[ARP].hwsrc = mask_mac_packet(safe_decode_bytes(packet[ARP].hwsrc), gdpr_map, highest_mac)
                        highest_mac = increment_mac(highest_mac)
                    if is_mac_address(safe_decode_bytes(packet[ARP].hwdst)):
                        packet[ARP].hwdst = mask_mac_packet(safe_decode_bytes(packet[ARP].hwdst), gdpr_map, highest_mac)
                        highest_mac = increment_mac(highest_mac)
                    if is_ip_address(safe_decode_bytes(packet[ARP].psrc)):
                        packet[ARP].psrc = mask_ip_packet(safe_decode_bytes(packet[ARP].psrc), gdpr_map, highest_ip)
                        highest_ip += 1
                    if is_ip_address(safe_decode_bytes(packet[ARP].pdst)):
                        packet[ARP].pdst = mask_ip_packet(safe_decode_bytes(packet[ARP].pdst), gdpr_map, highest_ip)
                        highest_ip += 1

            # Mask IP and MAC addresses in CookedLinux layer, if present
            #if CookedLinux in packet:
            #    if is_mac_address(safe_decode_bytes(packet[CookedLinux].src)):
            #        packet[CookedLinux].src = mask_mac_packet#(safe_decode_bytes(packet[CookedLinux].src), gdpr_map, highest_mac)
            #        highest_mac = increment_mac(highest_mac)
            #    if is_mac_address(safe_decode_bytes(packet[CookedLinux].dst)):
            #        packet[CookedLinux].dst = mask_mac_packet(safe_decode_bytes(packet[CookedLinux].dst), gdpr_map, highest_mac)
            #        highest_mac = increment_mac(highest_mac)

            # Mask SIP payload in UDP packets (if SIP port 5060 is used)
            if packet.haslayer(UDP):
                if packet.haslayer(UDP) and (packet[UDP].sport == 5060 or packet[UDP].dport == 5060):
                    # Decode the SIP payload and mask IPs in the payload
                    sip_payload = bytes(packet[UDP].payload)
                    masked_sip_payload = mask_sip_payload(sip_payload.decode('utf-8', errors="backslashreplace"), gdpr_map, highest_ip)

                    # Replace the original payload with the masked payload
                    packet[UDP].remove_payload()
                    packet[UDP].add_payload(masked_sip_payload)


            # Mask IP addresses in the TCP layer, if present
            if packet.haslayer(TCP):
                if TCP in packet:
                    if is_ip_address(safe_decode_bytes(packet[IP].src)):
                        packet[IP].src = mask_ip_packet(safe_decode_bytes(packet[IP].src), gdpr_map, highest_ip)
                        highest_ip += 1
                    if is_ip_address(safe_decode_bytes(packet[IP].dst)):
                        packet[IP].dst = mask_ip_packet(safe_decode_bytes(packet[IP].dst), gdpr_map, highest_ip)
                        highest_ip += 1
        except Exception as e:
            print(e)
            continue
       
       

    original_filename, original_extension = os.path.splitext(os.path.basename(file_path))  # Get filename and extension
    output_file = os.path.join(output_dir, f"{original_filename}_masked{original_extension}")
    print(original_filename)
    print(original_extension)

    # Create the processed directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the masked packets to the processed directory
    wrpcap(output_file, packets)
    return output_file


# Function to mask SIP payload by masking IP addresses within it using the GDPR map
def mask_sip_payload(payload, gdpr_map, highest_ip):
    # Regex pattern to match IPv4 addresses
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'

    # Function that masks IPs using the existing gdpr_map and highest_ip
    def mask_ip_in_payload(match):
        ip_address = match.group(0)
        # Use the existing mask_ip function to ensure consistent IP masking
        masked_ip = mask_ip_packet(ip_address, gdpr_map, highest_ip)
        return masked_ip

    # Use regex to find and mask IP addresses in the SIP payload
    masked_payload = re.sub(ip_pattern, mask_ip_in_payload, payload)

    return masked_payload

# Function to mask a text file and save it in <username>/processed/<filename>/
def mask_text_file(file_path, processed_dir):
    with open(file_path, 'r') as file:
        content = file.read()

    # Mask IP addresses
    masked_content = mask_text_files(content)

    # Construct the new path in the processed directory
    relative_path = os.path.relpath(file_path, start=processed_dir.replace("processed", "process_zip"))  # Find the relative path
    original_filename, original_extension = os.path.splitext(relative_path)  # Preserve original extension
    processed_file_path = os.path.join(processed_dir, f"{original_filename}_masked{original_extension}")

    # Ensure the directory structure exists in the processed directory
    os.makedirs(os.path.dirname(processed_file_path), exist_ok=True)

    # Save the masked content to the processed directory
    with open(processed_file_path, 'w') as masked_file:
        masked_file.write(masked_content)

def zip_file_with_progress(zip_mask_task_id, username: str, file_path: str):

    processed_dir = os.path.join(BASE_DIR, username, "processed", file_path)
    archive_path = os.path.join(BASE_DIR, username, "processed", f"{file_path}_archive.zip")
    
    total_files = sum([len(files) for r, d, files in os.walk(processed_dir)])
    zipped_files = 0

    try:
        with zipfile.ZipFile(archive_path, 'w') as zipf:
            for root, dirs, files in os.walk(processed_dir):
                for file in files:
                    file_full_path = os.path.join(root, file)
                    zipf.write(file_full_path, os.path.relpath(file_full_path, processed_dir))
                    zipped_files += 1
                    progress = (zipped_files / total_files) * 100
                    update_mask_zip_task_progress(zip_mask_task_id, int(progress))  # Reuse the mask progress tracker
                   
        update_mask_zip_task_progress(zip_mask_task_id, 100)  # Mark as completed
    except Exception as e:
        update_mask_zip_task_progress(zip_mask_task_id, -1)  # Indicate failure
        raise HTTPException(status_code=500, detail=f"File zipping failed: {str(e)}")

# Background task for file processing
def background_unzip_process(unzip_task_id, file_path, extracted_dir):
    unzip_file_with_progress(unzip_task_id, file_path, extracted_dir)

# Background task to mask files
def background_mask_process(mask_task_id, username: str, file_path: str):
    mask_files_with_progress(mask_task_id, username, file_path)

# Background task for file processing
def background_zip_mask_process (zip_mask_task_id, username: str, file_path: str):
    zip_file_with_progress(zip_mask_task_id, username, file_path)

# Upload a file to /users/<username>/uploads
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...), 
    username: str = Form(...)
):
    user_upload_path = os.path.join(BASE_DIR, username, "uploads")
    ensure_dir(user_upload_path)  # Ensure upload directory exists

    # Save the uploaded file
    file_path = os.path.join(user_upload_path, file.filename)
    with open(file_path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"detail": f"File '{file.filename}' uploaded successfully"}

# List user files in a specific folder (uploads/processed)
@router.get("/{username}/{folder}")
async def list_user_files(username: str, folder: str):
    valid_folders = ["uploads", "processed"]

    # Ensure folder name is valid
    if folder not in valid_folders:
        raise HTTPException(status_code=400, detail="Invalid folder")

    files_path = os.path.join(BASE_DIR, username, folder)
    ensure_dir(files_path)  # Ensure the folder exists

    files = os.listdir(files_path)
    return {"files": files}

# Delete a file from uploads or processed folder
@router.delete("/delete/{username}/{folder}/{filename}")
async def delete_file(username: str, filename: str, folder: str = "uploads"):
    valid_folders = ["uploads", "processed"]

    # Ensure folder is valid
    if folder not in valid_folders:
        raise HTTPException(status_code=400, detail="Invalid folder")

    file_path = os.path.join(BASE_DIR, username, folder, filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        return {"detail": f"File '{filename}' deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found")

# Download a file from the processed folder
@router.get("/download/{username}/{filename}")
async def download_file(username: str, filename: str):
    print(filename)
    file_path = os.path.join(BASE_DIR, username, "processed", filename)
    print(file_path)

    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found")

# Start file processing in the background
@router.post("/process/{filename}")
async def process_file(filename: str, background_tasks: BackgroundTasks, data: dict = Body(...)):
    username = data.get("username")

    if not username:
        raise HTTPException(status_code=400, detail="Username is required")

    user_upload_path = os.path.join(BASE_DIR, username, "uploads", filename)
    extract_dir = os.path.join(BASE_DIR, username, "process_zip", filename)

    if not os.path.exists(user_upload_path):
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found in uploads")

    unzip_task_id = f"{username}_{filename}"
    background_tasks.add_task(background_unzip_process, unzip_task_id, user_upload_path, extract_dir)

    return {"detail": f"Processing of file '{filename}' started.", "task_id": unzip_task_id}

# Polling endpoint to check processing progress
@router.get("/process/progress/{task_id}")
async def get_process_progress(task_id: str):
    progress = process_progress.get(task_id, 0)

    if progress == -1:
        raise HTTPException(status_code=500, detail="File processing failed")

    return {"progress": progress}

# Start file masking in the background
@router.post("/mask/{filename}")
async def process_mask(filename: str, background_tasks: BackgroundTasks, data: dict = Body(...)):
    username = data.get("username")
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")

    process_zip_path = os.path.join(BASE_DIR, username, "process_zip", filename)
    if not os.path.exists(process_zip_path):
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found in process_zip")

    mask_task_id = f"{username}_mask_{filename}"
    background_tasks.add_task(background_mask_process, mask_task_id, username, filename)

    return {"detail": f"Masking of file '{filename}' started.", "maskTask_id": mask_task_id}

# Polling endpoint to check processing progress
@router.get("/masking/progress/{task_id}")
async def get_process_progress(task_id: str):
    progress = masking_progress.get(task_id, 0)
    if progress == -1:
        raise HTTPException(status_code=500, detail="File processing failed")

    return {"progress": progress}


# Start masked files archieve in the background
@router.post("/zipMask/{filename}")
async def process_zip(filename: str, background_tasks: BackgroundTasks, data: dict = Body(...)):
    username = data.get("username")
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")

    process_zip_path = os.path.join(BASE_DIR, username, "processed", filename)
    if not os.path.exists(process_zip_path):
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found in processed folder")

    zip_mask_task_id = f"{username}_mask_{filename}"
    background_tasks.add_task(background_zip_mask_process, zip_mask_task_id, username, filename)

    return {"detail": f"Masking of file '{filename}' started.", "zipMaskTask_id": zip_mask_task_id}

# Polling endpoint to check processing progress
@router.get("/masking/zip/{task_id}")
async def get_process_progress_mask_zip(task_id: str):
    progress = zip_mask_progress.get(task_id, 0)
    if progress == -1:
        raise HTTPException(status_code=500, detail="File processing failed")

    return {"progress": progress}

@router.get("/gdpr_map/")
async def get_gdpr_map():
    gdpr_map_path = os.path.join(BASE_DIR, "gdpr_map", GDPR_MASK_FILE)
    if not os.path.exists(gdpr_map_path):
        raise HTTPException(status_code=404, detail="GDPR map file not found")

    return FileResponse(gdpr_map_path, media_type="text/csv", filename="gdpr_map.csv")
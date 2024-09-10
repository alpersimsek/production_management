import os
import csv

# Load or create the GDPR map
def load_gdpr_map():
    map_file = "users/gdpr_map/gdpr_map.csv"
    if not os.path.exists(map_file):
        with open(map_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["original_value", "masked_value"])
    return map_file

# Add new values to the GDPR map
def add_to_gdpr_map(original_value, masked_value):
    map_file = load_gdpr_map()
    with open(map_file, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([original_value, masked_value])

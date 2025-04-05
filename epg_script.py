import json
import requests
import xml.etree.ElementTree as ET

# List of EPG provider URLs
provider_urls = {
    "blastTV.xml": "https://raw.githubusercontent.com/tv-noyzkie/tvguidePH/refs/heads/main/output/blast.xml",
    "clickthecity.xml": "https://raw.githubusercontent.com/tv-noyzkie/tvguidePH/refs/heads/main/output/clickthecity.xml",
    "cignal.xml": "https://raw.githubusercontent.com/tv-noyzkie/tvguidePH/refs/heads/main/output/cplay.xml",
    "mysky.xml": "https://raw.githubusercontent.com/tv-noyzkie/tvguidePH/refs/heads/main/output/mysky.xml",
}

# Load custom tvg-ids
try:
    with open("tvg_ids.json", "r", encoding="utf-8") as f:
        custom_tvg_ids = json.load(f)
    print(f"✅ Loaded {len(custom_tvg_ids)} TVG IDs from JSON")
except FileNotFoundError:
    print("❌ Error: tvg_ids.json not found!")
    custom_tvg_ids = {}

# Function to fetch EPG data
def fetch_epg_data(url):
    try:
        print(f"📡 Fetching: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text if response.text.strip() else None
    except requests.RequestException as e:
        print(f"❌ Failed to fetch {url}: {e}")
        return None

# Parse EPG data
def parse_epg_data(epg_xml):
    try:
        return ET.ElementTree(ET.fromstring(epg_xml))
    except ET.ParseError as e:
        print(f"❌ XML Parsing Error: {e}")
        return None

# Load EPG data and filter channels
epg_channels = {}
epg_programmes = []

for provider_file, url in provider_urls.items():
    epg_data = fetch_epg_data(url)
    if epg_data:
        tree = parse_epg_data(epg_data)
        if tree:
            root = tree.getroot()
            
            # Process channels
            for channel in root.findall('channel'):
                original_id = channel.get('id')

                # Find if there's a mapping for this channel
                matched_entry = next((key for key, val in custom_tvg_ids.items() if val["original-id"] == original_id and val["provider-url"] == provider_file), None)

                if matched_entry:
                    final_tvg_id = matched_entry  # Use the key in JSON as the final TVG ID
                    
                    custom_display_name = custom_tvg_ids[matched_entry]["tvg-name"]
                    if not custom_display_name:  # Use default from EPG if custom display name is missing
                        custom_display_name = channel.find("display-name").text

                    print(f"✅ Using TVG ID: {final_tvg_id} (Maps to {original_id}) - Display Name: {custom_display_name}")

                    # Update the channel ID and display name
                    channel.set("id", final_tvg_id)
                    display_name_element = channel.find("display-name")
                    if display_name_element is not None:
                        display_name_element.text = custom_display_name

                    epg_channels[final_tvg_id] = ET.tostring(channel, encoding='unicode')

            # Process programmes
            for programme in root.findall("programme"):
                original_channel_id = programme.get("channel")

                # Find if there's a custom TVG ID
                matched_entry = next((key for key, val in custom_tvg_ids.items() if val["original-id"] == original_channel_id), None)
                if matched_entry:
                    final_tvg_id = matched_entry  # Use the JSON key as the final TVG ID

                    programme.set("channel", final_tvg_id)  # Update programme channel to custom ID
                    epg_programmes.append(ET.tostring(programme, encoding='unicode'))

# Save filtered EPG data
if epg_channels:
    with open("epg.xml", "w", encoding="utf-8") as f:
        f.write("<?xml version='1.0' encoding='UTF-8'?>\n<tv>\n")
        for channel_xml in epg_channels.values():
            f.write(channel_xml + "\n")
        for programme_xml in epg_programmes:
            f.write(programme_xml + "\n")
        f.write("</tv>\n")
    print("✅ Successfully saved epg.xml with custom TVG IDs & Display Names")
else:
    print("❌ No valid EPG data found!")

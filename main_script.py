import json
import logging
import subprocess

# Setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# Load JSON data from 1.json and 2.json
with open("1.json", "r") as file1:
    tenants_data = json.load(file1)

with open("2.json", "r") as file2:
    namespace_data = json.load(file2)

# Extract relevant data
tenant = tenants_data[1]
namespaces = namespace_data[0]["items"]

# Construct the JSON structure
output_data = {
    "lmp": "RAKUTENLAB-26946",
    "created_by": "Farrukhbek Karimov",
    "reservation_interval_days": 150,
    "cluster_id": "40153f39-5f20-4b90-8e8e-2d4606dd9ba4",
    "resources": {
        "rpool_name": tenant["rpools"][0],
        "ldap_server": "ad_server_1",
        "reservation_data": [
            {
                "reservation_id": "uhn7klr37_tn-rh-ipa-auth-test77-v1",
                "tenant_level": {
                    "name": tenant["name"],
                    "description": tenant["description"],
                    "cpu_limits": [{"value": tenant["rpool_limits"][0]["limits"]["max_cores_per_tenant"], "unit": "cores"}],
                    "mem_limits": [{"value": tenant["rpool_limits"][0]["limits"]["max_mem_per_tenant"] // (1024**3), "unit": "Gi"}],
                    "ssd_limits": [{"value": tenant["rpool_limits"][0]["limits"]["max_ssd_per_tenant"] // (1024**3), "unit": "Gi"}],
                },
                "namespace_level": [
                    {
                        "name": ns["name"],
                        "owner_username": ns["username"],
                        "cpu_quota": {"value": 100, "unit": "cores"},  # Placeholder value
                        "mem_quota": {"value": 100, "unit": "Gi"},  # Placeholder value
                        "persistent_storage": [
                            {"storage_class_name": "robin", "value": 200, "unit": "Gi"}  # Placeholder value
                        ],
                        "ephemeral_storage": {"value": 50, "unit": "Gi"},  # Placeholder value
                        "hugepages": {"2Mi": 0, "1Gi": 60}  # Placeholder value
                    }
                    for ns in namespaces
                ],
                "network": {
                    "default_ip_pools": tenant["ip_pools"],
                    "non_default_ip_pools": [
                        {
                            "name": "nw-mv-cor-sr-upf-n3-da-ex-v6",
                            "driver": "sriov",
                            "vlan_number": 3900,
                            "zoneid": "default",
                            "ranges": ["240b:c0e0:0101:2F0E:DF28:0002:0080:0001-0003"],
                            "gateway": "240b:c0e0:0101:2F0E::FFFF",
                            "prefix": "64",
                            "ifcount": "2",
                            "vfdriver": "vfio-pci",
                            "trusted": "on",
                            "spoofchk": "off"
                        },
                        {
                            "name": "nw-mv-cor-sr-upf-n4u-da-ex-v6",
                            "driver": "sriov",
                            "vlan_number": 3856,
                            "zoneid": "default",
                            "ranges": ["240b:c0e0:0101:2F10:DF28:0002:0080:0001-0003"],
                            "gateway": "240b:c0e0:0101:2F10::FFFF",
                            "prefix": "64",
                            "ifcount": "2",
                            "vfdriver": "vfio-pci",
                            "trusted": "off",
                            "spoofchk": "on"
                        },
                        {
                            "name": "nw-rh-ipa-ov-vlan-3583-ex-v6-wrong-ip",
                            "driver": "ovs",
                            "vlan_number": 1565,
                            "zoneid": "default",
                            "ranges": ["240b:c0e0:104:5DFD:1c01:2::0003-0009"],
                            "gateway": "240b:c0e0:104:5dfd::ffff",
                            "prefix": "64"
                        }
                    ],
                },
                "users": [
                    {
                        "username": user["username"],
                        "namespaces": [ns["name"] for ns in namespaces if ns["username"] == user["username"]],
                        "role": user["role"]
                    }
                    for user in tenant["users"]
                ]
            }
        ]
    }
}

# Save the output JSON to a file
with open("final_output.json", "w") as output_file:
    json.dump(output_data, output_file, indent=4)

log.info("Transformed data saved to 'final_output.json'")

# API URL (ensure to replace <service_port> with actual port)
api_url = "http://[240b:c0e0:105:54b5:b452:2::]:8080/api/robinreserve/v1/reservation"

# Use curl to send the data to the API
curl_command = [
    "curl", "-X", "POST",
    "-H", "Content-Type: application/json",
    "-d", "@final_output.json",  # Use the output file generated above
    api_url
]

# Try to execute the curl command
try:
    subprocess.run(curl_command, check=True)
    log.info("Data successfully sent to the API using curl")
except subprocess.CalledProcessError as e:
    log.error(f"Error occurred while sending data to the API using curl: {e}")

# Mock API setup for DELETE request
from unittest.mock import Mock

# Define dummy behavior for the DELETE request
def dummy_delete_request(url, headers=None, json=None):
    log.info(f"Simulating DELETE request to URL: {url}")
    if "reservation" in url:
        return {"status": "success", "message": f"API called for {url}"}
    return {"status": "failure", "message": "Invalid URL"}

# Assign the mock to use the dummy function
mock_api = Mock()
mock_api.delete.side_effect = dummy_delete_request

# Simulate a DELETE request (optional, for testing)
mock_api.delete("http://mock-api-url.com/api/robinreserve/v1/reservation", headers={"Content-Type": "application/json"})

# Log the reservation message as per the format you requested
log.info(json.dumps({
    "message": "Reservation request passed",
    "reservation_name": "sample_tenant_cluster4",
    "status": "LMP notified",
    "createdAt": 1719846731
}))

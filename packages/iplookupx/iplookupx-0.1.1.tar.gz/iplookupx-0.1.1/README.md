# iplookupx

`iplookupx` is a versatile Python package that provides three main capabilities:

1. Retrieve your public and local IP addresses, including IPv4 and IPv6, along with detailed geolocation and ISP metadata.
2. Make HTTP requests and retrieve HTML content using proxies, supporting both standard requests and Selenium-based browsing for dynamic content fetching.
3. Check whether a given proxy is working by making a simple HTTP request to a test URL.

---

## Features

- **IP Lookup:**
  - Fetch public IPv4 and IPv6 addresses from multiple reliable services.
  - Retrieve local network IP addresses.
  - Obtain rich metadata (country, city, ISP, ASN, etc.) for your public IPv4 using a free external API.
  
- **Proxy HTTP Requests:**
  - Make HTTP requests via proxy servers.
  - Supports Selenium-based requests for sites requiring JavaScript rendering.
  - Easily integrate proxy usage for both simple and dynamic web scraping.

- **Proxy Health Check:**
  - Verify if a proxy is working by sending a simple HTTP request to a test URL.
  - Helps ensure proxy reliability before use.

---

## Installation

```bash
pip install iplookupx



# ================================================================

from iplookupx import ip_verifier
# Checks whether the given proxy is working by making a simple HTTP request to a test URL.

# Define your proxy settings (this is just an example, use a valid proxy IP and port)
proxy = {
    "http": "http://proxy_ip:port",
    "https": "https://proxy_ip:port"
}

proxy = {
    "http": "http://10.10.1.10:3128",
    "https": "https://10.10.1.10:1080"
}

# Call the function with the proxy
is_working = ip_verifier(proxy)

# Print the result
if is_working:
    print("The proxy is working!")
else:
    print("The proxy is not working.")


# Define custom headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json'
}

# Call the function with custom headers
is_working = ip_verifier(proxy, headers=headers)

# Print the result
if is_working:
    print("The proxy is working!")
else:
    print("The proxy is not working.")


# Call the function with a custom timeout of 10 seconds
is_working = ip_verifier(proxy, timeout=10)

# Print the result
if is_working:
    print("The proxy is working!")
else:
    print("The proxy is not working.")


# Call the function with SSL verification disabled
is_working = ip_verifier(proxy, verify=False)

# Print the result
if is_working:
    print("The proxy is working!")
else:
    print("The proxy is not working.")

# Without Proxy (Direct Request for Public IP)
ip_verifier(proxy=None)

from iplookupx import ip_info
# To fetches IP details from IP address

ip_info(ip_address = "8.8.8.8")

{
  'query': '8.8.8.8',
  'status': 'success',
  'address': {
    'continent': '',
    'continent_code': '',
    'country': 'United States',
    'country_code': 'US',
    'region': 'VA',
    'region_name': 'Virginia',
    'city': 'Ashburn',
    'district': '',
    'postal': '20149',
    'latitude': 39.03,
    'longitude': -77.5
  },
  'timezone': 'America/New_York',
  'offset': '',
  'currency': '',
  'service_provider': {
    'isp': 'Google LLC',
    'organization': 'Google Public DNS',
    'as_numer': 'AS15169 Google LLC',
    'as_name': '',
    'mobile': '',
    'proxy': '',
    'hosting': ''
  }
}

from iplookupx import my_ip_info

ip_data = my_ip_info()

print("===== Public IP Information =====")
print(f"IPv4: {ip_data['public_ip']['ipv4']}")
print(f"IPv6: {ip_data['public_ip']['ipv6']}")
print("Metadata (Geolocation, ISP, etc.):")
for key, value in ip_data["public_ip"]["info"].items():
    print(f"  {key.capitalize()}: {value}")

print("\n===== Local IP Addresses =====")
print(f"Local IPv4: {ip_data['local_ip']['IPv4']}")
print(f"Local IPv6: {ip_data['local_ip']['IPv6']}")

===== Public IP Information =====
IPv4: 203.0.113.45
IPv6: 2001:0db8:85a3::8a2e:0370:7334
Metadata (Geolocation, ISP, etc.):
  Country: United States
  City: San Francisco
  Org: Example ISP
  As: AS12345 ExampleNet

===== Local IP Addresses =====
Local IPv4: 192.168.1.100
Local IPv6: fe80::1c2d:3eff:fe4e:88a



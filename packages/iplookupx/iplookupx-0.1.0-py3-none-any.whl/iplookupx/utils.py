# iplookupx/utils.py
import requests
import socket
import json
from typing import Optional, Dict

def ip_verifier(proxy: Optional[Dict[str, str]] = None, url: str = "http://httpbin.org/ip", timeout: int = 5, headers: Optional[Dict[str, str]] = None, verify: bool = True) -> bool:
    """
    Checks whether the given proxy is working by making a simple HTTP request to a test URL.
    If no proxy is provided, it fetches the public IP directly.

    Args:
        proxy (dict, optional): The proxy configuration (e.g., {"http": "http://proxy_ip:port", "https": "https://proxy_ip:port"}). Default is None.
        url (str): The URL to test the proxy against. Default is http://httpbin.org/ip.
        timeout (int): The timeout value for the request in seconds. Default is 5 seconds.
        headers (dict, optional): Custom headers to be sent with the request. Default is None, which sends a standard User-Agent.
        verify (bool, optional): Whether to verify SSL certificates. Default is True. Set to False if you want to skip SSL verification.

    Returns:
        bool: True if the proxy is working, False otherwise.
    """
    # If no proxy is provided, default to an empty dictionary
    if proxy is None:
        proxy = {}

    # If no custom headers are provided, use a default User-Agent header
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    try:
        # If no proxy is given, get the public IP directly
        if not proxy:
            print(url)
            response = requests.get(url, headers=headers, timeout=timeout, verify=verify)
        else:
            # Sending a GET request to the test URL using the proxy, custom headers, timeout, and SSL verification
            response = requests.get(url, proxies=proxy, headers=headers, timeout=timeout, verify=verify)
        
        # If the status code is 200, the proxy is working or we got the IP
        if response.status_code == 200:
            if not proxy:
                # If no proxy, just print and return the public IP
                public_ip = response.json().get("origin", "Unknown")
                print(f"Public IP is used: {public_ip}")
                return True
            else:
                # If proxy was used, print success
                print(f"Proxy {proxy} is working!")
                return True
        else:
            print(f"Failed with status code {response.status_code}")
            return False    

    except requests.exceptions.ConnectTimeout:
        print(f"Error: timeout")
        return False

    except requests.exceptions.ConnectionError:
        print(f"Error: check net connections")
        return False

    except requests.exceptions.SSLError:
        print(f"Error: certificate verify failed (SSL)")
        return False

    except requests.exceptions.JSONDecodeError:
        print(f"Error: decoding JSON")
        return False

    except requests.exceptions.ReadTimeout:
        print(f"Error: ReadTimeout")
        return False        

    except Exception as error:
        print(error)
        return False 

def ip_details(ip_address: str) -> Optional[Dict[str, str]]:
    """
    Fetches IP details from ip-api.com.

    Args:
    - ip: IP address to fetch details for.

    Returns:
    - A dictionary with details like 'IP', 'City', 'Region', 'Country', 'Location', and 'ISP/Org'.
    - Returns None if there's an error or no data is available.
    """
    url = f"http://ip-api.com/json/{ip_address}"
    try:
        response = requests.get(url)
        json_data = response.json()
        status = json_data.get("status","")
        if response.status_code == 200 and status =="success":
            data_dict = dict()
            query = json_data.get("query","")

            # ================Address==================
            continent = json_data.get("continent","")
            continent_code = json_data.get("continentCode","")
            country = json_data.get("country","")
            country_code = json_data.get("countryCode","")
            region = json_data.get("region","")
            region_name = json_data.get("regionName","")
            city = json_data.get("city","")
            district = json_data.get("district","")
            postal = json_data.get("zip","")
            latitude = json_data.get("lat","")
            longitude = json_data.get("lon","")
            address = {"continent":continent,"continent_code":continent_code,"country":country,"country_code":country_code,"region":region,"region_name":region_name,"city":city,"district":district,"postal":postal,"latitude":latitude,"longitude":longitude}

            # ================Service Provider==================
            isp = json_data.get("isp","")
            organization = json_data.get("org","")
            as_numer = json_data.get("as","")
            as_name = json_data.get("asname","")
            mobile = json_data.get("mobile","")
            proxy = json_data.get("proxy","")
            hosting = json_data.get("hosting","")
            service_provider = {"isp":isp,"organization":organization,"as_numer":as_numer,"as_name":as_name,"mobile":mobile,"proxy":proxy,"hosting":hosting}

            timezone = json_data.get("timezone","")
            offset = json_data.get("offset","")
            currency = json_data.get("currency","")

            # =================Return data====================
            data_dict["query"] = query
            data_dict["status"] = status
            data_dict["address"] = address
            data_dict["timezone"] = timezone
            data_dict["offset"] = offset
            data_dict["currency"] = currency
            data_dict["service_provider"] = service_provider
            return data_dict
        else:
            return json_data

    except Exception as error:
        return {"query":ip_address, "status":error}        

def try_services(version: str) -> str | None:
    """
    Tries a list of public IP services for the specified IP version and returns the IP address.

    Args:
        version (str): Either 'IPv4' or 'IPv6'.

    Returns:
        str | None: The public IP address as a string, or None if all services fail.
    """

    # Dictionary of public IP lookup services for both IPv4 and IPv6
    service_urls: dict[str, list[str]] = {
        "IPv4": [
            "https://checkip.amazonaws.com",
            "https://api.ipify.org?format=json",
            "https://ipv4.icanhazip.com",
            "https://v4.ident.me",
            "https://ifconfig.me/ip"
        ],
        "IPv6": [
            "https://ifconfig.co/ip",
            "https://api64.ipify.org?format=json",
            "https://ipv6.icanhazip.com",
            "https://v6.ident.me",
            "https://ifconfig.me/ip"
        ]
    }
    for url in service_urls[version]:
        try:
            headers = {"User-Agent": "curl"}  # Some services block requests without a user agent
            response = requests.get(url, timeout=5, headers=headers)
            if response.ok:
                if "json" in url:
                    return response.json().get("ip")
                return response.text.strip()
        except Exception:
            continue  # Silently ignore and try next service
    return None

def get_public_ip(version_name: str | None = None) -> dict[str, str | None]:
    """
    Gets the public IPv4 and/or IPv6 addresses.

    Args:
        version_name (str | None): If 'IPv4' or 'IPv6', only retrieves that version; if None, retrieves both.

    Returns:
        dict[str, str | None]: Dictionary with keys 'IPv4' and/or 'IPv6' mapping to public IPs.
    """
    results: dict[str, str | None] = {}
    if version_name is None:
        results["IPv4"] = try_services("IPv4")
        results["IPv6"] = try_services("IPv6")
    elif version_name in ("IPv4", "IPv6"):
        results[version_name] = try_services(version_name)
    return results

def get_local_ips() -> dict[str, str | None]:
    """
    Retrieves local network IPv4 and IPv6 addresses of the host machine.

    Returns:
        dict[str, str | None]: Dictionary with local 'IPv4' and 'IPv6' addresses.
    """
    local_ips: dict[str, str | None] = {"IPv4": None, "IPv6": None}
    try:
        addr_info = socket.getaddrinfo(socket.gethostname(), None)
        for info in addr_info:
            family, _, _, _, sockaddr = info
            if family == socket.AF_INET and not local_ips["IPv4"]:
                local_ips["IPv4"] = sockaddr[0]
            elif family == socket.AF_INET6 and not local_ips["IPv6"]:
                ip = sockaddr[0]
                if not ip.startswith("fe80"):  # Skip link-local addresses
                    local_ips["IPv6"] = ip
    except Exception:
        pass  # Ignore errors and return what we have
    return local_ips

def get_ip_info() -> dict[str, dict]:
    """
    Combines public and local IP information, along with geolocation or metadata for the public IPv4.

    Returns:
        dict[str, dict]: A structured dictionary containing local and public IPs and their details.
    """
    public_ip_data = get_public_ip()
    ipv4 = public_ip_data.get("IPv4", "")
    ipv6 = public_ip_data.get("IPv6", "")
    ip_info = ip_details(ipv4) if ipv4 else {}

    # Remove unwanted keys from external API response
    ip_info.pop("query", None)
    ip_info.pop("status", None)

    final_data: dict[str, dict] = {
        "public_ip": {
            "ipv4": ipv4,
            "ipv6": ipv6,
            "info": ip_info
        },
        "local_ip": get_local_ips()
    }
    return final_data   
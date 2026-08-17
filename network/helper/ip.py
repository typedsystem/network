def _is_ipv4(entity: str) -> bool:
    try:
        from ipaddress import IPv4Address
        IPv4Address(entity)
        return True
    except:
        return False

def _is_ipv6(entity: str) -> bool:
    try:
        from ipaddress import IPv6Address
        IPv6Address(entity)
        return True
    except:
        return False

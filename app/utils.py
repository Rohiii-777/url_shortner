import string
import random
import ipaddress
from urllib.parse import urlparse

BASE62 = string.ascii_letters + string.digits
CODE_LENGTH = 6


def generate_short_code() -> str:
    return "".join(random.choices(BASE62, k=CODE_LENGTH))


def is_safe_url(url: str) -> bool:
    try:
        parsed = urlparse(url)

        # scheme check
        if parsed.scheme not in ("http", "https"):
            return False

        # block userinfo abuse: user@host
        if parsed.username or parsed.password:
            return False

        host = parsed.hostname
        if not host:
            return False

        # If host is an IP, validate it's public
        try:
            ip = ipaddress.ip_address(host)
            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_reserved
                or ip.is_multicast
            ):
                return False
        except ValueError:
            # Not an IP → hostname
            pass

        return True
    except Exception:
        return False

import dns.resolver
import requests
from dns.exception import Timeout as DnsTimeout
from pythonping import ping
from scapy.all import sr1
from scapy.layers.inet import ICMP, IP, UDP

from daydream.plugins import Plugin
from daydream.plugins.mixins import McpServerMixin, tool


class NetworkingPlugin(Plugin, McpServerMixin):
    """A plugin for providing common networking tools."""

    @tool()
    def ping(self, host: str) -> str:
        """Ping a host and return the result."""
        return repr(ping(host, count=4, timeout=5))

    @tool()
    def dig(self, hostname: str, record_type: str = "A") -> str:
        """Use the 'dig' command to resolve a hostname and return the result."""
        result = ""
        try:
            resolver = dns.resolver.Resolver()
            answers = resolver.resolve(hostname, record_type)
            for rdata in answers:
                result += str(rdata) + "\n"
        except dns.resolver.NXDOMAIN:
            result = f"Host '{hostname}' not found."
        except dns.resolver.NoAnswer:
            result = f"No record found for '{hostname}' with type '{record_type}'."
        except DnsTimeout:
            result = "Timeout while querying DNS server."

        return result

    @tool()
    def traceroute(self, destination: str, max_hops: int = 30) -> str:
        """Trace the route to a destination and return the result."""
        result = ""
        for ttl in range(1, max_hops + 1):
            packet = IP(dst=destination, ttl=ttl) / UDP(dport=33434)
            reply = sr1(packet, verbose=0, timeout=1)
            if reply is None:
                result += f"{ttl}\t* * * Request timed out.\n"
            elif reply.haslayer(ICMP) and reply[ICMP].type == 11:
                result += f"{ttl}\t{reply.src}\n"
            elif reply.haslayer(ICMP) and reply[ICMP].type == 3:
                result += f"{ttl}\t{reply.src} Destination reached.\n"
                break
            else:
                result += f"{ttl}\t{reply.src} Other reply type.\n"

        return result

    @tool()
    def request_url(self, url: str) -> str:
        """Request a URL with the GET method and return the result."""
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text

#!/usr/bin/env python3
"""NetCalc: an ipcalc-style subnet calculator.

Usage:
    python3 subnet_calc.py 192.168.1.26 /24
    python3 subnet_calc.py 192.168.1.26 24
    python3 subnet_calc.py 192.168.1.26 255.255.255.0
    python3 subnet_calc.py 192.168.1.26/24
    python3 subnet_calc.py --bits 192.168.1.26 /26
"""

import argparse
import ipaddress
import sys


def normalize_mask(token):
    token = token.strip().lstrip("/")
    if token.isdigit():
        prefix = int(token)
        if not 0 <= prefix <= 32:
            raise ValueError(f"prefix /{prefix} must be between 0 and 32")
    return token


def build_network(ip, mask):
    if mask is None:
        if "/" not in ip:
            raise ValueError("give a mask: /24, 24, or 255.255.255.0")
        value = ip
    else:
        value = f"{ip}/{normalize_mask(mask)}"
    return ipaddress.ip_network(value, strict=False)


def analyze(net):
    prefix = net.prefixlen
    total = net.num_addresses
    nw = net.network_address
    bc = net.broadcast_address
    mask = net.netmask

    if prefix >= 31:
        host_min, host_max = nw, bc
        usable = total
    else:
        host_min, host_max = nw + 1, bc - 1
        usable = total - 2

    nxt = nw + total
    if nxt <= ipaddress.IPv4Address("255.255.255.255"):
        next_net = str(nxt)
    else:
        next_net = "beyond IPv4 space"

    return [
        ("Network", str(nw)),
        ("Netmask", str(mask)),
        ("CIDR", f"/{prefix}"),
        ("Broadcast", str(bc)),
        ("HostMin", str(host_min)),
        ("HostMax", str(host_max)),
        ("Hosts/Net", str(usable)),
        ("Total IPs", str(total)),
        ("Next network", next_net),
    ]


def show_bits(net, ip):
    addr = int(ip)
    mask = int(net.netmask)
    print(f"{'IP':<9} = {addr:032b}")
    print(f"{'MASK':<9} = {mask:032b}")
    print(f"{'NETWORK':<9} = {addr & mask:032b}")


def main():
    parser = argparse.ArgumentParser(
        prog="subnet_calc.py",
        description="Compute network, broadcast, host range and more from an IP and mask.",
    )
    parser.add_argument("ip", help="IPv4 address (e.g. 192.168.1.26)")
    parser.add_argument("mask", nargs="?", default=None,
                        help="prefix (/24), integer (24), or dotted mask (255.255.255.0)")
    parser.add_argument("--bits", action="store_true", help="show binary IP AND mask")
    args = parser.parse_args()

    try:
        ip_obj = ipaddress.ip_address(args.ip.split("/")[0])
        net = build_network(args.ip, args.mask)
    except ValueError as exc:
        parser.error(str(exc))

    rows = analyze(net)
    width = max(len(key) for key, _ in rows)
    for key, value in rows:
        print(f"{key:<{width}} = {value}")

    if args.bits:
        print()
        show_bits(net, ip_obj)


if __name__ == "__main__":
    main()
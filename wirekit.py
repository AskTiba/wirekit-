#!/usr/bin/env python3
"""wirekit: an ipcalc-style subnet calculator.

Usage:
    python3 wirekit.py 192.168.1.26 /24
    python3 wirekit.py 192.168.1.26 24
    python3 wirekit.py 192.168.1.26 255.255.255.0
    python3 wirekit.py 192.168.1.26/24
    python3 wirekit.py --bits 192.168.1.26 /26
"""

import argparse
import ipaddress
import json
import random


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

    nxt = int(nw) + total
    if nxt <= 0xFFFFFFFF:
        next_net = str(ipaddress.IPv4Address(nxt))
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


_QUIZ_PREFIXES = (8, 16, 20, 22, 24, 25, 26, 27, 28, 29, 30, 31, 32)


def make_quiz_question(rng=random):
    prefix = rng.choice(_QUIZ_PREFIXES)
    ip = ipaddress.IPv4Address(rng.getrandbits(32))
    net = ipaddress.ip_network(f"{ip}/{prefix}", strict=False)
    nw = net.network_address
    bc = net.broadcast_address
    if prefix >= 31:
        first, last = nw, bc
        usable = net.num_addresses
    else:
        first, last = nw + 1, bc - 1
        usable = net.num_addresses - 2

    choices = [
        (f"What is the network address of {ip}/{prefix}?", str(nw)),
        (f"What is the broadcast address of {ip}/{prefix}?", str(bc)),
        (f"How many usable hosts are in {ip}/{prefix}?", str(usable)),
    ]
    if prefix < 31:
        choices.append((f"What is the first usable host in {ip}/{prefix}?", str(first)))
        choices.append((f"What is the last usable host in {ip}/{prefix}?", str(last)))
    return rng.choice(choices)


def _clean(text):
    return text.strip().replace(" ", "").replace(",", "")


def run_quiz():
    print("wirekit quiz — answer each question, or type 'q' to quit.")
    asked = correct = 0
    while True:
        question, answer = make_quiz_question()
        print()
        print(f"Q: {question}")
        try:
            reply = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if reply.strip().lower() in ("q", "quit", "exit"):
            break
        asked += 1
        if _clean(reply) == _clean(answer):
            correct += 1
            print("Correct!")
        else:
            print(f"Not quite — {answer}")
    if asked:
        print(f"\nScore: {correct}/{asked}")
    print("Keep practicing!")


def main():
    parser = argparse.ArgumentParser(
        prog="wirekit",
        description=(
            "Compute network, broadcast, host range and more from an IP and mask."
        ),
    )
    parser.add_argument(
        "ip", nargs="?", default=None, help="IPv4 address (e.g. 192.168.1.26)"
    )
    parser.add_argument(
        "mask",
        nargs="?",
        default=None,
        help="prefix (/24), integer (24), or dotted mask (255.255.255.0)",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--bits", action="store_true", help="show binary IP AND mask")
    mode.add_argument(
        "--json", action="store_true", help="machine-readable JSON output"
    )
    mode.add_argument(
        "--quiz", action="store_true", help="interactive subnetting practice"
    )
    args = parser.parse_args()

    if args.quiz:
        run_quiz()
        return

    if args.ip is None:
        parser.error("give an IPv4 address, e.g. 192.168.1.26 /24")

    try:
        ip_obj = ipaddress.ip_address(args.ip.split("/")[0])
        net = build_network(args.ip, args.mask)
    except ValueError as exc:
        parser.error(str(exc))

    rows = analyze(net)
    if args.json:
        print(json.dumps(dict(rows)))
        return
    width = max(len(key) for key, _ in rows)
    for key, value in rows:
        print(f"{key:<{width}} = {value}")

    if args.bits:
        print()
        show_bits(net, ip_obj)


if __name__ == "__main__":
    main()  # pragma: no cover

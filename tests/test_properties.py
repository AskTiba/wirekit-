"""Property-based tests for wirekit subnet math (hypothesis).

Unlike the example tests in test_wirekit.py, these assert invariants that must
hold for EVERY IPv4 address and prefix — hypothesis generates thousands of
random cases, including edge space (0.0.0.0/0, 255.255.255.255/32).
"""

import ipaddress

from hypothesis import given
from hypothesis import strategies as st

import wirekit

addrs = st.integers(min_value=0, max_value=0xFFFFFFFF).map(ipaddress.IPv4Address)
prefixes = st.integers(min_value=0, max_value=32)


@given(addrs, prefixes)
def test_network_is_prefix_aligned_and_contains_ip(ip, prefix):
    net = wirekit.build_network(str(ip), str(prefix))
    total = net.num_addresses
    nw = int(net.network_address)
    assert nw % total == 0
    assert nw <= int(ip) <= int(net.broadcast_address)


@given(addrs, prefixes)
def test_broadcast_is_last_address_of_block(ip, prefix):
    net = wirekit.build_network(str(ip), str(prefix))
    expected = int(net.network_address) + net.num_addresses - 1
    assert int(net.broadcast_address) == expected


@given(addrs, prefixes)
def test_analyze_rows_are_internally_consistent(ip, prefix):
    net = wirekit.build_network(str(ip), str(prefix))
    rows = dict(wirekit.analyze(net))

    total = net.num_addresses
    nw = int(net.network_address)
    bc = int(net.broadcast_address)
    host_min = int(ipaddress.ip_address(rows["HostMin"]))
    host_max = int(ipaddress.ip_address(rows["HostMax"]))

    assert nw <= host_min <= host_max <= bc
    assert rows["Total IPs"] == str(total)
    assert rows["CIDR"] == f"/{prefix}"
    assert rows["Network"] == str(net.network_address)
    assert rows["Netmask"] == str(net.netmask)
    assert rows["Broadcast"] == str(net.broadcast_address)

    expected_usable = total if prefix >= 31 else total - 2
    assert rows["Hosts/Net"] == str(expected_usable)
    if prefix < 31:
        assert host_min == nw + 1
        assert host_max == bc - 1
    else:
        assert host_min == nw
        assert host_max == bc


@given(addrs, prefixes)
def test_next_network_is_one_block_past_or_beyond_space(ip, prefix):
    net = wirekit.build_network(str(ip), str(prefix))
    rows = dict(wirekit.analyze(net))
    nxt = int(net.network_address) + net.num_addresses
    if nxt <= 0xFFFFFFFF:
        assert rows["Next network"] == str(ipaddress.IPv4Address(nxt))
    else:
        assert rows["Next network"] == "beyond IPv4 space"


@given(addrs, prefixes)
def test_all_mask_forms_build_the_same_network(ip, prefix):
    net = wirekit.build_network(str(ip), str(prefix))
    assert wirekit.build_network(f"{ip}/{prefix}", None) == net
    assert wirekit.build_network(str(ip), f"/{prefix}") == net
    assert wirekit.build_network(str(ip), str(net.netmask)) == net

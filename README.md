# wirekit

An `ipcalc`-style subnet calculator that turns any IPv4 address and mask into the network, broadcast, host range, and more — in a single command.

## Description

`wirekit` is a command-line tool that computes everything about an IPv4 subnet from one address and one mask. It accepts the mask as CIDR (`/24`), a bare prefix (`24`), or a dotted-decimal subnet mask (`255.255.255.0`), and it handles the awkward edge cases — `/31`, `/32`, and host addresses passed inside a larger network.

## Show, Don't Tell

<!-- TODO: optional hero screenshot of a terminal running `net` (dark theme). -->
<!-- ![wirekit in the terminal](docs/hero.png) -->

```console
$ net 172.30.197.206 /20
Network      = 172.30.192.0
Netmask      = 255.255.240.0
CIDR         = /20
Broadcast    = 172.30.207.255
HostMin      = 172.30.192.1
HostMax      = 172.30.207.254
Hosts/Net    = 4094
Total IPs    = 4096
Next network = 172.30.208.0
```

## Motivation

Subnetting is the kind of skill you only really learn by checking your work — do a problem by hand, then confirm you got the network, broadcast, and host range right. Existing calculators either force a strict CIDR-only syntax or give you a wall of numbers with no context.

I built `wirekit` to be the answer key I kept reaching for: it takes the mask exactly the way you'd type it in the real world (from `ipconfig`, a router page, or a CIDR block), it reports exactly the values you're practicing, and its `--bits` mode shows the underlying **IP AND mask** operation so you can see *why* the network ID is what it is.

## Quick Start

```bash
git clone https://github.com/AskTiba/wirekit-.git wirekit
cd wirekit
chmod +x install.sh
./install.sh
source ~/.bashrc        # or: source ~/.zshrc
net 192.168.1.245/24
```

## Usage

The mask can be written three ways, and all three are equivalent:

```console
$ net 192.168.1.26 /24
$ net 192.168.1.26 24
$ net 192.168.1.26 255.255.255.192
```

The mask can also be glued to the address:

```console
$ net 10.0.3.77/21
```

Add `--bits` to see the binary `IP AND MASK` that produces the network ID — the teaching mode:

```console
$ net --bits 192.168.1.26 /26
Network      = 192.168.1.0
Netmask      = 255.255.255.192
CIDR         = /26
Broadcast    = 192.168.1.63
HostMin      = 192.168.1.1
HostMax      = 192.168.1.62
Hosts/Net    = 62
Total IPs    = 64
Next network = 192.168.1.64

IP        = 11000000101010000000000100011010
MASK      = 11111111111111111111111111000000
NETWORK   = 11000000101010000000000100000000
```

### Output reference

| Field | Meaning |
|---|---|
| `Network` | Network ID (the `IP AND mask`) |
| `Netmask` | Dotted-decimal subnet mask |
| `CIDR` | Prefix length, e.g. `/20` |
| `Broadcast` | Broadcast address |
| `HostMin` / `HostMax` | First and last usable host addresses |
| `Hosts/Net` | Number of usable host addresses |
| `Total IPs` | Total addresses in the block (`2^host_bits`) |
| `Next network` | The first address of the next equal-sized block |

### Edge cases handled

| Input | Behavior |
|---|---|
| `/31` | 2 usable hosts (RFC 3021 point-to-point); `HostMin`/`HostMax` are both addresses |
| `/32` | 1 usable host (the address itself) |
| Host address in a larger block (`172.30.197.206 /20`) | Normalized to its network (`172.30.192.0/20`) |
| Prefix out of range (`/33`) | Clear error message, no traceback |
| Invalid address (`999.1.1.1`) | Clear error message, no traceback |
| Missing mask | Usage hint telling you the accepted formats |

## Installing on another machine

The `install.sh` script is cross-shell: it copies the script to `~/.local/bin`, makes it executable, and adds the `net` alias to `~/.zshrc` or `~/.bashrc` (whichever your shell uses). Transfer the folder (`git clone`, `scp`, or a USB stick), then:

```bash
chmod +x install.sh && ./install.sh
source ~/.bashrc
```

## Contributing

### Clone the repo

```bash
git clone https://github.com/AskTiba/wirekit-.git wirekit && cd wirekit
```

### Run it without installing

```bash
python3 subnet_calc.py 192.168.1.26 /24
```

### Submit a pull request

Fork → create a branch → open a PR against `main`.

## Roadmap

- `pytest` suite covering `/8`, `/24`, `/30`, `/31`, `/32`, and invalid input
- `--quiz` mode to generate random subnetting problems and check your answers
- Optional JSON output for scripting

## License

_No license has been added yet — add one (e.g. MIT) if you want others to reuse this._

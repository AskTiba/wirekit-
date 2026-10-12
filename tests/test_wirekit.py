import pathlib
import random
import subprocess
import sys

import pytest

import wirekit

ROOT = pathlib.Path(__file__).resolve().parent.parent


def analyze(ip_mask):
    if " " in ip_mask:
        ip, mask = ip_mask.split()
    else:
        ip, mask = ip_mask, None
    net = wirekit.build_network(ip, mask)
    return dict(wirekit.analyze(net))


def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(ROOT / "wirekit.py"), *args],
        capture_output=True,
        text=True,
    )


def test_slash8():
    info = analyze("10.0.0.1 /8")
    assert info["Network"] == "10.0.0.0"
    assert info["CIDR"] == "/8"
    assert info["Broadcast"] == "10.255.255.255"
    assert info["HostMin"] == "10.0.0.1"
    assert info["HostMax"] == "10.255.255.254"
    assert info["Hosts/Net"] == "16777214"
    assert info["Total IPs"] == "16777216"
    assert info["Next network"] == "11.0.0.0"


def test_slash24():
    info = analyze("192.168.1.245 /24")
    assert info["Network"] == "192.168.1.0"
    assert info["Netmask"] == "255.255.255.0"
    assert info["Broadcast"] == "192.168.1.255"
    assert info["HostMin"] == "192.168.1.1"
    assert info["HostMax"] == "192.168.1.254"
    assert info["Hosts/Net"] == "254"
    assert info["Total IPs"] == "256"
    assert info["Next network"] == "192.168.2.0"


def test_slash30():
    info = analyze("192.168.1.0 /30")
    assert info["Network"] == "192.168.1.0"
    assert info["Broadcast"] == "192.168.1.3"
    assert info["HostMin"] == "192.168.1.1"
    assert info["HostMax"] == "192.168.1.2"
    assert info["Hosts/Net"] == "2"
    assert info["Total IPs"] == "4"


def test_slash31_point_to_point():
    info = analyze("192.168.1.0 /31")
    assert info["HostMin"] == "192.168.1.0"
    assert info["HostMax"] == "192.168.1.1"
    assert info["Hosts/Net"] == "2"
    assert info["Total IPs"] == "2"


def test_slash32_single_host():
    info = analyze("192.168.1.7 /32")
    assert info["Network"] == "192.168.1.7"
    assert info["Broadcast"] == "192.168.1.7"
    assert info["HostMin"] == "192.168.1.7"
    assert info["HostMax"] == "192.168.1.7"
    assert info["Hosts/Net"] == "1"
    assert info["Total IPs"] == "1"


def test_host_address_is_normalized():
    info = analyze("172.30.197.206 /20")
    assert info["Network"] == "172.30.192.0"
    assert info["CIDR"] == "/20"
    assert info["Netmask"] == "255.255.240.0"
    assert info["Broadcast"] == "172.30.207.255"


def test_next_network_beyond_ipv4():
    info = analyze("255.255.255.0 /24")
    assert info["Next network"] == "beyond IPv4 space"


@pytest.mark.parametrize("mask", ["/26", "26", "255.255.255.192"])
def test_mask_formats_are_equivalent(mask):
    info = analyze(f"192.168.1.26 {mask}")
    assert info["CIDR"] == "/26"
    assert info["Network"] == "192.168.1.0"
    assert info["Hosts/Net"] == "62"


def test_glued_cidr_form():
    info = analyze("10.0.3.77/21")
    assert info["Network"] == "10.0.0.0"
    assert info["CIDR"] == "/21"


def test_normalize_mask_accepts_forms():
    assert wirekit.normalize_mask("/24") == "24"
    assert wirekit.normalize_mask("24") == "24"
    assert wirekit.normalize_mask("  /30 ") == "30"


def test_normalize_mask_rejects_out_of_range():
    with pytest.raises(ValueError):
        wirekit.normalize_mask("33")


def test_build_network_requires_mask():
    with pytest.raises(ValueError):
        wirekit.build_network("192.168.1.1", None)


def test_cli_runs_clean():
    result = run_cli("192.168.1.26", "/24")
    assert result.returncode == 0
    assert "192.168.1.0" in result.stdout
    assert "Broadcast" in result.stdout


def test_cli_bits_mode():
    result = run_cli("--bits", "192.168.1.26", "/26")
    assert result.returncode == 0
    assert "11000000101010000000000100011010" in result.stdout
    assert "11111111111111111111111111000000" in result.stdout


def test_cli_invalid_ip_fails():
    result = run_cli("999.1.1.1", "/24")
    assert result.returncode == 2
    assert "error" in result.stderr.lower()


def test_cli_invalid_prefix_fails():
    result = run_cli("192.168.1.1", "/33")
    assert result.returncode == 2
    assert "between 0 and 32" in result.stderr


def test_cli_missing_mask_fails():
    result = run_cli("192.168.1.1")
    assert result.returncode == 2
    assert "mask" in result.stderr.lower()


def test_cli_no_args_fails():
    result = run_cli()
    assert result.returncode == 2
    assert "ipv4 address" in result.stderr.lower()


def test_clean_normalizes_answers():
    assert wirekit._clean(" 1.1.1.1 ") == "1.1.1.1"
    assert wirekit._clean("1,024") == "1024"


def test_quiz_question_is_well_formed():
    rng = random.Random(0)
    for _ in range(100):
        question, answer = wirekit.make_quiz_question(rng)
        assert isinstance(question, str) and question
        assert isinstance(answer, str) and answer


def test_run_quiz_scores_answers(monkeypatch, capsys):
    questions = iter(
        [
            ("What is the network address?", "10.0.0.0"),
            ("How many usable hosts?", "254"),
            ("unused", "unused"),
        ]
    )
    replies = iter(["10.0.0.0", "nope", "q"])
    monkeypatch.setattr(wirekit, "make_quiz_question", lambda: next(questions))
    monkeypatch.setattr("builtins.input", lambda *a: next(replies))

    wirekit.run_quiz()

    out = capsys.readouterr().out
    assert "Correct!" in out
    assert "Not quite" in out
    assert "Score: 1/2" in out

import typing as t
import logging
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from ipaddress import IPv4Address

import fscm
from jinja2 import Template
from fscm import p, run, remote
from fscm.modules import systemd


logger = logging.getLogger(__name__)


@dataclass
class Peer:
    name: str
    ip: IPv4Address
    pubkey: str
    endpoint: str
    a: t.Optional[t.Union[str, list, tuple]] = None
    dns: t.Optional[str] = None


@dataclass
class Server:
    name: str
    cidr: str
    port: int
    pubkey: str
    interfaces: t.List[str]
    host: str
    public_endpoint: str
    external_peers: t.Dict[str, str]

    # If False, ensure that INPUT traffic to the server is blocked. This is useful
    # when you have untrusted peers on the network.
    allow_traffic_to_server: bool = False

    @classmethod
    def from_dict(cls, name, d):
        return cls(
            name,
            cidr=d["cidr"],
            port=int(d["port"]),
            pubkey=d["pubkey"],
            interfaces=d["interfaces"],
            host=d["host"],
            public_endpoint=d["public_endpoint"],
            external_peers=d.get("external_peers", {}),
            allow_traffic_to_server=d.get("allow_traffic_to_server"),
        )

    @property
    def external_peers_objs(self) -> dict[str, Peer]:
        peers = {}

        for name, pk_and_ip in self.external_peers.items():
            if not pk_and_ip:
                continue
            pubkey, ip = [i.strip() for i in pk_and_ip.split(',')]
            peers[name] = Peer(name, IPv4Address(ip), pubkey, self.public_endpoint)

        return peers


class WireguardHostType(t.Protocol):
    wireguards: t.Dict[str, Peer]
    name: str


class Host(remote.Host):
    """A mixin that adds the .wireguard attribute to a Host."""

    def __init__(
        self,
        *args,
        wgs: t.Optional[t.Dict[str, Peer]] = None,
        **kwargs,
    ):
        kwargs.setdefault("ssh_hostname", args[0] + ".lan")
        super().__init__(*args, **kwargs)
        self.wireguards = wgs or {}

    @classmethod
    def from_dict(cls, name, d):
        wgd = d.pop("wireguard", {})
        instance = super().from_dict(name, d)
        wgs = {}

        for wgname, netd in wgd.items():
            wgs[wgname] = Peer(wgname, **netd)

        instance.wireguards = wgs
        return instance


def _wg_server_config(wg: Server, hosts: t.List[WireguardHostType]) -> str:
    hosts = [h for h in hosts if wg.name in h.wireguards]

    input_rule = "iptables -I INPUT 1 -i %i -j DROP"
    input_rule_d = "iptables -D INPUT -i %i -j DROP"

    if wg.allow_traffic_to_server:
        input_rule = "iptables -I INPUT 1 -i %i -j ACCEPT"
        input_rule_d = "iptables -D INPUT -i %i -j ACCEPT"

    conf = dedent(
        f"""
    [Interface]
    Address = {wg.cidr}
    ListenPort = {wg.port}

    PostUp = wg set %i private-key /etc/wireguard/{wg.name}-privkey
    PreUp = sysctl -w net.ipv4.ip_forward=1

    # Scripts to run when interface comes up/down
    PostUp = /etc/wireguard/{wg.name}-updown.sh up
    PostDown = /etc/wireguard/{wg.name}-updown.sh down

    # PostUp = {input_rule}
    # PostDown = {input_rule_d}

    # # Allow incoming wireguard connections over all interfaces.
    # PostUp = iptables -I INPUT 1 -p udp -m udp --dport {wg.port} -j ACCEPT
    # PostDown = iptables -D INPUT -p udp -m udp --dport {wg.port} -j ACCEPT

    # # Allow DNS access to wireguard server.
    # PostUp = iptables -I INPUT 1 -i %i -p udp --dport 53 -j ACCEPT
    # PostDown = iptables -D INPUT -i %i -p udp --dport 53 -j ACCEPT

    # PostUp = iptables -I FORWARD 1 -i %i -j ACCEPT
    # PostDown = iptables -D FORWARD -i %i -j ACCEPT

    # PostUp = iptables -I FORWARD 1 -o %i -j ACCEPT
    # PostDown = iptables -D FORWARD -o %i -j ACCEPT
    """
    ).lstrip()

    for host in hosts:
        hwg = host.wireguards[wg.name]

        if not hwg.pubkey:
            continue

        conf += dedent(
            f"""

            [Peer]
            # {host.name}
            PublicKey = {hwg.pubkey}
            AllowedIPs = {hwg.ip}/32
            """
        )

    for name, val in wg.external_peers.items():
        [pubkey, ip] = [i.strip() for i in val.split(",")]
        if ip.endswith("/32"):
            ip = ip.rstrip("/32")

        conf += dedent(
            f"""
            [Peer]
            # {name} (external)
            PublicKey = {pubkey}
            AllowedIPs = {ip}/32
            """
        )

    return conf


def server(
    host: remote.Host, wg: Server, hosts: t.List[WireguardHostType]
):
    fscm.s.pkgs_install("wireguard-tools")

    if not wg.pubkey:
        pubkey = make_privkey(wg.name)
        print(f"Pubkey for {host}, {wg} is {pubkey}")

    updown_sh_tmpl = Template(UPDOWN_TMPL)
    updown_sh = updown_sh_tmpl.render(wg=wg)

    changed = (
        p(f"/etc/wireguard/{wg.name}-updown.sh", sudo=True)
        .contents(updown_sh)
        .chmod(755)
        .make_executable(sudo=True)
        .changes
    )

    changed = (
        p(f"/etc/wireguard/{wg.name}.conf", sudo=True)
        .contents(_wg_server_config(wg, hosts))
        .changes
    ) or changed

    systemd.enable_service(f"wg-quick@{wg.name}", restart=bool(changed), sudo=True)


def peer(host: WireguardHostType, wgs: dict[str, Server]):
    fscm.s.pkgs_install("wireguard-tools")

    for wg in host.wireguards.values():
        if not wg.pubkey:
            pubkey = make_privkey(wg.name)
            if not pubkey:
                logger.warn(f"privkey for {host}, {wg} already exists - using that")
                pubkey = (
                    run(
                        f"cat /etc/wireguard/{wg.name}-privkey | wg pubkey",
                        sudo=True,
                        quiet=True,
                    )
                    .assert_ok()
                    .stdout
                )

            assert pubkey
            logger.info(f"setting pubkey for {wg}:\n\n{pubkey}")
            wg.pubkey = pubkey

        server = wgs[wg.name]
        changed = bool(
            p(f"/etc/wireguard/{wg.name}.conf", sudo=True)
            .contents(peer_config(server, wg))
            .changes
        )

        systemd.enable_service(f"wg-quick@{wg.name}", restart=changed, sudo=True)


def peer_config(wgs: Server, wg: Peer) -> str:
    first_host = wgs.cidr.split("/")[0]
    if not wgs.pubkey:
        raise ValueError("wireguard server must have a pubkey assigned")

    return dedent(
        f"""
        [Interface]
        Address = {wg.ip}/32
        PostUp = wg set %i private-key /etc/wireguard/{wgs.name}-privkey
        PostUp = sleep 0.5; nc -nvuz {first_host} {wgs.port}
        {f'# DNS = {wg.dns}' if wg.dns else ''}

        [Peer]
        PublicKey = {wgs.pubkey}
        AllowedIPs = {wgs.cidr}
        Endpoint = {wg.endpoint}:{wgs.port}
        PersistentKeepalive = 25
        """
    ).lstrip()


def make_privkey(wg_name: str, overwrite: bool = False) -> t.Optional[str]:
    privkey = Path(f"/etc/wireguard/{wg_name}-privkey")
    if not overwrite:
        if run(f"ls {privkey}", sudo=True, quiet=True).ok:
            return None

    return (
        run(
            f"( umask 077 & wg genkey | tee {privkey} | wg pubkey )",
            sudo=True,
            quiet=True,
        )
        .assert_ok()
        .stdout.strip()
    )


UPDOWN_TMPL = """
#!/bin/bash

set -e

WG_NAME="{{ wg.name }}"
WG_SUBNET="{{ wg.cidr }}"
WG_CHAIN="${WG_NAME}_RULES"
WG_FORWARD_CHAIN="${WG_NAME}_FORWARD"
WG_LOGDROP_CHAIN="${WG_NAME}_LOGDROP"

if [ "$1" == "up" ]; then
    echo "Setting up iptables rules for $WG_NAME..."

    # Create custom chains
    iptables -t filter -N $WG_CHAIN 2>/dev/null || true
    iptables -t filter -N $WG_FORWARD_CHAIN 2>/dev/null || true
    iptables -t filter -N $WG_LOGDROP_CHAIN 2>/dev/null || true

    # Clear existing rules in our custom chains
    iptables -t filter -F $WG_CHAIN
    iptables -t filter -F $WG_FORWARD_CHAIN
    iptables -t filter -F $WG_LOGDROP_CHAIN

    # === LOGDROP CHAIN RULES ===
    iptables -A $WG_LOGDROP_CHAIN -m limit --limit 2/sec -j LOG --log-level debug --log-prefix 'DROPIN> ({{ wg.name }})'
    iptables -A $WG_LOGDROP_CHAIN -j DROP

    # === INPUT CHAIN RULES (for traffic TO the server) ===

    # Allow inbound wireguard UDP traffic
    iptables -I INPUT 1 -p udp --dport {{ wg.port }} -j ACCEPT

    # Jump to our custom chain for WireGuard interface traffic
    iptables -I INPUT -i $WG_NAME -j $WG_CHAIN

    # Allow DNS requests from WireGuard clients
    iptables -A $WG_CHAIN -p udp --dport 53 -j ACCEPT
    iptables -A $WG_CHAIN -p tcp --dport 53 -j ACCEPT

    # Allow WireGuard clients to ping the server
    iptables -A $WG_CHAIN -p icmp --icmp-type echo-request -j ACCEPT

    # Allow established and related connections
    iptables -A $WG_CHAIN -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

    {% if wg.allow_traffic_to_server %}
    # wg.allow_traffic_to_server == True
    iptables -A $WG_CHAIN -i $WG_NAME -j ACCEPT
    {% endif %}

    # Everything else gets logged and dropped
    iptables -A $WG_CHAIN -j $WG_LOGDROP_CHAIN

    # === FORWARD CHAIN RULES (for traffic THROUGH the server) ===
    # Jump to our custom forward chain for WireGuard traffic
    iptables -I FORWARD -i $WG_NAME -j $WG_FORWARD_CHAIN
    iptables -I FORWARD -o $WG_NAME -j $WG_FORWARD_CHAIN

    # Allow forwarding between WireGuard clients
    iptables -A $WG_FORWARD_CHAIN -i $WG_NAME -o $WG_NAME -j ACCEPT

    # Allow WireGuard clients to access the internet
    {% for iface in wg.interfaces %}
    iptables -A $WG_FORWARD_CHAIN -i $WG_NAME -o {{ iface }} -j ACCEPT
    # Allow return traffic from internet to WireGuard clients
    iptables -A $WG_FORWARD_CHAIN -i {{ iface }} -o $WG_NAME -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
    {% endfor %}

    # Enable IP forwarding
    echo 1 > /proc/sys/net/ipv4/ip_forward

    echo "iptables rules for $WG_NAME configured successfully"

elif [ "$1" == "down" ]; then
    echo "Cleaning up iptables rules for $WG_NAME..."

    iptables -D INPUT -p udp --dport {{ wg.port }} -j ACCEPT

    # Remove jump rules to our custom chains
    iptables -D INPUT -i $WG_NAME -j $WG_CHAIN 2>/dev/null || true
    iptables -D INPUT -i $WG_NAME -j $WG_LOGDROP_CHAIN 2>/dev/null || true
    iptables -D FORWARD -i $WG_NAME -j $WG_FORWARD_CHAIN 2>/dev/null || true
    iptables -D FORWARD -o $WG_NAME -j $WG_FORWARD_CHAIN 2>/dev/null || true

    # Flush and delete custom chains
    iptables -t filter -F $WG_CHAIN 2>/dev/null || true
    iptables -t filter -X $WG_CHAIN 2>/dev/null || true

    iptables -t filter -F $WG_FORWARD_CHAIN 2>/dev/null || true
    iptables -t filter -X $WG_FORWARD_CHAIN 2>/dev/null || true

    iptables -t filter -F $WG_LOGDROP_CHAIN 2>/dev/null || true
    iptables -t filter -X $WG_LOGDROP_CHAIN 2>/dev/null || true

    echo "iptables rules for $WG_NAME cleaned up successfully"
else
    exit 1
fi
"""

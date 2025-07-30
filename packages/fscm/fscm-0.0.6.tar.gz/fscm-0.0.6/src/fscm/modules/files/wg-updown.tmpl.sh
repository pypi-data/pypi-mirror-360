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
    # Jump to our custom chain for WireGuard interface traffic
    iptables -I INPUT -i $WG_NAME -j $WG_CHAIN

    (% if wg.allow_traffic_to_server %}
    iptables -I INPUT 1 -i $WG_NAME -j ACCEPT
    {% else %}
    iptables -I INPUT 1 -i $WG_NAME -j $WG_LOGDROP_CHAIN
    {% endif %}

    # Allow DNS requests from WireGuard clients
    iptables -A $WG_CHAIN -p udp --dport 53 -j ACCEPT
    iptables -A $WG_CHAIN -p tcp --dport 53 -j ACCEPT

    # Allow WireGuard clients to ping the server
    iptables -A $WG_CHAIN -p icmp --icmp-type echo-request -j ACCEPT

    # Allow established and related connections
    iptables -A $WG_CHAIN -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

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

    # Remove jump rules to our custom chains
    iptables -D INPUT -i $WG_NAME -j $WG_CHAIN 2>/dev/null || true
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

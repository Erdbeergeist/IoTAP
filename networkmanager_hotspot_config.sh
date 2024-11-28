#!/bin/bash
nmcli con delete iotap
nmcli con add type wifi ifname wlan0 mode ap con-name iotap ssid "PLACE SSID HERE"  autoconnect false
nmcli con modify iotap 802-11-wireless.band bg
nmcli con modify iotap 802-11-wireless.channel 3
nmcli con modify iotap ipv4.method shared ipv4.address 10.10.10.1/24
nmcli con modify iotap wifi-sec.group ccmp
nmcli con modify iotap wifi-sec.pairwise ccmp
nmcli connection modify iotap 802-11-wireless-security.pmf 1
nmcli con modify iotap ipv6.method disabled
nmcli con modify iotap wifi-sec.key-mgmt wpa-psk
nmcli con modify iotap wifi-sec.psk "PLACE PASSWORD HERE"
nmcli con up iotap

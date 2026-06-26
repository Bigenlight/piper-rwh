#!/usr/bin/env bash
# host-can-up.sh — bring up a SocketCAN interface on the HOST for real Piper hardware.
#
# Run this on the Linux host (NOT inside the container), with sudo, before
# starting the `real` profile (docker compose --profile real up).
# The AgileX Piper uses a USB-CAN adapter exposed via the gs_usb kernel driver.
#
# Usage:
#   sudo ./scripts/host-can-up.sh [IFACE] [BITRATE]
#   sudo CAN_IFACE=can0 CAN_BITRATE=1000000 ./scripts/host-can-up.sh
#
# Defaults match versions.env / SPEC: iface=can0, bitrate=1000000 (1 Mbit/s).
set -euo pipefail

IFACE="${1:-${CAN_IFACE:-can0}}"
BITRATE="${2:-${CAN_BITRATE:-1000000}}"

if [ "$(id -u)" -ne 0 ]; then
  echo "WARNING: not running as root — 'ip link set ... up' will likely fail." >&2
  echo "         re-run with: sudo $0 $IFACE $BITRATE" >&2
fi

echo "==> Loading gs_usb kernel module (USB-CAN driver)"
if ! modprobe gs_usb; then
  echo "WARNING: 'modprobe gs_usb' failed — continuing anyway." >&2
  echo "         (driver may be built-in, already loaded, or adapter not present)" >&2
fi

echo "==> Bringing up ${IFACE} as CAN @ ${BITRATE} bit/s"
# Bring down first — if the iface is already UP (previous run / wrong bitrate),
# reconfiguring while UP fails with "Device or resource busy". AgileX's own
# can_activate.sh does the same. Tolerate the iface not existing yet.
ip link set "${IFACE}" down 2>/dev/null || true
ip link set "${IFACE}" up type can bitrate "${BITRATE}"
# Bigger TX queue: a single Piper streams thousands of frames/s; the default
# txqueuelen (10) can drop frames under bursts. Best-effort (ignore if unsupported).
ip link set "${IFACE}" txqueuelen 65536 2>/dev/null || true

echo "==> Interface state:"
ip -details link show "${IFACE}"

cat <<EOF

==> ${IFACE} is up. Sanity-check traffic with:
      candump ${IFACE}
    (install with: sudo apt install can-utils)

    To bring it back down later:
      sudo ip link set ${IFACE} down
EOF

# ----------------------------------------------------------------------------
# OPTIONAL: automatic bring-up at boot / on adapter plug-in
# ----------------------------------------------------------------------------
# 1) udev rule — rename the adapter to a stable name and trigger setup.
#    Create /etc/udev/rules.d/90-piper-can.rules :
#
#      # match the gs_usb CAN adapter and give it a stable name "can0"
#      SUBSYSTEM=="net", ACTION=="add", DRIVERS=="gs_usb", NAME="can0"
#
#    Then: sudo udevadm control --reload-rules && sudo udevadm trigger
#
# 2) systemd-networkd — configure bitrate + auto-up declaratively.
#    Create /etc/systemd/network/80-can0.network :
#
#      [Match]
#      Name=can0
#
#      [CAN]
#      BitRate=1000000
#
#    And enable: sudo systemctl enable --now systemd-networkd
#    (systemd-networkd will set the bitrate and bring can0 up automatically
#     whenever it appears, removing the need to run this script manually.)
# ----------------------------------------------------------------------------

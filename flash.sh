#!/usr/bin/env bash
# Fetch the latest Planck EZ Glow firmware from GitHub and flash it, without
# needing a working keyboard during the flash.
#
# Usage:
#   ./flash.sh              Download the latest firmware, then wait and flash.
#   ./flash.sh --offline    Skip the download; flash the .bin already in
#                           firmware_download/ (useful with no network).
#
# Flow:
#   1. Run this script.
#   2. When it says "Waiting for the keyboard...", press the reset button on
#      the underside of the Planck EZ (or tap your QK_BOOT key).
#   3. It flashes automatically and the board reboots into the new firmware.
#
# Because the script is already running before you enter the bootloader, you
# do NOT need a working keyboard during the flash.

set -euo pipefail

REPO="thompsy/planck-ez-firmware"
DIR="$(cd "$(dirname "$0")" && pwd)/firmware_download"
OFFLINE=0

for arg in "$@"; do
  case "$arg" in
    --offline) OFFLINE=1 ;;
    -h|--help)
      sed -n '2,18p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown option: $arg (try --help)" >&2
      exit 2
      ;;
  esac
done

# --- Preflight: required tools --------------------------------------------
if ! command -v dfu-util >/dev/null 2>&1; then
  echo "dfu-util not found. Install it with: brew install dfu-util" >&2
  exit 1
fi

# --- Fetch the latest firmware from the rolling 'latest' release ----------
if [[ "$OFFLINE" -eq 0 ]]; then
  if ! command -v gh >/dev/null 2>&1; then
    echo "gh (GitHub CLI) not found. Install it with: brew install gh" >&2
    echo "Or run with --offline to flash an already-downloaded .bin." >&2
    exit 1
  fi
  if ! gh auth status >/dev/null 2>&1; then
    echo "gh is not authenticated. Run: gh auth login" >&2
    echo "Or run with --offline to flash an already-downloaded .bin." >&2
    exit 1
  fi

  echo ">>> Fetching the latest firmware from $REPO (release: latest)..."
  mkdir -p "$DIR"
  if ! gh release download latest --repo "$REPO" \
        --pattern '*.bin' --dir "$DIR" --clobber; then
    echo "Failed to download the latest release asset." >&2
    echo "Check that the 'latest' release exists and that your active gh" >&2
    echo "account can access $REPO (gh auth status)." >&2
    exit 1
  fi
fi

# --- Locate the .bin (glob, so the exact filename can change) -------------
shopt -s nullglob
bins=("$DIR"/*.bin)
shopt -u nullglob

if [[ ${#bins[@]} -eq 0 ]]; then
  echo "No firmware .bin found in: $DIR" >&2
  if [[ "$OFFLINE" -eq 1 ]]; then
    echo "Run without --offline to download the latest firmware first." >&2
  fi
  exit 1
fi

# If multiple .bins are present, pick the most recently modified one.
FW="${bins[0]}"
for f in "${bins[@]}"; do
  [[ "$f" -nt "$FW" ]] && FW="$f"
done

echo "Firmware: $FW"
echo
echo ">>> Waiting for the keyboard to enter bootloader mode."
echo ">>> Press the RESET button on the underside of the Planck EZ now"
echo ">>> (or tap your QK_BOOT key). Ctrl-C to cancel."
echo

# --- Wait for the STM32 DFU device, then flash ----------------------------
while true; do
  if dfu-util -l 2>/dev/null | grep -q "0483:df11"; then
    echo ">>> Bootloader detected. Flashing..."
    dfu-util -a 0 -s 0x08000000:leave -D "$FW"
    echo
    echo ">>> Done. The keyboard should have rebooted into the new firmware."
    exit 0
  fi
  sleep 1
done

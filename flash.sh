#!/usr/bin/env bash
# Flash the Planck EZ Glow firmware without needing to type anything after
# entering the bootloader.
#
# Usage:
#   1. Run this script:  ./flash.sh
#   2. When it says "Waiting for the keyboard...", press the reset button on
#      the underside of the Planck EZ (or tap your QK_BOOT key).
#   3. It flashes automatically and the board reboots into the new firmware.
#
# Because the script is already running before you enter the bootloader, you
# do NOT need a working keyboard during the flash.

set -euo pipefail

FW="$(cd "$(dirname "$0")" && pwd)/firmware_download/zsa_planck_ez_glow_miryoku_tweaked.bin"

if [[ ! -f "$FW" ]]; then
  echo "Firmware not found at: $FW" >&2
  echo "Re-download it with: gh run download 27879760874 --repo thompsy/planck-ez-firmware --name planck_ez_glow_firmware --dir firmware_download" >&2
  exit 1
fi

echo "Firmware: $FW"
echo
echo ">>> Waiting for the keyboard to enter bootloader mode."
echo ">>> Press the RESET button on the underside of the Planck EZ now"
echo ">>> (or tap your QK_BOOT key). Ctrl-C to cancel."
echo

# Poll until the STM32 DFU device (0483:df11) shows up, then flash.
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

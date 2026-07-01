#!/usr/bin/env bash
# Capture a timestamped QMK console keylog for later analysis with
# analyse_keylog.py. Requires CONSOLE_ENABLE (already on in this firmware).
#
# Usage:
#   ./tools/keylog.sh [output-file]      # default: ~/planck-keylog.txt
#
# Type normally in a NON-SENSITIVE document, and tap the centre 2u bar the
# instant you notice a typing mistake (it types nothing, flashes red, and
# writes a MARK line). Ctrl-C to stop, then:
#
#   ./tools/analyse_keylog.py <output-file>
#
# This is a full keystroke logger while running — do not capture passwords/2FA.
set -euo pipefail

OUT="${1:-$HOME/planck-keylog.txt}"

if ! command -v qmk >/dev/null 2>&1; then
  echo "qmk CLI not found. Install it (e.g. 'pipx install qmk' or 'python3 -m pip install qmk')," >&2
  echo "or capture with hid_listen instead. On Linux you may need the QMK udev rules or sudo" >&2
  echo "to read the console HID device." >&2
  exit 1
fi

echo ">>> Logging QMK console to: $OUT"
echo ">>> Type normally; tap the centre bar on mistakes. Ctrl-C to stop."
echo
exec qmk console -t | tee -a "$OUT"

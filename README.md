# Planck EZ Glow — Miryoku (tweaked) firmware

Cloud-compiled QMK firmware for my Planck EZ Glow. The layout lives in
[`keymap/`](keymap/); GitHub Actions builds it against
[mainline QMK](https://github.com/qmk/qmk_firmware) and publishes the `.bin`
as a downloadable artifact. **No local toolchain required** — build in the
cloud, then flash with QMK Toolbox or `dfu-util`.

## One-time setup

1. Create a new GitHub repo (private is fine).
2. Push this folder to it:
   ```bash
   cd planck-ez-firmware
   git init -b main
   git add .
   git commit -m "Planck EZ Miryoku layout (mainline QMK)"
   git remote add origin git@github.com:<you>/<repo>.git
   git push -u origin main
   ```
   The push triggers the build automatically.

## Get a new firmware build

- Edit anything under `keymap/`, commit, and push — or open the **Actions** tab
  and use **Run workflow** on "Build Planck EZ firmware".
- When the run finishes (green check, ~2–5 min), open it and download the
  **`planck_ez_glow_firmware`** artifact from the Artifacts section. It's a zip
  containing the `.bin`.

The workflow pins a specific mainline QMK commit (`ref:` in
`.github/workflows/build.yml`) for reproducible builds. Bump that SHA to pick up
a newer QMK, then re-run and re-test.

## Flash

The Planck EZ is an STM32 board and uses the built-in **DFU bootloader** over
USB. Enter the bootloader by pressing the physical **reset button** (underside
of the board) or by tapping the `QK_BOOT` key already mapped on several layers.

Then flash with whichever tool you prefer:

- **QMK Toolbox (GUI, no compiler):** open the `.bin`, put the board in
  bootloader mode, click **Flash**.
- **QMK CLI:** `qmk flash -kb zsa/planck_ez/glow -km miryoku_tweaked`
  (compiles locally, then waits for the bootloader).
- **`dfu-util` (raw CLI):**
  ```bash
  dfu-util -a 0 -s 0x08000000:leave -D planck_ez_glow_miryoku_tweaked.bin
  ```

## What changed vs. the Oryx export

- **Tap/hold tuning made explicit** in `keymap/config.h`: `PERMISSIVE_HOLD`,
  `CHORDAL_HOLD`, and `FLOW_TAP_TERM 150` (the settings you'd toggled in Oryx,
  now under your control and tunable).
- **Caps Word** (`CW_TOGG`) replaces plain `KC_CAPS` on the Nav layer
  (left-thumb Enter hold). Tap it, then type — the next word auto-capitalises and
  cancels on space. This removes most need to *hold* a home-row Shift while
  typing fast, which is the root cause of the `pyHon`/`t'` misfires.
- **Per-key Flow Tap** (`get_flow_tap_term()` in `keymap/keymap.c`): Flow Tap
  normally forces a mod-tap/layer-tap to its *tap* when pressed quickly after the
  previous key, which caused two misfires — `Shift+'` came out as `t"`, and
  layer-thumb symbols like `-` came out as `<space><letter>` (because `KC_SPC` is
  in Flow Tap's default set). The callback returns `0` (disables Flow Tap) for the
  two home-row Shift keys and all six layer-tap thumb keys, so deliberate
  Shift-chords and layer holds always engage. Flow Tap stays active on the inner
  home-row mods (GUI/Alt/Ctrl/RALT), so fast letter rolls are still protected from
  accidental modifiers. Tune `FLOW_TAP_TERM` in `config.h` for those remaining
  keys; add/remove cases in the callback to change which keys opt out.

## Converted from the ZSA fork to mainline QMK

This layout originally built against ZSA's QMK fork. It now builds against
mainline `qmk/qmk_firmware`. The changes made for the port:

- `EZ_SAFE_RANGE` → `SAFE_RANGE` (mainline custom-keycode range).
- Layer-6 lighting keys migrated from the removed rgblight `RGB_*` keycodes to
  RGB Matrix `RM_*` keycodes (`RM_TOGG`, `RM_NEXT`, `RM_HUEU/HUED`,
  `RM_VALU/VALD`, `RM_SATU/SATD`, `RM_SPDU/SPDD`). The custom `RGB_SLD` key now
  calls `rgb_matrix_mode(RGB_MATRIX_SOLID_COLOR)`.
- Removed the Oryx/Keymapp live-control hooks (`rawhid_state`), which don't exist
  in mainline. Per-layer LED colours still work — they're driven by
  `rgb_matrix_indicators_user()` + the `ledmap[]` table in `keymap.c`, gated only
  by `keyboard_config.disable_layer_led`.
- `rules.mk`: dropped `ORYX_ENABLE` and `RGB_MATRIX_CUSTOM_KB`; deleted the empty
  `rgb_matrix_kb.inc` (the glow's RGB matrix is built into the mainline keyboard).
- `config.h`: added `#define ORYX_CONFIGURATOR`, which is how mainline exposes the
  `TOGGLE_LAYER_COLOR` and `LED_LEVEL` keycodes for the Planck EZ.

### Trade-off vs. Keymapp

Mainline builds can't be flashed or inspected with Keymapp's live per-layer LED
display (that depends on the ZSA-fork-only Oryx hooks). Flashing is done with
QMK Toolbox / `qmk flash` / `dfu-util` instead, as above.

## Notes / troubleshooting

- Tuning knob: `FLOW_TAP_TERM` in `config.h`. Lower (~120) = more aggressive at
  treating fast keys as taps (fewer roll misfires); higher (~175) = easier to
  land deliberate mod chords.
- If a build breaks after bumping the pinned QMK SHA, the usual cause is a
  keycode rename or hook-signature change in mainline. Check the QMK changelog
  for the range you jumped, or pin back to the previous SHA.

## Why not Achordion?

Achordion is the usual "go further" suggestion, but it overlaps with the
`CHORDAL_HOLD`/`FLOW_TAP` setup already in use. The `"`→`t"` and `-`→`<space>g`
misfires turned out to be Flow Tap demoting deliberate holds to taps, so the
targeted fix is the per-key `get_flow_tap_term()` callback (see above) rather
than adding another tap/hold heuristic on top.

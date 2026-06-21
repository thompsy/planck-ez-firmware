# Planck EZ Glow — Miryoku (tweaked) firmware

## Overview

Custom QMK firmware for the **Planck EZ Glow** — a 47-key, 4×12 ortholinear
keyboard with an STM32 microcontroller and per-key RGB. The layout is a
**Miryoku-style** layered keymap: Colemak-DH alphas, home-row mods, and thumb
keys that double as layer switches. "Tweaked" means a few personal adjustments
on top of vanilla Miryoku — tap/hold tuning, Caps Word, and a per-key Flow Tap
fix for symbol misfires.

It builds **entirely in the cloud** — GitHub Actions compiles it against
[mainline QMK](https://github.com/qmk/qmk_firmware), uploads the `.bin` as an
artifact, and publishes it to a rolling **`latest`** GitHub Release. No local
toolchain is required: build in the cloud, then run [`./flash.sh`](flash.sh) to
fetch the newest firmware and flash it in one step (or use QMK Toolbox /
`dfu-util` manually).

> **This is my personal config.** The repository URL, the `SERIAL_NUMBER` in
> `keymap/config.h`, and the UK currency keys (`£`, `€`) are specific to me. If
> you want to reuse it, fork the repo and adjust those to taste.

## The layout

Base layer (tap legends shown; held behaviour noted below):

```
┌─────┬─────┬─────┬─────┬─────┬─────┐ ┌─────┬─────┬─────┬─────┬─────┬─────┐
│  Q  │  W  │  F  │  P  │  B  │ TD  │ │     │  J  │  L  │  U  │  Y  │  '  │
├─────┼─────┼─────┼─────┼─────┼─────┤ ├─────┼─────┼─────┼─────┼─────┼─────┤
│  A  │  R  │  S  │  T  │  G  │     │ │     │  M  │  N  │  E  │  I  │  O  │
│ GUI │ Alt │ Ctl │ Sft │     │     │ │     │     │ Sft │ Ctl │ Alt │ GUI │
├─────┼─────┼─────┼─────┼─────┼─────┤ ├─────┼─────┼─────┼─────┼─────┼─────┤
│  Z  │  X  │  C  │  D  │  V  │     │ │     │  K  │  H  │  ,  │  .  │  /  │
│     │RAlt │     │ Meh │     │     │ │     │     │ Meh │     │RAlt │     │
├─────┼─────┼─────┼─────┼─────┼─────┤ ├─────┼─────┼─────┼─────┼─────┼─────┤
│     │     │ Esc │ Ent │ Tab │     │ │     │ Bsp │ Spc │ Del │     │     │
└─────┴─────┴─────┴─────┴─────┴─────┘ └─────┴─────┴─────┴─────┴─────┴─────┘
```

- **Home-row mods** (hold a home-row key for a modifier): GUI / Alt / Ctrl /
  Shift, mirrored on both hands. `X` and `.` add Right-Alt; `D` and `H` add Meh
  (Ctrl+Alt+Shift).
- **Thumb keys** tap to `Esc Ent Tab` (left) and `Bsp Spc Del` (right), and
  **hold** to reach layers:
  | Hold thumb | Layer                                    |
  |------------|------------------------------------------|
  | Esc        | RGB / media controls                     |
  | Enter      | Navigation (arrows, Home/End, Caps Word) |
  | Tab        | Mouse (cursor, wheel, buttons)           |
  | Space      | Numbers + math symbols                   |
  | Bksp       | Symbols / brackets                       |
  | Delete     | Function keys (F1–F12)                   |
- **TD** (top row) is a tap-dance: double-tap to switch to/from a plain QWERTY
  layer.

The full keymap, all layers, and the RGB per-layer colour map live in
[`keymap/keymap.c`](keymap/keymap.c).

## Repo layout

| Path                          | What it is                                                |
|-------------------------------|-----------------------------------------------------------|
| `keymap/`                     | The layout: `keymap.c`, `config.h`, `rules.mk`, etc.      |
| `flash.sh`                    | Helper that downloads the latest firmware and flashes it. |
| `.github/workflows/build.yml` | Cloud build + rolling-release workflow.                   |

## Get a new firmware build

- Edit anything under `keymap/`, commit, and push — or open the **Actions** tab
  and use **Run workflow** on "Build Planck EZ firmware".
- When the run finishes (green check, ~2–5 min), open it and download the
  **`planck_ez_glow_firmware`** artifact from the Artifacts section. It's a zip
  containing the `.bin`.

Every successful build on `main` also updates a rolling **`latest`** GitHub
Release with the `.bin` at a stable URL:
<https://github.com/thompsy/planck-ez-firmware/releases/tag/latest>. This is the
durable download source — unlike Actions artifacts (which expire after ~90
days), the release sticks around, and it's what [`./flash.sh`](flash.sh) fetches.

The workflow pins a specific mainline QMK commit (`ref:` in
`.github/workflows/build.yml`) for reproducible builds. Bump that SHA to pick up
a newer QMK, then re-run and re-test.

## Flash

The Planck EZ is an STM32 board and uses the built-in **DFU bootloader** over
USB. Enter the bootloader by pressing the physical **reset button** (underside
of the board) or by tapping the `QK_BOOT` key already mapped on several layers.

### Recommended: `./flash.sh`

The [`flash.sh`](flash.sh) helper fetches the latest firmware from the `latest`
release and flashes it — no manual download, no hunting for the `.bin`.

Prerequisites (one-time):

```bash
brew install gh dfu-util
gh auth login          # authenticate as an account that can read this repo
```

Then:

```bash
./flash.sh             # download the latest .bin, wait for the bootloader, flash
```

Run it, and when it prints "Waiting for the keyboard...", press the reset button
(or tap `QK_BOOT`). Because the script is already running, you don't need a
working keyboard during the flash. It auto-detects the DFU device and flashes.

Flags:

- `./flash.sh --offline` — skip the download and flash the `.bin` already in
  `firmware_download/` (useful with no network).
- `./flash.sh --help` — usage.

### Manual alternatives

If you'd rather not use the script:

- **QMK Toolbox (GUI, no compiler):** open the `.bin`, put the board in
  bootloader mode, click **Flash**.
- **QMK CLI:** `qmk flash -kb zsa/planck_ez/glow -km miryoku_tweaked`
  (compiles locally, then waits for the bootloader).
- **`dfu-util` (raw CLI):** with the board in bootloader mode, point it at the
  `.bin` (e.g. the one `flash.sh` downloaded into `firmware_download/`):
  ```bash
  dfu-util -a 0 -s 0x08000000:leave -D firmware_download/zsa_planck_ez_glow_miryoku_tweaked.bin
  ```

## Notes / troubleshooting

- **Tap/hold tuning knob:** `FLOW_TAP_TERM` in `config.h`. Lower (~120) = more
  aggressive at treating fast keys as taps (fewer roll misfires); higher (~175)
  = easier to land deliberate mod chords.
- **Symbol misfires:** a per-key `get_flow_tap_term()` callback in `keymap.c`
  disables Flow Tap on the Shift mod-taps and the layer-tap thumbs, which fixes
  `"` coming out as `t"` and `-` as `<space>g`. Adjust the cases there if other
  keys misfire.
- **Build breaks after bumping the pinned QMK SHA:** usually a keycode rename or
  hook-signature change in mainline. Check the QMK changelog for the range you
  jumped, or pin back to the previous SHA.
- **Background:** this firmware was ported from ZSA's QMK fork to mainline
  `qmk/qmk_firmware`; see the git history for the porting details and the
  reasoning behind the Flow Tap fix.

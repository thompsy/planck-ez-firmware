# Planck EZ Glow — Miryoku (tweaked) firmware

Cloud-compiled QMK firmware for my Planck EZ Glow. The layout lives in
[`keymap/`](keymap/); GitHub Actions builds it against
[ZSA's QMK fork](https://github.com/zsa/qmk_firmware) and publishes the `.bin`
as a downloadable artifact. **No local toolchain required** — flash the result
through Keymapp exactly like an Oryx build.

## One-time setup

1. Create a new GitHub repo (private is fine).
2. Push this folder to it:
   ```bash
   cd planck-ez-firmware
   git init -b main
   git add .
   git commit -m "Initial Planck EZ Miryoku layout"
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

## Flash

1. Unzip to get `zsa_planck_ez_glow.bin` (name may vary slightly).
2. Open **Keymapp**, click **Flash**, choose **Flash a custom firmware**, and
   select the `.bin`. Put the board in bootloader mode (reset) when prompted.

`ORYX_ENABLE = yes` is kept in `keymap/rules.mk`, so Keymapp's live per-layer
LED display still works.

## What changed vs. the Oryx export

These are the only edits to the original Oryx source:

- **Tap/hold tuning made explicit** in `keymap/config.h`: `PERMISSIVE_HOLD`,
  `CHORDAL_HOLD`, and `FLOW_TAP_TERM 150` (the settings you'd toggled in Oryx,
  now under your control and tunable).
- **Caps Word** (`CW_TOGG`) replaces plain `KC_CAPS` on the Nav layer
  (left-thumb Enter hold). Tap it, then type — the next word auto-capitalises and
  cancels on space. This removes most need to *hold* a home-row Shift while
  typing fast, which is the root cause of the `pyHon`/`t'` misfires.
- **`"` via a combo**: press **U + Y together** to emit `"`. Because no Shift is
  involved, flow-tap can't demote it — so `"` is reliable while `python` stays
  correct. Move it by editing `dquo_combo[]` in `keymap/keymap.c` (keep
  `COMBO_COUNT` in `config.h` in sync).

## Notes / troubleshooting

- This keymap depends on ZSA-only code (`EZ_SAFE_RANGE`, `rawhid_state`,
  `ORYX_ENABLE`, the custom RGB matrix), so it **must** build against ZSA's fork.
  Don't switch the workflow to `qmk/qmk_firmware` (mainline) — it won't compile.
- If the build ever fails on `CHORDAL_HOLD` or `FLOW_TAP_TERM`, ZSA's fork
  branch is older than those features; remove those two lines from `config.h`
  (you'll fall back to permissive-hold-only behaviour) or pin a newer ref in
  `.github/workflows/build.yml`.
- Tuning knob: `FLOW_TAP_TERM` in `config.h`. Lower (~120) = more aggressive at
  treating fast keys as taps (fewer roll misfires); higher (~175) = easier to
  land deliberate mod chords.

## Why not Achordion?

Achordion is the usual "go further" suggestion, but it wouldn't fix the `"`
problem: like flow-tap, its streak/handedness logic decides Shift's fate from
timing, so fast `Shift+"` still looks like a roll. It also overlaps with the
`CHORDAL_HOLD`/`FLOW_TAP` setup you already like. The combo sidesteps the issue
entirely by not using Shift at all, so it's the better fix here.

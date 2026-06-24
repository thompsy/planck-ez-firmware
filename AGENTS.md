# AGENTS.md

QMK keymap for the ZSA Planck EZ Glow. See `README.md` for the layout and flash
docs; this file covers the non-obvious things.

## Repo is keymap-only

Only the keymap source lives here (`keymap/keymap.c`, `config.h`, `rules.mk`,
`i18n.h`). The QMK firmware tree is **not** vendored, so there is no local
`make` target and you cannot build locally without a separate QMK checkout.

## Builds run in CI, not locally

- `.github/workflows/build.yml` checks out mainline QMK at a pinned SHA
  (`ref:`), copies `keymap/*` into `keyboards/zsa/planck_ez/keymaps/miryoku_tweaked/`,
  and runs `make zsa/planck_ez/glow:miryoku_tweaked`.
- The build/keymap name `miryoku_tweaked` comes from the workflow's copy
  destination — it is not derived from any file in this repo.
- To build/verify a change: commit and push (or Actions -> Run workflow), then
  confirm the "Build Planck EZ firmware" run goes green. That is the only
  verification available here.
- Upgrade QMK by editing the `ref:` SHA in the workflow. Build breaks after a
  bump are usually keycode renames / hook-signature changes in mainline.

## Pushing to `main` ships firmware

Every successful build on `main` also publishes a rolling `latest` GitHub
Release with the `.bin`. `flash.sh` fetches from that release. Treat pushes to
`main` as releases.

## Flashing

`./flash.sh` (needs `gh` authenticated + `dfu-util`); `--offline` flashes the
`.bin` already in `firmware_download/`. STM32 DFU device id is `0483:df11`.

## Tap/hold

Governed solely by `TAPPING_TERM` (215) + `QUICK_TAP_TERM 0` in `config.h`.
Flow Tap, Permissive Hold, and Chordal Hold are all intentionally **disabled**;
do not reintroduce them when tuning misfires — adjust `TAPPING_TERM` instead.

## Temporary debug state

`rules.mk` has `CONSOLE_ENABLE = yes` and `keymap.c` sets `debug_enable = true`,
both flagged "TEMPORARY DEBUG" for tap-hold diagnosis. Leave on for now; revert
before shipping a clean build.

## Personalization (not generic)

`SERIAL_NUMBER` in `config.h`, the repo slug `thompsy/planck-ez-firmware` in
`flash.sh`, and the UK currency keys in `i18n.h` are owner-specific.

## keymap.c structure

Enums at the top (`planck_keycodes`, `tap_dance_codes`, `planck_layers`), 10
layers via `LAYOUT_planck_grid`, `process_record_user()`, tap-dance `dance_*`
handlers, and the RGB per-layer colour map (`ledmap` / `set_layer_color` /
`rgb_matrix_indicators_user`).

# AGENTS.md

QMK keymap for the ZSA Planck EZ Glow. See `README.md` for the layout and flash
docs; this file covers the non-obvious things.

## Repo is keymap-only

Only the keymap source lives here (`keymap/keymap.c`, `config.h`, `rules.mk`,
`i18n.h`). The QMK firmware tree is **not** vendored, so there is no local
`make` target and you cannot build locally without a separate QMK checkout.

## Version control: use `jj`, not `git`

This repo is managed with [Jujutsu (`jj`)](https://jj-vcs.github.io/) on top of
the git backend. **Always use `jj` for version-control operations; do not use
raw `git` commands** (the working copy is usually a detached-HEAD `jj` commit,
so plain `git commit`/`git push` will fight the tool).

Core workflow:

- `jj status` — show working-copy changes (analogous to `git status`).
- `jj diff` — show the diff of the working copy.
- `jj log` — show the commit graph; `@` is the working copy, `@-` its parent.
- `jj describe -m "message"` — set/replace the description of the current
  working-copy commit (`@`). This is how you "commit": edits are already
  tracked in `@`, you just give it a message.
- `jj new` — start a fresh empty working-copy commit on top of the current one
  (do this after `describe` so the next batch of edits is separate).
- `jj bookmark set main -r @-` — move the `main` bookmark to a commit (jj
  bookmarks are git branches). Point it at the described commit you want to
  ship.
- `jj git push` — push bookmarks to the `origin` remote. Pushing `main` ships
  firmware (see below). Use `jj git fetch` to update from the remote.

Typical "commit and push" sequence here:

```
jj describe -m "Short summary"   # describe the current @ (your edits)
jj new                           # leave a clean working copy on top
jj bookmark set main -r @-       # advance main to the described commit
jj git push                      # publish (this triggers the CI build/release)
```

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

Enums at the top (`planck_keycodes`, `tap_dance_codes`, `planck_layers`), 8
layers via `LAYOUT_planck_grid`, `process_record_user()`, tap-dance `dance_*`
handlers, and the RGB per-layer colour map (`ledmap` / `set_layer_color` /
`rgb_matrix_indicators_user`).

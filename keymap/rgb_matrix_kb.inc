// No custom RGB matrix effects for this layout.
//
// RGB_MATRIX_CUSTOM_KB = yes (rules.mk) makes QMK #include this file so it can
// register custom effect modes via RGB_MATRIX_EFFECT(...). This layout defines
// none — all per-layer colours are driven by rgb_matrix_indicators_user() and
// the ledmap[] table in keymap.c — so this file is intentionally empty.
//
// The ZSA Oryx export relied on this file existing (on the current firmware25
// branch the keyboard no longer ships it), so we provide it here. Add
// RGB_MATRIX_EFFECT(my_effect) lines plus the effect body if you ever want
// custom animations.

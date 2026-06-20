CONSOLE_ENABLE = no
COMMAND_ENABLE = no
AUDIO_ENABLE = no
ORYX_ENABLE = yes
# Oryx set this to pull in a custom RGB-effects file (rgb_matrix_kb.inc) that the
# export never shipped; this layout's per-layer colours come from
# rgb_matrix_indicators_user + the ledmap table instead, which need no custom
# effects. Leaving it on breaks the build on current ZSA fork (missing .inc).
RGB_MATRIX_CUSTOM_KB = no
TAP_DANCE_ENABLE = yes
SPACE_CADET_ENABLE = no
CAPS_WORD_ENABLE = yes
COMBO_ENABLE = yes

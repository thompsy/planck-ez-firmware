CONSOLE_ENABLE = no
COMMAND_ENABLE = no
AUDIO_ENABLE = no
ORYX_ENABLE = yes
# Required on ZSA's fork: this also wires in ZSA keycodes used by the keyboard
# (LED_LEVEL, TOGGLE_LAYER_COLOR). It pulls in rgb_matrix_kb.inc, which the Oryx
# export omitted — we ship an empty one alongside this keymap (no custom effects;
# colours come from rgb_matrix_indicators_user + the ledmap table).
RGB_MATRIX_CUSTOM_KB = yes
TAP_DANCE_ENABLE = yes
SPACE_CADET_ENABLE = no
CAPS_WORD_ENABLE = yes
COMBO_ENABLE = yes

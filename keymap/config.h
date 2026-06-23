#pragma once

#ifdef AUDIO_ENABLE
#define STARTUP_SONG SONG(PLANCK_SOUND)
#endif

#define MIDI_BASIC

/* Enables ZSA Oryx-origin keycodes that mainline QMK keeps for the Planck EZ:
   TOGGLE_LAYER_COLOR and LED_LEVEL, plus smart-LED-aware RM_TOGG behaviour. */
#define ORYX_CONFIGURATOR

#define ENCODER_RESOLUTION 4

#undef TAPPING_TERM
#define TAPPING_TERM 215

#define QUICK_TAP_TERM 0

/* Home-row-mod tap/hold tuning (previously toggled in Oryx; defined here now
   that we own the build). Adjust FLOW_TAP_TERM down toward 120 if cross-hand
   letter rolls (e.g. "th") still occasionally fire a mod, up toward 175 if
   deliberate mod chords get demoted to taps. */
#define PERMISSIVE_HOLD
#define CHORDAL_HOLD
#define FLOW_TAP_TERM 130

#define USB_SUSPEND_WAKEUP_DELAY 0
#define SERIAL_NUMBER "3yGOB/7vBBxj"
#define LAYER_STATE_16BIT

#define RGB_MATRIX_STARTUP_SPD 60


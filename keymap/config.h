#pragma once

#ifdef AUDIO_ENABLE
#define STARTUP_SONG SONG(PLANCK_SOUND)
#endif

/* Enables ZSA Oryx-origin keycodes that mainline QMK keeps for the Planck EZ:
   TOGGLE_LAYER_COLOR and LED_LEVEL, plus smart-LED-aware RM_TOGG behaviour. */
#define ORYX_CONFIGURATOR

#define ENCODER_RESOLUTION 4

#undef TAPPING_TERM
#define TAPPING_TERM 215

#define QUICK_TAP_TERM 0

/* Home-row-mod tap/hold tuning (previously toggled in Oryx; defined here now
   that we own the build). Flow Tap, Permissive Hold and Chordal Hold are all
   disabled; tap/hold resolution is governed purely by TAPPING_TERM (with
   QUICK_TAP_TERM 0). A mod only engages by holding past the tapping term. */

#define USB_SUSPEND_WAKEUP_DELAY 0
#define SERIAL_NUMBER "3yGOB/7vBBxj"
#define LAYER_STATE_16BIT

#define RGB_MATRIX_STARTUP_SPD 60


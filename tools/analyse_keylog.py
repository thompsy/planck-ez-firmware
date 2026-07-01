#!/usr/bin/env python3
"""Analyse a QMK console keylog from the Planck EZ miryoku_tweaked firmware.

The firmware's process_record_user() logs every key event:

    kc:<keycode>   pressed:<0|1> time:<ms> int:<0|1> count:<n>

and the ERR_MARK "typing error" key (the centre 2u bar) logs:

    MARK ================ time:<ms>

This script pairs each MARK with the keystrokes just before it (ground-truth
"I made a mistake here" labels), and adds aggregate tap/hold and correction
stats, so home-row-mod misfires can be pinned to specific keys/fingers.

Usage:
    ./analyse_keylog.py ~/planck-keylog.txt
    ./analyse_keylog.py log.txt --window-ms 3000 --window-keys 14

Notes:
- `time:` is the firmware's 16-bit millisecond timer; it wraps every ~65 s.
  We reconstruct a monotonic timeline, which is reliable during active typing
  (gaps < 65 s). Idle gaps longer than that can mis-order — capture in bursts.
- Lines may carry a `qmk console -t` timestamp/prefix; we scan for the `kc:` /
  `MARK` tokens anywhere in the line, so prefixes are ignored.
"""
import argparse
import re
import statistics
import sys
from collections import Counter, defaultdict

KC_LINE = re.compile(
    r"kc:(?P<kc>.*?)\s+pressed:(?P<pressed>\d+)\s+time:\s*(?P<time>\d+)"
    r"\s+int:(?P<intr>\d+)\s+count:(?P<count>\d+)"
)
MARK_LINE = re.compile(r"MARK\b.*?time:\s*(?P<time>\d+)")
TAPHOLD = re.compile(r"(_T\(|MT\(|LT\d*\()")
INNER_KC = re.compile(r"KC_([A-Z0-9_]+)")
WRAP = 65536

# base-layer home-row mods, for friendlier reporting. mod token -> label,
# checked in this order so RALT is matched before ALT and MEH before the rest.
MODS = [("MEH", "Meh"), ("RALT", "RAlt"), ("SFT", "Shift"),
        ("CTL", "Ctrl"), ("ALT", "Alt"), ("GUI", "GUI")]


def mod_of(kc):
    for token, label in MODS:
        if token in kc:
            return label
    if kc.startswith("LT") or "LT(" in kc:
        return "Layer"
    return None


def load(path):
    raw = []
    with open(path, errors="replace") as fh:
        for lineno, line in enumerate(fh, 1):
            m = KC_LINE.search(line)
            if m:
                raw.append(("key", {
                    "kc": m["kc"].strip(),
                    "pressed": int(m["pressed"]),
                    "time": int(m["time"]),
                    "intr": int(m["intr"]),
                    "count": int(m["count"]),
                    "lineno": lineno,
                }))
                continue
            m = MARK_LINE.search(line)
            if m:
                raw.append(("mark", {"time": int(m["time"]), "lineno": lineno}))
    return raw


def add_monotonic(raw):
    base = 0
    prev = None
    for _, f in raw:
        t = f["time"]
        if prev is not None and prev - t > WRAP // 2:
            base += WRAP
        prev = t
        f["t"] = base + t
    return raw


def make_stroke(press, release):
    kc = press["kc"]
    is_th = bool(TAPHOLD.search(kc))
    count = (release or press)["count"]
    if is_th:
        resolved = "tap" if count > 0 else "hold"
    else:
        resolved = "plain"
    inner = INNER_KC.search(kc)
    return {
        "kc": kc,
        "letter": inner.group(1) if inner else kc,
        "mod": mod_of(kc),
        "is_th": is_th,
        "resolved": resolved,
        "press_t": press["t"],
        "release_t": release["t"] if release else None,
        "dwell": (release["t"] - press["t"]) if release else None,
        "press_line": press["lineno"],
    }


def build(events):
    """Return (strokes sorted by press time, list of mark times)."""
    mark_times = {f["time"] for k, f in events if k == "mark"}
    marker_kcs = {
        f["kc"] for k, f in events
        if k == "key" and f["pressed"] == 1 and f["time"] in mark_times
    }
    marks = [f["t"] for k, f in events if k == "mark"]

    strokes = []
    open_presses = defaultdict(list)
    for kind, f in events:
        if kind != "key" or f["kc"] in marker_kcs:
            continue
        if f["pressed"] == 1:
            open_presses[f["kc"]].append(f)
        elif open_presses[f["kc"]]:
            strokes.append(make_stroke(open_presses[f["kc"]].pop(), f))
    for lst in open_presses.values():
        for press in lst:
            strokes.append(make_stroke(press, None))
    strokes.sort(key=lambda s: s["press_t"])
    return strokes, marks, marker_kcs


def overlaps(stroke, strokes):
    """Other keys pressed while this key was held down (a roll into the mod)."""
    if stroke["release_t"] is None:
        return []
    return [o for o in strokes
            if o is not stroke
            and stroke["press_t"] < o["press_t"] < stroke["release_t"]]


def suspicion(stroke, rolled, next_letter, tapping_term):
    """Heuristic score for 'this mod-tap fired when a tap was intended'.

    With permissive/chordal hold disabled, every hold was physically held past
    the tapping term, so a misfire now looks like a hold only *just* over the
    term that overlapped the next key (a fast roll that tipped over the line).
    A hold well past the term is almost certainly a deliberate chord, not a slip.
    """
    if stroke["resolved"] != "hold" or stroke["mod"] in (None, "Layer"):
        return 0, ""
    dwell = stroke["dwell"]
    why = [f"{stroke['mod']} hold on {stroke['letter']}"]
    if dwell is None:
        score = 1
    elif dwell <= tapping_term + 70:
        score = 3 if rolled else 2
        why.append(f"barely over the {tapping_term}ms term ({dwell}ms)")
    elif dwell >= tapping_term + 130:
        score = 0
        why.append(f"long {dwell}ms hold — likely a deliberate chord")
    else:
        score = 2 if rolled else 1
        why.append(f"{dwell}ms hold")
    if rolled and score > 0:
        why.append(f"rolled into {','.join(r['letter'] for r in rolled)}")
    # C-t is the user's Emacs leader: a Ctrl hold into 't' is likely intentional.
    if stroke["mod"] == "Ctrl" and next_letter == "T":
        score -= 3
        why.append("(likely C-t leader)")
    return max(score, 0), "; ".join(why)


def fmt_stroke(s):
    dwell = f"{s['dwell']:>4}ms" if s["dwell"] is not None else "  ?  "
    tag = {"hold": "HOLD", "tap": "tap ", "plain": "    "}[s["resolved"]]
    mod = f" {s['mod']}" if s["resolved"] == "hold" and s["mod"] else ""
    return f"{s['letter']:<10} {tag}{mod:<6} {dwell}"


def report(strokes, marks, marker_kcs, args):
    presses = strokes
    p = print
    span = (presses[-1]["press_t"] - presses[0]["press_t"]) / 1000 if presses else 0

    p("=" * 66)
    p("QMK keylog analysis")
    p("=" * 66)
    p(f"key strokes : {len(presses)}")
    p(f"markers     : {len(marks)}")
    p(f"active span : {span:.0f} s (device timer, wrap-corrected)")
    if marker_kcs:
        p(f"marker kc   : {', '.join(sorted(marker_kcs))} (auto-detected, excluded)")

    # --- key frequency (a rough heatmap) --------------------------------
    freq = Counter(s["letter"] for s in presses)
    p("\n" + "-" * 66)
    p("Most-pressed keys")
    p("-" * 66)
    for letter, n in freq.most_common(15):
        p(f"  {letter:<12} {n}")

    # --- tap/hold resolution per tap-hold key ---------------------------
    th_tap = Counter()
    th_hold = Counter()
    th_dwell = defaultdict(list)
    for s in presses:
        if not s["is_th"]:
            continue
        key = (s["letter"], s["mod"])
        if s["resolved"] == "hold":
            th_hold[key] += 1
            if s["dwell"] is not None:
                th_dwell[key].append(s["dwell"])
        elif s["resolved"] == "tap":
            th_tap[key] += 1
    p("\n" + "-" * 66)
    p("Tap-hold keys: tap vs hold resolution")
    p("-" * 66)
    p(f"  {'key':<10}{'mod':<7}{'taps':>6}{'holds':>7}{'med hold dwell':>16}")
    for key in sorted(set(th_tap) | set(th_hold), key=lambda k: -th_hold[k]):
        letter, mod = key
        dwell = th_dwell[key]
        med = f"{int(statistics.median(dwell))}ms" if dwell else "-"
        p(f"  {letter:<10}{str(mod or ''):<7}{th_tap[key]:>6}{th_hold[key]:>7}{med:>16}")

    # --- corrections (backspace / delete bursts) ------------------------
    corr = Counter()
    for i, s in enumerate(presses):
        if s["letter"] in ("BSPC", "DEL", "DELETE", "BSPACE") and i > 0:
            corr[presses[i - 1]["letter"]] += 1
    if corr:
        p("\n" + "-" * 66)
        p("Keys most often deleted right after being typed")
        p("-" * 66)
        for letter, n in corr.most_common(12):
            p(f"  {letter:<12} {n}")

    # --- marker windows (the ground truth) ------------------------------
    p("\n" + "-" * 66)
    p(f"Marked mistakes: the {args.window_keys} keys / {args.window_ms}ms before each MARK")
    p("-" * 66)
    culprits = Counter()
    for k, mt in enumerate(marks, 1):
        window = [s for s in presses if mt - args.window_ms <= s["press_t"] <= mt]
        window = window[-args.window_keys:]
        seq = " ".join(
            f"[{s['mod']}-{s['letter']}]" if s["resolved"] == "hold" else s["letter"]
            for s in window
        )
        p(f"\n  MARK #{k}:  {seq or '(no keys in window)'}")
        best = None
        for j, s in enumerate(window):
            nxt = window[j + 1]["letter"] if j + 1 < len(window) else ""
            rolled = overlaps(s, presses)
            score, why = suspicion(s, rolled, nxt, args.tapping_term)
            flag = ""
            if why:
                flag = f"   <-- SUSPECT: {why}" if score >= 2 else f"   ({why})"
            if score >= 2 and (best is None or score > best[0]):
                best = (score, s, why)
            p(f"      {fmt_stroke(s)}{flag}")
        if best:
            _, s, why = best
            culprits[(s["letter"], s["mod"])] += 1
            p(f"    => likely culprit: {why}")
        else:
            p("    => no fast-roll mod misfire here — likely a plain typo or a")
            p("       deliberate chord (read the sequence above).")

    if culprits:
        p("\n" + "-" * 66)
        p("Suspected misfire culprits across all markers (ranked)")
        p("-" * 66)
        for (letter, mod), n in culprits.most_common():
            p(f"  {letter:<10}{str(mod or ''):<7} {n}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("logfile", help="QMK console log captured with keylog.sh / qmk console")
    ap.add_argument("--window-ms", type=int, default=2500,
                    help="lookback window before each MARK (default 2500)")
    ap.add_argument("--window-keys", type=int, default=12,
                    help="max keys to show before each MARK (default 12)")
    ap.add_argument("--tapping-term", type=int, default=215,
                    help="firmware TAPPING_TERM in ms; holds barely over it are suspect (default 215)")
    args = ap.parse_args()

    raw = add_monotonic(load(args.logfile))
    if not raw:
        sys.exit("No recognisable log lines found. Is this a QMK console capture?")
    strokes, marks, marker_kcs = build(raw)
    if not strokes:
        sys.exit("Parsed the file but found no key strokes to analyse.")
    report(strokes, marks, marker_kcs, args)


if __name__ == "__main__":
    main()

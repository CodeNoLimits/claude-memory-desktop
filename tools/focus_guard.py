#!/opt/homebrew/bin/python3
"""
focus_guard — filet de sécurité anti-vol-de-focus (2026-06-11, demande David).

Problème : les automations (Playwright/CDP/bringToFront/launch Chrome) volaient le
focus pendant que David tapait → texte perdu, apps fermées par des Cmd+Q aveugles.

Ce daemon surveille l'app frontmost (NSWorkspace, ZÉRO permission requise) :
  • "Chromium" / "Google Chrome for Testing" frontmost → cachés IMMÉDIATEMENT
    (ce sont toujours des navigateurs d'agents, David n'utilise jamais ces apps).
  • "Google Chrome Beta" frontmost → caché SEULEMENT si c'est l'instance agent :
    - sa fenêtre front est offscreen (x < -5000, le profil agent vit à -9999), ou
    - le check de position est impossible ET une instance avec le profil
      ~/.chrome-beta-cdp-profile tourne.
    Les fenêtres Chrome Beta NORMALES de David (à l'écran) ne sont JAMAIS touchées.
  • Chrome Canary / Antigravity / tout le reste = SACRÉ, jamais touché.

hide() rend le focus à l'app précédente instantanément (API AppKit, pas de
System Events, pas de permission Accessibility nécessaire pour le hide).

Chaque interception est loguée → ~/etz-chaim/daemons/logs/focus_guard.log
(pour identifier QUEL script a volé le focus : regarder l'heure et croiser).
"""
import os
import subprocess
import time
from datetime import datetime

from AppKit import NSWorkspace

LOG_PATH = os.path.expanduser("~/etz-chaim/daemons/logs/focus_guard.log")
# Navigateurs d'AGENTS = toujours cachés (David ne travaille QUE sur Chrome Canary, jamais ceux-ci).
# "Google Chrome" inclus depuis 2026-06-27 : il volait le focus car non couvert avant.
FORCE_HIDE = {"Google Chrome", "Chromium", "Google Chrome for Testing"}
BETA = "Google Chrome Beta"
AGENT_PROFILE_MARKER = "chrome-beta-cdp-profile"
POLL_SECONDS = 1.0


def log(msg: str) -> None:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(f"{datetime.now().isoformat(timespec='seconds')} {msg}\n")


def beta_agent_instance_running() -> bool:
    r = subprocess.run(["pgrep", "-f", AGENT_PROFILE_MARKER], capture_output=True)
    return r.returncode == 0


def beta_front_window_offscreen():
    """True = fenêtre agent (offscreen), False = fenêtre normale de David,
    None = indéterminé (pas de permission Accessibility ou pas de fenêtre)."""
    script = ('tell application "System Events" to tell process "Google Chrome Beta" '
              "to get position of front window")
    try:
        r = subprocess.run(["osascript", "-e", script],
                           capture_output=True, text=True, timeout=5)
        if r.returncode != 0:
            return None
        x = int(r.stdout.split(",")[0].strip())
        return x < -5000
    except Exception:
        return None


def main() -> None:
    log("focus_guard démarré (v2 : + Google Chrome ; sweep sur VISIBLE pas seulement frontmost ; poll 1.0s)")
    ws = NSWorkspace.sharedWorkspace()
    while True:
        try:
            # SWEEP : tout navigateur d'agent VISIBLE (même pas frontmost) → caché immédiatement.
            # .hide() (AppKit) rend le focus à l'app de David sans permission Accessibility.
            for app in ws.runningApplications():
                if app.isHidden():
                    continue
                nm = app.localizedName()
                if nm in FORCE_HIDE:
                    app.hide()
                    log(f"⛔ {nm} visible → caché (navigateur agent)")
                elif nm == BETA:
                    # Beta : caché si c'est l'instance agent (préserve une fenêtre Beta normale de David).
                    off = beta_front_window_offscreen()
                    if off is True or (off is None and beta_agent_instance_running()):
                        app.hide()
                        log("⛔ Google Chrome Beta (instance agent) visible → caché")
        except Exception as exc:  # le guard ne doit jamais mourir
            log(f"erreur: {exc}")
            time.sleep(5)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()

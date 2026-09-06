#!/usr/bin/env python3
"""Generate BetterDiscord themes from Gogh color schemes.

Reads data/themes-min.json (Gogh-Co/Gogh) and writes one self-contained
.theme.css per scheme into themes/dark/ or themes/light/.
"""
import colorsys
import json
import os
import re
import sys
import urllib.request

DATA_URL = "https://raw.githubusercontent.com/Gogh-Co/Gogh/master/data/themes-min.json"
DATA_FILE = "data/themes-min.json"

TEMPLATE = """/**
 * @name Gogh - {name}
 * @author {author}
 * @version 1.0.0
 * @description Gogh "{name}" terminal color scheme applied to BetterDiscord.
 * @source https://github.com/Gogh-Co/Gogh
 */
/* PALETTE */
:root, .theme-dark, .theme-light, .theme-darker, .theme-midnight {{
  --gogh-bg: {bg};
  --gogh-fg: {fg};
  --gogh-accent: {accent};
  --gogh-red: {c2};
  --gogh-green: {c3};
  --gogh-yellow: {c4};
  --gogh-blue: {c5};
  --gogh-magenta: {c6};
  --gogh-cyan: {c7};
  /* BACKGROUNDS */
  --background-primary: {bg1};
  --background-secondary: {bg2};
  --background-secondary-alt: {bg3};
  --background-tertiary: {bg4};
  --background-floating: {bg5};
  --background-mobile-primary: {bg1};
  --background-mobile-secondary: {bg2};
  --channeltextarea-background: {bg2};
  --background-message-hover: {bghover};
  --background-modifier-hover: {bghover};
  --background-modifier-active: {bgactive};
  --background-modifier-selected: {bgselected};
  --background-modifier-accent: {bgaccent};
  --scrollbar-thin-thumb: {bg4};
  --scrollbar-auto-thumb: {bg4};
  --scrollbar-auto-track: {bg2};
  /* TEXT */
  --text-normal: {fg};
  --text-muted: {muted};
  --text-link: {accent};
  --text-brand: {accent};
  --header-primary: {fg};
  --header-secondary: {muted};
  --interactive-normal: {muted};
  --interactive-hover: {fg};
  --interactive-active: {fg};
  --interactive-muted: {imuted};
  /* BRAND / ACCENT */
  --brand-experiment: {accent};
  --brand-experiment-500: {accent};
  --brand-experiment-560: {accent_darker};
  --brand-experiment-600: {accent_darker};
  --brand-500: {accent};
  --brand-560: {accent_darker};
  --brand-600: {accent_darker};
  /* STATUS */
  --online-color: {c3};
  --idle-color: {c4};
  --dnd-color: {c2};
  --streaming-color: {c6};
  --status-green: {c3};
  --status-yellow: {c4};
  --status-red: {c2};
  --status-purple: {c6};
}}"""


def clamp(v):
    return max(0, min(255, round(v)))


def mix(hex_color, target, pct):
    """Mix hex_color toward target (hex) by pct (0-100)."""
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    tr, tg, tb = (int(target[i:i + 2], 16) for i in (1, 3, 5))
    f = pct / 100.0
    return "#{:02x}{:02x}{:02x}".format(
        clamp(r + (tr - r) * f), clamp(g + (tg - g) * f), clamp(b + (tb - b) * f))


def saturation(hex_color):
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    _, _, _ = colorsys.rgb_to_hsv(r, g, b)
    return colorsys.rgb_to_hsv(r, g, b)[1]


def slug(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def build(theme):
    bg, fg = theme["background"], theme["foreground"]
    colors = [theme[f"color_{i:02d}"] for i in range(2, 8)]
    # Accent: most saturated ANSI color, avoid near-background noise
    accent = max(colors, key=saturation)
    if theme["variant"] == "dark":
        bg1 = bg                                  # chat area
        bg2 = mix(bg, "#000000", 4)               # sidebars / textarea
        bg3 = mix(bg, "#000000", 8)
        bg4 = mix(bg, "#000000", 14)              # deepest (server list)
        bg5 = mix(bg, "#ffffff", 6)               # popouts/floating
    else:
        bg1 = bg
        bg2 = mix(bg, "#000000", 4)
        bg3 = mix(bg, "#000000", 8)
        bg4 = mix(bg, "#000000", 14)
        bg5 = "#ffffff"
    muted = mix(fg, bg, 40)
    imuted = mix(fg, bg, 55)
    accent_darker = mix(accent, "#000000", 25)
    return TEMPLATE.format(
        name=theme["name"], author=theme.get("author") or "Gogh",
        bg=bg, fg=fg, accent=accent, c2=colors[0], c3=colors[1], c4=colors[2],
        c5=colors[3], c6=colors[4], c7=colors[5],
        bg1=bg1, bg2=bg2, bg3=bg3, bg4=bg4, bg5=bg5,
        bghover=mix(bg1, fg, 6) if theme["variant"] == "dark" else mix(bg1, "#000000", 4),
        bgactive=mix(bg1, fg, 10) if theme["variant"] == "dark" else mix(bg1, "#000000", 7),
        bgselected=mix(bg1, fg, 12) if theme["variant"] == "dark" else mix(bg1, "#000000", 9),
        bgaccent=mix(fg, bg, 85), muted=muted, imuted=imuted,
        accent_darker=accent_darker,
    )


def main():
    try:
        with open(DATA_FILE) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"{DATA_FILE} not found, downloading from {DATA_URL}")
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        urllib.request.urlretrieve(DATA_URL, DATA_FILE)
        with open(DATA_FILE) as f:
            data = json.load(f)

    for theme in data:
        variant = theme["variant"]
        if variant not in ("dark", "light"):
            sys.exit(f"unknown variant {variant!r} for {theme['name']}")
        path = f"themes/{variant}/gogh_{slug(theme['name'])}.css"
        with open(path, "w") as f:
            f.write(build(theme))
    print(f"wrote {len(data)} themes")


if __name__ == "__main__":
    main()
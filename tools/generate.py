#!/usr/bin/env python3
"""Generate BetterDiscord themes from Gogh color schemes.

Reads data/themes-min.json (Gogh-Co/Gogh) and writes one self-contained
.theme.css per scheme into themes/dark/ or themes/light/.
Only the theme's own 16 palette colors (+ foreground) are used - no
synthesized shades.
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
 * @version 1.1.0
 * @description Gogh "{name}" terminal color scheme applied to BetterDiscord.
 * @source https://github.com/Gogh-Co/Gogh
 */
/* FULL PALETTE - all 16 Gogh colors, exposed for reuse */
:root, .theme-dark, .theme-light, .theme-darker, .theme-midnight {{
  --gogh-color-01: {c01}; /* background */
  --gogh-color-02: {c02}; /* red */
  --gogh-color-03: {c03}; /* green */
  --gogh-color-04: {c04}; /* yellow */
  --gogh-color-05: {c05}; /* blue */
  --gogh-color-06: {c06}; /* magenta */
  --gogh-color-07: {c07}; /* cyan */
  --gogh-color-08: {c08}; /* white (normal) */
  --gogh-color-09: {c09}; /* bright black (surface tone) */
  --gogh-color-10: {c10}; /* bright red */
  --gogh-color-11: {c11}; /* bright green */
  --gogh-color-12: {c12}; /* bright yellow */
  --gogh-color-13: {c13}; /* bright blue */
  --gogh-color-14: {c14}; /* bright magenta */
  --gogh-color-15: {c15}; /* bright cyan */
  --gogh-color-16: {c16}; /* bright white (text) */
  /* BACKGROUNDS - 2025 visual refresh vars */
  --background-base-lowest: {surface};
  --background-base-lower: {chat};
  --background-base-lower-alt: {surface};
  --background-base-low: {surface};
  --background-base-medium: {surface};
  --background-base-high: {chat};
  --background-base-higher: {floating};
  --background-base-highest: {floating};
  --background-nested-floating: {floating};
  --bg-overlay-chat: {chat};
  --bg-overlay-home: {surface};
  --bg-overlay-home-card: {chat};
  --bg-overlay-app-frame: {chat};
  --bg-overlay-1: {chat};
  --bg-overlay-2: {chat};
  --bg-overlay-3: {chat};
  --bg-overlay-4: {surface};
  --bg-overlay-5: {surface};
  --bg-overlay-6: {floating};
  --bg-overlay-color: {rgb01};
  /* BACKGROUNDS - legacy vars */
  --background-primary: {chat};
  --background-secondary: {surface};
  --background-secondary-alt: {surface};
  --background-tertiary: {surface};
  --background-floating: {floating};
  --background-mobile-primary: {chat};
  --background-mobile-secondary: {surface};
  --channeltextarea-background: {surface};
  --background-message-hover: {surface};
  --background-modifier-hover: {surface};
  --background-modifier-active: {surface};
  --background-modifier-selected: {surface};
  --background-modifier-accent: {text_dim};
  --background-mentioned: {mention_bg};
  --background-mentioned-hover: {mention_bg};
  --mention-foreground: {accent};
  --scrollbar-thin-thumb: {text_dim};
  --scrollbar-auto-thumb: {text_dim};
  --scrollbar-auto-track: {chat};
  /* TEXT */
  --text-normal: {text};
  --text-default: {text};
  --text-muted: {text_dim};
  --text-low-contrast: {text_dim};
  --text-link: {link};
  --text-brand: {accent};
  --text-positive: {c03};
  --text-positive-hover: {c11};
  --text-feedback-positive: {c03};
  --text-danger: {c02};
  --text-danger-hover: {c10};
  --text-warning: {c04};
  --text-warning-hover: {c12};
  --text-info: {c07};
  --text-info-hover: {c15};
  --header-primary: {text_emph};
  --header-secondary: {text_dim};
  --interactive-normal: {text_norm};
  --interactive-hover: {text_emph};
  --interactive-active: {text_emph};
  --interactive-muted: {text_dim};
  --interactive-text-default: {text_dim};
  --interactive-text-hover: {text_emph};
  --interactive-text-active: {text_emph};
  --channels-default: {text_norm};
  /* BRAND / ACCENT */
  --accent: {accent};
  --brand-experiment: {accent};
  --brand-experiment-500: {accent};
  --brand-experiment-560: {accent};
  --brand-experiment-600: {accent};
  --brand-500: {accent};
  --brand-560: {accent};
  --brand-600: {accent};
  --brand-700: {accent};
  /* STATUS */
  --online-color: {c03};
  --idle-color: {c04};
  --dnd-color: {c02};
  --streaming-color: {c06};
  --status-online: {c03};
  --status-idle: {c04};
  --status-dnd: {c02};
  --status-streaming: {c06};
}}

/* APP SHELL - refresh base layer + guild sidebar paint over stock colors */
[class*="-baseLayer"] > [class*="-container"],
nav[class*="guilds"] {{
  background: {chat} !important;
}}"""


def rgb_triplet(hex_color):
    return " ".join(str(int(hex_color[i:i + 2], 16)) for i in (1, 3, 5))


def saturation(hex_color):
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return colorsys.rgb_to_hsv(r, g, b)[1]


def slug(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def build(theme):
    colors = {f"c{i:02d}": theme[f"color_{i:02d}"] for i in range(1, 17)}
    bg = theme["background"]
    # Accent: most saturated ANSI color
    accent = max((theme[f"color_{i:02d}"] for i in range(2, 8)), key=saturation)
    # Terminal roles flip between variants: in dark schemes color_09 (bright
    # black) is a gray surface tone; in light schemes color_08/color_16 are
    # paper tones and color_01/09 are dark text tones. Map accordingly.
    if theme["variant"] == "dark":
        roles = dict(
            chat=bg, surface=colors["c09"], floating=colors["c09"],
            text=theme["foreground"], text_emph=colors["c16"],
            text_dim=colors["c09"], text_norm=colors["c08"],
            link=colors["c13"], mention_bg=colors["c09"],
        )
    else:
        roles = dict(
            chat=bg, surface=colors["c08"], floating=colors["c16"],
            text=theme["foreground"], text_emph=colors["c01"],
            text_dim=colors["c09"], text_norm=colors["c09"],
            link=colors["c05"], mention_bg=colors["c08"],
        )
    return TEMPLATE.format(
        name=theme["name"], author=theme.get("author") or "Gogh",
        accent=accent, rgb01=rgb_triplet(roles["surface"]), **roles, **colors)


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
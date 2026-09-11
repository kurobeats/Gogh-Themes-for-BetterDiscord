#!/usr/bin/env python3
"""Generate BetterDiscord themes from Gogh color schemes.

Reads data/themes-min.json (Gogh-Co/Gogh) and writes one self-contained
.theme.css per scheme into themes/dark/ or themes/light/.

Mapping follows the catppuccin/discord themes (github.com/catppuccin/discord):
- layered surface ladder synthesized from the scheme background (subtle steps,
  chat = scheme background; outermost frame darkest, popouts contrast),
- text and surfaces always far apart in luminance (muted text is never a
  surface color),
- hover/active/selected as translucent overlays with escalating alpha,
- accent with hover/active shades and auto-contrasted on-accent text.
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
 * @version 1.2.0
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
  /* SURFACE LADDER - outermost frame darkest, popouts contrast (catppuccin style) */
  --background-base-lowest: {lowest};
  --background-base-lower: {lower};
  --background-base-lower-alt: {surface};
  --background-base-low: {low};
  --background-base-medium: {surface};
  --background-base-high: {chat};
  --background-base-higher: {higher};
  --background-base-highest: {highest};
  --background-nested-floating: {floating};
  --app-frame-background: {lowest};
  --__header-bar-background: {lower};
  --bg-overlay-chat: {chat};
  --bg-overlay-home: {chat};
  --bg-overlay-home-card: {surface};
  --bg-overlay-app-frame: {lowest};
  --bg-overlay-1: {chat};
  --bg-overlay-2: {surface};
  --bg-overlay-3: {surface};
  --bg-overlay-4: {surface};
  --bg-overlay-5: {floating};
  --bg-overlay-6: {floating};
  --bg-overlay-color: {rgb_surface};
  --modal-background: {chat};
  --modal-footer-background: {surface};
  /* BACKGROUNDS - legacy vars */
  --background-primary: {chat};
  --background-secondary: {surface};
  --background-secondary-alt: {surface};
  --background-tertiary: {low};
  --background-floating: {floating};
  --background-mobile-primary: {chat};
  --background-mobile-secondary: {surface};
  --channeltextarea-background: {surface};
  --background-message-hover: {msg_hover};
  --background-modifier-hover: {mod_hover};
  --background-modifier-active: {mod_active};
  --background-modifier-selected: {mod_selected};
  --background-modifier-accent: {c09};
  --background-mentioned: {mention_bg};
  --background-mentioned-hover: {mention_bg};
  --mention-foreground: {accent};
  --scrollbar-thin-thumb: {scrollbar};
  --scrollbar-auto-thumb: {scrollbar};
  --scrollbar-auto-track: {lowest};
  /* TEXT */
  --text-normal: {text};
  --text-default: {text};
  --text-strong: {text_emph};
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
  --interactive-text-default: {text_norm};
  --interactive-text-hover: {text_emph};
  --interactive-text-active: {text_emph};
  --channels-default: {text_norm};
  /* BRAND / ACCENT */
  --accent: {accent};
  --brand-experiment: {accent};
  --brand-experiment-500: {accent};
  --brand-experiment-560: {accent_hover};
  --brand-experiment-600: {accent_hover};
  --brand-500: {accent};
  --brand-560: {accent_hover};
  --brand-600: {accent_hover};
  --brand-700: {accent_active};
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

/* ACCENT BUTTONS - text on accent auto-contrasted (dark on light accents) */
button[class*="lookFilled_"][class*="colorBrand_"] {{ color: {on_accent} !important; }}
button[class*="lookFilled_"][class*="colorGreen_"] {{ color: {on_positive} !important; }}
button[class*="lookFilled_"][class*="colorRed_"] {{ color: {on_danger} !important; }}

/* APP SHELL - refresh base layer + guild sidebar paint over stock colors */
[class*="-baseLayer"] > [class*="-container"],
nav[class*="guilds"] {{
  background: {chat} !important;
}}"""


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


def to_rgb(hex_color):
    return tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))


def to_hex(rgb):
    return "#%02X%02X%02X" % rgb


def mix(hex_a, hex_b, t):
    """Blend hex_a toward hex_b by fraction t."""
    a, b = to_rgb(hex_a), to_rgb(hex_b)
    return to_hex(tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3)))


def rgb_triplet(hex_color):
    return " ".join(str(v) for v in to_rgb(hex_color))


def luminance(hex_color):
    def chan(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = to_rgb(hex_color)
    return 0.2126 * chan(r) + 0.7152 * chan(g) + 0.0722 * chan(b)


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def saturation(hex_color):
    r, g, b = (v / 255 for v in to_rgb(hex_color))
    return colorsys.rgb_to_hsv(r, g, b)[1]


def on_color(fg):
    """Pick black-ish or white text with the better contrast against fg."""
    return to_hex(BLACK) if contrast(fg, to_hex(BLACK)) >= contrast(fg, to_hex(WHITE)) else to_hex(WHITE)


def readable(cand, bg):
    """cand if readable on chat, else the scheme foreground."""
    return cand if contrast(cand, bg) >= 3.0 else None


def best_text(cands, bg):
    """Most readable candidate; black/white if none is (bad schemes exist)."""
    best = max(cands, key=lambda c: contrast(c, bg))
    return best if contrast(best, bg) >= 3.0 else on_color(bg)


def slug(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def build(theme):
    colors = {f"c{i:02d}": theme[f"color_{i:02d}"] for i in range(1, 17)}
    bg = theme["background"]
    accent = max((theme[f"color_{i:02d}"] for i in range(2, 8)), key=saturation)
    text = best_text([theme["foreground"], colors["c16"], colors["c08"]], bg)
    norm = readable(colors["c08" if theme["variant"] == "dark" else "c09"], bg) or text
    surface = mix(bg, "#000000", 0.05 if theme["variant"] == "dark" else 0.045)
    dim = mix(norm, bg, 0.25 if theme["variant"] == "dark" else 0.12)
    if contrast(dim, surface) < 2.0:
        dim = norm  # never let muted text sink into the surface
    # Surface ladder synthesized from the scheme background (catppuccin's
    # crust/mantle/base/overlay idea, works for any scheme). Dark and light
    # variants mirror each other: chat stays the scheme background, sidebars
    # and the textarea step slightly away from it, popouts contrast.
    if theme["variant"] == "dark":
        ladder = dict(
            chat=bg,
            surface=surface,
            low=mix(bg, "#000000", 0.10),
            lower=mix(bg, "#000000", 0.20),
            lowest=mix(bg, "#000000", 0.35),
            higher=mix(bg, "#FFFFFF", 0.07),
            highest=mix(bg, "#FFFFFF", 0.11),
            floating=mix(bg, "#FFFFFF", 0.11),
            text=text,
            text_emph=readable(colors["c16"], bg) or text,
            text_dim=dim,
            text_norm=norm,
            link=colors["c13"],
        )
    else:
        ladder = dict(
            chat=bg,
            surface=surface,
            low=mix(bg, "#000000", 0.09),
            lower=mix(bg, "#000000", 0.15),
            lowest=mix(bg, "#000000", 0.25),
            higher=mix(bg, "#FFFFFF", 0.04),
            highest=mix(bg, "#FFFFFF", 0.08),
            floating=mix(bg, "#FFFFFF", 0.08),
            text=text,
            text_emph=readable(colors["c01"], bg) or text,
            text_dim=dim,
            text_norm=norm,
            link=colors["c05"],
        )
    roles = dict(
        ladder,
        accent=accent,
        accent_hover=mix(accent, "#000000", 0.15),
        accent_active=mix(accent, "#000000", 0.30),
        on_accent=on_color(accent),
        on_positive=on_color(colors["c03"]),
        on_danger=on_color(colors["c02"]),
        msg_hover=f"rgba({rgb_triplet(ladder['lowest'])}, 0.3)",
        mod_hover=f"rgba({rgb_triplet(colors['c09'])}, 0.10)",
        mod_active=f"rgba({rgb_triplet(colors['c09'])}, 0.20)",
        mod_selected=f"rgba({rgb_triplet(colors['c09'])}, 0.30)",
        mention_bg=f"rgba({rgb_triplet(accent)}, 0.3)",
        scrollbar=f"rgba({rgb_triplet(colors['c09'])}, 0.4)",
        rgb_surface=rgb_triplet(ladder["surface"]),
    )
    return TEMPLATE.format(name=theme["name"], author=theme.get("author") or "Gogh",
                           **roles, **colors)


def check(theme, css):
    """Fail loudly if a generated theme would be unreadable."""
    chat = theme["background"]
    surface = mix(chat, "#000000", 0.045 if theme["variant"] == "light" else 0.05)
    for var, bg in (("--text-normal:", chat), ("--header-primary:", chat),
                    ("--text-muted:", surface), ("--interactive-text-default:", surface),
                    ("--channels-default:", surface)):
        val = re.search(rf"{re.escape(var)} (#[0-9A-Fa-f]+)", css).group(1)
        assert val.upper() != surface.upper(), f"{theme['name']}: {var} equals surface"
        assert contrast(val, bg) >= 2.0, f"{theme['name']}: {var} unreadable on {bg}"


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
        css = build(theme)
        check(theme, css)
        path = f"themes/{variant}/gogh_{slug(theme['name'])}.css"
        with open(path, "w") as f:
            f.write(css)
    print(f"wrote {len(data)} themes")


if __name__ == "__main__":
    main()
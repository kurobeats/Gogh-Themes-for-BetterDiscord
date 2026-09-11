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
  --background-surface-high: {chat};
  --background-surface-higher: {higher};
  --background-surface-highest: {highest};
  --bg-surface-raised: {surface};
  --background-gradient-highest: {low};
  --home-background: {chat};
  --chat-background: {chat};
  --chat-background-default: {chat};
  --chat-text-muted: {text_dim};
  --chat-border: {lowest};
  --border-normal: {lowest};
  --border-strong: {surface};
  --border-muted: {highest};
  --border-subtle: {chat};
  --background-mod-muted: {mod_05};
  --background-mod-normal: {mod_15};
  --background-mod-subtle: {mod_25};
  --background-mod-strong: {mod_45};
  --background-code: {chat};
  --input-background-default: {lowest};
  --input-text-default: {text};
  --input-placeholder-text-default: {text_dim};
  --input-border-default: {c09};
  --channel-text-area-placeholder: {placeholder};
  --channel-icon: {text_norm};
  --icon-default: {text};
  --icon-strong: {text_emph};
  --icon-subtle: {text_dim};
  --interactive-icon-default: {text};
  --interactive-icon-hover: {text_emph};
  --interactive-icon-active: {text_emph};
  --message-background-hover: {msg_hover};
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
{ramp}
  /* CONTROLS */
  --control-primary-background-default: {accent};
  --control-primary-background-hover: {accent_hover};
  --control-primary-background-active: {accent_active};
  --control-secondary-background-default: {c09};
  --control-secondary-background-hover: {control_hover};
  --control-secondary-background-active: {control_active};
  --control-secondary-border-default: {control_border};
  --control-secondary-text-default: {text};
  --control-secondary-text-hover: {text};
  --control-brand-foreground: {accent};
  --control-brand-foreground-new: {accent};
  --control-critical-primary-background-default: {c02};
  --control-critical-primary-background-hover: {c02_hover};
  --control-critical-primary-background-active: {c02_active};
  --control-critical-primary-text-default: {on_danger};
  --control-critical-primary-text-hover: {on_danger};
  --control-critical-secondary-background-default: transparent;
  --control-critical-secondary-background-hover: {c02_hover};
  --control-critical-secondary-background-active: {c02_active};
  --control-critical-secondary-border-default: {c02};
  --control-critical-secondary-border-hover: {c02_hover};
  --control-critical-secondary-border-active: {c02_hover};
  --control-critical-secondary-text-default: {text};
  --control-critical-secondary-text-hover: {text};
  --control-critical-secondary-text-active: {text};
  --control-connected-background-default: {c03};
  --control-connected-background-hover: {c03_hover};
  --control-connected-background-active: {c03_active};
  --control-connected-border-default: {c03};
  --control-connected-border-hover: {c03_hover};
  --control-connected-border-active: {c03_hover};
  --checkbox-icon-active: {on_accent};
  --checkbox-border-default: {c09};
  --radio-thumb-background-active: {on_accent};
  /* STATUS + FEEDBACK */
  --white: {text};
  --white-500: {text};
  --black-500: {lowest};
  --primary-100: {text_norm};
  --primary-200: {text_dim};
  --primary-300: {text_norm};
  --primary-400: {text_norm};
  --primary-630: {highest};
  --primary-700: {surface};
  --primary-800: {lowest};
  --green-360: {c03};
  --green-300: {c03};
  --yellow-360: {c04};
  --yellow-300: {c04};
  --red-400: {c02};
  --red-430: {c02_hover};
  --red-500: {c02_active};
  --blue-500: {accent_hover};
  --blue-530: {accent_active};
  --blurple-50: {accent};
  --blurple-60: {accent_hover};
  --status-positive: {c03};
  --status-positive-background: {c03};
  --status-positive-text: {on_positive};
  --status-warning: {c04};
  --status-warning-background: {c04};
  --status-warning-text: {on_warning};
  --status-danger: {c02};
  --online-color: {c03};
  --idle-color: {c04};
  --dnd-color: {c02};
  --streaming-color: {c06};
  --status-online: {c03};
  --status-idle: {c04};
  --status-dnd: {c02};
  --status-streaming: {c06};
  --text-status-online: {c03};
  --text-status-idle: {c04};
  --text-status-dnd: {c02};
  --text-status-offline: {text_dim};
  --icon-status-online: {c03};
  --icon-status-idle: {c04};
  --icon-status-dnd: {c02};
  --icon-status-offline: {text_dim};
  --icon-muted: {text_dim};
  --icon-voice-muted: {c02};
  --badge-notification-background: {c02};
  --badge-text-brand: {on_accent};
  --text-feedback-positive: {c03};
  --text-feedback-critical: {c02};
  --text-feedback-warning: {c04};
  --text-feedback-info: {accent};
  --background-feedback-positive: {feedback_positive};
  --background-feedback-critical: {feedback_danger};
  --background-feedback-warning: {feedback_warning};
  --background-feedback-info: {feedback_info};
  --background-feedback-notification: {c02};
  --icon-feedback-positive: {c03};
  --icon-feedback-critical: {c02};
  --icon-feedback-warning: {c04};
  --icon-feedback-info: {accent};
  --icon-feedback-notification: {c02};
  --notice-background-critical: {c02};
  --notice-background-info: {accent};
  --notice-background-positive: {c03};
  --notice-background-warning: {c04};
  --notice-text-critical: {on_danger};
  --notice-text-info: {on_accent};
  --notice-text-positive: {on_positive};
  --notice-text-warning: {on_warning};
  --mention-background: {mention_bg};
  --message-reacted-background-default: {mention_bg};
  --message-reacted-text-default: {accent};
  --message-mentioned-background-default: {mentioned_msg};
  --message-mentioned-background-hover: {mentioned_msg};
  --message-highlight-background-default: {highlight};
  --message-highlight-background-hover: {highlight};
  --message-automod-background-default: {automod};
  --message-automod-background-hover: {automod};
  --text-subtle: {text_norm};
  --logo-primary: {text};
  --textbox-markdown-syntax: {c09};
  --spoiler-revealed-background: {highest};
  --spoiler-hidden-background: {c09};
  --background-accent: {c09};
  --card-background-default: {highest};
  --user-profile-overlay-background: {surface};
  --user-profile-overlay-background-hover: {highest};
  --custom-channel-members-bg: {surface};
  --custom-status-bubble-background: {lowest};
  --custom-status-bubble-background-color: {surface};
  --plum-23: {chat};
  --thread-core: {text};
  --thread-default: {text_norm};
  --thread-muted: {text_dim};
  --thread-spine: {c09};
  --spine-default: {c09};
  --hidden: {c09};
  --scrollbar-thin-track: transparent;
  --interactive-background-hover: {interactive_hover};
  --interactive-background-selected: {interactive_selected};
  --interactive-background-active: {interactive_active};
  --button-outline-primary-text: {text};
  --button-outline-brand-text: {text};
  --button-outline-brand-background-hover: {accent_hover};
  --button-outline-brand-border-active: {accent_hover};
  --twitch: {c06};
  --playstation: {c13};
  --spotify: {c03};
  --guild-boosting-pink: {c06};
  --guild-boosting-blue: {accent};
  --guild-boosting-purple: {boost_purple};
  --premium-perk-yellow: {c04};
  --premium-perk-purple: {c06};
  --premium-perk-dark-blue: {c13};
  --premium-perk-light-blue: {c15};
  --premium-perk-blue: {accent};
  --premium-perk-green: {c03};
  --premium-perk-pink: {c06};
  --premium-perk-orange: {perk_orange};
  --premium-tier-0-blue: {accent};
  --premium-tier-0-purple: {c06};
  --premium-tier-1-blue-for-gradients: {c13};
  --premium-tier-1-dark-blue-for-gradients: {accent};
  --premium-tier-2-purple-for-gradients: {c06};
  --premium-tier-2-purple-for-gradients-2: {boost_purple};
  --premium-tier-2-pink-for-gradients: {c06};
  --scrollbar-auto-scrollbar-color-thumb: {scrollbar};
  --scrollbar-auto-scrollbar-color-track: {lowest};
}}

::selection {{
  background-color: rgba({rgb_accent}, 0.6);
}}

/* ACCENT BUTTONS - text on accent auto-contrasted (dark on light accents) */
button[class*="lookFilled_"][class*="colorBrand_"] {{ color: {on_accent} !important; --white: {on_accent}; --white-500: {on_accent}; }}
button[class*="lookFilled_"][class*="colorGreen_"] {{ color: {on_positive} !important; --white: {on_positive}; }}
button[class*="lookFilled_"][class*="colorRed_"] {{ color: {on_danger} !important; --white: {on_danger}; }}

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


def rgb_list(hex_color):
    return ",".join(str(v) for v in to_rgb(hex_color))


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
    ladder_lowest = ladder["lowest"]
    roles = dict(
        ladder,
        accent=accent,
        accent_hover=mix(accent, "#000000", 0.15),
        accent_active=mix(accent, "#000000", 0.30),
        on_accent=on_color(accent),
        on_positive=on_color(colors["c03"]),
        on_danger=on_color(colors["c02"]),
        on_warning=on_color(colors["c04"]),
        c02_hover=mix(colors["c02"], "#000000", 0.15),
        c02_active=mix(colors["c02"], "#000000", 0.30),
        c03_hover=mix(colors["c03"], "#000000", 0.15),
        c03_active=mix(colors["c03"], "#000000", 0.30),
        control_hover=mix(colors["c09"], bg, 0.25),
        control_active=mix(colors["c09"], bg, 0.45),
        control_border=mix(colors["c09"], ladder_lowest, 0.5),
        feedback_positive=f"rgba({rgb_list(colors['c03'])}, 0.15)",
        feedback_danger=f"rgba({rgb_list(colors['c02'])}, 0.15)",
        feedback_warning=f"rgba({rgb_list(colors['c04'])}, 0.15)",
        feedback_info=f"rgba({rgb_list(accent)}, 0.15)",
        mentioned_msg=f"rgba({rgb_list(colors['c04'])}, 0.1)",
        highlight=f"rgba({rgb_list(accent)}, 0.08)",
        automod=f"rgba({rgb_list(colors['c09'])}, 0.05)",
        rgb_accent=rgb_triplet(accent),
        interactive_hover=f"rgba({rgb_list(colors['c09'])}, 0.15)",
        interactive_selected=f"rgba({rgb_list(colors['c09'])}, 0.25)",
        interactive_active=f"rgba({rgb_list(ladder['text'])}, 0.17)",
        boost_purple=mix(colors["c06"], colors["c13"], 0.5),
        perk_orange=mix(colors["c04"], colors["c02"], 0.4),
        ramp="\n".join(
            f"  --brand-{shade}: {mix(accent, '#FFFFFF' if int(shade[0]) <= 4 else '#000000', step)};"
            for shade, step in [("100", .85), ("130", .78), ("160", .70), ("200", .62),
                                ("230", .55), ("260", .47), ("300", .38), ("330", .30),
                                ("360", .20), ("400", .10), ("430", .05), ("460", .03),
                                ("530", .08), ("630", .22), ("660", .28), ("730", .38),
                                ("760", .45), ("800", .50), ("830", .58), ("860", .65), ("900", .72)]
        ) + "\n" + "\n".join(
            f"  --brand-{a}: rgba({rgb_list(accent)}, {alpha});"
            for a, alpha in [(f"{n:02d}a", n / 100) for n in range(5, 100, 5)]
        ) + "\n" + "\n".join(
            f"  --opacity-blurple-{n}: rgba({rgb_list(accent)}, {alpha});"
            for n, alpha in [("8", .08), ("16", .16), ("24", .24), ("32", .32), ("60", .60)]
        ),
        msg_hover=f"rgba({rgb_list(ladder['lowest'])}, 0.3)",
        mod_hover=f"rgba({rgb_list(colors['c09'])}, 0.10)",
        mod_active=f"rgba({rgb_list(colors['c09'])}, 0.20)",
        mod_selected=f"rgba({rgb_list(colors['c09'])}, 0.30)",
        mod_05=f"rgba({rgb_list(colors['c09'])}, 0.05)",
        mod_15=f"rgba({rgb_list(colors['c09'])}, 0.15)",
        mod_25=f"rgba({rgb_list(colors['c09'])}, 0.25)",
        mod_45=f"rgba({rgb_list(colors['c09'])}, 0.45)",
        placeholder=f"rgba({rgb_list(ladder['text'])}, 0.5)",
        mention_bg=f"rgba({rgb_list(accent)}, 0.3)",
        scrollbar=f"rgba({rgb_list(colors['c09'])}, 0.4)",
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
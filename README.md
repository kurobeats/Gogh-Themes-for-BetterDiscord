# Gogh Themes for BetterDiscord

Every color scheme from [Gogh](https://gogh.website/) — a collection of 1200+
terminal color schemes — ported to [BetterDiscord](https://betterdiscord.app/)
themes. One self-contained `.css` file per scheme.

## Structure

```
themes/
├── dark/   # 964 themes for Discord's dark mode  (gogh_<theme_name>.css)
└── light/  # 265 themes for Discord's light mode (gogh_<theme_name>.css)
```

- `themes/dark/` — Gogh schemes with the `dark` variant (use with Discord's dark theme).
- `themes/light/` — Gogh schemes with the `light` variant (use with Discord's light theme).
- `data/themes-min.json` — Gogh's palette data (downloaded from [Gogh-Co/Gogh](https://github.com/Gogh-Co/Gogh/tree/master/data) at generation time).
- `tools/generate.py` — generator script; rerun to regenerate everything.

## Install

1. Copy the `gogh_<name>.css` file you want into your BetterDiscord themes folder
   (`Settings → Themes → Open Theme Folder`, or `~/.config/BetterDiscord/themes` on Linux).
2. Enable it under `Settings → Themes`.
3. Match Discord's built-in appearance to the theme's folder: themes in
   `themes/dark/` look right with Discord's dark mode, `themes/light/` with light mode.

## How themes are built

Each file is self-contained (no external imports) and maps the Gogh palette
onto Discord's CSS variables:

| Gogh value            | Discord usage                                        |
| --------------------- | ---------------------------------------------------- |
| `background`          | app backgrounds (chat, sidebars, guild list, popouts) |
| `foreground`          | normal text, headers, interactive elements            |
| `color_02`–`color_07` | accent (most saturated ANSI color), status dot colors |
| variant (`dark`/`light`) | placement in `themes/dark/` or `themes/light/`     |

Each theme targets both the current (2025 visual refresh) Discord variables
(`--background-base-*`, `--bg-overlay-*`, `--text-default`,
`--interactive-text-*`) and the legacy set (`--background-primary`,
`--text-normal`, ...), so surfaces stay consistent across client versions.
The app shell (base layer + guild sidebar) is painted directly to cover stock
colors that don't route through a variable.

Each theme uses **only the scheme's own palette** — all 16 ANSI colors plus
`foreground` — no synthesized shades. Terminal roles flip with the variant:
in dark schemes `color_09` (bright black) is the surface tone, in light
schemes `color_08`/`color_16` (paper tones) take the surface role and
`color_01`/`color_09` become text tones.

| Gogh value                  | Discord usage                                                       |
| --------------------------- | ------------------------------------------------------------------- |
| `background` / `color_01`   | chat background (dark: chat + shell; light: chat)                   |
| `color_09` (dark schemes)   | sidebars, textarea, panels, hover states, dividers, scrollbars      |
| `color_08`/`color_16` (light)| sidebars/textarea (`color_08`), popouts/floating (`color_16`)      |
| `color_02`–`color_07`       | status dots (red/yellow/green/magenta), `--text-*` semantic colors  |
| `color_10`–`color_15`       | hover variants of the semantic text colors (danger/warning/info/positive) |
| `color_08` (dark) / `color_01`, `color_16` | muted text, interactive states, headers |
| `foreground`                | main text (`--text-normal`, `--text-default`)                       |
| most saturated of 02–07     | accent / brand color (`--brand-500`, mentions, buttons)             |
| variant (`dark`/`light`)    | placement in `themes/dark/` or `themes/light/`                      |

All 16 colors are also exposed as `--gogh-color-01` … `--gogh-color-16` for
custom snippets. Both the current (2025 visual refresh) Discord variables
(`--background-base-*`, `--bg-overlay-*`, `--text-default`) and the legacy set
(`--background-primary`, `--text-normal`, ...) are set. The app shell (base
layer + guild sidebar) is painted directly to cover stock colors that don't
route through a variable.

## Regenerating

```sh
python3 tools/generate.py
```

Downloads `data/themes-min.json` if missing, then rewrites every theme file.

## Credits

- Color schemes: [Gogh](https://gogh.website/) / [Gogh-Co/Gogh](https://github.com/Gogh-Co/Gogh)
- Theme structure follows the standard BetterDiscord theme header format
  (see [ClearVision](https://github.com/ClearVision/ClearVision-v7) for a full-featured example).
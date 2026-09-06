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
| `background`          | app backgrounds (chat, sidebars, server list, etc.)   |
| `foreground`          | normal text, headers, interactive elements            |
| `color_02`–`color_07` | accent (most saturated ANSI color), status dot colors |
| variant (`dark`/`light`) | placement in `themes/dark/` or `themes/light/`     |

Accent color is picked automatically as the most saturated ANSI color from the
scheme's palette; status colors (online/idle/dnd/streaming) reuse the scheme's
green/yellow/red/magenta.

## Regenerating

```sh
python3 tools/generate.py
```

Downloads `data/themes-min.json` if missing, then rewrites every theme file.

## Credits

- Color schemes: [Gogh](https://gogh.website/) / [Gogh-Co/Gogh](https://github.com/Gogh-Co/Gogh)
- Theme structure follows the standard BetterDiscord theme header format
  (see [ClearVision](https://github.com/ClearVision/ClearVision-v7) for a full-featured example).
# ExplorerTweaks README hero decision

This folder keeps the source material, rejected layout, selected final, and visual review evidence for the README hero.

## Inputs

- `README-before.md` preserves the README before the hero was integrated.
- `previous-social-card.png` is the earlier logo-and-tagline artwork. It remains useful as historical context, but it doesn't show the product.
- `selected-logo-source.png` is an exact copy of the approved folder-controls master.
- `current-run/` records the private-desktop app captures used for the initial audit.
- `current-run-v2.16.2/` records the five accepted private-desktop captures after the release bump. Capture mode used sample data and blocked system commands.

## Decision

`readme-hero-candidate-01.png` was rejected because its supporting sentence ran under the product frame and appeared clipped.

`readme-hero-candidate-02.png` fixed that layout fault. It became `readme-hero-final.png` and the production `assets/marketing/readme-hero.png`. The design uses the approved mark without redrawing it. The product frame comes from the real Appearance capture, cropped to omit the app's release label.

The final has clear type hierarchy, readable copy at GitHub widths, and direct product proof. It contains no release number. `comparison-old-vs-selected.png` shows the earlier and selected artwork at the same 2:1 ratio. The `responsive-review/` folder keeps the inspected 960 px and 640 px versions.

## Acceptance record

- Canvas: 1280 x 640 PNG, RGB, 179,889 bytes.
- Final SHA-256: `2c35c054fb18084ce851060fe5e208d81fb01b6f5c4693407ee0c6091f255ffc`.
- Approved logo SHA-256: `f655fa93a8d12c3676e1d070b893e7623c6f78a68311c5c504fc1685413bf27f`.
- Accepted Appearance capture SHA-256: `9504e8d7411385766a26fc93d72fb6efafcb53938ffa76191ccb14f69db982a7`.
- README contract: this hero is the first content and its asset path appears exactly once.

The repeatable source is [`tools/render_readme_hero.py`](../../../tools/render_readme_hero.py). [`selection.json`](selection.json) stores the machine-readable decision.

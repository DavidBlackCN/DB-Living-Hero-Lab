# Homepage layout / typography polish

## Result
- Reference-scale clock: `clamp(90px, 8.3vw, 320px)`; supporting text follows a shared viewport-aware type scale instead of multiple fixed tiny sizes.
- Local-hour greeting includes the original green status dot, static rather than pulsing.
- Signature uses a restrained quotation mark, KaiTi text, citation rule and italic signature. GitHub / BiliBili / Email / QQ are labelled SVG buttons with no href or action.
- Bottom-right view / light controls / immersive action share one horizontal toolbar; control glyphs now use a single SVG stroke language.
- Both control levels use the same translucent panel. Closed details unmount, fixing hidden content contributing to scroll overflow. Desktop and normal mobile have no menu scrollbars; short landscape keeps scroll access if the expanded panel cannot fit.

## Motion review
| Before | After | Why |
| --- | --- | --- |
| Hidden grid row inside a scroll container | Details removed from layout when closed | Prevent hidden overflow and stray scrollbar |
| Uniform toggle transition | 240ms upward entry / 140ms exit | Preserve spatial connection with faster dismissal |
| Keyboard and pointer use same motion | Keyboard disclosure has no transition | Immediate focus and state feedback |
| Text glyph icons vary by font | Consistent inline SVG | Stable alignment and stroke weight |
| Stacked corner controls | One horizontal utility bar | Clearer hierarchy and less visual noise |

No renderer, lighting, artwork or animation-system changes; no new dependencies or remote fonts. Existing local .gitignore edits were left out of this commit.

## Browser verification
Actual headed Edge preview at 3828×1931, plus 1672×941, 1280×720, 390×844, 360×640 and 844×390.
- Primary menus: no overflow in all tested dimensions.
- Expanded menu: no scroll at full desktop sizes, remains inside viewport on short displays.
- No page overflow; social buttons never navigate; Escape collapses levels and restores focus.
- All six parameters, exact automatic reset, time controls, fullscreen/immersive, reduced-motion and unchanged canvas identity pass.
- `pnpm typecheck`, `pnpm build` passed; browser page errors: none.

## Screenshots
- [Full desktop](homepage-polish/desktop-home.png)
- [Primary menu](homepage-polish/desktop-primary.png)
- [Expanded menu](homepage-polish/desktop-expanded.png)
- [Four phases](homepage-polish/four-phases.jpg)
- [Mobile](homepage-polish/mobile.png)
- [Compact expanded menu](homepage-polish/layout-360x640.png)

Mobile retains the accepted whole-art contain fit. Awaiting human visual acceptance.

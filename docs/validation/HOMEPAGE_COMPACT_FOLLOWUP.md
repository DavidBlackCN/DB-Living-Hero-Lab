# Homepage compact controls follow-up

- Signature and citation share a baseline; removed the David Black italic byline.
- Immersive mode preserves the complete left clock/profile block and hides peripheral header, caption, border, footer and controls except the restore button.
- Replaced the OS-native view dropdown with a themed local menu. Keyboard arrows/Home/End, Enter, Escape, focus return and outside dismissal are supported.
- Lighting panel maximum width reduced from 880 to 640 CSS px; its own type scale is 13–22px. Only the circular plus/minus button receives the expand hover/focus treatment, rather than the entire heading row.
- No renderer or frozen visual-system changes.

## Verification
Typecheck/build passed. Built-page controls, exact automatic reset, unchanged canvas identity, view switching, time playback, reduced motion and viewport tests passed. Headed Edge reviewed at 3828×1931, 1280×720, 390×844, 360×640 and 844×390; primary menu has no scroll overflow, expanded content stays within viewport. Browser errors: none.

[Home](homepage-followup/desktop-home.png) · [Immersive](homepage-followup/desktop-immersive.png) · [View menu](homepage-followup/view-menu.png) · [Compact lighting](homepage-followup/desktop-expanded.png)

Awaiting manual review. User's .gitignore changes remain uncommitted by this task.

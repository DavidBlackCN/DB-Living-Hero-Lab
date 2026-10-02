# Homepage profile / upward controls and lamp registration

## Scope
- Only lamp source geometry changed: R/G still contain three glass panes per lantern. The far left pane ends at x=150.5 and front begins at x=154, preserving the metal mullion. Source edge blur reduced from 0.45 to 0.28 source px to avoid spilling into narrow frames. Influence, light intensity, timing and Bloom unchanged.
- Profile text comes from the local BlogHorizon → HorizonProfile component: 黑姐姐 / DavidBlackCN, Developer · Blogger · INFJ-T, introduction and 《售梦者》 signature. Greeting follows actual local hour, including midnight and wake from hidden tab; preview time does not change greeting.
- Clock reduced; supporting text promoted to a consistent readable scale. Mobile uses a compact identity block with the existing whole-art fit.
- Bottom-right button opens the primary time menu upward; lighting section expands within that same panel into a two-column parameter menu. No side drawer or backdrop. Outside click closes; Escape collapses detail then menu. Parameter values and renderer survive closure.
- Restrained hover/press, upward panel entrance and inline expansion; reduced-motion disables transitions.

## Verification
- pnpm typecheck / pnpm build passed.
- Lamp registration validator passed: three faces each, source limited to corridor, near right coverage retained, far metal gap checked at x=151–153.
- Built /dist/ test passed: six parameter controls, exact auto reset, same canvas identity, playback/realtime, fullscreen, immersive, 390×844 resize, reduced-motion and no page errors.
- No changes to Character / Sky / Atmosphere / Leaves / Motion / Blink or Lamp influence/timing.

## Review
- [Four phases](homepage-refinement/four-phases.jpg)
- [Expanded controls](homepage-refinement/lighting-drawer.png)
- [Mobile](homepage-refinement/mobile.png)
- [Mobile controls](homepage-refinement/mobile-drawer.png)
- [Base / source / overlay](homepage-refinement/lamp-registration.png)
- [Night lamps](homepage-refinement/night-lamps.png)

At extreme zoom, original painted lantern contours remain soft. This registration preserves that softness without filling the metal gaps. Mobile retains the accepted contain fit and therefore letterboxing. Waiting for visual review.

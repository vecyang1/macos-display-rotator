# Feature Research

**Domain:** macOS Display Rotation Utilities
**Researched:** 2026-03-01
**Confidence:** MEDIUM

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Menu bar icon | Standard for macOS utilities | LOW | All competitors have this - users expect quick access |
| Rotation control (90°, 180°, 270°) | Core functionality | LOW | Native macOS API support via CGDisplaySetDisplayMode |
| Auto-detect displays | Users don't want manual config | MEDIUM | CoreGraphics API provides display enumeration |
| Instant rotation | Users expect immediate response | LOW | Native API is synchronous |
| System Preferences integration | Feels native to macOS | LOW | Can be launched via URL scheme |
| Basic error handling | Prevents crashes | LOW | Handle unsupported displays gracefully |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Preserve display arrangement | Solves major pain point - macOS often forgets positions after rotation | HIGH | Requires capturing origin coordinates before rotation, recalculating after orientation change |
| Global hotkey | Faster than menu bar clicking | MEDIUM | System-wide keyboard shortcut registration |
| Profile switching | Save/restore multiple rotation configs | MEDIUM | Store display configs, apply atomically |
| Rotation presets | One-click common scenarios (portrait/landscape) | LOW | Wrapper around basic rotation |
| Auto-rotation triggers | Rotate based on app launch or time | MEDIUM | App monitoring + scheduled tasks |
| Display-specific settings | Remember rotation per display | MEDIUM | Track by display UUID/serial |
| Rotation animation | Visual feedback during transition | MEDIUM | Requires custom rendering or Core Animation |
| CLI interface | Power users + automation | LOW | Expose core functions via command line |
| Notification feedback | Confirm rotation completed | LOW | NSUserNotification or modern equivalents |
| Multi-display rotation | Rotate multiple displays at once | MEDIUM | Coordinate multiple display changes |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Window position restoration | Users want windows back where they were | macOS window management is complex; apps control their own windows; requires accessibility permissions; high maintenance burden | Let macOS handle it - focus on display arrangement only |
| Automatic rotation detection | "Smart" rotation based on physical orientation | Requires hardware sensors not available on external displays; unreliable; confusing UX | Manual trigger with hotkey - predictable and fast |
| Per-app rotation profiles | Auto-rotate when specific app launches | Race conditions; conflicts with user intent; complex state management | User-triggered profiles instead |
| Rotation animations/transitions | "Looks cool" | Adds latency; can cause visual glitches; increases complexity significantly | Instant rotation is actually preferred for productivity |
| Resolution changes with rotation | "Optimize for orientation" | Different displays have different optimal resolutions; too opinionated; hard to predict user intent | Keep rotation and resolution separate |

## Feature Dependencies

```
[Menu bar icon]
    └──requires──> [Rotation control]
                       └──requires──> [Auto-detect displays]

[Global hotkey] ──enhances──> [Rotation control]

[Profile switching]
    └──requires──> [Display-specific settings]
    └──requires──> [Preserve display arrangement]

[Auto-rotation triggers] ──requires──> [Profile switching]

[Multi-display rotation] ──conflicts──> [Preserve display arrangement]
    (rotating multiple displays makes arrangement preservation exponentially complex)

[Window position restoration] ──conflicts──> [Preserve display arrangement]
    (different concerns; window positions are app responsibility)
```

### Dependency Notes

- **Preserve display arrangement requires rotation control:** Must capture arrangement before rotation to restore after
- **Global hotkey enhances rotation control:** Provides faster access than menu bar
- **Profile switching requires display-specific settings:** Profiles are meaningless without per-display memory
- **Multi-display rotation conflicts with arrangement preservation:** Rotating multiple displays simultaneously makes coordinate recalculation extremely complex
- **Window restoration conflicts with core focus:** Window management is a separate domain; mixing concerns creates maintenance burden

## MVP Definition

### Launch With (v1)

Minimum viable product — what's needed to validate the concept.

- [x] Menu bar icon — Standard macOS utility pattern
- [x] Auto-detect second display — Core value prop: "just works"
- [x] Rotation control (90°, 180°, 270°, standard) — Basic functionality
- [x] Preserve display arrangement — Key differentiator vs native macOS
- [x] Global hotkey — Faster than menu bar, validates "one-click" promise
- [x] Basic error handling — Prevents crashes on unsupported displays

### Add After Validation (v1.x)

Features to add once core is working.

- [ ] Display-specific settings — Add when users have multiple displays with different needs
- [ ] Profile switching — Add when users request "save my setup" functionality
- [ ] Notification feedback — Add if users report uncertainty about rotation completion
- [ ] CLI interface — Add when power users request automation
- [ ] Rotation presets — Add if users request common scenarios beyond basic rotation

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] Auto-rotation triggers — Defer until profile switching is validated
- [ ] Multi-display rotation — Defer until single-display rotation is rock-solid
- [ ] Rotation animation — Defer indefinitely (anti-feature unless proven valuable)

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Menu bar icon | HIGH | LOW | P1 |
| Auto-detect second display | HIGH | MEDIUM | P1 |
| Rotation control | HIGH | LOW | P1 |
| Preserve display arrangement | HIGH | HIGH | P1 |
| Global hotkey | HIGH | MEDIUM | P1 |
| Basic error handling | HIGH | LOW | P1 |
| Display-specific settings | MEDIUM | MEDIUM | P2 |
| Profile switching | MEDIUM | MEDIUM | P2 |
| Notification feedback | LOW | LOW | P2 |
| CLI interface | MEDIUM | LOW | P2 |
| Rotation presets | LOW | LOW | P2 |
| Auto-rotation triggers | LOW | MEDIUM | P3 |
| Multi-display rotation | LOW | HIGH | P3 |
| Rotation animation | LOW | MEDIUM | P3 |

**Priority key:**
- P1: Must have for launch (MVP)
- P2: Should have, add when possible (post-validation)
- P3: Nice to have, future consideration (defer)

## Competitor Feature Analysis

| Feature | Display Rotation Menu | displayplacer | SwitchResX | BetterDisplay | Our Approach |
|---------|----------------------|---------------|------------|---------------|--------------|
| Menu bar access | ✓ | ✗ (CLI only) | ✓ | ✓ | ✓ (P1) |
| Rotation control | ✓ | ✓ | ✓ | ✓ | ✓ (P1) |
| Global hotkey | ✗ | ✗ | ✓ | ✓ | ✓ (P1) |
| Preserve arrangement | ✗ | ✓ | ✓ | ✗ | ✓ (P1 - key differentiator) |
| Profile switching | ✗ | ✓ | ✓ | ✓ | ✓ (P2) |
| CLI interface | ✗ | ✓ | ✗ | ✗ | ✓ (P2) |
| Resolution control | ✗ | ✓ | ✓ | ✓ | ✗ (out of scope) |
| Brightness control | ✗ | ✗ | ✗ | ✓ | ✗ (out of scope) |
| Window restoration | ✗ | ✗ | ✓ | ✗ | ✗ (anti-feature) |
| Multi-display | ✗ | ✓ | ✓ | ✓ | ✗ (P3 - defer) |
| Price | Free | Free | $14.99 | $18.99 | Free (MVP) |

**Competitive positioning:**
- **Display Rotation Menu:** Simple but lacks arrangement preservation and hotkey
- **displayplacer:** Powerful CLI but no GUI, steep learning curve
- **SwitchResX:** Feature-rich but expensive, complex, includes unnecessary features
- **BetterDisplay:** Comprehensive but overkill for rotation-only use case

**Our advantage:** Focus on rotation + arrangement preservation with minimal complexity. Free, simple, reliable.

## Sources

### Competitor Products Analyzed
- [Display Rotation Menu](https://macdownload.informer.com/display-rotation-menu/) - Simple menu bar rotation tool
- [displayplacer](https://github.com/jakehilborn/displayplacer) - CLI utility for display configuration
- [SwitchResX](https://mac.softpedia.com/get/System-Utilities/SwitchRes-X.shtml) - Advanced display management
- [BetterDisplay](https://github.com/waydabber/BetterDisplay) - Comprehensive display control utility
- [Display Menu](https://mac.softpedia.com/get/Utilities/Display-Menu.shtml) - Resolution switching utility

### Technical Resources
- [macOS Display Configuration](https://jakehilborn.github.io/displayplacer/) - displayplacer documentation
- [Display Arrangement Issues](https://discussions.apple.com/thread/253841249) - macOS arrangement memory problems
- [Rotation Automation](https://discussions.apple.com/thread/7588942) - Automator rotation scripts

### User Research
- [macOS Display Rotation](https://discussions.apple.com/thread/255072447) - User discussions on rotation
- [Arrangement Preservation](https://gadgetstouse.com/blog/2022/07/23/mac-forgets-dual-monitor-arrangement/) - Common pain point
- [Rotation Workflows](https://forums.macrumors.com/threads/program-that-automatically-adjusts-monitor-orientation.2454697/) - User needs analysis

---
*Feature research for: macOS Display Rotation Utilities*
*Researched: 2026-03-01*

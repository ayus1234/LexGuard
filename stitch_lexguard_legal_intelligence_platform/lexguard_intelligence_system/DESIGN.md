---
name: LexGuard Intelligence System
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#45464d'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#76777d'
  outline-variant: '#c6c6cd'
  surface-tint: '#565e74'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#131b2e'
  on-primary-container: '#7c839b'
  inverse-primary: '#bec6e0'
  secondary: '#006398'
  on-secondary: '#ffffff'
  secondary-container: '#5bb8fe'
  on-secondary-container: '#00476e'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#2f1500'
  on-tertiary-container: '#c76c00'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dae2fd'
  primary-fixed-dim: '#bec6e0'
  on-primary-fixed: '#131b2e'
  on-primary-fixed-variant: '#3f465c'
  secondary-fixed: '#cce5ff'
  secondary-fixed-dim: '#93ccff'
  on-secondary-fixed: '#001d31'
  on-secondary-fixed-variant: '#004b73'
  tertiary-fixed: '#ffdcc3'
  tertiary-fixed-dim: '#ffb77d'
  on-tertiary-fixed: '#2f1500'
  on-tertiary-fixed-variant: '#6e3900'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.025em
  headline-xl-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 30px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
    letterSpacing: -0.005em
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
    letterSpacing: 0em
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0em
  code-md:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: -0.01em
  code-sm:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-md:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.04em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-md: 1.5rem
  gutter-lg: 2rem
  margin: 1rem
  margin-md: 1.5rem
  margin-lg: 2.5rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

This design system establishes a high-precision, mission-critical workspace for automated legal intelligence, contract risk assessment, and document synthesis. Designed for corporate counsel, compliance directors, and legal operations teams, the experience projects unshakeable authority, rigorous structural discipline, and state-of-the-art computational intelligence. 

The aesthetic is Modern Institutional Precision—a synthesis of high-density financial terminals, forensic document readers, and contemporary enterprise SaaS. It intentionally rejects traditional legal clichés: there are no ornate serif crests, brass balance scales, faux-parchment skeuomorphism, or gilded accents. Instead, the visual language relies on razor-sharp contrast, structural 1px linear scaffolding, slate-tinted neutral surfaces, and deliberate, calibrated semantic accents. 

Every surface communicates neutrality, verification, and deterministic accuracy. Data density is prioritized over gratuitous whitespace, yet elements breathe through disciplined mathematical rhythm, ensuring users can parse complex 80-page master service agreements with zero visual fatigue.

## Colors

The palette balances deep naval slate foundations with focused, functional hues. Colors carry strict informational semantics; decorative color usage is strictly prohibited.

- **Primary (`#0F172A` - Slate 900):** Represents structural authority. Applied to primary text, deep command bars, primary interactive buttons, and high-level section anchors.
- **Secondary (`#0284C7` - Sky 600 / `#0EA5E9` - Sky 500 / `#2563EB` - Cobalt):** Reserved for generative AI analysis highlights, primary interactive link states, active entity extractions, and computational signals.
- **Tertiary / Warning (`#D97706` - Amber 600 / Surface: `#FEF3C7`):** Marks clauses flagged with `Review Recommended`, non-standard liabilities, ambiguous indemnifications, and statutory disclaimers.
- **Success / Verified (`#059669` - Emerald 600 / Surface: `#ECFDF5`):** Denotes verified standard precedent, counterparty mutual agreement, validated electronic signatures, and compliant terms.
- **Neutral Scaffold (`#F8FAFC` - Slate 50, `#F1F5F9` - Slate 100, `#E2E8F0` - Slate 200, `#64748B` - Slate 500):** Provides a crisp, non-glare background canvas that maintains high legibility across document diffs and split-pane viewers.

## Typography

The typographic hierarchy is divided into three distinct roles:
1. **Display & Structure (`Plus Jakarta Sans`):** Delivers clean, geometric clarity for document titles, view headers, and risk summary dashboards without calligraphic distractions.
2. **Reading & Document Text (`Inter`):** Engineered for sustained technical reading. High x-height, neutral letterforms, and optimized kerning handle dense contract paragraphs, annotations, and UI controls.
3. **Citations & Metadata (`JetBrains Mono`):** Dedicated to technical metadata, including clause designations (e.g., `§ 14.3(b)`), SHA-256 document hashes, timestamp logs, execution values, and redline diff coordinates.

Legal disclaimers and metadata badges use uppercase small labels with tracking (`+0.04em`) to ensure distinct visual separation from actionable legal narrative text.

## Layout & Spacing

This design system uses a flexible, content-prioritized column layout bounded within an enterprise shell:

- **Desktop (1280px+):** Tri-panel architecture. A collapsible global utility rail (64px–240px), a fluid central document inspection pane (min 640px, max 880px for optimal legal reading length of 65–75 characters per line), and an AI audit/chat rail (380px–460px).
- **Tablet (768px - 1279px):** Dual-pane structure. The central document view dominates; the AI intelligence drawer transitions into an overlay or bottom sheet accessible via a persistent floating toggle.
- **Mobile (<768px):** Single-column stacked layout. Analysis findings, clause cards, and redlines stack sequentially under the active section selector.

All element pacing adheres to an absolute 4px/8px modular grid. Layout distance tokens (`gutter`, `margin`) dictate canvas-level division, while internal component tokens (`space-xs` through `space-xl`) define the internal padding of cards, badges, and actionable lists.

## Elevation & Depth

Visual hierarchy relies on structural borders and tonal layering rather than high-elevation drop shadows:

- **Surface Tiers:**
  - `Base`: Canvas background (`#F8FAFC`).
  - `Surface Tier 1`: Primary working cards, document viewing sheets, and top navigation header (`#FFFFFF`).
  - `Surface Tier 2`: Embedded metadata panels, clause comparison wells, and secondary callouts (`#F1F5F9`).
  - `Surface Tier 3`: Elevated popovers, autocomplete menus, and active modal dialogs (`#FFFFFF`).

- **Linear Scaffolding (1px Borders):** All cards, inputs, and section dividers utilize a crisp `1px solid #E2E8F0` border. Active or focused states shift sharply to `#0284C7` or `#0F172A` without increasing border stroke width.
- **Ambient Shadow System:**
  - *Resting Cards / Tables:* `none` (depth achieved strictly via 1px slate-200 boundary).
  - *Floating Menus & Filter Dropdowns:* `0 4px 12px -2px rgba(15, 23, 42, 0.08), 0 2px 6px -1px rgba(15, 23, 42, 0.04)`.
  - *Modal Overlays:* `0 20px 25px -5px rgba(15, 23, 42, 0.12), 0 8px 10px -6px rgba(15, 23, 42, 0.08)`.

## Shapes

The design system enforces a precise, professional shape language (`roundedness: 1`):

- **Interactive Elements (Buttons, Inputs, Selectors):** `0.25rem` (4px). Provides a clean, functional edge that resists casual roundness.
- **Containers (Cards, Document Viewers, Modals):** `0.5rem` (8px). Softens boundaries while retaining structural integrity in dense layouts.
- **Badges & Micro-Pills:** `9999px` (Full Pill). Used exclusively for contract status tags (`Executed`, `Draft`, `High Risk`), clause citations, and numerical count indicators to set them apart from structural UI cards.

## Components

### Buttons
- **Primary:** Background `#0F172A`, text `#FFFFFF`, 1px border `#0F172A`, 4px radius. Hover: `#1E293B`. Focus: `2px` offset outline `#0284C7`.
- **Secondary / Ghost:** Background transparent, text `#0F172A`, 1px border `#E2E8F0`. Hover: `#F1F5F9`.
- **AI Action / Accent:** Background `#0284C7`, text `#FFFFFF`. Hover: `#0369A1`. Used exclusively for triggering GenAI syntheses, drafting alternative clauses, or executing cross-document comparisons.

### Chips & Status Badges
- Built with full pill geometry, padding `2px 8px`, typography `label-sm` or `code-sm`.
- **Verified / Standard:** Background `#ECFDF5`, text `#065F46`, border `1px solid #A7F3D0`.
- **Review Recommended:** Background `#FEF3C7`, text `#92400E`, border `1px solid #FDE68A`.
- **Clause Reference:** Background `#F1F5F9`, text `#334155`, border `1px solid #CBD5E1`, font `JetBrains Mono`.

### Input Fields & Search
- Background `#FFFFFF`, 1px border `#CBD5E1`, 4px radius, text `body-md` (`#0F172A`), placeholder `#94A3B8`.
- Focus state: Border color `#0284C7` with a subtle box-shadow ring: `0 0 0 1px #0284C7`.
- Leading icon slot reserved for semantic search parameters, query scopes, and boolean operators.

### Educational Disclaimer Banners
- Non-intrusive full-width or card-anchored utility blocks. Background `#FFFBEB`, border `1px solid #FCD34D`, border-left `4px solid #D97706`.
- Typography: `body-sm` (`#92400E`), explicitly stating AI model output boundaries, statutory verification requirements, and non-retention policies.

### Segmented Controls & Tabs
- Track background `#F1F5F9` with a 4px inner radius and 2px interior padding.
- Selected segment: Background `#FFFFFF`, text `#0F172A`, border `1px solid #E2E8F0`, subtle micro-shadow. Inactive: Text `#64748B`, hover text `#0F172A`.

### Split Document Viewer & Cards
- Document card containers use `#FFFFFF` with a 1px `#E2E8F0` border.
- Diff views highlight modifications with inline background tints: Redline Deletions (`#FEF2F2`, strike-through `#991B1B`), Additions (`#F0FDF4`, underline `#166534`), and AI Commentary anchors (`#F0F9FF`, border-bottom `2px solid #0284C7`).
# Memory Trails Native Mobile App (Expo / React Native) — Design Specification

**Date:** 2026-10-06  
**Status:** Approved  
**Location:** `webapp/apps/mobile/`  

---

## 1. Executive Summary & Objective

Rebuild Google Photos **Memory Trails** as a native mobile application using **Expo (React Native)**, delivering:
1. An authentic **Google Photos mobile shell** (Material You / M3 styling, bottom navigation tabs, top search bar with account avatar, and chronological virtualized photo grid).
2. A high-performance **native touch gesture layer** validating mobile ergonomics that the desktop web prototype could not test:
   - Smooth draggable bottom sheet (`@gorhom/bottom-sheet`) for the retrieval flow with rubber-banding and swipe-down to dismiss.
   - Fluid pinch-to-zoom and double-tap zoom (`react-native-gesture-handler` + `react-native-reanimated`).
   - Swipe-down dismiss on the full-screen photo viewer.
   - Haptic feedback (`expo-haptics`) on "That's the one" confirmation and clue interactions.
3. Full integration with the **retrieval fixes**:
   - Multi-category extraction and staged suggestions ("I also heard...").
   - Clue completeness ranking priority (`clue_hits` before episode size) with full-match card badges.
   - Temporally-centered horizontal Time Ribbon ("Around that time" / "Browse months").
   - Singleton photo card parity with multi-photo episodes.
4. **Client-Server Architecture with Offline Fallback**: Direct HTTP communication with the existing FastAPI backend (`/api/py/*`) plus an embedded offline JSON metadata store for standalone demo reliability.

---

## 2. Directory Structure & Architecture

The mobile app lives inside the monorepo at `webapp/apps/mobile/`:

```
webapp/apps/mobile/
├── assets/                  # App icon, splash screen, and sample photo assets
├── src/
│   ├── api/                 # API client & offline fallback store
│   │   ├── client.ts        # FastAPI endpoints (/api/py/extract, /api/py/search, /api/py/facets)
│   │   ├── fallback.ts      # Offline fallback using bundled demo metadata
│   │   └── types.ts         # Shared interfaces (Chip, Episode, Photo, Facets, Ledger)
│   ├── components/
│   │   ├── GooglePhotosHeader.tsx   # Top search bar with brand logo & user avatar
│   │   ├── BottomNav.tsx            # Material 3 bottom navigation (Photos, Search/Trails, Library)
│   │   ├── PhotosGrid.tsx           # Virtualized chronological photo stream with date headers
│   │   ├── MemoryTrailsSheet.tsx    # Native Gorhom bottom sheet containing the Trails assistant
│   │   ├── ClueChipsBar.tsx         # Horizontally scrollable chips with kind tags & "+ I also heard"
│   │   ├── MomentsList.tsx          # Candidate cards with full-match badge & singleton parity
│   │   ├── TimeRibbonNative.tsx     # Centered horizontal month scrubber with rubber-banding
│   │   └── NativePhotoViewer.tsx    # Full-screen viewer modal with pinch-zoom & swipe-down dismiss
│   ├── context/
│   │   └── MemoryTrailsContext.tsx  # Global state for retrieval session, query, filters, & viewer
│   ├── theme/
│   │   └── colors.ts        # Material 3 tokens (Google Blue #1a73e8, surface containers, dark theme)
│   ├── App.tsx              # Root component with GestureHandlerRootView & SheetProvider
│   └── index.ts             # Expo app entry point
├── package.json             # Expo SDK 52, React Native 0.76+, Reanimated, Gesture Handler
├── app.json                 # Expo project configuration
└── tsconfig.json            # Strict TypeScript configuration
```

---

## 3. Google Photos Shell & Navigation

### 3.1 Top App Bar (`GooglePhotosHeader.tsx`)
- **Brand Identity:** Google Photos multi-color pinwheel icon on the left.
- **Search Pill:** Rounded Material 3 search bar: *"Search your photos, or find a memory..."*.
- **Account Avatar:** User profile initial bubble with Google styling.
- **Interaction:** Tapping the search bar or header activates the **Search / Trails** flow.

### 3.2 Bottom Navigation Tabs (`BottomNav.tsx`)
- **Tab 1: Photos (Home)**:
  - Chronological 3-column photo grid.
  - Sticky/scrolling date group headers ("Today", "September 2026", "June 2026").
  - Vertical fast-scrub timeline indicator on the right edge.
  - Tapping any photo opens `NativePhotoViewer`.
- **Tab 2: Search / Trails**:
  - Highlights Memory Trails hero card: *"Recall a moment with vague clues"*.
  - Quick-starter memories: *"cafe in Bengaluru with friends"*, *"lake picnic sunset"*, etc.
  - Automatically opens the `MemoryTrailsSheet`.
- **Tab 3: Library**:
  - Clean Material 3 cards for Albums, Favorites, Archive, and Trash.

---

## 4. Memory Trails Native Bottom Sheet & Touch Gesture Layer

### 4.1 Native Bottom Sheet (`MemoryTrailsSheet.tsx`)
- Powered by `@gorhom/bottom-sheet` within a `GestureHandlerRootView`.
- **Snap Points:** `['45%', '85%', '95%']` allowing partial peek or immersive interaction.
- **Dismiss Interaction:** Dragging down on the handle smoothly docks or closes the sheet.
- **Flow Stages:**
  1. **Compose Stage:**
     - Natural language text input with mic icon and sample memory chips.
     - Live loading indicator during extraction.
     - One-time disclaimer placed in info modal/sheet footer, never cluttering active action areas.
  2. **Recap Stage:**
     - Extracted clue chips displaying cue kinds (`Place`, `Time`, `Person`, `Scene`).
     - Staged category suggestions row: *"I also heard:"* `[+ cafe]` `[+ dosa]`. Tapping adds the clue with haptic feedback.
     - Editable chips (tap chip to modify/remove).
  3. **Moments Stage:**
     - Candidate moment cards with cover photo or contact sheet.
     - Full-match cards display green `✓ Matches all your clues` badge and rank first.
     - Singleton photos receive the same first-class card parity and "View photo" action.
     - Ruled-out moments notice includes an active `Restore` button.
  4. **Time Ribbon (`TimeRibbonNative.tsx`):**
     - Horizontal month pills with native rubber-band physics.
     - Auto-centers on the active memory date window (e.g. May 2026) on mount.
     - Contextual title: *"Around that time"* when anchored to a date clue, *"Browse months"* when undated.
  5. **Confirmation Stage:**
     - "Found it!" confirmation with celebration haptic pulse.
     - Optional Yes/Partly/No survey deferred until after "Done".

### 4.2 Native Photo Viewer (`NativePhotoViewer.tsx`)
- Full-screen modal over dark background.
- **Pinch-to-Zoom:** Using `PinchGestureHandler` with `Reanimated` scale transform (1.0x to 4.0x) centered on focal point.
- **Double-Tap Zoom:** Double-tap toggles between 1.0x and 2.0x zoom.
- **Swipe-Down to Dismiss:** Vertical `PanGestureHandler` with interactive translateY and fading opacity; releasing past threshold smoothly dismisses the modal.
- **Haptics:** `ExpoHaptics.impactAsync(ImpactFeedbackStyle.Medium)` on "That's the one" action.

---

## 5. Networking, Fallback Store, & State Management

### 5.1 API Client (`src/api/client.ts`)
- Communicates with FastAPI backend (`/api/py/*`) with configurable `EXPO_PUBLIC_API_URL` (default `http://localhost:8000` or local network host).
- Implements request timeouts with automated fallback.

### 5.2 Standalone Fallback Store (`src/api/fallback.ts`)
- Bundles the demo photo metadata index (`library.jsonl` / `gallery.json` records).
- Implements client-side clue matching, `clue_hits` calculation, and ranking fallback in TypeScript.
- If backend HTTP requests fail, seamlessly serves the local library dataset with an unobtrusive notice: *"Using offline library demo"*.

### 5.3 Photo Assets
- Uses `expo-image` with caching and smooth cross-fade.
- Resolves image URIs from local assets or remote static server (`/library/{id}.jpg`).

---

## 6. Testing & Quality Acceptance Criteria

1. **Native Gestures:**
   - Bottom sheet drags smoothly between snap points with rubber-band edge resistance.
   - Photo viewer supports fluid multi-touch pinch-to-zoom and swipe-down dismiss.
   - Haptics fire on key actions ("That's the one", adding suggested clues).
2. **Retrieval Parity:**
   - Multi-scene queries (e.g. cafe + dosa) extract primary clue and show suggestions.
   - Singleton photos matching all clues rank first above partial multi-photo episodes.
   - Time ribbon centers on the active memory date window.
3. **Build & Compatibility:**
   - Compiles cleanly in Expo (`npx expo start`) with web preview support (`npx expo start --web`) and native iOS/Android simulator support.
   - TypeScript compiles with 0 errors.

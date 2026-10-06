# Memory Trails Native Expo Mobile App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a native Expo (React Native) mobile application for Google Photos Memory Trails at `webapp/apps/mobile`, delivering a complete Google Photos shell, native gesture-driven bottom sheet assistant, fluid pinch-to-zoom and swipe-down photo inspection, haptic feedback, and offline fallback retrieval.

**Architecture:** 
- Mobile client built with Expo SDK 52 and React Native under `webapp/apps/mobile`.
- Native gesture layer using `react-native-gesture-handler`, `react-native-reanimated`, and `@gorhom/bottom-sheet` for 60/120fps physics.
- Client-server networking with existing FastAPI backend (`/api/py/*`) plus an embedded offline JSON metadata store for standalone demo reliability.
- Material 3 design system matching Google Photos mobile styling.

**Tech Stack:** Expo SDK 52, React Native 0.76+, TypeScript, `@gorhom/bottom-sheet`, `react-native-reanimated`, `react-native-gesture-handler`, `expo-haptics`, `expo-image`, Jest.

## Global Constraints

- App must be placed in `webapp/apps/mobile/` within the monorepo.
- TypeScript strict mode with 0 compile errors.
- Never crash when the backend is offline; seamlessly fall back to local bundled metadata.
- Date formatting must always be natural language (e.g., "31 Mar – 29 Jun 2026").
- All gesture handlers must work seamlessly without native build step required for Expo Go / web export preview.

---

### Task 1: Scaffolding Mobile Project & Dependency Setup

**Files:**
- Create: `webapp/apps/mobile/package.json`
- Create: `webapp/apps/mobile/app.json`
- Create: `webapp/apps/mobile/tsconfig.json`
- Create: `webapp/apps/mobile/babel.config.js`
- Create: `webapp/apps/mobile/metro.config.js`
- Create: `webapp/apps/mobile/index.ts`
- Create: `webapp/apps/mobile/assets/icon.png` (or placeholder svg/png)

**Interfaces:**
- Produces: Runnable Expo workspace under `webapp/apps/mobile`.

- [x] **Step 1: Create `package.json`**

In `webapp/apps/mobile/package.json`:
```json
{
  "name": "memory-trails-mobile",
  "version": "1.0.0",
  "main": "index.ts",
  "scripts": {
    "start": "expo start",
    "android": "expo start --android",
    "ios": "expo start --ios",
    "web": "expo start --web",
    "test": "jest",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "@gorhom/bottom-sheet": "^5.0.6",
    "expo": "~52.0.0",
    "expo-constants": "~17.0.0",
    "expo-haptics": "~14.0.0",
    "expo-image": "~2.0.0",
    "expo-status-bar": "~2.0.0",
    "react": "18.3.1",
    "react-native": "0.76.7",
    "react-native-gesture-handler": "~2.20.2",
    "react-native-reanimated": "~3.16.1",
    "react-native-safe-area-context": "4.12.0",
    "react-native-screens": "~4.4.0"
  },
  "devDependencies": {
    "@babel/core": "^7.25.0",
    "@types/jest": "^29.5.14",
    "@types/react": "~18.3.12",
    "jest": "^29.7.0",
    "ts-jest": "^29.2.5",
    "typescript": "^5.3.3"
  },
  "private": true
}
```

- [x] **Step 2: Create `tsconfig.json` & `app.json` & configs**

Create `webapp/apps/mobile/tsconfig.json`:
```json
{
  "extends": "expo/tsconfig.base",
  "compilerOptions": {
    "strict": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

Create `webapp/apps/mobile/app.json`:
```json
{
  "expo": {
    "name": "Memory Trails",
    "slug": "memory-trails",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "userInterfaceStyle": "automatic",
    "splash": {
      "backgroundColor": "#ffffff"
    },
    "ios": {
      "supportsTablet": true,
      "bundleIdentifier": "com.google.memorytrails"
    },
    "android": {
      "package": "com.google.memorytrails"
    },
    "web": {
      "bundler": "metro"
    }
  }
}
```

Create `webapp/apps/mobile/babel.config.js`:
```javascript
module.exports = function (api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: ['react-native-reanimated/plugin'],
  };
};
```

Create `webapp/apps/mobile/metro.config.js`:
```javascript
const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

module.exports = config;
```

- [x] **Step 3: Install dependencies**

Run:
```bash
cd webapp/apps/mobile && npm install --legacy-peer-deps
```
Expected: Node modules installed.

- [x] **Step 4: Verify package setup**

Run:
```bash
npm --prefix webapp/apps/mobile run typecheck
```
Expected: PASS (or empty index check).

- [x] **Step 5: Commit Task 1**

```bash
git add webapp/apps/mobile
git commit -m "chore(mobile): scaffold Expo React Native project with gesture dependencies"
```

---

### Task 2: Data Types, API Client, & Standalone Fallback Store

**Files:**
- Create: `webapp/apps/mobile/src/api/types.ts`
- Create: `webapp/apps/mobile/src/api/client.ts`
- Create: `webapp/apps/mobile/src/api/fallback.ts`
- Test: `webapp/apps/mobile/src/api/__tests__/fallback.test.ts`

**Interfaces:**
- Produces: `extractClues(query: string)`, `searchMoments(filters: Filters)`, `getFacets()`, `getEpisode(id: string)`.
- All methods return typed results and seamlessly fall back to local metadata when network fails.

- [x] **Step 1: Write failing test for fallback retrieval logic**

Create `webapp/apps/mobile/src/api/__tests__/fallback.test.ts`:
```typescript
import { fallbackExtract, fallbackSearch, BUNDLED_PHOTOS } from '../fallback';

describe('Fallback Retrieval Engine', () => {
  it('extracts primary and suggested scene words', () => {
    const res = fallbackExtract("cafe in Bengaluru with friends, dosa on the table");
    expect(res.filters.location).toBe("Bengaluru");
    expect(res.filters.category).toBeDefined();
    expect(res.suggested_categories.length).toBeGreaterThan(0);
    const all = [res.filters.category, ...res.suggested_categories.map(s => s.category)];
    expect(all).toContain("cafe");
    expect(all).toContain("dosa");
  });

  it('ranks full-match candidate cards first', () => {
    const filters = {
      location: "Bengaluru",
      category: "cafe"
    };
    const results = fallbackSearch(filters);
    expect(results.length).toBeGreaterThan(0);
    expect(results[0].clue_hits).toBeGreaterThan(0);
  });
});
```

- [x] **Step 2: Run test to verify it fails**

Run:
```bash
npm --prefix webapp/apps/mobile test fallback.test.ts
```
Expected: FAIL because `fallback.ts` does not exist yet.

- [x] **Step 3: Implement `types.ts`, `client.ts`, and `fallback.ts`**

Create `src/api/types.ts` defining `Photo`, `Episode`, `Chip`, `Filters`, `ExtractResult`, `Facets`.

Create `src/api/fallback.ts`:
- Include representative sample photo metadata from `data/demo/library.jsonl` (places like Bengaluru, Hampi, scenes like cafe, dosa, picnic, friends, concert, dates spanning 2026).
- Implement rule-based clue extraction with synonym mapping and suggested categories.
- Implement episode grouping, `clue_hits` calculation, and sorting by `(-clue_hits, -usefulness, -score)`.

Create `src/api/client.ts`:
- Fetch from `${API_URL}/api/py/extract`, falling back to `fallbackExtract()` on network error or timeout.
- Fetch from `${API_URL}/api/py/search`, falling back to `fallbackSearch()` on network error.
- Export unified retrieval functions.

- [x] **Step 4: Run test to verify it passes**

Run:
```bash
npm --prefix webapp/apps/mobile test fallback.test.ts
```
Expected: PASS.

- [x] **Step 5: Commit Task 2**

```bash
git add webapp/apps/mobile/src/api
git commit -m "feat(mobile): implement typed API client and standalone retrieval fallback store"
```

---

### Task 3: Theme, State Management Context & Shell Components

**Files:**
- Create: `webapp/apps/mobile/src/theme/colors.ts`
- Create: `webapp/apps/mobile/src/context/MemoryTrailsContext.tsx`
- Create: `webapp/apps/mobile/src/components/GooglePhotosHeader.tsx`
- Create: `webapp/apps/mobile/src/components/BottomNav.tsx`
- Test: `webapp/apps/mobile/src/context/__tests__/context.test.tsx`

**Interfaces:**
- Produces: `MemoryTrailsProvider`, `useMemoryTrails()` hook managing:
  - `stage`: `"idle" | "compose" | "recap" | "moments" | "confirmed"`
  - `query`: string
  - `chips`: Chip[]
  - `suggestedCategories`: { category: string; word: string; label?: string }[]
  - `moments`: Episode[]
  - `activeMoment`: Episode | null
  - `selectedPhoto`: Photo | null
  - `rejectedIds`: string[]
  - `restoreRejected()`
- Produces `GooglePhotosHeader` and `BottomNav`.

- [x] **Step 1: Write failing test for state management context**

Create test verifying clue chip additions, category switching, and restoring rejected moments.

- [x] **Step 2: Run test to verify failure**

Run: `npm --prefix webapp/apps/mobile test context.test.tsx`  
Expected: FAIL.

- [x] **Step 3: Implement Theme, Context, Header, and BottomNav**

- `colors.ts`: Google brand blue (`#1a73e8`), dark surface (`#1f1f1f`), surface variant (`#f1f3f4`), text primary, green full-match badge (`#137333` / `#e6f4ea`).
- `MemoryTrailsContext.tsx`: Full lifecycle state, action handlers with `expo-haptics` triggers.
- `GooglePhotosHeader.tsx`: Google Photos 4-color pinwheel icon, search input pill, avatar bubble.
- `BottomNav.tsx`: Tab buttons for "Photos", "Search", "Library" with active tint indicator.

- [x] **Step 4: Run test to verify passes**

Run: `npm --prefix webapp/apps/mobile test context.test.tsx`  
Expected: PASS.

- [x] **Step 5: Commit Task 3**

```bash
git add webapp/apps/mobile/src/theme webapp/apps/mobile/src/context webapp/apps/mobile/src/components/GooglePhotosHeader.tsx webapp/apps/mobile/src/components/BottomNav.tsx
git commit -m "feat(mobile): add Google Photos theme, state context, header, and bottom navigation"
```

---

### Task 4: Chronological Photos Grid & Right Scrubber

**Files:**
- Create: `webapp/apps/mobile/src/components/PhotosGrid.tsx`
- Test: `webapp/apps/mobile/src/components/__tests__/PhotosGrid.test.tsx`

**Interfaces:**
- Consumes: `useMemoryTrails().openPhotoViewer(photo)`.
- Produces: Virtualized 3-column photo grid grouped by date sections, fast date scrubber on the right edge.

- [x] **Step 1: Write test for PhotosGrid date grouping**

Verify photos are grouped into chronological month/date buckets with proper headers.

- [x] **Step 2: Run test to verify failure**

- [x] **Step 3: Implement `PhotosGrid.tsx`**

- Use `FlatList` with `numColumns={3}`.
- Section headers (e.g., "September 2026", "June 2026", "May 2026").
- `expo-image` with smooth crossfade and caching.
- Right-side date scrubber indicator.
- Tap photo triggers `openPhotoViewer(photo)`.

- [x] **Step 4: Run test to verify passes**

Run: `npm --prefix webapp/apps/mobile test PhotosGrid.test.tsx`  
Expected: PASS.

- [x] **Step 5: Commit Task 4**

```bash
git add webapp/apps/mobile/src/components/PhotosGrid.tsx webapp/apps/mobile/src/components/__tests__/PhotosGrid.test.tsx
git commit -m "feat(mobile): implement chronological photo grid with date scrubber"
```

---

### Task 5: Native Time Ribbon Component

**Files:**
- Create: `webapp/apps/mobile/src/components/TimeRibbonNative.tsx`
- Test: `webapp/apps/mobile/src/components/__tests__/TimeRibbonNative.test.tsx`

**Interfaces:**
- Consumes: `chapters`, `activeDateFrom`, `activeDateTo`, `onShiftMonth`.
- Produces: Horizontally scrollable month pills auto-centered on active date window; dynamic title.

- [x] **Step 1: Write test for Time Ribbon auto-centering calculation & title**

Verify active index calculation and title:
- When `activeDateFrom` is "2026-05-01", title is "Around that time" and active index points to May 2026.
- When no date filter, title is "Browse months".

- [x] **Step 2: Run test to verify failure**

- [x] **Step 3: Implement `TimeRibbonNative.tsx`**

- Use `ScrollView` horizontal with `showsHorizontalScrollIndicator={false}`.
- Dynamic title and subtitle based on `Boolean(activeDateFrom || activeDateTo)`.
- Use `useEffect` and `scrollTo({ x: targetOffset, animated: true })` to center the active month capsule.
- Haptic feedback on tapping a month pill.

- [x] **Step 4: Run test to verify passes**

Run: `npm --prefix webapp/apps/mobile test TimeRibbonNative.test.tsx`  
Expected: PASS.

- [x] **Step 5: Commit Task 5**

```bash
git add webapp/apps/mobile/src/components/TimeRibbonNative.tsx webapp/apps/mobile/src/components/__tests__/TimeRibbonNative.test.tsx
git commit -m "feat(mobile): implement native time ribbon with temporal centering and dynamic title"
```

---

### Task 6: Memory Trails Native Bottom Sheet & Workflow Stages

**Files:**
- Create: `webapp/apps/mobile/src/components/ClueChipsBar.tsx`
- Create: `webapp/apps/mobile/src/components/MomentsList.tsx`
- Create: `webapp/apps/mobile/src/components/MemoryTrailsSheet.tsx`
- Test: `webapp/apps/mobile/src/components/__tests__/MemoryTrailsSheet.test.tsx`

**Interfaces:**
- Consumes: `useMemoryTrails()`.
- Produces: `@gorhom/bottom-sheet` bottom sheet with snap points `['45%', '85%', '95%']`, handling Compose, Recap, Moments, and Confirmation stages.

- [x] **Step 1: Write test for MemoryTrails stages & suggestion chips**

Verify:
- Clicking a suggestion chip (`+ dosa`) adds it to active chips and triggers retrieval refresh.
- Full-match moment cards render the `✓ Matches all your clues` badge.
- Ruled-out moments notice includes an active `Restore` button.

- [x] **Step 2: Run test to verify failure**

- [x] **Step 3: Implement `ClueChipsBar`, `MomentsList`, and `MemoryTrailsSheet`**

- `ClueChipsBar.tsx`:
  - Renders clue chips with kind tags (`Place`, `Time`, `Person`, `Scene`).
  - Staged suggestions row: *"I also heard:"* `[+ cafe]` `[+ dosa]`.
- `MomentsList.tsx`:
  - Moment cards showing cover photo / grid, title, date range (formatted), and reason.
  - Full-match badge on cards matching all clues.
  - Parity for singleton photos (unnamed moments) with "View photo" action.
  - Ruled out section with interactive "Restore" button.
- `MemoryTrailsSheet.tsx`:
  - Bottom sheet container with handle, snap points, and swipe-down dismiss.
  - Staging flows (Compose -> Recap -> Moments -> Confirmation).
  - Confirmation aha moment with "That's the one" action and celebration haptics.

- [x] **Step 4: Run test to verify passes**

Run: `npm --prefix webapp/apps/mobile test MemoryTrailsSheet.test.tsx`  
Expected: PASS.

- [x] **Step 5: Commit Task 6**

```bash
git add webapp/apps/mobile/src/components/ClueChipsBar.tsx webapp/apps/mobile/src/components/MomentsList.tsx webapp/apps/mobile/src/components/MemoryTrailsSheet.tsx webapp/apps/mobile/src/components/__tests__/MemoryTrailsSheet.test.tsx
git commit -m "feat(mobile): implement native Memory Trails bottom sheet and workflow stages"
```

---

### Task 7: Native Photo Viewer with Pinch-Zoom & Swipe-Down Dismiss

**Files:**
- Create: `webapp/apps/mobile/src/components/NativePhotoViewer.tsx`
- Test: `webapp/apps/mobile/src/components/__tests__/NativePhotoViewer.test.tsx`

**Interfaces:**
- Consumes: `selectedPhoto`, `onClose()`, `onConfirmMemory()`.
- Produces: Full-screen modal supporting:
  - Pinch-to-zoom (1x - 4x) using `Gesture.Pinch()`.
  - Double-tap zoom toggle using `Gesture.Tap().numberOfTaps(2)`.
  - Vertical drag dismiss using `Gesture.Pan()`.
  - "That's the one" button triggering `Haptics.impactAsync(Medium)`.

- [x] **Step 1: Write test for NativePhotoViewer gesture handlers and close callback**

- [x] **Step 2: Run test to verify failure**

- [x] **Step 3: Implement `NativePhotoViewer.tsx`**

- Use `GestureDetector` with composed simultaneous gestures:
  - `Pinch`: Updates scale shared value with boundary clamp [1, 4].
  - `Tap` (double): Toggles scale between 1 and 2 with spring animation.
  - `Pan` (vertical): Animates translateY and dims background opacity when scale is 1; closes if velocity/distance exceeds threshold.
- Action buttons: "Close" and "That's the one!" (haptic impact).

- [x] **Step 4: Run test to verify passes**

Run: `npm --prefix webapp/apps/mobile test NativePhotoViewer.test.tsx`  
Expected: PASS.

- [x] **Step 5: Commit Task 7**

```bash
git add webapp/apps/mobile/src/components/NativePhotoViewer.tsx webapp/apps/mobile/src/components/__tests__/NativePhotoViewer.test.tsx
git commit -m "feat(mobile): implement full-screen photo viewer with pinch-zoom, swipe-down dismiss, and haptics"
```

---

### Task 8: App Root Integration & Verification

**Files:**
- Create: `webapp/apps/mobile/src/App.tsx`
- Modify: `webapp/apps/mobile/index.ts`

**Interfaces:**
- Assembles `GestureHandlerRootView`, `SafeAreaProvider`, `MemoryTrailsProvider`, `PhotosGrid`, `BottomNav`, `MemoryTrailsSheet`, and `NativePhotoViewer`.

- [x] **Step 1: Implement `App.tsx` and `index.ts`**

Connect all providers and shell components in `App.tsx` with proper SafeArea padding and bottom sheet portals.

- [x] **Step 2: Execute full test suite**

Run:
```bash
npm --prefix webapp/apps/mobile test
```
Expected: All Jest unit and component tests pass.

- [x] **Step 3: Execute TypeScript check**

Run:
```bash
npm --prefix webapp/apps/mobile run typecheck
```
Expected: 0 errors.

- [x] **Step 4: Verify Expo export / bundle**

Run:
```bash
npx --prefix webapp/apps/mobile expo export --platform web --output-dir dist
```
Expected: Clean export bundle created with 0 errors.

- [x] **Step 5: Commit Task 8 & Integration**

```bash
git add webapp/apps/mobile
git commit -m "feat(mobile): integrate complete Google Photos Memory Trails mobile application"
```

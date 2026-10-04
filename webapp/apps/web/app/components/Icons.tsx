/* Hand-written rather than an icon package: the app carries no UI library, and
   clean SVGs keep the bundle lightweight and fast. 24px grid, 1.8px stroke. */

export type IconName =
  | "photos"
  | "spark"
  | "albums"
  | "documents"
  | "screenshots"
  | "pets"
  | "places"
  | "search"
  | "help"
  | "voice"
  | "lens"
  | "star"
  | "star-filled"
  | "share"
  | "close"
  | "back"
  | "check"
  | "chevron-right"
  | "sliders"
  | "calendar"
  | "clock"
  | "map-pin";

const PATHS: Record<IconName, React.ReactNode> = {
  photos: (
    <>
      <rect x="3" y="5" width="18" height="14" rx="3" />
      <circle cx="8.5" cy="10" r="1.6" fill="currentColor" stroke="none" />
      <path d="M4 17l4.5-4.5L12 16l3-2.5 5 4.5" strokeLinejoin="round" />
    </>
  ),
  spark: (
    <path d="M12 3.5l1.9 5.1 5.1 1.9-5.1 1.9L12 17.5l-1.9-5.1L5 10.5l5.1-1.9zM18.5 16l.8 2.2 2.2.8-2.2.8-.8 2.2-.8-2.2-2.2-.8 2.2-.8z" strokeLinejoin="round" />
  ),
  albums: (
    <>
      <rect x="4" y="3.5" width="16" height="17" rx="2.5" />
      <path d="M9 3.5v7l2.5-1.6L14 10.5v-7" strokeLinejoin="round" />
    </>
  ),
  documents: (
    <>
      <rect x="4.5" y="4" width="15" height="16" rx="2" />
      <path d="M8 9h8M8 12.5h8M8 16h5" strokeLinecap="round" />
    </>
  ),
  screenshots: (
    <>
      <rect x="7" y="2.5" width="10" height="19" rx="2.2" />
      <path d="M4 7V5.5A2 2 0 0 1 5 4M20 7V5.5A2 2 0 0 0 19 4M4 17v1.5A2 2 0 0 0 5 20M20 17v1.5a2 2 0 0 1-1 1.5" strokeLinecap="round" />
    </>
  ),
  pets: (
    <>
      <circle cx="7" cy="9" r="1.8" />
      <circle cx="11" cy="6" r="1.8" />
      <circle cx="15.5" cy="6.5" r="1.8" />
      <circle cx="18.5" cy="10.5" r="1.8" />
      <path d="M12.5 11.5c-2.6 0-5 3.3-5 5.6 0 1.6 1.2 2.4 2.6 2.4 1 0 1.6-.5 2.4-.5s1.4.5 2.4.5c1.4 0 2.6-.8 2.6-2.4 0-2.3-2.4-5.6-5-5.6z" />
    </>
  ),
  places: (
    <>
      <path d="M12 21s-6.5-6.2-6.5-11A6.5 6.5 0 0 1 18.5 10c0 4.8-6.5 11-6.5 11z" />
      <circle cx="12" cy="10" r="2.3" />
    </>
  ),
  search: (
    <>
      <circle cx="11" cy="11" r="6.2" />
      <path d="M15.6 15.6L20 20" strokeLinecap="round" />
    </>
  ),
  help: (
    <>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M9.6 9.6a2.5 2.5 0 1 1 3.4 2.3c-.6.3-1 .8-1 1.5v.4" strokeLinecap="round" />
      <circle cx="12" cy="16.8" r="1" fill="currentColor" stroke="none" />
    </>
  ),
  voice: (
    <>
      <rect x="9" y="3" width="6" height="11" rx="3" />
      <path d="M5 10a7 7 0 0 0 14 0M12 18v3M8 21h8" strokeLinecap="round" strokeLinejoin="round" />
    </>
  ),
  lens: (
    <>
      <rect x="4" y="4" width="16" height="16" rx="4" />
      <circle cx="12" cy="12" r="3.2" />
      <circle cx="16" cy="8" r="1" fill="currentColor" stroke="none" />
    </>
  ),
  star: (
    <path d="M12 3l2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-2.9-5.6 2.9 1.1-6.2-4.5-4.4 6.2-.9z" strokeLinejoin="round" />
  ),
  "star-filled": (
    <path d="M12 3l2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-2.9-5.6 2.9 1.1-6.2-4.5-4.4 6.2-.9z" fill="#FBBC04" stroke="#FBBC04" strokeLinejoin="round" />
  ),
  share: (
    <>
      <circle cx="18" cy="5" r="3" />
      <circle cx="6" cy="12" r="3" />
      <circle cx="18" cy="19" r="3" />
      <path d="M8.6 13.5l6.8 3.9M15.4 6.6l-6.8 3.9" />
    </>
  ),
  close: (
    <path d="M18 6L6 18M6 6l12 12" strokeLinecap="round" strokeLinejoin="round" />
  ),
  back: (
    <path d="M19 12H5M12 19l-7-7 7-7" strokeLinecap="round" strokeLinejoin="round" />
  ),
  check: (
    <path d="M20 6L9 17l-5-5" strokeLinecap="round" strokeLinejoin="round" />
  ),
  "chevron-right": (
    <path d="M9 18l6-6-6-6" strokeLinecap="round" strokeLinejoin="round" />
  ),
  sliders: (
    <>
      <path d="M4 6h16M4 12h16M4 18h16" strokeLinecap="round" />
      <circle cx="8" cy="6" r="2" fill="currentColor" />
      <circle cx="16" cy="12" r="2" fill="currentColor" />
      <circle cx="10" cy="18" r="2" fill="currentColor" />
    </>
  ),
  calendar: (
    <>
      <rect x="3.5" y="4.5" width="17" height="16" rx="2.5" />
      <path d="M3.5 9.5h17M8 2.5v3M16 2.5v3" strokeLinecap="round" />
    </>
  ),
  clock: (
    <>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 7.5v4.8l3.2 1.9" strokeLinecap="round" strokeLinejoin="round" />
    </>
  ),
  "map-pin": (
    <>
      <path d="M12 21s-6-5.5-6-10a6 6 0 0 1 12 0c0 4.5-6 10-6 10z" />
      <circle cx="12" cy="11" r="2.2" />
    </>
  ),
};

export function Icon({ name, size = 22, className }: { name: IconName; size?: number; className?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className={className} aria-hidden="true">
      {PATHS[name]}
    </svg>
  );
}

/** Authentic Google Photos 4-color pinwheel logo */
export function GooglePhotosLogo({ size = 28 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg" aria-label="Google Photos">
      {/* Top blue petal */}
      <path d="M18 18V8.5C18 5.46 20.46 3 23.5 3C26.54 3 29 5.46 29 8.5C29 11.54 26.54 14 23.5 14H18V18Z" fill="#4285F4" />
      {/* Right red petal */}
      <path d="M18 18H27.5C30.54 18 33 20.46 33 23.5C33 26.54 30.54 29 27.5 29C24.46 29 22 26.54 22 23.5V18H18Z" fill="#EA4335" />
      {/* Bottom yellow petal */}
      <path d="M18 18V27.5C18 30.54 15.54 33 12.5 33C9.46 33 7 30.54 7 27.5C7 24.46 9.46 22 12.5 22H18V18Z" fill="#FBBC04" />
      {/* Left green petal */}
      <path d="M18 18H8.5C5.46 18 3 15.54 3 12.5C3 9.46 5.46 7 8.5 7C11.54 7 14 9.46 14 12.5V18H18Z" fill="#34A853" />
    </svg>
  );
}

/** Colorful Google Gemini sparkle for Ask Photos / Memory Trails */
export function GeminiSpark({ size = 18 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <defs>
        <linearGradient id="gemini-grad" x1="2" y1="2" x2="22" y2="22" gradientUnits="userSpaceOnUse">
          <stop stopColor="#4285F4" />
          <stop offset="0.35" stopColor="#9B72CB" />
          <stop offset="0.7" stopColor="#D96570" />
          <stop offset="1" stopColor="#F2A25C" />
        </linearGradient>
      </defs>
      <path
        d="M12 2C12 7.5 7.5 12 2 12C7.5 12 12 16.5 12 22C12 16.5 16.5 12 22 12C16.5 12 12 7.5 12 2Z"
        fill="url(#gemini-grad)"
      />
    </svg>
  );
}

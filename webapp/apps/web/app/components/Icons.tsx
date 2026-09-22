/* Hand-written rather than an icon package: the app carries no UI library, and
   a dozen outline glyphs do not justify starting one. 24px grid, 1.8px stroke. */

export type IconName =
  | "photos" | "spark" | "albums" | "documents" | "screenshots" | "pets" | "places" | "search" | "help";

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
};

export function Icon({ name, size = 22 }: { name: IconName; size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
      {PATHS[name]}
    </svg>
  );
}

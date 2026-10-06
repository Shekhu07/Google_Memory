import { fallbackExtract, fallbackSearch, BUNDLED_PHOTOS } from '../fallback';

describe('Fallback Retrieval Engine', () => {
  it('extracts primary and suggested scene words', () => {
    const res = fallbackExtract('cafe in Bengaluru with friends, dosa on the table');
    expect(res.filters.location).toBe('Bengaluru');
    expect(res.filters.category).toBeDefined();
    expect(res.suggested_categories).toBeDefined();
    expect(res.suggested_categories!.length).toBeGreaterThan(0);
    const all = [res.filters.category, ...(res.suggested_categories || []).map((s) => s.category)];
    expect(all).toContain('cafe');
    expect(all).toContain('dosa');
  });

  it('ranks full-match candidate cards first', () => {
    const filters = {
      location: 'Bengaluru',
      category: 'cafe',
    };
    const results = fallbackSearch(filters);
    expect(results.length).toBeGreaterThan(0);
    expect(results[0].clue_hits).toBeGreaterThan(0);
    expect(results[0].full_match).toBe(true);
  });

  it('contains bundled photos dataset spanning multiple locations and categories', () => {
    expect(BUNDLED_PHOTOS.length).toBeGreaterThan(10);
    const locations = new Set(BUNDLED_PHOTOS.map((p) => p.location));
    expect(locations.has('Bengaluru')).toBe(true);
  });
});

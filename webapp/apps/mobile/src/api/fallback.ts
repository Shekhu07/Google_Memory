import { Episode, ExtractResult, FacetsResult, Filters, Photo, SuggestedCategory, Chip } from './types';

export const BUNDLED_PHOTOS: Photo[] = [
  // Bengaluru cafe & food (Singletons & episode)
  { id: 'demo:0101', file: 'library/0101.jpg', date: '2026-05-24T10:15:00', location: 'Bengaluru', category: 'cafe', episode: '' },
  { id: 'demo:0102', file: 'library/0102.jpg', date: '2026-05-24T10:30:00', location: 'Bengaluru', category: 'food', episode: '' },
  { id: 'demo:0103', file: 'library/0103.jpg', date: '2026-05-28T16:00:00', location: 'Bengaluru', category: 'cafe', episode: 'weekend cafe trail' },
  { id: 'demo:0104', file: 'library/0104.jpg', date: '2026-05-28T16:45:00', location: 'Bengaluru', category: 'food', episode: 'weekend cafe trail' },
  { id: 'demo:0105', file: 'library/0105.jpg', date: '2026-05-28T17:15:00', location: 'Bengaluru', category: 'street', episode: 'weekend cafe trail' },

  // Fever week receipts (Bengaluru Feb 2024 / 2026)
  { id: 'demo:0000', file: 'library/0000.jpg', date: '2026-02-21T14:37:00', location: 'Bengaluru', category: 'receipt', episode: 'fever week' },
  { id: 'demo:0001', file: 'library/0001.jpg', date: '2026-02-22T12:19:00', location: 'Bengaluru', category: 'receipt', episode: 'fever week' },
  { id: 'demo:0002', file: 'library/0002.jpg', date: '2026-02-20T19:11:00', location: 'Bengaluru', category: 'medicine', episode: 'fever week' },

  // Goa trip (Beach & party)
  { id: 'demo:0201', file: 'library/0201.jpg', date: '2025-12-31T20:00:00', location: 'Goa', category: 'beach', episode: 'new year goa' },
  { id: 'demo:0202', file: 'library/0202.jpg', date: '2026-01-01T01:30:00', location: 'Goa', category: 'festival', episode: 'new year goa' },
  { id: 'demo:0203', file: 'library/0203.jpg', date: '2026-01-01T15:00:00', location: 'Goa', category: 'beach', episode: 'new year goa' },

  // Graduation & performance
  { id: 'demo:0301', file: 'library/0301.jpg', date: '2026-06-15T11:00:00', location: 'Bengaluru', category: 'graduation', episode: "sister's graduation" },
  { id: 'demo:0302', file: 'library/0302.jpg', date: '2026-06-15T12:30:00', location: 'Bengaluru', category: 'cake', episode: "sister's graduation" },
  { id: 'demo:0303', file: 'library/0303.jpg', date: '2026-04-10T19:00:00', location: 'Bengaluru', category: 'performance', episode: 'college performance' },
  { id: 'demo:0304', file: 'library/0304.jpg', date: '2026-04-10T21:00:00', location: 'Bengaluru', category: 'performance', episode: 'college performance' },

  // Pet and home
  { id: 'demo:0401', file: 'library/0401.jpg', date: '2026-03-05T09:00:00', location: 'Bengaluru', category: 'pet', episode: 'puppy vet visits' },
  { id: 'demo:0402', file: 'library/0402.jpg', date: '2026-03-12T14:00:00', location: 'Bengaluru', category: 'pet', episode: 'puppy vet visits' },

  // Mountain & Kochi
  { id: 'demo:0501', file: 'library/0501.jpg', date: '2026-07-18T10:00:00', location: 'Manali', category: 'mountain', episode: 'himalayan trek' },
  { id: 'demo:0502', file: 'library/0502.jpg', date: '2026-08-25T13:00:00', location: 'Kochi', category: 'food', episode: 'onam lunch' },
  { id: 'demo:0503', file: 'library/0503.jpg', date: '2026-08-25T15:00:00', location: 'Kochi', category: 'festival', episode: 'onam lunch' },
];

const LOCATIONS = ['Bengaluru', 'Goa', 'Kochi', 'Manali', 'Mumbai', 'Chennai', 'Mysuru', 'Hyderabad'];

const CATEGORY_SYNONYMS: Record<string, string> = {
  cafe: 'cafe',
  café: 'cafe',
  coffee: 'cafe',
  restaurant: 'cafe',
  dosa: 'dosa',
  food: 'food',
  friends: 'friends',
  dinner: 'food',
  meal: 'food',
  beach: 'beach',
  sea: 'beach',
  mountain: 'mountain',
  trek: 'mountain',
  hill: 'mountain',
  pet: 'pet',
  dog: 'pet',
  puppy: 'pet',
  cat: 'pet',
  graduation: 'graduation',
  convocation: 'graduation',
  cake: 'cake',
  performance: 'performance',
  dance: 'performance',
  receipt: 'receipt',
  bill: 'receipt',
  medicine: 'medicine',
  prescription: 'medicine',
  festival: 'festival',
  onam: 'festival',
  diwali: 'festival',
};

const CATEGORY_LABELS: Record<string, string> = {
  cafe: 'café',
  food: 'food',
  dosa: 'dosa',
  friends: 'friends',
  beach: 'beach',
  mountain: 'mountain',
  pet: 'pet',
  graduation: 'graduation',
  cake: 'cake',
  performance: 'performance',
  receipt: 'receipt',
  medicine: 'medicine',
  festival: 'festival',
};

export function fallbackExtract(query: string): ExtractResult {
  const low = query.toLowerCase();
  const filters: Filters = {};
  const chips: Chip[] = [];
  const suggested: SuggestedCategory[] = [];
  let chipId = 1;

  // 1. Location matching
  for (const loc of LOCATIONS) {
    if (new RegExp(`\\b${loc.toLowerCase()}\\b`, 'i').test(low)) {
      filters.location = loc;
      chips.push({
        id: `c_${chipId++}`,
        cue: 'location',
        label: loc,
        filter_key: 'location',
        value: loc,
        editable: true,
      });
      break;
    }
  }

  // 2. Date clues (Month recognition)
  const monthNames = [
    'january', 'february', 'march', 'april', 'may', 'june',
    'july', 'august', 'september', 'october', 'november', 'december'
  ];
  for (let m = 0; m < monthNames.length; m++) {
    const month = monthNames[m];
    if (new RegExp(`\\b${month}\\b`, 'i').test(low)) {
      const monthNum = String(m + 1).padStart(2, '0');
      const year = '2026';
      filters.date_from = `${year}-${monthNum}-01`;
      filters.date_to = `${year}-${monthNum}-28`;
      chips.push({
        id: `c_${chipId++}`,
        cue: 'time',
        label: `${month.charAt(0).toUpperCase() + month.slice(1)} ${year}`,
        filter_key: 'date_window',
        value: filters.date_from,
        value_to: filters.date_to,
        editable: true,
      });
      break;
    }
  }

  // 3. Category matching (multi-match)
  const matchedCategories: { word: string; category: string }[] = [];
  const words = Object.keys(CATEGORY_SYNONYMS).sort((a, b) => b.length - a.length);
  for (const word of words) {
    if (new RegExp(`\\b${word}\\b`, 'i').test(low)) {
      const cat = CATEGORY_SYNONYMS[word];
      if (!matchedCategories.some((mc) => mc.category === cat)) {
        matchedCategories.push({ word, category: cat });
      }
    }
  }

  if (matchedCategories.length > 0) {
    const primary = matchedCategories[0];
    filters.category = primary.category;
    chips.push({
      id: `c_${chipId++}`,
      cue: 'object',
      label: CATEGORY_LABELS[primary.category] || primary.category,
      filter_key: 'category',
      value: primary.category,
      editable: true,
    });

    for (let i = 1; i < matchedCategories.length; i++) {
      const sec = matchedCategories[i];
      suggested.push({
        category: sec.category,
        word: sec.word,
        label: CATEGORY_LABELS[sec.category] || sec.category,
      });
    }
  }

  return {
    filters,
    chips,
    suggested_categories: suggested,
    source: 'offline_fallback',
  };
}

export function fallbackSearch(filters: Filters): Episode[] {
  // Candidate grouping
  const groupMap: Record<string, { photos: Photo[]; episode: string; episode_id: string; location: string }> = {};

  for (const photo of BUNDLED_PHOTOS) {
    const key = photo.episode ? `ep_${photo.episode}` : `single_${photo.id}`;
    if (!groupMap[key]) {
      groupMap[key] = {
        photos: [],
        episode: photo.episode || '',
        episode_id: photo.episode ? key : '',
        location: photo.location || '',
      };
    }
    groupMap[key].photos.push(photo);
  }

  const queryDims: string[] = [];
  if (filters.location) queryDims.push('location');
  if (filters.category) queryDims.push('category');
  if (filters.date_from || filters.date_to) queryDims.push('date');

  const episodes: Episode[] = [];

  for (const [key, grp] of Object.entries(groupMap)) {
    const photos = grp.photos;
    const dates = photos.map((p) => p.date || '').filter(Boolean).sort();
    const dateFrom = dates[0] ? dates[0].slice(0, 10) : null;
    const dateTo = dates[dates.length - 1] ? dates[dates.length - 1].slice(0, 10) : null;

    let hits = 0;
    if (filters.location && photos.some((p) => p.location?.toLowerCase() === filters.location.toLowerCase())) {
      hits += 1;
    }
    if (filters.category && photos.some((p) => p.category?.toLowerCase() === filters.category.toLowerCase())) {
      hits += 1;
    }
    if ((filters.date_from || filters.date_to) && dateFrom && dateTo) {
      const from = filters.date_from || '1970-01-01';
      const to = filters.date_to || '2099-12-31';
      if (dateTo >= from && dateFrom <= to) {
        hits += 1;
      }
    }

    const fullMatch = queryDims.length > 0 && hits >= queryDims.length;
    const usefulness = Math.round((0.5 * (hits / (queryDims.length || 1)) + 0.3 * Math.min(1, photos.length / 5)) * 100) / 100;

    episodes.push({
      episode_id: grp.episode_id,
      episode: grp.episode,
      location: grp.location || photos[0]?.location || '',
      date_from: dateFrom,
      date_to: dateTo,
      count: photos.length,
      episode_total: photos.length,
      places: 1,
      scenes: [[photos[0]?.category || 'photo', photos.length]],
      span_days: 1,
      usefulness,
      clue_hits: hits,
      full_match: fullMatch,
      why: [
        { kind: 'location', value: grp.location || '' },
        { kind: 'category', value: photos[0]?.category || '' },
      ],
      evidence: [
        { dimension: 'Place', value: grp.location || '', certainty: 'strong', source: 'metadata' },
        { dimension: 'Date', value: `${dateFrom || ''} to ${dateTo || ''}`, certainty: 'strong', source: 'metadata' },
      ],
      photos: photos.map((p) => ({ id: p.id, file: p.file, date: p.date, location: p.location, category: p.category })),
    });
  }

  // Sort by (-clue_hits, -usefulness, -photos.length)
  episodes.sort((a, b) => {
    if ((b.clue_hits || 0) !== (a.clue_hits || 0)) {
      return (b.clue_hits || 0) - (a.clue_hits || 0);
    }
    if (b.usefulness !== a.usefulness) {
      return b.usefulness - a.usefulness;
    }
    return b.count - a.count;
  });

  return episodes;
}

export function fallbackFacets(): FacetsResult {
  return {
    locations: LOCATIONS,
    categories: Object.values(CATEGORY_LABELS),
    episodes: ["weekend cafe trail", "fever week", "new year goa", "sister's graduation", "college performance", "puppy vet visits"],
    top_anchors: [
      { id: 'a1', cue: 'event_anchor', kind_label: 'An event', label: 'graduation', filter_key: 'episode', value: "sister's graduation" },
      { id: 'a2', cue: 'object', kind_label: 'An object', label: 'café', filter_key: 'category', value: 'cafe' },
      { id: 'a3', cue: 'object', kind_label: 'People', label: 'friends', filter_key: 'category', value: 'friends' },
    ],
    monthly_chapters: [
      { month: '2026-08', label: 'August 2026', date_from: '2026-08-01', date_to: '2026-08-31', count: 2, thumbnail: 'library/0502.jpg' },
      { month: '2026-07', label: 'July 2026', date_from: '2026-07-01', date_to: '2026-07-31', count: 1, thumbnail: 'library/0501.jpg' },
      { month: '2026-06', label: 'June 2026', date_from: '2026-06-01', date_to: '2026-06-30', count: 2, thumbnail: 'library/0301.jpg' },
      { month: '2026-05', label: 'May 2026', date_from: '2026-05-01', date_to: '2026-05-31', count: 5, thumbnail: 'library/0101.jpg' },
      { month: '2026-04', label: 'April 2026', date_from: '2026-04-01', date_to: '2026-04-30', count: 2, thumbnail: 'library/0303.jpg' },
      { month: '2026-03', label: 'March 2026', date_from: '2026-03-01', date_to: '2026-03-31', count: 2, thumbnail: 'library/0401.jpg' },
      { month: '2026-02', label: 'February 2026', date_from: '2026-02-01', date_to: '2026-02-28', count: 3, thumbnail: 'library/0000.jpg' },
      { month: '2026-01', label: 'January 2026', date_from: '2026-01-01', date_to: '2026-01-31', count: 2, thumbnail: 'library/0202.jpg' },
    ],
    demo_today: '2026-09-23',
  };
}

import { Episode, ExtractResult, FacetsResult, Filters } from './types';
import { fallbackExtract, fallbackFacets, fallbackSearch } from './fallback';

export const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

const TIMEOUT_MS = 2500;

async function fetchWithTimeout(url: string, options: RequestInit = {}): Promise<Response> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const res = await fetch(url, { ...options, signal: controller.signal });
    clearTimeout(id);
    return res;
  } catch (err) {
    clearTimeout(id);
    throw err;
  }
}

export async function extractClues(query: string): Promise<ExtractResult> {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/api/py/extract`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return {
      filters: data.filters || {},
      chips: data.chips || [],
      suggested_categories: data.suggested_categories || [],
      source: data.source || 'server',
      notice: data.notice || null,
    };
  } catch (_err) {
    // Network failure or backend offline: return rich offline fallback
    return fallbackExtract(query);
  }
}

export async function searchMoments(filters: Filters): Promise<Episode[]> {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/api/py/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filters }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data.results || [];
  } catch (_err) {
    return fallbackSearch(filters);
  }
}

export async function getFacets(): Promise<FacetsResult> {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/api/py/facets`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (_err) {
    return fallbackFacets();
  }
}

export function resolvePhotoUri(file: string): string {
  if (file.startsWith('http://') || file.startsWith('https://')) {
    return file;
  }
  // If running with local web server or static server
  const clean = file.replace(/^\/?(library\/)?/, '');
  return `http://localhost:3000/library/${clean}`;
}

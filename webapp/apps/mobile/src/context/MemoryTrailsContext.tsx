import React, { createContext, useContext, useState, useCallback } from 'react';
import * as Haptics from 'expo-haptics';
import { Chip, Episode, Filters, Photo, SuggestedCategory } from '../api/types';
import { extractClues, searchMoments } from '../api/client';

export type Stage = 'idle' | 'compose' | 'recap' | 'moments' | 'confirmed';
export type Tab = 'photos' | 'search' | 'library';

interface MemoryTrailsContextType {
  stage: Stage;
  setStage: (stage: Stage) => void;
  query: string;
  setQuery: (query: string) => void;
  chips: Chip[];
  suggestedCategories: SuggestedCategory[];
  filters: Filters;
  moments: Episode[];
  activeMoment: Episode | null;
  selectedPhoto: Photo | null;
  rejectedIds: string[];
  loading: boolean;
  activeTab: Tab;
  setActiveTab: (tab: Tab) => void;
  isSheetOpen: boolean;
  openSheet: () => void;
  closeSheet: () => void;
  runExtract: (text: string) => Promise<void>;
  addSuggestedCategory: (suggestion: SuggestedCategory) => Promise<void>;
  removeChip: (chipId: string) => void;
  runSearch: (overrideFilters?: Filters) => Promise<void>;
  selectMoment: (moment: Episode | null) => void;
  rejectEpisode: (episodeId: string) => void;
  restoreRejected: () => void;
  confirmMemory: (moment: Episode) => void;
  openPhotoViewer: (photo: Photo) => void;
  closePhotoViewer: () => void;
  resetSession: () => void;
}

const MemoryTrailsContext = createContext<MemoryTrailsContextType | undefined>(undefined);

export function MemoryTrailsProvider({ children }: { children: React.ReactNode }) {
  const [stage, setStage] = useState<Stage>('idle');
  const [query, setQuery] = useState('');
  const [chips, setChips] = useState<Chip[]>([]);
  const [suggestedCategories, setSuggestedCategories] = useState<SuggestedCategory[]>([]);
  const [filters, setFilters] = useState<Filters>({});
  const [moments, setMoments] = useState<Episode[]>([]);
  const [activeMoment, setActiveMoment] = useState<Episode | null>(null);
  const [selectedPhoto, setSelectedPhoto] = useState<Photo | null>(null);
  const [rejectedIds, setRejectedIds] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<Tab>('photos');
  const [isSheetOpen, setIsSheetOpen] = useState(false);

  const openSheet = useCallback(() => {
    setIsSheetOpen(true);
    if (stage === 'idle') {
      setStage('compose');
    }
  }, [stage]);

  const closeSheet = useCallback(() => {
    setIsSheetOpen(false);
  }, []);

  const runExtract = useCallback(async (text: string) => {
    setLoading(true);
    setQuery(text);
    try {
      const res = await extractClues(text);
      setFilters(res.filters || {});
      setChips(res.chips || []);
      setSuggestedCategories(res.suggested_categories || []);
      setStage('recap');

      // Auto-search candidate moments
      const results = await searchMoments(res.filters || {});
      setMoments(results);
    } catch (_err) {
      // Handled in client fallback
    } finally {
      setLoading(false);
    }
  }, []);

  const addSuggestedCategory = useCallback(async (suggestion: SuggestedCategory) => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    } catch {}

    const updatedFilters = { ...filters, category: suggestion.category };
    setFilters(updatedFilters);
    const newChip: Chip = {
      id: `c_cat_${Date.now()}`,
      cue: 'object',
      label: suggestion.label || suggestion.category,
      filter_key: 'category',
      value: suggestion.category,
      editable: true,
    };
    setChips((prev) => [...prev.filter((c) => c.filter_key !== 'category'), newChip]);
    setSuggestedCategories((prev) => prev.filter((item) => item.category !== suggestion.category));

    // Refresh candidate search with new category
    const res = await searchMoments(updatedFilters);
    setMoments(res);
  }, [filters]);

  const removeChip = useCallback((chipId: string) => {
    setChips((prev) => {
      const target = prev.find((c) => c.id === chipId);
      const remaining = prev.filter((c) => c.id !== chipId);
      if (target) {
        setFilters((currentFilters) => {
          const updated = { ...currentFilters };
          delete updated[target.filter_key];
          searchMoments(updated).then((res) => setMoments(res));
          return updated;
        });
      }
      return remaining;
    });
  }, []);

  const runSearch = useCallback(async (overrideFilters?: Filters) => {
    setLoading(true);
    try {
      const targetFilters = overrideFilters || filters;
      const res = await searchMoments(targetFilters);
      setMoments(res);
      setStage('moments');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  const selectMoment = useCallback((moment: Episode | null) => {
    setActiveMoment(moment);
  }, []);

  const rejectEpisode = useCallback((episodeId: string) => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    } catch {}
    setRejectedIds((prev) => (prev.includes(episodeId) ? prev : [...prev, episodeId]));
  }, []);

  const restoreRejected = useCallback(() => {
    setRejectedIds([]);
  }, []);

  const confirmMemory = useCallback((moment: Episode) => {
    try {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch {}
    setActiveMoment(moment);
    setStage('confirmed');
  }, []);

  const openPhotoViewer = useCallback((photo: Photo) => {
    setSelectedPhoto(photo);
  }, []);

  const closePhotoViewer = useCallback(() => {
    setSelectedPhoto(null);
  }, []);

  const resetSession = useCallback(() => {
    setStage('idle');
    setQuery('');
    setChips([]);
    setSuggestedCategories([]);
    setFilters({});
    setMoments([]);
    setActiveMoment(null);
    setRejectedIds([]);
  }, []);

  return (
    <MemoryTrailsContext.Provider
      value={{
        stage,
        setStage,
        query,
        setQuery,
        chips,
        suggestedCategories,
        filters,
        moments,
        activeMoment,
        selectedPhoto,
        rejectedIds,
        loading,
        activeTab,
        setActiveTab,
        isSheetOpen,
        openSheet,
        closeSheet,
        runExtract,
        addSuggestedCategory,
        removeChip,
        runSearch,
        selectMoment,
        rejectEpisode,
        restoreRejected,
        confirmMemory,
        openPhotoViewer,
        closePhotoViewer,
        resetSession,
      }}
    >
      {children}
    </MemoryTrailsContext.Provider>
  );
}

export function useMemoryTrails() {
  const context = useContext(MemoryTrailsContext);
  if (!context) {
    throw new Error('useMemoryTrails must be used within a MemoryTrailsProvider');
  }
  return context;
}

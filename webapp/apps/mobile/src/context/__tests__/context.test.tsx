import React, { useEffect } from 'react';
import TestRenderer, { act } from 'react-test-renderer';
import { MemoryTrailsProvider, useMemoryTrails } from '../MemoryTrailsContext';

// Mock expo-haptics
jest.mock('expo-haptics', () => ({
  impactAsync: jest.fn(),
  notificationAsync: jest.fn(),
  ImpactFeedbackStyle: { Light: 'light', Medium: 'medium', Heavy: 'heavy' },
  NotificationFeedbackType: { Success: 'success' },
}));

describe('MemoryTrailsContext', () => {
  let latestState: ReturnType<typeof useMemoryTrails> | null = null;

  function TestConsumer() {
    const trails = useMemoryTrails();
    latestState = trails;
    return null;
  }

  function renderWithProvider() {
    return TestRenderer.create(
      <MemoryTrailsProvider>
        <TestConsumer />
      </MemoryTrailsProvider>
    );
  }

  beforeEach(() => {
    latestState = null;
  });

  it('initializes with default state', () => {
    renderWithProvider();
    expect(latestState).not.toBeNull();
    expect(latestState!.stage).toBe('idle');
    expect(latestState!.query).toBe('');
    expect(latestState!.chips).toEqual([]);
    expect(latestState!.suggestedCategories).toEqual([]);
    expect(latestState!.selectedPhoto).toBeNull();
    expect(latestState!.rejectedIds).toEqual([]);
  });

  it('runs extraction and populates chips and suggestions', async () => {
    renderWithProvider();
    await act(async () => {
      await latestState!.runExtract('cafe in Bengaluru with friends, dosa on the table');
    });
    expect(latestState!.stage).toBe('recap');
    expect(latestState!.chips.length).toBeGreaterThan(0);
    expect(latestState!.suggestedCategories.length).toBeGreaterThan(0);
  });

  it('promotes a suggested category into active chips', async () => {
    renderWithProvider();
    await act(async () => {
      await latestState!.runExtract('cafe in Bengaluru with friends, dosa on the table');
    });
    const firstSuggested = latestState!.suggestedCategories[0];
    await act(async () => {
      await latestState!.addSuggestedCategory(firstSuggested);
    });
    const chipValues = latestState!.chips.map((c) => c.value);
    expect(chipValues).toContain(firstSuggested.category);
    expect(latestState!.suggestedCategories).not.toContain(firstSuggested);
  });

  it('rejects an episode and restores it', () => {
    renderWithProvider();
    act(() => {
      latestState!.rejectEpisode('ep_1');
    });
    expect(latestState!.rejectedIds).toContain('ep_1');
    act(() => {
      latestState!.restoreRejected();
    });
    expect(latestState!.rejectedIds).toEqual([]);
  });

  it('opens and closes photo viewer', () => {
    renderWithProvider();
    const dummyPhoto = { id: 'p1', file: 'p1.jpg' };
    act(() => {
      latestState!.openPhotoViewer(dummyPhoto);
    });
    expect(latestState!.selectedPhoto).toEqual(dummyPhoto);
    act(() => {
      latestState!.closePhotoViewer();
    });
    expect(latestState!.selectedPhoto).toBeNull();
  });
});

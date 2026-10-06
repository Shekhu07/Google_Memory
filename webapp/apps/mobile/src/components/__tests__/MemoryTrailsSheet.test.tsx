import React from 'react';
import TestRenderer, { act } from 'react-test-renderer';
import { Text as RNText } from 'react-native';
import { MemoryTrailsSheet } from '../MemoryTrailsSheet';
import { MemoryTrailsProvider, useMemoryTrails } from '../../context/MemoryTrailsContext';

describe('MemoryTrailsSheet', () => {
  let trailsRef: ReturnType<typeof useMemoryTrails> | null = null;

  function TestConsumer() {
    trailsRef = useMemoryTrails();
    return <MemoryTrailsSheet />;
  }

  function renderSheet() {
    let tree: TestRenderer.ReactTestRenderer;
    act(() => {
      tree = TestRenderer.create(
        <MemoryTrailsProvider>
          <TestConsumer />
        </MemoryTrailsProvider>
      );
    });
    return tree!;
  }

  beforeEach(() => {
    trailsRef = null;
  });

  it('renders compose stage initially with quick-start memories', () => {
    const tree = renderSheet();
    act(() => {
      trailsRef!.openSheet();
    });

    const root = tree.root;
    const texts = root.findAllByType(RNText).map((t) => t.props.children);
    expect(texts).toContain('Describe a moment you remember');
    expect(texts).toContain('Try an example:');
  });

  it('renders recap stage with clue kinds and "+ I also heard" suggestions', async () => {
    const tree = renderSheet();
    act(() => {
      trailsRef!.openSheet();
    });

    await act(async () => {
      await trailsRef!.runExtract('cafe in Bengaluru with friends, dosa on the table');
    });

    const root = tree.root;
    const texts = root.findAllByType(RNText).map((t) => String(t.props.children));
    expect(texts.some((t) => t.includes('Bengaluru'))).toBe(true);
    expect(texts.some((t) => t.includes('I also heard:'))).toBe(true);
  });

  it('renders full-match badges and singleton photo parity in moments stage', async () => {
    const tree = renderSheet();
    act(() => {
      trailsRef!.openSheet();
    });

    await act(async () => {
      await trailsRef!.runExtract('cafe in Bengaluru');
    });

    act(() => {
      trailsRef!.setStage('moments');
    });

    const root = tree.root;
    const texts = root.findAllByType(RNText).map((t) => String(t.props.children));
    expect(texts.some((t) => t.includes('Matches all your clues'))).toBe(true);
  });
});

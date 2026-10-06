import React from 'react';
import TestRenderer, { act } from 'react-test-renderer';
import { Text as RNText, TouchableOpacity } from 'react-native';
import { TimeRibbonNative, computeActiveMonthIndex } from '../TimeRibbonNative';
import { MonthlyChapter } from '../../api/types';

describe('TimeRibbonNative', () => {
  const chapters: MonthlyChapter[] = [
    { month: '2026-06', label: 'June 2026', date_from: '2026-06-01', date_to: '2026-06-30', count: 4, thumbnail: '1.jpg' },
    { month: '2026-05', label: 'May 2026', date_from: '2026-05-01', date_to: '2026-05-31', count: 5, thumbnail: '2.jpg' },
    { month: '2026-04', label: 'April 2026', date_from: '2026-04-01', date_to: '2026-04-30', count: 2, thumbnail: '3.jpg' },
  ];

  it('computes correct active index from activeDateFrom', () => {
    expect(computeActiveMonthIndex(chapters, '2026-05-15', null)).toBe(1);
    expect(computeActiveMonthIndex(chapters, null, null)).toBe(-1);
  });

  it('renders "Around that time" when date clue is present', () => {
    let tree: TestRenderer.ReactTestRenderer;
    act(() => {
      tree = TestRenderer.create(
        <TimeRibbonNative chapters={chapters} activeDateFrom="2026-05-01" activeDateTo="2026-05-31" />
      );
    });
    const root = tree!.root;
    const texts = root.findAllByType(RNText).map((t) => t.props.children);
    expect(texts).toContain('Around that time');
  });

  it('renders "Browse months" when no date clue is present', () => {
    let tree: TestRenderer.ReactTestRenderer;
    act(() => {
      tree = TestRenderer.create(
        <TimeRibbonNative chapters={chapters} activeDateFrom={null} activeDateTo={null} />
      );
    });
    const root = tree!.root;
    const texts = root.findAllByType(RNText).map((t) => t.props.children);
    expect(texts).toContain('Browse months');
  });

  it('calls onShiftMonth when a month pill is tapped', () => {
    const onShift = jest.fn();
    let tree: TestRenderer.ReactTestRenderer;
    act(() => {
      tree = TestRenderer.create(
        <TimeRibbonNative chapters={chapters} onShiftMonth={onShift} />
      );
    });
    const root = tree!.root;
    const touchables = root.findAllByType(TouchableOpacity);
    expect(touchables.length).toBeGreaterThan(0);
    act(() => {
      touchables[0].props.onPress();
    });
    expect(onShift).toHaveBeenCalledWith('2026-06-01', '2026-06-30');
  });
});

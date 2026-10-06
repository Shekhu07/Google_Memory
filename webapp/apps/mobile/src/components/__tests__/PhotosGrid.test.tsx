import React from 'react';
import TestRenderer, { act } from 'react-test-renderer';
import { Text as RNText } from 'react-native';
import { PhotosGrid, groupPhotosByMonth } from '../PhotosGrid';
import { MemoryTrailsProvider } from '../../context/MemoryTrailsContext';
import { Photo } from '../../api/types';

// Mock expo-image
jest.mock('expo-image', () => {
  const { View } = require('react-native');
  return {
    Image: (props: any) => <View {...props} testID="expo-image" />,
  };
});

describe('PhotosGrid', () => {
  const samplePhotos: Photo[] = [
    { id: '1', file: '1.jpg', date: '2026-05-24T10:00:00', location: 'Bengaluru' },
    { id: '2', file: '2.jpg', date: '2026-05-28T12:00:00', location: 'Bengaluru' },
    { id: '3', file: '3.jpg', date: '2026-02-21T14:00:00', location: 'Bengaluru' },
  ];

  it('groups photos into chronological monthly sections', () => {
    const groups = groupPhotosByMonth(samplePhotos);
    expect(groups.length).toBe(2);
    expect(groups[0].title).toBe('May 2026');
    expect(groups[0].photos.length).toBe(2);
    expect(groups[1].title).toBe('February 2026');
    expect(groups[1].photos.length).toBe(1);
  });

  it('renders photo grid with section headers and items', () => {
    let tree: TestRenderer.ReactTestRenderer;
    act(() => {
      tree = TestRenderer.create(
        <MemoryTrailsProvider>
          <PhotosGrid photos={samplePhotos} />
        </MemoryTrailsProvider>
      );
    });

    const root = tree!.root;
    const texts = root.findAllByType(RNText).map((t) => t.props.children);
    expect(texts).toContain('May 2026');
    expect(texts).toContain('February 2026');
  });
});

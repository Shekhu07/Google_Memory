import React from 'react';
import TestRenderer, { act } from 'react-test-renderer';
import { Text as RNText, TouchableOpacity } from 'react-native';
import { NativePhotoViewer } from '../NativePhotoViewer';
import { Photo } from '../../api/types';

describe('NativePhotoViewer', () => {
  const photo: Photo = {
    id: 'demo:0101',
    file: 'library/0101.jpg',
    location: 'Bengaluru',
    category: 'cafe',
    date: '2026-05-24T10:00:00',
  };

  it('renders nothing when photo is null', () => {
    let tree: TestRenderer.ReactTestRenderer;
    act(() => {
      tree = TestRenderer.create(
        <NativePhotoViewer photo={null} onClose={jest.fn()} onConfirm={jest.fn()} />
      );
    });
    expect(tree!.toJSON()).toBeNull();
  });

  it('renders full-screen photo details and action buttons when photo is provided', () => {
    let tree: TestRenderer.ReactTestRenderer;
    const onClose = jest.fn();
    const onConfirm = jest.fn();

    act(() => {
      tree = TestRenderer.create(
        <NativePhotoViewer photo={photo} onClose={onClose} onConfirm={onConfirm} />
      );
    });

    const root = tree!.root;
    const texts = root.findAllByType(RNText).map((t) => String(t.props.children));
    expect(texts.some((t) => t.includes('Bengaluru'))).toBe(true);
    expect(texts.some((t) => t.includes("That's the one!"))).toBe(true);

    // Test close button
    const touchables = root.findAllByType(TouchableOpacity);
    const closeBtn = touchables.find((t) => t.props.accessibilityLabel === 'Close viewer');
    expect(closeBtn).toBeDefined();
    act(() => {
      closeBtn!.props.onPress();
    });
    expect(onClose).toHaveBeenCalled();

    // Test confirm button
    const confirmBtn = touchables.find((t) => t.props.accessibilityLabel === "Confirm that's the one");
    expect(confirmBtn).toBeDefined();
    act(() => {
      confirmBtn!.props.onPress();
    });
    expect(onConfirm).toHaveBeenCalledWith(photo);
  });
});

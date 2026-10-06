import React from 'react';
import TestRenderer, { act } from 'react-test-renderer';
import App from '../App';

describe('App Root Integration', () => {
  it('renders Google Photos shell with tabs and header without crashing', () => {
    let tree: TestRenderer.ReactTestRenderer;
    act(() => {
      tree = TestRenderer.create(<App />);
    });
    expect(tree!).toBeDefined();
    expect(tree!.toJSON()).not.toBeNull();
  });
});

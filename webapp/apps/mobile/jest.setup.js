const React = require('react');

jest.mock('react-native', () => {
  const View = (props) => React.createElement('View', props, props.children);
  const Text = (props) => React.createElement('Text', props, props.children);
  const TouchableOpacity = ({ onPress, children, ...props }) =>
    React.createElement('TouchableOpacity', { onClick: onPress, onPress, ...props }, children);
  const ScrollView = (props) => React.createElement('ScrollView', props, props.children);
  const FlatList = ({ data, renderItem, keyExtractor, ...props }) => {
    return React.createElement(
      'View',
      props,
      data ? data.map((item, index) => {
        const key = keyExtractor ? keyExtractor(item, index) : index;
        return React.createElement('View', { key }, renderItem({ item, index }));
      }) : null
    );
  };
  const StyleSheet = {
    create: (styles) => styles,
    hairlineWidth: 1,
  };
  const Dimensions = {
    get: () => ({ width: 375, height: 812 }),
  };

  return {
    View,
    Text,
    TouchableOpacity,
    ScrollView,
    FlatList,
    StyleSheet,
    Dimensions,
    Platform: { OS: 'ios', select: (obj) => obj.ios || obj.default },
  };
});

jest.mock('expo-image', () => {
  return {
    Image: (props) => React.createElement('Image', props),
  };
});

jest.mock('expo-haptics', () => ({
  impactAsync: jest.fn(),
  notificationAsync: jest.fn(),
  ImpactFeedbackStyle: { Light: 'light', Medium: 'medium', Heavy: 'heavy' },
  NotificationFeedbackType: { Success: 'success' },
}));

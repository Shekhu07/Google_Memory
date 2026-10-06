const React = require('react');

jest.mock('react-native', () => {
  const View = React.forwardRef((props, ref) => React.createElement('View', { ref, ...props }, props.children));
  const Text = (props) => React.createElement('Text', props, props.children);
  const TextInput = React.forwardRef((props, ref) => React.createElement('TextInput', { ref, ...props }));
  const TouchableOpacity = ({ onPress, children, ...props }) =>
    React.createElement('TouchableOpacity', { onClick: onPress, onPress, ...props }, children);
  const ScrollView = React.forwardRef((props, ref) => {
    return React.createElement('ScrollView', { ref, ...props }, props.children);
  });
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
  const ActivityIndicator = (props) => React.createElement('ActivityIndicator', props);
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
    TextInput,
    ActivityIndicator,
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

jest.mock('@gorhom/bottom-sheet', () => {
  const BottomSheet = React.forwardRef(({ children, ...props }, ref) => {
    return React.createElement('View', { ref, testID: 'bottom-sheet', ...props }, children);
  });
  const BottomSheetView = ({ children, ...props }) =>
    React.createElement('View', props, children);
  const BottomSheetScrollView = React.forwardRef(({ children, ...props }, ref) =>
    React.createElement('ScrollView', { ref, ...props }, children)
  );
  const BottomSheetTextInput = React.forwardRef((props, ref) =>
    React.createElement('TextInput', { ref, ...props })
  );

  return {
    __esModule: true,
    default: BottomSheet,
    BottomSheetView,
    BottomSheetScrollView,
    BottomSheetTextInput,
  };
});

jest.mock('react-native-gesture-handler', () => {
  const GestureHandlerRootView = ({ children, ...props }) =>
    React.createElement('View', props, children);
  const GestureDetector = ({ children }) => React.createElement('View', null, children);
  const Gesture = {
    Pinch: () => ({ onUpdate: () => Gesture.Pinch(), onEnd: () => Gesture.Pinch() }),
    Pan: () => ({ onUpdate: () => Gesture.Pan(), onEnd: () => Gesture.Pan() }),
    Tap: () => ({ numberOfTaps: () => ({ onEnd: () => Gesture.Tap() }) }),
    Simultaneous: (...gestures) => ({ gestures }),
  };

  return {
    GestureHandlerRootView,
    GestureDetector,
    Gesture,
  };
});

jest.mock('react-native-reanimated', () => {
  const Reanimated = require('react-native');
  return {
    ...Reanimated,
    useSharedValue: (init) => ({ value: init }),
    useAnimatedStyle: (fn) => fn(),
    withSpring: (toValue) => toValue,
    withTiming: (toValue) => toValue,
    runOnJS: (fn) => fn,
  };
});

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Modal,
  Dimensions,
} from 'react-native';
import { Image } from 'expo-image';
import { GestureDetector, Gesture } from 'react-native-gesture-handler';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
  runOnJS,
} from 'react-native-reanimated';
import * as Haptics from 'expo-haptics';
import { Photo } from '../api/types';
import { resolvePhotoUri } from '../api/client';
import { Colors } from '../theme/colors';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

interface NativePhotoViewerProps {
  photo: Photo | null;
  onClose: () => void;
  onConfirm?: (photo: Photo) => void;
}

export function NativePhotoViewer({
  photo,
  onClose,
  onConfirm,
}: NativePhotoViewerProps) {
  if (!photo) return null;

  const scale = useSharedValue(1);
  const translateY = useSharedValue(0);

  // 1. Pinch to Zoom Gesture
  const pinchGesture = Gesture.Pinch()
    .onUpdate((e) => {
      scale.value = Math.min(Math.max(e.scale, 1), 4);
    })
    .onEnd(() => {
      if (scale.value < 1.1) {
        scale.value = withSpring(1);
      }
    });

  // 2. Double Tap Zoom Toggle
  const doubleTapGesture = Gesture.Tap()
    .numberOfTaps(2)
    .onEnd(() => {
      if (scale.value > 1.2) {
        scale.value = withSpring(1);
      } else {
        scale.value = withSpring(2.2);
      }
    });

  // 3. Swipe Down to Dismiss (when scale is 1)
  const panGesture = Gesture.Pan()
    .onUpdate((e) => {
      if (scale.value <= 1.05 && e.translationY > 0) {
        translateY.value = e.translationY;
      }
    })
    .onEnd((e) => {
      if (e.translationY > 150) {
        translateY.value = withTiming(SCREEN_HEIGHT, { duration: 200 }, () => {
          runOnJS(onClose)();
        });
      } else {
        translateY.value = withSpring(0);
      }
    });

  const composedGestures = Gesture.Simultaneous(
    pinchGesture,
    doubleTapGesture,
    panGesture
  );

  const animatedImageStyle = useAnimatedStyle(() => {
    return {
      transform: [
        { translateY: translateY.value },
        { scale: scale.value },
      ],
    };
  });

  const handleConfirm = () => {
    try {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch {}
    if (onConfirm) {
      onConfirm(photo);
    }
    onClose();
  };

  const handleClose = () => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    } catch {}
    onClose();
  };

  return (
    <Modal
      visible={true}
      transparent={false}
      animationType="fade"
      onRequestClose={handleClose}
    >
      <View style={styles.container}>
        {/* Top bar header */}
        <View style={styles.topBar}>
          <TouchableOpacity
            style={styles.closeBtn}
            onPress={handleClose}
            accessibilityRole="button"
            accessibilityLabel="Close viewer"
          >
            <Text style={styles.closeIcon}>✕</Text>
          </TouchableOpacity>

          <View style={styles.headerInfo}>
            <Text style={styles.headerLocation}>
              {photo.location || 'Photo'}
            </Text>
            {Boolean(photo.date) && (
              <Text style={styles.headerDate}>
                {photo.date?.slice(0, 10)}
              </Text>
            )}
          </View>

          <View style={{ width: 40 }} />
        </View>

        {/* Interactive Gesture Image Area */}
        <View style={styles.imageWrapper}>
          <GestureDetector gesture={composedGestures}>
            <Animated.View style={[styles.animatedWrap, animatedImageStyle]}>
              <Image
                source={{ uri: resolvePhotoUri(photo.file) }}
                style={styles.fullImage}
                contentFit="contain"
                transition={200}
              />
            </Animated.View>
          </GestureDetector>
        </View>

        {/* Bottom confirmation action */}
        <View style={styles.bottomBar}>
          <TouchableOpacity
            style={styles.confirmBtn}
            onPress={handleConfirm}
            accessibilityRole="button"
            accessibilityLabel="Confirm that's the one"
          >
            <Text style={styles.confirmBtnText}>That's the one!</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000000',
  },
  topBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 48,
    paddingHorizontal: 16,
    paddingBottom: 12,
    zIndex: 10,
  },
  closeBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  closeIcon: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '700',
  },
  headerInfo: {
    alignItems: 'center',
  },
  headerLocation: {
    color: '#ffffff',
    fontSize: 15,
    fontWeight: '600',
  },
  headerDate: {
    color: 'rgba(255, 255, 255, 0.7)',
    fontSize: 12,
    marginTop: 2,
  },
  imageWrapper: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  animatedWrap: {
    width: SCREEN_WIDTH,
    height: SCREEN_HEIGHT * 0.7,
  },
  fullImage: {
    width: '100%',
    height: '100%',
  },
  bottomBar: {
    paddingHorizontal: 24,
    paddingBottom: 40,
    alignItems: 'center',
  },
  confirmBtn: {
    backgroundColor: Colors.primary,
    borderRadius: 24,
    paddingVertical: 14,
    paddingHorizontal: 32,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
  },
  confirmBtnText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '700',
  },
});

import React, { useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { Image } from 'expo-image';
import * as Haptics from 'expo-haptics';
import { MonthlyChapter } from '../api/types';
import { resolvePhotoUri } from '../api/client';
import { Colors } from '../theme/colors';

export function computeActiveMonthIndex(
  chapters: MonthlyChapter[],
  activeDateFrom?: string | null,
  activeDateTo?: string | null
): number {
  const target = activeDateFrom || activeDateTo;
  if (!target) return -1;
  const monthKey = target.slice(0, 7);
  return chapters.findIndex((c) => c.month === monthKey);
}

interface TimeRibbonNativeProps {
  chapters: MonthlyChapter[];
  activeDateFrom?: string | null;
  activeDateTo?: string | null;
  onShiftMonth?: (dateFrom: string, dateTo: string) => void;
}

const ITEM_WIDTH = 130;

export function TimeRibbonNative({
  chapters,
  activeDateFrom,
  activeDateTo,
  onShiftMonth,
}: TimeRibbonNativeProps) {
  const scrollRef = useRef<ScrollView>(null);
  const activeIndex = computeActiveMonthIndex(chapters, activeDateFrom, activeDateTo);
  const hasDateClue = Boolean(activeDateFrom || activeDateTo);

  const title = hasDateClue ? 'Around that time' : 'Browse months';
  const subtitle = hasDateClue
    ? 'Shift to nearby months to explore surrounding moments'
    : 'Explore moments across the library timeline';

  useEffect(() => {
    if (activeIndex >= 0 && scrollRef.current) {
      // Center item horizontally in standard mobile screen width (~375)
      const offset = Math.max(0, activeIndex * (ITEM_WIDTH + 10) - 120);
      scrollRef.current.scrollTo({ x: offset, animated: true });
    }
  }, [activeIndex]);

  const handlePillPress = (chapter: MonthlyChapter) => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    } catch {}
    if (onShiftMonth) {
      onShiftMonth(chapter.date_from, chapter.date_to);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>{title}</Text>
        <Text style={styles.subtitle}>{subtitle}</Text>
      </View>

      <ScrollView
        ref={scrollRef}
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
      >
        {chapters.map((ch, idx) => {
          const isActive = idx === activeIndex;
          return (
            <TouchableOpacity
              key={ch.month}
              style={[styles.pill, isActive && styles.activePill]}
              activeOpacity={0.7}
              onPress={() => handlePillPress(ch)}
              accessibilityRole="button"
              accessibilityLabel={`${ch.label}, ${ch.count} moments`}
            >
              <Image
                source={{ uri: resolvePhotoUri(ch.thumbnail) }}
                style={styles.pillThumb}
                contentFit="cover"
              />
              <View style={styles.pillTextWrap}>
                <Text
                  style={[styles.pillLabel, isActive && styles.activePillLabel]}
                  numberOfLines={1}
                >
                  {ch.label}
                </Text>
                <Text style={styles.pillCount}>{ch.count} moments</Text>
              </View>
            </TouchableOpacity>
          );
        })}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginVertical: 12,
    backgroundColor: Colors.surface,
  },
  header: {
    paddingHorizontal: 16,
    marginBottom: 8,
  },
  title: {
    fontSize: 15,
    fontWeight: '700',
    color: Colors.textPrimary,
  },
  subtitle: {
    fontSize: 12,
    color: Colors.textSecondary,
    marginTop: 2,
  },
  scrollContent: {
    paddingHorizontal: 12,
    paddingVertical: 4,
  },
  pill: {
    width: ITEM_WIDTH,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.surfaceVariant,
    borderRadius: 20,
    padding: 6,
    marginRight: 10,
    borderWidth: 1.5,
    borderColor: 'transparent',
  },
  activePill: {
    borderColor: Colors.primary,
    backgroundColor: '#e8f0fe',
  },
  pillThumb: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#ccc',
  },
  pillTextWrap: {
    marginLeft: 8,
    flex: 1,
  },
  pillLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: Colors.textPrimary,
  },
  activePillLabel: {
    color: Colors.primary,
  },
  pillCount: {
    fontSize: 10,
    color: Colors.textSecondary,
    marginTop: 1,
  },
});

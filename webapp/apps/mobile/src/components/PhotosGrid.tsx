import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import { Image } from 'expo-image';
import { Photo } from '../api/types';
import { resolvePhotoUri } from '../api/client';
import { useMemoryTrails } from '../context/MemoryTrailsContext';
import { Colors } from '../theme/colors';

const { width } = Dimensions.get('window');
const COLUMN_COUNT = 3;
const SPACING = 2;
const ITEM_SIZE = (width - SPACING * (COLUMN_COUNT - 1)) / COLUMN_COUNT;

export interface MonthSection {
  monthKey: string;
  title: string;
  photos: Photo[];
}

export function groupPhotosByMonth(photos: Photo[]): MonthSection[] {
  const map: Record<string, Photo[]> = {};

  const sorted = [...photos].sort((a, b) => {
    const da = a.date || '';
    const db = b.date || '';
    return db.localeCompare(da);
  });

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December',
  ];

  for (const photo of sorted) {
    if (!photo.date) continue;
    const year = photo.date.slice(0, 4);
    const monthNum = parseInt(photo.date.slice(5, 7), 10);
    const monthName = monthNames[monthNum - 1] || 'Unknown';
    const key = `${year}-${photo.date.slice(5, 7)}`;
    const title = `${monthName} ${year}`;

    if (!map[key]) {
      map[key] = [];
    }
    map[key].push(photo);
  }

  return Object.keys(map)
    .sort((a, b) => b.localeCompare(a))
    .map((k) => {
      const year = k.slice(0, 4);
      const m = parseInt(k.slice(5, 7), 10);
      return {
        monthKey: k,
        title: `${monthNames[m - 1]} ${year}`,
        photos: map[k],
      };
    });
}

interface PhotosGridProps {
  photos: Photo[];
}

export function PhotosGrid({ photos }: PhotosGridProps) {
  const { openPhotoViewer } = useMemoryTrails();
  const sections = groupPhotosByMonth(photos);

  const renderSection = ({ item }: { item: MonthSection }) => {
    return (
      <View style={styles.sectionContainer}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>{item.title}</Text>
          <Text style={styles.photoCount}>{item.photos.length} photos</Text>
        </View>

        <View style={styles.gridRow}>
          {item.photos.map((photo) => (
            <TouchableOpacity
              key={photo.id}
              style={styles.photoItem}
              activeOpacity={0.8}
              onPress={() => openPhotoViewer(photo)}
              accessibilityRole="imagebutton"
              accessibilityLabel={`Photo from ${photo.location || 'unknown'}`}
            >
              <Image
                source={{ uri: resolvePhotoUri(photo.file) }}
                style={styles.thumbnail}
                contentFit="cover"
                transition={200}
              />
            </TouchableOpacity>
          ))}
        </View>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <FlatList
        data={sections}
        keyExtractor={(item) => item.monthKey}
        renderItem={renderSection}
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
      />

      {/* Google Photos Fast Date Scrubber on right edge */}
      <View style={styles.scrubber}>
        {sections.slice(0, 6).map((sec) => (
          <View key={sec.monthKey} style={styles.scrubberDot}>
            <Text style={styles.scrubberText}>
              {sec.title.slice(0, 3)}
            </Text>
          </View>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.surface,
  },
  listContent: {
    paddingBottom: 80,
  },
  sectionContainer: {
    marginBottom: 16,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 10,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: Colors.textPrimary,
  },
  photoCount: {
    fontSize: 12,
    color: Colors.textSecondary,
  },
  gridRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  photoItem: {
    width: ITEM_SIZE,
    height: ITEM_SIZE,
    marginBottom: SPACING,
    marginRight: SPACING,
  },
  thumbnail: {
    width: '100%',
    height: '100%',
    backgroundColor: Colors.surfaceVariant,
  },
  scrubber: {
    position: 'absolute',
    right: 4,
    top: 40,
    bottom: 80,
    justifyContent: 'space-around',
    alignItems: 'center',
    width: 28,
  },
  scrubberDot: {
    backgroundColor: 'rgba(255, 255, 255, 0.85)',
    borderRadius: 8,
    paddingHorizontal: 4,
    paddingVertical: 2,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: Colors.border,
  },
  scrubberText: {
    fontSize: 9,
    fontWeight: '600',
    color: Colors.textSecondary,
  },
});

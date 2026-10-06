import React, { useMemo } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { Colors } from './theme/colors';
import {
  MemoryTrailsProvider,
  useMemoryTrails,
} from './context/MemoryTrailsContext';
import { GooglePhotosHeader } from './components/GooglePhotosHeader';
import { BottomNav } from './components/BottomNav';
import { PhotosGrid } from './components/PhotosGrid';
import { MemoryTrailsSheet } from './components/MemoryTrailsSheet';
import { NativePhotoViewer } from './components/NativePhotoViewer';
import { BUNDLED_PHOTOS } from './api/fallback';

function AppContent() {
  const {
    activeTab,
    openSheet,
    selectedPhoto,
    closePhotoViewer,
    confirmMemory,
  } = useMemoryTrails();

  const photos = useMemo(() => BUNDLED_PHOTOS, []);

  return (
    <SafeAreaView style={styles.safeArea} edges={['top', 'left', 'right']}>
      <StatusBar style="auto" />

      {/* Top Google Photos Header with brand pinwheel & search pill */}
      <GooglePhotosHeader />

      {/* Main Tab Screen Content */}
      <View style={styles.mainContent}>
        {activeTab === 'photos' && <PhotosGrid photos={photos} />}

        {activeTab === 'search' && (
          <ScrollView contentContainerStyle={styles.searchTabContainer}>
            {/* Memory Trails Hero Launch Card */}
            <TouchableOpacity
              style={styles.heroCard}
              activeOpacity={0.85}
              onPress={openSheet}
              accessibilityRole="button"
            >
              <View style={styles.heroBadge}>
                <Text style={styles.heroBadgeText}>NEW FEATURE</Text>
              </View>
              <Text style={styles.heroTitle}>Memory Trails</Text>
              <Text style={styles.heroSubtitle}>
                Recall moments with vague, partial clues. Describe a place, time,
                or what you ate, and let Google Photos find the trail.
              </Text>
              <View style={styles.heroCta}>
                <Text style={styles.heroCtaText}>Try Memory Trails →</Text>
              </View>
            </TouchableOpacity>

            <View style={styles.exploreSection}>
              <Text style={styles.exploreSectionTitle}>All Photos in Library</Text>
              <PhotosGrid photos={photos} />
            </View>
          </ScrollView>
        )}

        {activeTab === 'library' && (
          <ScrollView contentContainerStyle={styles.libraryContainer}>
            <Text style={styles.libraryHeading}>Library</Text>
            <View style={styles.libraryGrid}>
              {['Favorites', 'Albums', 'Utilities', 'Archive', 'Trash'].map(
                (item) => (
                  <View key={item} style={styles.libraryCard}>
                    <Text style={styles.libraryCardTitle}>{item}</Text>
                  </View>
                )
              )}
            </View>
          </ScrollView>
        )}
      </View>

      {/* Material 3 Bottom Navigation Bar */}
      <BottomNav />

      {/* Native Gorhom Bottom Sheet for Memory Trails */}
      <MemoryTrailsSheet />

      {/* Full-screen Photo Viewer with gestures (pinch-zoom, swipe-down dismiss) */}
      <NativePhotoViewer
        photo={selectedPhoto}
        onClose={closePhotoViewer}
        onConfirm={(p) => {
          // If viewing from moment
          const ep = {
            episode_id: p.episode ? `ep_${p.episode}` : `single_${p.id}`,
            episode: p.episode || '',
            location: p.location || '',
            date_from: p.date ? p.date.slice(0, 10) : null,
            date_to: p.date ? p.date.slice(0, 10) : null,
            count: 1,
            episode_total: 1,
            places: 1,
            scenes: [[p.category || 'photo', 1] as [string, number]],
            span_days: 1,
            usefulness: 1,
            why: [],
            evidence: [],
            photos: [p],
          };
          confirmMemory(ep);
        }}
      />
    </SafeAreaView>
  );
}

export default function App() {
  return (
    <GestureHandlerRootView style={styles.root}>
      <SafeAreaProvider>
        <MemoryTrailsProvider>
          <AppContent />
        </MemoryTrailsProvider>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
  },
  safeArea: {
    flex: 1,
    backgroundColor: Colors.surface,
  },
  mainContent: {
    flex: 1,
  },
  searchTabContainer: {
    padding: 16,
  },
  heroCard: {
    backgroundColor: '#e8f0fe',
    borderRadius: 20,
    padding: 20,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#d2e3fc',
  },
  heroBadge: {
    alignSelf: 'flex-start',
    backgroundColor: Colors.primary,
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 8,
    marginBottom: 10,
  },
  heroBadgeText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  heroTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: Colors.textPrimary,
    marginBottom: 6,
  },
  heroSubtitle: {
    fontSize: 14,
    color: Colors.textSecondary,
    lineHeight: 20,
    marginBottom: 14,
  },
  heroCta: {
    alignSelf: 'flex-start',
  },
  heroCtaText: {
    color: Colors.primary,
    fontSize: 14,
    fontWeight: '700',
  },
  exploreSection: {
    marginTop: 8,
  },
  exploreSectionTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: Colors.textPrimary,
    marginBottom: 12,
  },
  libraryContainer: {
    padding: 16,
  },
  libraryHeading: {
    fontSize: 22,
    fontWeight: '700',
    color: Colors.textPrimary,
    marginBottom: 16,
  },
  libraryGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  libraryCard: {
    width: '47%',
    height: 100,
    backgroundColor: Colors.surfaceVariant,
    borderRadius: 16,
    padding: 16,
    justifyContent: 'flex-end',
    borderWidth: 1,
    borderColor: Colors.border,
  },
  libraryCardTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: Colors.textPrimary,
  },
});

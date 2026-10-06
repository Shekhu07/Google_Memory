import React, { useState, useMemo, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import BottomSheet, { BottomSheetScrollView } from '@gorhom/bottom-sheet';
import * as Haptics from 'expo-haptics';
import { useMemoryTrails } from '../context/MemoryTrailsContext';
import { ClueChipsBar } from './ClueChipsBar';
import { MomentsList } from './MomentsList';
import { TimeRibbonNative } from './TimeRibbonNative';
import { fallbackFacets } from '../api/fallback';
import { Colors } from '../theme/colors';

const SAMPLE_MEMORIES = [
  'cafe in Bengaluru with friends, dosa on the table',
  'weekend beach trip in Goa around new year',
  "sister's graduation cake in June 2026",
  'puppy vet visits in March',
];

export function MemoryTrailsSheet() {
  const {
    stage,
    setStage,
    query,
    setQuery,
    chips,
    suggestedCategories,
    filters,
    moments,
    activeMoment,
    rejectedIds,
    loading,
    isSheetOpen,
    closeSheet,
    runExtract,
    addSuggestedCategory,
    removeChip,
    rejectEpisode,
    restoreRejected,
    confirmMemory,
    openPhotoViewer,
    resetSession,
  } = useMemoryTrails();

  const [inputVal, setInputVal] = useState(query);
  const facets = useMemo(() => fallbackFacets(), []);
  const bottomSheetRef = useRef<BottomSheet>(null);
  const snapPoints = useMemo(() => ['45%', '85%', '95%'], []);

  if (!isSheetOpen) {
    return null;
  }

  const handleExtractSubmit = async (text: string) => {
    if (!text.trim()) return;
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    } catch {}
    await runExtract(text.trim());
  };

  const handleShiftMonth = (from: string, to: string) => {
    // Shifting month adds or updates date window chip
    const newChip = {
      id: `c_date_${Date.now()}`,
      cue: 'time',
      label: from.slice(0, 7),
      filter_key: 'date_window',
      value: from,
      value_to: to,
      editable: true,
    };
    runExtract(`${query} in ${from.slice(0, 7)}`);
  };

  return (
    <BottomSheet
      ref={bottomSheetRef}
      index={1}
      snapPoints={snapPoints}
      enablePanDownToClose
      onClose={closeSheet}
      backgroundStyle={styles.sheetBackground}
      handleIndicatorStyle={styles.sheetHandle}
    >
      <BottomSheetScrollView contentContainerStyle={styles.sheetContent}>
        {/* Header navigation bar inside sheet */}
        <View style={styles.sheetHeader}>
          <TouchableOpacity
            onPress={() => {
              if (stage === 'moments') setStage('recap');
              else if (stage === 'recap') setStage('compose');
              else closeSheet();
            }}
            style={styles.backBtn}
            accessibilityRole="button"
          >
            <Text style={styles.backBtnText}>
              {stage === 'compose' ? '✕' : '← Back'}
            </Text>
          </TouchableOpacity>

          <Text style={styles.headerTitle}>
            {stage === 'confirmed'
              ? 'Memory Retrieved'
              : stage === 'moments'
              ? 'Candidate Moments'
              : stage === 'recap'
              ? 'Understood Clues'
              : 'Memory Trails'}
          </Text>

          <TouchableOpacity
            onPress={resetSession}
            style={styles.resetBtn}
            accessibilityRole="button"
          >
            <Text style={styles.resetBtnText}>Reset</Text>
          </TouchableOpacity>
        </View>

        {/* STAGE 1: COMPOSE */}
        {stage === 'compose' && (
          <View style={styles.composeContainer}>
            <Text style={styles.sectionHeading}>
              Describe a moment you remember
            </Text>
            <Text style={styles.sectionSubheading}>
              Mention a place, month, season, person, or objects from the scene.
            </Text>

            <View style={styles.inputWrap}>
              <TextInput
                value={inputVal}
                onChangeText={setInputVal}
                placeholder="e.g. cafe in Bengaluru with friends..."
                placeholderTextColor={Colors.textTertiary}
                style={styles.textInput}
                multiline
                returnKeyType="done"
              />

              <TouchableOpacity
                style={[styles.submitBtn, loading && styles.submitBtnDisabled]}
                disabled={loading}
                onPress={() => handleExtractSubmit(inputVal)}
                accessibilityRole="button"
              >
                {loading ? (
                  <ActivityIndicator color="#ffffff" size="small" />
                ) : (
                  <Text style={styles.submitBtnText}>Find clues →</Text>
                )}
              </TouchableOpacity>
            </View>

            {/* Quick Starter Suggestions */}
            <View style={styles.examplesSection}>
              <Text style={styles.examplesTitle}>Try an example:</Text>
              {SAMPLE_MEMORIES.map((sample) => (
                <TouchableOpacity
                  key={sample}
                  style={styles.examplePill}
                  activeOpacity={0.7}
                  onPress={() => {
                    setInputVal(sample);
                    handleExtractSubmit(sample);
                  }}
                  accessibilityRole="button"
                >
                  <Text style={styles.exampleText}>"{sample}"</Text>
                </TouchableOpacity>
              ))}
            </View>

            {/* One-time disclaimer parked in info footer */}
            <Text style={styles.disclaimerText}>
              Concept prototype · Treats today as 23 Sep 2026. Private by default.
            </Text>
          </View>
        )}

        {/* STAGE 2: RECAP */}
        {stage === 'recap' && (
          <View style={styles.recapContainer}>
            <Text style={styles.sectionHeading}>
              Here is what we heard from your memory
            </Text>

            <ClueChipsBar
              chips={chips}
              suggestedCategories={suggestedCategories}
              onRemoveChip={removeChip}
              onAddSuggestedCategory={addSuggestedCategory}
            />

            <TimeRibbonNative
              chapters={facets.monthly_chapters}
              activeDateFrom={filters.date_from}
              activeDateTo={filters.date_to}
              onShiftMonth={handleShiftMonth}
            />

            <TouchableOpacity
              style={styles.seeMomentsBtn}
              onPress={() => setStage('moments')}
              accessibilityRole="button"
            >
              <Text style={styles.seeMomentsBtnText}>
                See candidate moments ({moments.length}) →
              </Text>
            </TouchableOpacity>
          </View>
        )}

        {/* STAGE 3: MOMENTS */}
        {stage === 'moments' && (
          <View style={styles.momentsContainer}>
            <ClueChipsBar
              chips={chips}
              suggestedCategories={suggestedCategories}
              onRemoveChip={removeChip}
              onAddSuggestedCategory={addSuggestedCategory}
            />

            <TimeRibbonNative
              chapters={facets.monthly_chapters}
              activeDateFrom={filters.date_from}
              activeDateTo={filters.date_to}
              onShiftMonth={handleShiftMonth}
            />

            <MomentsList
              moments={moments}
              rejectedIds={rejectedIds}
              onOpenPhoto={openPhotoViewer}
              onConfirm={confirmMemory}
              onReject={rejectEpisode}
              onRestoreRejected={restoreRejected}
            />
          </View>
        )}

        {/* STAGE 4: CONFIRMED */}
        {stage === 'confirmed' && (
          <View style={styles.confirmedContainer}>
            <Text style={styles.celebrationIcon}>🎉</Text>
            <Text style={styles.confirmedTitle}>Found it!</Text>
            <Text style={styles.confirmedSubtitle}>
              {activeMoment?.episode || `${activeMoment?.location} moment`} retrieved successfully.
            </Text>

            <TouchableOpacity
              style={styles.doneBtn}
              onPress={closeSheet}
              accessibilityRole="button"
            >
              <Text style={styles.doneBtnText}>Done</Text>
            </TouchableOpacity>
          </View>
        )}
      </BottomSheetScrollView>
    </BottomSheet>
  );
}

const styles = StyleSheet.create({
  sheetBackground: {
    backgroundColor: Colors.surface,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
  },
  sheetHandle: {
    backgroundColor: Colors.border,
    width: 36,
  },
  sheetContent: {
    paddingBottom: 40,
  },
  sheetHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: Colors.border,
  },
  backBtn: {
    padding: 6,
  },
  backBtnText: {
    color: Colors.primary,
    fontSize: 14,
    fontWeight: '600',
  },
  headerTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: Colors.textPrimary,
  },
  resetBtn: {
    padding: 6,
  },
  resetBtnText: {
    color: Colors.textSecondary,
    fontSize: 13,
  },
  composeContainer: {
    padding: 16,
  },
  sectionHeading: {
    fontSize: 18,
    fontWeight: '700',
    color: Colors.textPrimary,
    marginBottom: 4,
  },
  sectionSubheading: {
    fontSize: 13,
    color: Colors.textSecondary,
    marginBottom: 16,
  },
  inputWrap: {
    backgroundColor: Colors.surfaceVariant,
    borderRadius: 16,
    padding: 12,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  textInput: {
    fontSize: 15,
    color: Colors.textPrimary,
    minHeight: 70,
    textAlignVertical: 'top',
  },
  submitBtn: {
    backgroundColor: Colors.primary,
    borderRadius: 20,
    paddingVertical: 10,
    paddingHorizontal: 16,
    alignSelf: 'flex-end',
    marginTop: 8,
  },
  submitBtnDisabled: {
    opacity: 0.6,
  },
  submitBtnText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
  examplesSection: {
    marginTop: 10,
  },
  examplesTitle: {
    fontSize: 13,
    fontWeight: '600',
    color: Colors.textSecondary,
    marginBottom: 8,
  },
  examplePill: {
    backgroundColor: Colors.surfaceContainer,
    borderRadius: 12,
    padding: 10,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  exampleText: {
    fontSize: 13,
    color: Colors.primary,
    fontStyle: 'italic',
  },
  disclaimerText: {
    fontSize: 11,
    color: Colors.textTertiary,
    textAlign: 'center',
    marginTop: 24,
  },
  recapContainer: {
    paddingTop: 8,
  },
  seeMomentsBtn: {
    backgroundColor: Colors.primary,
    marginHorizontal: 16,
    marginTop: 16,
    paddingVertical: 12,
    borderRadius: 24,
    alignItems: 'center',
  },
  seeMomentsBtnText: {
    color: '#ffffff',
    fontSize: 15,
    fontWeight: '600',
  },
  momentsContainer: {
    paddingTop: 8,
  },
  confirmedContainer: {
    padding: 32,
    alignItems: 'center',
  },
  celebrationIcon: {
    fontSize: 48,
    marginBottom: 12,
  },
  confirmedTitle: {
    fontSize: 22,
    fontWeight: '700',
    color: Colors.textPrimary,
  },
  confirmedSubtitle: {
    fontSize: 14,
    color: Colors.textSecondary,
    textAlign: 'center',
    marginTop: 6,
    marginBottom: 24,
  },
  doneBtn: {
    backgroundColor: Colors.primary,
    paddingVertical: 12,
    paddingHorizontal: 36,
    borderRadius: 24,
  },
  doneBtnText: {
    color: '#ffffff',
    fontSize: 15,
    fontWeight: '600',
  },
});

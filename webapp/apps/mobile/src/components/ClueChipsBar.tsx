import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import * as Haptics from 'expo-haptics';
import { Chip, SuggestedCategory } from '../api/types';
import { Colors } from '../theme/colors';

export function getCueKindLabel(cue: string): string {
  switch (cue) {
    case 'place_named':
    case 'location':
      return 'Place';
    case 'exact_date':
    case 'time':
    case 'date_window':
      return 'Time';
    case 'people':
    case 'social':
      return 'Person';
    case 'event_anchor':
      return 'Event';
    case 'object':
    case 'category':
    default:
      return 'Scene';
  }
}

interface ClueChipsBarProps {
  chips: Chip[];
  suggestedCategories?: SuggestedCategory[];
  onRemoveChip?: (chipId: string) => void;
  onAddSuggestedCategory?: (suggestion: SuggestedCategory) => void;
}

export function ClueChipsBar({
  chips,
  suggestedCategories = [],
  onRemoveChip,
  onAddSuggestedCategory,
}: ClueChipsBarProps) {
  const handleRemove = (id: string) => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    } catch {}
    if (onRemoveChip) onRemoveChip(id);
  };

  const handleAdd = (s: SuggestedCategory) => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    } catch {}
    if (onAddSuggestedCategory) onAddSuggestedCategory(s);
  };

  return (
    <View style={styles.container}>
      {/* Active Clue Chips */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
      >
        {chips.map((chip) => (
          <TouchableOpacity
            key={chip.id}
            style={styles.chip}
            activeOpacity={0.7}
            onPress={() => handleRemove(chip.id)}
            accessibilityRole="button"
            accessibilityLabel={`${chip.label}, ${getCueKindLabel(chip.cue)}. Tap to remove`}
          >
            <View style={styles.chipKindBadge}>
              <Text style={styles.chipKindText}>{getCueKindLabel(chip.cue)}</Text>
            </View>
            <Text style={styles.chipLabel}>{chip.label}</Text>
            <Text style={styles.chipRemoveIcon}>✕</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Staged Suggestions: "I also heard: [+ cafe] [+ dosa]" */}
      {suggestedCategories.length > 0 && (
        <View style={styles.suggestionsContainer}>
          <Text style={styles.suggestionsTitle}>I also heard:</Text>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.suggestionsScroll}
          >
            {suggestedCategories.map((s) => (
              <TouchableOpacity
                key={s.category}
                style={styles.suggestionBtn}
                activeOpacity={0.7}
                onPress={() => handleAdd(s)}
                accessibilityRole="button"
                accessibilityLabel={`Add ${s.label || s.category} clue`}
              >
                <Text style={styles.suggestionBtnText}>
                  + {s.label || s.category}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginVertical: 8,
  },
  scrollContent: {
    paddingHorizontal: 16,
    paddingVertical: 4,
  },
  chip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#e8f0fe',
    borderRadius: 20,
    paddingVertical: 6,
    paddingHorizontal: 10,
    marginRight: 8,
    borderWidth: 1,
    borderColor: '#d2e3fc',
  },
  chipKindBadge: {
    backgroundColor: Colors.primary,
    borderRadius: 10,
    paddingHorizontal: 6,
    paddingVertical: 2,
    marginRight: 6,
  },
  chipKindText: {
    fontSize: 10,
    fontWeight: '700',
    color: '#ffffff',
    textTransform: 'uppercase',
  },
  chipLabel: {
    fontSize: 13,
    fontWeight: '600',
    color: Colors.textPrimary,
    marginRight: 6,
  },
  chipRemoveIcon: {
    fontSize: 12,
    color: Colors.textSecondary,
    fontWeight: '700',
  },
  suggestionsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    marginTop: 8,
  },
  suggestionsTitle: {
    fontSize: 12,
    fontWeight: '500',
    color: Colors.textSecondary,
    marginRight: 8,
  },
  suggestionsScroll: {
    alignItems: 'center',
  },
  suggestionBtn: {
    backgroundColor: Colors.surfaceVariant,
    borderRadius: 16,
    paddingVertical: 4,
    paddingHorizontal: 10,
    marginRight: 8,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  suggestionBtnText: {
    fontSize: 12,
    fontWeight: '600',
    color: Colors.primary,
  },
});

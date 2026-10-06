import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
} from 'react-native';
import { Image } from 'expo-image';
import * as Haptics from 'expo-haptics';
import { Episode, Photo } from '../api/types';
import { resolvePhotoUri } from '../api/client';
import { Colors } from '../theme/colors';

export function formatDateRange(from?: string | null, to?: string | null): string {
  if (!from && !to) return '';
  const formatDate = (iso: string) => {
    try {
      const d = new Date(iso);
      if (isNaN(d.getTime())) return iso;
      return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
    } catch {
      return iso;
    }
  };

  const f = from ? formatDate(from) : '';
  const t = to ? formatDate(to) : '';
  if (f && t && f !== t) return `${f} – ${t}`;
  return f || t;
}

interface MomentsListProps {
  moments: Episode[];
  rejectedIds: string[];
  onOpenPhoto: (photo: Photo) => void;
  onConfirm: (moment: Episode) => void;
  onReject: (episodeId: string) => void;
  onRestoreRejected: () => void;
}

export function MomentsList({
  moments,
  rejectedIds,
  onOpenPhoto,
  onConfirm,
  onReject,
  onRestoreRejected,
}: MomentsListProps) {
  const visibleMoments = moments.filter(
    (m) => !rejectedIds.includes(m.episode_id || m.photos[0]?.id)
  );

  return (
    <View style={styles.container}>
      {/* Ruled out undo banner */}
      {rejectedIds.length > 0 && (
        <View style={styles.undoBanner}>
          <Text style={styles.undoText}>
            Not showing {rejectedIds.length} moment{rejectedIds.length === 1 ? '' : 's'} you ruled out.
          </Text>
          <TouchableOpacity
            onPress={onRestoreRejected}
            style={styles.restoreBtn}
            accessibilityRole="button"
          >
            <Text style={styles.restoreBtnText}>Restore</Text>
          </TouchableOpacity>
        </View>
      )}

      {visibleMoments.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyTitle}>No matching moments found</Text>
          <Text style={styles.emptySubtitle}>
            Try adjusting your clues or clearing filters above.
          </Text>
        </View>
      ) : (
        <ScrollView contentContainerStyle={styles.cardsScroll}>
          {visibleMoments.map((ep, idx) => {
            const isFullMatch = Boolean(ep.full_match || (ep.clue_hits && ep.clue_hits > 0));
            const isNamed = Boolean(ep.episode);
            const coverPhoto = ep.photos[0];
            const dateStr = formatDateRange(ep.date_from, ep.date_to);

            return (
              <View key={ep.episode_id || idx} style={styles.card}>
                {/* Full match badge */}
                {isFullMatch && (
                  <View style={styles.fullMatchBadge}>
                    <Text style={styles.fullMatchText}>✓ Matches all your clues</Text>
                  </View>
                )}

                {/* Photo preview / contact sheet */}
                <TouchableOpacity
                  activeOpacity={0.85}
                  onPress={() => coverPhoto && onOpenPhoto(coverPhoto)}
                  style={styles.photoPreviewWrap}
                >
                  {coverPhoto && (
                    <Image
                      source={{ uri: resolvePhotoUri(coverPhoto.file) }}
                      style={styles.coverPhoto}
                      contentFit="cover"
                      transition={200}
                    />
                  )}
                  {ep.photos.length > 1 && (
                    <View style={styles.photoCountBadge}>
                      <Text style={styles.photoCountText}>+{ep.photos.length - 1} more</Text>
                    </View>
                  )}
                </TouchableOpacity>

                {/* Content info */}
                <View style={styles.cardInfo}>
                  <Text style={styles.cardTitle}>
                    {isNamed ? ep.episode : `${ep.location} ${ep.photos[0]?.category || 'Moment'}`}
                  </Text>
                  {Boolean(dateStr) && <Text style={styles.cardDate}>{dateStr}</Text>}
                  <Text style={styles.cardLocation}>{ep.location}</Text>
                </View>

                {/* Action buttons */}
                <View style={styles.cardActions}>
                  <TouchableOpacity
                    style={styles.notQuiteBtn}
                    onPress={() => onReject(ep.episode_id || coverPhoto?.id || '')}
                    accessibilityRole="button"
                  >
                    <Text style={styles.notQuiteText}>Not this</Text>
                  </TouchableOpacity>

                  <TouchableOpacity
                    style={styles.foundItBtn}
                    onPress={() => onConfirm(ep)}
                    accessibilityRole="button"
                  >
                    <Text style={styles.foundItText}>That's the one!</Text>
                  </TouchableOpacity>
                </View>
              </View>
            );
          })}
        </ScrollView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  undoBanner: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: Colors.surfaceVariant,
    paddingHorizontal: 16,
    paddingVertical: 8,
    marginHorizontal: 16,
    borderRadius: 8,
    marginBottom: 8,
  },
  undoText: {
    fontSize: 12,
    color: Colors.textSecondary,
    flex: 1,
  },
  restoreBtn: {
    paddingHorizontal: 8,
    paddingVertical: 4,
  },
  restoreBtnText: {
    color: Colors.primary,
    fontWeight: '700',
    fontSize: 12,
  },
  emptyContainer: {
    padding: 32,
    alignItems: 'center',
  },
  emptyTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: Colors.textPrimary,
  },
  emptySubtitle: {
    fontSize: 13,
    color: Colors.textSecondary,
    textAlign: 'center',
    marginTop: 6,
  },
  cardsScroll: {
    paddingHorizontal: 16,
    paddingBottom: 40,
  },
  card: {
    backgroundColor: Colors.surface,
    borderRadius: 16,
    marginBottom: 16,
    padding: 12,
    borderWidth: 1,
    borderColor: Colors.border,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
    elevation: 2,
  },
  fullMatchBadge: {
    alignSelf: 'flex-start',
    backgroundColor: Colors.fullMatchBg,
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 12,
    marginBottom: 8,
  },
  fullMatchText: {
    color: Colors.fullMatchGreen,
    fontSize: 11,
    fontWeight: '700',
  },
  photoPreviewWrap: {
    height: 180,
    borderRadius: 12,
    overflow: 'hidden',
    backgroundColor: Colors.surfaceVariant,
    position: 'relative',
  },
  coverPhoto: {
    width: '100%',
    height: '100%',
  },
  photoCountBadge: {
    position: 'absolute',
    bottom: 8,
    right: 8,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    borderRadius: 12,
    paddingHorizontal: 8,
    paddingVertical: 4,
  },
  photoCountText: {
    color: '#ffffff',
    fontSize: 11,
    fontWeight: '600',
  },
  cardInfo: {
    marginTop: 10,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: Colors.textPrimary,
  },
  cardDate: {
    fontSize: 12,
    color: Colors.textSecondary,
    marginTop: 2,
  },
  cardLocation: {
    fontSize: 12,
    color: Colors.textTertiary,
    marginTop: 1,
  },
  cardActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 12,
    paddingTop: 8,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: Colors.border,
  },
  notQuiteBtn: {
    paddingVertical: 8,
    paddingHorizontal: 12,
  },
  notQuiteText: {
    fontSize: 13,
    color: Colors.textSecondary,
    fontWeight: '500',
  },
  foundItBtn: {
    backgroundColor: Colors.primary,
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 20,
  },
  foundItText: {
    color: '#ffffff',
    fontSize: 13,
    fontWeight: '600',
  },
});

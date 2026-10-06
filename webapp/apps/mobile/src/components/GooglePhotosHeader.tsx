import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Colors } from '../theme/colors';
import { useMemoryTrails } from '../context/MemoryTrailsContext';

export function GooglePhotosHeader() {
  const { openSheet, setActiveTab } = useMemoryTrails();

  const handleSearchPress = () => {
    setActiveTab('search');
    openSheet();
  };

  return (
    <View style={styles.headerContainer}>
      <TouchableOpacity
        style={styles.searchBar}
        activeOpacity={0.8}
        onPress={handleSearchPress}
        accessibilityRole="button"
        accessibilityLabel="Search your photos, or find a memory"
      >
        {/* Google Pinwheel icon representation */}
        <View style={styles.pinwheel}>
          <View style={[styles.pinwheelPetal, { backgroundColor: Colors.googleBlue }]} />
          <View style={[styles.pinwheelPetal, { backgroundColor: Colors.googleRed }]} />
          <View style={[styles.pinwheelPetal, { backgroundColor: Colors.googleYellow }]} />
          <View style={[styles.pinwheelPetal, { backgroundColor: Colors.googleGreen }]} />
        </View>

        <Text style={styles.searchPlaceholder} numberOfLines={1}>
          Search your photos, or find a memory...
        </Text>

        {/* User avatar */}
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>A</Text>
        </View>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  headerContainer: {
    paddingHorizontal: 16,
    paddingTop: 8,
    paddingBottom: 8,
    backgroundColor: Colors.surface,
  },
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.surfaceVariant,
    borderRadius: 24,
    paddingHorizontal: 12,
    paddingVertical: 10,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  pinwheel: {
    width: 24,
    height: 24,
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginRight: 10,
  },
  pinwheelPetal: {
    width: 10,
    height: 10,
    borderRadius: 5,
    margin: 1,
  },
  searchPlaceholder: {
    flex: 1,
    fontSize: 15,
    color: Colors.textSecondary,
    fontWeight: '400',
  },
  avatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: Colors.googleBlue,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 8,
  },
  avatarText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
});

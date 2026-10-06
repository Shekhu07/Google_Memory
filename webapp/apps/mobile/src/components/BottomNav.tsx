import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Colors } from '../theme/colors';
import { Tab, useMemoryTrails } from '../context/MemoryTrailsContext';

export function BottomNav() {
  const { activeTab, setActiveTab, openSheet } = useMemoryTrails();

  const handleTabPress = (tab: Tab) => {
    setActiveTab(tab);
    if (tab === 'search') {
      openSheet();
    }
  };

  return (
    <View style={styles.navBar}>
      {/* Photos Tab */}
      <TouchableOpacity
        style={styles.tabButton}
        activeOpacity={0.7}
        onPress={() => handleTabPress('photos')}
        accessibilityRole="tab"
        accessibilityState={{ selected: activeTab === 'photos' }}
      >
        <View style={[styles.pill, activeTab === 'photos' && styles.activePill]}>
          <Text style={[styles.tabIcon, activeTab === 'photos' && styles.activeIcon]}>🖼</Text>
        </View>
        <Text style={[styles.tabLabel, activeTab === 'photos' && styles.activeLabel]}>Photos</Text>
      </TouchableOpacity>

      {/* Search / Trails Tab */}
      <TouchableOpacity
        style={styles.tabButton}
        activeOpacity={0.7}
        onPress={() => handleTabPress('search')}
        accessibilityRole="tab"
        accessibilityState={{ selected: activeTab === 'search' }}
      >
        <View style={[styles.pill, activeTab === 'search' && styles.activePill]}>
          <Text style={[styles.tabIcon, activeTab === 'search' && styles.activeIcon]}>🔍</Text>
        </View>
        <Text style={[styles.tabLabel, activeTab === 'search' && styles.activeLabel]}>Search</Text>
      </TouchableOpacity>

      {/* Library Tab */}
      <TouchableOpacity
        style={styles.tabButton}
        activeOpacity={0.7}
        onPress={() => handleTabPress('library')}
        accessibilityRole="tab"
        accessibilityState={{ selected: activeTab === 'library' }}
      >
        <View style={[styles.pill, activeTab === 'library' && styles.activePill]}>
          <Text style={[styles.tabIcon, activeTab === 'library' && styles.activeIcon]}>📁</Text>
        </View>
        <Text style={[styles.tabLabel, activeTab === 'library' && styles.activeLabel]}>Library</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  navBar: {
    flexDirection: 'row',
    backgroundColor: Colors.surface,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: Colors.border,
    paddingVertical: 6,
    paddingBottom: 16,
    justifyContent: 'space-around',
    alignItems: 'center',
  },
  tabButton: {
    alignItems: 'center',
    flex: 1,
  },
  pill: {
    width: 60,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 4,
  },
  activePill: {
    backgroundColor: '#c2e7ff', // Google active container pill
  },
  tabIcon: {
    fontSize: 18,
    color: Colors.textSecondary,
  },
  activeIcon: {
    color: Colors.primary,
  },
  tabLabel: {
    fontSize: 12,
    fontWeight: '500',
    color: Colors.textSecondary,
  },
  activeLabel: {
    color: Colors.textPrimary,
    fontWeight: '600',
  },
});

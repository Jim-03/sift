import React from 'react';
import { Modal, ScrollView, Text, TouchableOpacity, useColorScheme, View } from 'react-native';
import Animated, { FadeIn, SlideInDown } from 'react-native-reanimated';
import { RotateCcw, X } from 'lucide-react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { EmploymentType } from '@/lib/dto';

interface FiltersModalProps {
  visible: boolean;
  onClose: () => void;
  onApply: () => void;
  jobType: EmploymentType | null;
  setJobType: (val: EmploymentType | null) => void;
  read: boolean | null;
  setRead: (val: boolean | null) => void;
  applied: boolean | null;
  setApplied: (val: boolean | null) => void;
}

/**
 * Component rendering the filter modal
 * @param props
 * @param props.visible Condition to check if the modal is to be displayed
 * @param props.onClose State function triggered on closing the modal
 * @param props.onApply State function triggered on clicking the apply button
 * @param props.jobType Active job type
 * @param props.setJobType State function to change the job type
 * @param props.read View status
 * @param props.setRead State function to change the view status
 * @param props.applied Application status
 * @param props.setApplied State function to change the application status
 */
export default function FiltersModal({
  visible,
  onClose,
  onApply,
  jobType,
  setJobType,
  read,
  setRead,
  applied,
  setApplied,
}: FiltersModalProps) {
  const insets = useSafeAreaInsets();
  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';

  const iconText = isDark ? '#f8fafc' : '#0f172a'; // Slate 50 / 900
  const iconPrimary = '#6366f1'; // Indigo 500

  // Reset all filters
  const handleReset = () => {
    setJobType(null);
    setRead(null);
    setApplied(null);
  };

  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={onClose}>
      {/* BACKDROP */}
      <View className="flex-1 justify-end bg-slate-900/60">
        {/* BOTTOM SHEET */}
        <Animated.View
          entering={SlideInDown.duration(400)}
          className="rounded-t-3xl bg-white shadow-2xl dark:bg-slate-900"
          style={{ paddingBottom: insets.bottom || 24, maxHeight: '85%' }}>
          {/* HEADER */}
          <View className="flex-row items-center justify-between border-b border-slate-100 px-6 py-4 dark:border-slate-800">
            <TouchableOpacity onPress={handleReset} className="flex-row items-center">
              <RotateCcw color={iconPrimary} size={16} />
              <Text className="ml-1.5 text-sm font-bold text-indigo-500">Reset</Text>
            </TouchableOpacity>

            <Text className="text-lg font-extrabold text-slate-900 dark:text-white">Filters</Text>

            <TouchableOpacity
              onPress={onClose}
              className="h-8 w-8 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800">
              <X color={iconText} size={18} />
            </TouchableOpacity>
          </View>

          {/* SCROLLABLE FILTER CONTENT */}
          <ScrollView showsVerticalScrollIndicator={false} className="px-6 py-2">
            {/* EMPLOYMENT TYPE */}
            <FilterSection title="Employment Type">
              <View className="flex-row flex-wrap gap-3">
                <FilterPill
                  label="Any"
                  isActive={jobType === null}
                  onPress={() => setJobType(null)}
                />
                <FilterPill
                  label="Full-Time"
                  isActive={jobType === EmploymentType.FULL_TIME}
                  onPress={() => setJobType(EmploymentType.FULL_TIME)}
                />
                <FilterPill
                  label="Contract"
                  isActive={jobType === EmploymentType.CONTRACT}
                  onPress={() => setJobType(EmploymentType.CONTRACT)}
                />
                <FilterPill
                  label="Internship"
                  isActive={jobType === EmploymentType.INTERNSHIP}
                  onPress={() => setJobType(EmploymentType.INTERNSHIP)}
                />
              </View>
            </FilterSection>

            {/* READ STATUS */}
            <FilterSection title="View Status">
              <View className="flex-row flex-wrap gap-3">
                <FilterPill label="Any" isActive={read === null} onPress={() => setRead(null)} />
                <FilterPill
                  label="Unread"
                  isActive={read === false}
                  onPress={() => setRead(false)}
                />
                <FilterPill label="Read" isActive={read === true} onPress={() => setRead(true)} />
              </View>
            </FilterSection>

            {/* APPLIED STATUS */}
            <FilterSection title="Application Status">
              <View className="flex-row flex-wrap gap-3">
                <FilterPill
                  label="Any"
                  isActive={applied === null}
                  onPress={() => setApplied(null)}
                />
                <FilterPill
                  label="Not Applied"
                  isActive={applied === false}
                  onPress={() => setApplied(false)}
                />
                <FilterPill
                  label="Applied"
                  isActive={applied === true}
                  onPress={() => setApplied(true)}
                />
              </View>
            </FilterSection>
          </ScrollView>

          {/* FOOTER ACTION */}
          <View className="mt-2 border-t border-slate-100 px-6 pt-4 dark:border-slate-800">
            <TouchableOpacity
              onPress={onApply}
              activeOpacity={0.8}
              className="h-14 w-full items-center justify-center rounded-2xl bg-indigo-500 shadow-md shadow-indigo-200 dark:shadow-none">
              <Text className="text-lg font-bold text-white">Apply Filters</Text>
            </TouchableOpacity>
          </View>
        </Animated.View>
      </View>
    </Modal>
  );
}

function FilterSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <Animated.View
      entering={FadeIn.duration(300).delay(100)}
      className="border-b border-slate-50 py-5 dark:border-slate-800/50">
      <Text className="mb-4 text-base font-bold text-slate-900 dark:text-white">{title}</Text>
      {children}
    </Animated.View>
  );
}

function FilterPill({
  label,
  isActive,
  onPress,
}: {
  label: string;
  isActive: boolean;
  onPress: () => void;
}) {
  return (
    <TouchableOpacity
      onPress={onPress}
      activeOpacity={0.7}
      // REMOVED: shadow-sm shadow-indigo-200 dark:shadow-none
      className={`rounded-xl border px-4 py-2.5 ${
        isActive
          ? 'border-indigo-500 bg-indigo-500'
          : 'border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-slate-800'
      }`}
      // ADDED: Standard React Native shadow props for iOS, and elevation for Android
      style={
        isActive
          ? {
              shadowColor: '#818cf8',
              shadowOffset: { width: 0, height: 1 },
              shadowOpacity: 0.3,
              shadowRadius: 2,
              elevation: 2,
            }
          : undefined
      }>
      <Text
        className={`font-semibold ${
          isActive ? 'text-white' : 'text-slate-600 dark:text-slate-300'
        }`}>
        {label}
      </Text>
    </TouchableOpacity>
  );
}

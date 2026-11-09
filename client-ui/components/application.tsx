import React from 'react';
import { Modal, Text, TouchableOpacity, useColorScheme, View } from 'react-native';
import Animated, { FadeIn, ZoomIn } from 'react-native-reanimated';
import { Info } from 'lucide-react-native';

interface ApplyMarkerModalProps {
  visible: boolean;
  close: () => void;
  apply: () => void;
}

/**
 * Component displaying the application modal
 * @param props
 * @param props.visible Condition to check if the modal is visible
 * @param props.close Function triggered on closing the modal
 * @param props.apply Function triggered on clicking the mark button
 */
export default function ApplyMarkerModal({ visible, close, apply }: ApplyMarkerModalProps) {
  useColorScheme();
  const iconPrimary = '#6366f1'; // Indigo 500

  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={close}>
      {/* BACKDROP */}
      <Animated.View
        entering={FadeIn.duration(200)}
        className="flex-1 items-center justify-center bg-slate-900/60 px-6">
        {/* DIALOG BOX */}
        <Animated.View
          entering={ZoomIn.duration(300)}
          className="w-full rounded-3xl bg-white p-6 shadow-2xl dark:bg-slate-800">
          {/* ICON HEADER */}
          <View className="mb-4 h-14 w-14 items-center justify-center rounded-2xl bg-indigo-50 dark:bg-indigo-500/10">
            <Info color={iconPrimary} size={28} />
          </View>

          {/* TITLE & MESSAGE */}
          <Text className="mb-2 text-xl font-extrabold text-slate-900 dark:text-white">
            Mark as Applied?
          </Text>
          <Text className="mb-8 text-base leading-relaxed text-slate-500 dark:text-slate-400">
            This will only mark the job as applied in your SIFT dashboard for tracking purposes. You
            still need to submit your actual application on the company&#39;s official website.
          </Text>

          {/* ACTIONS */}
          <View className="flex-row items-center justify-end gap-3">
            <TouchableOpacity onPress={close} activeOpacity={0.7} className="rounded-xl px-5 py-3">
              <Text className="font-bold text-slate-500 dark:text-slate-400">Cancel</Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={() => {
                apply();
                close();
              }}
              activeOpacity={0.8}
              className="items-center justify-center rounded-xl bg-indigo-500 px-6 py-3 shadow-md shadow-indigo-200 dark:shadow-none">
              <Text className="font-bold text-white">OK, Mark it</Text>
            </TouchableOpacity>
          </View>
        </Animated.View>
      </Animated.View>
    </Modal>
  );
}

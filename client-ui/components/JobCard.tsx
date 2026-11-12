import React from 'react';
import { Text, TouchableOpacity, useColorScheme, View } from 'react-native';
import { Building2, CheckCircle, ChevronRight, Clock, Layers, Wallet } from 'lucide-react-native';
import { JobDto } from '@/lib/dto';

interface JobCardProps {
  job: JobDto;
  onPress?: () => void;
}

/**
 * Reusable component rendering the job card
 * @param props
 * @param props.job Job data
 * @param props.onPress Function triggered on pressing the job card
 */
export default function JobCard({ job, onPress }: JobCardProps) {
  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';

  const iconNeutral = isDark ? '#94a3b8' : '#64748b';
  const iconIndigo = '#6366f1';

  const formatDate = (dateString: string) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  };

  return (
    <TouchableOpacity
      onPress={onPress}
      activeOpacity={0.7}
      className="mb-4 rounded-2xl border border-slate-100 bg-white p-5 shadow-sm shadow-slate-200/50 dark:border-slate-700 dark:bg-slate-800 dark:shadow-none">
      {/* HEADER: Company, Date & Unread Indicator */}
      <View className="mb-3 flex-row items-center justify-between">
        <View className="flex-row items-center gap-3">
          <View className="h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 dark:bg-indigo-500/10">
            <Building2 color={iconIndigo} size={20} />
          </View>
          <Text className="text-sm font-semibold text-slate-700 dark:text-slate-300">
            {job.company}
          </Text>
        </View>
        <View className="flex-row items-center">
          {/* Unread indicator dot */}
          {!job.read && <View className="mr-2 h-2 w-2 rounded-full bg-indigo-500" />}
          <Clock color={iconNeutral} size={14} />
          <Text className="ml-1 text-xs font-medium text-slate-400 dark:text-slate-500">
            {formatDate(job.created_at)}
          </Text>
        </View>
      </View>

      {/* TITLE & DESCRIPTION */}
      <Text className="mb-2 text-lg font-bold text-slate-900 dark:text-white">{job.title}</Text>

      {/* description with 3-line truncation limit */}
      <Text
        className="mb-4 text-sm leading-relaxed text-slate-500 dark:text-slate-400"
        numberOfLines={3}>
        {job.description}
      </Text>

      {/* TAGS: Applied Status, Employment Type & Experience Level */}
      <View className="mb-4 flex-row flex-wrap gap-2">
        {/* Applied Tag */}
        {job.applied && (
          <View className="flex-row items-center rounded-lg bg-green-50 px-2.5 py-1.5 dark:bg-green-500/10">
            <CheckCircle color="#22c55e" size={12} />
            <Text className="ml-1.5 text-xs font-medium text-green-700 dark:text-green-400">
              Applied
            </Text>
          </View>
        )}

        <View className="flex-row items-center rounded-lg bg-slate-50 px-2.5 py-1.5 dark:bg-slate-700/50">
          <Layers color={iconNeutral} size={12} />
          <Text className="ml-1.5 text-xs font-medium capitalize text-slate-600 dark:text-slate-300">
            {job.employment_type?.toLowerCase().replace('-', ' ')}
          </Text>
        </View>

        <View className="flex-row items-center rounded-lg bg-slate-50 px-2.5 py-1.5 dark:bg-slate-700/50">
          <Text className="text-xs font-medium capitalize text-slate-600 dark:text-slate-300">
            {job.experience_level?.toLowerCase().replace('-', ' ')}
          </Text>
        </View>
      </View>

      {/* FOOTER: Salary & Action Arrow */}
      <View className="mt-2 flex-row items-center justify-between border-t border-slate-100 pt-3 dark:border-slate-700">
        <View className="flex-row items-center">
          <Wallet color={iconNeutral} size={16} />
          <Text className="ml-2 font-bold text-slate-900 dark:text-white">
            {job.salary || 'Salary undisclosed'}
          </Text>
        </View>
        <View className="h-8 w-8 items-center justify-center rounded-full bg-indigo-50 dark:bg-indigo-500/10">
          <ChevronRight color={iconIndigo} size={16} />
        </View>
      </View>
    </TouchableOpacity>
  );
}

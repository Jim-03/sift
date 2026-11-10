import React, { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  ScrollView,
  Text,
  TouchableOpacity,
  useColorScheme,
  View,
} from 'react-native';
import Animated, { FadeIn, FadeInDown, FadeInRight } from 'react-native-reanimated';
import {
  Briefcase,
  BriefcaseBusiness,
  CheckCircle,
  ChevronRight,
  House,
  Layers,
  Sparkles,
} from 'lucide-react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Tabs, useRouter } from 'expo-router';
import client from '@/lib/client';
import { Statistics } from '@/lib/dto';
import { AxiosError } from 'axios';
import JobCard from '@/components/JobCard';

export default function HomeScreen() {
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState<Statistics | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const loadData = async () => {
      try {
        const response = await client.get('/jobs/statistics');
        setStats(response.data as Statistics);
        setError(null);
      } catch (e) {
        if (e instanceof AxiosError) {
          const message =
            e.response?.data.detail || 'An error has occurred while fetching the statistics';
          setError(typeof message === 'string' ? message : 'Failed to load');
          console.error(message);
        }
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';

  const iconPrimary = '#6366f1';
  const iconNeutral = isDark ? '#94a3b8' : '#64748b';

  // --- LOADING STATE ---
  if (isLoading) {
    return (
      <SafeAreaView className="flex-1 items-center justify-center bg-slate-50 dark:bg-slate-900">
        <ActivityIndicator size="large" color={iconPrimary} />
        <Text className="mt-4 font-medium text-slate-500 dark:text-slate-400">
          Gathering your insights...
        </Text>
      </SafeAreaView>
    );
  }

  // --- ERROR STATE ---
  if (error || !stats) {
    return (
      <SafeAreaView className="flex-1 items-center justify-center bg-slate-50 px-6 dark:bg-slate-900">
        <BriefcaseBusiness color={iconNeutral} size={48} strokeWidth={1.5} />
        <Text className="mt-4 text-center text-lg font-bold text-slate-900 dark:text-white">
          Whoops!
        </Text>
        <Text className="mt-2 text-center font-medium text-slate-500 dark:text-slate-400">
          {error || 'Could not load your job dashboard.'}
        </Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView className="flex-1 bg-slate-50 dark:bg-slate-900">
      <Tabs.Screen options={{ tabBarIcon: () => <House /> }} />
      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{ paddingBottom: 40 }}>
        {/* HEADER */}
        <View className="flex-row items-center justify-between px-6 pb-4 pt-6">
          <View>
            <Text className="text-sm font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Welcome back
            </Text>
            <Text className="mt-1 text-3xl font-extrabold text-slate-900 dark:text-white">
              SIFT<Text className="text-indigo-500">.</Text>
            </Text>
          </View>
          {/* TODO: Implement notifications */}
          {/*
            <TouchableOpacity
              onPress={() => router.push('/notifications')}
              className="h-10 w-10 items-center justify-center rounded-full bg-slate-200 dark:bg-slate-800">
              <Bell color={iconText} size={20} />
            </TouchableOpacity>
          */}
        </View>

        {/* OVERVIEW STATS */}
        <Animated.View
          entering={FadeInDown.duration(500).delay(100)}
          className="mb-8 flex-row justify-between px-6">
          <StatCard
            title="Total in DB"
            value={stats.total_jobs.toLocaleString()}
            icon={<Briefcase color={iconPrimary} size={22} />}
          />
          <StatCard
            title="Best Match"
            value={stats.total_matches.toLocaleString()}
            icon={<Sparkles color="#eab308" size={22} />} // Yellow for matches
          />
          <StatCard
            title="Applied"
            value={stats.applied.toLocaleString()}
            icon={<CheckCircle color="#22c55e" size={22} />} // Green for applied
          />
        </Animated.View>

        {/* BEST MATCHES SECTION */}
        <View className="mb-8 px-5">
          <SectionHeader
            title="Best Matches"
            actionText="View all"
            action={() => router.push({ pathname: '/jobs', params: { mode: 'matches' } })}
          />

          {stats.best_match_jobs?.length === 0 ? (
            <EmptyState message="No best matches found right now. Keep sifting!" />
          ) : (
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={{ paddingHorizontal: 10, gap: 16 }}>
              {stats.best_match_jobs.map((job, index) => (
                <Animated.View key={job.id} entering={FadeInRight.duration(400).delay(index * 150)}>
                  <TouchableOpacity
                    className="w-72 rounded-3xl bg-indigo-500 p-5 shadow-lg shadow-indigo-200 dark:bg-indigo-600 dark:shadow-none"
                    activeOpacity={0.9}>
                    <View className="mb-4 flex-row items-start justify-between">
                      <View className="flex-row items-center gap-2">
                        <View className="rounded-full bg-white/20 px-3 py-1">
                          <Text className="text-xs font-bold text-white">Top Match</Text>
                        </View>

                        {/* Applied Indicator */}
                        {job.applied && (
                          <View className="rounded-full border border-green-300/30 bg-green-400/20 px-2.5 py-1">
                            <Text className="text-xs font-bold text-green-100">Applied</Text>
                          </View>
                        )}
                      </View>

                      {/* Unread Indicator */}
                      {!job.read && (
                        <View className="mt-1 h-2.5 w-2.5 rounded-full bg-yellow-300 shadow-sm shadow-yellow-200/50" />
                      )}
                    </View>

                    <Text className="mb-1 text-xl font-bold text-white" numberOfLines={1}>
                      {job.title}
                    </Text>
                    <Text className="mb-4 font-medium text-indigo-100">{job.company}</Text>

                    <View className="mt-auto flex-row items-center justify-between">
                      <View className="flex-row items-center">
                        <Layers color="#e0e7ff" size={14} />
                        <Text className="ml-1 text-sm capitalize text-indigo-100">
                          {job.employment_type.toLowerCase().replace('-', ' ')}
                        </Text>
                      </View>
                    </View>
                  </TouchableOpacity>
                </Animated.View>
              ))}
            </ScrollView>
          )}
        </View>

        {/* RECENT JOBS SECTION */}
        <View className="px-5">
          <SectionHeader
            title="Latest Arrivals"
            actionText="Browse"
            action={() => router.push({ pathname: '/jobs', params: { mode: 'browse' } })}
          />

          {stats.recent_jobs?.length === 0 ? (
            <EmptyState message="No new arrivals at the moment." />
          ) : (
            <View className="gap-4">
              {stats.recent_jobs.map((job, index) => (
                <JobCard
                  job={job}
                  key={index}
                  onPress={() => router.push({ pathname: '/job', params: { job_id: job.id } })}
                />
              ))}
            </View>
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

// --- SUBCOMPONENTS ---

function StatCard({
  title,
  value,
  icon,
}: {
  title: string;
  value: string | number;
  icon: React.ReactNode;
}) {
  return (
    <View className="w-[30%] items-center rounded-2xl border border-slate-100 bg-white p-3 shadow-sm shadow-slate-200/50 dark:border-slate-700 dark:bg-slate-800 dark:shadow-none">
      <View className="mb-2 rounded-full bg-slate-50 p-2 dark:bg-slate-700/50">{icon}</View>
      <Text className="text-lg font-bold text-slate-900 dark:text-white">{value}</Text>
      <Text className="mt-1 text-center text-xs font-medium text-slate-500 dark:text-slate-400">
        {title}
      </Text>
    </View>
  );
}

function SectionHeader({
  title,
  actionText,
  action,
}: {
  title: string;
  actionText: string;
  action: () => void;
}) {
  const iconPrimary = '#6366f1';

  return (
    <View className="mb-4 flex-row items-end justify-between">
      <Text className="text-xl font-bold text-slate-900 dark:text-white">{title}</Text>
      <TouchableOpacity className="flex-row items-center" onPress={action}>
        <Text className="mr-1 text-sm font-bold text-indigo-500">{actionText}</Text>
        <ChevronRight color={iconPrimary} size={16} />
      </TouchableOpacity>
    </View>
  );
}

function EmptyState({ message }: { message: string }) {
  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';

  return (
    <Animated.View
      entering={FadeIn.duration(400)}
      className="items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-slate-50/50 py-6 dark:border-slate-700 dark:bg-slate-800/50">
      <BriefcaseBusiness color={isDark ? '#475569' : '#cbd5e1'} size={32} />
      <Text className="mt-3 px-4 text-center text-sm font-medium text-slate-500 dark:text-slate-400">
        {message}
      </Text>
    </Animated.View>
  );
}

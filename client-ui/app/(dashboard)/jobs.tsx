import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  RefreshControl,
  Text,
  TextInput,
  TouchableOpacity,
  useColorScheme,
  View,
} from 'react-native';
import { Tabs, useLocalSearchParams, useRouter } from 'expo-router';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import Animated, { FadeIn, SlideInDown } from 'react-native-reanimated';
import { Briefcase, BriefcaseBusiness, Search, SlidersHorizontal, Sparkles, } from 'lucide-react-native';
import client from '@/lib/client';
import { EmploymentType, FullJobDto } from '@/lib/dto';
import JobCard from '@/components/JobCard';
import FiltersModal from '@/components/filters';
import { AxiosError } from 'axios';

/**
 * Component displaying the Jobs Tab Screen
 */
export default function JobsScreen() {
  const { mode = 'browse' } = useLocalSearchParams<{ mode: 'matches' | 'browse' }>();
  const router = useRouter();
  const insets = useSafeAreaInsets();

  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';

  const iconPrimary = '#6366f1';
  const iconNeutral = isDark ? '#94a3b8' : '#64748b';

  const [jobs, setJobs] = useState<FullJobDto[]>([]);
  const [searchQuery, setSearchQuery] = useState('');

  // Filter States
  const [isFilterModalVisible, setIsFilterModalVisible] = useState(false);
  const [jobType, setJobType] = useState<EmploymentType | null>(null);
  const [filterRead, setFilterRead] = useState<boolean | null>(null);
  const [filterApplied, setFilterApplied] = useState<boolean | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isFetchingMore, setIsFetchingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const LIMIT = 10;

  // Data fetching
  const fetchJobs = useCallback(
    async (pageNum = 0, isRefresh = false) => {
      if (isFetchingMore) return;

      try {
        if (isRefresh) setIsRefreshing(true);
        else if (pageNum === 0) setIsLoading(true);
        else setIsFetchingMore(true);

        setError(null);

        if (mode === 'matches') {
          const response = await client.get('/jobs/best');
          setJobs(response.data as FullJobDto[]);
          setHasMore(false);
        } else {
          const response = await client.get('/jobs', {
            params: {
              search_query: searchQuery || undefined,
              limit: LIMIT,
              page: pageNum,
              job_type: jobType || undefined,
              read: filterRead !== null ? filterRead : undefined,
              applied: filterApplied !== null ? filterApplied : undefined,
            },
          });

          const newJobs = response.data as FullJobDto[];

          if (newJobs.length < LIMIT) setHasMore(false);
          else setHasMore(true);

          if (isRefresh || pageNum === 0) {
            setJobs(newJobs);
          } else {
            setJobs((prev) => [...prev, ...newJobs]);
          }
          setPage(pageNum);
        }
      } catch (e) {
        if (e instanceof AxiosError) {
          setError(e.response?.data.detail || 'Failed to fetch jobs');
        }
      } finally {
        setIsLoading(false);
        setIsRefreshing(false);
        setIsFetchingMore(false);
      }
    },
    [mode, searchQuery, jobType, filterRead, filterApplied]
  );

  // Initial load
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchJobs(0);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode]);

  // Trigger search ONLY on keyboard submit
  const handleSearchSubmit = () => {
    fetchJobs(0);
  };

  const handleLoadMore = () => {
    if (!hasMore || isFetchingMore || isLoading) return;
    fetchJobs(page + 1);
  };

  // --- RENDERERS ---
  const renderEmptyState = () => {
    if (isLoading) return null;
    return (
      <Animated.View entering={FadeIn} className="mt-20 items-center justify-center px-6">
        {mode === 'matches' ? (
          <Sparkles color={isDark ? '#475569' : '#cbd5e1'} size={48} />
        ) : (
          <BriefcaseBusiness color={isDark ? '#475569' : '#cbd5e1'} size={48} />
        )}
        <Text className="mt-4 text-center text-lg font-bold text-slate-900 dark:text-white">
          No jobs found
        </Text>
        <Text className="mt-2 text-center text-sm font-medium text-slate-500 dark:text-slate-400">
          {mode === 'matches'
            ? "We haven't found any strong matches yet. Keep checking back!"
            : 'Adjust your search terms or filters, or check back later for new arrivals.'}
        </Text>
      </Animated.View>
    );
  };

  const renderFooter = () => {
    if (!isFetchingMore) return <View className="h-20" />;
    return (
      <View className="h-20 items-center justify-center py-4">
        <ActivityIndicator color={iconPrimary} size="small" />
      </View>
    );
  };

  return (
    <View className="flex-1 bg-slate-50 dark:bg-slate-900" style={{ paddingTop: insets.top }}>
      <Tabs.Screen
        options={{
          headerShown: false,
          tabBarLabel: mode === 'matches' ? 'Matches' : 'Jobs',
          tabBarIcon: ({ color }) =>
            mode === 'matches' ? (
              <Sparkles color={color} size={24} />
            ) : (
              <Briefcase color={color} size={24} />
            ),
        }}
      />

      <View className="border-b border-slate-200 bg-white px-4 pb-4 pt-4 dark:border-slate-800 dark:bg-slate-900">
        <Text className="text-3xl font-extrabold text-slate-900 dark:text-white">
          {mode === 'matches' ? 'Your Best Matches' : 'Browse Jobs'}
        </Text>

        {mode === 'browse' && (
          <Animated.View
            entering={SlideInDown.duration(300).springify()}
            className="mt-4 flex-row items-center gap-3">
            <View className="flex-1 flex-row items-center rounded-2xl bg-slate-100 px-4 py-3 dark:bg-slate-800">
              <Search color={iconNeutral} size={18} />
              <TextInput
                className="ml-2 flex-1 text-base text-slate-900 dark:text-white"
                placeholder="Search job titles..."
                placeholderTextColor={iconNeutral}
                value={searchQuery}
                onChangeText={setSearchQuery}
                onSubmitEditing={handleSearchSubmit}
                returnKeyType="search"
              />
            </View>

            {/* Launch Filter Modal */}
            <TouchableOpacity
              onPress={() => setIsFilterModalVisible(true)}
              className="h-12 w-12 items-center justify-center rounded-2xl bg-indigo-50 dark:bg-indigo-500/10">
              <SlidersHorizontal color={iconPrimary} size={20} />
            </TouchableOpacity>
          </Animated.View>
        )}
      </View>

      {isLoading && page === 0 ? (
        <View className="flex-1 items-center justify-center">
          <ActivityIndicator size="large" color={iconPrimary} />
        </View>
      ) : error ? (
        <View className="flex-1 items-center justify-center px-6">
          <Text className="mb-4 text-center font-medium text-red-500">{error}</Text>
          <TouchableOpacity
            onPress={() => fetchJobs(0)}
            className="rounded-lg bg-indigo-500 px-6 py-2">
            <Text className="font-bold text-white">Retry</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <FlatList
          data={jobs}
          keyExtractor={(item) => item.id}
          contentContainerStyle={{ padding: 24 }}
          showsVerticalScrollIndicator={false}
          ListEmptyComponent={renderEmptyState}
          ListFooterComponent={renderFooter}
          onEndReached={mode === 'browse' ? handleLoadMore : null}
          onEndReachedThreshold={0.5}
          refreshControl={
            <RefreshControl
              refreshing={isRefreshing}
              onRefresh={() => fetchJobs(0, true)}
              tintColor={iconPrimary}
            />
          }
          renderItem={({ item }) => (
            <Animated.View entering={FadeIn.duration(400)}>
              <JobCard
                job={item}
                onPress={() => router.push({ pathname: '/job', params: { job_id: item.id } })}
              />
            </Animated.View>
          )}
        />
      )}

      {/* FILTER MODAL COMPONENT */}
      {mode === 'browse' && (
        <FiltersModal
          visible={isFilterModalVisible}
          onClose={() => setIsFilterModalVisible(false)}
          onApply={() => {
            setIsFilterModalVisible(false);
            fetchJobs(0);
          }}
          jobType={jobType}
          setJobType={setJobType}
          read={filterRead}
          setRead={setFilterRead}
          applied={filterApplied}
          setApplied={setFilterApplied}
        />
      )}
    </View>
  );
}

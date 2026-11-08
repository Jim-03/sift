import React, { useEffect, useState } from 'react';
import { ActivityIndicator, Linking, ScrollView, Text, TouchableOpacity, useColorScheme, View, } from 'react-native';
import { Stack, useLocalSearchParams, useRouter } from 'expo-router';
import { SafeAreaView, useSafeAreaInsets } from 'react-native-safe-area-context';
import Animated, { FadeInDown, SlideInRight } from 'react-native-reanimated';
import {
  ArrowLeft,
  BriefcaseBusiness,
  Building2,
  CalendarDays,
  CheckCircle2,
  ExternalLink,
  Layers,
  Sparkles,
  Wallet,
  XCircle,
} from 'lucide-react-native';
import client from '@/lib/client';
import { FullJobDto, Verdict } from '@/lib/dto';
import { AxiosError } from 'axios';

/**
 * Reusable component displayed on clicking a job card
 */
export default function JobDetailsScreen() {
  const { job_id } = useLocalSearchParams<{ job_id: string }>();
  const router = useRouter();
  const insets = useSafeAreaInsets();

  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';

  const [job, setJob] = useState<FullJobDto | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const iconPrimary = '#6366f1'; // Indigo 500
  const iconNeutral = isDark ? '#94a3b8' : '#64748b'; // Slate 400/500

  useEffect(() => {
    const fetchJobDetails = async () => {
      try {
        const response = await client.get(`/jobs/${job_id}`);
        setJob(response.data as FullJobDto);
      } catch (e) {
        if (e instanceof AxiosError) {
          setError(e.response?.data || 'Failed to load job details');
        }
      } finally {
        setIsLoading(false);
      }
    };

    if (job_id) fetchJobDetails();
  }, [job_id]);

  const formatDate = (dateStr: string) => {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getVerdictColors = (verdict: Verdict) => {
    switch (verdict) {
      case Verdict.STRONG:
        return { bg: 'bg-green-500', text: 'text-green-50', icon: '#22c55e' };
      case Verdict.GOOD:
        return { bg: 'bg-indigo-500', text: 'text-indigo-50', icon: '#6366f1' };
      case Verdict.PARTIAL:
        return { bg: 'bg-yellow-500', text: 'text-yellow-50', icon: '#eab308' };
      case Verdict.WEAK:
        return { bg: 'bg-orange-500', text: 'text-orange-50', icon: '#f97316' };
      default:
        return { bg: 'bg-slate-500', text: 'text-slate-50', icon: '#64748b' };
    }
  };

  // --- LOADING STATE ---
  if (isLoading) {
    return (
      <SafeAreaView className="flex-1 items-center justify-center bg-slate-50 dark:bg-slate-900">
        <Stack.Screen options={{ headerShown: false }} />
        <ActivityIndicator size="large" color={iconPrimary} />
      </SafeAreaView>
    );
  }

  // --- ERROR STATE ---
  if (error || !job) {
    return (
      <SafeAreaView className="flex-1 items-center justify-center bg-slate-50 px-6 dark:bg-slate-900">
        <Stack.Screen options={{ headerShown: false }} />
        <BriefcaseBusiness color={iconNeutral} size={48} />
        <Text className="mt-4 text-center text-lg font-bold text-slate-900 dark:text-white">
          Job not found
        </Text>
        <TouchableOpacity
          onPress={() => router.back()}
          className="mt-6 rounded-xl bg-indigo-500 px-6 py-3">
          <Text className="font-bold text-white">Go Back</Text>
        </TouchableOpacity>
      </SafeAreaView>
    );
  }

  return (
    <View className="flex-1 bg-slate-50 dark:bg-slate-900">
      <Stack.Screen options={{ headerShown: false }} />

      {/* CUSTOM HEADER */}
      <View
        style={{ paddingTop: insets.top }}
        className="w-full flex-row items-center justify-center border-b border-slate-200 bg-white px-4 pb-4 dark:border-slate-800 dark:bg-slate-900">
        <TouchableOpacity
          onPress={() => router.back()}
          className="absolute bottom-2.5 left-2.5 h-10 w-10 items-center justify-center rounded-full  bg-slate-100 dark:bg-slate-800">
          <ArrowLeft color={isDark ? '#f8fafc' : '#0f172a'} size={20} />
        </TouchableOpacity>
        <Text className="font-bold text-slate-900 dark:text-white">Job Details</Text>
      </View>

      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{ paddingBottom: 120 }}>
        {/* HERO SECTION */}
        <Animated.View
          entering={SlideInRight.duration(400)}
          className="bg-white p-6 shadow-sm shadow-slate-200/50 dark:bg-slate-800 dark:shadow-none">
          <View className="mb-4 h-16 w-16 items-center justify-center rounded-2xl bg-indigo-50 dark:bg-indigo-500/10">
            <Building2 color={iconPrimary} size={32} />
          </View>
          <Text className="mb-2 text-2xl font-extrabold text-slate-900 dark:text-white">
            {job.title}
          </Text>
          <Text className="mb-6 text-base font-semibold text-indigo-500">{job.company}</Text>

          {/* Quick Metrics */}
          <View className="flex-row flex-wrap gap-4 border-t border-slate-100 pt-4 dark:border-slate-700">
            <Metric
              icon={<Wallet color={iconNeutral} size={16} />}
              text={job.salary || 'Undisclosed'}
            />
            <Metric
              icon={<Layers color={iconNeutral} size={16} />}
              text={job.employment_type.toLowerCase().replace('-', ' ')}
            />
            <Metric
              icon={<BriefcaseBusiness color={iconNeutral} size={16} />}
              text={job.experience_level.toLowerCase().replace('-', ' ')}
            />
            <Metric
              icon={<CalendarDays color={iconNeutral} size={16} />}
              text={`Deadline: ${formatDate(job.deadline)}`}
            />
          </View>
        </Animated.View>

        {/* SIFT METADATA / FITNESS ASSESSOR */}
        <Animated.View entering={FadeInDown.duration(400).delay(100)} className="mt-6 px-6">
          {job.job_metadata ? (
            <View className="overflow-hidden rounded-3xl bg-indigo-500 shadow-lg shadow-indigo-200 dark:bg-indigo-600 dark:shadow-none">
              <View className="flex-row items-center justify-between bg-black/10 p-5">
                <View className="flex-row items-center">
                  <Sparkles color="#ffffff" size={20} />
                  <Text className="ml-2 font-bold text-white">SIFT Analysis</Text>
                </View>
                <View
                  className={`rounded-full px-3 py-1 ${getVerdictColors(job.job_metadata.verdict).bg}`}>
                  <Text className="text-xs font-bold uppercase text-white">
                    {job.job_metadata.verdict} MATCH
                  </Text>
                </View>
              </View>
              <View className="p-5">
                <Text className="mb-4 text-sm leading-relaxed text-indigo-50">
                  {job.job_metadata.reasoning}
                </Text>

                {job.job_metadata.matches.length > 0 && (
                  <View className="mb-3">
                    <Text className="mb-2 text-xs font-bold uppercase tracking-wider text-indigo-200">
                      Key Matches
                    </Text>
                    {job.job_metadata.matches.map((match, i) => (
                      <View key={i} className="mb-1.5 flex-row items-start">
                        <CheckCircle2 color="#34d399" size={14} className="mr-2 mt-0.5" />
                        <Text className="flex-1 text-sm text-white">{match}</Text>
                      </View>
                    ))}
                  </View>
                )}

                {job.job_metadata.gaps.length > 0 && (
                  <View className="mt-2">
                    <Text className="mb-2 text-xs font-bold uppercase tracking-wider text-indigo-200">
                      Identified Gaps
                    </Text>
                    {job.job_metadata.gaps.map((gap, i) => (
                      <View key={i} className="mb-1.5 flex-row items-start">
                        <XCircle color="#f87171" size={14} className="mr-2 mt-0.5" />
                        <Text className="flex-1 text-sm text-white">{gap}</Text>
                      </View>
                    ))}
                  </View>
                )}
              </View>
            </View>
          ) : (
            <View className="items-center rounded-3xl border border-dashed border-slate-300 bg-slate-100/50 p-6 dark:border-slate-700 dark:bg-slate-800/50">
              <View className="mb-3 h-12 w-12 items-center justify-center rounded-full bg-indigo-100 dark:bg-indigo-500/20">
                <Sparkles color={iconPrimary} size={24} />
              </View>
              <Text className="mb-1 text-base font-bold text-slate-900 dark:text-white">
                Unassessed Role
              </Text>
              <Text className="mb-4 text-center text-sm text-slate-500 dark:text-slate-400">
                SIFT hasn&#39;t reviewed this job against your profile yet.
              </Text>
              <TouchableOpacity className="rounded-full bg-indigo-500 px-6 py-2.5">
                <Text className="font-bold text-white">Assess Fitness</Text>
              </TouchableOpacity>
            </View>
          )}
        </Animated.View>

        {/* JOB DETAILS TABS / SECTIONS */}
        <Animated.View entering={FadeInDown.duration(400).delay(200)} className="mt-6 px-6">
          <Section title="About the Role">
            <Text className="text-base leading-relaxed text-slate-600 dark:text-slate-400">
              {job.description}
            </Text>
          </Section>

          {job.responsibilities?.length > 0 && (
            <Section title="Responsibilities">
              {job.responsibilities.map((req, i) => (
                <BulletPoint key={i} text={req} />
              ))}
            </Section>
          )}

          {job.requirements?.length > 0 && (
            <Section title="Requirements">
              {job.requirements.map((req, i) => (
                <BulletPoint key={i} text={req} />
              ))}
            </Section>
          )}

          {job.benefits?.length > 0 && (
            <Section title="Benefits">
              {job.benefits.map((benefit, i) => (
                <BulletPoint key={i} text={benefit} />
              ))}
            </Section>
          )}
        </Animated.View>
      </ScrollView>

      {/* STICKY BOTTOM ACTION BAR */}
      <View
        style={{ paddingBottom: insets.bottom || 16 }}
        className="absolute bottom-0 w-full flex-row items-center border-t border-slate-200 bg-white px-6 pt-4 dark:border-slate-800 dark:bg-slate-900">
        <TouchableOpacity
          onPress={() => Linking.openURL(job.url)}
          className="mr-3 h-14 w-14 items-center justify-center rounded-2xl bg-slate-100 dark:bg-slate-800">
          <ExternalLink color={iconPrimary} size={24} />
        </TouchableOpacity>

        {/*TODO: Implement application*/}
        <TouchableOpacity className="h-14 flex-1 items-center justify-center rounded-2xl bg-indigo-500 shadow-md shadow-indigo-200 dark:shadow-none">
          <Text className="text-lg font-bold text-white">
            {job.applied ? 'Already Applied' : 'Apply Now'}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

function Metric({ icon, text }: { icon: React.ReactNode; text: string }) {
  return (
    <View className="flex-row items-center">
      {icon}
      <Text className="ml-1.5 text-sm font-medium capitalize text-slate-600 dark:text-slate-400">
        {text}
      </Text>
    </View>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <View className="mb-8">
      <Text className="mb-4 text-xl font-bold text-slate-900 dark:text-white">{title}</Text>
      {children}
    </View>
  );
}

function BulletPoint({ text }: { text: string }) {
  return (
    <View className="mb-3 flex-row items-start pl-1">
      <View className="mr-3 mt-2 h-1.5 w-1.5 rounded-full bg-indigo-500" />
      <Text className="flex-1 text-base leading-relaxed text-slate-600 dark:text-slate-400">
        {text}
      </Text>
    </View>
  );
}

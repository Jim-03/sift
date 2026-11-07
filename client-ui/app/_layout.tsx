import { Stack } from 'expo-router';
import '../global.css';

/**
 * Root app layout structure
 */
export default function RootLayout() {
  return <Stack screenOptions={{ headerShown: false }} />;
}

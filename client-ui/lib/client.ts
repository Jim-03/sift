import { create } from 'axios';

const client = create({
  baseURL: process.env.EXPO_PUBLIC_SERVER_URL,
  headers: {
    Authorization: `Bearer ${process.env.EXPO_PUBLIC_AUTH_KEY}`,
  },
});

export default client;

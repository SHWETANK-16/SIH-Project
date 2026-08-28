import { RouterProvider } from 'react-router-dom';
import { Suspense } from 'react';
import { AppProviders } from './providers';
import { router } from './router';
import { LoadingScreen } from '../shared/components/LoadingScreen';

export function App() {
  return <AppProviders><Suspense fallback={<LoadingScreen />}><RouterProvider router={router} /></Suspense></AppProviders>;
}

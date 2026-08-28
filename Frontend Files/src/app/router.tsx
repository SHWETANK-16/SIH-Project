import { lazy, type ReactNode } from 'react';
import { createBrowserRouter, Navigate, Outlet } from 'react-router-dom';
import { useAuthContext } from './providers';

const AppLayout = lazy(() => import('../shared/layout/AppLayout').then(({ AppLayout: Page }) => ({ default: Page })));
const LandingPage = lazy(() => import('../features/landing/pages/LandingPage').then(({ LandingPage: Page }) => ({ default: Page })));
const LoginPage = lazy(() => import('../features/auth/pages/LoginPage').then(({ LoginPage: Page }) => ({ default: Page })));
const DashboardPage = lazy(() => import('../features/dashboard/pages/DashboardPage').then(({ DashboardPage: Page }) => ({ default: Page })));
const TransactionsPage = lazy(() => import('../features/transactions/pages/TransactionsPage').then(({ TransactionsPage: Page }) => ({ default: Page })));
const TransactionDetailsPage = lazy(() => import('../features/transactions/pages/TransactionDetailsPage').then(({ TransactionDetailsPage: Page }) => ({ default: Page })));
const InvestigationPage = lazy(() => import('../features/investigations/pages/InvestigationPage').then(({ InvestigationPage: Page }) => ({ default: Page })));
const EntityPage = lazy(() => import('../features/entities/pages/EntityPage').then(({ EntityPage: Page }) => ({ default: Page })));
const AlertsPage = lazy(() => import('../features/alerts/pages/AlertsPage').then(({ AlertsPage: Page }) => ({ default: Page })));
const ReportsPage = lazy(() => import('../features/reports/pages/ReportsPage').then(({ ReportsPage: Page }) => ({ default: Page })));

function ProtectedRoute() { const { user } = useAuthContext(); return user ? <Outlet /> : <Navigate to="/login" replace />; }
function PublicOnly({ children }: { children: ReactNode }) { const { user } = useAuthContext(); return user ? <Navigate to="/dashboard" replace /> : children; }

export const router = createBrowserRouter([
  { path: '/', element: <LandingPage /> },
  { path: '/login', element: <PublicOnly><LoginPage /></PublicOnly> },
  { element: <ProtectedRoute />, children: [{ element: <AppLayout />, children: [
    { path: '/dashboard', element: <DashboardPage /> },
    { path: '/transactions', element: <TransactionsPage /> },
    { path: '/transactions/:id', element: <TransactionDetailsPage /> },
    { path: '/investigations/:id', element: <InvestigationPage /> },
    { path: '/entities/:id', element: <EntityPage /> },
    { path: '/alerts', element: <AlertsPage /> },
    { path: '/reports', element: <ReportsPage /> },
  ] }] },
  { path: '*', element: <Navigate to="/" replace /> },
]);

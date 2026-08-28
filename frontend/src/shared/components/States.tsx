import { AlertTriangle, FolderOpen, RotateCcw } from 'lucide-react';
import { Link } from 'react-router-dom';
import { LoadingScreen } from './LoadingScreen';

export function LoadingState({ label = 'Loading intelligence data...' }: { label?: string }) {
  return <LoadingScreen label={label} />;
}

export function ErrorState({ message = 'Unable to load investigation data.', onRetry }: { message?: string; onRetry?: () => void }) {
  return <div className="state-panel error-state"><AlertTriangle size={26} /><p>{message}</p><div className="state-actions">{onRetry && <button className="button button-secondary" onClick={onRetry}><RotateCcw size={15} /> Retry</button>}<Link className="button button-ghost" to="/dashboard">Return to Dashboard</Link></div></div>;
}

export function EmptyState({ label = 'No intelligence records found.' }: { label?: string }) {
  return <div className="state-panel"><FolderOpen size={26} /><p>{label}</p></div>;
}

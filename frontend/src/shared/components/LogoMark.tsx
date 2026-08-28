import logo from '../../assets/logo/guard-rupee.png';
import { APP_CONFIG } from '../../app/config';

export function LogoMark({ compact = false, className = '' }: { compact?: boolean; className?: string }) {
  return <div className={`logo-mark ${compact ? 'logo-compact' : ''} ${className}`}>
    <img src={logo} alt="Guard Rupee symbol" />
    {!compact && <span>{APP_CONFIG.projectShortName}</span>}
  </div>;
}

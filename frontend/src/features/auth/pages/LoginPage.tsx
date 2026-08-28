import { ArrowLeft, LockKeyhole } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { APP_CONFIG } from '../../../app/config';
import { useAuthContext } from '../../../app/providers';
import logo from '../../../assets/logo/guard-rupee.png';
import { NetworkSphere } from '../../landing/components/NetworkSphere';
import { LoginForm } from '../components/LoginForm';
import type { AuthenticatedUser } from '../types';

export function LoginPage() {
  const { signIn } = useAuthContext();
  const navigate = useNavigate();
  function finishLogin(user: AuthenticatedUser) { signIn(user); window.setTimeout(() => navigate('/dashboard'), 180); }
  return <div className="login-page"><section className="login-showcase"><Link className="back-link" to="/"><ArrowLeft size={16} /> Back to introduction</Link><div className="login-identity"><img src={logo} alt="Guard Rupee symbol" /><div><span className="eyebrow">Financial intelligence platform</span><h1>{APP_CONFIG.projectName}</h1><p>{APP_CONFIG.description}</p></div></div><div className="login-network"><NetworkSphere /><div className="network-caption"><LockKeyhole size={15} /> Encrypted intelligence environment</div></div><footer>Secure access gateway · Session integrity monitored</footer></section><section className="login-panel"><div className="login-card"><LoginForm onSuccess={finishLogin} /></div></section></div>;
}

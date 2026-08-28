import { ArrowRight, Radar } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { APP_CONFIG } from '../../../app/config';
import logo from '../../../assets/logo/guard-rupee.png';
import { NetworkSphere } from '../components/NetworkSphere';

export function LandingPage() {
  const navigate = useNavigate();
  return <div className="landing-page"><div className="landing-grid" /><div className="landing-ambient ambient-one" /><div className="landing-ambient ambient-two" />
    <header className="landing-header"><div className="landing-brand"><img src={logo} alt="Guard Rupee" /><span>{APP_CONFIG.projectShortName}</span></div><div className="secure-label"><Radar size={14} /> Financial Intelligence Network</div></header>
    <section className="hero-content"><div className="hero-visual"><NetworkSphere /><img className="hero-logo" src={logo} alt="Guard Rupee financial intelligence symbol" /></div><div className="hero-copy"><span className="eyebrow">Sovereign financial intelligence</span><h1>{APP_CONFIG.projectName}</h1><p className="hero-tagline">{APP_CONFIG.tagline}</p><p className="hero-description">{APP_CONFIG.description}</p><div className="hero-actions"><button className="button button-primary" onClick={() => navigate('/login')}>Enter Investigation Center <ArrowRight size={17} /></button><a className="button button-secondary" href="#platform">Explore Platform</a></div></div></section>
    <section className="landing-capabilities" id="platform"><div><span>01</span><p>Trace financial pathways</p></div><div><span>02</span><p>Surface suspicious patterns</p></div><div><span>03</span><p>Connect hidden relationships</p></div></section>
  </div>;
}

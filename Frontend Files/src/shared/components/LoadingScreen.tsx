import logo from '../../assets/logo/guard-rupee.png';

export function LoadingScreen({ label = 'Initializing Investigation Center...' }: { label?: string }) {
  return <div className="loading-screen"><div className="loading-logo-wrap"><span className="loading-orbit" /><img src={logo} alt="Guard Rupee" /></div><p>{label}</p></div>;
}

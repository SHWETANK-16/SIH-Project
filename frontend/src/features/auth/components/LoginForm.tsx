import { Eye, EyeOff, LockKeyhole, Mail, ShieldCheck } from 'lucide-react';
import { useState, type FormEvent } from 'react';
import { useLogin } from '../hooks';
import type { LoginCredentials } from '../types';

export function LoginForm({ onSuccess }: { onSuccess: (user: Awaited<ReturnType<ReturnType<typeof useLogin>['mutateAsync']>>) => void }) {
  const [showPassword, setShowPassword] = useState(false);
  const [form, setForm] = useState<LoginCredentials>({ identifier: '', password: '', remember: true });
  const login = useLogin();
  async function handleSubmit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); const user = await login.mutateAsync(form); onSuccess(user); }
  return <form className="login-form" onSubmit={handleSubmit}>
    <div className="login-card-heading"><span className="icon-tile"><ShieldCheck size={19} /></span><div><p className="eyebrow">Restricted access</p><h1>Investigator Login</h1></div></div>
    <p className="form-intro">Use your verified credentials to access secure case intelligence.</p>
    <label className="form-field"><span>Username / Email</span><div className="input-with-icon"><Mail size={16} /><input autoComplete="username" value={form.identifier} onChange={(e) => setForm({ ...form, identifier: e.target.value })} placeholder="investigator@agency.gov" /></div></label>
    <label className="form-field"><span>Password</span><div className="input-with-icon"><LockKeyhole size={16} /><input autoComplete="current-password" type={showPassword ? 'text' : 'password'} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="Enter your password" /><button className="visibility-button" type="button" onClick={() => setShowPassword((value) => !value)} aria-label={showPassword ? 'Hide password' : 'Show password'}>{showPassword ? <EyeOff size={16} /> : <Eye size={16} />}</button></div></label>
    <div className="form-options"><label className="check-label"><input type="checkbox" checked={form.remember} onChange={(e) => setForm({ ...form, remember: e.target.checked })} /> <span>Remember me</span></label><button type="button" className="text-button">Forgot password?</button></div>
    {login.error && <p className="form-error" role="alert">{login.error.message}</p>}
    <button className="button button-primary login-submit" type="submit" disabled={login.isPending}>{login.isPending ? 'Verifying secure access...' : 'Secure Login'} <LockKeyhole size={16} /></button>
    <p className="login-disclaimer">Authorized personnel only. Sessions are audited and encrypted.</p>
  </form>;
}

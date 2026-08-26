import type{ReactNode}from'react';import type{RiskLevel}from'../../types';import{AlertTriangle,DatabaseZap,LoaderCircle}from'lucide-react';
export const money=(n:number)=>new Intl.NumberFormat('en-IN',{style:'currency',currency:'INR',maximumFractionDigits:0,notation:n>999999?'compact':'standard'}).format(n);
export const date=(d:string)=>new Intl.DateTimeFormat('en-IN',{day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit'}).format(new Date(d));
export function Badge({children,tone='neutral'}:{children:ReactNode;tone?:string}){return <span className={`badge ${tone.toLowerCase().replaceAll('_','-')}`}>{children}</span>}
export function RiskBadge({level}:{level:RiskLevel}){return <Badge tone={level}>{level}</Badge>}
export function DemoLabel({children='SYNTHETIC DATA'}:{children?:ReactNode}){return <span className="demo-label"><DatabaseZap size={12}/>{children}</span>}
export function PageHeader({eyebrow='INTELLIGENCE WORKSPACE',title,description,actions}:{eyebrow?:string;title:string;description:string;actions?:ReactNode}){return <header className="page-header"><div><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p>{description}</p></div>{actions}</header>}
export function MetricCard({label,value,detail,icon,accent='mint'}:{label:string;value:string;detail:string;icon:ReactNode;accent?:string}){return <article className={`metric-card ${accent}`}><div className="metric-icon">{icon}</div><p>{label}</p><strong>{value}</strong><small>{detail}</small></article>}
export function Panel({title,subtitle,children,action,className=''}:{title:string;subtitle?:string;children:ReactNode;action?:ReactNode;className?:string}){return <section className={`panel ${className}`}><header><div><h2>{title}</h2>{subtitle&&<p>{subtitle}</p>}</div>{action}</header>{children}</section>}
export function LoadingState(){return <div className="state"><LoaderCircle className="spin"/><h3>Loading intelligence</h3><p>Assembling the synthetic investigation view.</p></div>}
export function ErrorState({error}:{error:Error}){return <div className="state error-state"><AlertTriangle/><h3>Intelligence service unavailable</h3><p>{error.message} Start the FastAPI backend on port 8000, then retry.</p></div>}
export function EmptyState({message='No records match this view.'}:{message?:string}){return <div className="state"><DatabaseZap/><h3>No intelligence found</h3><p>{message}</p></div>}

import {api} from './api';import type{Account,Investigation,InvestigationStatus,ModelMetrics,MoneyFlow,Network,RiskResult,Simulation,SystemStatus,Transaction}from'../types';
export const transactionService={list:()=>api<Transaction[]>('/transactions'),get:(id:string)=>api<Transaction>(`/transactions/${id}`)};
export const accountService={list:()=>api<Account[]>('/accounts'),get:(id:string)=>api<Account>(`/accounts/${id}`),risk:(id:string)=>api<RiskResult>(`/risk/${id}`)};
export const networkService={list:()=>api<Network[]>('/networks'),get:(id:string)=>api<Network>(`/networks/${id}`)};
export const investigationService={list:()=>api<Investigation[]>('/investigations'),get:(id:string)=>api<Investigation>(`/investigations/${id}`),status:(id:string,status:InvestigationStatus)=>api<Investigation>(`/investigations/${id}/status`,{method:'PATCH',body:JSON.stringify({status})}),report:(id:string)=>api<Record<string,unknown>>(`/investigations/${id}/report`)};
export const tracingService={trace:(id:string)=>api<MoneyFlow>(`/trace/${id}`)};
export const simulationService={start:(data:Simulation['parameters'])=>api<Simulation>('/simulation/start',{method:'POST',body:JSON.stringify(data)})};
export const modelService={metrics:()=>api<ModelMetrics>('/model/metrics'),status:()=>api<SystemStatus>('/system/status')};

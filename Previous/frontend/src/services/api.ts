const BASE=import.meta.env.VITE_API_BASE_URL||'http://localhost:8000/api/v1';
export class ApiError extends Error{constructor(public status:number,message:string){super(message)}}
export async function api<T>(path:string,options?:RequestInit):Promise<T>{const response=await fetch(`${BASE}${path}`,{...options,headers:{'Content-Type':'application/json',...options?.headers}});if(!response.ok){const body=await response.json().catch(()=>null);throw new ApiError(response.status,body?.error?.message||'Unable to reach the intelligence service.')}return response.json() as Promise<T>}

import{useQuery,type UseQueryResult}from'@tanstack/react-query';

/** Supports list/detail union queries while preserving their inferred union type. */
export function useFlexibleQuery<T extends Promise<unknown>>(options:{queryKey:readonly unknown[];queryFn:()=>T;enabled?:boolean}):UseQueryResult<Awaited<T>,Error>{
  type Result=Awaited<T>;
  return useQuery<Result,Error>({queryKey:options.queryKey,queryFn:options.queryFn as()=>Promise<Result>,enabled:options.enabled});
}

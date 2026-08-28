import { useLocation } from 'react-router-dom';
import type { PropsWithChildren } from 'react';

export function PageTransition({ children }: PropsWithChildren) {
  const location = useLocation();
  return <main className="page-transition" key={location.pathname}>{children}</main>;
}

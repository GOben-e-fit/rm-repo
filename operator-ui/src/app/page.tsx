import { redirect } from 'next/navigation';

export default function Home() {
  // Phase 1: redirect to overview dashboard. Auth-Gate kommt in Phase 1.b.
  redirect('/overview');
}

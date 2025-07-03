'use client';

import { useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useUser } from '../components/UserContext';

export default function PremiumSuccess() {
  const { user, refreshUser } = useUser();
  const router = useRouter();
  const redirected = useRef(false); // 🧠 prevent infinite redirect

  useEffect(() => {
    const upgradeAndRedirect = async () => {
      if (user && !redirected.current) {
        redirected.current = true;
        await refreshUser(user.user_id);
        router.replace('/dashboard'); // ✅ use replace to avoid history loop
      }
    };

    upgradeAndRedirect();
  }, [user, refreshUser, router]);

  return (
    <div className="p-8 text-center">
      <h1 className="text-2xl font-semibold mb-4">Upgrading your account...</h1>
      <p className="text-gray-600">Please wait while we activate your premium access.</p>
    </div>
  );
}

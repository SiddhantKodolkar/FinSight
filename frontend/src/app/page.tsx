// app/page.tsx or pages/index.tsx

import LoginForm from "./components/LoginForm";

export default function Home() {
  return (
    <main className="flex flex-col items-center justify-center min-h-screen p-4">
      <h1 className="text-3xl font-bold mb-4">FinSight</h1>
      <LoginForm/>
    </main>
  );
}

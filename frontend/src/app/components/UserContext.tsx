// context/UserContext.tsx
"use client";
import { createContext, useState, useEffect, useContext } from "react";

type User = {
  user_id: number;
  user_email: string;
  user_name: string;
  user_is_premium: boolean;
};

type UserContextType = {
  user: User | null;
  login: (user: User) => void;
  logout: () => void;
  refreshUser: (userId: number) => Promise<void>;
};

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (storedUser) setUser(JSON.parse(storedUser));
  }, []);

  const login = (user: User) => {
    setUser(user);
    localStorage.setItem("user", JSON.stringify(user));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("user");
  };

  const refreshUser = async (userId: number) => {
    const res = await fetch(`http://localhost:8000/users/${userId}`);
    const updatedUser = await res.json();
    console.log("Refreshed user from backend:", updatedUser);
    if (updatedUser) {
      setUser(updatedUser);
      localStorage.setItem("user", JSON.stringify(updatedUser));
    }
  };

  return (
    <UserContext.Provider value={{ user, login, logout, refreshUser }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) throw new Error("useUser must be used inside UserProvider");
  return context;
};

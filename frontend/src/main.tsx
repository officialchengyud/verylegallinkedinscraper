import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Theme } from "@radix-ui/themes";
import { BrowserRouter, Route, Routes } from "react-router";
import "@radix-ui/themes/styles.css";
import App from "./App.tsx";
import Login from "./Authentication/index.tsx";
import "./index.css";
import { AuthProvider } from "./Context/AuthContext.tsx";
import { initializeApp } from "firebase/app";
import AuthLayout from "./Authentication/AuthLayout.tsx";

const firebaseConfig = {
  apiKey: "AIzaSyA-KDbMQQ5LOar1qawH5uqxQMHF37Felus",
  authDomain: "verylegallinkedinscraper-575c6.firebaseapp.com",
  projectId: "verylegallinkedinscraper-575c6",
  storageBucket: "verylegallinkedinscraper-575c6.firebasestorage.app",
  messagingSenderId: "1005539042984",
  appId: "1:1005539042984:web:f014c1cb903716cf43049d",
  measurementId: "G-1Q8XL79H10",
};

const app = initializeApp(firebaseConfig);

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <Theme>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route element={<AuthLayout />}>
              <Route path="/" element={<App />} />
            </Route>
            <Route path="/login" element={<Login />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </Theme>
  </StrictMode>
);

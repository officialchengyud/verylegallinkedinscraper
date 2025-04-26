import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Theme } from "@radix-ui/themes";
import { BrowserRouter, Route, Routes } from "react-router";
import "@radix-ui/themes/styles.css";
import App from "./App.tsx";
import Login from "./Authentication/index.tsx";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <Theme>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<App />} />
          <Route path="/login" element={<Login />} />
        </Routes>
      </BrowserRouter>
    </Theme>
  </StrictMode>
);

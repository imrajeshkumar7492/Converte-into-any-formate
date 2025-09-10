import React from "react";
import "./App.css";
import IframeHeroSection from "./components/IframeHeroSection";
import ErrorBoundary from "./components/ErrorBoundary";
import { Toaster } from "./components/ui/toaster";

function App() {
  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
        <IframeHeroSection />
        <Toaster />
      </div>
    </ErrorBoundary>
  );
}

export default App;
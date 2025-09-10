import React from "react";
import "./App.css";
import HeroSection from "./components/HeroSection";
import ErrorBoundary from "./components/ErrorBoundary";
import { Toaster } from "./components/ui/toaster";

function App() {
  return (
    <ErrorBoundary>
      <div className="App">
        <HeroSection />
        <Toaster />
      </div>
    </ErrorBoundary>
  );
}

export default App;
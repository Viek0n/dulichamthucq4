
import { useState, useEffect } from "react";

function InstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [isInstalled, setIsInstalled] = useState(false);
  const [showInstructions, setShowInstructions] = useState(false);

  useEffect(() => {
    // Check whether the PWA is already installed.
    const checkInstalled = () => {
      setIsInstalled(
        window.matchMedia("(display-mode: standalone)").matches ||
        window.navigator.standalone === true
      );
    };

    checkInstalled();

    // Listen for browser installation availability.
    const handleBeforeInstallPrompt = (event) => {
      event.preventDefault();
      setDeferredPrompt(event);
      console.log("PWA installation is available");
    };

    // Listen for successful installation.
    const handleAppInstalled = () => {
      setIsInstalled(true);
      setDeferredPrompt(null);
      setShowInstructions(false);
      console.log("PWA successfully installed");
    };

    window.addEventListener(
      "beforeinstallprompt",
      handleBeforeInstallPrompt
    );

    window.addEventListener("appinstalled", handleAppInstalled);

    return () => {
      window.removeEventListener(
        "beforeinstallprompt",
        handleBeforeInstallPrompt
      );

      window.removeEventListener("appinstalled", handleAppInstalled);
    };
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) {
      setShowInstructions(true);
      return;
    }

    // Show the native browser installation prompt.
    await deferredPrompt.prompt();

    const { outcome } = await deferredPrompt.userChoice;

    console.log("Installation result:", outcome);

    // The event can only be used once.
    setDeferredPrompt(null);

    if (outcome === "accepted") {
      console.log("User accepted installation");
    }
  };

  if (isInstalled) {
    return null;
  }

  return (
    <>
      <button
        onClick={handleInstall}
        style={{
          position: "fixed",
          bottom: "20px",
          right: "20px",
          zIndex: 1000,
          backgroundColor: "#4CAF50",
          color: "white",
          padding: "15px 30px",
          border: "none",
          borderRadius: "25px",
          fontSize: "16px",
          cursor: "pointer",
          boxShadow: "0 4px 6px rgba(0,0,0,0.1)"
        }}
      >
        📱 Install App
      </button>

      {showInstructions && (
        <div
          style={{
            position: "fixed",
            bottom: "85px",
            right: "20px",
            zIndex: 1001,
            background: "white",
            color: "#333",
            padding: "20px",
            borderRadius: "12px",
            boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
            maxWidth: "280px"
          }}
        >
          <h3>Install this app</h3>
          <p>
            Open your browser menu and select
            {" "}Install app or Add to Home Screen.
          </p>

          <button onClick={() => setShowInstructions(false)}>
            Close
          </button>
        </div>
      )}
    </>
  );
}

export default InstallPrompt;

import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App"; // ✅ Importa desde src/App.tsxq

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

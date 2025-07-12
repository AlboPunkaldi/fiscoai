import React, { useState } from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import Login from "./Login.jsx";

function Root() {
  // se nel localStorage c’è già il token ⇒ utente autenticato
  const [isAuth, setIsAuth] = useState(!!localStorage.getItem("token"));

  return isAuth ? <App /> : <Login onLogin={() => setIsAuth(true)} />;
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>
);
import { useState } from "react";

function Login({ onLogin }) {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        try {
            const body = new URLSearchParams();
            body.append("username", email);
            body.append("password", password);

            const res = await fetch("/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body
            });
            if (!res.ok) {
                throw new Error("Credenziali errate");
            }
            const data = await res.json();
            localStorage.setItem("token", data.access_token);
            onLogin();
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <form onSubmit={handleSubmit} style={{ maxWidth: 300, margin: "4rem auto" }}>
            <h2>Accedi</h2>
            <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                style={{ width: "100%", marginBottom: "0.5rem" }}
            />
            <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                style={{ width: "100%", marginBottom: "0.5rem" }}
            />
            <button type="submit" style={{ width: "100%" }}>
                Accedi
            </button>
            {error && <p style={{ color: "red" }}>{error}</p>}
        </form>
    );
}

export default Login;
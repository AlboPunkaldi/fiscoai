import { useEffect, useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';

const authFetch = (url, options = {}) => {
  const token = localStorage.getItem("token");
  return fetch(url, {
    ...options,
    headers: {
      ...(options.headers || {}),
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
};

function App() {
  const [rows, setRows] = useState([]);

  // Stato per la chat: array di { role: "user"|"ai", text: string }
  const [chatMessages, setChatMessages] = useState([]);
  // Stato per l’input dell’utente
  const [chatInput, setChatInput] = useState("");
  // Stato di caricamento richiesta
  const [chatLoading, setChatLoading] = useState(false);

  useEffect(() => {
    authFetch('http://127.0.0.1:8000/tax/monthly')
      .then((r) => r.json())
      .then((data) => {
        console.log('Dati ricevuti dal backend 👇', data.mesi);
        setRows(data.mesi);
      })
      .catch((err) => console.error('Errore fetch:', err));
  }, []);

  // Funzione per inviare la domanda alla nostra API /chat
  const sendMessage = async () => {
    if (!chatInput.trim()) return; // non inviare input vuoti
    const userMsg = { role: "user", text: chatInput };
    // Aggiunge subito il messaggio utente
    setChatMessages(msgs => [...msgs, userMsg]);
    setChatInput("");
    setChatLoading(true);

    try {
      const res = await authFetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userMsg.text })
      });
      if (!res.ok) throw new Error(`Server risponde ${res.status}`);
      const data = await res.json();
      // data.answer contiene la risposta dell’AI
      const aiMsg = { role: "ai", text: data.answer };
      setChatMessages(msgs => [...msgs, aiMsg]);
    } catch (err) {
      console.error("Errore chat:", err);
      const errorMsg = { role: "ai", text: "Errore: non ho potuto contattare il server." };
      setChatMessages(msgs => [...msgs, errorMsg]);
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <main style={{ padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>
        Dashboard Tasse {new Date().getFullYear()}
      </h1>

      <ResponsiveContainer width="100%" height={350}>
        <BarChart data={rows}>
          <XAxis dataKey="mese" interval={0} tick={{ fontSize: 12 }} minTickGap={5} />
          <YAxis />
          <Tooltip />
          <Legend />
          {/* colore fissato per evitare coincidenze con lo sfondo */}
          <Bar dataKey="ricavi" name="Ricavi (€)" stackId="a" fill="#4e79a7" />
          <Bar dataKey="tasse_totali" name="Tasse (€)" stackId="a" fill="#f28e2b" />
        </BarChart>
      </ResponsiveContainer>
      <section style={{ marginTop: '2rem' }}>
        <h2 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>Chat fiscale</h2>
        <div
          style={{
            border: '1px solid #ccc',
            borderRadius: 4,
            padding: '1rem',
            maxHeight: 300,
            overflowY: 'auto',
            background: '#fafafa'
          }}
        >
          {chatMessages.map((m, i) => (
            <div
              key={i}
              style={{
                textAlign: m.role === 'user' ? 'right' : 'left',
                margin: '0.5rem 0'
              }}
            >
              <span
                style={{
                  display: 'inline-block',
                  padding: '0.5rem 1rem',
                  borderRadius: 20,
                  background: m.role === 'user' ? '#4e79a7' : '#f28e2b',
                  color: 'white',
                  maxWidth: '80%'
                }}
              >
                {m.text}
              </span>
            </div>
          ))}
        </div>
        <div style={{ marginTop: '0.5rem', display: 'flex' }}>
          <input
            type="text"
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Scrivi una domanda..."
            style={{ flex: 1, padding: '0.5rem', fontSize: '1rem' }}
            disabled={chatLoading}
          />
          <button
            onClick={sendMessage}
            disabled={chatLoading}
            style={{ marginLeft: '0.5rem', padding: '0.5rem 1rem' }}
          >
            {chatLoading ? '...' : 'Invia'}
          </button>
        </div>
      </section>
    </main>
  );
}

export default App;
import { useEffect, useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';

function App() {
  const [rows, setRows] = useState([]);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/tax/monthly')
      .then((r) => r.json())
      .then((data) => {
        console.log('Dati ricevuti dal backend 👇', data.mesi);
        setRows(data.mesi);
      })
      .catch((err) => console.error('Errore fetch:', err));
  }, []);

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
    </main>
  );
}

export default App;
const { Pool } = require('pg');

const pool = new Pool({
  connectionString: "postgresql://neondb_owner:npg_rtgT9R3GEhAV@ep-snowy-dream-a5reiccc-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require",
});

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ message: 'Método não permitido' });

  try {
    const { id_relato } = req.body;
    await pool.query("UPDATE relatos SET curtidas = curtidas + 1 WHERE id = $1", [id_relato]);
    res.status(200).json({ mensagem: "Curtida registrada!" });
  } catch (error) {
    res.status(500).json({ error: "Erro ao registrar curtida" });
  }
}

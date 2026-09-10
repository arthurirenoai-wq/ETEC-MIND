const { Pool } = require('pg');

const pool = new Pool({
  connectionString: "postgresql://neondb_owner:npg_rtgT9R3GEhAV@ep-snowy-dream-a5reiccc-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require",
});

export default async function handler(req, res) {
  if (req.method !== 'GET') return res.status(405).json({ message: 'Método não permitido' });

  try {
    // Cria a coluna de curtidas automaticamente se ela não existir
    await pool.query("ALTER TABLE relatos ADD COLUMN IF NOT EXISTS curtidas INT DEFAULT 0");
    
    const result = await pool.query(
      "SELECT id, nome, email, materia, nivel, detalhes, curtidas FROM relatos ORDER BY data_envio DESC"
    );
    res.status(200).json(result.rows);
  } catch (error) {
    res.status(500).json({ error: "Erro ao buscar relatos" });
  }
}

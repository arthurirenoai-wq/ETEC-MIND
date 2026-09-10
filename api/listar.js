const { Pool } = require('pg');

// Conexão com o seu banco de dados Neon
const pool = new Pool({
  connectionString: "postgresql://neondb_owner:npg_rtgT9R3GEhAV@ep-snowy-dream-a5reiccc-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require",
});

export default async function handler(req, res) {
  // Permite apenas requisições do tipo GET (buscar dados)
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Método não permitido' });
  }

  try {
    // Busca todos os relatos no banco de dados, do mais recente para o mais antigo
    const result = await pool.query(
      "SELECT id, nome, email, materia, nivel, detalhes FROM relatos ORDER BY data_envio DESC"
    );
    
    // Devolve a lista de relatos para o HTML
    res.status(200).json(result.rows);
  } catch (error) {
    console.error("Erro no listar.js:", error);
    res.status(500).json({ error: "Erro ao buscar relatos no banco de dados" });
  }
}

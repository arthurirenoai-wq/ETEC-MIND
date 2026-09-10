const { Pool } = require('pg');

// Conexão com o seu banco de dados Neon
const pool = new Pool({
  connectionString: "postgresql://neondb_owner:npg_rtgT9R3GEhAV@ep-snowy-dream-a5reiccc-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require",
});

export default async function handler(req, res) {
  // Permite apenas requisições do tipo POST (enviar dados)
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Método não permitido' });
  }

  try {
    const { nome, email, materia, nivel, detalhes } = req.body;
    
    // Insere os dados enviados pelo formulário direto no Neon
    await pool.query(
      "INSERT INTO relatos (nome, email, materia, nivel, detalhes, status) VALUES ($1, $2, $3, $4, $5, 'Pendente')",
      [nome, email, materia, nivel, detalhes]
    );

    // Responde que deu tudo certo
    res.status(200).json({ mensagem: "Salvo com sucesso!" });
  } catch (error) {
    console.error("Erro no salvar.js:", error);
    res.status(500).json({ error: "Erro ao salvar no banco de dados" });
  }
}

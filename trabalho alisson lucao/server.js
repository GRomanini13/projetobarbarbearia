async function criarUsuario(email, senha) {
  try {
    const res = await fetch('http://127.0.0.1:8000/usuarios', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, senha })
    });

    if (!res.ok) {
      // tenta extrair mensagem de erro do backend
      const txt = await res.text();
      throw new Error(`HTTP ${res.status} — ${txt}`);
    }

    const data = await res.json(); // se o backend retornar JSON
    console.log('Resposta do servidor:', data);
    return data;
  } catch (err) {
    console.error('Erro ao criar usuário:', err);
    throw err;
  }
}

// uso de exemplo
criarUsuario('teste@exemplo.com', 'minhasenha123')
  .then(r => console.log('Usuário criado:', r))
  .catch(e => console.log('Falha:', e.message));

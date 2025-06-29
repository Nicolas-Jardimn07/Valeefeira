
# 🌱 Vale&feira - Marketplace de Produtos Rurais

**"Do Vale para o mercado: mais acesso, menos desperdício"**

Uma plataforma digital que conecta produtores rurais diretamente aos consumidores, promovendo o acesso a produtos frescos e reduzindo o desperdício na cadeia de distribuição.

## 🚀 Funcionalidades

### Para Produtores
- ✅ Cadastro de produtos com imagens
- ✅ Sistema de chat direto com compradores
- ✅ Planos de assinatura (Básico/Premium)
- ✅ Produtos em destaque para maior visibilidade
- ✅ Analytics de desempenho
- ✅ Sistema de avaliações

### Para Compradores
- ✅ Busca avançada por produtos, categoria e cidade
- ✅ Sistema de favoritos
- ✅ Chat direto com produtores
- ✅ Avaliações de produtos e vendedores
- ✅ Interface responsiva

### Recursos Técnicos
- ✅ Armazenamento de imagens no banco de dados
- ✅ Sistema de autenticação completo
- ✅ Recuperação de senha via WhatsApp
- ✅ Pagamentos PIX integrados
- ✅ Deploy automático no Replit

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python, Flask, SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Banco de Dados**: PostgreSQL
- **Autenticação**: Flask-Login
- **Upload de Imagens**: PIL/Pillow
- **Deploy**: Replit com Gunicorn

## 🏗️ Estrutura do Projeto

```
vale-feira/
├── app.py              # Configuração principal do Flask
├── main.py             # Ponto de entrada da aplicação
├── models.py           # Modelos do banco de dados
├── routes.py           # Rotas e controllers
├── forms.py            # Formulários WTForms
├── utils.py            # Funções utilitárias
├── static/             # Arquivos estáticos (CSS, JS, imagens)
├── templates/          # Templates HTML
└── README.md           # Documentação
```

## 🚀 Como Executar

### No Replit (Recomendado)
1. Importe este repositório no Replit
2. Clique no botão "Run"
3. A aplicação estará disponível automaticamente

### Localmente
```bash
# Clone o repositório
git clone https://github.com/Nicolas-Jardimn07/ValeConecta.git
cd ValeConecta

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
export DATABASE_URL="sua_url_do_banco"
export SESSION_SECRET="sua_chave_secreta"

# Execute a aplicação
python main.py
```

## 🌐 Deploy

A aplicação está configurada para deploy automático no Replit:
- URL de produção: https://valeefeira.replit.app
- Deploy via Replit Deployments
- Banco PostgreSQL integrado

## 📝 Variáveis de Ambiente

```env
DATABASE_URL=postgresql://...
SESSION_SECRET=sua_chave_secreta_aqui
MAIL_USERNAME=seu_email@gmail.com
MAIL_PASSWORD=sua_senha_de_app
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

**Nicolas Jardim**
- GitHub: [@Nicolas-Jardimn07](https://github.com/Nicolas-Jardimn07)

## 🔧 Suporte

Para suporte ou dúvidas sobre o projeto, abra uma issue no GitHub ou entre em contato.

---

*Desenvolvido com ❤️ para conectar o campo à mesa*

# 🗞 VCtv AInews

Portal de notícias com geração automática por IA, integrado ao GitHub Pages.

## ✨ Funcionalidades

- **Notícias em tempo real** — RSS de BBC, NY Times, G1 e mais
- **IA integrada** — Pollinations AI expande cada notícia (sem custo, sem API key)
- **Geração automática diária** — GitHub Actions publica todo dia às 9h (Brasília)
- **Edição de fim de semana** — Cobertura ampliada aos sábados e domingos
- **Edições especiais** — Datas comemorativas detectadas automaticamente
- **Gerador personalizado** — Escreva sobre qualquer tema e a IA cria a notícia
- **Seletor de linhas e velocidade** — Controle o tamanho e qualidade da geração

---

## 🚀 Como publicar no GitHub Pages

### 1. Criar o repositório

```bash
git init
git add .
git commit -m "🗞 VCtv AInews — Setup inicial"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/SEU_REPO.git
git push -u origin main
```

### 2. Ativar o GitHub Pages

1. Vá em **Settings → Pages**
2. Em "Source", selecione **Deploy from a branch**
3. Escolha a branch `main` e pasta `/ (root)`
4. Clique em **Save**
5. Após ~1 minuto, o site estará em: `https://SEU_USUARIO.github.io/SEU_REPO`

### 3. Ativar o GitHub Actions

- O workflow já está em `.github/workflows/daily-news.yml`
- Vá em **Actions → Enable Actions** (se necessário)
- Para testar, vá em **Actions → 🗞 VCtv AInews** → **Run workflow**

---

## 📅 Agenda de publicação

| Quando | Tipo | Horário |
|--------|------|---------|
| Segunda a Sexta | Edição Diária | 09:00 BRT |
| Sábados e Domingos | Edição de Fim de Semana | 10:00 BRT |
| Datas especiais | Edição Especial | Mesmo horário |

---

## 📁 Estrutura

```
├── index.html           # Site principal
├── news.json            # Notícias geradas (atualizado pelo bot)
├── generate_news.py     # Script Python de geração
└── .github/
    └── workflows/
        └── daily-news.yml  # Automação GitHub Actions
```

---

## 🎨 Personalização

### Adicionar fontes RSS
Edite `generate_news.py`, na lista `RSS_FEEDS`:
```python
{"url": "https://exemplo.com/feed.xml", "source": "Minha Fonte", "category": "Tecnologia"},
```

### Adicionar datas especiais
Edite `SPECIAL_EVENTS` em `generate_news.py`:
```python
"06-12": "Dia dos Namorados (BR)",
```

### Rodar localmente
```bash
python generate_news.py
# Abre index.html no navegador
```

---

## 🛠 Tecnologias

- **Frontend**: HTML/CSS/JS puro — sem frameworks
- **IA**: [Pollinations AI](https://pollinations.ai) — gratuito, sem API key
- **Notícias**: RSS público de BBC, NY Times, G1
- **Automação**: GitHub Actions
- **Hospedagem**: GitHub Pages

---

*VCtv AInews — Feito com ❤ e IA*

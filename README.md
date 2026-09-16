# Atende Bot

> Bot de atendimento automatizado para pequenos negócios. Respostas inteligentes via WhatsApp, Instagram ou qualquer canal.

[![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)

## O que é

Um template de bot de atendimento que entende perguntas frequentes (horário, localização, preços) e responde automaticamente. Captura leads e exporta pra CSV.

## Instalação

```bash
git clone https://github.com/klcombr/atende-bot.git
cd atende-bot
pip install -r requirements.txt
```

## Uso

1. Edite `config.json` com os dados do negócio
2. Rode:

```bash
python bot.py
```

3. Simule conversas no terminal ou integre com API do WhatsApp

## Funcionalidades

- Respostas automáticas para perguntas frequentes
- Deteção de intenção (horário, preço, localização)
- Captura de leads (nome + telefone → CSV)
- Agendamento de compromissos
- Horário comercial configurável

## Configuração

Edite `config.json` com:
- Nome e dados do negócio
- Serviços e preços
- Mensagens automáticas personalizadas
- Horário de funcionamento

## Licença

MIT — use, modifie, distribua.

---
Feito por [KL Com](https://github.com/klcombr)

#!/usr/bin/env python3
"""Atende Bot — Bot de atendimento para pequenos negócios."""

import json
import csv
import re
from datetime import datetime
from pathlib import Path

class AtendeBot:
    def __init__(self, config_path="config.json"):
        with open(config_path) as f:
            self.config = json.load(f)
        self.leads_file = Path("leads.csv")

    def detect_intent(self, message):
        msg = message.lower().strip()

        keywords = {
            "horario": ["horário", "horario", "hora", "abre", "fecha", "funciona", "aberto"],
            "preco": ["preço", "preco", "quanto", "valor", "custa", "paga"],
            "localizacao": ["onde", "endereço", "endereco", "local", "chegar", "fica"],
            "servico": ["serviço", "servico", "faz", "fazem", "trabalha", "trabalham"],
            "contato": ["telefone", "whatsapp", "email", "contato", "ligar"],
        }

        for intent, words in keywords.items():
            if any(w in msg for w in words):
                return intent
        return "outro"

    def respond(self, message):
        cfg = self.config
        intent = self.detect_intent(message)

        responses = {
            "horario": f"Olá! Nosso horário de funcionamento é: {cfg.get('working_hours', 'Seg-Sex: 8h às 18h')}. Como posso ajudar?",
            "preco": f"Olá! Temos os seguintes serviços:\n" + "\n".join(
                f"• {s['name']}: {s.get('price', 'Consulte')}" for s in cfg.get('services', [])
            ) + "\nDeseja mais detalhes?",
            "localizacao": f"Estamos em: {cfg.get('address', 'Consulte nosso endereço')}. Pode checar no Google Maps!",
            "servico": f"Trabalhamos com:\n" + "\n".join(
                f"• {s['name']} — {s.get('description', '')}" for s in cfg.get('services', [])
            ) + "\nQuer saber mais sobre algum?",
            "contato": f"Nosso contato: {cfg.get('phone', '')} | WhatsApp: {cfg.get('whatsapp', '')}",
            "outro": cfg.get('auto_reply', 'Olá! Como posso ajudar?')
        }

        return responses.get(intent, responses["outro"])

    def capture_lead(self, name, phone, source="bot"):
        file_exists = self.leads_file.exists()
        with open(self.leads_file, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["nome", "telefone", "origem", "data", "interesse"])
            writer.writerow([name, phone, source, datetime.now().isoformat(), ""])
        print(f"Lead capturado: {name} ({phone})")

    def run(self):
        print(f"=== Atende Bot — {self.config.get('business_name', 'Negócio')} ===")
        print("Digite sua mensagem (ou 'sair' para encerrar):\n")

        while True:
            msg = input("Cliente: ").strip()
            if msg.lower() in ["sair", "exit", "quit"]:
                print("Encerrado.")
                break

            response = self.respond(msg)
            print(f"Bot: {response}\n")

            if msg.lower() in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"]:
                name = input("Bot: Qual seu nome? ").strip()
                phone = input("Bot: Seu telefone (opcional, Enter pra pular): ").strip()
                if name:
                    self.capture_lead(name, phone or "não informado")

if __name__ == "__main__":
    bot = AtendeBot()
    bot.run()

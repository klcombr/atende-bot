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

    def _is_purchase_intent(self, intent):
        """Check if intent indicates potential customer interest."""
        return intent in ("preco", "servico")

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

    def validate_phone(self, phone):
        """Validate Brazilian phone format: (XX) 9XXXX-XXXX or (XX) XXXX-XXXX."""
        if not phone:
            return True  # Optional field
        digits = re.sub(r'\D', '', phone)
        if len(digits) == 10 or len(digits) == 11:
            return True
        return False

    def _normalize_phone(self, phone):
        """Extract only digits from phone number."""
        return re.sub(r'\D', '', phone) if phone else ""

    def _read_leads(self):
        """Read existing leads into a dict keyed by normalized phone."""
        leads = {}
        if not self.leads_file.exists():
            return leads
        with open(self.leads_file, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = self._normalize_phone(row.get("telefone", ""))
                if key and key != "naoinformado":
                    leads[key] = row
        return leads

    def capture_lead(self, name, phone, source="bot"):
        """Capture lead with deduplication by phone number."""
        norm_phone = self._normalize_phone(phone) or "naoinformado"
        file_exists = self.leads_file.exists()

        existing = self._read_leads()
        if norm_phone != "naoinformado" and norm_phone in existing:
            print(f"Lead já registrado: {name} ({phone}). Atualizando registro.")
            rows = []
            with open(self.leads_file, "r", newline="") as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                for row in reader:
                    if self._normalize_phone(row.get("telefone", "")) == norm_phone:
                        row["last_contact"] = datetime.now().isoformat()
                        row["interesse"] = row.get("interesse", "") + f"[{source}] "
                    rows.append(row)
            with open(self.leads_file, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            print(f"Lead atualizado: {name} ({phone})")
            return

        with open(self.leads_file, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["nome", "telefone", "origem", "data", "interesse", "last_contact"])
            writer.writerow([name, phone or "não informado", source, datetime.now().isoformat(), "", datetime.now().isoformat()])
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

            intent = self.detect_intent(msg)
            is_greeting = msg.lower() in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"]
            is_purchase = self._is_purchase_intent(intent)

            if is_greeting or is_purchase:
                name = input("Bot: Qual seu nome? ").strip()
                if name:
                    while True:
                        phone = input("Bot: Seu telefone (opcional, Enter pra pular): ").strip()
                        if not phone:
                            break
                        if self.validate_phone(phone):
                            break
                        print("Bot: Formato inválido. Use: (DDD) 9XXXX-XXXX ou Enter pra pular.")
                    self.capture_lead(name, phone or "não informado")


if __name__ == "__main__":
    bot = AtendeBot()
    bot.run()

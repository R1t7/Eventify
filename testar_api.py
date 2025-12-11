#!/usr/bin/env python3
"""
Script para testar a API REST do Eventify
"""
import requests
import json

# Configurações
BASE_URL = "http://localhost:8000"
USERNAME = "org_admin"  # Mude para seu usuário
PASSWORD = "senha123"   # Mude para sua senha

def obter_token():
    """Obtém o token de autenticação"""
    url = f"{BASE_URL}/api/auth/login/"
    data = {"username": USERNAME, "password": PASSWORD}

    print(f"🔑 Obtendo token para usuário '{USERNAME}'...")
    response = requests.post(url, json=data)

    if response.status_code == 200:
        token = response.json()['token']
        print(f"✅ Token obtido: {token[:20]}...")
        return token
    else:
        print(f"❌ Erro ao obter token: {response.status_code}")
        print(response.text)
        return None

def listar_eventos(token):
    """Lista todos os eventos"""
    url = f"{BASE_URL}/api/eventos/"
    headers = {"Authorization": f"Token {token}"}

    print(f"\n📋 Listando eventos...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        eventos = response.json()
        print(f"✅ {len(eventos)} eventos encontrados:")
        for evento in eventos:
            print(f"  - {evento['titulo']} ({evento['tipo']})")
        return eventos
    else:
        print(f"❌ Erro ao listar eventos: {response.status_code}")
        return []

def detalhes_evento(token, evento_id):
    """Obtém detalhes de um evento específico"""
    url = f"{BASE_URL}/api/eventos/{evento_id}/"
    headers = {"Authorization": f"Token {token}"}

    print(f"\n🔍 Detalhes do evento {evento_id}...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        evento = response.json()
        print(f"✅ Evento: {evento['titulo']}")
        print(f"   Descrição: {evento['descricao'][:50]}...")
        print(f"   Data: {evento['data_inicio']} a {evento['data_fim']}")
        print(f"   Vagas: {evento['vagas_disponiveis']}/{evento['vagas']}")
        return evento
    else:
        print(f"❌ Erro ao obter detalhes: {response.status_code}")
        return None

def testar_rate_limit(token):
    """Testa o rate limiting fazendo várias requisições"""
    url = f"{BASE_URL}/api/eventos/"
    headers = {"Authorization": f"Token {token}"}

    print(f"\n⏱️  Testando rate limiting (limite: 20 requisições/dia)...")

    for i in range(1, 25):
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            print(f"  Requisição {i}: ✅ OK")
        elif response.status_code == 429:
            print(f"  Requisição {i}: ⛔ BLOQUEADO - Rate limit atingido!")
            print(f"  Mensagem: {response.json()}")
            break
        else:
            print(f"  Requisição {i}: ❌ Erro {response.status_code}")

def main():
    print("=" * 60)
    print("🚀 TESTE DA API REST - Eventify")
    print("=" * 60)

    # 1. Obter token
    token = obter_token()
    if not token:
        print("\n❌ Não foi possível obter o token. Verifique as credenciais.")
        return

    # 2. Listar eventos
    eventos = listar_eventos(token)

    # 3. Detalhes de um evento (se houver)
    if eventos:
        evento_id = eventos[0]['id']
        detalhes_evento(token, evento_id)

    # 4. Testar rate limit (opcional - descomente se quiser testar)
    # ATENÇÃO: Isso vai esgotar seu limite diário!
    # testar_rate_limit(token)

    print("\n" + "=" * 60)
    print("✅ Testes concluídos!")
    print("=" * 60)

if __name__ == "__main__":
    main()

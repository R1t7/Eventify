#!/bin/bash

# Script de Comandos Úteis - SGEA
# Facilita a execução dos comandos mais comuns

echo "========================================"
echo "   SGEA - Comandos Úteis"
echo "========================================"
echo ""

show_menu() {
    echo "Escolha uma opção:"
    echo ""
    echo "1) Criar/Atualizar banco de dados (makemigrations + migrate)"
    echo "2) Popular banco com dados de teste (seed_database)"
    echo "3) Gerar certificados automáticos"
    echo "4) Executar servidor de desenvolvimento"
    echo "5) Criar superusuário"
    echo "6) Executar todos os passos (setup completo)"
    echo "7) Limpar banco e recriar"
    echo "8) Testar API (obter token)"
    echo "0) Sair"
    echo ""
    echo -n "Digite a opção: "
}

criar_banco() {
    echo "Criando migrações..."
    python manage.py makemigrations
    echo ""
    echo "Aplicando migrações..."
    python manage.py migrate
    echo "✅ Banco de dados atualizado!"
}

popular_banco() {
    echo "Populando banco com dados de teste..."
    python manage.py seed_database
    echo "✅ Dados carregados!"
}

gerar_certificados() {
    echo "Gerando certificados..."
    python manage.py gerar_certificados
    echo "✅ Certificados gerados!"
}

executar_servidor() {
    echo "Iniciando servidor em http://localhost:8000"
    echo "Pressione Ctrl+C para parar"
    python manage.py runserver
}

criar_superusuario() {
    echo "Criando superusuário..."
    python manage.py createsuperuser
}

setup_completo() {
    echo "Executando setup completo..."
    criar_banco
    echo ""
    popular_banco
    echo ""
    echo "✅ Setup completo!"
    echo ""
    echo "Iniciar servidor? (s/n)"
    read resposta
    if [ "$resposta" = "s" ]; then
        executar_servidor
    fi
}

limpar_banco() {
    echo "⚠️  ATENÇÃO: Isso irá deletar o banco de dados!"
    echo "Deseja continuar? (s/n)"
    read resposta
    if [ "$resposta" = "s" ]; then
        rm -f db.sqlite3
        echo "Banco deletado!"
        criar_banco
        echo ""
        popular_banco
        echo "✅ Banco recriado com sucesso!"
    else
        echo "Operação cancelada."
    fi
}

testar_api() {
    echo "Testando autenticação da API..."
    echo ""
    curl -X POST http://localhost:8000/api/auth/login/ \
      -H "Content-Type: application/json" \
      -d '{"username": "aluno@sgea.com", "password": "Aluno@123"}'
    echo ""
    echo ""
    echo "✅ Se você viu um token acima, a API está funcionando!"
}

# Verifica se está na pasta correta
if [ ! -f "manage.py" ]; then
    echo "❌ Erro: execute este script da pasta projetoWeb"
    echo "Use: cd projetoWeb && bash ../comandos_uteis.sh"
    exit 1
fi

# Loop principal
while true; do
    echo ""
    show_menu
    read opcao
    echo ""

    case $opcao in
        1) criar_banco ;;
        2) popular_banco ;;
        3) gerar_certificados ;;
        4) executar_servidor ;;
        5) criar_superusuario ;;
        6) setup_completo ;;
        7) limpar_banco ;;
        8) testar_api ;;
        0)
            echo "Saindo..."
            exit 0
            ;;
        *)
            echo "❌ Opção inválida!"
            ;;
    esac
done

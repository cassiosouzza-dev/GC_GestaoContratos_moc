import sys
from sinc import DriveConector

print("--- INICIANDO TESTE DE CONEXÃO E UPLOAD ---")

try:
    # 1. Tentar Conectar
    print("1. Tentando conectar ao Google...")
    drive = DriveConector()
    drive.conectar()
    print("✅ Conexão realizada com sucesso!")

    # 2. Tentar Criar um Arquivo de Teste
    print("\n2. Tentando criar arquivo de teste na nuvem...")
    dados_teste = {"mensagem": "Se você está lendo isso, a nuvem funcionou!"}
    
    # Força o upload (criação)
    drive.subir_json("ARQUIVO_TESTE_DEBUG.json", dados_teste)
    print("✅ Upload concluído (teoricamente).")

    # 3. Verificar se o arquivo existe mesmo
    print("\n3. Verificando se o arquivo aparece na lista...")
    arquivo = drive.buscar_id_arquivo("ARQUIVO_TESTE_DEBUG.json")
    
    if arquivo:
        print(f"🎉 SUCESSO TOTAL! Arquivo encontrado.")
        print(f"ID do Arquivo: {arquivo['id']}")
        print(f"Nome: {arquivo['name']}")
        print("Pode apagar este arquivo do Drive depois.")
    else:
        print("❌ ERRO: O upload diz que foi feito, mas o arquivo não foi encontrado na busca.")

except Exception as e:
    print("\n❌ ERRO FATAL DURANTE O TESTE:")
    print(e)
    # Mostra detalhes se for erro do Google
    if hasattr(e, 'content'):
        print("Detalhes do Google:", e.content)

print("\n--- FIM DO TESTE ---")
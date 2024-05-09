import openai
from openai import OpenAI
import pandas as pd
import streamlit as st
import time
import shelve

# Trabalhando no assitente
# Inicialização da instância do cliente OpenAI com chave de API
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -----------------------------------------------------------------
# Gerenciando threads
# -----------------------------------------------------------------
def check_if_thread_exists(wa_id):
    with shelve.open("threads_db") as threads_shelf:
            return threads_shelf.get(wa_id, None)
    
def store_thread(thread_id):
     with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf[thread_id] = True


# -----------------------------------------------------------------
# Gerando resposta
# -----------------------------------------------------------------
# Função para criar conversa e perguntar
def generate_response(message_body, thread_id=None):
    # Verifica se a thread ja existe para recuperar o historico
    #thread_id = check_if_thread_exists(wa_id)

    # Se a thread não existir, cria uma nova e guarda no shelf
    if thread_id is None:
         print(f"Criando nova thread")
         thread = client.beta.threads.create()
         store_thread(thread.id)
         thread_id = thread.id

    # Se for existente, recupera a thread
    else:
         print(f"Recuperando conversa")
         thread = client.beta.threads.retrieve(thread_id)

    # Adiciona mensagem a thread (conversa)
    message = client.beta.threads.messages.create(
        thread_id = thread_id,
        role = "user",
        content=message_body,
    )

    # Roda o assistente e pega nova mensagem
    new_message = run_assistant(thread)
    print(f"Resposta:", new_message)
    return new_message

# -----------------------------------------------------------------
# Rodando assistente
# -----------------------------------------------------------------
def run_assistant(thread):
    # Pega o assistente
    assistant = client.beta.assistants.retrieve("asst_Vl27V5UoDuh8IDsidVm4HZLB")

    # Rodar o assistente
    run = client.beta.threads.runs.create(
        thread_id=thread.id, 
        assistant_id=assistant.id,
    )

    while run.status != "completed":
        # Espera retorno
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    # Recebe os mensageiros
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    #print(messages)

    # Testando tratamento da API
    # Transformando os dados das mensagens
    transformed_data = transform_api_response(messages)
    # Invertendo a lista
    transformed_data.reverse()
    # Exibindo os dados transformados
    print(transformed_data)

    new_message = messages.data[0].content[0].text.value
    print(new_message)
    return new_message

# Função teste - Gerar historico da conversa para imprimir na tela
#def generate_chat_history(wa_id, name):
#    # Verifica se a thread ja existe para recuperar o historico
#    thread_id = check_if_thread_exists(wa_id)
#
#    # Se a thread não existir, cria uma nova e guarda no shelf
#    if thread_id is None:
#         print(f"Criando nova thread para {name} com wa_id {wa_id}")
#         thread = client.beta.threads.create()
#         store_thread(wa_id, thread.id)
#         thread_id = thread.id
#
#    # Se for existente, recupera a thread
#    else:
#         print(f"Recuperando conversa para {name} e id {wa_id}")
#         thread = client.beta.threads.retrieve(thread_id)

# Tratar dados de retorno do histórico da Thread
def transform_api_response(messages):
    transformed_data = []
    
    # Itera sobre cada mensagem na lista
    for message in messages:
        content_blocks = message.content if hasattr(message, 'content') else []
        role = message.role if hasattr(message, 'role') else 'Não especificada'
        for block in content_blocks:
            if block.type == 'text':
                transformed_data.append({
                    'role': role,
                    'content': block.text.value
                })
    
    return transformed_data


#new_message = generate_response("Qual o nome da pessoa do curriculo?", "123", "joao")
#new_message = generate_response("da pessoa do curriculo", "456", "beatriz")
new_message = generate_response("Me diga quais sao os pontos fortes da pessoa do curriculo")




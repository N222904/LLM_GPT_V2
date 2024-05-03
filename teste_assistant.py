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
    
def store_thread(wa_id, thread_id):
     with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf[wa_id] = thread_id


# -----------------------------------------------------------------
# Gerando resposta
# -----------------------------------------------------------------
# Função para criar conversa e perguntar
def generate_response(message_body, wa_id, name):
    # Verifica se a thread ja existe para recuperar o historico
    thread_id = check_if_thread_exists(wa_id)

    # Se a thread não existir, cria uma nova e guarda no shelf
    if thread_id is None:
         print(f"Criando nova thread para {name} com wa_id {wa_id}")
         thread = client.beta.threads.create()
         store_thread(wa_id, thread.id)
         thread_id = thread.id

    # Se for existente, recupera a thread
    else:
         print(f"Recuperando conversa para {name} e id {wa_id}")
         thread = client.beta.threads.retrieve(thread_id)

    # Adiciona mensagem a thread (conversa)
    message = client.beta.threads.messages.create(
        thread_id = thread_id,
        role = "user",
        content=message_body,
    )

    # Roda o assistente e pega nova mensagem
    new_message = run_assistant(thread)
    print(f"Para {name}:", new_message)
    return new_message

# -----------------------------------------------------------------
# Rodando assistente
# -----------------------------------------------------------------
def run_assistant(thread):
    # Pega o assistente
    assistant = client.beta.assistants.retrieve("asst_Vl27V5UoDuh8IDsidVm4HZLB")
    #thread = client.beta.threads.retrieve("thread_TilArJcR0RTOSdKIJ7pKeASy") - Thread com pergunta existente
    #thread = client.beta.threads.retrieve("thread_l93M6SyiNWnyAaJEygDx7j6J") - Thread vazia

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
    print(messages)
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

# Função em teste - Tratar dados de retorno do histórico da Thread
def transform_api_response(api_response):
    transformed_data = []
    
    # Verifica se há mensagens na resposta da API
    if not api_response:
        print("Nenhuma mensagem encontrada na resposta da API.")
        return transformed_data

    # Itera sobre cada mensagem na lista
    for message in api_response['data']:
        content_blocks = message.get('content', [])
        for block in content_blocks:
            if block['type'] == 'text':
                transformed_data.append({
                    'role': message.get('role', 'Não especificada'),
                    'value': block['text']['value']
                })
    
    return transformed_data


new_message = generate_response("Qual o nome da pessoa do curriculo?", "123", "joao")
#new_message = generate_response("da pessoa do curriculo", "456", "beatriz")
#new_message = generate_response("qual foi a ultima pergunta feita?", "456", "beatriz")




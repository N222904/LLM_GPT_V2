# Importando as bibliotecas necessárias
import openai
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import time
import shelve

# -----------------------------------------------------------------
# Inicialização da instância do cliente OpenAI com chave de API
# -----------------------------------------------------------------
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -----------------------------------------------------------------
# Gerenciando threads
# -----------------------------------------------------------------
def check_if_thread_exists(thread_id):
    with shelve.open("threads_db") as threads_shelf:
        return threads_shelf.get(thread_id, None)
    
def store_thread(thread_id):
    with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf[thread_id] = True  # Você pode armazenar True para indicar a existência da thread

# -----------------------------------------------------------------
# Gerando resposta
# -----------------------------------------------------------------
# Função para criar conversa e perguntar
def generate_response(message_body, thread_id = None):
    # Verifica se a thread ja existe para recuperar o historico
    #thread_id = check_if_thread_exists(wa_id)

    # Se a thread não existir, cria uma nova e guarda no shelf
    if thread_id is None:
         thread = client.beta.threads.create()
         store_thread(thread.id)
         thread_id = thread.id
         st.session_state['in_chat'] = thread_id
         print(st.session_state['in_chat'])

    # Se for existente, recupera a thread
    else:
         thread = client.beta.threads.retrieve(thread_id)

    # Adiciona mensagem a thread (conversa)
    message = client.beta.threads.messages.create(
        thread_id = thread.id,
        role = "user",
        content=message_body,
    )

    # Roda o assistente e pega nova mensagem
    new_message = run_assistant(thread_id)
    return new_message

# -----------------------------------------------------------------
# Rodando assistente
# -----------------------------------------------------------------
# Função para rodar assistente e pegar nova mensagem
def run_assistant(thread, historico=False):
    # Pega o assistente
    assistant = client.beta.assistants.retrieve("asst_Vl27V5UoDuh8IDsidVm4HZLB")

    # Rodar o assistente
    run = client.beta.threads.runs.create(
        thread_id=thread, 
        assistant_id=assistant.id,
    )

    while run.status != "completed":
        # Espera retorno
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(thread_id=thread, run_id=run.id)


    # Recebe os mensageiros
    messages = client.beta.threads.messages.list(thread_id=thread)

    if historico == True:
        # Transformando os dados das mensagens
        transformed_data = transform_api_response(messages)
        # Invertendo a lista
        transformed_data.reverse()
        # Exibindo os dados transformados
        return transformed_data
    else:
        new_message = messages.data[0].content[0].text.value
        return new_message

# -----------------------------------------------------------------
# Tratando histórico da thread 
# -----------------------------------------------------------------
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

# Inicializando estado da sessão:
# Initialization
if 'in_chat' not in st.session_state:
    st.session_state['in_chat'] = None

# Título da interface de Streamlit
st.title("GPT Analítico")

# Barra lateral e botões, carrega chat ao clicar. 
with shelve.open('threads_db') as db:
    # Itera sobre todas as chaves e imprime no nome da conversa
    for chat_thread in db.keys():
        button_label = chat_thread
        if st.sidebar.button(button_label):
            st.session_state['in_chat'] = chat_thread
            current_chat_id = chat_thread
            st.session_state.messages = []
            # Recuperar historico de conversa em lista de dicts
            msgs_antigas  = run_assistant(chat_thread, historico=True)
            for row in msgs_antigas:
                st.session_state.messages.append({"role": row['role'], "content": row['content']})
                with st.chat_message(row['role']):
                    st.markdown(row['content'])



# Definição do modelo padrão para usar com o OpenAI
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4"

# Inicializa a lista de mensagens
if "messages" not in st.session_state:
    st.session_state.messages = []

# Criação de campo de entrada para a mensagem do usuário
if prompt := st.chat_input("Escreva aqui:"):
    for i in range(len(st.session_state.messages)):
        aux = st.session_state.messages[i]["role"]
        with st.chat_message(aux):
            st.markdown(st.session_state.messages[i]["content"])
            
    # A mensagem do usuário é adicionada à lista de mensagens
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Aqui, passa a resposta do usuário para o assistente OpenAI e gera a resposta do assistente
    with st.chat_message("assistant"):
        if st.session_state['in_chat'] != None:
            nova_mensagem = generate_response(message_body=prompt,thread_id=str(st.session_state['in_chat']))
        else:
            nova_mensagem = generate_response(message_body=prompt)
        st.markdown(nova_mensagem)

    # A resposta do assistente é adicionada à lista de mensagens
    st.session_state.messages.append({"role": "assistant", "content": nova_mensagem})
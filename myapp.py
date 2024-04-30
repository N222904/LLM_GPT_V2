# Importando as bibliotecas necessárias
import openai
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd

CSV_FILE = "dataset_dummy_curso.csv"
try:
    chat_history_df = pd.read_csv(CSV_FILE)
except FileNotFoundError:
    chat_history_df = pd.DataFrame(columns=["ChatID", "Role", "Content"])

# Verificando se a chave 'key' existe no estado da sessão
# Se não existir, é inicializado um valor
#if 'key' not in st.session_state:
#    st.session_state['key'] = 'value'

# Título da interface de Streamlit
st.title("GPT Analítico")

def get_button_label(chat_df, chat_id):
    first_message = chat_df[(chat_df["ChatID"] == chat_id) & (chat_df["Role"] == "user")].iloc[0]["Content"]
    return f"Chat {chat_id[0:7]}: {' '.join(first_message.split()[:5])}..."


# Barra lateral e botões, carrega chat ao clicar. 
# Funcional, GPT corrigiu.
for chat_id in chat_history_df["ChatID"].unique():
    button_label = get_button_label(chat_history_df, chat_id)
    if st.sidebar.button(button_label):
        current_chat_id = chat_id
        for i, row in chat_history_df[chat_history_df["ChatID"] == chat_id].iterrows():
            st.session_state.messages.append({"role": row['Role'], "content": row['Content']})
            with st.chat_message(row['Role']):
                st.markdown(row['Content'])


# Inicialização da instância do cliente OpenAI com chave de API
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Definição do modelo padrão para usar com o OpenAI
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4"

# Inicializa a lista de mensagens
if "messages" not in st.session_state:
    st.session_state.messages = []


## Aqui, ele itera sobre todas as mensagens do CSV e as exibe (teste)
#for i in range(len(chat_history_df)):
#    st.session_state.messages.append({"role": chat_history_df['Role'][i], "content": chat_history_df['Content'][i]})
#    with st.chat_message(chat_history_df["Role"][i]):
#        st.markdown(chat_history_df["Content"][i])



## Aqui, ele itera sobre todas as mensagens e as exibe (ORIGINAL)
#for message in st.session_state.messages:
#    with st.chat_message(message["role"]):
#        st.markdown(message["content"])

# Criação de campo de entrada para a mensagem do usuário
if prompt := st.chat_input("Escreva aqui:"):
    # A mensagem do usuário é adicionada à lista de mensagens
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Aqui, passa a resposta do usuário para o assistente OpenAI e gera a resposta do assistente
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
        
    # A resposta do assistente é adicionada à lista de mensagens
    st.session_state.messages.append({"role": "assistant", "content": response})
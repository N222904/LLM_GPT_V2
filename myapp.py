# Importando as bibliotecas necessárias
import openai
import streamlit as st

# Verificando se a chave 'key' existe no estado da sessão
# Se não existir, é inicializado um valor
if 'key' not in st.session_state:
    st.session_state['key'] = 'value'

# Título da interface de Streamlit
st.title("GPT Protocolos De Inseminação")

# Inicialização da instância do cliente OpenAI com chave de API
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Definição do modelo padrão para usar com o OpenAI
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4"

# Inicializa a lista de mensagens
if "messages" not in st.session_state:
    st.session_state.messages = []

# Aqui, ele itera sobre todas as mensagens e as exibe
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

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
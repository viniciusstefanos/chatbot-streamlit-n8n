import streamlit as st
import requests
import uuid
import os

# Carregar variáveis do .env (opcional)
from dotenv import load_dotenv
load_dotenv()

# Função para gerar uma session ID única
def get_session_id():
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())
    return st.session_state["session_id"]

# Função para enviar a mensagem ao webhook do n8n
def query_n8n(session_id, user_input):
    webhook_url = os.getenv("N8N_WEBHOOK_URL")
    bearer_token = os.getenv("BEARER_TOKEN")

    if not webhook_url:
        raise ValueError("N8N_WEBHOOK_URL não está definida.")
    if not bearer_token:
        raise ValueError("BEARER_TOKEN não está definida.")

    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "sessionId": session_id,
        "chatInput": user_input
    }

    response = requests.post(webhook_url, json=payload, headers=headers)
    response.raise_for_status()

    data = response.json()
    if "output" not in data:
        raise ValueError("Resposta do webhook não contém o campo 'output'.")
    
    return data["output"]

# Função principal da aplicação
def main():
    st.set_page_config(page_title="Chatbot com LLM e n8n", layout="centered")
    st.title("💬 Chatbot com LLM e n8n")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Digite sua mensagem...")

    if user_input:
        session_id = get_session_id()
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                try:
                    output = query_n8n(session_id, user_input)
                except Exception as e:
                    output = f"Erro: {str(e)}"

                st.markdown(output)
                st.session_state.messages.append({"role": "assistant", "content": output})

if __name__ == "__main__":
    main()
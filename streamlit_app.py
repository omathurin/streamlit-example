import openai
import streamlit as st

st.title("ChatGPT-like clone")

# Replicate Credentials
with st.sidebar:
    st.title('🦙💬 ChatGPT-like Chatbot')
    if 'OPENAI_API_KEY' in st.secrets:
        st.success('API key already provided!', icon='✅')
        openai_api = st.secrets['OPENAI_API_KEY']
    else:
        openai_api = st.text_input('Enter OpenAI API token:', type='password')
        if not (openai_api.startswith('sk-') and len(openai_api)==51):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')

    models = ['gpt-3.5-turbo', 'gpt-4']
    model = st.sidebar.selectbox("Select Model", models)
    if ((model == 'gpt-3.5-turbo') or (model == 'text-davinci-003')):
        max_ = 4096
    else:
        max_ = 8192
        
    with st.expander("Advanced Settings"):
        temperature = st.slider("Temperature", min_value=0.1, max_value=1.0, value=0.7, step=0.1)
        max_tokens = st.slider("Max Tokens", min_value=64, max_value=max_, value=1024, step=64)
        top_p = st.slider("Top P", min_value=0.1, max_value=1.0, value=1.0, step=0.1)
        frequency_penalty = st.slider("Frequency Penalty", min_value=0.0, max_value=1.0, value=0.0, step=0.1)
        presence_penalty = st.slider("Presence Penalty", min_value=0.0, max_value=1.0, value=0.0, step=0.1)
        n = st.slider("n", min_value=1, max_value=5, value=1, step=1)

openai.api_key = openai_api


if "openai_model" not in st.session_state:
    #st.session_state["openai_model"] = "gpt-3.5-turbo"
    st.session_state["openai_model"] = model

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in openai.ChatCompletion.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        ):
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

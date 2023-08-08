import openai
import streamlit as st
from elevenlabs import generate, set_api_key
from hugchat import hugchat
from hugchat.login import Login

def generate_and_play(audio_text):
    elevenlabs_key = st.secrets['ELEVENLABS_API_KEY']
    set_api_key(elevenlabs_key)
    try:
        # Generate audio using ElevenLabs
        audio = generate(
            text=audio_text,
            voice="Bella",
            model='eleven_monolingual_v1'
        )
        # Play the audio
        st.audio(audio, format="audio/wav", start_time=0, sample_rate=None)
    except:
        pass

st.title("ChatGPT-like clone")

# Replicate Credentials
with st.sidebar:
    st.title('💬 Chatbot')

    models = ['gpt-3.5-turbo', 'gpt-4', 'text-davinci-003', 'HugChat']
    model = st.sidebar.selectbox("Select Model", models)

    if ((model == 'gpt-3.5-turbo') or (model == 'gpt-4') or (model == 'text-davinci-003')):
        if 'OPENAI_API_KEY' in st.secrets:
            st.success('API key already provided!', icon='✅')
            openai_api = st.secrets['OPENAI_API_KEY']
        else:
            openai_api = st.text_input('Enter OpenAI API token:', type='password')
            if not (openai_api.startswith('sk-') and len(openai_api)==51):
                st.warning('Please enter your credentials!', icon='⚠️')
            else:
                st.success('Proceed to entering your prompt message!', icon='👉')
        openai.api_key = openai_api
    else:
        if (model == 'HugChat'):
            if ('HUGGINGFACE_EMAIL' in st.secrets) and ('HUGGINGFACE_PASS' in st.secrets):
                st.success('HuggingFace Login credentials already provided!', icon='✅')
                hf_email = st.secrets['HUGGINGFACE_EMAIL']
                hf_pass = st.secrets['HUGGINGFACE_PASS']
            else:
                hf_email = st.text_input('Enter E-mail:', type='password')
                hf_pass = st.text_input('Enter password:', type='password')
                if not (hf_email and hf_pass):
                    st.warning('Please enter your credentials!', icon='⚠️')
                else:
                    st.success('Proceed to entering your prompt message!', icon='👉')

    with st.expander("Advanced Settings"):
        if ((model == 'gpt-3.5-turbo') or (model == 'gpt-4') or (model == 'text-davinci-003')):
            if ((model == 'gpt-3.5-turbo') or (model == 'text-davinci-003')):
                max_ = 4096
            else:
                max_ = 8192
        
            temperature = st.slider("Temperature", min_value=0.1, max_value=1.0, value=0.7, step=0.1)
            max_tokens = st.slider("Max Tokens", min_value=64, max_value=max_, value=1024, step=64)
            top_p = st.slider("Top P", min_value=0.1, max_value=1.0, value=1.0, step=0.1)
            frequency_penalty = st.slider("Frequency Penalty", min_value=0.0, max_value=1.0, value=0.0, step=0.1)
            presence_penalty = st.slider("Presence Penalty", min_value=0.0, max_value=1.0, value=0.0, step=0.1)
            n = st.slider("n", min_value=1, max_value=5, value=1, step=1)
            # Add best_of option for text-davinci-003
            if model == 'text-davinci-003':
                best_of = st.slider("Best Of", min_value=1, max_value=5, value=1, step=1)
        else:
            if (model == 'HugChat'):
                dummy = st.slider("Temperature", min_value=0.1, max_value=1.0, value=0.7, step=0.1)


# Function for generating LLM response
def hf_generate_response(prompt_input, email, passwd):
    # Hugging Face Login
    sign = Login(email, passwd)
    cookies = sign.login()
    # Create ChatBot                        
    chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
    return chatbot.chat(prompt_input)

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
        if (model == 'HugChat'):
            for response in hf_generate_response(prompt, hf_email, hf_pass) :
                full_response += response
                message_placeholder.markdown(full_response + "▌")
        else:
            if ((model == 'gpt-3.5-turbo') or (model == 'gpt-4')):
                for response in openai.ChatCompletion.create(
                    model=st.session_state["openai_model"],
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    frequency_penalty=frequency_penalty,
                    presence_penalty=presence_penalty,
                    n=n,
                    stream=True,
                ):
                    full_response += response.choices[0].delta.get("content", "")
                    message_placeholder.markdown(full_response + "▌")
            else:
                if (model == 'text-davinci-003'):
                    response = openai.Completion.create(
                        engine=model,
                        prompt=prompts,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=top_p,
                        frequency_penalty=frequency_penalty,
                        presence_penalty=presence_penalty,
                        n=n,
                        best_of=best_of
                    )
        response_output = response['choices'][0]['text']
        message_placeholder.markdown(full_response)
        generate_and_play(audio_text=full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})






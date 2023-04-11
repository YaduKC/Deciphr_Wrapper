import streamlit as st
import markdown
import openai
# import config
from transformers import GPT2TokenizerFast

# openai.api_key = config.OPENAI_KEY
openai.api_key = st.secrets["OPENAI_KEY"]

if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
    
if "GPT_TOKENIZER" not in st.session_state:
    GPT_TOKENIZER = GPT2TokenizerFast.from_pretrained("gpt2")

if "podcast_prompt" not in st.session_state:
    with open("podcast_prompt.txt", "r") as f:
        st.session_state.podcast_prompt = f.read()
        
if "pr_prompt" not in st.session_state:
    with open("pr_prompt.txt", "r") as f:
        st.session_state.pr_prompt = f.read()

if "transcript" not in st.session_state:
    st.session_state.transcript = None

if "suite" not in st.session_state:
    st.session_state.suite = None
    
if "model" not in st.session_state:
    st.session_state.model = None

if "parameters" not in st.session_state:
    st.session_state.parameters = None

if "result" not in st.session_state:
    st.session_state.result = ""

def reset_suite():
    st.session_state.suite = None

def login():
    st.title('Deciphr Admin Portal')
    user_name = st.text_input('Username')
    password = st.text_input('Password', type='password')
    if st.button('Login'):
        if user_name == 'admin' and password == 'admin':
            st.session_state.is_logged_in = True
            st.experimental_rerun()
        else:
            st.error('Incorrect username or password')            

def dashboard():
    st.title('Dashboard')
    st.write("---")
    st.info("Upload your transcript to get started.")
    transcript = st.text_area("Transcript", height=400)
    suite = st.selectbox("Content Suite", ["Podcast", "PR Agency"])
    if st.button("Generate"):
        if transcript == "":
            st.error("Please upload your transcript")
        else:
            st.session_state.result = ""
            st.session_state.suite = suite
            token_list = GPT_TOKENIZER(transcript)['input_ids']
            num_tokens = len(token_list)
            token_list = token_list[:5000] if len(token_list) > 5000 else token_list
            text = GPT_TOKENIZER.decode(token_list, skip_special_tokens=True)
            st.session_state.transcript = text
            st.write("---")
            st.info("Input tokens(Excluding prompt): {}".format(num_tokens))
            st.info(f"Input tokens trimmed to {len(token_list)} tokens")
            generate_content()
    st.write("---")
    if st.session_state.result != "":
        st.markdown(st.session_state.result)
        st.write("---")
        html = markdown.markdown(st.session_state.result)
        st.info("Set the file name and download the generated content. Please make sure to press enter after typing the file name.")
        file_name = "output"
        file_name = st.text_input("File Name", value=file_name)
        st.download_button("Download", html, file_name=f"{file_name}.html", mime="text/plain")
        st.write("---")

def generate_content():
    if st.session_state.suite == "Podcast":
        prompt = f"{st.session_state.transcript}\n\n{st.session_state.podcast_prompt}"
    elif st.session_state.suite == "PR Agency":
        prompt = f"{st.session_state.transcript}\n\n{st.session_state.pr_prompt}"
        
    report = []
    res_box = st.empty()
    # Looping over the response
    for resp in openai.ChatCompletion.create(model='gpt-4',
                                        messages=[{'role': 'user', 'content': prompt}],
                                        max_tokens=2400, 
                                        temperature = 0.9,
                                        stream = True):
        # join method to concatenate the elements of the list 
        # into a single string, 
        # then strip out any empty strings
        if "role" in resp['choices'][0]['delta']:
            continue
        if resp['choices'][0]['delta']:
            report.append(resp['choices'][0]['delta']['content'])
            st.session_state.result += report[-1]
            res_box.markdown(f'{st.session_state.result}')
    # Clear res_box
    res_box.empty()


if __name__ == '__main__':
    if not st.session_state.is_logged_in:
        login()
    else:
        dashboard()
        
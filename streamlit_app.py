import streamlit as st
import datetime
import re
from openai import OpenAI
from st_copy_to_clipboard import st_copy_to_clipboard

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# Load custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("safeit.css")

# Load system prompt
def load_system_prompt(file_path=".streamlit/system_prompt.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read().strip()
    except Exception as e:
        print(f"Error loading system prompt: {e}")
        return ""

# Parse OpenAI response for tags
def parse_response(response):
    content = response.choices[0].message.content.strip()
    hl_match = re.search(r'<headline>(.*?)</headline>', content, re.DOTALL)
    txt_match = re.search(r'<improved_entry>(.*?)</improved_entry>', content, re.DOTALL)
    fb_match = re.search(r'<supervisor_feedback>(.*?)</supervisor_feedback>', content, re.DOTALL)
    return (
        hl_match.group(1).strip() if hl_match else "",
        txt_match.group(1).strip() if txt_match else "",
        fb_match.group(1).strip() if fb_match else ""
    )

# Generate with OpenAI
def generate_response(date_time, author, citizen, entry):
    system = load_system_prompt()
    user_prompt = f"""
<entry_date>\n{date_time.strftime('%Y-%m-%d')}\n</entry_date>
<author_name>\n{author}\n</author_name>
<citizen_name>\n{citizen}\n</citizen_name>
<journal_entry>\n{entry}\n</journal_entry>
"""
    messages = [
        {"role": "system", "content": system},
        {"role": "user",   "content": user_prompt}
    ]
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=4096,
        temperature=0.7
    )
    return parse_response(resp)

# Initialize form visibility flag
if "show_form" not in st.session_state:
    st.session_state.show_form = True

# Callback to handle initial form submission
def submit_journal():
    author = st.session_state.input_author
    citizen = st.session_state.input_citizen
    entry = st.session_state.input_journal
    if not (author and citizen and entry):
        st.warning("Udfyld venligst alle felter før du sender journalnotatet.")
        return
    dt = st.session_state.input_date
    hl, txt, fb = generate_response(dt, author, citizen, entry)
    st.session_state.headline = hl
    st.session_state.generated_text = txt
    st.session_state.feedback = fb
    st.session_state.show_form = False

# Callback to regenerate text from stored inputs
def generate_new_text():
    dt = st.session_state.input_date
    auth = st.session_state.input_author
    cit = st.session_state.input_citizen
    ent = st.session_state.input_journal
    hl, txt, fb = generate_response(dt, auth, cit, ent)
    st.session_state.headline = hl
    st.session_state.generated_text = txt
    st.session_state.feedback = fb

# Callback to reset everything
def start_over():
    for key in ["input_date", "input_author", "input_citizen", "input_journal", "headline", "generated_text", "feedback"]:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.show_form = True

# HEADER
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown(
        "<div class='header'>JournalHelper<br><small>Velkommen til din personlige hjælper</small></div>",
        unsafe_allow_html=True
    )
with col2:
    st.image(
        "https://air-safeit-editor-frontend-v0-3.onrender.com/safe-it-logo.png",
        width=280
    )

# Main app: conditional form + output
if st.session_state.show_form:
    st.markdown("<div class='turquoise-bg'><div class='form-container'>", unsafe_allow_html=True)
    with st.form("journal_form"):
        st.date_input(
            "Dato og klokkeslæt", datetime.date.today(), format="DD/MM/YYYY", key="input_date"
        )
        st.text_input(
            "Forfatter", placeholder="Dit navn eller initialer", key="input_author"
        )
        st.text_input(
            "Borgernavn", placeholder="Navn eller initialer på borgeren", key="input_citizen"
        )
        st.text_area(
            "Journalen",
            placeholder='Kort beskrivelse af situationen eller aktiviteten.\nEksempel: "Under dagens fællesmiddag..."',
            key="input_journal"
        )
        st.form_submit_button(
            "Gennemgå Journalnotat",
            on_click=submit_journal
        )
    st.markdown("</div></div>", unsafe_allow_html=True)
else:
    st.title("Generated Journal")
    st.text_area(
        "Headline", value=st.session_state.headline, key="headline_output"
    )
    st.text_area(
        "Generated Text", value=st.session_state.generated_text,
        key="generated_text_output", disabled=True, height=200
    )
    st.text_area(
        "Feedback to Supervisor", value=st.session_state.feedback,
        key="feedback_output", height=150
    )
    plain_text = (
        f"Headline: {st.session_state.headline}\n"
        f"Generated Text: {st.session_state.generated_text}\n"
        f"Feedback to Supervisor: {st.session_state.feedback}\n"
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st_copy_to_clipboard(
            plain_text,
            before_copy_label='Tryk for at kopiere',
            after_copy_label='Tekst kopieret!'
        )
    with col2:
        st.button("Generér ny tekst", on_click=generate_new_text)
    with col3:
        st.button("Start forfra", on_click=start_over)

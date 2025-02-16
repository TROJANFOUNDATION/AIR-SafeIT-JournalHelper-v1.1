import streamlit as st
import datetime
import openai  # NEW: Import OpenAI for API calls

# Custom CSS for styling
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("safeit.css")

# ----------------- NEW: OpenAI API Setup -----------------
# In your .streamlit/secrets.toml, include:
# [openai]
# api_key = "YOUR_OPENAI_API_KEY"
openai.api_key = st.secrets["openai"]["api_key"]

st.markdown("<div class='turquoise-bg'>", unsafe_allow_html=True)

# ----------------- NEW: Session State Initialization -----------------
if "view" not in st.session_state:
    st.session_state.view = "input"  # "input" for form view, "output" for generated view
if "headline" not in st.session_state:
    st.session_state.headline = ""
if "generated_text" not in st.session_state:
    st.session_state.generated_text = ""
if "feedback" not in st.session_state:
    st.session_state.feedback = ""
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

# ----------------- NEW: OpenAI API Response Function -----------------
def generate_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.7
    )
    result = response.choices[0].message.content.strip()
    parts = result.split("\n")
    headline = parts[0] if len(parts) > 0 else ""
    generated_text = parts[1] if len(parts) > 1 else ""
    feedback = parts[2] if len(parts) > 2 else ""
    return headline, generated_text, feedback

# ----------------- NEW: Callback Functions -----------------
def generate_new_text():
    # Re-generate output using the stored input_text
    headline, generated_text, feedback = generate_response(st.session_state.input_text)
    st.session_state.headline = headline
    st.session_state.generated_text = generated_text
    st.session_state.feedback = feedback

def start_over():
    # Reset session state to show the input form again
    st.session_state.view = "input"
    st.session_state.headline = ""
    st.session_state.generated_text = ""
    st.session_state.feedback = ""
    st.session_state.input_text = ""
    st.experimental_rerun()

# HEADER
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("<div class='header'>JournalHelper<br><small>Velkommen til din personlige hjælper</small></div>", unsafe_allow_html=True)
with col2:
    st.image("https://i.ibb.co/tw8pVgJt/Screenshot-2025-02-16-at-10-14-01.png", width=50)  # Placeholder logo

st.markdown("<div class='form-container'>", unsafe_allow_html=True)

# FORM
with st.form("journal_form"):
    date_time = st.date_input("Dato og klokkeslæt", datetime.date.today(), format="DD/MM/YYYY")
    author = st.text_input("Forfatter", placeholder="Dit navn eller initialer", key="author", help="Skriv dit navn eller dine initialer")
    citizen_name = st.text_input("Borgernavn", placeholder="Navn eller initialer på borgeren", key="citizen_name", help="Indtast borgerens navn eller initialer")
    journal_entry = st.text_area("Journalen", placeholder='Kort beskrivelse af situationen eller aktiviteten. \nEksempel: "Under dagens fællesmiddag..."', key="journal_entry")

    submit = st.form_submit_button("Gennemgå Journalnotat")

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)  # Close turquoise-bg

# SIMULATED FORM SUBMISSION (DUMMY TARGET)
if submit:
    if author and citizen_name and journal_entry:
        st.success("Journalnotatet er blevet indsendt!")
        st.markdown(f"""
            ### 📜 Journalnotat
            **Dato:** {date_time.strftime('%d/%m/%Y')}  
            **Forfatter:** {author}  
            **Borgernavn:** {citizen_name}  
            ---
            **Journal:**  
            {journal_entry}
        """)
    else:
        st.warning("Udfyld venligst alle felter før du sender journalnotatet.")
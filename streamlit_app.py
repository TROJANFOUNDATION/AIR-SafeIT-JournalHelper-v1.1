import streamlit as st
import datetime
import re
from openai import OpenAI
from st_copy_to_clipboard import st_copy_to_clipboard

client = OpenAI(api_key=st.secrets["openai"]["api_key"])  # NEW: Import OpenAI for API calls

# Custom CSS for styling
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("safeit.css")

# ----------------- NEW: OpenAI API Setup -----------------
# In your .streamlit/secrets.toml, include:
# [openai]
# api_key = "YOUR_OPENAI_API_KEY"

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
if "input_date" not in st.session_state:
    st.session_state.input_date = None
if "input_author" not in st.session_state:
    st.session_state.input_author = ""
if "input_citizen" not in st.session_state:
    st.session_state.input_citizen = ""
if "input_journal" not in st.session_state:
    st.session_state.input_journal = ""

# ----------------- NEW: Loading System Prompt from file -----------------
def load_system_prompt(file_path=".streamlit/system_prompt.txt"):
    """
    Loads the system prompt from a specified text file.

    Args:
        file_path (str): Path to the system prompt file.

    Returns:
        str: The content of the system prompt file, stripped of leading/trailing whitespace.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read().strip()
    except Exception as e:
        print(f"Error loading system prompt from {file_path}: {e}")
        return ""

# ----------------- NEW: Parsing now standalone function -----------------
def parse_response(response):
    """
    Parses the response from the OpenAI API to extract headline, generated text, and feedback based on specific tags.
    """
    content = response.choices[0].message.content.strip()
    headline = re.search(r'<headline>(.*?)</headline>', content, re.DOTALL)
    generated_text = re.search(r'<improved_entry>(.*?)</improved_entry>', content, re.DOTALL)
    feedback = re.search(r'<supervisor_feedback>(.*?)</supervisor_feedback>', content, re.DOTALL)
    return (
        headline.group(1).strip() if headline else "",
        generated_text.group(1).strip() if generated_text else "",
        feedback.group(1).strip() if feedback else ""
    )

# ----------------- NEW: OpenAI API Response Function -----------------
def generate_response(date_time, author, citizen_name, journal_entry):
    """
    Generates a response from the OpenAI Chat Completions API by combining a system prompt
    with a user prompt constructed from the provided form fields.

    Args:
        date_time (datetime.date): The selected date.
        author (str): The author of the journal.
        citizen_name (str): The citizen's name.
        journal_entry (str): The journal entry text.

    Returns:
        tuple: A tuple containing the headline, generated text, and feedback.
    """
    # Load the developer (system) prompt
    developer_prompt = load_system_prompt()

    # Construct the user prompt with improved formatting
    # user_prompt = (
    #     f"Journal Entry Details:\n"
    #     f"Date: {date_time.strftime('%d/%m/%Y')}\n"
    #     f"Author: {author}\n"
    #     f"Citizen Name: {citizen_name}\n"
    #     f"Journal Entry: {journal_entry}"
    # )
    # Improved user prompt to include dynamic user data
    user_prompt = f"""
    This is my journal entry and key information about it. Please follow your developer/system instructions and use the data I have included to generate a better report and headline.

    <entry_date>
    {date_time.strftime('%Y-%m-%d')}
    </entry_date>

    <author_name>
    {author}
    </author_name>

    <citizen_name>
    {citizen_name}
    </citizen_name>

    <journal_entry>
    {journal_entry}
    </journal_entry>
    """

    # Construct messages for the API request following OpenAI best practices
    messages = [
        {"role": "system", "content": developer_prompt},
        {"role": "user", "content": user_prompt}
    ]

    # Call the API using the updated messages format
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=4096,
        temperature=0.7
    )
    
    # result = response.choices[0].message.content.strip()
    # parts = result.split("\n")
    # headline = parts[0] if len(parts) > 0 else ""
    # generated_text = parts[1] if len(parts) > 1 else ""
    # feedback = parts[2] if len(parts) > 2 else ""
    # return headline, generated_text, feedback
    return parse_response(response)

# ----------------- NEW: Callback Functions -----------------
def generate_new_text():
    st.session_state.update(dict(zip(
        ['headline','generated_text','feedback'],
        generate_response(st.session_state.input_date, st.session_state.input_author, st.session_state.input_citizen, st.session_state.input_journal)
    )))
def start_over():
    st.session_state.update({"view":"input","headline":"","generated_text":"","feedback":"","input_text":"","input_date":None,"input_author":"","input_citizen":"","input_journal":""})

# HEADER
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("<div class='header'>JournalHelper<br><small>Velkommen til din personlige hjælper</small></div>", unsafe_allow_html=True)
with col2:
    st.image("https://i.ibb.co/tw8pVgJt/Screenshot-2025-02-16-at-10-14-01.png", width=50)  # Placeholder logo

st.markdown("<div class='form-container'>", unsafe_allow_html=True)

# ----------------- NEW: Main App Flow with Two Views -----------------
if st.session_state.view == "input":
    # -------- Input View (Original Form modified) --------
    st.markdown("<div class='form-container'>", unsafe_allow_html=True)
    with st.form("journal_form"):
        date_time = st.date_input("Dato og klokkeslæt", datetime.date.today(), format="DD/MM/YYYY")
        author = st.text_input("Forfatter", placeholder="Dit navn eller initialer", key="author_input", help="Skriv dit navn eller dine initialer")
        citizen_name = st.text_input("Borgernavn", placeholder="Navn eller initialer på borgeren", key="citizen_name_input", help="Indtast borgerens navn eller initialer")
        journal_entry = st.text_area("Journalen", placeholder='Kort beskrivelse af situationen eller aktiviteten. \nEksempel: "Under dagens fællesmiddag..."', key="journal_entry_input")
        submit = st.form_submit_button("Gennemgå Journalnotat")
    st.markdown("</div>", unsafe_allow_html=True)  # Close form-container
    st.markdown("</div>", unsafe_allow_html=True)  # Close turquoise-bg

    if submit:
        if author and citizen_name and journal_entry:
            # Store individual form fields in session state for re-use
            st.session_state.input_date = date_time
            st.session_state.input_author = author
            st.session_state.input_citizen = citizen_name
            st.session_state.input_journal = journal_entry

            # Generate response using separated parameters
            headline, generated_text, feedback = generate_response(date_time, author, citizen_name, journal_entry)
            
            # Optionally, store a combined text if needed for copy functionality
            st.session_state.input_text = (
                f"Date: {date_time.strftime('%d/%m/%Y')}\n"
                f"Forfatter: {author}\n"
                f"Borgernavn: {citizen_name}\n"
                f"Journal: {journal_entry}"
            )
            st.session_state.headline = headline
            st.session_state.generated_text = generated_text
            st.session_state.feedback = feedback
            st.session_state.view = "output"
            # st.rerun()  # Rerun to display the output view
        else:
            st.warning("Udfyld venligst alle felter før du sender journalnotatet.")

elif st.session_state.view == "output":
    # -------- Output View (Updated Generated Content) --------
    st.markdown("</div>", unsafe_allow_html=True)  # Ensure previous div is closed
    st.title("Generated Journal")

    # Editable textarea for headline
    st.text_area("Headline", value=st.session_state.headline, key="headline_output")
    
    # Non-editable textarea for generated text
    st.text_area("Generated Text", value=st.session_state.generated_text, key="generated_text_output", disabled=True, height=200)
    
    # Editable textarea for feedback
    st.text_area("Feedback to Supervisor", value=st.session_state.feedback, key="feedback_output", height=150)
    
    plain_text = (
        f"Headline: {st.session_state.headline}\n"
        f"Generated Text: {st.session_state.generated_text}\n"
        f"Feedback to Supervisor: {st.session_state.feedback}\n"
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st_copy_to_clipboard(plain_text, before_copy_label='Tryk for at kopiere', after_copy_label='Tekst kopieret!')
    with col2:
        st.button("Generér ny tekst", on_click=generate_new_text)
    with col3:
        st.button("Start forfra", on_click=start_over)
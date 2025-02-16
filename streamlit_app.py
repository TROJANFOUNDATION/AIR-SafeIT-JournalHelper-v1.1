import streamlit as st
import datetime

# Custom CSS for styling
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("safeit.css")

st.markdown("<div class='turquoise-bg'>", unsafe_allow_html=True)

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
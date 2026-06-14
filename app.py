import streamlit as st
import pandas as pd

EXCEL_FILE = "Template for sample Interview questions.xlsx"

st.set_page_config(
    page_title="Interview Prep Tracker",
    page_icon="📘",
    layout="wide"
)

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data(ttl=10)
def load_data():
    company_df = pd.read_excel(
        EXCEL_FILE,
        sheet_name="Company",
        engine="openpyxl"
    )

    questions_df = pd.read_excel(
        EXCEL_FILE,
        sheet_name="Interview_Questions",
        engine="openpyxl"
    )

    company_df = company_df.fillna("")
    questions_df = questions_df.fillna("")

    return company_df, questions_df


def refresh_data():
    st.cache_data.clear()
    st.rerun()


# -----------------------------
# Initialize Session State
# -----------------------------
if "page" not in st.session_state:
    st.session_state.page = "company_list"

if "selected_c_id" not in st.session_state:
    st.session_state.selected_c_id = None

if "selected_company" not in st.session_state:
    st.session_state.selected_company = None


# -----------------------------
# App Header
# -----------------------------
st.title("📘 Interview Prep Tracker")

if st.button("🔄 Refresh Data"):
    refresh_data()


# -----------------------------
# Load Excel
# -----------------------------
try:
    company_df, questions_df = load_data()
except FileNotFoundError:
    st.error(f"Excel file not found: {EXCEL_FILE}")
    st.stop()
except Exception as e:
    st.error(f"Error loading Excel file: {e}")
    st.stop()


# -----------------------------
# Page 1: Company List
# -----------------------------
def show_company_list():
    st.subheader("Companies Applied")

    if company_df.empty:
        st.warning("No company data found.")
        return

    for _, row in company_df.iterrows():
        with st.container(border=True):
            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                st.markdown(f"### {row['Company Name']}")
                st.write(f"**Role:** {row['Role Applied For']}")
                st.write(f"**Location:** {row['Loc']}")

            with col2:
                st.write(f"**Recruiter/Contact:** {row['Recruiter/Contact']}")
                apply_link = row["Apply Link"]

                if str(apply_link).startswith("http"):
                    st.markdown(f"[Apply Link]({apply_link})")
                else:
                    st.write(f"**Apply Link:** {apply_link}")

            with col3:
                if st.button(
                    "View Questions",
                    key=f"btn_{row['C_Id']}"
                ):
                    st.session_state.selected_c_id = row["C_Id"]
                    st.session_state.selected_company = row["Company Name"]
                    st.session_state.page = "questions"
                    st.rerun()


# -----------------------------
# Page 2: Interview Questions
# -----------------------------
def show_questions():
    selected_c_id = st.session_state.selected_c_id
    selected_company = st.session_state.selected_company

    st.subheader(f"Interview Questions - {selected_company}")

    if st.button("⬅ Back to Company List"):
        st.session_state.page = "company_list"
        st.session_state.selected_c_id = None
        st.session_state.selected_company = None
        st.rerun()

    filtered_df = questions_df[
        questions_df["C_Id"].astype(str) == str(selected_c_id)
    ]

    if filtered_df.empty:
        st.warning("No interview questions found for this company.")
        return

    # Optional filters
    rounds = ["All"] + sorted(filtered_df["Interview Round"].dropna().unique().tolist())
    selected_round = st.selectbox("Filter by Interview Round", rounds)

    if selected_round != "All":
        filtered_df = filtered_df[
            filtered_df["Interview Round"] == selected_round
        ]

    for _, row in filtered_df.iterrows():
        with st.container(border=True):
            st.markdown(f"### {row['Interview Round']}")
            st.write(f"**Role:** {row['Role Applied For']}")
            st.write(f"**Question:** {row['Question asked in Interview']}")
            st.write(f"**Tags/Comments:** {row['Tags/Comments']}")


# -----------------------------
# Navigation
# -----------------------------
if st.session_state.page == "company_list":
    show_company_list()
elif st.session_state.page == "questions":
    show_questions()
import streamlit as st
import pandas as pd
import csv
import re
from datetime import date
from typing import List, Tuple

# ---------------- Constants ---------------- #

REQUIRED_COLUMNS: List[str] = [
    'First Name', 'Middle Name', 'Last Name', 'Nickname', 'Student Number',
    'Email', 'Course Type', 'Student Home Institution Abbrev',
    'Address1', 'Address2', 'City', 'State', 'Postal Code', 'Country',
    'Home Phone', 'Work Phone', 'Mobile Phone', 'Course Level', 'Course Name',
    'Student Home Institution Name'
]

FILTER_COLUMNS: List[str] = [
    'Person Status Id',
    'Student Home Institution Name',
    'Course Status Id',
    'Enrolment Status Id'
]

ALLOWED_PERSON_STATUS = {'PERSON_ACTIVE'}
ALLOWED_COURSE_STATUS = {'PROGRAM_ACTIVE'}
ALLOWED_ENROLMENT_STATUS = {'ENROLMENT_ENROLLED'}
ALLOWED_INSTITUTIONS_PRIMARY = (
    'Australian Lutheran College',
    'Catholic Theological College',
    'Eva Burrows College',
    'School of Graduate Research',
    'St Athanasius College',
    'St Barnabas College',
    'St Francis College',
    'Uniting College for Leadership and Theology',
    'University of Divinity',
    'Whitley College',
    'Wollaston Theological College',
    'Yarra Theological Union'
)
ALLOWED_INSTITUTIONS_SECONDARY = (
    'Pilgrim Theological College',
    'Trinity College Theological School'
)

HOME_BRANCH_MAPPING = {
    'ALC': '267183', 'CTC': '266990', 'SAC': '266992', 'YTU': '266993',
    'UCLT': '270309', 'UD': '267183', 'WHT': '271609', 'WTC': '94194',
    'SBC': '148870', 'TRI': '267183', 'EBC': '267183', 'SFC': '267183',
    'SGR': '267183', 'PIL': '267183'
}

PHOTO_URL_MAPPING = {
    'ALC': 'https://mannix.org.au/images/ALC.png',
    'CTC': 'https://mannix.org.au/images/CTC.png',
    'SAC': 'https://mannix.org.au/images/SAC.png',
    'YTU': 'https://mannix.org.au/images/YTU.png',
    'UCLT': 'https://mannix.org.au/images/UCLT_vertical.jpg',
    'UD': 'https://mannix.org.au/images/UD.png',
    'WHT': 'https://mannix.org.au/images/WHI.png',
    'WTC': 'https://mannix.org.au/images/UD.png',
    'SBC': 'https://mannix.org.au/images/SBC-Logo.png',
    'TRI': 'https://mannix.org.au/images/TRI.png',
    'EBC': 'https://mannix.org.au/images/EBC.png',
    'SFC': 'https://mannix.org.au/images/UD.png',
    'SGR': 'https://mannix.org.au/images/UD.png',
    'PIL': 'https://mannix.org.au/images/UD.png'
}

FIELD_ORDER: List[str] = [
    "prefix", "givenName", "middleName", "familyName", "suffix", "nickname",
    "canSelfEdit", "dateOfBirth", "gender", "institutionId", "barcode",
    "idAtSource", "sourceSystem", "borrowerCategory", "circRegistrationDate",
    "oclcExpirationDate", "homeBranch", "primaryStreetAddressLine1",
    "primaryStreetAddressLine2", "primaryCityOrLocality", "primaryStateOrProvince",
    "primaryPostalCode", "primaryCountry", "primaryPhone", "secondaryStreetAddressLine1",
    "secondaryStreetAddressLine2", "secondaryCityOrLocality", "secondaryStateOrProvince",
    "secondaryPostalCode", "secondaryCountry", "secondaryPhone", "emailAddress",
    "mobilePhone", "notificationEmail", "notificationTextPhone", "patronNotes",
    "photoURL", "customdata1", "customdata2", "customdata3", "customdata4",
    "username", "illId", "illApprovalStatus", "illPatronType", "illPickupLocation"
]

EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$")
DEFAULT_EXPIRATION_DATE = date(2026, 12, 31)
EXPIRATION_DATE_FORMAT = "%Y-%m-%dT00:00:00"
DEFAULT_HOME_BRANCH = HOME_BRANCH_MAPPING.get('UD', '')
DEFAULT_PHOTO_URL = PHOTO_URL_MAPPING.get('UD', '')
APP_CSS = """
<style>
:root {
  --radius: 14px;
  --shadow: 0 14px 28px rgba(28, 32, 36, 0.18);
  --display-font: "Iowan Old Style", "Palatino", "Baskerville", "Times New Roman", serif;
}

.stApp {
  background: var(--background-color);
  color: var(--text-color);
}

.block-container {
  max-width: 1100px;
  padding: 2.25rem 2.5rem 4rem;
}

.app-header {
  background: var(--secondary-background-color);
  border-radius: var(--radius);
  padding: 1.6rem 1.8rem;
  border: 1px solid rgba(0, 0, 0, 0.12);
  border: 1px solid color-mix(in srgb, var(--text-color) 12%, transparent);
  box-shadow: var(--shadow);
}

.app-header h1 {
  font-family: var(--display-font);
  font-weight: 700;
  margin: 0.35rem 0 0.4rem;
  font-size: 2.15rem;
  color: var(--text-color);
}

.app-header p {
  margin: 0;
  color: var(--text-color);
  opacity: 0.7;
  font-size: 1rem;
}

.eyebrow {
  display: inline-block;
  padding: 0.3rem 0.8rem;
  border-radius: 999px;
  border: 1px solid var(--primary-color);
  background: color-mix(in srgb, var(--primary-color) 14%, transparent);
  color: var(--primary-color);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.7rem;
}

.section-title {
  margin: 1.6rem 0 0.7rem 0;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--primary-color);
  text-transform: uppercase;
  letter-spacing: 1.1px;
}

.file-chip {
  display: inline-flex;
  gap: 0.5rem;
  align-items: center;
  padding: 0.4rem 0.85rem;
  border-radius: 999px;
  border: 1px solid var(--primary-color);
  color: var(--primary-color);
  font-weight: 600;
  font-size: 0.85rem;
}

div.stDownloadButton > button,
div.stButton > button {
  border-radius: 999px;
  padding: 0.6rem 1.5rem;
  font-weight: 600;
}

div[data-testid="stMetric"] {
  background: var(--secondary-background-color);
  border-radius: var(--radius);
  padding: 0.9rem 1.1rem;
  border: 1px solid rgba(0, 0, 0, 0.12);
  border: 1px solid color-mix(in srgb, var(--text-color) 12%, transparent);
}

div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
  color: var(--text-color);
  opacity: 0.7;
}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {
  color: var(--text-color);
}

div[data-testid="stDataFrame"] {
  background: var(--secondary-background-color);
  border-radius: var(--radius);
  padding: 0.4rem;
  border: 1px solid rgba(0, 0, 0, 0.12);
  border: 1px solid color-mix(in srgb, var(--text-color) 12%, transparent);
}

div[data-testid="stAlert"] {
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.12);
  border: 1px solid color-mix(in srgb, var(--text-color) 12%, transparent);
}
</style>
"""

# ---------------- Data Transformation ---------------- #

@st.cache_data(show_spinner=False)
def apply_filters(raw_data: pd.DataFrame, allowed_institutions: Tuple[str, ...]) -> pd.DataFrame:
    missing = [c for c in FILTER_COLUMNS if c not in raw_data.columns]
    if missing:
        st.error(f"Missing filter columns: {', '.join(missing)}")
        st.stop()

    df = raw_data.copy()
    for col in FILTER_COLUMNS:
        df[col] = df[col].fillna('').astype(str).str.strip()

    mask = (
        df['Person Status Id'].isin(ALLOWED_PERSON_STATUS)
        & df['Student Home Institution Name'].isin(allowed_institutions)
        & df['Course Status Id'].isin(ALLOWED_COURSE_STATUS)
        & df['Enrolment Status Id'].isin(ALLOWED_ENROLMENT_STATUS)
    )
    return df[mask].copy()

@st.cache_data(show_spinner=False)
def transform_student_data(raw_data: pd.DataFrame, expiration_date: str) -> pd.DataFrame:
    # -- Pre-cleaning --
    df = raw_data.fillna('').astype(str)
    df = df.apply(lambda col: col.str.strip())

    # -- Validate columns --
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        st.error(f"Missing columns: {', '.join(missing)}")
        st.stop()

    # -- Email sanity check --
    email_series = df['Email']
    invalid_emails = email_series[
        ~email_series.str.match(EMAIL_REGEX, na=False) & email_series.ne('')
    ]
    bad_emails = sorted(invalid_emails.unique())
    if bad_emails:
        preview = ", ".join(bad_emails[:5])
        suffix = "…" if len(bad_emails) > 5 else ""
        st.warning(f"Invalid email formats spotted: {preview}{suffix}")

    # -- Branch mapping check --
    abbrs = df['Student Home Institution Abbrev'].unique()
    unmapped = sorted({abbr for abbr in abbrs if abbr and abbr not in HOME_BRANCH_MAPPING})
    if unmapped:
        st.warning(f"Unmapped branches: {', '.join(unmapped)}; using default.")

    # -- Build transformed --
    T = pd.DataFrame({
        'prefix': "",
        'givenName': df['First Name'],
        'middleName': df['Middle Name'],
        'familyName': df['Last Name'],
        'suffix': "",
        'nickname': df['Nickname'],
        'canSelfEdit': False,
        'dateOfBirth': "",
        'gender': "",
        'institutionId': "134059",
        'barcode': df['Student Number'],
        'idAtSource': df['Email'],
        'sourceSystem': "https://idp.divinity.edu.au/realms/divinity",
        'borrowerCategory': df['Course Type']
            .str.upper()
            .eq('RESEARCH')
            .map({True: 'HDR Student', False: 'Student'}),
        'circRegistrationDate': "",
        'oclcExpirationDate': expiration_date,
        'homeBranch': df['Student Home Institution Abbrev']
                       .map(HOME_BRANCH_MAPPING)
                       .fillna(DEFAULT_HOME_BRANCH),
        'primaryStreetAddressLine1': df['Address1'],
        'primaryStreetAddressLine2': df['Address2'],
        'primaryCityOrLocality': df['City'],
        'primaryStateOrProvince': df['State'],
        'primaryPostalCode': df['Postal Code'],
        'primaryCountry': df['Country'],
        'primaryPhone': df['Home Phone'],
        'secondaryStreetAddressLine1': "",
        'secondaryStreetAddressLine2': "",
        'secondaryCityOrLocality': "",
        'secondaryStateOrProvince': "",
        'secondaryPostalCode': "",
        'secondaryCountry': "",
        'secondaryPhone': df['Work Phone'],
        'emailAddress': df['Email'],
        'mobilePhone': df['Mobile Phone'],
        'notificationEmail': "",
        'notificationTextPhone': "",
        'patronNotes': df['Student Home Institution Name'],
        'photoURL': df['Student Home Institution Abbrev']
                   .map(PHOTO_URL_MAPPING)
                   .fillna(DEFAULT_PHOTO_URL),
        'customdata1': df['Course Level'],
        'customdata2': df['Course Name'],
        'customdata3': df['Course Type'],
        'customdata4': "",
        'username': df['Email'],
        'illId': "",
        'illApprovalStatus': "",
        'illPatronType': "",
        'illPickupLocation': ""
    })

    # -- Guarantee all fields and order --
    for f in FIELD_ORDER:
        if f not in T.columns:
            T[f] = ""
    return T[FIELD_ORDER]

# ---------------- Main App ---------------- #

def main():
    st.set_page_config(page_title="Student Enrollment Transformer", layout="wide")
    st.markdown(APP_CSS, unsafe_allow_html=True)
    st.markdown(
        """
        <div class="app-header">
          <div class="eyebrow">Student Enrollment</div>
          <h1>Student Enrollment Data Transformer</h1>
          <p>Upload a CSV and export a clean, tab-delimited file in seconds.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # -- Sidebar --
    with st.sidebar:
        st.header("Upload and Settings")
        uploaded = st.file_uploader("Choose CSV file", type="csv")
        exp_date = st.date_input(
            "Expiration Date",
            value=DEFAULT_EXPIRATION_DATE
        ).strftime(EXPIRATION_DATE_FORMAT)
        st.caption("Output format: tab-delimited TXT encoded as ISO-8859-1.")

    if not uploaded:
        st.info("Waiting on that CSV...")
        return

    try:
        raw = pd.read_csv(uploaded, dtype=str)
        st.success("CSV loaded.")
    except Exception as e:
        st.error(f"Couldn’t read CSV: {e}")
        return

    st.markdown("<div class='section-title'>Filters</div>", unsafe_allow_html=True)
    st.markdown(
        """
        - Person Status Id = `PERSON_ACTIVE`
        - Course Status Id = `PROGRAM_ACTIVE`
        - Enrolment Status Id = `ENROLMENT_ENROLLED`
        """,
        unsafe_allow_html=True
    )
    with st.expander("Allowed institutions (primary file)"):
        st.markdown(
            "\n".join(f"- {name}" for name in sorted(ALLOWED_INSTITUTIONS_PRIMARY))
        )
    with st.expander("Allowed institutions (secondary file)"):
        st.markdown(
            "\n".join(f"- {name}" for name in sorted(ALLOWED_INSTITUTIONS_SECONDARY))
        )

    with st.spinner("Applying filters…"):
        filtered_primary = apply_filters(raw, ALLOWED_INSTITUTIONS_PRIMARY)
        filtered_secondary = apply_filters(raw, ALLOWED_INSTITUTIONS_SECONDARY)
    st.success(
        "Filters applied: "
        f"{len(filtered_primary):,} primary rows, "
        f"{len(filtered_secondary):,} secondary rows."
    )

    dl_cols = st.columns(2, gap="large")
    with dl_cols[0]:
        st.download_button(
            "Download primary filtered CSV",
            data=filtered_primary.to_csv(index=False),
            file_name="filtered_report_primary.csv",
            mime="text/csv"
        )
    with dl_cols[1]:
        st.download_button(
            "Download secondary filtered CSV",
            data=filtered_secondary.to_csv(index=False),
            file_name="filtered_report_secondary.csv",
            mime="text/csv"
        )

    with st.spinner("Transforming…"):
        out_primary = transform_student_data(filtered_primary, exp_date)
        out_secondary = transform_student_data(filtered_secondary, exp_date)
        out_secondary['institutionId'] = '51546'
        out_secondary['borrowerCategory'] = 'Home Colleges'
        out_secondary['homeBranch'] = '266145'
    st.success("Transformation complete.")
    st.markdown(
        f"<div class='file-chip'>Loaded: {uploaded.name}</div>",
        unsafe_allow_html=True
    )

    stat_cols = st.columns(4, gap="large")
    stat_cols[0].metric("Raw rows", f"{len(raw):,}")
    stat_cols[1].metric("Primary rows", f"{len(filtered_primary):,}")
    stat_cols[2].metric("Secondary rows", f"{len(filtered_secondary):,}")
    stat_cols[3].metric("Expiration", exp_date.split("T")[0])

    st.markdown("<div class='section-title'>Export</div>", unsafe_allow_html=True)

    # -- Force strings on key dates --
    for d in ['dateOfBirth', 'oclcExpirationDate']:
        if d in out_primary:
            out_primary[d] = out_primary[d].astype(str)
        if d in out_secondary:
            out_secondary[d] = out_secondary[d].astype(str)

    # -- Download button --
    txt_primary = out_primary.to_csv(index=False, sep='\t', quoting=csv.QUOTE_NONE, escapechar='\\')
    txt_secondary = out_secondary.to_csv(index=False, sep='\t', quoting=csv.QUOTE_NONE, escapechar='\\')
    txt_cols = st.columns(2, gap="large")
    with txt_cols[0]:
        st.download_button(
            "Download primary TXT",
            data=txt_primary.encode('latin-1', errors='replace'),
            file_name="transformed_data_primary.txt",
            mime="text/plain; charset=ISO-8859-1"
        )
    with txt_cols[1]:
        st.download_button(
            "Download secondary TXT",
            data=txt_secondary.encode('latin-1', errors='replace'),
            file_name="transformed_data_secondary.txt",
            mime="text/plain; charset=ISO-8859-1"
        )

    st.markdown("<div class='section-title'>Preview</div>", unsafe_allow_html=True)
    preview_tab, full_tab, filtered_tab, txt_tab = st.tabs(
        ["Preview", "Full transformed", "Filtered data", "TXT preview"]
    )
    with preview_tab:
        left, right = st.columns(2, gap="large")
        with left:
            st.subheader("Primary filtered")
            st.dataframe(filtered_primary.head())
        with right:
            st.subheader("Transformed")
            st.dataframe(out_primary.head())
    with full_tab:
        st.dataframe(out_primary)
    with filtered_tab:
        full_left, full_right = st.columns(2, gap="large")
        with full_left:
            st.subheader("Primary filtered")
            st.dataframe(filtered_primary)
        with full_right:
            st.subheader("Secondary filtered")
            st.dataframe(filtered_secondary)
    with txt_tab:
        txt_left, txt_right = st.columns(2, gap="large")
        with txt_left:
            st.subheader("Primary TXT")
            st.dataframe(out_primary)
        with txt_right:
            st.subheader("Secondary TXT")
            st.dataframe(out_secondary)

if __name__ == "__main__":
    main()

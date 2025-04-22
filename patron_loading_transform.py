import streamlit as st
import pandas as pd
import csv
import re
from typing import List

# ---------------- Constants ---------------- #

REQUIRED_COLUMNS: List[str] = [
    'First Name', 'Middle Name', 'Last Name', 'Nickname', 'Student Number',
    'Email', 'Course Type', 'Student Home Institution Abbrev',
    'Address1', 'Address2', 'City', 'State', 'Postal Code', 'Country',
    'Home Phone', 'Work Phone', 'Mobile Phone', 'Course Level', 'Course Name',
    'Student Home Institution Name'
]

HOME_BRANCH_MAPPING = {
    'ALC': '267183', 'CTC': '266990', 'SAC': '266992', 'YTU': '266993',
    'UCLT': '270309', 'UD': '267183', 'WHT': '271609', 'WTC': '94194',
    'SBC': '148870', 'TRI': '267183', 'EBC': '267183', 'SFC': '267183',
    'SGR': '267183'
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
    'SGR': 'https://mannix.org.au/images/UD.png'
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

# ---------------- Data Transformation ---------------- #

@st.cache_data(show_spinner=False)
def transform_student_data(raw_data: pd.DataFrame, expiration_date: str) -> pd.DataFrame:
    # -- Pre-cleaning --
    df = raw_data.fillna('').astype(str).applymap(lambda x: x.strip())

    # -- Validate columns --
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        st.error(f"Missing columns: {', '.join(missing)}")
        st.stop()

    # -- Email sanity check --
    bad_emails = df.loc[~df['Email'].apply(lambda e: bool(EMAIL_REGEX.match(e))), 'Email'].unique()
    if len([e for e in bad_emails if e]) > 0:
        st.warning(f"Invalid email formats spotted: {', '.join(bad_emails[:5])}…")

    # -- Branch mapping check --
    abbrs = df['Student Home Institution Abbrev'].unique()
    unmapped = set(abbrs) - HOME_BRANCH_MAPPING.keys()
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
        'borrowerCategory': df['Course Type'].apply(
            lambda x: 'HDR Student' if x.upper()=='RESEARCH' else 'Student'
        ),
        'circRegistrationDate': "",
        'oclcExpirationDate': expiration_date,
        'homeBranch': df['Student Home Institution Abbrev']
                       .map(HOME_BRANCH_MAPPING)
                       .fillna(HOME_BRANCH_MAPPING.get('UD')),
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
                   .fillna(PHOTO_URL_MAPPING.get('UD')),
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
    st.set_page_config(page_title="🎓 Student Enrollment Transformer", layout="wide")
    st.title("🎓 Student Enrollment Data Transformer")
    st.markdown("Upload a CSV, dance in the rain, and get tab‑delimited magic.")

    # -- Sidebar --
    with st.sidebar:
        st.header("Upload & Settings")
        uploaded = st.file_uploader("Choose CSV", type="csv")
        exp_date = st.date_input(
            "Expiration Date",
            value=pd.to_datetime("2025-12-31")
        ).strftime("%Y-%m-%dT00:00:00")

    if not uploaded:
        st.info("Waiting on that CSV…")
        return

    try:
        raw = pd.read_csv(uploaded, dtype=str)
        st.success("CSV loaded!")
    except Exception as e:
        st.error(f"Couldn’t read CSV: {e}")
        return

    with st.spinner("Transforming…"):
        out = transform_student_data(raw, exp_date)
    st.success("Done. Feast your eyes below!")

    # -- Previews --
    with st.expander("🔍 Raw Preview"):
        st.dataframe(raw.head())
    with st.expander("✅ Transformed Preview"):
        st.dataframe(out.head())

    # -- Force strings on key dates --
    for d in ['dateOfBirth','oclcExpirationDate']:
        if d in out:
            out[d] = out[d].astype(str)

    # -- Download button --
    txt = out.to_csv(index=False, sep='\t', quoting=csv.QUOTE_NONE, escapechar='\\')
    btn = st.download_button(
        "⬇️ Download TXT",
        data=txt.encode('latin-1', errors='replace'),
        file_name="transformed_data.txt",
        mime="text/plain; charset=ISO-8859-1"
    )

    # -- Full data if you dare --
    with st.expander("🗂️ Full Transformed"):
        st.dataframe(out)

if __name__ == "__main__":
    main()

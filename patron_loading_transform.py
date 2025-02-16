import streamlit as st
import pandas as pd
import csv
from io import StringIO
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

# Defines the final output order (46 fields)
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

# ---------------- Data Transformation ---------------- #

def transform_data_with_patron_notes(raw_data: pd.DataFrame) -> pd.DataFrame:
    """
    Transform the raw CSV data into the desired tab-delimited format.
    
    Parameters:
        raw_data (pd.DataFrame): Data loaded from the uploaded CSV file.
        
    Returns:
        pd.DataFrame: Transformed DataFrame with columns in the required order.
    """
    # Validate required columns
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in raw_data.columns]
    if missing_columns:
        st.error(f"Missing required columns: {', '.join(missing_columns)}")
        st.stop()

    transformed = pd.DataFrame()

    # Basic personal info and identifiers
    transformed['prefix'] = ""
    transformed['givenName'] = raw_data['First Name'].fillna("")
    transformed['middleName'] = raw_data['Middle Name'].fillna("")
    transformed['familyName'] = raw_data['Last Name'].fillna("")
    transformed['suffix'] = ""
    transformed['nickname'] = raw_data['Nickname'].fillna("")
    transformed['canSelfEdit'] = False
    transformed['dateOfBirth'] = ""
    transformed['gender'] = ""
    transformed['institutionId'] = "134059"
    transformed['barcode'] = raw_data['Student Number'].fillna("")
    transformed['idAtSource'] = raw_data['Email'].fillna("")
    transformed['sourceSystem'] = "https://idp.divinity.edu.au/realms/divinity"

    # Borrower Category mapping based on Course Type
    transformed['borrowerCategory'] = raw_data['Course Type'].apply(
        lambda x: 'HDR Student' if isinstance(x, str) and x.strip().upper() == 'RESEARCH' else 'Student'
    )
    transformed['circRegistrationDate'] = ""
    transformed['oclcExpirationDate'] = "2025-12-31T00:00:00"

    # Map home branch using the institution abbreviation
    transformed['homeBranch'] = raw_data['Student Home Institution Abbrev'].map(HOME_BRANCH_MAPPING).fillna("267183")

    # Address information
    transformed['primaryStreetAddressLine1'] = raw_data['Address1'].fillna("")
    transformed['primaryStreetAddressLine2'] = raw_data['Address2'].fillna("")
    transformed['primaryCityOrLocality'] = raw_data['City'].fillna("")
    transformed['primaryStateOrProvince'] = raw_data['State'].fillna("")
    transformed['primaryPostalCode'] = raw_data['Postal Code'].fillna("")
    transformed['primaryCountry'] = raw_data['Country'].fillna("")
    transformed['primaryPhone'] = raw_data['Home Phone'].fillna("")
    transformed['secondaryStreetAddressLine1'] = ""
    transformed['secondaryStreetAddressLine2'] = ""
    transformed['secondaryCityOrLocality'] = ""
    transformed['secondaryStateOrProvince'] = ""
    transformed['secondaryPostalCode'] = ""
    transformed['secondaryCountry'] = ""
    transformed['secondaryPhone'] = raw_data['Work Phone'].fillna("")

    # Contact details
    transformed['emailAddress'] = raw_data['Email'].fillna("")
    transformed['mobilePhone'] = raw_data['Mobile Phone'].fillna("")
    transformed['notificationEmail'] = ""
    transformed['notificationTextPhone'] = ""

    # Additional fields: Patron notes, photo, and custom data
    transformed['patronNotes'] = raw_data['Student Home Institution Name'].fillna("")
    transformed['photoURL'] = raw_data['Student Home Institution Abbrev'].map(PHOTO_URL_MAPPING).fillna(
        "https://mannix.org.au/images/UD.png"
    )
    transformed['customdata1'] = raw_data['Course Level'].fillna("")
    transformed['customdata2'] = raw_data['Course Name'].fillna("")
    transformed['customdata3'] = raw_data['Course Type'].fillna("")
    transformed['customdata4'] = ""
    transformed['username'] = raw_data['Email'].fillna("")
    transformed['illId'] = ""
    transformed['illApprovalStatus'] = ""
    transformed['illPatronType'] = ""
    transformed['illPickupLocation'] = ""

    # Ensure all fields exist, even if empty
    for field in FIELD_ORDER:
        if field not in transformed.columns:
            transformed[field] = ""

    # Reorder columns according to FIELD_ORDER
    return transformed[FIELD_ORDER]

# ---------------- Main App Function ---------------- #

def main() -> None:
    st.set_page_config(
        page_title="Student Enrollment Data Transformer",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🎓 Student Enrollment Data Transformer")
    st.markdown(
        """
        Upload your student enrollment CSV file below, and the app will transform it into a tab-delimited format 
        that meets the required specification.
        """
    )

    # Sidebar file upload section
    with st.sidebar:
        st.header("Upload Data")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

        if uploaded_file is not None:
            try:
                raw_data = pd.read_csv(uploaded_file)
                st.success("File uploaded successfully!")
            except Exception as e:
                st.error(f"Error reading CSV file: {e}")
                st.stop()
        else:
            st.info("Awaiting CSV file to be uploaded.")
            return

    # Data transformation process
    with st.spinner("Transforming data..."):
        transformed_data = transform_data_with_patron_notes(raw_data)
    st.success("Data transformation complete!")

    # Data previews for user inspection
    with st.expander("📄 Raw Data Preview"):
        st.dataframe(raw_data.head())

    with st.expander("✅ Transformed Data Preview"):
        st.dataframe(transformed_data.head())

    # Ensure date fields are treated as strings
    for field in ['dateOfBirth', 'oclcExpirationDate']:
        if field in transformed_data.columns:
            transformed_data[field] = transformed_data[field].astype(str)

    # Generate a tab-delimited string from the transformed data
    txt_data = transformed_data.to_csv(
        index=False,
        sep='\t',
        quoting=csv.QUOTE_NONE,  # No quotes around fields
        escapechar='\\'          # Escape special characters if necessary
    )

    # Encode the string to Latin-1 (ISO-8859-1)
    txt_bytes = txt_data.encode('latin-1', errors='replace')

    # Download button for the transformed TXT file
    st.download_button(
        label="⬇️ Download Transformed Data (TXT)",
        data=txt_bytes,
        file_name="transformed_data.txt",
        mime="text/plain; charset=ISO-8859-1"
    )

    # Optionally show the entire transformed dataset
    with st.expander("🔍 View Entire Transformed Data"):
        st.dataframe(transformed_data)

if __name__ == "__main__":
    main()

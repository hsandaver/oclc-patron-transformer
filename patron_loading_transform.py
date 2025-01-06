import streamlit as st
import pandas as pd
from io import StringIO

def transform_data_with_patron_notes(raw_data):
    transformed = pd.DataFrame()

    # Define required columns
    required_columns = [
        'First Name', 'Middle Name', 'Last Name', 'Nickname', 'Student Number',
        'Email', 'Course Type', 'Student Home Institution Abbrev',
        'Address1', 'Address2', 'City', 'State', 'Postal Code', 'Country',
        'Home Phone', 'Work Phone', 'Mobile Phone', 'Course Level', 'Course Name',
        'Student Home Institution Name'
    ]

    # Check for missing columns
    missing_columns = [col for col in required_columns if col not in raw_data.columns]
    if missing_columns:
        st.error(f"The following required columns are missing in the uploaded CSV: {', '.join(missing_columns)}")
        st.stop()

    # Static fields
    transformed['prefix'] = ''
    transformed['givenName'] = raw_data['First Name'].fillna('')
    transformed['middleName'] = raw_data['Middle Name'].fillna('')
    transformed['familyName'] = raw_data['Last Name'].fillna('')
    transformed['suffix'] = ''
    transformed['nickname'] = raw_data['Nickname'].fillna('')
    transformed['canSelfEdit'] = False
    transformed['dateOfBirth'] = ''
    transformed['gender'] = ''
    transformed['institutionId'] = '134059'
    transformed['barcode'] = raw_data['Student Number'].fillna('')
    transformed['idAtSource'] = raw_data['Email'].fillna('')
    transformed['sourceSystem'] = 'https://idp.divinity.edu.au/realms/divinity'
    
    # Borrower Category Mapping
    transformed['borrowerCategory'] = raw_data['Course Type'].apply(
        lambda x: 'HDR Student' if isinstance(x, str) and x.strip().upper() == 'RESEARCH' else 'Student'
    )

    transformed['circRegistrationDate'] = ''
    transformed['oclcExpirationDate'] = '2025-12-31T00:00:00'  # Ensuring it's a string

    # Home Branch Mapping
    home_branch_mapping = {
        'ALC': '267183', 'CTC': '266990', 'SAC': '266992', 'YTU': '266993',
        'UCLT': '270309', 'UD': '267183', 'WHT': '271609', 'WTC': '94194',
        'SBC': '148870', 'TRI': '267183', 'EBC': '267183', 'SFC': '267183',
        'SGR': '267183'
    }
    transformed['homeBranch'] = raw_data['Student Home Institution Abbrev'].map(home_branch_mapping).fillna('267183')

    # Address fields
    transformed['primaryStreetAddressLine1'] = raw_data['Address1'].fillna('')
    transformed['primaryStreetAddressLine2'] = raw_data['Address2'].fillna('')
    transformed['primaryCityOrLocality'] = raw_data['City'].fillna('')
    transformed['primaryStateOrProvince'] = raw_data['State'].fillna('')
    transformed['primaryPostalCode'] = raw_data['Postal Code'].fillna('')
    transformed['primaryCountry'] = raw_data['Country'].fillna('')
    transformed['primaryPhone'] = raw_data['Home Phone'].fillna('')
    transformed['secondaryStreetAddressLine1'] = ''
    transformed['secondaryStreetAddressLine2'] = ''
    transformed['secondaryCityOrLocality'] = ''
    transformed['secondaryStateOrProvince'] = ''
    transformed['secondaryPostalCode'] = ''
    transformed['secondaryCountry'] = ''
    transformed['secondaryPhone'] = raw_data['Work Phone'].fillna('')

    # Contact fields
    transformed['emailAddress'] = raw_data['Email'].fillna('')
    transformed['mobilePhone'] = raw_data['Mobile Phone'].fillna('')
    transformed['notificationEmail'] = ''
    transformed['notificationTextPhone'] = ''

    # Other fields
    transformed['patronNotes'] = raw_data['Student Home Institution Name'].fillna('')

    # Photo URL Mapping
    photo_url_mapping = {
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
    transformed['photoURL'] = raw_data['Student Home Institution Abbrev'].map(photo_url_mapping).fillna(
        'https://mannix.org.au/images/UD.png'
    )

    # Custom fields
    transformed['customdata1'] = raw_data['Course Level'].fillna('')
    transformed['customdata2'] = raw_data['Course Name'].fillna('')
    transformed['customdata3'] = raw_data['Course Type'].fillna('')
    transformed['customdata4'] = ''
    transformed['username'] = raw_data['Email'].fillna('')
    transformed['illId'] = ''
    transformed['illApprovalStatus'] = ''
    transformed['illPatronType'] = ''
    transformed['illPickupLocation'] = ''

    # Reordering the fields
    field_order = [
        "prefix", "givenName", "middleName", "familyName", "suffix", "nickname", "canSelfEdit", "dateOfBirth", "gender",
        "institutionId", "barcode", "idAtSource", "sourceSystem", "borrowerCategory", "circRegistrationDate", "oclcExpirationDate", "homeBranch",
        "primaryStreetAddressLine1", "primaryStreetAddressLine2", "primaryCityOrLocality", "primaryStateOrProvince", "primaryPostalCode",
        "primaryCountry", "primaryPhone", "secondaryStreetAddressLine1", "secondaryStreetAddressLine2", "secondaryCityOrLocality",
        "secondaryStateOrProvince", "secondaryPostalCode", "secondaryCountry", "secondaryPhone", "emailAddress", "mobilePhone",
        "notificationEmail", "notificationTextPhone", "patronNotes", "photoURL", "customdata1", "customdata2", "customdata3",
        "customdata4", "username", "illId", "illApprovalStatus", "illPatronType", "illPickupLocation"
    ]

    # Ensure all fields in the order are present
    for field in field_order:
        if field not in transformed.columns:
            transformed[field] = ""  # Add blank column for unspecified fields

    return transformed[field_order]

def main():
    st.set_page_config(
        page_title="Student Enrollment Data Transformer",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🎓 Student Enrollment Data Transformer")
    st.markdown("""
    Upload your student enrollment CSV file, and we'll transform it into the required format.
    """)

    # Sidebar for file upload
    with st.sidebar:
        st.header("Upload Data")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file is not None:
            try:
                raw_data = pd.read_csv(uploaded_file)
                st.success("File uploaded successfully!")
            except Exception as e:
                st.error(f"Error reading the CSV file: {e}")
                st.stop()
        else:
            st.info("Awaiting CSV file to be uploaded.")

    if uploaded_file is not None:
        with st.spinner("Transforming data..."):
            transformed_data = transform_data_with_patron_notes(raw_data)
        st.success("Data transformation complete!")

        # Display raw data
        with st.expander("📄 Raw Data Preview"):
            st.dataframe(raw_data.head())

        # Display transformed data
        with st.expander("✅ Transformed Data Preview"):
            st.dataframe(transformed_data.head())

        # Ensure date fields are strings (if any additional date fields are present)
        date_fields = ['dateOfBirth', 'oclcExpirationDate']  # Add more if necessary
        for field in date_fields:
            if field in transformed_data.columns:
                transformed_data[field] = transformed_data[field].astype(str)

        # Provide download link as tab-delimited TXT
        txt = transformed_data.to_csv(index=False, sep='\t', quoting=1, encoding='utf-8')
        st.download_button(
            label="⬇️ Download Transformed Data (TXT)",
            data=txt,
            file_name="transformed_data.txt",
            mime="text/plain"
        )

        # Optional: Display entire transformed data
        with st.expander("🔍 View Entire Transformed Data"):
            st.dataframe(transformed_data)

if __name__ == "__main__":
    main()
import streamlit as st
import pandas as pd
from pathlib import Path
import re
import os
import sys

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

# Set page config
st.set_page_config(
    page_title="ParcelMyBox - Contact Importer",
    page_icon="📊",
    layout="wide"
)

def main():
    st.title("📊 Contact Importer")
    st.markdown("Upload a CSV or Excel file to import contacts into the system.")

    # File uploader
    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])

    if uploaded_file is not None:
        try:
            # Read the file
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            # Show a preview of the data
            st.subheader("Data Preview")
            st.dataframe(df.head())

            # Show column mapping UI
            st.subheader("Column Mapping")
            
            # Get unique column names from the uploaded file
            file_columns = df.columns.tolist()
            
            # Define required and optional fields
            required_fields = {
                'first_name': 'First Name',
                'last_name': 'Last Name',
                'email': 'Email',
                'phone_number': 'Phone Number',
                'country': 'Country'
            }
            
            optional_fields = {
                'company': 'Company',
                'address_line1': 'Address Line 1',
                'address_line2': 'Address Line 2',
                'city': 'City',
                'state': 'State',
                'postal_code': 'Postal Code',
                'notes': 'Notes'
            }

            # Create column mapping
            col_mapping = {}
            
            # Map required fields
            st.markdown("### Map Required Fields")
            for field, display_name in required_fields.items():
                col1, col2 = st.columns(2)
                with col1:
                    st.text_input(f"{display_name} Column", value=field, key=f"label_{field}", disabled=True)
                with col2:
                    selected_col = st.selectbox(
                        f"Select column for {display_name}",
                        [""] + file_columns,
                        key=f"select_{field}",
                        index=0
                    )
                    if selected_col:
                        col_mapping[field] = selected_col
            
            # Map optional fields
            st.markdown("### Map Optional Fields")
            for field, display_name in optional_fields.items():
                col1, col2 = st.columns(2)
                with col1:
                    st.text_input(f"{display_name} Column", value=field, key=f"label_opt_{field}", disabled=True)
                with col2:
                    selected_col = st.selectbox(
                        f"Select column for {display_name} (optional)",
                        [""] + file_columns,
                        key=f"select_opt_{field}",
                        index=0
                    )
                    if selected_col:
                        col_mapping[field] = selected_col

            # Import button
            if st.button("Import Contacts"):
                # Validate required fields
                missing_fields = [field for field in required_fields if field not in col_mapping]
                if missing_fields:
                    st.error(f"Please map all required fields: {', '.join(missing_fields)}")
                    return
                
                # Process the data
                try:
                    # Initialize counters
                    total = len(df)
                    success = 0
                    errors = []
                    
                    # Process each row
                    for idx, row in df.iterrows():
                        try:
                            # Extract data based on mapping
                            contact_data = {}
                            address_data = {}
                            
                            for field, col in col_mapping.items():
                                if col in row and pd.notna(row[col]):
                                    if field in ['first_name', 'last_name', 'email', 'phone_number', 'company', 'notes']:
                                        contact_data[field] = str(row[col])
                                    else:
                                        address_data[field] = str(row[col])
                            
                            # Here you would typically save to the database
                            # For now, we'll just count as success
                            success += 1
                            
                        except Exception as e:
                            errors.append(f"Row {idx + 2}: {str(e)}")
                    
                    # Show results
                    st.success(f"Successfully processed {success} of {total} records.")
                    
                    if errors:
                        st.warning(f"Encountered {len(errors)} errors:")
                        for error in errors:
                            st.error(error)
                    
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"An error occurred during import: {str(e)}")

        except Exception as e:
            st.error(f"Error reading file: {str(e)}")

if __name__ == "__main__":
    # Check if we can import Django settings
    try:
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pmb_hello.settings')
        django.setup()
    except ImportError:
        st.warning("Django not found. Running in standalone mode.")
    
    main()

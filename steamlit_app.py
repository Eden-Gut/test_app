import streamlit as st
import pandas as pd
from fuzzywuzzy import process

# פונקציה לזיהוי כפילויות
def fuzzy_duplicate_check(df, column, threshold):
    for idx, row in df.iterrows():
        matches = process.extract(row[column], df[column], limit=10)
        similar_entries = [match for match in matches if match[1] >= threshold and match[0] != row[column]]
        if similar_entries:
            yield idx, row[column], similar_entries

# העלאת קובץ CSV
uploaded_file = st.file_uploader("Upload your CSV file!!!!!!!", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Here is the raw data:")
    st.write(df)

    # בחירת עמודה לבדיקה
    column = st.selectbox("Select the column to check for duplicates:", df.columns)

    # בחירת סף דמיון
    threshold = st.slider("Select the similarity threshold (0-100):", 0, 100, 85)

    # הצגת כפילויות וממשק אינטראקטיבי לעריכה
    for idx, value, similar_entries in fuzzy_duplicate_check(df, column, threshold):
        st.write(f"Possible duplicates for {value} at index {idx}:")
        for record in similar_entries:
            similar_index = df[df[column] == record[0]].index[0]
            st.write(f"Similar to '{record[0]}' at index {similar_index} with {record[1]}% similarity.")
            
            # אפשרות לבחון את הרשומה ולערוך
            if st.button(f"Review row {similar_index}"):
                st.write(df.iloc[similar_index])  # מציג את השורה
                # אפשרות לשנות את השורה או למחוק
                edit_value = st.text_input("Edit value", value=df.iloc[similar_index][column])
                if st.button(f"Save changes to row {similar_index}"):
                    df.at[similar_index, column] = edit_value
                    st.success("Row updated successfully!")

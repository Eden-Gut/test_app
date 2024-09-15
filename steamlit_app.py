import streamlit as st
import pandas as pd
from fuzzywuzzy import process

# כותרת האפליקציה
st.title('Fuzzy Duplicate Finder')

# העלאת קובץ CSV
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Here is the raw data:")
    st.write(df)

    # בחירת עמודה לבדיקה
    column = st.selectbox("Select the column to check for duplicates:", df.columns)

    # בחירת סף דמיון
    threshold = st.slider("Select the similarity threshold (0-100):", 0, 100, 85)

    # פונקציה לזיהוי כפילויות לא מדויקות
    def fuzzy_duplicate_check(row, df, threshold):
        matches = process.extract(row[column], df[column], limit=10)
        similar_entries = [match for match in matches if match[1] >= threshold and match[0] != row[column]]
        return similar_entries

    # הצגת תוצאות
    st.write(f"Finding duplicates with similarity threshold of {threshold}%...")
    for idx, row in df.iterrows():
        similar_records = fuzzy_duplicate_check(row, df, threshold)
        if similar_records:
            st.write(f"Possible duplicates for {row[column]}: {similar_records}")

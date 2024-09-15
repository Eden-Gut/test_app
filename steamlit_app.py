import streamlit as st
import pandas as pd
import numpy as np
from fuzzywuzzy import process


# פונקציה לזיהוי כפילויות
def fuzzy_duplicate_check(df, column, threshold):
    for idx, row in df.iterrows():
        matches = process.extract(row[column], df[column], limit=10)
        similar_entries = [match for match in matches if match[1] >= threshold and match[0] != row[column]]
        if similar_entries:
            yield idx, row[column], similar_entries

# פונקציה לזיהוי אנומליות
def find_anomalies(df, column):
    threshold = 3  # ערכים עם Z-Score מעל 3 נחשבים חריגים
    z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
    anomalies = df[z_scores > threshold]
    return anomalies

# פונקציה לתיקון ערכים חסרים
def fix_missing_values(df):
    for column in df.columns:
        if df[column].isnull().sum() > 0:
            if df[column].dtype == np.number:
                df[column].fillna(df[column].mean(), inplace=True)
            else:
                df[column].fillna(df[column].mode()[0], inplace=True)
    return df

# פונקציה לנורמליזציה של מחרוזות
def normalize_strings(df, columns):
    for column in columns:
        df[column] = df[column].str.lower().str.strip()
    return df

# פונקציה לניקוי והמרת תאריכים
def clean_date_format(df, column):
    df[column] = pd.to_datetime(df[column], errors='coerce').dt.strftime('%Y-%m-%d')
    return df

# העלאת קובץ CSV
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    with st.expander("Data Preview")
       st.write(df)

    # סרגל כלים צדדי
    steps = ["Duplicate Detection", "Anomaly Detection", "Fix Missing Values", "Normalization", "Date Cleaning"]
    selected_step = st.sidebar.radio("Select a step", steps)

    # שלב 1: זיהוי כפילויות
    if selected_step == "Duplicate Detection":
        st.write("### Step 1: Detecting duplicates")
        column = st.selectbox("Select the column to check for duplicates:", df.columns)
        threshold = st.slider("Select the similarity threshold (0-100):", 0, 100, 85)

        for idx, value, similar_entries in fuzzy_duplicate_check(df, column, threshold):
            st.write(f"Possible duplicates for {value} at index {idx}:")
            for record in similar_entries:
                similar_index = df[df[column] == record[0]].index[0]
                st.write(f"Similar to '{record[0]}' at index {similar_index} with {record[1]}% similarity.")
                
                # אפשרות לבחון ולשנות נתונים
                if st.button(f"Review row {similar_index}", key=f"review_button_{similar_index}"):
                    st.write(df.iloc[similar_index])
                    edit_value = st.text_input("Edit value", value=df.iloc[similar_index][column])
                    if st.button(f"Save changes to row {similar_index}", key=f"save_button_{similar_index}"):
                        df.at[similar_index, column] = edit_value
                        st.success(f"Row {similar_index} updated successfully!")

    # שלב 2: זיהוי אנומליות
    elif selected_step == "Anomaly Detection":
        st.write("### Step 2: Detecting anomalies")
        column = st.selectbox("Select the column to check for anomalies:", df.select_dtypes(include=[np.number]).columns)

        anomalies = find_anomalies(df, column)
        if not anomalies.empty:
            st.write("Anomalies found:")
            st.write(anomalies)
        else:
            st.write("No anomalies detected.")

    # שלב 3: תיקון ערכים חסרים
    elif selected_step == "Fix Missing Values":
        st.write("### Step 3: Fixing missing values")
        df = fix_missing_values(df)
        st.write("Missing values have been fixed.")
        st.write(df)

    # שלב 4: נורמליזציה
    elif selected_step == "Normalization":
        st.write("### Step 4: Normalizing data")
        text_columns = st.multiselect("Select columns to normalize (text only):", df.select_dtypes(include=[object]).columns)

        if text_columns:
            df = normalize_strings(df, text_columns)
            st.write("Data normalized successfully.")
            st.write(df)

    # שלב 5: ניקוי והמרת פורמט תאריכים
    elif selected_step == "Date Cleaning":
        st.write("### Step 5: Cleaning and formatting dates")
        date_column = st.selectbox("Select the date column:", df.select_dtypes(include=[object]).columns)

        df = clean_date_format(df, date_column)
        st.write("Date formats cleaned and converted.")
        st.write(df)

    # הורדת הדאטה בסוף התהליך
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download cleaned data",
        data=csv,
        file_name='cleaned_data.csv',
        mime='text/csv',
    )

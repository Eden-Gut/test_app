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

# העלאת קובץ CSV
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Here is the raw data:")
    
    # הצגת הטבלה במלוא הרוחב
    st.dataframe(df, use_container_width=True)

    # סינון עמודות להצגה
    selected_columns = st.multiselect("Select columns to display", options=df.columns, default=df.columns)
    filtered_df = df[selected_columns]
    
    # הצגת טבלה מסוננת על פי העמודות שנבחרו
    st.dataframe(filtered_df, use_container_width=True)

    # סרגל כלים עם כפתורים בצד
    st.sidebar.title("Data Cleaning Steps")
    step = st.session_state.get("step", 1)  # הגדרת השלב הנוכחי בעזרת session_state

    # כפתורים עבור כל שלב, כאשר השלב הנוכחי מודגש
    if st.sidebar.button("Step 1: Duplicate Detection", key="step1", disabled=(step == 1)):
        step = 1
    if st.sidebar.button("Step 2: Anomaly Detection", key="step2", disabled=(step == 2)):
        step = 2
    if st.sidebar.button("Step 3: Fix Missing Values", key="step3", disabled=(step == 3)):
        step = 3
    if st.sidebar.button("Step 4: Normalization", key="step4", disabled=(step == 4)):
        step = 4
    if st.sidebar.button("Step 5: Date Cleaning", key="step5", disabled=(step == 5)):
        step = 5

    # עדכון של השלב הנוכחי בזיכרון
    st.session_state["step"] = step

    # טיפול לפי השלב הנבחר
    if step == 1:
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

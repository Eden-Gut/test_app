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
    
    # הצגת הטבלה עם אפשרות להרחיב ולהצמצם
    with st.expander("Data Preview", expanded=False):
        st.dataframe(df, use_container_width=True)

    # סרגל כלים בצד עם כותרות שניתן ללחוץ עליהן
    st.sidebar.title("Data Cleaning Steps")
    
    step = st.session_state.get("step", 1)

    # שלבי העבודה ככותרות עם הדגשת השלב הנוכחי
    def sidebar_step(label, step_number, current_step):
        if step_number == current_step:
            st.sidebar.markdown(f"*:red[{label}]*")  # השלב הנוכחי בצבע אדום
        else:
            if st.sidebar.button(label):
                st.session_state["step"] = step_number

    sidebar_step("Step 1: Duplicate Detection", 1, step)
    sidebar_step("Step 2: Anomaly Detection", 2, step)
    sidebar_step("Step 3: Fix Missing Values", 3, step)
    sidebar_step("Step 4: Normalization", 4, step)
    sidebar_step("Step 5: Date Cleaning", 5, step)

    # התוכן העיקרי לפי השלב הנבחר
    step = st.session_state.get("step", 1)
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

import streamlit as st
import pandas as pd
import numpy as np

# פונקציה לניתוח עמודה (מציג נתונים סטטיסטיים בסיסיים)
def analyze_column(df, column):
    col_data = df[column]
    st.write(f"### Analysis of '{column}'")
    
    # מציג כמה ערכים יוניקים, ערכים חסרים, סך הכל ערכים
    st.write(f"Unique values: {col_data.nunique()}")
    st.write(f"Missing values: {col_data.isna().sum()}")
    st.write(f"Total values: {col_data.size}")
    
    # אם העמודה היא מספרית
    if pd.api.types.is_numeric_dtype(col_data) and not col_data.astype(str).str.contains(r'\D').any():
        st.write(f"Sum: {col_data.sum()}")
        st.write(f"Mean: {col_data.mean()}")
        st.write(f"Median: {col_data.median()}")
        st.write(f"Standard deviation: {col_data.std()}")

# העלאת קובץ CSV
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # חלוקת המסך: שליש למסך הנתונים ושני שליש לניתוח
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # תצוגת הדאטה (Data Preview)
        st.write("### Data Preview")
        st.dataframe(df, use_container_width=True)
    
    with col2:
        # בחירת עמודה לניתוח
        column = st.selectbox("Select a column to analyze:", df.columns)
        
        # ניתוח העמודה הנבחרת
        analyze_column(df, column)
        
        # שינוי פורמט עמודה (דוגמה לשינוי בסיסי)
        st.write("### Change Column Format")
        format_options = ["None", "Currency", "Date"]
        format_choice = st.selectbox("Choose format:", format_options)
        
        if format_choice == "Currency":
            # המרה לפורמט מטבע (לדוגמה, עם פורמט דולרי)
            df[column] = df[column].apply(lambda x: f"${x:,.2f}" if pd.api.types.is_numeric_dtype(df[column]) else x)
            st.write(f"Column '{column}' formatted as Currency.")
        
        elif format_choice == "Date":
            # המרה לפורמט תאריך
            df[column] = pd.to_datetime(df[column], errors='coerce')
            st.write(f"Column '{column}' formatted as Date.")
        
        # הצגת הטבלה עם השינויים
        st.write("### Updated Data Preview")
        st.dataframe(df, use_container_width=True)

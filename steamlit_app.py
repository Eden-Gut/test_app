import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# פונקציה לניתוח עמודה (מציג נתונים סטטיסטיים בסיסיים עם גרפים)
def analyze_column(df, column):
    col_data = df[column]
    st.write(f"### Analysis of '{column}'")
    
    # מציג כמה ערכים יוניקים, ערכים חסרים, סך הכל ערכים
    st.write(f"Total values: {col_data.size}")
    st.write(f"Unique values: {col_data.nunique()}")
    st.write(f"Missing values: {col_data.isna().sum()}")
    
    # גרף עוגה להצגת ערכים יוניקים וערכים חסרים בגודל קטן
    labels = ['Unique Values', 'Missing Values', 'Total Values']
    sizes = [col_data.nunique(), col_data.isna().sum(), col_data.size - col_data.isna().sum() - col_data.nunique()]
    
    fig1, ax1 = plt.subplots(figsize=(2, 2))  # גודל העוגה מוקטן
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')  # שומר על העיגול
    st.pyplot(fig1)
    
    # אם העמודה היא מספרית
    if pd.api.types.is_numeric_dtype(col_data):
        st.write(f"Sum: {col_data.sum()}")
        st.write(f"Mean: {col_data.mean()}")
        st.write(f"Median: {col_data.median()}")
        st.write(f"Standard deviation: {col_data.std()}")
        
        # גרף היסטוגרמה להצגת הפיזור
        fig2, ax2 = plt.subplots()
        ax2.hist(col_data.dropna(), bins=20, color='blue', edgecolor='black')
        ax2.set_title(f'Histogram of {column}')
        ax2.set_xlabel('Value')
        ax2.set_ylabel('Frequency')
        st.pyplot(fig2)

# פונקציה לשינוי פורמט עמודות
def change_column_format(df, column):
    st.write("### Change Column Format")
    
    # אפשרויות לפורמט עמודה
    format_options = ["None", "Currency", "Date", "Uppercase", "Lowercase"]
    format_choice = st.selectbox("Choose format:", format_options)
    
    if format_choice == "Currency":
        df[column] = df[column].apply(lambda x: f"${x:,.2f}" if pd.api.types.is_numeric_dtype(df[column]) else x)
        st.write(f"Column '{column}' formatted as Currency.")
    
    elif format_choice == "Date":
        df[column] = pd.to_datetime(df[column], errors='coerce')
        st.write(f"Column '{column}' formatted as Date.")
    
    elif format_choice == "Uppercase" and pd.api.types.is_string_dtype(df[column]):
        df[column] = df[column].str.upper()
        st.write(f"Column '{column}' formatted as Uppercase.")
    
    elif format_choice == "Lowercase" and pd.api.types.is_string_dtype(df[column]):
        df[column] = df[column].str.lower()
        st.write(f"Column '{column}' formatted as Lowercase.")

# פונקציה לשמירת שינויים ולחזרה אחורה (Undo/Redo)
history = []  # רשימת היסטוריה לשינויים
undo_stack = []  # מחסנית לביצוע חזרה אחורה (Redo)

def save_changes(df):
    history.append(df.copy())
    st.write("Changes saved.")

def undo_changes():
    if history:
        undo_stack.append(history.pop())
        st.write("Undo performed.")

def redo_changes():
    if undo_stack:
        history.append(undo_stack.pop())
        st.write("Redo performed.")

# העלאת קובץ CSV
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    history.append(df.copy())  # שמירה של המצב המקורי
    
    # חלוקת המסך: שליש למסך הנתונים ושני שליש לניתוח
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # תצוגת הדאטה (Data Preview) שמתעדכנת עם שינויים
        st.write("### Data Preview")
        selected_column = st.dataframe(df, use_container_width=True)

        # כפתורי Undo ו-Redo
        st.button("Undo", on_click=undo_changes)
        st.button("Redo", on_click=redo_changes)
    
    with col2:
        # הצגת העמודות לבחירה מתוך הרשימה הדינמית
        st.write("### Click a Column for Analysis")
        
        # הצגת עמודות הדינמית מתוך Data Preview
        column = st.selectbox("Select a column to analyze:", df.columns)
        if column:
            analyze_column(df, column)
            change_column_format(df, column)

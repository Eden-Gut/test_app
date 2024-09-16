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
    
    # גרף עוגה להצגת ערכים יוניקים וערכים חסרים
    labels = ['Unique Values', 'Missing Values', 'Total Values']
    sizes = [col_data.nunique(), col_data.isna().sum(), col_data.size - col_data.isna().sum() - col_data.nunique()]
    
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')  # שומר על העיגול
    st.pyplot(fig1)
    
    # אם העמודה היא מספרית
    if pd.api.types.is_numeric_dtype(col_data) and not col_data.astype(str).str.contains(r'\D').any():
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
    
    # עדכון הטבלה בצד שמאל
    st.write("### Updated Data Preview")
    st.dataframe(df, use_container_width=True)

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
        st.dataframe(df, use_container_width=True)

        # כפתורי Undo ו-Redo
        st.button("Undo", on_click=undo_changes)
        st.button("Redo", on_click=redo_changes)
    
    with col2:
        st.write("### Select a Column by Clicking its Header in Data Preview")
        column = st.selectbox("Select a column to analyze:", df.columns, key="column_select")
        
        # ניתוח העמודה הנבחרת
        analyze_column(df, column)
        
        # שינוי פורמט עמודה
        change_column_format(df, column)

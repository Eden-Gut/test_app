import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# פונקציה להצגת סטטיסטיקות (Sum, Mean, Median, Std Dev) בכרטיסים
def display_statistics(df, column):
    col_data = df[column]
    
    # אם העמודה היא מספרית
    if pd.api.types.is_numeric_dtype(col_data):
        total_sum = col_data.sum()
        mean_val = col_data.mean()
        median_val = col_data.median()
        std_dev = col_data.std()
        
        # שימוש בסט Columns להצגת הכרטיסים
        col1, col2, col3, col4 = st.columns(4)

        # הצגת כרטיסים עם ערכים
        with col1:
            st.metric(label="Sum", value=f"{total_sum:,.2f}")
        with col2:
            st.metric(label="Mean", value=f"{mean_val:,.2f}")
        with col3:
            st.metric(label="Median", value=f"{median_val:,.2f}")
        with col4:
            st.metric(label="Std Dev", value=f"{std_dev:,.2f}")

# פונקציה לניתוח עמודה (מציג נתונים סטטיסטיים בסיסיים עם גרפים)
def analyze_column(df, column):
    col_data = df[column]
    st.write(f"### Analysis of '{column}'")
    
    # מציג כמה ערכים יוניקים, ערכים חסרים, סך הכל ערכים
    total_values = col_data.size
    unique_values = col_data[col_data.duplicated(keep=False) == False].nunique()
    distinct_values = col_data.nunique()
    missing_values = col_data.isna().sum()
    
    # חישוב אחוזים
    unique_percentage = (unique_values / total_values) * 100
    distinct_percentage = (distinct_values / total_values) * 100
    missing_percentage = (missing_values / total_values) * 100
    
    # גרף עמודות להצגת ערכים יוניקים, ערכים חסרים וערכים כוללים
    labels = ['Unique Values', 'Distinct Values', 'Missing Values']
    values = [unique_values, distinct_values, missing_values]
    percentages = [unique_percentage, distinct_percentage, missing_percentage]
    
    fig1 = px.bar(x=labels, y=values, title='Bar Chart of Column Analysis', labels={'x': 'Category', 'y': 'Count'})
    fig1.update_traces(text=[f'{v} ({p:.2f}%)' for v, p in zip(values, percentages)], textposition='outside')
    fig1.update_layout(hovermode="x unified")
    st.plotly_chart(fig1)
    
    # יצירת expanders להצגת רשימות הערכים
    with st.expander("Unique Values"):
        st.write(col_data[col_data.duplicated(keep=False) == False].dropna().tolist())
    
    with st.expander("Distinct Values"):
        st.write(col_data.dropna().unique().tolist())
    
    with st.expander("Missing Values"):
        st.write(col_data[col_data.isna()].index.tolist())
    
    # אם העמודה היא מספרית, הצגת סטטיסטיקות
    if pd.api.types.is_numeric_dtype(col_data):
        display_statistics(df, column)

        # גרף היסטוגרמה להצגת הפיזור
        fig2 = px.histogram(col_data.dropna(), nbins=20, title=f'Histogram of {column}')
        fig2.update_layout(xaxis_title='Value', yaxis_title='Frequency')
        st.plotly_chart(fig2)

# פונקציה לשינוי פורמט עמודות
def change_column_format(df, column):
    st.write("### Change Column Format")
    
    # אפשרויות לפורמט עמודה
    format_options = ["None", "Currency", "Text"]
    format_choice = st.selectbox("Choose format:", format_options)
    
    if format_choice == "Currency":
        df[column] = df[column].apply(lambda x: f"${x:,.2f}" if pd.api.types.is_numeric_dtype(df[column]) else x)
        st.write(f"Column '{column}' formatted as Currency.")
    
    elif format_choice == "Text":
        df[column] = df[column].astype(str)
        st.write(f"Column '{column}' formatted as Text.")

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

# הגדרת מצב תצוגה רחב
st.set_page_config(layout="wide")

# העלאת קובץ CSV
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    history.append(df.copy())  # שמירה של המצב המקורי
    
    # תצוגת הדאטה (Data Preview) מוצגת בראש הדף
    st.write("### Data Preview")
    selected_column = st.dataframe(df, use_container_width=True)

    # כפתורי Undo ו-Redo מתחת ל-Data Preview
    st.button("Undo", on_click=undo_changes)
    st.button("Redo", on_click=redo_changes)
    
    # הצגת העמודות לבחירה מתוך הרשימה הדינמית
    st.write("### Click a Column for Analysis")
    
    # הצגת עמודות הדינמית מתוך Data Preview
    column = st.selectbox("Select a column to analyze:", df.columns)
    if column:
        change_column_format(df, column)  # הפורמט ישפיע על הטבלה המוצגת
        # הצגת ניתוח רק אם העמודה היא לא טקסט
        if not pd.api.types.is_string_dtype(df[column]):
            analyze_column(df, column)

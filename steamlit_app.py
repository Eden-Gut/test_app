import streamlit as st
import pandas as pd
import plotly.express as px

# הגדרת מצב תצוגה רחב
st.set_page_config(layout="wide")

# עיצוב סטייל מותאם עבור מחיקת עמודות
st.markdown(
    """
    <style>
    .delete-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-bottom: 20px;
    }
    .delete-item {
        padding: 5px 10px;
        border: 1px solid #ff4b4b;
        border-radius: 5px;
        display: inline-flex;
        align-items: center;
        background-color: #ff4b4b;
        color: white;
    }
    .delete-item button {
        background-color: transparent;
        border: none;
        margin-left: 5px;
        cursor: pointer;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True
)

# שמירת הפורמטים שנבחרו לכל עמודה
if "column_formats" not in st.session_state:
    st.session_state["column_formats"] = {}

# פונקציה ליישום הפורמטים על העמודות
def apply_column_formats(df):
    for column, format_type in st.session_state["column_formats"].items():
        if format_type == "Currency" and pd.api.types.is_numeric_dtype(df[column]):
            df[column] = df[column].apply(lambda x: f"${x:,.2f}")
        elif format_type == "Date":
            df[column] = pd.to_datetime(df[column], errors='coerce').dt.strftime('%Y-%m-%d')
        elif format_type == "Numeric":
            df[column] = pd.to_numeric(df[column], errors='coerce')
        elif format_type == "Text":
            df[column] = df[column].astype(str)
    return df

# פונקציה לשינוי פורמט עמודות
def change_column_format(df, column):
    st.write("### Change Column Format")
    
    # בדיקה אם יש פורמט שנשמר כבר לעמודה
    current_format = st.session_state["column_formats"].get(column, "None")
    
    # אפשרויות לפורמט עמודה
    format_options = ["None", "Currency", "Date", "Numeric", "Text"]
    format_choice = st.selectbox("Choose format:", format_options, index=format_options.index(current_format))
    
    if format_choice == "Currency":
        if pd.api.types.is_numeric_dtype(df[column]):
            df[column] = df[column].apply(lambda x: f"${x:,.2f}")
            st.write(f"Column '{column}' formatted as Currency.")
        else:
            st.warning(f"Cannot convert column '{column}' to Currency. It is not numeric.")
    
    elif format_choice == "Date":
        try:
            df[column] = pd.to_datetime(df[column], errors='coerce').dt.strftime('%Y-%m-%d')
            st.write(f"Column '{column}' formatted as Date.")
        except Exception as e:
            st.warning(f"Cannot convert column '{column}' to Date. Error: {e}")
    
    elif format_choice == "Numeric":
        if pd.api.types.is_numeric_dtype(df[column]):
            df[column] = pd.to_numeric(df[column], errors='coerce')
            st.write(f"Column '{column}' formatted as Numeric.")
        else:
            st.warning(f"Cannot convert column '{column}' to Numeric. It is not numeric.")
    
    elif format_choice == "Text":
        df[column] = df[column].astype(str)
        st.write(f"Column '{column}' formatted as Text.")
    
    # כפתור לשמירת הפורמט הנבחר ולייצוא
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Save Format"):
            st.session_state["column_formats"][column] = format_choice
            st.success(f"Format for column '{column}' saved as {format_choice}.")
    
    with col2:
        if st.button("Export as CSV"):
            df_export = apply_column_formats(df.copy())
            csv = df_export.to_csv(index=False)
            st.download_button(label="Download CSV", data=csv, file_name="formatted_data.csv", mime="text/csv")

    st.dataframe(df, use_container_width=True)

# פונקציה למחיקת עמודות באמצעות בר אופקי עם כפתור "X"
def delete_columns(df):
    st.write("### Columns:")
    columns = df.columns.tolist()
    
    # שימוש בעיצוב מותאם למחיקה
    st.markdown('<div class="delete-bar">', unsafe_allow_html=True)
    
    for column in columns:
        st.markdown(f'''
        <div class="delete-item">
            {column}
            <button onclick="window.location.href += '&delete={column}'">X</button>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # בדיקה אם המשתמש לחץ על כפתור מחיקה
    delete_col = st.experimental_get_query_params().get("delete", None)
    if delete_col:
        df.drop(columns=delete_col, inplace=True)
        st.experimental_rerun()

# פונקציה להצגת השורות עם ערכים חסרים
def show_missing_data(df):
    st.write("### Handling Missing Values")
    
    missing_data = df[df.isnull().any(axis=1)]
    if not missing_data.empty:
        st.write("Rows with Missing Values:")
        st.dataframe(missing_data)
    
    column = st.selectbox("Select column to fill missing values:", df.columns[df.isnull().any()])
    
    if column:
        fill_option = st.selectbox("How would you like to fill the missing values?", ["Mean", "Median", "Mode", "Custom Value"])
        
        if fill_option == "Mean":
            df[column].fillna(df[column].mean(), inplace=True)
        elif fill_option == "Median":
            df[column].fillna(df[column].median(), inplace=True)
        elif fill_option == "Mode":
            df[column].fillna(df[column].mode()[0], inplace=True)
        elif fill_option == "Custom Value":
            custom_value = st.text_input("Enter custom value:")
            if custom_value:
                df[column].fillna(custom_value, inplace=True)
        
        st.write("### Data after handling missing values")
        st.dataframe(df)

# Expander להעלאת קובץ
with st.expander("Upload your CSV file", expanded=True):
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    with st.expander("Data Preview", expanded=True):
        df = apply_column_formats(df)  # יישום פורמטים שנשמרו
        st.dataframe(df, use_container_width=True)

    # מחיקת עמודות עם בר אופקי וכפתורי "X"
    delete_columns(df)

    column = st.selectbox("Select a column to analyze:", df.columns)
    if column:
        change_column_format(df, column)
        analyze_column(df, column)
    
    show_missing_data(df)

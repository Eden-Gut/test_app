import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# הגדרת מצב תצוגה רחב
st.set_page_config(layout="wide")

# עיצוב סטייל מותאם עבור הסטטיסטיקות וה-sidebar
st.markdown(
    """
    <style>
    div[data-testid="stMetric"] {
        background-color: #f5f5f5;
        border: 2px solid #000000;
        padding: 10px;
        border-radius: 10px;
        color: black;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px;
        font-weight: bold;
    }

    section[data-testid="stSidebar"] {
        background-color: #333333;
    }

    /* עיצוב הכותרות ב-sidebar */
    .sidebar-link {
        color: #f5f5f5 !important;
        font-weight: bold;
        text-decoration: none !important;
    }

    .sidebar-link:hover {
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True
)

# ודא שמפתח 'column_formats' קיים ב-session_state
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
    st.write("### Change Column Format", anchor="change-column-format")
    
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
    
    # הוספת כפתורים במבנה ברור יותר עם מרווח להודעה
    save_col, download_col = st.columns([1, 1])
    with save_col:
        if st.button("Save Format"):
            st.session_state["column_formats"][column] = format_choice
            st.success(f"Format for column '{column}' saved as {format_choice}.")
    with download_col:
        @st.cache_data
        def convert_df_to_excel(df):
            return df.to_excel(index=False)

        if st.button('Download Excel'):
            excel_data = convert_df_to_excel(df)
            st.download_button(
                label="Download Excel file",
                data=excel_data,
                file_name='filtered_data.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
    
    # בחירת עמודות לסינון
    selected_columns = st.multiselect(
        "Filter columns",
        options=df.columns,
        default=df.columns.tolist(),
        key="filter-columns"
    )

    filtered_df = df[selected_columns]
    st.dataframe(filtered_df, use_container_width=True)


# פונקציה להצגת ערכים חסרים כולל ריקים ""
def highlight_missing(val):
    if pd.isnull(val) or val == "":
        return 'background-color: red'
    return ''

def show_missing_data(df):
    st.write("### Handling Missing Values", anchor="handling-missing-values")
    
    # התייחסות לערכים חסרים וריקים ""
    missing_data = df[df.isnull().any(axis=1) | (df == "").any(axis=1)]
    
    if not missing_data.empty:
        st.write("Rows with Missing Values:")
        st.dataframe(missing_data.style.applymap(highlight_missing), use_container_width=True)
    
    column = st.selectbox("Select column to fill missing values:", df.columns[df.isnull().any() | (df == "").any()])

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
        st.dataframe(df, use_container_width=True)

# Expander להעלאת קובץ
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    with st.expander("Data Preview", expanded=True):
        st.write("### Data Preview")
        df = apply_column_formats(df)  # יישום פורמטים שנשמרו
        st.dataframe(df, use_container_width=True)

    column = st.selectbox("Select a column to analyze:", df.columns)
    if column:
        change_column_format(df, column)
        show_missing_data(df)

    # Sidebar עם קישורים יופיע רק אחרי העלאת קובץ
    with st.sidebar:
        st.markdown("<h2 style='color:white;'>Navigation</h2>", unsafe_allow_html=True)
        st.markdown("[Change Column Format](#change-column-format)", unsafe_allow_html=True)
        st.markdown("[Filter Columns](#filter-columns)", unsafe_allow_html=True)
        st.markdown("[Missing Values](#handling-missing-values)", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

else:
    st.sidebar.write("Upload a CSV file to enable navigation.")

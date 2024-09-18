import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# הגדרת מצב תצוגה רחב
st.set_page_config(layout="wide")

# עיצוב סטייל מותאם עבור הסטטיסטיקות
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
    
    button_container = st.container()

    with button_container:
        col1, col2 = st.columns([0.1, 0.9])  # הקטנתי את הרוחב כדי שהכפתורים יהיו צמודים
        with col1:
            # כפתור לשמירת הפורמט הנבחר
            if st.button("Save Format"):
                st.session_state["column_formats"][column] = format_choice
                st.success(f"Format for column '{column}' saved as {format_choice}.")
        with col2:
            # יצירת כפתור להורדת הקובץ
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
        default=df.columns.tolist()
    )

    filtered_df = df[selected_columns]
    st.dataframe(filtered_df, use_container_width=True)


# פונקציה להצגת סטטיסטיקות עבור עמודות מספריות
def display_statistics_numeric(df, column):
    col_data = df[column]
    total_sum = col_data.sum()
    mean_val = col_data.mean()
    median_val = col_data.median()
    std_dev = col_data.std()
    min_val = col_data.min()
    max_val = col_data.max()
    q25 = col_data.quantile(0.25)
    q75 = col_data.quantile(0.75)
    
    # חלוקה לשלוש עמודות: שתיים לסטטיסטיקות, אחת להיסטוגרמה
    col1, col2, col3 = st.columns([1, 1, 1])
      
    with col1:
        st.metric(label="Sum", value=f"{total_sum:,.2f}")
        st.metric(label="Median", value=f"{median_val:,.2f}")
        st.metric(label="Min", value=f"{min_val:,.2f}")
        st.metric(label="25th Percentile", value=f"{q25:,.2f}")
      
    with col2:
        st.metric(label="Mean", value=f"{mean_val:,.2f}")
        st.metric(label="Std Dev", value=f"{std_dev:,.2f}")
        st.metric(label="Max", value=f"{max_val:,.2f}")
        st.metric(label="75th Percentile", value=f"{q75:,.2f}")
    
    with col3:
        fig = px.histogram(col_data.dropna(), nbins=20, title=f'Histogram of {column}')
        fig.update_layout(xaxis_title='Value', yaxis_title='Frequency')
        st.plotly_chart(fig)

# פונקציה להצגת סטטיסטיקות עבור עמודות טקסטואליות
def display_statistics_text(df, column):
    col_data = df[column]
    total_values = col_data.size
    unique_values = col_data.nunique()
    distinct_values = col_data.drop_duplicates().nunique()
    
    unique_percentage = (unique_values / total_values) * 100
    distinct_percentage = (distinct_values / total_values) * 100
    
    # חלוקה לשלוש עמודות: גרף עוגה, גרף בר ו-expander
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        top_values = col_data.value_counts().head(5)
        fig_pie = px.pie(values=top_values.values, names=top_values.index, title="Top 5 Most Frequent Values")
        st.plotly_chart(fig_pie)
    
    with col2:
        labels = ['Unique Values', 'Distinct Values']
        values = [unique_values, distinct_values]
        percentages = [unique_percentage, distinct_percentage]
        
        fig_bar = px.bar(x=labels, y=values, title='Bar Chart of Column Analysis', labels={'x': 'Category', 'y': 'Count'})
        fig_bar.update_traces(text=[f'{v} ({p:.2f}%)' for v, p in zip(values, percentages)], textposition='outside')
        fig_bar.update_layout(
            hovermode="x unified",
            width=550,  # שמירה על רוחב הגרף
            height=500  # שמירה על גובה הגרף
        )
        fig_bar.update_traces(
            textfont_size=12  # שמירה על גודל הגופן של הערכים
        )
        st.plotly_chart(fig_bar)
    
    with col3:
        with st.expander("Unique Values"):
            st.write(col_data.dropna().unique().tolist())
        
        with st.expander("Distinct Values"):
            st.write(col_data.drop_duplicates().unique().tolist())

# פונקציה לניתוח עמודה 
def analyze_column(df, column):
    col_data = df[column]
    st.write(f"### Analysis of '{column}'")
    
    if pd.api.types.is_numeric_dtype(col_data):
        # הצגת סטטיסטיקות וגרף היסטוגרמה עבור עמודות מספריות
        display_statistics_numeric(df, column)
    
    elif pd.api.types.is_string_dtype(col_data):
        # ניתוח עבור עמודות טקסטואליות
        display_statistics_text(df, column)

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
        st.write("### Data Preview")
        df = apply_column_formats(df)  # יישום פורמטים שנשמרו
        st.dataframe(df, use_container_width=True)

    column = st.selectbox("Select a column to analyze:", df.columns)
    if column:
        change_column_format(df, column)
        analyze_column(df, column)
    
    show_missing_data(df)

    # ייצוא הנתונים כקובץ Excel
    st.write("### Export Data")
    if st.button("Export as CSV"):
        df_export = apply_column_formats(df.copy())
        csv = df_export.to_csv(index=False)
        st.download_button(label="Download CSV", data=csv, file_name="formatted_data.csv", mime="text/csv")

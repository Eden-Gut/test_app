import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# פונקציה לשינוי פורמט עמודות
def change_column_format(df, column):
    st.write("### Change Column Format")
    
    # אפשרויות לפורמט עמודה
    format_options = ["None", "Currency", "Date", "Numeric", "Text"]
    format_choice = st.selectbox("Choose format:", format_options)
    
    if format_choice == "Currency":
        df[column] = df[column].apply(lambda x: f"${x:,.2f}" if pd.api.types.is_numeric_dtype(df[column]) else x)
        st.write(f"Column '{column}' formatted as Currency.")
    
    elif format_choice == "Date":
        df[column] = pd.to_datetime(df[column], errors='coerce').dt.strftime('%Y-%m-%d')
        st.write(f"Column '{column}' formatted as Date.")
    
    elif format_choice == "Numeric":
        df[column] = pd.to_numeric(df[column], errors='coerce')
        st.write(f"Column '{column}' formatted as Numeric.")
    
    elif format_choice == "Text":
        df[column] = df[column].astype(str)
        st.write(f"Column '{column}' formatted as Text.")
    
    st.dataframe(df, use_container_width=True)

# פונקציה להצגת סטטיסטיקות או הערכים הנפוצים ביותר
def display_statistics_or_top_values(df, column):
    col_data = df[column]
    
    if pd.api.types.is_numeric_dtype(col_data):
        total_sum = col_data.sum()
        mean_val = col_data.mean()
        median_val = col_data.median()
        std_dev = col_data.std()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Sum", value=f"{total_sum:,.2f}")
        with col2:
            st.metric(label="Mean", value=f"{mean_val:,.2f}")
        
        col3, col4 = st.columns(2)
        with col3:
            st.metric(label="Median", value=f"{median_val:,.2f}")
        with col4:
            st.metric(label="Std Dev", value=f"{std_dev:,.2f}")
    
    elif pd.api.types.is_string_dtype(col_data):
        top_values = col_data.value_counts().head(4)
        col1, col2 = st.columns(2)
        for i, (value, count) in enumerate(top_values.items()):
            if i % 2 == 0:
                with col1:
                    st.metric(label=f"Value {i+1}", value=value)
            else:
                with col2:
                    st.metric(label=f"Value {i+1}", value=value)

# פונקציה לניתוח עמודה 
def analyze_column(df, column):
    col_data = df[column]
    st.write(f"### Analysis of '{column}'")
    
    total_values = col_data.size
    unique_values = col_data.nunique()
    missing_values = col_data.isna().sum()
    
    unique_percentage = (unique_values / total_values) * 100
    missing_percentage = (missing_values / total_values) * 100
    
    labels = ['Unique Values', 'Missing Values']
    values = [unique_values, missing_values]
    percentages = [unique_percentage, missing_percentage]
    
    col1, col2 = st.columns([2, 1])
    with col1:
        fig1 = px.bar(x=labels, y=values, title='Bar Chart of Column Analysis', labels={'x': 'Category', 'y': 'Count'})
        fig1.update_traces(text=[f'{v} ({p:.2f}%)' for v, p in zip(values, percentages)], textposition='outside')
        fig1.update_layout(hovermode="x unified")
        st.plotly_chart(fig1)
    
    with col2:
        with st.expander("Unique Values"):
            st.write(col_data.dropna().unique().tolist())
        
        with st.expander("Missing Values"):
            st.write(col_data[col_data.isna()].index.tolist())
    
    col3, col4 = st.columns(2)
    with col3:
        if pd.api.types.is_numeric_dtype(col_data):
            fig2 = px.histogram(col_data.dropna(), nbins=20, title=f'Histogram of {column}')
            fig2.update_layout(xaxis_title='Value', yaxis_title='Frequency')
            st.plotly_chart(fig2)
    
    with col4:
        display_statistics_or_top_values(df, column)

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

# הגדרת מצב תצוגה רחב
st.set_page_config(layout="wide")

# Expander להעלאת קובץ
with st.expander("Upload your CSV file", expanded=True):
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    with st.expander("Data Preview", expanded=True):
        st.write("### Data Preview")
        st.dataframe(df, use_container_width=True)

    column = st.selectbox("Select a column to analyze:", df.columns)
    if column:
        change_column_format(df, column)
        analyze_column(df, column)
        
    show_missing_data(df)

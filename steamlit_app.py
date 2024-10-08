import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff #למפת חום

# הגדרת מצב תצוגה רחב
st.set_page_config(layout="wide")

# עיצוב סטייל מותאם עבור הסטטיסטיקות וה-sidebar
st.markdown(
    """
    <style>
    {
    font-size: 24px
    }
    div[data-testid="stMetric"] {
        # background-color: #f5f5f5;
        border: 6px solid #5D7599;
        padding: 10px;
        border-radius: 10px;
        color: black;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        font-size: 30px;
    }
    [data-testid="stMetricLabel"] {
        font-size: 30px;
        font-weight: bold;
        margin-bottom: 5px;
       
    }
   [data-testid="stMetricValue"] {
        font-size: 24px;
        font-weight: bold;
    }

    section[data-testid="stSidebar"] {
        background-color: #333333;
    }

    a {
        color: #F0F2F6 !important;
        text-decoration: none !important;

    }

    a:hover {
        color: #f7f0c6 !important;
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
    st.markdown("<h3 id='change-column-format'>Change Column Format</h3>", unsafe_allow_html=True)
    
    current_format = st.session_state["column_formats"].get(column, "None")
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
    
    save_col, download_col = st.columns([1, 1])
    with save_col:
        if st.button("Save Format"):
            st.session_state["column_formats"][column] = format_choice
            st.success(f"Format for column '{column}' saved as {format_choice}.")
    with download_col:
        @st.cache_data
        def convert_df_to_excel(df):
            return df.to_excel(index=False)

       
    selected_columns = st.multiselect(
        "Filter columns",
        options=df.columns,
        default=df.columns.tolist(),
        key="filter-columns"
    )

    filtered_df = df[selected_columns]
    st.dataframe(filtered_df, use_container_width=True)
# פונקציה להצגת מפת חום של מתאמים
def display_correlation_heatmap(df):
    # סינון עמודות מספריות בלבד
    numeric_df = df.select_dtypes(include=['number'])
    
    # חישוב מטריצת המתאמים
    corr_matrix = numeric_df.corr()
    
    # יצירת מפת חום עם Plotly
    fig = ff.create_annotated_heatmap(
        z=corr_matrix.values,
        x=list(corr_matrix.columns),
        y=list(corr_matrix.columns),
        annotation_text=corr_matrix.round(2).values,
        colorscale='Viridis'
    )
    fig.update_layout(xaxis_title='Columns', yaxis_title='Columns')
    
    # הצגת מפת החום ב-Streamlit
    st.plotly_chart(fig, use_container_width=True)
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
    
    col1, col2, col3, col4 = st.columns([0.3, 0.3, 1,1])
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
        histogram = px.histogram(col_data.dropna(), nbins=20, title=f'Histogram of {column}')
        histogram.update_layout(xaxis_title='Value', yaxis_title='Frequency', title_font=dict(size=20))
        st.plotly_chart(histogram)
    with col4:
        box_plot = px.box(df, y=column, title=f'Box Plot of {column} with Outliers')
        box_plot.update_layout(title_font=dict(size=20)) 
        st.plotly_chart(box_plot)
        #st.markdown(f"<h4>Correlation Heatmap for Numerical Columns</h4>", unsafe_allow_html=True)
       # numeric_df = df.select_dtypes(include=[np.number])
       # if not numeric_df.empty:
        #    display_correlation_heatmap(numeric_df)

# פונקציה להצגת סטטיסטיקות עבור עמודות טקסטואליות
def display_statistics_text(df, column):
    col_data = df[column]
    total_values = col_data.size
    unique_values = col_data.nunique()
    distinct_values = col_data.drop_duplicates().nunique()
    
    unique_percentage = (unique_values / total_values) * 100
    distinct_percentage = (distinct_values / total_values) * 100
    
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
        st.plotly_chart(fig_bar)
    with col3:
        with st.expander("Unique Values"):
            st.write(col_data.dropna().unique().tolist())
        with st.expander("Distinct Values"):
            st.write(col_data.drop_duplicates().unique().tolist())

# פונקציה לניתוח עמודה
def analyze_column(df, column):
    st.markdown("<h3 id='analyze-column'>Analyze Column</h3>", unsafe_allow_html=True)
    col_data = df[column]
    
    if pd.api.types.is_numeric_dtype(col_data):
        display_statistics_numeric(df, column)
    elif pd.api.types.is_string_dtype(col_data) or  pd.api.types.is_categorical_dtype(col_data):
        display_statistics_text(df, column)

# פונקציה להצגת ערכים חסרים כולל ריקים ""
def highlight_missing(val):
    if pd.isnull(val) or val == "":
        return 'background-color: #C43636'
    return ''

def show_missing_data(df):
    st.markdown("<h3 id='handling-missing-values'>Handling Missing Values</h3>", unsafe_allow_html=True)
    missing_data = df[df.isnull().any(axis=1) | (df == "").any(axis=1)]
    
    if not missing_data.empty:
        st.write("Rows with Missing Values:")
        st.dataframe(missing_data.style.applymap(highlight_missing), use_container_width=True)
    
    column = st.selectbox("Select column to fill missing values:", df.columns[df.isnull().any() | (df == "").any()])
    if column:
        if pd.api.types.is_numeric_dtype(df[column]):
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
        else:
            fill_option = st.selectbox("How would you like to fill the missing values?", ["Mode", "Custom Value"])
            if fill_option == "Mode":
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
        st.markdown("<h3 id='data-preview'>Data Preview</h3>", unsafe_allow_html=True)
        df = apply_column_formats(df)
        st.dataframe(df, use_container_width=True)

    column = st.selectbox("Select a column to analyze:", df.columns)
    if column:
        change_column_format(df, column)
        analyze_column(df, column)
        show_missing_data(df)

    # Sidebar עם קישורים יופיע רק אחרי העלאת קובץ
    with st.sidebar:
        st.markdown("<h2 style='color:white;'>Navigation</h2>", unsafe_allow_html=True)
        st.markdown("[Change Column Format](#change-column-format)", unsafe_allow_html=True)
        st.markdown("[Analyze Column](#analyze-column)", unsafe_allow_html=True)
        st.markdown("[Handling Missing Values](#handling-missing-values)", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

else:
    st.sidebar.write("Upload a CSV file to enable navigation.")

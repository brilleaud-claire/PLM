# streamlit app
import streamlit as st
from streamlit import components
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px


st.set_page_config(
    page_title="SWEET YOGURT",
    layout="wide"
)

#Title of the app
st.title(":blue[SWEET YOGURT]")
st.subheader("created by Noémie, Claire, Tulipe and Bérénice")
st.markdown("SB A5 -- ESILV")
st.image("sunrise.jpg")

#Uploading dataset
st.sidebar.title("Upload dataset")
df = st.sidebar.file_uploader("Choose a file", type = ["csv"])
if df is None :
    st.write("Please, put your file on the left part of the application !")
else :
    df = pd.read_csv(df)

st.set_option('deprecation.showPyplotGlobalUse', False)


# basic information and pre-processing
def basic_info():
    st.title("Basic Information")
    st.write("This page is dedicated to basic information about the dataset and preprocessing.")
    
    #shape
    st.write(f"Data shape: {df.shape}")
    
    #head
    st.markdown("Data preview")
    st.write(df.head())
    
    #types
    st.markdown("Data types")
    df.dtypes
    
    #columns
    st.markdown("Columns name")
    df.columns
    
    #unique value
    st.markdown("Unique value")
    unique = df.nunique()
    st.write(unique)
    
    #cheking NaN or Null value
    st.write("Check NaN, Null or Na values :")
    check = df.isna().sum()
    st.write(check)

    #describe
    st.markdown("Data description")
    st.write(df.describe())

    #number of records
    st.write(f"Number of records: {df.shape[0]}")
    
    #number of features
    st.write(f"Number of features: {df.shape[1]}")

# Data visualization and plot Distribution  
def  user_selected_feature():
    
    feature = st.selectbox("Select a feature ", df.columns)

    # Plot of the distribution of patients 
    plt.figure(figsize=(8, 8))
    st.title("Plot of the distribution of patients by "+ str(feature))
    num_bins = st.slider("Select number of bins:", min_value=5, max_value=50, value=20)
    sns.histplot(df[feature], bins=num_bins, color="blue", kde=True)
    #plt.hist(df[feature], bins=num_bins, color="skyblue", edgecolor="blue")
    st.pyplot()

    # Table with statistical information
    st.title("Table with statistical information on "+str(feature))
    st.table(df[feature].describe())

    # Plot a box plot for the selected feature
    plt.figure(figsize=(8, 8))
    st.title("Box Plot for "+str(feature))
    fig, ax = plt.subplots()
    sns.boxplot(data=df, y=feature, ax=ax)
    st.pyplot(fig)

    # Pie chart for the selected feature
    plt.figure(figsize=(8, 8))
    st.title("Pie chart for "+str(feature))
    if feature == 'bmi' :
        df['bmi_cat'] = df['bmi'].apply(imc)
        bmi_cat_count = df['bmi_cat'].value_counts()
        plt.pie(bmi_cat_count, labels=bmi_cat_count.index, autopct='%1.1f%%', startangle=0)
        st.pyplot()
    
    elif feature == 'age':
        df['age_group'] = df['age'].apply(age_grp)
        age_cat_count = df['age_group'].value_counts()
        plt.pie(age_cat_count, labels=age_cat_count.index, autopct='%1.1f%%', startangle=0)
        plt.title('Age Group Distribution')
        st.pyplot()
        
    else :
        pie_chart = df.groupby([feature])[feature].count()
        labels = pie_chart.index
        fig, ax = plt.subplots()
        ax.pie(pie_chart, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        st.pyplot(fig)

# function to make bmi category
def imc(imc):
    
    if imc < 18.5:
        return "underweight"
    elif 18.5 <= imc < 25:
        return "Normal"
    elif 25 <= imc < 30:
        return "Overweight"
    elif 30 <= imc < 35:
        return "Obesity I"
    elif 35 <= imc < 40:
        return "Obesity II"
    else:
        return "Obésity III"

# function to make age category
def age_grp(age):
    if age < 20:
        return "under 20"
    elif 20 <= age < 30:
        return "20-30"
    elif 30 <= age < 40:
        return "30-40"
    elif 40 <= age < 50:
        return "40-50"
    elif 50 <= age < 60:
        return "50-60"
    else:
        return "over 60"
        
def correlation():
    
    st.write('Here you can visualize the correlation between two features.')
    
    feature1 = st.selectbox("Select a feature 1 ", df.columns)
    feature2 = st.selectbox("Select a feature 2 ", df.columns) 
    
    if df[feature1].dtype == object or df[feature2].dtype == object :
        st.write('Please, take int or float features.')
    else:
        correlation = df[[feature1, feature2]]
        correlation= correlation.dropna(subset=[feature2])
    
        st.write('You will have a scatterplot between this two variables, a correlation matrix and a scatterplot with stroke as hue.')

        # scatterplot
        st.write("# Scatterplot")
        
        plt.figure(figsize=(8, 8))    
        sns.scatterplot(x=feature1, y=feature2, alpha=0.2, data=df)
        sns.regplot(x=feature1, y=feature2, data=df)
        st.pyplot()
        
        # matrix
        st.write('# Correlation matrix')
        plt.figure(figsize=(8, 8))
        fig = px.imshow(correlation.corr(), text_auto=True)
        st.plotly_chart(fig)
        
        # scatterplot with stroke as hue
        st.write('# Scatterplot with stroke as hue')
        plt.figure(figsize=(8, 8))
        sns.scatterplot(x=feature1, y=feature2, hue="stroke", alpha=0.3, data=df)
        st.pyplot()
    
# User input
def user_input():
    
    st.title('User Input')
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    # age
    age = col1.number_input("Age", min_value=1, max_value=120, value=25)

    # gender
    gender_options = ["Male", "Female", "Other"]
    gender = col2.radio("Gender", gender_options)
    
    # married
    married_status = col3.checkbox("Ever married")

    # smoking status
    smoking_options = ["never smoked","formerly smoke", "smokes"]
    smoking_status = col4.selectbox("Smoking status",smoking_options)
    
    # strok
    has_stroke = col5.checkbox("Already have a stroke")
    
    # residence type
    residence_type = ["Urban", "Rural"]
    residence = col6.radio("Residence type", residence_type)
    
    # summary
    st.subheader("Patient Profile")
   
    st.write(f"**Age:** {age}")
    st.write(f"**Gender:** {gender}")
    st.write(f"**Married Status:** {married_status}")
    st.write(f"**Smoking Status:** {smoking_status}")
    st.write(f"**Residence type:** {residence}")
    st.write(f"**Already has a stroke:** {has_stroke}")

# page names 
page_functions = {
    "Basic Information": basic_info,
    "User selected feature ": user_selected_feature,
    "Correlation ": correlation,
    "User Input":user_input,
}

# tabs
tabs = st.sidebar.selectbox("Select a page", tuple(page_functions.keys()))

# Render the selected page
page_functions[tabs]()
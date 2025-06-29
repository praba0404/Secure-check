import streamlit as st
import pandas as pd
import plotly.express as px
import mysql.connector
from mysql.connector import Error


st.set_page_config(page_title='Secure check police dashboard')
# Now other Streamlit commands
st.title("Police Logs Dashboard")

# Inject custom CSS to set a mild background color
st.markdown("""
    <style>
    .stApp {
        background-color: #e8f5e9;  /* Light green */
    }
    </style>
    """, unsafe_allow_html=True)



# Create a connection to the MySQL database
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Disneyworld@33',
            database='Secure_Check'
        )
        return connection
    except Error as e:
        st.error(f"Connection failed: {e}")
        return None
    

# Fetch data using a SQL query
def fetch_data(query):
    connection = create_connection()
    if connection is None:
        return pd.DataFrame()  

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            column_names = [i[0] for i in cursor.description]
            df = pd.DataFrame(result, columns=column_names)
            return df
    except Error as e:
        st.error(f"Query failed: {e}")
        return pd.DataFrame()
    finally:
        connection.close()


# Streamlit UI:
st.title("SecureCheck: A Python-SQL Digital Ledger for Police Post Logs")
st.markdown("Law Enforcement & Public Safety Real-time Monitoring Systems")

# Main Data Overview:
st.header('Police Log Overview')
query = "SELECT * FROM traffic_logs"
data = fetch_data(query)

# Debug log:
st.write("✅ Rows fetched:", len(data))

if not data.empty:
    st.dataframe(data, use_container_width=True)
else:
    st.warning("⚠️ No data fetched from the database.")


#Queries:
st.header('Advanced Insights')

combined_query_map = {
    # First group of insights
    "Frequently searched vehical": """
        SELECT Vehicle_number, 
    COUNT(*) AS Search_count 
FROM traffic_logs
WHERE LOWER(Search_type) = 1
GROUP BY Vehicle_number
ORDER BY Search_count DESC;
    """,

    "Highest age group got arrested": """
       SELECT 
    CASE 
        WHEN Driver_age BETWEEN 15 AND 25 THEN '15-25'
        WHEN Driver_age BETWEEN 26 AND 35 THEN '26-35'
        WHEN Driver_age BETWEEN 36 AND 45 THEN '36-45'
        WHEN Driver_age BETWEEN 46 AND 60 THEN '46-60'
        ELSE '60+'
    END AS Age_Group,
    COUNT(*) AS Total_Stops,
    SUM(CASE WHEN Is_arrested = '1' THEN 1 ELSE 0 END) AS Arrests,
    ROUND(100.0 * SUM(CASE WHEN Is_arrested = '1' THEN 1 ELSE 0 END) / COUNT(*), 2) AS Arrest_Rate
FROM traffic_logs
GROUP BY Age_Group
ORDER BY Arrest_Rate DESC;
    """,

    "The gender of driver stopped in each country": """
        SELECT Country_name, Driver_gender, COUNT(*) AS Stop_Count 
        FROM traffic_logs
        GROUP BY Country_name, Driver_gender
        ORDER BY Country_name, Stop_Count DESC;
    """,

    "Race and Gender combination has the highest search rate": """
    SELECT Driver_race, Driver_gender, 
    COUNT(*) AS Total_Stops,
    SUM(CASE 
            WHEN Search_conducted IN ('Vehicle Search', 'Frisk') THEN 1 ELSE 0 END) AS Specific_Searches,
    ROUND(
        100.0 * SUM(CASE WHEN Search_conducted IN ('Vehicle Search', 'Frisk') THEN 1 ELSE 0 END) / COUNT(*), 
        2
    ) AS Search_Rate
FROM traffic_logs
GROUP BY Driver_race, Driver_gender
ORDER BY Search_Rate DESC;
""",

    "The time of day sees the most traffic stops": """
        SELECT HOUR(Stop_time) AS Hour, COUNT(*) AS Stop_Count
        FROM traffic_logs
        GROUP BY HOUR(Stop_time)
        ORDER BY Stop_Count DESC;
    """,
    "The average stop duration for different violations": """st
        SELECT Violation,
               ROUND(AVG(
                   CASE 
                       WHEN Stop_duration = '0-15 Min' THEN 10
                       WHEN Stop_duration = '16-30 Min' THEN 23
                       WHEN Stop_duration = '30+ Min' THEN 40
                       ELSE NULL
                   END
               ), 2) AS Avg_Stop_Duration_Minutes
        FROM traffic_logs
        GROUP BY Violation
        ORDER BY Avg_Stop_Duration_Minutes DESC;
    """,
    "Are stops during the night more likely to lead to arrests": """
        SELECT
            CASE
                WHEN HOUR(Stop_time) BETWEEN 0 AND 5 THEN 'Night'
                WHEN HOUR(Stop_time) BETWEEN 6 AND 11 THEN 'Morning'
                WHEN HOUR(Stop_time) BETWEEN 12 AND 17 THEN 'Afternoon'
                ELSE 'Evening'
            END AS Time_of_Day,
            COUNT(*) AS Total_Stops,
            SUM(CASE WHEN LOWER(Is_arrested) = '1' THEN 1 ELSE 0 END) AS Total_Arrests,
            ROUND(100.0 * SUM(CASE WHEN LOWER(Is_arrested) = '1' THEN 1 ELSE 0 END) / COUNT(*), 2) AS Arrest_Rate_Percent
        FROM traffic_logs
        WHERE Stop_time IS NOT NULL
        GROUP BY Time_of_Day
        ORDER BY Arrest_Rate_Percent DESC;
    """,

    "Country that report the highest rate of drug-related stops": """
       SELECT Country_name,
    COUNT(*) AS Total_Stops,
    SUM(CASE WHEN Drugs_related_stop = '1' THEN 1 ELSE 0 END) AS Drug_Stops,
    ROUND(
        100.0 * SUM(CASE WHEN Drugs_related_stop = '1' THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS Drug_Stop_Rate_Percent
FROM traffic_logs
WHERE Country_name IS NOT NULL
GROUP BY Country_name
ORDER BY Drug_Stop_Rate_Percent DESC;
    """,

    "Violations that are most common among younger drivers (<25)": """
        SELECT Violation,
               COUNT(*) AS Total_Stops
        FROM traffic_logs
        WHERE Driver_age < 25 AND Violation IS NOT NULL
        GROUP BY Violation
        ORDER BY Total_Stops DESC;
    """,

    # Second group of insights
    "Yearly Breakdown of Stops and Arrests by Country": """
       SELECT
    Year,
    Country_name,
    Total_Stops,
    Total_Arrests,
    ROUND(100.0 * Total_Arrests / Total_Stops, 2) AS Arrest_Rate_Percent,
    SUM(Total_Arrests) OVER (PARTITION BY Country_name ORDER BY Year) AS Cumulative_Arrests
FROM (
    SELECT
        YEAR(Stop_date) AS Year,
        Country_name,
        COUNT(*) AS Total_Stops,
        SUM(CASE WHEN Is_arrested IN ('1') THEN 1  ELSE 0  END) AS Total_Arrests
    FROM traffic_logs
    WHERE  Stop_date IS NOT NULL AND  Country_name IS NOT NULL
    GROUP BY YEAR(Stop_date), Country_name
) AS YearlyStats
ORDER BY Country_name, Year;
    """,

    "Driver Violation Trends Based on Age and Race": """
        SELECT
    CASE
        WHEN Driver_age BETWEEN 15 AND 25 THEN '15-25'
        WHEN Driver_age BETWEEN 26 AND 35 THEN '26-35'
        WHEN Driver_age BETWEEN 36 AND 45 THEN '36-45'
        WHEN Driver_age BETWEEN 46 AND 60 THEN '46-60'
        WHEN Driver_age > 60 THEN '60+'
        ELSE 'Unknown'
    END AS Age_Group,
    Driver_race,
    Violation,
    COUNT(*) AS Total_Stops
FROM  traffic_logs
WHERE Driver_age IS NOT NULL
    AND Driver_race IS NOT NULL
    AND Violation IS NOT NULL
GROUP BY Age_Group, Driver_race, Violation
ORDER BY Age_Group, Driver_race, Total_Stops DESC;
    """,

    "Time Period Analysis of Stops":"""
SELECT
    YEAR(Stop_date) AS Stop_Year,
    MONTH(Stop_date) AS Stop_Month,
    HOUR(Stop_time) AS Stop_Hour,
    COUNT(*) AS Total_Stops
FROM traffic_logs
WHERE Stop_date IS NOT NULL 
    AND Stop_time IS NOT NULL
GROUP BY YEAR(Stop_date), MONTH(Stop_date), HOUR(Stop_time)
ORDER BY Stop_Year, Stop_Month, Stop_Hour;
""",

    "Violations with High Search and Arrest Rates":"""SELECT
    Violation,
    Total_Stops,
    Searches,
    Arrests,
    Search_Rate_Percent,
    Arrest_Rate_Percent,
    RANK() OVER (ORDER BY Search_Rate_Percent DESC) AS Search_Rank,
    RANK() OVER (ORDER BY Arrest_Rate_Percent DESC) AS Arrest_Rank
FROM (
    SELECT
        Violation,
        COUNT(*) AS Total_Stops,
        SUM(CASE WHEN LOWER(Search_conducted) in ('Vehicle Search', 'Frisk') THEN 1 ELSE 0 END) AS Searches,
        SUM(CASE WHEN LOWER(Is_arrested) = 1 THEN 1 ELSE 0 END) AS Arrests,
        ROUND(100.0 * SUM(CASE WHEN LOWER(Search_conducted) in ('Vehicle Search', 'Frisk')  THEN 1 ELSE 0 END) / COUNT(*), 2) AS Search_Rate_Percent,
        ROUND(100.0 * SUM(CASE WHEN LOWER(Is_arrested) = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS Arrest_Rate_Percent
    FROM traffic_logs
    WHERE Violation IS NOT NULL
    GROUP BY Violation
) AS violation_stats
ORDER BY Arrest_Rate_Percent DESC, Search_Rate_Percent DESC;
""",

    "Top 5 Violations with Highest Arrest Rates": """SELECT
    Violation,
    COUNT(*) AS Total_Stops,
    SUM(CASE WHEN LOWER(Is_arrested) = 1 THEN 1 ELSE 0 END) AS Total_Arrests,
    ROUND(100.0 * SUM(CASE WHEN LOWER(Is_arrested) = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS Arrest_Rate_Percent
FROM traffic_logs
WHERE Violation IS NOT NULL
GROUP BY Violation
HAVING COUNT(*) > 10  -- Optional: exclude very rare violations for reliability
ORDER BY Arrest_Rate_Percent DESC
LIMIT 5;
"""
}

# Sidebar Filters(bar chart,pie chart)
st.sidebar.header("Filter Options")

gender_filter = st.sidebar.selectbox("Select Driver Gender", options=['All'] + data['Driver_gender'].dropna().unique().tolist())
race_filter = st.sidebar.selectbox("Select Driver Race", options=['All'] + data['Driver_race'].dropna().unique().tolist())

# Apply filters
filtered_data = data.copy()
if gender_filter != 'All':
    filtered_data = filtered_data[filtered_data['Driver_gender'] == gender_filter]
if race_filter != 'All':
    filtered_data = filtered_data[filtered_data['Driver_race'] == race_filter]

# 1. Total Arrests by Country 
arrests_by_country = (
    filtered_data.groupby('Country_name')['Is_arrested']
    .sum()
    .reset_index()
    .sort_values(by='Is_arrested', ascending=False)
)

fig1 = px.bar(
    arrests_by_country,
    x='Country_name',
    y='Is_arrested',
    title='Total Arrests by Country',
    color='Is_arrested',
    color_continuous_scale='Blues'
)
fig1.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig1, use_container_width=True)

# 2. Age Distribution
fig2 = px.histogram(
    filtered_data,
    x='Driver_age',
    nbins=20,
    title='Driver Age Distribution'
)
st.plotly_chart(fig2, use_container_width=True)

# 3. Stop Outcomes (Pie Chart)
outcome_counts = filtered_data['Stop_outcome'].value_counts().reset_index()
outcome_counts.columns = ['Outcome', 'Count']
fig3 = px.pie(
    outcome_counts,
    names='Outcome',
    values='Count',
    title='Stop Outcomes Distribution'
)
st.plotly_chart(fig3)

# 4. Violation vs. Gender
fig4 = px.histogram(
    filtered_data,
    x='Violation',
    color='Driver_gender',
    barmode='group',
    title='Violation Type by Gender'
)
st.plotly_chart(fig4, use_container_width=True)

# Dropdown to select query:

selected_query = st.selectbox("Select an insight to run", list(combined_query_map.keys()))

# Run the query when button is clicked
if st.button("Run Query"):
    df_result = fetch_data(combined_query_map[selected_query])
    if not df_result.empty:
        st.success(f"✅ Query executed successfully: {selected_query}")
        st.dataframe(df_result, use_container_width=True)
    else:
        st.warning("⚠️ No results returned for this query.")

st.header("Police log Prediction & Outcome:")

# Form for new log prediction:
with st.form('new_log_form'):
    Stop_date = st.date_input("Stop date")
    Stop_time = st.time_input("Stop time")
    Country_name = st.selectbox("Country name",['India','Canada','USA','other'])
    Driver_gender = st.radio("Driver gender", ['Male', 'Female'])
    Driver_age =int( st.number_input("Driver age", min_value=16, max_value=100))
    Driver_race = st.selectbox("Driver race", ['Asian', 'White','Black','Hispanic','other'])
    Violation = st.selectbox("Violation",['Speeding','DUI','Seatbelt','Signal','other'])
    Search_conducted = st.selectbox("Search conducted",['0','1'] )
    Search_type = st.selectbox("Search type",['Vehical search', 'Frisk'])
    Stop_outcome = st.selectbox("Stop outcome",['Warning','Ticket','Arrest'])
    Is_arrested = st.selectbox("Is arrested?", ['1','0'])
    Stop_duration = st.selectbox("Stop duration", ['0-15 Min', '16-30 Min', '30+ Min'])         
    Drugs_related_stop = st.selectbox("Drugs Related Stop", ['0', '1'])

    submitted = st.form_submit_button("Predict stop outcome and violation")
    


# Handle prediction:
if submitted:
    try:
        # Debug output
        st.write("🔍 Debug - Filtering with values:")
        st.write({
            "Driver_gender": Driver_gender,
            "Driver_age": Driver_age,
            "Search_conducted": Search_conducted,
            "Search_type": Search_type,
            "Stop_outcome": Stop_outcome,
            "Stop_duration": Stop_duration,
            "Is_arrested": Is_arrested,
            "Drugs_related_stop": Drugs_related_stop,
            "Violation": Violation,
            "Stop_date": Stop_date,
            "Stop_time": Stop_time,
            "Driver_race": Driver_race,
            "Country_name": Country_name,
        })

        # Filtering from the DataFrame
        Filtered_data = data[
            (data['Driver_gender'] == Driver_gender) &
            (data['Driver_age'] == Driver_age) &
            (data['Search_conducted'].astype(str) == Search_conducted) &
            (data['Search_type'] == Search_type) &
            (data['Stop_outcome'] == Stop_outcome) &
            (data['Stop_duration'] == Stop_duration) &
            (data['Is_arrested'] == int(Is_arrested)) &
            (data['Drugs_related_stop'] == int(Drugs_related_stop)) &
            (data['Violation'] == Violation) &
            (data['Stop_date'] == Stop_date) &
            (data['Stop_time'] == Stop_time) &
            (data['Driver_race'] == Driver_race) &
            (data['Country_name'] == Country_name)
        ]

        # Prediction logic:
        if not Filtered_data.empty:
            predicted_outcome = Filtered_data['Stop_outcome'].mode()[0]
            predicted_violation = Filtered_data['Violation'].mode()[0]
        else:
            predicted_outcome = "Warning"
            predicted_violation = "Speeding"

        # Display result:
        st.markdown("### 📊 Prediction Summary")
        st.success("✅ Prediction completed based on your input.")
        st.markdown(f"""
        **Predicted Violation:** :blue[**{predicted_violation}**]  
        **Predicted Outcome:** :red[**{predicted_outcome}**]  

        A **{Driver_age}**-year-old **{Driver_gender}** driver in **{Country_name}** was stopped at  
        **{Stop_time.strftime('%I:%M %p')}** on **{Stop_date.strftime('%B %d, %Y')}**  
        during a **{Search_type}**. The stop was marked as **{Drugs_related_stop}** for drugs.  

        - **Stop Duration:** {Stop_duration}  
        - **Violation:** {Violation}
        """)

    except Exception as e:
        st.error(f"❌ An error occurred during filtering or prediction:\n\n{e}")









  

	
	


	
	
    	
        	
      
        
        	
            



    


    















    
    








    
























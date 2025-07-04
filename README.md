# Secure-check
Step 1:
Setup and Imports - Required libraries are imported:
         -->streamlit for creating interactive web UI
         -->pandas for data manipulation and handling
         -->plotly.express for building visual charts and graphs
         -->mysql.connector for database connectivity
         -->dotenv (from dotenv import load_dotenv)  for securely loading environment variables from a .env file
         -->os for accessing the environment variables inside your Python code


         
Step 2: 
Streamlit Page Configuration - The page title is set, and a light green background is applied via custom CSS for a clean UI.

Step 3:
MySQL Connection Setup - A function create_connection() is defined to establish a connection to the MySQL Secure_Check database. Error handling is included to notify failed connections.

Step 4: 
Data Fetching Function - A reusable function fetch_data(query) is created to Execute custom SQL queries,Return results as a DataFrameHandle errors and close connections properly.

Step 5:
Dashboard Initialization
         -->The dashboard title and intro are set.
         -->A default query fetches all data from traffic_logs for display.
         -->A table view is shown with real-time data and row count.
         
Step 6:
SQL Insight Queries - A dictionary combined_query_map holds multiple predefined SQL insights, such as Most searched vehicles,Arrest rate by age group,Violation trends,Drug-related stop rates,Stop patterns over time. These queries use various SQL techniques like grouping, filtering, CASE statements, and window functions,joints.

Step 7: 
Sidebar Filter Options - Additionally, sidebar widgets allow the user to filter data by Driver Gender and Driver Race. Filtered data is used in charts and prediction logic.

Step 8:
Visual Data Representations using Plotly: 
         -->Total arrests by country (bar chart)
         -->Driver age distribution (histogram)
         -->Stop outcomes (pie chart)
         -->Violations by gender (grouped bar chart)
       
Step 9:
SQL Query Execution:
         -->A dropdown allows to select queries from predefined SQL insights.
         -->On clicking "Run Query", the corresponding SQL query is executed.
         -->Results are shown in a dataframe with success/error messages.
        
Step 10:
Prediction & Outcome Section - A Streamlit form (st.form) captures new log details like Driver info (age, gender, race),country,Stop details (time, date, type, duration),Violation, search type, and drug involvement

Step 11:
Prediction Logic - Once submitted, the form:    
          -->Filters the main dataset based on input criteria
          -->If matches are found: It predicts the most common violation and stop outcome
          -->If no match: Then defaults to "Speeding" and "Warning"
          
Step 12: 
Error Handling: Any filtering or prediction error is caught then it would help with debugging.
Final prediction logic: Finally, the prediction logic checks if any data matches the input. If a match is found, it predicts the most frequent violation and stop outcome.
Otherwise, it falls back to default values:
Violation --> "Speeding"
Outcome --> "Warning"



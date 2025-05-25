# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests # Import the requests library
import pandas as pd # Import pandas for DataFrame operations

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom smoothie!
    """
)

name_on_order = st.text_input("Name on Smoothie:")

# Only show the name if it's entered
if name_on_order:
    st.write("The name on your smoothie will be:", name_on_order)

# Establish Snowflake connection
# Make sure your connection is set up correctly in Streamlit secrets or config
cnx = st.connection("snowflake")
session = cnx.session() # Corrected from cnx_session() to cnx.session()

# Fetch fruit options from Snowflake
# IMPORTANT: Select all columns you intend to use.
# I'm assuming 'search_on' is a column in your fruit_options table that holds the value you want.
# If the column name is different, please change 'search_on' to your actual column name.
my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name'), col('search_on'))

# Convert Snowpark DataFrame to Pandas DataFrame for easier filtering/lookup
pd_df = my_dataframe.to_pandas()

# --- DEBUGGING LINES ADDED HERE ---
st.subheader("Debugging DataFrame Content:")
st.write("Columns in pd_df:", pd_df.columns.tolist())
st.dataframe(pd_df)
# --- END DEBUGGING LINES ---

# Convert the 'FRUIT_NAME' column from the Pandas DataFrame to a list for st.multiselect
# This line will also fail if 'FRUIT_NAME' is not a column in pd_df
fruit_names_list = pd_df['FRUIT_NAME'].tolist()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_names_list,
    max_selections=5
)

# Debugging: Check if 'requests' is defined after import (from previous troubleshooting)
st.write(f"Is 'requests' defined after import? {'requests' in globals()}")
try:
    st.write(f"Type of 'requests' after import: {type(requests)}")
except NameError:
    st.write("`requests` is not defined immediately after import!")


# Process the selected ingredients and prepare the order
if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Corrected lookup in the Pandas DataFrame
        # Column names from Snowflake often become uppercase in Pandas DataFrames
        try:
            # The KeyError is happening here if 'FRUIT_NAME' is not found
            search_on_value = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
            st.write('The search value for ',fruit_chosen,' is ', search_on_value)
        except IndexError:
            st.warning(f"Could not find search value for '{fruit_chosen}'. Check your fruit_options table data.")
        except KeyError as e:
            # More specific error message for debugging
            st.error(f"KeyError: {e}. Missing expected column in DataFrame. Please check Snowflake table schema and column casing.")


    # Corrected SQL insert statement
    # Changed 'customer_name' to 'NAME_ON_ORDER' to match common Snowflake unquoted identifier casing.
    # IMPORTANT: Verify this matches your actual column name and casing in Snowflake.
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, NAME_ON_ORDER)
        VALUES ('{ingredients_string.strip()}', '{name_on_order}')
    """

    # Display the query for debugging purposes (optional, remove in production)
    # st.write("Generated SQL Query:", my_insert_stmt)

    # Button to submit the order
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        if not name_on_order:
            st.error("Please enter a name for your smoothie before submitting the order.")
        else:
            try:
                session.sql(my_insert_stmt).collect()
                st.success('Your Smoothie is ordered!', icon="✅")
            except Exception as e:
                st.error(f"An error occurred while submitting your order: {e}")
                st.write("Please check your Snowflake table schema and connection.")

# --- Add requests API call here ---
# Make a request to an external API and display its JSON response
st.subheader("External API Data Example:")
try:
    smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
    # Check if the request was successful
    if smoothiefroot_response.status_code == 200:
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
    else:
        st.error(f"Failed to fetch data from API. Status code: {smoothiefroot_response.status_code}")
except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the API: {e}")

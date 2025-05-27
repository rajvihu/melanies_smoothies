import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom smoothie!
    """
)

name_on_order = st.text_input("Name on Smoothie:")

if name_on_order:
    st.write("The name on your smoothie will be:", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options from Snowflake
# Ensure 'SEARCH_ON' is indeed the column name and case in your Snowflake table
my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name'), col('search_on'))
pd_df = my_dataframe.to_pandas()

# --- DEBUGGING LINES ADDED HERE ---
st.subheader("Debugging DataFrame Content (after to_pandas):")
st.write("Columns in pd_df:", pd_df.columns.tolist())
st.dataframe(pd_df) # Inspect this DataFrame carefully
# --- END DEBUGGING LINES ---

# Convert the 'FRUIT_NAME' column from the Pandas DataFrame to a list for st.multiselect
# Ensure 'FRUIT_NAME' is the correct column name (case-sensitive)
try:
    fruit_names_list = pd_df['FRUIT_NAME'].tolist()
except KeyError:
    st.error("Error: 'FRUIT_NAME' column not found in the DataFrame. Please check your Snowflake query and column casing.")
    fruit_names_list = [] # Initialize to empty list to prevent further errors

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_names_list,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # --- CRITICAL DEBUGGING FOR search_on ---
        st.write(f"Processing: {fruit_chosen}")
        
        # Ensure column names are correct (FRUIT_NAME, SEARCH_ON)
        # Use .copy() to avoid SettingWithCopyWarning if you modify this later, though not strictly needed here.
        filtered_fruit = pd_df[pd_df['FRUIT_NAME'] == fruit_chosen]

        if not filtered_fruit.empty:
            # Check if 'SEARCH_ON' column exists in the filtered DataFrame
            if 'SEARCH_ON' in filtered_fruit.columns:
                search_on = filtered_fruit['SEARCH_ON'].iloc[0]
                st.write(f"Resolved 'search_on' for '{fruit_chosen}': '{search_on}' (Type: {type(search_on)})")

                # Ensure search_on is a string and not None
                if isinstance(search_on, str) and search_on.strip() != '':
                    st.subheader(fruit_chosen + ' Nutrition Information')
                    try:
                        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
                        if fruityvice_response.status_code == 200:
                            # Added a check for empty JSON response, which can happen for some fruits
                            if fruityvice_response.json():
                                st.dataframe(data=fruityvice_response.json(), use_container_width=True)
                            else:
                                st.warning(f"No nutrition data found for '{fruit_chosen}' from Fruityvice API.")
                        else:
                            st.error(f"Failed to fetch nutrition data for {fruit_chosen}. Status code: {fruityvice_response.status_code}. Response: {fruityvice_response.text}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Error connecting to Fruityvice API for {fruit_chosen}: {e}")
                else:
                    st.warning(f"Invalid or empty 'SEARCH_ON' value for '{fruit_chosen}'. Skipping API call.")
            else:
                st.error(f"Error: 'SEARCH_ON' column not found in DataFrame for '{fruit_chosen}'. Check Snowflake schema and column casing.")
        else:
            st.warning(f"'{fruit_chosen}' not found in fruit options DataFrame. Cannot fetch nutrition info.")
        # --- END CRITICAL DEBUGGING FOR search_on ---


    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, NAME_ON_ORDER)
        VALUES ('{ingredients_string.strip()}', '{name_on_order}')
    """

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

# External API Data Example (this was already outside the loop)
st.subheader("External API Data Example:")
try:
    # This specific call to smoothiefroot.com should ideally be conditional or removed
    # if it's not directly related to user selection.
    # It was causing a NameError before, now it's correctly placed and defined.
    smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
    if smoothiefroot_response.status_code == 200:
        st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
    else:
        st.error(f"Failed to fetch data from custom API. Status code: {smoothiefroot_response.status_code}")
except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the custom API: {e}")

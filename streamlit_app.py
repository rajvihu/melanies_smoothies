# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw,Customize Your Smoothie!:cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom smoothie!.
  """
)

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)
# Establish Snowflake connection
# Make sure your connection is set up correctly in Streamlit secrets or config
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select (col('fruit_name'))
#st.dataframe(data=my_dataframe, use_container_width=True)
ingredients_list = st.multiselect(
    'choose up to 5 ingredients:'
    ,my_dataframe
    ,max_selections=5
)
if ingredients_list:
    ingredients_string =''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ''
        
    #st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients)
            values ('""" + ingredients_string + """','"""+name_on_order+ """')""" 
    #st.write(my_insert_stmt)
    #st.stop()
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
       session.sql(my_insert_stmt).collect()
    st.success('Your Smoothie is ordered!', icon="✅")
# --- Add requests API call here ---
# Make a request to an external API and display its JSON response
st.subheader("External API Data Example:")
try:
    smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
    # Check if the request was successful
    sf_df = st.dataframe(data=smoothiefroot_response.json(),use_container_width=true)

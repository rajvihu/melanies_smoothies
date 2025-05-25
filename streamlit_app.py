# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
# --- ADD THESE TWO LINES RIGHT AFTER THE IMPORT ---
st.write(f"Is 'requests' defined after import? {'requests' in globals()}")
try:
    st.write(f"Type of 'requests' after import: {type(requests)}")
except NameError:
    st.write("`requests` is not defined immediately after import!")

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
#my_dataframe = session.table("smoothies.public.fruit_options").select (col('fruit_name'))
#st.dataframe(data=my_dataframe, use_container_width=True)
my_dataframe = session.table("smoothies.public.fruit_options").select (col('fruit_name'),col('search_on'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

#convert the snowpark dataframe to a pandas  dataframe
pd_df=my_dataframe.to_pandas()
#st.dataframe(pd_pf)
#st.stop()
ingredients_list = st.multiselect(
    'choose up to 5 ingredients:'
    ,my_dataframe
    ,max_selections=5
)
if ingredients_list:
    ingredients_string =''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ''
        search_on=pd_df.loc[pd_df['fruit_name'] == fruit_chosen, 'search_on'].iloc[0]
        #st.write('The search value for ',fruit_chosen,' is ', search_on, '.')
        st.subheader(fruit_chosen + 'Nutrition Information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/"+search_on)
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
        #smoothiefroot_response = requests.get(smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/"+ fruit_chosen)
        #sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)  
    
    #st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients)
            values ('""" + ingredients_string + """','"""+name_on_order+ """')""" 
    #st.write(my_insert_stmt)
    #st.stop()
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
       session.sql(my_insert_stmt).collect()
    st.success('Your Smoothie is ordered!', icon="✅")
#new section to display smoothiefroot.com
#import requests
#smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
#st.text(smoothiefroot_response)
#sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
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

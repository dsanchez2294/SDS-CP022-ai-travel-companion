import streamlit as st
import re
from web_scraper import WebScraper
from travel_agent import TravelAgent

# --- Sidebar Authentication ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

st.sidebar.header("Authentication")

if not st.session_state.authenticated:
    login_method = st.sidebar.radio("Select login method", ["Username/Password", "API Keys"])
    # Retrieve credentials from Streamlit secrets
    DEFAULT_USERNAME = st.secrets["credentials"]["username"]
    DEFAULT_PASSWORD = st.secrets["credentials"]["password"]
    if login_method == "Username/Password":
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            # Replace these with your actual authentication logic.
            if username == DEFAULT_USERNAME and password == DEFAULT_PASSWORD:
                st.session_state.authenticated = True
                st.sidebar.success("Logged in successfully!")
            else:
                st.sidebar.error("Invalid username or password.")
    else:  # API Keys option
        openai_api_key = st.sidebar.text_input("OPENAI_API_KEY", type="password")
        tavily_api_key = st.sidebar.text_input("TAVILY_API_KEY", type="password")
        if st.sidebar.button("Continue without Login"):
            if openai_api_key and tavily_api_key:
                st.session_state.authenticated = True
                st.session_state.openai_api_key = openai_api_key
                st.session_state.tavily_api_key = tavily_api_key
                st.sidebar.success("Using provided API keys!")
            else:
                st.sidebar.error("Please provide both API keys.")
                
    # Stop the app from continuing until authentication is completed.
    if not st.session_state.authenticated:
        st.stop()

# --- Main App ---
st.title("Top Destinations for Travel")

# Initialize session state variables.
if "quit_app" not in st.session_state:
    st.session_state.quit_app = False

if "city_list" not in st.session_state:
    st.session_state.city_list = None

if "selected_city" not in st.session_state:
    st.session_state.selected_city = "Select a city"

if "travel_time" not in st.session_state:
    st.session_state.travel_time = "Anytime"

if "see_tickets" not in st.session_state:
    st.session_state.see_tickets = "N"

if "see_city_desc" not in st.session_state:
    st.session_state.see_city_desc = "N"

# Layout for loading destination data.
col1, col2 = st.columns(2)
with col1:
    if st.button("Find top Destinations from web"):
        scraper = WebScraper()  
        st.session_state.city_list = scraper.extract_ranked_cities()
        st.session_state.selected_city = "Select a city"
        st.session_state.quit_app = False

with col2:
    if st.button("Load cached Destinations"):
        st.session_state.city_list = WebScraper.return_cached_cities()
        st.session_state.selected_city = "Select a city"
        st.session_state.quit_app = False

if not st.session_state.quit_app:
    if st.session_state.city_list:
        # Build radio options including a placeholder.
        city_options = ["Select a city"] + st.session_state.city_list

        # Determine the index for the currently selected city.
        initial_index = city_options.index(st.session_state.selected_city) if st.session_state.selected_city in city_options else 0

        selected_city = st.radio("Choose a city from the list", options=city_options, index=initial_index)
        if selected_city != st.session_state.selected_city:
            st.session_state.selected_city = selected_city

        if st.session_state.selected_city != "Select a city":
            st.write(f"You selected: **{st.session_state.selected_city}**")

            # Option: See more city description.
            see_city_desc_options = ["Y", "N"]
            see_city_desc_selected = st.radio(
                "Do you wish to see more description about this city?",
                see_city_desc_options,
                index=see_city_desc_options.index(st.session_state.see_city_desc)
            )
            st.session_state.see_city_desc = see_city_desc_selected
            st.write(f"You selected: **{st.session_state.see_city_desc}**")

            # Option: Select the travel month.
            travel_time_options = ["Anytime", "January", "February", "March", "April", "May", "June",
                                   "July", "August", "September", "October", "November", "December"]
            travel_time_selected = st.radio(
                "What time of the year do you wish to travel?",
                travel_time_options,
                index=travel_time_options.index(st.session_state.travel_time)
            )
            st.session_state.travel_time = travel_time_selected
            st.write(f"Time of year selected: **{st.session_state.travel_time}**")

            # Option: See airline ticket pricing.
            see_ticket_options = ["Y", "N"]
            see_tickets_selected = st.radio(
                "Do you wish to see air tickets for this trip?",
                see_ticket_options,
                index=see_ticket_options.index(st.session_state.see_tickets)
            )
            st.session_state.see_tickets = see_tickets_selected
            st.write(f"You selected: **{st.session_state.see_tickets}**") 

            # Button to invoke the agent.
            if st.button("Show Details"):
                # Remove ranking (number and hyphen) from the city string.
                city_clean = re.sub(r'^\d+\s*[-]\s*', '', st.session_state.selected_city)
                query = f"City: {city_clean}. "
                if st.session_state.travel_time != "Anytime":
                    query += f"Travel month: {st.session_state.travel_time}. Please provide the weather forecast for that month. "
                if st.session_state.see_city_desc == "Y":
                    query += "Also provide a brief description of the city with points of interest from Wikipedia. "
                if st.session_state.see_tickets == "Y":
                    query += "Additionally, provide the best economy airline ticket pricing information. "
                else:
                    query += "Do not include any airline ticket pricing information. "

                try:
                    agent = TravelAgent()
                    st.write("Invoking agent ...")
                    response = agent.run_query(query)
                    st.subheader("Agent Response")
                    st.write(response)
                except Exception as e:
                    st.error(f"Error initializing or running agent: {e}")

        if st.button("Quit"):
            st.session_state.quit_app = True
    else:
        st.info("Click **Find top Destinations from web** or **Load cached Destinations** to fetch and display the list.")
else:
    st.write("Thanks for using the app!")

import streamlit as st
from datetime import date, timedelta
from main import TravelPlanner

def login():
    st.title("Rajan's AI Travel Itinerary Planner - Login")
    
    # Sidebar selection for login method
    login_method = st.sidebar.radio("Login Method", ["User/Password", "API Keys"])
    
    if login_method == "User/Password":
        st.write("Please log in using your username and password.")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", key="login_up"):
            # Retrieve credentials from streamlit secrets (adjust key names as needed)
            secret_username = st.secrets["credentials"].get("USERNAME")
            secret_password = st.secrets["credentials"].get("PASSWORD")

            #
            if username == secret_username and password == secret_password:
                st.success("Login successful!")
                # Extract API keys from secrets and store in session_state
                st.session_state["OPENAI_API_KEY"] = st.secrets.get("OPENAI_API_KEY")
                st.session_state["TAVILY_API_KEY"] = st.secrets.get("TAVILY_API_KEY")
                st.session_state["logged_in"] = True
                st.rerun(scope="app")
            else:
                st.error("Invalid credentials. Please try again.")
                
    else:  # API Keys mode
        st.write("Please enter your API Keys.")
        openai_key = st.text_input("OPENAI_API_KEY", type="password")
        tavily_key = st.text_input("TAVILY_API_KEY", type="password")
        
        if st.button("Login", key="login_api"):
            if openai_key and tavily_key:
                st.success("Login successful!")
                st.session_state["OPENAI_API_KEY"] = openai_key
                st.session_state["TAVILY_API_KEY"] = tavily_key
                st.session_state["logged_in"] = True
                st.rerun(scope="app")
            else:
                st.error("Both API keys are required.")

def main():
    st.title("Rajan's AI Travel Itinerary Planner ")
    st.write("Login Successful!")  # Debug message

    # Input fields for itinerary details.
    origin = st.text_input("Origin", value="Los Angeles")
    destination = st.text_input("Destination")
    
    # Calendar controls for travel dates.
    start_date = st.date_input("Travel Start Date", value=date.today() + timedelta(days=10))
    end_date = st.date_input("Travel End Date", value=date.today() + timedelta(days=24))

    if st.button("Generate Itinerary"):
        # Validate required fields and date logic.
        if not destination:
            st.error("Destination is required.")
        elif end_date < start_date:
            st.error("End date must be after the start date.")
        else:
            with st.spinner("Generating itinerary..."):
                try:
                    planner = TravelPlanner(st.session_state["OPENAI_API_KEY"], st.session_state["TAVILY_API_KEY"])
                    itinerary = planner.plan_itinerary(origin, destination, start_date, end_date)
                    st.markdown("### Generated Itinerary")
                    st.markdown(itinerary)
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    raise e

if __name__ == "__main__":
    # Initialize session state variable for login status if not already set
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.session_state["logged_in"]:
        main()
    else:
        login()

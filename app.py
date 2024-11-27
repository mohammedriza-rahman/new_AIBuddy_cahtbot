import streamlit as st
import requests
import json
import time
from PIL import Image
import warnings

# Ignore warnings
warnings.filterwarnings("ignore")

# Define API Key and Base URL
API_KEY = "taPxd2jFPxNTTEXZsGAXbRxSgylLsEKi"
API_BASE_URL = "https://oapi.tasking.ai/v1"
MODEL_ID = "X5lMtrEVvhZuirQGg3aflNOW"

# Define profession and domain hierarchies
PROFESSION_DOMAINS = {
    "Teacher": [
        "Mathematics", "Science", "English", "History", "Computer Science", 
        "Primary Education", "Secondary Education", "Special Education", "Other"
    ],
    "Doctor": [
        "General Medicine", "Pediatrics", "Cardiology", "Neurology", "Surgery",
        "Alternative Medicine", "Public Health", "Other"
    ],
    "Engineer": [
        "Civil", "Mechanical", "Electrical", "Software", "Chemical",
        "Robotics", "AI/ML", "Environmental", "Other"
    ],
    "Student": [
        "Arts and Humanities", "Science", "Commerce/Business", "Engineering", 
        "Medical", "Computer Science", "Other"
    ],
    "Other": []
}

# Streamlit interface setup
st.set_page_config(page_title="AI-Buddy Assistant", page_icon="🤖", layout="centered")

# Initialize session state for sidebar visibility
if "sidebar_visible" not in st.session_state:
    st.session_state.sidebar_visible = False

# Sidebar toggle button with the logo in the same row
col1, col2 = st.columns([0.1, 0.9])  # Create two columns for sidebar button and logo
with col1:
    if st.button("☰"):
        st.session_state.sidebar_visible = not st.session_state.sidebar_visible

with col2:
    # Load and display the logo image (resize it if needed)
    img = Image.open("AI Buddy Green Logo.png")  # Make sure this image path is correct
    resized_img = img.resize((400, 150))  # Resize the logo if needed
    st.image(resized_img, caption="AI-Buddy Assistant", use_column_width=False, output_format="PNG")

# Sidebar content based on visibility
if st.session_state.sidebar_visible:
    with st.sidebar:
        st.title("Customize Your Experience")
        # First dropdown - Profession Selection
        profession = st.selectbox(
            "Choose Your Profession",
            ["Select Profession"] + list(PROFESSION_DOMAINS.keys()),
            key="profession_selector"
        )

        # Initialize variables
        selected_profession = None
        selected_domain = None

        # Handle profession selection
        if profession == "Other":
            custom_profession = st.text_input("Please specify your profession")
            if custom_profession:
                selected_profession = custom_profession
        else:
            selected_profession = profession

        # Domain selection
        if profession and profession != "Select Profession":
            if profession == "Other":
                domain = st.text_input("Please specify your domain")
                if domain:
                    selected_domain = domain
            else:
                domain = st.selectbox(
                    "Choose Your Domain",
                    ["Select Domain"] + PROFESSION_DOMAINS[profession],
                    key="domain_selector"
                )

                if domain == "Other":
                    custom_domain = st.text_input("Please specify your domain")
                    if custom_domain:
                        selected_domain = custom_domain
                else:
                    selected_domain = domain

        # Description text area
        description = st.text_area(
            "About you (a short description)", 
            placeholder="Briefly describe your role",
            key="description"
        )

        # Submit button with validation
        if st.button("Submit"):
            if profession == "Select Profession":
                st.error("Please select a profession.")
            elif profession == "Other" and not custom_profession:
                st.error("Please specify your profession.")
            elif not selected_domain or (domain == "Select Domain"):
                st.error("Please select or specify a domain.")
            else:
                # Format the profession details for the chat
                profession_details = f"My profession is {selected_profession} in the {selected_domain} domain"

                # Add input details as a message to chat history
                st.session_state.messages.append({
                    "role": "user",
                    "content": f"{profession_details}. Here's a bit about me: {description}. Tell me how AI-Buddy can help me."
                })

                # Clear the sidebar content
                st.write("Details submitted! You can continue chatting below.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! How can I assist you today?"}
    ]

# Function to make a request to the custom API
def get_chat_response():
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }
    data = {
        "model": MODEL_ID,
        "messages": st.session_state.messages
    }

    try:
        response = requests.post(f"{API_BASE_URL}/chat/completions", headers=headers, json=data)

        if response.status_code == 200:
            response_json = response.json()
            content = response_json["choices"][0]["message"]["content"]

            try:
                content_parsed = json.loads(content)
                return content_parsed["choices"][0]["message"]["content"]
            except json.JSONDecodeError:
                return content
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")

    except Exception as e:
        st.error("Re-enter the prompt")
        print(f"Error: {e}")
        return None

# Function to simulate streaming effect
def display_response_streaming(response_content):
    response_placeholder = st.empty()
    streaming_text = ""
    for char in response_content:
        streaming_text += char
        response_placeholder.write(streaming_text)
        time.sleep(0.05)

# Chat interface - User Input
if prompt := st.chat_input("Type your message"):
    st.session_state.messages.append({"role": "user", "content": prompt})

# Display chat history and generate assistant response
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Generate assistant response if the last message is from the user
if st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_content = get_chat_response()
            if response_content:
                display_response_streaming(response_content)
                st.session_state.messages.append({"role": "assistant", "content": response_content})
            else:
                st.write("Sorry, Re-enter the prompt")

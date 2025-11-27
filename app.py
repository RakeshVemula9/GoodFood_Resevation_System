"""
GoodFoods AI Reservation System - Streamlit Frontend

A conversational AI interface for booking tables at GoodFoods restaurant chain.
Uses llama-3.3-8b via Groq API with Model Context Protocol (MCP) for tool calling.
"""

import streamlit as st
from agent_core import Agent
import json

# Page Configuration
st.set_page_config(
    page_title="🍽️ GoodFoods Reservation Assistant",
    page_icon="🍽️",
    layout="wide"
)

# Custom CSS for Premium GoodFoods Branding
st.markdown("""
<style>
    /* Dark theme with GoodFoods brand colors */
    .stApp {
        background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
        color: #fafafa;
    }
    
    /* Chat messages */
    .stChatMessage {
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 8px;
        background-color: rgba(255, 255, 255, 0.05);
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
        color: white;
        border-radius: 24px;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #f7931e 0%, #ff6b35 100%);
        box-shadow: 0 4px 12px rgba(255, 107, 53, 0.4);
        transform: translateY(-2px);
    }
    
    /* Headers */
    h1 {
        font-family: 'Helvetica Neue', 'Arial', sans-serif;
        font-weight: 700;
        background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    h2, h3 {
        color: #ff6b35;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f2e 0%, #0f1419 100%);
    }
    
    /* Input fields */
    .stTextInput input, .stTextArea textarea {
        background-color: rgba(255, 255, 255, 0.08);
        color: #fafafa;
        border: 1px solid rgba(255, 107, 53, 0.3);
        border-radius: 8px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: rgba(255, 107, 53, 0.1);
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🍽️ GoodFoods Reservation Assistant")

st.markdown("""
<div style='background: linear-gradient(135deg, rgba(255, 107, 53, 0.15) 0%, rgba(247, 147, 30, 0.15) 100%); 
            padding: 20px; border-radius: 12px; margin-bottom: 20px;'>
    <h3 style='margin: 0; color: #ff6b35;'>Welcome to GoodFoods! 🌟</h3>
    <p style='margin: 10px 0 0 0; color: #e0e0e0;'>
        We're a premium casual dining chain with <strong>50+ locations</strong> across India, 
        serving Italian, North Indian, Continental, and Asian Fusion cuisines.
    </p>
    <p style='margin: 5px 0 0 0; color: #b0b0b0; font-size: 0.9em;'>
        💬 Try: <em>"Find a branch in Bangalore" or "Book a romantic table tomorrow evening"</em>
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Configuration
    api_key = st.text_input(
        "Groq API Key",
        value="",
        type="password",
        help="Enter your Groq API key. Get one at https://console.groq.com/"
    )
    
    model_name = st.selectbox(
        "Model",
        options=[
            "llama-3.1-8b-instant",
            "llama3-groq-70b-8192-tool-use-preview",
            "llama-3.3-70b-versatile",
            "mixtral-8x7b-32768"
        ],
        index=0,
        help="llama-3.1-8b-instant is an 8B parameter model (small model as required)"
    )
    
    st.markdown("---")
    
    # About Section
    st.markdown("### 📖 About")
    st.markdown(f"""
    **GoodFoods Reservation System**
    
    - 🤖 **Model**: {model_name}
    - 🔧 **Protocol**: MCP (Model Context Protocol)
    - 🏢 **Branches**: 50+ locations
    - 🌍 **Coverage**: 18+ cities across India
    
    **Features:**
    - ✅ Natural language booking
    - ✅ Intelligent recommendations
    - ✅ Multi-location search
    - ✅ Real-time availability
    """)
    
    # Stats
    try:
        with open('d:/assign/goodfoods_branches.json', 'r', encoding='utf-8') as f:
            branches_data = json.load(f)
            total_branches = len(branches_data)
            total_cities = len(set(b['city'] for b in branches_data))
        
        st.markdown("---")
        st.markdown("### 📊 Network Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Branches", total_branches)
        with col2:
            st.metric("Cities", total_cities)
    except:
        pass
    
    # Reset button
    st.markdown("---")
    if st.button("🔄 Reset Conversation"):
        st.session_state.messages = []
        st.session_state.agent = None
        st.rerun()

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state and api_key:
    try:
        st.session_state.agent = Agent(api_key=api_key, model=model_name)
    except Exception as e:
        st.error(f"Failed to initialize agent: {e}")

# Display Chat History
for message in st.session_state.messages:
    role = message["role"]
    if role == "tool" or role == "system":
        continue  # Skip system and tool messages in UI
    
    content = message.get("content", "")
    
    # Show tool calls in assistant messages
    if role == "assistant" and "tool_calls" in message:
        tool_info = ""
        for tc in message["tool_calls"]:
            tool_info += f"\n\n🔧 *Calling: {tc['function']['name']}*"
        content = tool_info + ("\n\n" + content if content else "")
    
    if content:
        with st.chat_message(role):
            st.markdown(content)

# Chat Input
if prompt := st.chat_input("How can I help you dine today? 🍽️"):
    if not api_key:
        st.error("⚠️ Please enter your Groq API key in the sidebar to continue.")
    else:
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Add to session state
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking... 🤔"):
                try:
                    # Re-initialize agent if config changed
                    if (not hasattr(st.session_state, 'agent') or 
                        st.session_state.agent is None or 
                        st.session_state.agent.api_key != api_key or 
                        st.session_state.agent.model != model_name):
                        st.session_state.agent = Agent(api_key=api_key, model=model_name)
                    
                    # Get response
                    response_text = st.session_state.agent.chat(prompt)
                    st.markdown(response_text)
                    
                    # Sync session state with agent history
                    st.session_state.messages = st.session_state.agent.history
                    
                except Exception as e:
                    error_msg = f"❌ An error occurred: {str(e)}"
                    st.error(error_msg)
                    print(f"Error details: {e}")  # Debug logging

# Debug Panel (Optional)
with st.expander("🔍 Debug: View Branch Data"):
    try:
        with open('d:/assign/goodfoods_branches.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        st.markdown(f"**Total Branches:** {len(data)}")
        
        # Display as searchable dataframe
        import pandas as pd
        df = pd.DataFrame(data)
        
        # Select columns to display
        display_columns = ['id', 'branch_name', 'city', 'locality', 'rating', 'capacity', 'branch_type']
        if all(col in df.columns for col in display_columns):
            st.dataframe(
                df[display_columns],
                use_container_width=True,
                height=400
            )
        else:
            st.dataframe(df, use_container_width=True, height=400)
            
    except Exception as e:
        st.write(f"No branch data found: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; font-size: 0.85em; padding: 20px;'>
    <p>Powered by <strong>llama-3.3-8b</strong> via Groq | Using <strong>Model Context Protocol (MCP)</strong></p>
    <p>GoodFoods © 2025 | Premium Casual Dining Excellence</p>
</div>
""", unsafe_allow_html=True)

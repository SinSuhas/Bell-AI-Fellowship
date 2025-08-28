import streamlit as st
import requests
import pandas as pd
from datetime import date, datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import os

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL","https://18.222.156.181:8000")

# Page configuration
st.set_page_config(
    page_title="Habit Rabbit 🐰",
    page_icon="🐰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #FF6B6B;
        font-size: 3rem;
        margin-bottom: 2rem;
    }
    .habit-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #FF6B6B;
    }
    .completed-habit {
        background-color: #d4edda;
        border-left-color: #28a745;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def make_api_request(endpoint, method="GET", data=None):
    """Make API request with error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to the backend API. Please make sure the FastAPI server is running on http://localhost:8000")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def main():
    # Header
    st.markdown('<h1 class="main-header">🐰 Habit Rabbit</h1>', unsafe_allow_html=True)
    st.markdown("### Track your daily habits and build consistency!")
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 📋 Menu")
        page = st.selectbox("Choose a page", ["🏠 Today's Habits", "📊 Analytics", "⚙️ Manage Habits"])
    
    if page == "🏠 Today's Habits":
        show_today_habits()
    elif page == "📊 Analytics":
        show_analytics()
    elif page == "⚙️ Manage Habits":
        show_manage_habits()

def show_today_habits():
    st.markdown("## 🌅 Today's Habits")
    
    # Get today's habits
    habits = make_api_request("/habits/today")
    
    if habits is None:
        return
    
    if not habits:
        st.info("No habits found. Go to 'Manage Habits' to add your first habit!")
        return
    
    # Display metrics
    completed_count = sum(1 for habit in habits if habit['completed_today'])
    total_count = len(habits)
    completion_rate = (completed_count / total_count * 100) if total_count > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("✅ Completed Today", completed_count)
    with col2:
        st.metric("📝 Total Habits", total_count)
    with col3:
        st.metric("📈 Completion Rate", f"{completion_rate:.1f}%")
    
    st.markdown("---")
    
    # Display habits
    for habit in habits:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                status_emoji = "✅" if habit['completed_today'] else "⭕"
                st.markdown(f"**{status_emoji} {habit['name']}**")
                if habit['description']:
                    st.caption(habit['description'])
            
            with col2:
                button_text = "Mark Incomplete" if habit['completed_today'] else "Mark Complete"
                button_type = "secondary" if habit['completed_today'] else "primary"
                
                if st.button(button_text, key=f"toggle_{habit['id']}", type=button_type):
                    result = make_api_request(f"/habits/{habit['id']}/complete", method="POST")
                    if result:
                        st.success(result['message'])
                        st.rerun()
        
        st.markdown("---")

def show_analytics():
    st.markdown("## 📊 Analytics & Progress")
    
    # Get all habits for analytics
    habits = make_api_request("/habits/")
    
    if habits is None or not habits:
        st.info("No habits found. Add some habits first to see analytics!")
        return
    
    # Habit selection for detailed view
    selected_habit = st.selectbox("Select a habit for detailed analytics", 
                                 options=habits, 
                                 format_func=lambda x: x['name'])
    
    if selected_habit:
        # Get habit history
        history = make_api_request(f"/habits/{selected_habit['id']}/history")
        
        if history:
            # Create DataFrame for visualization
            df = pd.DataFrame(history)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Completion trend chart
            fig = px.line(df, x='date', y='completed', 
                         title=f"Completion Trend for '{selected_habit['name']}'",
                         labels={'completed': 'Completed', 'date': 'Date'})
            fig.update_traces(mode='markers+lines')
            st.plotly_chart(fig, use_container_width=True)
            
            # Weekly completion rate
            df['week'] = df['date'].dt.to_period('W')
            weekly_stats = df.groupby('week')['completed'].agg(['sum', 'count']).reset_index()
            weekly_stats['completion_rate'] = (weekly_stats['sum'] / weekly_stats['count'] * 100).round(1)
            
            if len(weekly_stats) > 0:
                fig2 = px.bar(weekly_stats, x='week', y='completion_rate',
                             title="Weekly Completion Rate (%)",
                             labels={'completion_rate': 'Completion Rate (%)', 'week': 'Week'})
                st.plotly_chart(fig2, use_container_width=True)
            
            # Statistics
            total_days = len(df)
            completed_days = df['completed'].sum()
            completion_percentage = (completed_days / total_days * 100) if total_days > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Days Tracked", total_days)
            with col2:
                st.metric("Days Completed", completed_days)
            with col3:
                st.metric("Overall Completion", f"{completion_percentage:.1f}%")

def show_manage_habits():
    st.markdown("## ⚙️ Manage Your Habits")
    
    # Add new habit section
    with st.expander("➕ Add New Habit", expanded=False):
        with st.form("add_habit"):
            habit_name = st.text_input("Habit Name *", placeholder="e.g., Drink 8 glasses of water")
            habit_description = st.text_area("Description (Optional)", 
                                           placeholder="e.g., Stay hydrated throughout the day")
            
            if st.form_submit_button("Add Habit", type="primary"):
                if habit_name.strip():
                    data = {"name": habit_name.strip(), "description": habit_description.strip()}
                    result = make_api_request("/habits/", method="POST", data=data)
                    if result:
                        st.success(f"✅ Added habit: {habit_name}")
                        st.rerun()
                else:
                    st.error("Please enter a habit name!")
    
    # List existing habits
    st.markdown("### 📋 Current Habits")
    habits = make_api_request("/habits/")
    
    if habits is None:
        return
    
    if not habits:
        st.info("No habits yet. Add your first habit above! 🐰")
        return
    
    for habit in habits:
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"**{habit['name']}**")
                if habit['description']:
                    st.caption(habit['description'])
                st.caption(f"Created: {habit['created_date']}")
            
            with col2:
                if st.button("🗑️ Delete", key=f"delete_{habit['id']}", type="secondary"):
                    result = make_api_request(f"/habits/{habit['id']}", method="DELETE")
                    if result:
                        st.success("Habit deleted!")
                        st.rerun()
        
        st.markdown("---")

if __name__ == "__main__":
    main()

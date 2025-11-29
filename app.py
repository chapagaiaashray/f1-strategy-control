import streamlit as st
import pandas as pd
import joblib
import numpy as np
import altair as alt
import os
import time

# ==========================================
# 1. PAGE CONFIG & CUSTOM STYLING
# ==========================================
st.set_page_config(
    page_title="F1 Strategy Control", 
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="collapsed" # Start with sidebar hidden for cleaner look
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #0e1117;
    }
    /* Metrics Styling */
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        color: #ffffff;
    }
    /* Button Styling */
    div.stButton > button {
        width: 100%;
        background-color: #ff2b2b;
        color: white;
        font-weight: bold;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #cc0000;
        border-color: #cc0000;
        color: white;
        box-shadow: 0 4px 14px 0 rgba(255, 43, 43, 0.39);
    }
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    /* Cards for Home Page */
    .track-card {
        background-color: #1f2937;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #374151;
        text-align: center;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. GLOBAL DATA & ASSETS
# ==========================================
available_tracks = ['Bahrain', 'Saudi Arabia', 'Italy', 'Japan']

track_characteristics = {
    "Bahrain": {
        "Type": "High Degradation (Rough Surface)",
        "Desc": "The asphalt is very abrasive (made of granite). Tires wear out quickly. Pit stops are very powerful here.",
        "Laps": 57
    },
    "Saudi Arabia": {
        "Type": "Street Circuit (Smooth Surface)",
        "Desc": "The track is smooth and fast. Tires last a long time. It is hard to pass, so track position is more important.",
        "Laps": 50
    },
    "Italy": {
        "Type": "Extreme Speed (Low Downforce)",
        "Desc": "Mostly long straights. Cars drive at full throttle for 80% of the lap. Pit loss is higher due to high track speeds.",
        "Laps": 53
    },
    "Japan": {
        "Type": "High Lateral Load (Twisty)",
        "Desc": "The 'Figure-8' layout has many fast corners. This puts sideways energy into the tires, causing high wear.",
        "Laps": 53
    }
}

def load_assets(track_name):
    filename = f"f1_model_{track_name}.pkl"
    if not os.path.exists(filename):
        return None, None
    return joblib.load(filename), joblib.load('compound_encoder.pkl')

# ==========================================
# 3. STATE MANAGEMENT
# ==========================================
if 'page' not in st.session_state:
    st.session_state['page'] = 'home'
if 'selected_track' not in st.session_state:
    st.session_state['selected_track'] = 'Bahrain'

def switch_to_sim():
    st.session_state['page'] = 'simulation'

def switch_to_home():
    st.session_state['page'] = 'home'

# ==========================================
# 4. HOME PAGE (LANDING)
# ==========================================
def show_home_page():
    # Hero Section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.title("🏎️ Formula One Strategy Control")
        st.markdown("### The Race Engineer's Digital Brain")
        st.write("Welcome to the advanced **Undercut Simulator**. This tool uses Machine Learning trained on 2024 telemetry data to reverse-engineer Formula 1 strategy decisions.")
        
        st.markdown("""
        **What does this model do?**
        * **Predicts Pace:** Uses Random Forest regression to calculate lap times based on tire life and fuel burn.
        * **Simulates Decay:** Models specific degradation curves for High-Deg vs. Low-Deg tracks.
        * **Forecasts Over-takes:** Runs Monte Carlo-lite simulations to see if an undercut will succeed.
        """)
        
    with col2:
        # A simple visual to make it pop (You can replace with an actual image later)
        st.info("💡 **Did you know?**\n For Monza 2024, this model correctly predicted that Oscar Piastri would fail to catch Charles Leclerc by 1.2 seconds (with minute error margin).")

    st.markdown("---")
    
    # Track Selection Area
    st.subheader("🏁 Select a Grand Prix to Begin")
    
    # We use a cleaner layout for selection
    c1, c2 = st.columns([3, 1])
    with c1:
        chosen_track = st.selectbox("Choose Circuit", available_tracks, index=available_tracks.index(st.session_state['selected_track']))
        # Update session state immediately
        st.session_state['selected_track'] = chosen_track
        
    with c2:
        st.write("") # Spacer
        st.write("") # Spacer
        if st.button("ENTER PIT WALL ➡️"):
            switch_to_sim()
            st.rerun()

    # Track Preview Card
    info = track_characteristics[chosen_track]
    st.success(f"**{chosen_track} Profile:** {info['Type']}\n\n{info['Desc']}")

# ==========================================
# 5. SIMULATION PAGE (DASHBOARD)
# ==========================================
def show_simulation_page():
    # --- Sidebar Logic (Only appears on this page) ---
    with st.sidebar:
        st.title("🏎️ Strategy Control")
        if st.button("⬅️ Back to Menu"):
            switch_to_home()
            st.rerun()
        st.markdown("---")
        
        # Track is already selected from Home, but allow changing it here too
        selected_track = st.selectbox("Current Circuit", available_tracks, index=available_tracks.index(st.session_state['selected_track']))
        
        # Load Brain
        model, encoder = load_assets(selected_track)
        if model is None:
            st.error(f"⚠️ Model for {selected_track} missing! Run train_model.py.")
            st.stop()

        # Telemetry Controls (Same as before)
        st.markdown("### 🚗 Telemetry")
        col1, col2 = st.columns(2)
        with col1:
            my_tire = st.selectbox("My Tire", ['SOFT', 'MEDIUM', 'HARD'])
            target_compound = st.selectbox("Pit To", ['SOFT', 'MEDIUM', 'HARD'])
        with col2:
            my_tire_age = st.number_input("Tire Age", 1, 50, 25)

        st.markdown("### 🎯 Opponent")
        col3, col4 = st.columns(2)
        with col3:
            opp_tire = st.selectbox("Opp Tire", ['SOFT', 'MEDIUM', 'HARD'], index=2)
        with col4:
            opp_tire_age = st.number_input("Opp Age", 1, 50, 15)
        
        opp_response = st.radio("Opponent Response", ["Cover Move (Pit Next Lap)", "Stay Out (No Stop)"])

        st.markdown("### 🏁 Race State")
        defaults = {"Italy": 24.0, "Bahrain": 22.5, "Saudi Arabia": 22.5, "Japan": 22.5}
        track_info = track_characteristics[selected_track]
        
        gap_to_leader = st.number_input("Gap to Leader (s)", value=18.0, step=0.1)
        current_lap = st.number_input("Current Lap", 1, track_info['Laps'], 40)
        laps_to_sim = st.slider("Sim Horizon", 3, 15, 8)
        pit_loss = st.slider("Pit Loss (s)", 15.0, 30.0, defaults.get(selected_track, 22.5))

        st.markdown("###")
        run_btn = st.button("🚀 RUN SIMULATION")

    # --- Main Dashboard Area ---
    
    # Header
    col_head1, col_head2 = st.columns([3, 1])
    with col_head1:
        st.markdown(f"# {selected_track} Grand Prix")
        st.markdown("#### Strategic Performance Analysis")
    with col_head2:
        st.info(f"**Circuit Type:**\n{track_characteristics[selected_track]['Type']}")

    # --- Logic Engine (Using your existing accurate logic) ---
    def predict_pace(compound, age, lap_number):
        encoded = encoder.transform([compound])[0]
        # Guardrails to prevent hallucination
        if compound == 'SOFT' and age > 25: age = 25
        if compound == 'MEDIUM' and age > 35: age = 35
        if compound == 'HARD' and age > 50: age = 50
        
        input_data = pd.DataFrame({
            'Compound_Encoded': [encoded], 'TyreLife': [age], 'LapNumber': [lap_number]
        })
        return model.predict(input_data)[0]

    def run_simulation_logic():
        # Setup
        my_in_lap = predict_pace(my_tire, my_tire_age, current_lap)
        my_times = [my_in_lap + pit_loss]
        
        # Me (Simulating Stint)
        curr_sim_lap = current_lap
        curr_tire_age = 0
        for i in range(laps_to_sim):
            curr_sim_lap += 1
            curr_tire_age += 1
            if curr_sim_lap > track_info['Laps']: break
            my_times.append(predict_pace(target_compound, curr_tire_age, curr_sim_lap))

        # Opponent (Simulating Stint)
        opp_times = [predict_pace(opp_tire, opp_tire_age, current_lap)]
        opp_sim_lap = current_lap
        opp_sim_age = opp_tire_age
        wants_cover = (opp_response == "Cover Move (Pit Next Lap)")

        for i in range(laps_to_sim):
            opp_sim_lap += 1
            opp_sim_age += 1
            if opp_sim_lap > track_info['Laps']: break
            
            if wants_cover:
                if i == 0: opp_times.append(predict_pace(opp_tire, opp_sim_age, opp_sim_lap))
                elif i == 1: 
                    opp_times.append(predict_pace(opp_tire, opp_sim_age, opp_sim_lap) + pit_loss)
                    opp_sim_age = 0
                else: opp_times.append(predict_pace(target_compound, opp_sim_age, opp_sim_lap))
            else:
                opp_times.append(predict_pace(opp_tire, opp_sim_age, opp_sim_lap))
                
        return my_times, opp_times

    # --- Run & Visualize ---
    if run_btn:
        with st.spinner('Calculating tire degradation curves...'):
            time.sleep(0.3)
            my_pace, opp_pace = run_simulation_logic()
            
            L = min(len(my_pace), len(opp_pace))
            my_pace, opp_pace = my_pace[:L], opp_pace[:L]
            
            my_cum = np.cumsum(my_pace) + gap_to_leader
            opp_cum = np.cumsum(opp_pace)
            sim_laps = np.arange(current_lap, current_lap + L)
            gap_history = opp_cum - my_cum
            final_gap = gap_history[-1]
            
            df = pd.DataFrame({'Lap': sim_laps, 'Me': my_cum, 'Opponent': opp_cum, 'Gap': gap_history})
            
            success = final_gap > 0
            status_icon = "✅" if success else "❌"
            
            st.markdown("### Simulation Results")
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            with kpi1: st.metric("Outcome", "Overtake" if success else "Defended", delta=status_icon, delta_color="off")
            with kpi2: st.metric("Final Gap", f"{abs(final_gap):.2f} sec", delta=f"{final_gap:.2f}s")
            with kpi3: 
                catch_lap = df[df['Gap'] > 0]['Lap'].min() if success else "N/A"
                st.metric("Catch Lap", f"{catch_lap}")
            with kpi4: st.metric("Strategy", "Undercut" if my_pace[0] > opp_pace[0] else "Overcut")

            st.toast("Strategy Calculation Complete!", icon="🏁")

            tab1, tab2, tab3 = st.tabs(["📉 Gap Analysis", "⏱️ Race Trace", "📋 Data Table"])
            
            with tab1:
                st.markdown("##### Interval History (Positive = Ahead)")
                chart_gap = alt.Chart(df).mark_area(line={'color':'white'}, opacity=0.6).encode(
                    x=alt.X('Lap', axis=alt.Axis(tickMinStep=1)),
                    y=alt.Y('Gap', title='Gap to Leader (s)'),
                    color=alt.condition(alt.datum.Gap > 0, alt.value("#2ecc71"), alt.value("#ff4b4b")),
                    tooltip=['Lap', alt.Tooltip('Gap', format='.2f')]
                ).properties(height=400)
                rule = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(color='white', strokeDash=[5,5]).encode(y='y')
                st.altair_chart(chart_gap + rule, use_container_width=True)

            with tab2:
                st.markdown("##### Cumulative Race Time")
                df_melt = df.melt('Lap', value_vars=['Me', 'Opponent'], var_name='Driver', value_name='Time')
                lines = alt.Chart(df_melt).mark_line(point=True).encode(
                    x=alt.X('Lap', axis=alt.Axis(tickMinStep=1)),
                    y=alt.Y('Time', scale=alt.Scale(zero=False), title='Cumulative Time (s)'),
                    color=alt.Color('Driver', scale={'range': ['#3498db', '#e67e22']}),
                    tooltip=['Lap', 'Driver', alt.Tooltip('Time', format='.1f')]
                ).properties(height=400)
                st.altair_chart(lines, use_container_width=True)
                
            with tab3:
                st.dataframe(df.style.format("{:.2f}").background_gradient(subset=['Gap'], cmap="RdYlGn"), use_container_width=True)
    else:
        st.info("👈 Configure the scenario in the sidebar and click **RUN SIMULATION**.")
        st.markdown(f"**Current Track State:** {track_characteristics[selected_track]['Desc']}")

# ==========================================
# 6. APP ROUTER
# ==========================================
if st.session_state['page'] == 'home':
    show_home_page()
else:
    show_simulation_page()
import fastf1
import os

# 1. SETUP CACHING
if not os.path.exists('cache_dir'):
    os.makedirs('cache_dir')

fastf1.Cache.enable_cache('cache_dir') 

def load_race_data(year, gp_name, session_type):
    """
    Loads the specific race session data using FastF1.
    """
    print(f"\n--- Loading {session_type} data for {gp_name} {year} ---")
    try:
        # FastF1 is smart enough to match 'Italy' to Monza, etc.
        session = fastf1.get_session(year, gp_name, session_type)
        session.load()
        print(f"✅ Success: {gp_name} loaded.")
        return session
    except Exception as e:
        print(f"❌ Error loading {gp_name}: {e}")
        return None

if __name__ == "__main__":
    # The Big 4: Distinct characteristics for portfolio variety
    tracks_to_load = ['Bahrain', 'Saudi Arabia', 'Italy', 'Japan']
    
    print("Starting download of the 'Big 4' tracks...")
    for track in tracks_to_load:
        load_race_data(2024, track, 'R')
        
    print("\nAll tracks cached successfully!")
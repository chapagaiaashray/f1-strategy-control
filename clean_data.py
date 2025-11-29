import fastf1
import pandas as pd
import os

# Enable cache again so we don't re-download everything
fastf1.Cache.enable_cache('cache_dir') 

def get_clean_data(year, gp_name, session_type):
    print(f"Loading raw data for {gp_name} {year}...")
    session = fastf1.get_session(year, gp_name, session_type)
    session.load()
    
    # Get all laps
    laps = session.laps
    
    # --- STEP 1: DROP NON-RACING LAPS ---
    # pick_track_status('1') keeps only 'Green Flag' (normal racing)
    # pick_quicklaps() removes outliers (extremely slow laps)
    # pick_wo_box() removes In-laps and Out-laps (entering/leaving pits)
    racing_laps = laps.pick_track_status('1').pick_quicklaps().pick_wo_box()
    
    # --- STEP 2: CONVERT LAP TIME TO SECONDS ---
    # Currently LapTime is a "Timedelta" (0 days 00:01:30). 
    # Machines hate Timedeltas. We need Seconds (90.0).
    racing_laps['LapTimeSeconds'] = racing_laps['LapTime'].dt.total_seconds()
    
    # --- STEP 3: KEEP ONLY USEFUL COLUMNS ---
    # We don't need 'Sector1Time' or 'SpeedI1' for our basic model yet.
    # We DO need TyreLife (how old tires are) and Compound (Soft/Med/Hard).
    cols_to_keep = [
        'Driver', 'LapNumber', 'LapTimeSeconds', 
        'Compound', 'TyreLife', 'FreshTyre', 'Team'
    ]
    
    # Create a clean DataFrame
    clean_df = racing_laps[cols_to_keep].copy()
    
    # Drop any rows that still have missing values (NaN)
    clean_df = clean_df.dropna()
    
    return clean_df

if __name__ == "__main__":
    # processing Bahrain again
    df = get_clean_data(2024, 'Bahrain', 'R')
    
    print("\nData Cleaning Complete!")
    print(f"Total laps kept: {len(df)}")
    print("\nFirst 5 rows of Clean Data:")
    print(df.head())
    
    # Checking tire compounds
    print("\nTire Compounds used:")
    print(df['Compound'].value_counts())
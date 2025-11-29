import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import LabelEncoder
import joblib 
from clean_data import get_clean_data 

# The same list as ingest_data
TRACKS = ['Bahrain', 'Saudi Arabia', 'Italy', 'Japan']

def train_and_save_model(gp_name):
    print(f"\n--- Training Model for {gp_name} ---")
    
    # 1. GET DATA
    # We use a try/except block in case one download failed
    try:
        df = get_clean_data(2024, gp_name, 'R')
    except Exception as e:
        print(f"Skipping {gp_name}: Could not load clean data. ({e})")
        return

    # 2. PREPARE FEATURES
    le = LabelEncoder()
    le.fit(['HARD', 'MEDIUM', 'SOFT'])
    df['Compound_Encoded'] = le.transform(df['Compound'])
    
    # Save encoder (overwriting is fine, it's the same logic for all)
    joblib.dump(le, 'compound_encoder.pkl')
    
    features = ['Compound_Encoded', 'TyreLife', 'LapNumber']
    target = 'LapTimeSeconds'
    
    X = df[features]
    y = df[target]
    
    # 3. SPLIT & TRAIN
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # 4. EVALUATE
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    print(f"MAE for {gp_name}: {mae:.3f} seconds")
    
    # 5. SAVE
    # We save as 'f1_model_Italy.pkl', 'f1_model_Japan.pkl', etc.
    filename = f"f1_model_{gp_name}.pkl"
    joblib.dump(model, filename)
    print(f"Saved to {filename}")

if __name__ == "__main__":
    for track in TRACKS:
        train_and_save_model(track)
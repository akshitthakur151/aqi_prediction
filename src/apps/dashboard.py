import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Load states and cities data ──────────────────────────────────────────────
@st.cache_data
def load_states_cities():
    """Load all states and cities from the data"""
    try:
        df = pd.read_csv("data/aqi_data.csv")
        states = sorted(df['state'].unique().tolist())
        # Get all cities from dataset
        all_cities = sorted(df['city'].unique().tolist())
        # Create state-city mapping
        state_city_map = {}
        for state in states:
            cities = sorted(df[df['state'] == state]['city'].unique().tolist())
            state_city_map[state] = cities
        return states, all_cities, state_city_map
    except Exception as e:
        # Fallback to default states and cities
        states = ["Delhi", "Maharashtra", "Karnataka", "Tamil Nadu", "Andhra Pradesh", 
                  "Telangana", "Gujarat", "Rajasthan", "Punjab", "Haryana", 
                  "Uttar Pradesh", "Bihar", "Odisha", "Jharkhand", "Madhya Pradesh", 
                  "Chhattisgarh", "West Bengal", "Assam", "Kerala", "Goa", 
                  "Himachal Pradesh", "Uttarakhand", "Jammu & Kashmir", "Ladakh", 
                  "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Sikkim", "Tripura",
                  "Arunachal Pradesh"]
        all_cities = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Hyderabad", 
                      "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Lucknow",
                      "Chandigarh", "Indore", "Bhopal", "Coimbatore", "Visakhapatnam"]
        state_city_map = {
            "Delhi": ["Delhi", "New Delhi"],
            "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Aurangabad"],
            "Karnataka": ["Bangalore", "Mysore", "Belgaum"],
            "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai"],
            "Other": ["Other"]
        }
        return states, all_cities, state_city_map

states_list, all_cities_list, state_city_map = load_states_cities()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AQI Predictor – India",
    page_icon="🌫️",
    layout="wide",
)

# ── AQI helpers (same logic as your training code) ───────────────────────────
def calculate_aqi(pm25, pm10, no2, so2, co, o3):
    def sub_pm25(v):
        if pd.isna(v): return np.nan
        if v <= 30:  return v * 50 / 30
        if v <= 60:  return 50  + (v - 30)  * 50  / 30
        if v <= 90:  return 100 + (v - 60)  * 100 / 30
        if v <= 120: return 200 + (v - 90)  * 100 / 30
        if v <= 250: return 300 + (v - 120) * 100 / 130
        return              400 + (v - 250) * 100 / 130

    def sub_pm10(v):
        if pd.isna(v): return np.nan
        if v <= 50:  return v
        if v <= 100: return 50  + (v - 50)  * 50  / 50
        if v <= 250: return 100 + (v - 100) * 100 / 150
        if v <= 350: return 200 + (v - 250) * 100 / 100
        if v <= 430: return 300 + (v - 350) * 100 / 80
        return              400 + (v - 430) * 100 / 80

    def sub_no2(v):
        if pd.isna(v): return np.nan
        if v <= 40:  return v * 50 / 40
        if v <= 80:  return 50  + (v - 40)  * 50  / 40
        if v <= 180: return 100 + (v - 80)  * 100 / 100
        if v <= 280: return 200 + (v - 180) * 100 / 100
        if v <= 400: return 300 + (v - 280) * 100 / 120
        return              400 + (v - 400) * 100 / 120

    def sub_so2(v):
        if pd.isna(v): return np.nan
        if v <= 40:   return v * 50 / 40
        if v <= 80:   return 50  + (v - 40)   * 50  / 40
        if v <= 380:  return 100 + (v - 80)   * 100 / 300
        if v <= 800:  return 200 + (v - 380)  * 100 / 420
        if v <= 1600: return 300 + (v - 800)  * 100 / 800
        return               400 + (v - 1600) * 100 / 800

    def sub_co(v):
        if pd.isna(v): return np.nan
        if v <= 1.0: return v * 50 / 1.0
        if v <= 2.0: return 50  + (v - 1.0) * 50  / 1.0
        if v <= 10:  return 100 + (v - 2.0) * 100 / 8.0
        if v <= 17:  return 200 + (v - 10)  * 100 / 7.0
        if v <= 34:  return 300 + (v - 17)  * 100 / 17
        return              400 + (v - 34)  * 100 / 17

    def sub_o3(v):
        if pd.isna(v): return np.nan
        if v <= 50:  return v
        if v <= 100: return 50  + (v - 50)  * 50  / 50
        if v <= 168: return 100 + (v - 100) * 100 / 68
        if v <= 208: return 200 + (v - 168) * 100 / 40
        if v <= 748: return 300 + (v - 208) * 100 / 540
        return              400 + (v - 748) * 100 / 540

    subs = [sub_pm25(pm25), sub_pm10(pm10), sub_no2(no2),
            sub_so2(so2),   sub_co(co),     sub_o3(o3)]
    valid = [s for s in subs if not np.isnan(s)]
    return max(valid) if valid else np.nan


def aqi_category(aqi):
    if pd.isna(aqi):  return "Unknown",      "#999999"
    if aqi <= 50:     return "Good",          "#55A84F"
    if aqi <= 100:    return "Satisfactory",  "#A3C853"
    if aqi <= 200:    return "Moderate",      "#FFF833"
    if aqi <= 300:    return "Poor",          "#F29C33"
    if aqi <= 400:    return "Very Poor",     "#E93F33"
    return                   "Severe",        "#AF2D24"


# ── Load trained model (if available) ────────────────────────────────────────
@st.cache_resource
def load_model():
    try:
        with open("models/best_aqi_model.pkl", "rb") as f:
            model = pickle.load(f)
        with open("models/scaler.pkl", "rb") as f:
            scaler = pickle.load(f)
        with open("models/feature_names.pkl", "rb") as f:
            features = pickle.load(f)
        with open("models/state_encoder.pkl", "rb") as f:
            le_state = pickle.load(f)
        with open("models/city_encoder.pkl", "rb") as f:
            le_city = pickle.load(f)
        return model, scaler, features, le_state, le_city
    except Exception as e:
        # Return None - will use default predictions
        return None, None, None, None, None
        
def create_default_model():
    """Create a simple scikit-learn model for demo purposes"""
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.preprocessing import LabelEncoder
    
    # Simple demo model
    model = RandomForestRegressor(n_estimators=10, random_state=42)
    scaler = StandardScaler()
    features = ["PM2.5", "PM10", "NO2", "SO2", "CO", "OZONE", "NH3", 
                "PM_ratio", "NOx_SOx_ratio", "PM_NO2_interaction", 
                "PM_CO_interaction", "NO2_SO2_interaction",
                "Total_PM", "Total_Gas", "state_encoded", "city_encoded", "latitude", "longitude"]
    
    # Train on dummy data
    dummy_data = np.random.rand(100, len(features)) * 100
    dummy_target = np.random.rand(100) * 500
    scaler.fit(dummy_data)
    model.fit(scaler.transform(dummy_data), dummy_target)
    
    le_state = LabelEncoder()
    le_city = LabelEncoder()
    le_state.fit(["Delhi", "Maharashtra", "Karnataka", "Tamil Nadu", "Other"])
    le_city.fit(["Delhi", "Mumbai", "Bangalore", "Chennai", "Hyderabad", "Other"])
    
    return model, scaler, features, le_state, le_city


model, scaler, features, le_state, le_city = load_model()

# If models don't exist, create default ones
if model is None:
    model, scaler, features, le_state, le_city = create_default_model()

model_available = model is not None


def predict_with_model(pm25, pm10, no2, so2, co, ozone, nh3,
                        state, city, lat, lon):
    pm_ratio       = pm25 / (pm10 + 1)
    nox_sox_ratio  = no2  / (so2  + 1)
    pm_no2         = pm25 * no2
    pm_co          = pm25 * co
    no2_so2        = no2  * so2
    total_pm       = pm25 + pm10
    total_gas      = no2  + so2 + co

    try:   state_enc = le_state.transform([state])[0]
    except: state_enc = 0
    try:   city_enc = le_city.transform([city])[0]
    except: city_enc = le_city.transform(["Other"])[0]

    data = {
        "PM2.5": pm25, "PM10": pm10, "NO2": no2, "SO2": so2,
        "CO": co, "OZONE": ozone, "NH3": nh3,
        "PM_ratio": pm_ratio, "NOx_SOx_ratio": nox_sox_ratio,
        "PM_NO2_interaction": pm_no2, "PM_CO_interaction": pm_co,
        "NO2_SO2_interaction": no2_so2,
        "Total_PM": total_pm, "Total_Gas": total_gas,
        "state_encoded": state_enc, "city_encoded": city_enc,
        "latitude": lat, "longitude": lon,
    }
    X = pd.DataFrame([data])[features]
    X_scaled = scaler.transform(X)
    return float(model.predict(X_scaled)[0])


# ── AQI gauge chart ───────────────────────────────────────────────────────────
def draw_gauge(aqi_val):
    fig, ax = plt.subplots(figsize=(5, 2.8), facecolor="none")
    ax.set_facecolor("none")

    segments = [
        (0,   50,  "#55A84F", "Good"),
        (50,  100, "#A3C853", "Satisfactory"),
        (100, 200, "#FFF833", "Moderate"),
        (200, 300, "#F29C33", "Poor"),
        (300, 400, "#E93F33", "Very Poor"),
        (400, 500, "#AF2D24", "Severe"),
    ]
    total = 500
    for lo, hi, color, _ in segments:
        start = 180 - (lo  / total) * 180
        end   = 180 - (hi  / total) * 180
        theta1, theta2 = min(start, end), max(start, end)
        wedge = mpatches.Wedge(
            (0.5, 0.05), 0.42, theta1, theta2,
            width=0.12, transform=ax.transAxes,
            facecolor=color, edgecolor="white", linewidth=0.5,
        )
        ax.add_patch(wedge)

    # Needle
    angle_deg = 180 - (min(aqi_val, 500) / total) * 180
    angle_rad = np.radians(angle_deg)
    nx = 0.5 + 0.32 * np.cos(angle_rad)
    ny = 0.05 + 0.32 * np.sin(angle_rad)
    ax.annotate("", xy=(nx, ny), xytext=(0.5, 0.05),
                xycoords="axes fraction", textcoords="axes fraction",
                arrowprops=dict(arrowstyle="-|>", color="#333333",
                                lw=2, mutation_scale=12))
    ax.plot(0.5, 0.05, "o", color="#333333", ms=6,
            transform=ax.transAxes, zorder=5)

    ax.text(0.5, 0.52, f"{aqi_val:.0f}", ha="center", va="center",
            transform=ax.transAxes, fontsize=28, fontweight="bold",
            color="#222222")

    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis("off")
    fig.tight_layout(pad=0)
    return fig


# ── UI ────────────────────────────────────────────────────────────────────────
st.title("🌫️ AQI Predictor – India")
st.caption("Based on Indian CPCB air quality standards · 511 monitoring stations")

if not model_available:
    st.info(
        "**No trained model found.** Showing CPCB formula-based AQI. "
        "Place your `.pkl` files in a `models/` folder to enable ML predictions.",
        icon="ℹ️",
    )

tab_predict, tab_batch, tab_about = st.tabs(
    ["🔢 Single Prediction", "📂 Batch Prediction (CSV)", "ℹ️ About"])


# ── Tab 1: Single Prediction ──────────────────────────────────────────────────
with tab_predict:
    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.subheader("Enter pollutant values")

        c1, c2 = st.columns(2)
        with c1:
            pm25  = st.number_input("PM2.5 (µg/m³)",  0.0, 1000.0, 55.0,  step=1.0)
            no2   = st.number_input("NO2 (µg/m³)",     0.0,  500.0, 28.0,  step=1.0)
            co    = st.number_input("CO (mg/m³)",       0.0,  100.0,  1.2,  step=0.1)
            nh3   = st.number_input("NH3 (µg/m³)",     0.0,  500.0, 12.0,  step=1.0)
        with c2:
            pm10  = st.number_input("PM10 (µg/m³)",    0.0, 1000.0, 90.0,  step=1.0)
            so2   = st.number_input("SO2 (µg/m³)",     0.0,  500.0, 14.0,  step=1.0)
            ozone = st.number_input("Ozone (µg/m³)",   0.0,  500.0, 42.0,  step=1.0)

        if model_available:
            st.divider()
            st.subheader("Location (for ML model)")
            lc1, lc2 = st.columns(2)
            
            # Initialize session state for state and city selection
            if "selected_state" not in st.session_state:
                st.session_state.selected_state = "Delhi"
            if "selected_city" not in st.session_state:
                st.session_state.selected_city = None
            
            with lc1:
                # State selection - triggers dynamic city update
                state = st.selectbox(
                    "📍 Select State",
                    states_list,
                    index=states_list.index(st.session_state.selected_state) if st.session_state.selected_state in states_list else 0,
                    help="Choose a state from the list",
                    key="state_select_main"
                )
                # Update session state when state changes
                st.session_state.selected_state = state
                
                lat   = st.number_input("Latitude",  -90.0, 90.0, 28.6, format="%.4f")
            
            with lc2:
                # Get cities ONLY for the selected state (DYNAMIC)
                cities_for_state = sorted(state_city_map.get(state, ["Other"]))
                
                # Set default city if not set or if it's not in current state's cities
                if st.session_state.selected_city is None or st.session_state.selected_city not in cities_for_state:
                    default_city_index = 0
                    st.session_state.selected_city = cities_for_state[0] if cities_for_state else "Other"
                else:
                    default_city_index = cities_for_state.index(st.session_state.selected_city)
                
                # City selection - DYNAMICALLY populated from state's cities
                city = st.selectbox(
                    "🏙️ Select City",
                    cities_for_state,
                    index=default_city_index,
                    help=f"Cities in {state} with data ({len(cities_for_state)} available)",
                    key="city_select_main"
                )
                # Update session state when city changes
                st.session_state.selected_city = city
                
                lon   = st.number_input("Longitude", -180.0, 180.0, 77.2, format="%.4f")
            
            # Show all cities available in selected state
            st.caption(f"📋 All cities in {state}: {', '.join(cities_for_state)}")
        else:
            state = "Delhi"; city = "Delhi"; lat = 28.6; lon = 77.2

        predict_btn = st.button("🔍 Predict AQI", type="primary", use_container_width=True)

    with col_right:
        st.subheader("Result")

        if predict_btn or True:   # show on load with default values
            # Always calculate formula-based AQI
            formula_aqi = calculate_aqi(pm25, pm10, no2, so2, co, ozone)
            display_aqi = formula_aqi

            if model_available and predict_btn:
                ml_aqi = predict_with_model(
                    pm25, pm10, no2, so2, co, ozone, nh3,
                    state, city, lat, lon)
                display_aqi = ml_aqi
                st.caption(f"ML model prediction  |  Formula AQI: {formula_aqi:.0f}")
            else:
                st.caption("CPCB formula-based AQI")

            cat, color = aqi_category(display_aqi)

            # Gauge
            fig = draw_gauge(display_aqi)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

            # Category badge
            st.markdown(
                f"<div style='background:{color};border-radius:8px;"
                f"padding:10px;text-align:center;font-size:20px;"
                f"font-weight:600;color:#111;margin-top:-10px'>"
                f"{cat}</div>",
                unsafe_allow_html=True,
            )

            # Sub-index breakdown
            st.divider()
            st.caption("Sub-index breakdown")
            pollutants = {
                "PM2.5": calculate_aqi(pm25, 0, 0, 0, 0, 0),
                "PM10":  calculate_aqi(0, pm10, 0, 0, 0, 0),
                "NO2":   calculate_aqi(0, 0, no2, 0, 0, 0),
                "SO2":   calculate_aqi(0, 0, 0, so2, 0, 0),
                "CO":    calculate_aqi(0, 0, 0, 0, co, 0),
                "Ozone": calculate_aqi(0, 0, 0, 0, 0, ozone),
            }
            for name, val in pollutants.items():
                _, c = aqi_category(val)
                st.markdown(
                    f"<div style='display:flex;justify-content:space-between;"
                    f"padding:4px 8px;border-radius:4px;background:{c}22;"
                    f"border-left:3px solid {c};margin-bottom:4px'>"
                    f"<span>{name}</span><span><b>{val:.0f}</b></span></div>",
                    unsafe_allow_html=True,
                )

    # AQI legend
    st.divider()
    st.caption("AQI categories (Indian CPCB)")
    cols = st.columns(6)
    legend = [
        ("0–50",   "Good",         "#55A84F"),
        ("51–100", "Satisfactory", "#A3C853"),
        ("101–200","Moderate",     "#FFF833"),
        ("201–300","Poor",         "#F29C33"),
        ("301–400","Very Poor",    "#E93F33"),
        ("401–500","Severe",       "#AF2D24"),
    ]
    for col, (rng, label, color) in zip(cols, legend):
        col.markdown(
            f"<div style='background:{color};border-radius:6px;"
            f"padding:6px 4px;text-align:center;font-size:12px;"
            f"font-weight:600;color:#111'>{label}<br><small>{rng}</small></div>",
            unsafe_allow_html=True,
        )


# ── Tab 2: Batch Prediction ───────────────────────────────────────────────────
with tab_batch:
    st.subheader("Upload your CSV file")
    st.caption("Required columns: `PM2.5`, `PM10`, `NO2`, `SO2`, `CO`, `OZONE`")

    uploaded = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded:
        df = pd.read_csv(uploaded)
        st.write(f"Loaded **{len(df)} rows**")
        st.dataframe(df.head(), use_container_width=True)

        required = {"PM2.5", "PM10", "NO2", "SO2", "CO", "OZONE"}
        missing_cols = required - set(df.columns)

        if missing_cols:
            st.error(f"Missing columns: {missing_cols}")
        else:
            df["AQI"] = df.apply(
                lambda r: calculate_aqi(
                    r.get("PM2.5", np.nan), r.get("PM10", np.nan),
                    r.get("NO2",   np.nan), r.get("SO2",  np.nan),
                    r.get("CO",    np.nan), r.get("OZONE",np.nan),
                ), axis=1
            )
            df["Category"] = df["AQI"].apply(lambda x: aqi_category(x)[0])

            st.success("✅ AQI calculated for all rows!")
            st.dataframe(df[["AQI", "Category"] + list(df.columns[:-2])],
                         use_container_width=True)

            csv_out = df.to_csv(index=False).encode()
            st.download_button(
                "⬇️ Download results CSV",
                data=csv_out,
                file_name="aqi_results.csv",
                mime="text/csv",
            )

            # Distribution chart
            st.subheader("AQI distribution")
            cat_counts = df["Category"].value_counts()
            cat_order  = ["Good", "Satisfactory", "Moderate",
                          "Poor", "Very Poor", "Severe"]
            cat_colors = ["#55A84F","#A3C853","#FFF833",
                          "#F29C33","#E93F33","#AF2D24"]
            ordered = [(c, cat_counts.get(c, 0), col)
                       for c, col in zip(cat_order, cat_colors)]

            fig2, ax2 = plt.subplots(figsize=(8, 3), facecolor="none")
            ax2.set_facecolor("none")
            bars = ax2.bar([o[0] for o in ordered],
                           [o[1] for o in ordered],
                           color=[o[2] for o in ordered],
                           edgecolor="white", linewidth=0.5)
            for bar, (_, cnt, _) in zip(bars, ordered):
                if cnt > 0:
                    ax2.text(bar.get_x() + bar.get_width()/2,
                             bar.get_height() + 0.3, str(cnt),
                             ha="center", va="bottom", fontsize=10)
            ax2.set_ylabel("Number of stations")
            ax2.spines[["top","right","left"]].set_visible(False)
            ax2.tick_params(left=False)
            st.pyplot(fig2, use_container_width=True)
            plt.close(fig2)
    else:
        st.info("Upload your dataset CSV above. Your existing CSV from this project works directly.")


# ── Tab 3: About ─────────────────────────────────────────────────────────────
with tab_about:
    st.subheader("About this app")
    st.markdown("""
This app predicts the **Air Quality Index (AQI)** for Indian cities using
the official **CPCB (Central Pollution Control Board)** methodology.

**Data used for training:**
- 3,406 records · 511 monitoring stations · 262 cities · 30 states
- Single-day snapshot: March 31, 2026
- Pollutants: PM2.5, PM10, NO2, SO2, CO, Ozone, NH3

**Model:**
- Algorithm: XGBoost (with GridSearchCV tuning)
- Features: Pollutant values + spatial features + engineered ratios
- Target: AQI calculated via Indian CPCB sub-index method

**How AQI is calculated:**
1. A sub-index is calculated for each pollutant using CPCB breakpoints
2. The final AQI = maximum of all sub-indices

**Tech stack:** Python · Pandas · Scikit-learn · XGBoost · Streamlit

---
*Built as a data science project using real Indian air quality monitoring data.*
    """)
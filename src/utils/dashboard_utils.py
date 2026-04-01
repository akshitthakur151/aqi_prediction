"""
dashboard_utils.py
Dashboard utilities and helper functions for AQI visualization
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pickle


def load_saved_models():
    """Load trained models"""
    try:
        with open('models/best_aqi_model.pkl', 'rb') as f:
            model = pickle.load(f)
        with open('models/scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        return model, scaler
    except:
        return None, None


def get_aqi_category(aqi):
    """Get AQI category and health info"""
    if aqi <= 50:
        return {
            'category': 'Good',
            'color': '#00E400',
            'bgColor': '#E8F5E9',
            'health': '✓ Air quality is satisfactory',
            'recommendation': 'No restrictions on outdoor activities'
        }
    elif aqi <= 100:
        return {
            'category': 'Satisfactory',
            'color': '#FFFF00',
            'bgColor': '#FFFDE7',
            'health': '⚠ Some sensitive individuals may experience effects',
            'recommendation': 'Sensitive groups should limit outdoor activity'
        }
    elif aqi <= 200:
        return {
            'category': 'Moderately Polluted',
            'color': '#FF7E00',
            'bgColor': '#FFF3E0',
            'health': '⚠⚠ Members of sensitive groups may experience health issues',
            'recommendation': 'Avoid outdoor activities for sensitive groups'
        }
    elif aqi <= 300:
        return {
            'category': 'Poor',
            'color': '#FF0000',
            'bgColor': '#FFEBEE',
            'health': '⚠⚠⚠ Health alert: increased risk for everyone',
            'recommendation': 'Everyone should reduce outdoor exposure'
        }
    elif aqi <= 400:
        return {
            'category': 'Very Poor',
            'color': '#8F3F97',
            'bgColor': '#F3E5F5',
            'health': '⚠⚠⚠⚠ Serious health effects for all',
            'recommendation': 'Avoid outdoor activities, use N95 masks indoors'
        }
    else:
        return {
            'category': 'Severe',
            'color': '#7E0023',
            'bgColor': '#FCE4EC',
            'health': '⚠⚠⚠⚠⚠ Emergency conditions',
            'recommendation': 'Stay indoors, close windows, use air purifiers'
        }


def create_aqi_gauge(aqi_value):
    """Create a gauge chart for AQI display"""
    category_info = get_aqi_category(aqi_value)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=aqi_value,
        title={'text': "AQI"},
        delta={'reference': 100},
        gauge={
            'axis': {'range': [0, 500]},
            'bar': {'color': category_info['color']},
            'steps': [
                {'range': [0, 50], 'color': '#E8F5E9'},
                {'range': [50, 100], 'color': '#FFFDE7'},
                {'range': [100, 200], 'color': '#FFF3E0'},
                {'range': [200, 300], 'color': '#FFEBEE'},
                {'range': [300, 400], 'color': '#F3E5F5'},
                {'range': [400, 500], 'color': '#FCE4EC'},
            ],
            'threshold': {
                'line': {'color': 'red', 'width': 4},
                'thickness': 0.75,
                'value': aqi_value
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=20)
    )
    
    return fig


def create_pollutants_chart(pollutants):
    """Create pollutant concentration chart"""
    df = pd.DataFrame([pollutants])
    
    fig = go.Figure(data=[
        go.Bar(x=list(pollutants.keys()), y=list(pollutants.values()))
    ])
    
    fig.update_layout(
        title="Pollutant Concentrations",
        xaxis_title="Pollutant",
        yaxis_title="Concentration (μg/m³)",
        height=300,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig


def create_time_series_chart(data, column):
    """Create time series chart for a specific pollutant"""
    fig = px.line(
        data,
        x='datetime' if 'datetime' in data.columns else data.index,
        y=column,
        title=f"{column} Trend",
        markers=True
    )
    
    fig.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=50, b=10),
        hovermode='x unified',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig


def create_city_comparison(city_data):
    """Create comparison chart for multiple cities"""
    fig = px.bar(
        city_data,
        x='city' if 'city' in city_data.columns else city_data.index,
        y='aqi' if 'aqi' in city_data.columns else city_data.iloc[:, 0],
        title="AQI Comparison Across Cities",
        color='aqi' if 'aqi' in city_data.columns else city_data.iloc[:, 0],
        color_continuous_scale="RdYlGn_r"
    )
    
    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig


def display_health_recommendations(aqi):
    """Display health recommendations based on AQI"""
    category_info = get_aqi_category(aqi)
    
    st.write(f"### Category: {category_info['category']}")
    st.markdown(f"**Health Impact**: {category_info['health']}")
    st.markdown(f"**Recommendation**: {category_info['recommendation']}")
    
    # Activity recommendations
    st.write("#### Activity Recommendations:")
    
    if aqi <= 50:
        st.markdown("✓ All outdoor activities recommended")
        st.markdown("✓ Exercise outdoors is beneficial")
    elif aqi <= 100:
        st.markdown("⚠ Unusual symptoms should be checked")
        st.markdown("⚠ Consider reducing prolonged outdoor exertion")
    elif aqi <= 200:
        st.markdown("⚠ Sensitive groups should reduce outdoor activity")
        st.markdown("⚠ Use N95 mask for outdoor activities")
    elif aqi <= 300:
        st.markdown("⚠ Everyone should reduce outdoor exposure")
        st.markdown("⚠ Avoid vigorous outdoor activities")
    elif aqi <= 400:
        st.markdown("⚠ Avoid outdoor activities")
        st.markdown("⚠ Use air purifiers indoors")
        st.markdown("⚠ Keep windows closed")
    else:
        st.markdown("⚠ Stay indoors")
        st.markdown("⚠ Avoid all outdoor activities")
        st.markdown("⚠ Use medical-grade air filters")


def display_vulnerable_groups(aqi):
    """Display vulnerable groups for current AQI"""
    category_info = get_aqi_category(aqi)
    
    vulnerable_info = {
        'Good': [],
        'Satisfactory': ['Asthma patients', 'Elderly populations'],
        'Moderately Polluted': ['Asthma patients', 'Elderly populations', 'Children', 'People with heart disease'],
        'Poor': ['Asthma patients', 'Elderly populations', 'Children', 'People with heart disease', 'Athletes'],
        'Very Poor': ['Everyone', 'Especially: Asthma patients', 'Elderly populations', 'Children'],
        'Severe': ['Everyone - Emergency situation'],
    }
    
    groups = vulnerable_info.get(category_info['category'], [])
    
    st.write("#### Vulnerable Groups:")
    if groups:
        for group in groups:
            st.write(f"• {group}")
    else:
        st.write("• No particularly vulnerable groups")


def predict_future_aqi(historical_data, days=7):
    """Simple trend-based AQI prediction"""
    if len(historical_data) < 2:
        return None
    
    # Simple linear trend
    recent_data = historical_data[-7:] if len(historical_data) >= 7 else historical_data
    x = np.arange(len(recent_data))
    y = recent_data.values
    
    # Fit polynomial
    z = np.polyfit(x, y, 2)
    p = np.poly1d(z)
    
    # Future predictions
    future_x = np.arange(len(recent_data), len(recent_data) + days)
    future_y = p(future_x)
    
    return future_y


# Export utilities
__all__ = [
    'load_saved_models',
    'get_aqi_category',
    'create_aqi_gauge',
    'create_pollutants_chart',
    'create_time_series_chart',
    'create_city_comparison',
    'display_health_recommendations',
    'display_vulnerable_groups',
    'predict_future_aqi'
]

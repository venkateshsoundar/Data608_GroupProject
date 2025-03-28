import boto3
import plotly.express as px
import pandas as pd
import io
import streamlit as st
import plotly.graph_objects as go
from scipy.stats import pearsonr

# Set page config must be first Streamlit command
st.set_page_config(layout="wide", page_title="Weather Analytics Dashboard", page_icon="🌦️")

# Initialize S3 client and load data
@st.cache_data
def load_data(bucket_name, file_key):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    return pd.read_csv(io.BytesIO(response['Body'].read()))

# Main app starts here
def main():
    df = load_data('firstbucketdata608', 'weather_data.csv')
    st.title("🌦️ Weather Analytics Dashboard")

    # Sidebar for filters
    with st.sidebar:
        st.header("Filters")
        selected_city = st.selectbox("Select City", df['Location'].unique())
        st.markdown("---")
        st.markdown("**Dashboard Features:**")
        st.markdown("- Monthly temperature trends")
        st.markdown("- Weather condition distribution")
        st.markdown("- Precipitation & humidity analysis")
        st.markdown("- Hourly temperature patterns")
        st.markdown("- Temperature correlations")
        st.markdown("- Forecast")
        st.markdown("---")
    st.markdown("*Data Source: [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api)*")

    # Filter data for selected city
    city_data = df[df['Location'] == selected_city]
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']

    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🌡️ Temperature Analysis", "💧 Precipitation & Weather", "📊 Statistical Insights", "🌤️ Forecast"])

    # Tab 1: Temperature Analysis
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Monthly Temperature Chart
            st.subheader(f"Monthly Temperature Trend in {selected_city}")
            monthly_avg_temp = city_data.groupby('month', observed=False, as_index=False)['temp'].mean()
            
            if pd.api.types.is_numeric_dtype(monthly_avg_temp['month']):
                monthly_avg_temp['month_name'] = monthly_avg_temp['month'].map(
                    lambda m: month_order[int(m)-1] if not pd.isna(m) else None)
            else:
                month_abbr_to_full = {**{m[:3]: m for m in month_order}, 
                                    **{m.lower(): m for m in month_order},
                                    **{m: m for m in month_order}}
                monthly_avg_temp['month_name'] = monthly_avg_temp['month'].str.strip().map(
                    lambda x: month_abbr_to_full.get(x.title(), x))
            
            temp_fig = px.line(
                monthly_avg_temp,
                x='month_name',
                y='temp',
                markers=True,
                labels={'temp': 'Temperature (°C)', 'month_name': 'Month'}
            )
            
            # Add seasonal backgrounds
            seasons = [
                {'name': 'Winter', 'months': ['December', 'January', 'February'], 'color': 'rgba(173, 216, 230, 0.3)'},
                {'name': 'Spring', 'months': ['March', 'April', 'May'], 'color': 'rgba(144, 238, 144, 0.3)'},
                {'name': 'Summer', 'months': ['June', 'July', 'August'], 'color': 'rgba(255, 255, 153, 0.3)'},
                {'name': 'Fall', 'months': ['September', 'October', 'November'], 'color': 'rgba(255, 160, 122, 0.3)'}
            ]
            
            for season in seasons:
                month_indices = [month_order.index(month) for month in season['months']]
                temp_fig.add_vrect(
                    x0=min(month_indices)-0.5,
                    x1=max(month_indices)+0.5,
                    fillcolor=season['color'],
                    layer="below",
                    line_width=0,
                    showlegend=False
                )
                temp_fig.add_scatter(
                    x=[None], y=[None],
                    mode='lines',
                    line=dict(width=10, color=season['color']),
                    name=season['name']
                )
            
            temp_fig.update_layout(
                xaxis=dict(type='category', categoryorder='array', categoryarray=month_order),
                yaxis_title='Avg Temperature (°C)',
                template='plotly_white',
                legend=dict(title='Seasons', orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                height=400
            )
            st.plotly_chart(temp_fig, use_container_width=True)
        
        with col2:
            # Hourly Temperature Chart
            st.subheader(f"Daily Temperature Pattern in {selected_city}")
            city_data['corrected_hour'] = (pd.to_datetime(city_data['time']).dt.hour + 14) % 24
            hourly_avg_temp = city_data.groupby('corrected_hour', as_index=False)['temp'].mean()
            
            hourly_fig = px.line(
                hourly_avg_temp,
                x='corrected_hour',
                y='temp',
                markers=True,
                labels={'temp': 'Temperature (°C)', 'corrected_hour': 'Hour (24h)'}
            )
            
            hourly_fig.update_layout(
                xaxis=dict(tickmode='array', tickvals=list(range(24))),
                yaxis_title='Avg Temperature (°C)',
                template='plotly_white',
                height=400
            )
            st.plotly_chart(hourly_fig, use_container_width=True)

    # Tab 2: Precipitation & Weather
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Weather Description Pie Chart
            st.subheader(f"Weather Conditions in {selected_city}")
            weather_counts = city_data['weather_description'].value_counts().nlargest(10)
            weather_fig = px.pie(
                values=weather_counts, 
                names=weather_counts.index, 
                hole=0.3
            )
            weather_fig.update_traces(textinfo='percent+label')
            weather_fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(weather_fig, use_container_width=True)
        
        with col2:
            # Precipitation/Snowfall Chart
            st.subheader(f"Precipitation & Snowfall in {selected_city}")
            precip_snow_city = city_data[['month', 'precipitation', 'snowfall']].copy()
            
            if pd.api.types.is_numeric_dtype(precip_snow_city['month']):
                precip_snow_city['month_name'] = precip_snow_city['month'].map(
                    lambda m: month_order[int(m)-1] if not pd.isna(m) else None)
            
            selected_vars = st.multiselect(
                'Select metrics:',
                options=['Precipitation', 'Snowfall'],
                default=['Precipitation', 'Snowfall'],
                key='precip_snow_filter'
            )
            
            precip_snow_fig = go.Figure()
            if 'Precipitation' in selected_vars:
                precip_snow_fig.add_trace(go.Bar(
                    x=precip_snow_city['month_name'],
                    y=precip_snow_city['precipitation'],
                    name='Precipitation (mm)',
                    marker_color='#1f77b4'
                ))
            if 'Snowfall' in selected_vars:
                precip_snow_fig.add_trace(go.Bar(
                    x=precip_snow_city['month_name'],
                    y=precip_snow_city['snowfall'],
                    name='Snowfall (mm)',
                    marker_color='#7f7f7f'
                ))
            
            precip_snow_fig.update_layout(
                xaxis=dict(type='category', categoryorder='array', categoryarray=month_order),
                barmode='group',
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                height=400
            )
            st.plotly_chart(precip_snow_fig, use_container_width=True)
        
        # Humidity and Precipitation Chart
        st.subheader(f"Humidity and Precipitation Trends in {selected_city}")
        monthly_avg = city_data.groupby('month').agg({'humidity': 'mean', 'precipitation': 'mean'}).reset_index()
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        line_bar_fig = go.Figure()
        line_bar_fig.add_trace(go.Scatter(
            x=monthly_avg['month'], 
            y=monthly_avg['humidity'], 
            mode='lines', 
            name='Average Humidity (%)', 
            line=dict(color='blue', width=2),
            yaxis='y1'
        ))
        line_bar_fig.add_trace(go.Bar(
            x=monthly_avg['month'], 
            y=monthly_avg['precipitation'], 
            name='Average Precipitation (mm)', 
            marker=dict(color='green', opacity=0.6),
            yaxis='y2'
        ))
        
        line_bar_fig.update_layout(
            xaxis_title="Month",
            xaxis=dict(
                tickmode='array',
                tickvals=monthly_avg['month'],
                ticktext=month_names
            ),
            yaxis_title="Humidity (%)",
            yaxis2=dict(
                title="Precipitation (mm)",
                overlaying='y',
                side='right'
            ),
            barmode='overlay',
            showlegend=True,
            height=500
        )
        st.plotly_chart(line_bar_fig, use_container_width=True)

    # Tab 3: Statistical Insights
    with tab3:
        st.subheader(f"Temperature Correlations in {selected_city}")
        
        try:
            features = ['temp', 'precipitation', 'humidity', 'snowfall', 'wind_speed']
            corr_data = city_data[features].apply(pd.to_numeric, errors='coerce').dropna()
            
            results = []
            for feature in features[1:]:
                corr, pval = pearsonr(corr_data['temp'], corr_data[feature])
                results.append({'Feature': feature, 'Correlation': corr, 'p-value': pval})
            
            result_df = pd.DataFrame(results).sort_values('Correlation', ascending=False)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=result_df['Correlation'],
                y=result_df['Feature'],
                orientation='h',
                marker_color=['#1f77b4' if x >= 0 else '#d62728' for x in result_df['Correlation']]
            ))
            
            fig.update_layout(
                xaxis=dict(range=[-1, 1], title="Correlation Coefficient"),
                yaxis=dict(title="Feature"),
                height=400,
                margin=dict(l=100, r=50, t=50, b=50)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error calculating correlations: {str(e)}")

    # Tab 4: Forecast
    
    df_forecast = load_data('firstbucketdata608', 'forecast_data.csv')

    with tab4:
        st.subheader(f"Temperature Forecast for {selected_city}")
        
        # Filter the forecast data for the selected city
        city_forecast = df_forecast[df_forecast['Location'] == selected_city]
        
        # Ensure the 'time' column is in datetime format (if it's not already)
        city_forecast['time'] = pd.to_datetime(city_forecast['time'])
        
        # Create the forecast temperature line plot
        forecast_fig = px.line(
            city_forecast,
            x='time',
            y='forecast_temp',
            markers=True,
            title=f"Temperature Forecast for {selected_city}",
            labels={'forecast_temp': 'Temperature (°C)', 'time': 'Time'}
        )
        
        # Calculate the boundaries (e.g., ±1°C)
        upper_bound = city_forecast['forecast_temp'] + 1  # Upper Bound (Forecast + 1)
        lower_bound = city_forecast['forecast_temp'] - 1  # Lower Bound (Forecast - 1)
        
        # Add the upper and lower boundaries as shaded regions
        forecast_fig.add_traces(go.Scatter(
            x=city_forecast['time'], 
            y=upper_bound, 
            fill=None, 
            mode='lines',
            line=dict(color='green', dash='dot'),
            name='Upper Bound'
        ))

        forecast_fig.add_traces(go.Scatter(
            x=city_forecast['time'], 
            y=lower_bound, 
            fill='tonexty',  # Fill the area between the upper and lower bounds
            mode='lines',
            line=dict(color='green', dash='dot'),
            name='Lower Bound',
            fillcolor='rgba(0, 255, 0, 0.2)'  # Set the shaded region color (light green)
        ))

        # Update layout for the chart
        forecast_fig.update_layout(
            template='plotly_white',
            height=400,
            xaxis=dict(title="Time", tickformat="%H:%M", tickmode="array"),
            yaxis_title="Forecasted Temperature (°C)",
            title=f"Temperature Forecast for {selected_city}"
        )
        
        # Display the forecast temperature chart
        st.plotly_chart(forecast_fig, use_container_width=True)


    # Dashboard styling
    st.markdown("""
        <style>
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 8px 16px;
            border-radius: 4px 4px 0 0;
        }
        .stTabs [aria-selected="true"] {
            background-color: #f0f2f6;
        }
        </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

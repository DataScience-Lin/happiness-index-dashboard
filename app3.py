import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(
    page_title="World Happiness Report Dashboard",
    page_icon="😊",
    layout="wide",
)

# --- Data Loading and Caching ---
@st.cache_data
def load_happiness_data(file_path):
    try:
        df = pd.read_excel(file_path)
    except FileNotFoundError:
        st.error(f"FATAL ERROR: '{file_path}' not found.")
        st.stop()
    
    # Clean up column names for easier use
    df = df.rename(columns={
        'Country name': 'Country',
        'Life evaluation (3-year average)': 'Happiness Score',
        'Explained by: Log GDP per capita': 'GDP per capita',
        'Explained by: Social support': 'Social support',
        'Explained by: Healthy life expectancy': 'Healthy Life Expectancy',
        'Explained by: Freedom to make life choices': 'Freedom',
        'Explained by: Generosity': 'Generosity',
        'Explained by: Perceptions of corruption': 'Perceptions of corruption'
    })

    # Add a 'Region' column if it doesn't exist. You should add this to your Excel file for best results.
    if 'Region' not in df.columns:
        st.warning("Your data does not have a 'Region' column. Filtering by region will not be available. Please add a 'Region' column to your Excel file.")
        df['Region'] = 'N/A'

    return df

# --- Main App Layout ---
st.title("😊 World Happiness Report: An Interactive Analysis")
st.markdown("Explore the factors that contribute to happiness around the globe. Data from the World Happiness Report.")

df = load_happiness_data('happiness_data.xlsx')

# --- Create All Five Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔑 Key Findings", 
    "🏆 Advanced Ranking Table", 
    "🗺️ Factor Explorer Map", 
    "💰 GDP vs. Happiness", 
    "📈 Country Comparison"
])

# --- TAB 1: KEY FINDINGS ---
with tab1:
    st.header("Key Findings from the Latest Report")
    latest_year = df['Year'].max()
    st.markdown(f"A summary of the happiness landscape for the year **{latest_year}**.")

    df_latest = df[df['Year'] == latest_year].sort_values(by='Rank')
    
    top_country = df_latest.iloc[0]
    second_country = df_latest.iloc[1]
    last_country = df_latest.iloc[-1]

    col1, col2, col3 = st.columns(3)
    col1.metric(label=f"Happiest Country", value=top_country['Country'], delta=f"#{int(top_country['Rank'])} Overall")
    col2.metric(label=f"Runner-Up", value=second_country['Country'], delta=f"#{int(second_country['Rank'])} Overall")
    col3.metric(label=f"Least Happy Country", value=last_country['Country'], delta=f"#{int(last_country['Rank'])} Overall", delta_color="inverse")

    st.divider()
    st.subheader("What Makes the Happiest Country Happy?")
    st.markdown(f"Let's look at the 'recipe for happiness' for **{top_country['Country']}**.")

    recipe_factors = ['GDP per capita', 'Social support', 'Healthy Life Expectancy', 'Freedom', 'Generosity', 'Perceptions of corruption', 'Dystopia + residual']
    valid_factors = [factor for factor in recipe_factors if factor in top_country]
    recipe_data = top_country[valid_factors].reset_index()
    recipe_data.columns = ['Factor', 'Contribution to Score']
    
    fig_recipe = px.bar(recipe_data, x='Contribution to Score', y='Factor', orientation='h', title=f"Components of {top_country['Country']}'s Happiness Score")
    fig_recipe.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_recipe, use_container_width=True)

# --- TAB 2: ADVANCED RANKING TABLE ---
with tab2:
    st.header("Global Happiness Rankings")
    col1, col2, col3 = st.columns([0.3, 0.4, 0.3])
    with col1:
        all_years = sorted(df['Year'].unique(), reverse=True)
        selected_year = st.selectbox("Select a Year:", options=all_years)
    with col2:
        all_regions = sorted(df['Region'].unique())
        selected_regions = st.multiselect("Filter by Region:", options=all_regions, default=all_regions)
    with col3:
        country_search = st.text_input("Search for a Country:")

    df_filtered = df[df['Year'] == selected_year]
    if selected_regions:
        df_filtered = df_filtered[df_filtered['Region'].isin(selected_regions)]
    if country_search:
        df_filtered = df_filtered[df_filtered['Country'].str.contains(country_search, case=False, na=False)]

    if df_filtered.empty:
        st.warning("No data found for the selected filters.")
    else:
        columns_to_display = ['Rank', 'Country', 'Happiness Score', 'Social support', 'GDP per capita', 'Healthy Life Expectancy', 'Freedom', 'Generosity', 'Perceptions of corruption']
        existing_cols = [col for col in columns_to_display if col in df_filtered.columns]
        df_display = df_filtered[existing_cols].sort_values(by='Rank').set_index('Rank')
        st.markdown(f"**Displaying {len(df_display)} countries for {selected_year}**")
        st.dataframe(df_display, use_container_width=True)

# --- TAB 3: FACTOR EXPLORER MAP ---
with tab3:
    st.header("Explore the Components of Happiness on a World Map")
    factor_cols = ['GDP per capita', 'Social support', 'Healthy Life Expectancy', 'Freedom', 'Generosity', 'Perceptions of corruption']
    selected_factor = st.selectbox("Select a Factor to Visualize:", options=factor_cols)
    
    df_map = df[df['Year'] == df['Year'].max()]
    fig_map = px.choropleth(df_map, locations="Country", locationmode='country names', color=selected_factor, hover_name="Country", hover_data={'Happiness Score': ':.2f'}, color_continuous_scale=px.colors.sequential.Plasma, title=f"World Map of '{selected_factor}' ({df['Year'].max()})")
    st.plotly_chart(fig_map, use_container_width=True)

# --- TAB 4: GDP VS. HAPPINESS ---
with tab4:
    st.header("The Relationship Between Wealth and Happiness")
    st.markdown("Does a higher GDP per capita lead to a higher happiness score?")
    
    df_scatter = df[df['Year'] == df['Year'].max()]
    fig_scatter = px.scatter(df_scatter, x="GDP per capita", y="Happiness Score", hover_name="Country", size="Happiness Score", color="Happiness Score", title=f"Does Money Buy Happiness ({df['Year'].max()})")
    st.plotly_chart(fig_scatter, use_container_width=True)

# --- TAB 5: COUNTRY COMPARISON ---
with tab5:
    st.header("Compare Countries Over Time")
    all_countries_list = sorted(df['Country'].unique())
    default_countries = ["Finland", "Denmark", "United States", "China", "India"]
    valid_defaults = [c for c in default_countries if c in all_countries_list]
    
    selected_countries = st.multiselect("Select countries to compare:", options=all_countries_list, default=valid_defaults)
    
    if selected_countries:
        trend_df = df[df['Country'].isin(selected_countries)]
        trend_pivot = trend_df.pivot_table(index='Year', columns='Country', values='Happiness Score')
        st.line_chart(trend_pivot, height=500)
    else:
        st.warning("Please select at least one country to display.")
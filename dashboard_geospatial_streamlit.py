import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title='Dashboard Geospatial - Gapminder',
    page_icon='🌍',
    layout='wide'
)

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df['year'] = df['year'].astype(int)
    df['gdp_tier'] = df['gdp_tier'].astype(str)
    return df

DATA_PATH = 'dataset_gapminder_geospatial.csv'
df = load_data(DATA_PATH)

st.sidebar.header('Interactive Filter')

all_continents = sorted(df['continent'].dropna().unique().tolist())
all_tiers = ['Sangat Rendah', 'Rendah', 'Menengah', 'Menengah Atas', 'Tinggi']
all_tiers_id = ['Sangat Rendah', 'Rendah', 'Menengah', 'Menengah Atas', 'Tinggi']
all_tiers_en = ['Very Low', 'Low', 'Medium', 'Upper Medium', 'High']

# Mapping antara kategori bahasa Inggris dan Indonesia
tier_mapping = {
    'Very Low': 'Sangat Rendah',
    'Low': 'Rendah',
    'Medium': 'Menengah',
    'Upper Medium': 'Menengah Atas',
    'High': 'Tinggi'
}

all_years = sorted(df['year'].unique().tolist())

selected_year = st.sidebar.slider(
    'Select Year',
    min_value=min(all_years),
    max_value=max(all_years),
    value=max(all_years),
    step=5
)

# Pilih benua dari sidebar
selected_continents = st.sidebar.multiselect(
    'Select Continent',
    options=all_continents,
    default=all_continents
)

# Validasi: Jika kurang dari 2 benua dipilih, tampilkan pesan error
if len(selected_continents) < 2:
    st.sidebar.error('Please select at least 2 continents!')

# Pilih kategori GDP dalam bahasa Inggris di UI
selected_tiers_en = st.sidebar.multiselect(
    'Select GDP per Capita Category',  # Label dalam bahasa Inggris
    options=all_tiers_en,  # Menampilkan kategori dalam bahasa Inggris
    default=all_tiers_en  # Default juga dalam bahasa Inggris
)

# Mapping pilihan yang dipilih (dari bahasa Inggris ke bahasa Indonesia)
selected_tiers = [tier_mapping[tier] for tier in selected_tiers_en]

# Menampilkan hasil untuk debugging
# st.write("Selected tiers (in Indonesian):", selected_tiers)

top_n = st.sidebar.slider('Number of countries on the bar chart', 5, 20, 10)

filtered = df[
    (df['continent'].isin(selected_continents)) &
    (df['gdp_tier'].isin(selected_tiers))
].copy()

current = filtered[filtered['year'] == selected_year].copy()

if current.empty:
    st.error('No data matches the current filter combination.')
    st.stop()

trend = filtered.groupby(['year', 'continent'], as_index=False).agg(
    avg_lifeExp=('lifeExp', 'mean'),
    avg_gdpPercap=('gdpPercap', 'mean'),
    total_pop=('pop', 'sum')
)

current['gdp_tier_en'] = current['gdp_tier'].map({
    'Sangat Rendah': 'Very Low',
    'Rendah': 'Low',
    'Menengah': 'Medium',
    'Menengah Atas': 'Upper Medium',
    'Tinggi': 'High'
})

continent_avg = current.groupby('continent', as_index=False)['lifeExp'].mean().sort_values('lifeExp')
lowest_continent = continent_avg.iloc[0]['continent']
lowest_country_row = current.sort_values(['lifeExp', 'pop'], ascending=[True, False]).iloc[0]
highest_country_row = current.sort_values(['lifeExp', 'pop'], ascending=[False, False]).iloc[0]
global_avg = current['lifeExp'].mean()
below_avg_count = int((current['lifeExp'] < global_avg).sum())
total = len(current)
selected_continents_str = ', '.join(selected_continents)

# # Menampilkan teks dengan styling warna merah di Streamlit
if len(selected_continents) == len(all_continents):
    insight_title = (
        f'<h1><span style="color:red">{lowest_continent.upper()}</span> REMAINS A TOP PRIORITY IN THE WORLD DUE TO HAVING '
        f'<span style="color:red">THE LOWEST AVERAGE LIFE EXPECTANCY</span> IN {selected_year}</h1>'
    )
else:
    insight_title = (
        f'<h1><span style="color:red">{lowest_continent.upper()}</span> REMAINS A PRIORITY AMONG THE {len(selected_continents)} '
        f'SELECTED CONTINENTS DUE TO HAVING <span style="color:red">THE LOWEST AVERAGE LIFE EXPECTANCY</span> IN {selected_year}</h1>'
    )

# Menampilkan Insight Title dengan styling warna merah di Streamlit
st.markdown(insight_title, unsafe_allow_html=True)

# st.title(insight_title)
st.caption(f'The total number of countries covered in this dashboard is {total} countries from {len(selected_continents)} continents: {selected_continents_str}.'
           ' This dashboard helps identify countries with low life expectancy and regions that need to be prioritized for health policies based on geospatial and economic data.')

col1, col2, col3, col4 = st.columns(4)
# Rata-rata Harapan Hidup
col1.metric('Average Life Expectancy', f"{global_avg:.1f} years")

# Negara Terendah dengan warna merah dan panah ke bawah
delta_value = global_avg - lowest_country_row['lifeExp']

# Jika nilai delta negatif, gunakan panah ke bawah dan warna merah
if delta_value < 0:
    delta_display = abs(delta_value)  # hanya nilai delta (positif)
    delta_color = "red"
    delta_arrow = "<span style='font-size: 22px;'>↓</span>"  # Panah ke bawah emoji
else:
    delta_display = delta_value
    delta_color = "red"
    delta_arrow = "<span style='font-size: 22px;'>↓</span>"  # Panah ke atas emoji

# Negara Terendah
col2.metric('The Lowest Life Expectancy', f"{lowest_country_row['country']}")
col2.markdown(
    f"<div style='margin-top: -25px;'><span style='color:{delta_color}'>{delta_arrow} {lowest_country_row['lifeExp']:.1f} years</span></div>", 
    unsafe_allow_html=True
)

# Negara Tertinggi
col3.metric('The Highest Life Expectancy', f"{highest_country_row['country']}", f"{highest_country_row['lifeExp']:.1f} years")

# Negara di Bawah Rata-rata
col4.metric('Below Average Life Expectancy', f'{below_avg_count} countries')

# Membuat 2 kolom untuk menampilkan peta dan bar chart bersebelahan
col1, col2 = st.columns(2)

# Menampilkan peta di kolom pertama
with col1:
    map_fig = px.choropleth(
        current,
        locations='iso_alpha',
        color='lifeExp',
        hover_name='country',
        hover_data={
            'continent': True,
            'lifeExp': ':.1f',
            'gdpPercap': ':.0f',
            'pop': ':,.0f',
            'iso_alpha': False
        },
        color_continuous_scale='YlOrRd_r',
        projection='natural earth',
        title=f'Geospatial Map of Life Expectancy by Country in {selected_year}',
        labels={
            'lifeExp': 'Life Expectancy',
            'gdpPercap': 'GDP per Capita',
            'pop': 'Population'
        }
    )
    # Update layout to have consistent height and margins
    map_fig.update_layout(
        margin=dict(l=0, r=0, t=60, b=0),
        height=520
    )
    st.plotly_chart(map_fig, use_container_width=True)

# Menampilkan bar chart di kolom kedua
with col2:
    bottom_countries = current.sort_values(['lifeExp', 'pop'], ascending=[True, False]).head(top_n)
    bar_fig = px.bar(
        bottom_countries,
        x='lifeExp',
        y='country',
        color='continent',
        hover_data={
            'country': True,           # Country
            'lifeExp': ':.1f',         # Life Expectancy comes first
            'gdp_tier_en': True,       # GDP Tier
            'pop': ':,.0f',            # Population
            'continent': True,         # Continent
            'iso_alpha': False         # Not shown in hover
        },
        orientation='h',
        text='lifeExp',
        title=f'Top {top_n} Countries with the Lowest Life Expectancy in {selected_year}',
        labels={
            'continent': 'Continent',
            'country': 'Country',
            'lifeExp': 'Life Expectancy',
            'gdpPercap': 'GDP per Capita',
            'gdp_tier_en': 'GDP Tier',
            'pop': 'Population'
        }
    )
    
    # Update layout to match the map layout
    bar_fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    bar_fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        height=520,
        margin=dict(l=0, r=0, t=60, b=0)
    )
    
    st.plotly_chart(bar_fig, use_container_width=True)

line_fig = px.line(
    trend,
    x='year',
    y='avg_lifeExp',
    color='continent',
    markers=True,
    title='Average Life Expectancy Trend by Continent',
    labels={
        'year': 'Years',
        'avg_lifeExp': 'Average Life Expectancy',
        'continent': 'Continent'
    }
)
line_fig.update_layout(height=500)

# Update y-axis to show only one decimal place
line_fig.update_layout(
    height=500,
    yaxis_tickformat='.1f'  # Format y-axis to one decimal place
)

scatter_fig = px.scatter(
    current,
    x='gdpPercap',
    y='lifeExp',
    color='continent',
    size='pop',
    size_max=35,
    # log_x=True,
    hover_name='country',
    hover_data={
        'gdp_tier_en': True,  # GDP Tier comes first
        'pop': ':,.0f',       # Population
        'gdpPercap': ':,.2f', # GDP per Capita
        'lifeExp': ':,.1f',   # Life Expectancy
        'continent': True     # Continent
    },
    title=f'Relationship between GDP per Capita and Life Expectancy in {selected_year}',
    labels={
        'gdpPercap': 'GDP per Capita',
        'lifeExp': 'Life Expectancy',
        'continent': 'Continent',
        'pop': 'Population',
        'Sangat Rendah': 'Very Low',
        'Rendah': 'Low',
        'Menengah': 'Medium',
        'Menengah Atas': 'Upper Medium',
        'Tinggi': 'High',
        'gdp_tier_en': 'GDP Tier'
    },
    height=500
)

# top_left, top_right = st.columns([1.25, 1])
# with top_left:
#     st.plotly_chart(map_fig, use_container_width=True)
# with top_right:
#     st.plotly_chart(bar_fig, use_container_width=True)

bottom_left, bottom_right = st.columns(2)
with bottom_left:
    st.plotly_chart(line_fig, use_container_width=True)
with bottom_right:
    st.plotly_chart(scatter_fig, use_container_width=True)
    

st.subheader('Key Insight')

key_insight = (
    # f'Pada tahun {selected_year}, {lowest_continent} tercatat sebagai benua dengan harapan hidup terendah dibandingkan {len(selected_continents)-1} benua lainnya. '
    f'In {selected_year}, {lowest_continent} was recorded as the continent with the lowest life expectancy. Although there is a positive correlation between GDP and life expectancy, countries with similar GDP often show significant differences in life expectancy. This suggests that, in addition to economic factors, other factors such as social inequality and healthcare systems also play a crucial role.'
    # f'Terdapat perbedaan besar antara negara-negara di Benua {lowest_continent} dengan negara-negara di benua lain yang memiliki GDP serupa. '
    # f'Meskipun ada korelasi positif antara GDP dan harapan hidup, negara-negara dengan GDP serupa sering kali menunjukkan perbedaan besar dalam harapan hidup. Ini menunjukkan bahwa selain faktor ekonomi, faktor lain seperti kesenjangan sosial dan sistem kesehatan juga berperan penting.'
    # ' Artinya, selain faktor ekonomi, terdapat faktor-faktor lain yang menyebabkan harapan hidup suatu negara menjadi rendah. '
    # 'Misalkan seperti terdapat kesenjangan sosial yang cukup tinggi, sistem kesehatan tidak merata, dll.'
)
st.info(key_insight)

# Pada tahun 2007, Africa mencatatkan harapan hidup terendah, dengan perbedaan yang besar antara negara-negara dengan GDP serupa. Meskipun GDP berhubungan positif dengan harapan hidup, masih banyak negara dengan GDP tinggi yang memiliki harapan hidup rendah.

# Filter data negara-negara di lowest_continent
lowest_continent_data = current[current['continent'] == lowest_continent]

# X: 5 negara dengan GDP terbawah, tapi dengan populasi terbesar
X_countries = lowest_continent_data.sort_values(by=['gdpPercap', 'pop'], ascending=[True, False]).head(5)
X_country = X_countries.iloc[0]['country']  # Negara pertama dengan GDP terendah dan populasi terbesar

# Y: Negara dengan harapan hidup terendah tapi tidak dalam 5 GDP terendah
# Filter negara di lowest_continent yang gdpPercap bukan 'Sangat Rendah' atau 'Rendah'
valid_gdp_countries = lowest_continent_data[~lowest_continent_data['gdp_tier'].isin(['Sangat Rendah', 'Rendah'])]

# Urutkan negara berdasarkan harapan hidup terendah di antara negara yang tersisa
Y_country = valid_gdp_countries.sort_values(by='lifeExp').iloc[0]['country']

st.subheader('Recommendation')
recommendation = (
    f'The focus of intervention should be directed towards {lowest_continent}, which has the lowest average life expectancy. Prioritize countries with large populations and low life expectancy, such as {X_country}. Also, prioritize countries with high GDP but still lagging life expectancy, such as {Y_country}. Economic growth has not yet fully reflected in the quality of life, so more inclusive and equitable social and healthcare policies are needed.'
    # 'memiliki populasi besar dengan rata-rata harapan hidup yang rendah. Selain itu, negara dengan GDP per kapita yang sudah relatif tinggi tetapi harapan hidupnya '
    # 'masih tertinggal perlu mendapat perhatian khusus karena pertumbuhan ekonomi belum sepenuhnya tercermin dalam kualitas hidup.'
)
st.success(recommendation)

st.markdown('### Storytelling')

what_text = (
    # f'Pada {selected_year}, terdapat kesenjangan spasial yang jelas dalam harapan hidup antarnegara. '
    # f'{lowest_continent} berada pada posisi terendah secara rata-rata, sementara beberapa negara lain menunjukkan '
    # 'GDP per kapita yang cukup tinggi tetapi harapan hidupnya belum setara.'
    f'In {selected_year}, {lowest_continent} had the lowest average life expectancy compared to other continents. Countries in this continent, especially those with large populations, show significant gaps in quality of life despite economic growth.'
)

so_what_text = (
    # 'Hal ini menunjukkan bahwa pertumbuhan ekonomi saja belum cukup untuk menjamin kualitas hidup yang lebih baik. '
    # 'Jika keputusan hanya bertumpu pada indikator ekonomi, maka area dengan masalah kesehatan yang masih tertinggal dapat terlewat.'
    'Although GDP per capita is linked to life expectancy, many countries with high GDP still have low life expectancy. This indicates that factors beyond economics, such as uneven healthcare systems and social inequality, play a significant role in quality of life.'
)

now_what_text = (
    # 'Pembuat kebijakan perlu memprioritaskan negara dengan harapan hidup rendah, populasi besar, '
    # 'atau ketidakseimbangan antara GDP per kapita dan harapan hidup. Dashboard ini dapat dipakai untuk memilih area prioritas '
    # 'dan memantau perubahan dari waktu ke waktu.'
    f'Health policy interventions should be prioritized for {lowest_continent}, especially in countries with large populations and low life expectancy, such as {X_country}. Additionally, countries with high GDP but still lagging life expectancy, such as {Y_country}, need special attention to ensure that economic growth is more inclusive and benefits all segments of society.'
)

# Membuat 3 kolom untuk WHAT, SO WHAT, dan NOW WHAT
col1, col2, col3 = st.columns(3)

# Menampilkan WHAT dengan latar belakang warna biru, tinggi auto, dan responsif
with col1:
    st.markdown(
        f"<div style='background-color:#E3F2FD; padding: 20px; border: 0px solid #000; border-radius: 8px; height: auto; flex-grow: 1;'>"
        f"<b style='font-size: 22px;'>WHAT</b><br><div style='margin-bottom: 20px;'>{what_text}</div></div>",
        unsafe_allow_html=True
    )

# Menampilkan SO WHAT dengan latar belakang warna kuning, tinggi auto, dan responsif
with col2:
    st.markdown(
        f"<div style='background-color:#FFF9C4; padding: 20px; border: 0px solid #000; border-radius: 8px; height: auto; flex-grow: 1;'>"
        f"<b style='font-size: 22px;'>SO WHAT</b><br><div style='margin-bottom: 20px;'>{so_what_text}</div></div>",
        unsafe_allow_html=True
    )

# Menampilkan NOW WHAT dengan latar belakang warna hijau, tinggi auto, dan responsif
with col3:
    st.markdown(
        f"<div style='background-color:#C8E6C9; padding: 20px; border: 0px solid #000; border-radius: 8px; height: auto; flex-grow: 1;'>"
        f"<b style='font-size: 22px;'>NOW WHAT</b><br><div style='margin-bottom: 20px;'>{now_what_text}</div></div>",
        unsafe_allow_html=True
    )
    
st.markdown(
    "<p style='text-align: right; color: grey; font-size: 12px;'>Source data: https://www.gapminder.org/data/</p>",
    unsafe_allow_html=True
)
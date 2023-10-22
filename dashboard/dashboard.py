import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from datetime import datetime

sns.set(style='dark')

#Menyiapkan data
daily_df = pd.read_csv("dashboard\day.csv")
hourly_df = pd.read_csv("dashboard\hour.csv")

#Mengubah nama kolom dataframe
daily_df.rename(columns={'instant':'record','dteday':'datetime','yr':'year','mnth':'month','weathersit':'weather_condition',
                       'hum':'humidity','cnt':'total_count'},inplace=True)
hourly_df.rename(columns = {'instant':'record','dteday':'datetime','yr':'year','mnth':'month', 'hr': 'hour','weathersit':'weather_condition',
                       'hum':'humidity','cnt':'total_count'},inplace=True)

#Mengubah tipe data kolom 'datetime' menjadi datetime
daily_df['datetime'] = pd.to_datetime(daily_df['datetime'])  
hourly_df['datetime'] = pd.to_datetime(hourly_df['datetime'])  

#Mengubah nama unit
month_map = {1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April', 
             5: 'Mei', 6: 'Juni', 7: 'Juli', 8: 'Agustus', 
             9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'}

season_map = {1:'spring', 2:'summer', 3:'fall', 4:'winter'}

day_map = {0: 'Minggu', 1: 'Senin', 2: 'Selasa', 3: 'Rabu', 4: 'Kamis', 5: 'Jumat', 6: 'Sabtu'}

weather_map = {1:'clear', 2:'cloudy', 3: 'light snow', 4: 'heavy rain'}


daily_df['month'] = daily_df['month'].map(month_map)
hourly_df['month'] = hourly_df['month'].map(month_map)

daily_df['season'] = daily_df['season'].map(season_map)
hourly_df['season'] = hourly_df['season'].map(season_map)

daily_df['weekday'] = daily_df['weekday'].map(day_map)
hourly_df['weekday'] = hourly_df['weekday'].map(day_map)

daily_df['weather_condition'] = daily_df['weather_condition'].map(weather_map)
hourly_df['weather_condition'] = hourly_df['weather_condition'].map(weather_map)
    
    
#Mengubah tipe data objek menjadi kategori
for col in ['season', 'year', 'month', 'holiday', 'weekday', 'workingday', 'weather_condition']:
    daily_df[col] = daily_df[col].astype('category')
    hourly_df[col] = hourly_df[col].astype('category')

#Membuat komponen filter
min_date = daily_df['datetime'].min()
max_date = daily_df['datetime'].max()

with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>Bike Sharing Systems</h1>", unsafe_allow_html=True)
    st.image("https://bikeshare.metro.net/wp-content/uploads/2016/04/cropped-metro-bike-share-favicon.png")
    
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

daily_df = daily_df[(daily_df["datetime"] >= str(start_date)) & 
                (daily_df["datetime"] <= str(end_date))]

hourly_df = hourly_df[(hourly_df["datetime"] >= str(start_date)) & 
                (hourly_df["datetime"] <= str(end_date))]


#Membuat dashboard
st.header('Bike Sharing Systems')

#Dashboard penyewa Harian
daily_rent_df = daily_df.groupby(by='datetime').agg({'total_count': 'sum'}).reset_index()
daily_rent_registered_df = daily_df.groupby(by='datetime').agg({'registered': 'sum'}).reset_index()
daily_rent_casual_df = daily_df.groupby(by='datetime').agg({'casual': 'sum'}).reset_index()
RFM_df = daily_df
recency_overall = (pd.to_datetime('today') - RFM_df['datetime'].max()).days
RFM_df['Frequency'] = daily_df['total_count']
RFM_df['Monetary'] = daily_df['total_count'] 

st.subheader('Daily Rentals (RFM Analysis)')
col1,col2,col3 = st.columns(3)

with col1:
    total_rent_daily = daily_rent_df['total_count'].sum()
    st.metric("Total Rent", value=total_rent_daily)

with col2:
    registered_rent_daily = daily_rent_registered_df['registered'].sum()
    st.metric("Registered Rent", value=registered_rent_daily)
    
with col3:
    casual_rent_daily = daily_rent_casual_df['casual'].sum()
    st.metric("Casual Rent", value=casual_rent_daily)   
    
col4, col5, col6 = st.columns(3) 

with col4:
    st.metric("Recency(Days)", value=recency_overall)

with col5:
    frequency = RFM_df['Frequency'].sum()
    st.metric("Frequency", value=frequency)
    
with col6:
    monetary = RFM_df['Monetary'].sum()
    st.metric("Monetary", value=monetary)
    
    
#Visualisasi pengaruh musim dengan banyaknya penyewa
melted_df = daily_df.melt(id_vars=['season'], value_vars=['registered', 'casual'], 
                          var_name='type', value_name='count')

st.subheader('Jumlah Penyewa Sepeda Berdasarkan Musim')

#Penjelasan 1
st.write("""
Dari visualisasi di bawah terlihat bahwa pada saat spring, tingkat penyewaan sepeda cenderung rendah dibandingkan dengan musim-musim lainnya. 
Saat fall, penyewaan sepeda lebih diminati diikuti dengan summer dan winter baik untuk penyewa casual maupun penyewa registered.
""")

fig, ax = plt.subplots(figsize=(10,5))
sns.barplot(
    x='season',
    y='count',
    hue='type',
    data=melted_df,
    ax=ax
)
ax.set_title('Jumlah Penyewa Sepeda Berdasarkan Musim')
ax.set_xlabel('Musim')
ax.set_ylabel('Jumlah Penyewa Sepeda')

st.pyplot(fig)

#Visualisasi pengaruh jam dengan banyaknya penyewa sepeda
#penyewa registered
melted_df = hourly_df.melt(id_vars=['hour'], value_vars=['registered'], 
                          var_name='type', value_name='count')

st.subheader('Jumlah Penyewa Sepeda registered dan casual berdasarkan jam')

st.write("""
Terlihat bahwa penyewa registered cenderung lebih aktif pada waktu-waktu tertentu. Beberapa di antaranya adalah jam 8 pagi dan jam 5-6 sore.
Sedangkan untuk penyewa kasual penyewa mulai ramai dari jam 10 pagi hingga jam 7 malam.
""")

fig, ax = plt.subplots(figsize=(10,5))
sns.barplot(
    x='hour',
    y='count',
    hue='type',
    data=melted_df,
    ax=ax
)
ax.set_title('Jumlah Penyewa Sepeda registered Berdasarkan Jam')
ax.set_xlabel('Jam')
ax.set_ylabel('Jumlah Penyewa Sepeda')

st.pyplot(fig)  

#penyewa casual
melted_df = hourly_df.melt(id_vars=['hour'], value_vars=['casual'], 
                          var_name='type', value_name='count')

fig, ax = plt.subplots(figsize=(10,5))
sns.barplot(
    x='hour',
    y='count',
    hue='type',
    data=melted_df,
    ax=ax
)
ax.set_title('Jumlah Penyewa Sepeda Berdasarkan Jam')
ax.set_xlabel('Jam')
ax.set_ylabel('Jumlah Penyewa Sepeda')

st.pyplot(fig)  

# Membuat jumlah penyewaan bulanan
month_order = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 
               'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
daily_df['month'] = pd.Categorical(daily_df['month'], categories=month_order, ordered=True)
monthly_rent_df = daily_df.groupby(by=["month","year"]).agg({"total_count": "mean"}).reset_index()
monthly_rent_registered_df = daily_df.groupby(by=["month","year"]).agg({"registered": "mean"}).reset_index()
monthly_rent_casual_df = daily_df.groupby(by=["month","year"]).agg({"casual": "mean"}).reset_index()

st.subheader('Jumlah Penyewa sepeda total berdasarkan Bulan dan Tahun')

st.write("""
Dari visualisasi-visualisasi di bawah, terlihat dari tahun ke tahun terjadi kenaikan penyewa sepeda untuk penyewa teregistrasi maupun penyewa casual.
Selain itu, untuk setiap bulannya memiliki trend masing-masing. Untuk penyewa teregistrasi paling banyak menyewa pada bulan juni di tahun 0 dan bulan september di tahun 1.
Sedangkan untuk penyewa casual paling banyak menyewa di bulan juli pada tahun 0 dan september pada tahun 1.
""")

fig, ax = plt.subplots(figsize=(24, 8))
for year, group in monthly_rent_df.groupby("year"):
    ax.plot(group["month"], group["total_count"], label=year, marker='o', linewidth=2)
ax.set_title("Monthly Rent Data")
ax.set_xlabel("Month")
ax.set_ylabel("Total Count")
ax.legend()
st.pyplot(fig)

st.subheader('Jumlah Penyewa sepeda registered berdasarkan Bulan dan Tahun')
fig, ax = plt.subplots(figsize=(24, 8))
for year, group in monthly_rent_registered_df.groupby("year"):
    ax.plot(group["month"], group["registered"], label=year, marker='o', linewidth=2)
ax.set_title("Monthly Rent Data")
ax.set_xlabel("Month")
ax.set_ylabel("Registered")
ax.legend()
st.pyplot(fig)

st.subheader('Jumlah Penyewa sepeda casual berdasarkan Bulan dan Tahun')
fig, ax = plt.subplots(figsize=(24, 8))
for year, group in monthly_rent_casual_df.groupby("year"):
    ax.plot(group["month"], group["casual"], label=year, marker='o', linewidth=2)
ax.set_title("Monthly Rent Data")
ax.set_xlabel("Month")
ax.set_ylabel("Casual")
ax.legend()
st.pyplot(fig)


# Membuat heatmap korelasi
st.subheader('Heatmap Korelasi')
st.write("""
Berikut ini adalah heatmap korelasi antar kolom yang ada pada dataset.
Tidak terdapat korelasi yang kuat antara frekuensi penyewa sepeda dengan kecepatan angin, suhu dan kelembapan.
""")

numeric_df = daily_df.select_dtypes(include=['float64', 'int64'])
corr_matrix = numeric_df.corr()

fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", linewidths=.5, ax=ax)
ax.set_title('Heatmap Korelasi')
st.pyplot(fig)

st.caption('Copyright (c) Immanuel Mayerd 2023')

import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import requests
from io import BytesIO

# Konfigurasi Halaman Streamlit
st.set_page_config(page_title="Dashboard IBS UID Jatim", layout="wide")
st.title("📊 Dashboard Rekapitulasi Penjualan & Potensi IBS")

# 1. Setup API Google AI Studio (Gemini)
genai.configure(api_key="MASUKKAN_API_KEY_ANDA_DISINI")
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Fungsi Load Data dari Google Sheets
@st.cache_data(ttl=600) # Cache diperbarui setiap 10 menit jika ada perubahan data
def load_data_from_gsheets():
    # Mengambil ID dari link Google Drive Anda
    sheet_id = "1f4uh89R_DTC1qAAJxsBvcDIgKvsMt4yq_sJONBd9jAw"
    export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    
    try:
        # Mengunduh data spreadsheet ke memori
        response = requests.get(export_url)
        response.raise_for_status() 
        xls = pd.ExcelFile(BytesIO(response.content))
        
        # Abaikan sheet rekap, ambil murni sheet UP3 (BJN, BWI, KDR, dll)
        ignore_sheets = ['Sheet7', 'MITRA', 'REKAP', 'REKAP ALL']
        sheet_names = [s for s in xls.sheet_names if s not in ignore_sheets] 
        
        df_list = []
        for sheet in sheet_names:
            temp_df = pd.read_excel(xls, sheet_name=sheet)
            df_list.append(temp_df)
            
        df = pd.concat(df_list, ignore_index=True)
        
        col_nominal = 'Nominal Kontrak / Revenue (Rp)'
        col_status = 'Status Terupdate'
        
        status_won = ['Dealing', 'Pelaksanaan Pekerjaan', 'Closing / selesai Pekerjaan']
        status_potensi = ['Probing', 'Penawaran', 'Negosiasi']
        
        df['Close Won (Rp)'] = df.apply(lambda x: x[col_nominal] if str(x[col_status]).strip() in status_won else 0, axis=1)
        df['Potensi (Rp)'] = df.apply(lambda x: x[col_nominal] if str(x[col_status]).strip() in status_potensi else 0, axis=1)
        
        return df
    
    except Exception as e:
        st.error(f"Gagal mengambil data. Pastikan link Google Sheets disetel ke 'Siapa saja yang memiliki link' (Viewer). Error: {e}")
        return pd.DataFrame()

# Panggil fungsi data
df = load_data_from_gsheets()

if not df.empty:
    # 3. SIDEBAR UNTUK FILTER
    st.sidebar.header("Filter Data")
    pilih_up3 = st.sidebar.multiselect("Pilih UP3:", options=df['UP3'].dropna().unique())
    pilih_klaster = st.sidebar.multiselect("Pilih Klaster Produk:", options=df['Klaster Produk'].dropna().unique())
    
    df_filtered = df.copy()
    if pilih_up3:
        df_filtered = df_filtered[df_filtered['UP3'].isin(pilih_up3)]
    if pilih_klaster:
        df_filtered = df_filtered[df_filtered['Klaster Produk'].isin(pilih_klaster)]

    # 4. TAMPILAN METRIK UTAMA (KPI)
    total_project = len(df_filtered)
    total_revenue = df_filtered['Nominal Kontrak / Revenue (Rp)'].sum()
    total_won = df_filtered['Close Won (Rp)'].sum()
    total_potensi = df_filtered['Potensi (Rp)'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Project", f"{total_project} Unit")
    col2.metric("Total Revenue", f"Rp {total_revenue:,.0f}")
    col3.metric("Close Won", f"Rp {total_won:,.0f}")
    col4.metric("Potensi", f"Rp {total_potensi:,.0f}")
    
    # 5. VISUALISASI GRAFIK
    st.subheader("Distribusi Revenue per Klaster Produk")
    rekap_klaster = df_filtered.groupby('Klaster Produk')['Nominal Kontrak / Revenue (Rp)'].sum().reset_index()
    fig1 = px.bar(rekap_klaster, x='Klaster Produk', y='Nominal Kontrak / Revenue (Rp)', color='Klaster Produk')
    st.plotly_chart(fig1, use_container_width=True)
    
    # 6. INTEGRASI GOOGLE AI STUDIO
    st.subheader("🤖 AI Executive Summary")
    if st.button("Generate Narasi Evaluasi dengan AI"):
        with st.spinner("Menganalisis data..."):
            data_ringkas = f"Total Revenue: {total_revenue}, Close Won: {total_won}, Potensi: {total_potensi}. Produk teratas: {rekap_klaster.to_dict()}."
            prompt = f"Berdasarkan data performa agregat berikut: {data_ringkas}. Buatkan narasi evaluasi analitis singkat dan terstruktur untuk manajemen UID Jatim. Fokus pada evaluasi faktor pendorong dari pencapaian ini dan berikan rekomendasi strategis untuk mengeksekusi nilai 'Potensi' agar menjadi 'Close Won'."
            
            response = model.generate_content(prompt)
            st.info(response.text)

    # 7. TABEL DETAIL
    st.subheader("Data Detail")
    st.dataframe(df_filtered)

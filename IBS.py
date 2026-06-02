import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai

# Konfigurasi Halaman Streamlit
st.set_page_config(page_title="Dashboard IBS UID Jatim", layout="wide")
st.title("📊 Dashboard Rekapitulasi Penjualan & Potensi IBS")

# 1. Setup API Google AI Studio (Gemini)
# Ganti dengan API Key Anda nantinya
genai.configure(api_key="MASUKKAN_API_KEY_ANDA_DISINI")
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Fungsi Load Data (Di-cache agar cepat)
@st.cache_data
def load_data(file_path):
    # Membaca seluruh sheet dalam file Excel
    xls = pd.ExcelFile(file_path)
    # Abaikan sheet rekap jika ada, ambil hanya sheet UP3
    sheet_names = [s for s in xls.sheet_names if "REKAP" not in s.upper()] 
    
    df_list = []
    for sheet in sheet_names:
        temp_df = pd.read_excel(file_path, sheet_name=sheet)
        df_list.append(temp_df)
        
    df = pd.concat(df_list, ignore_index=True)
    
    # Membersihkan nama kolom sesuai gambar Anda
    col_nominal = 'Nominal Kontrak / Revenue (Rp)'
    col_status = 'Status Terupdate'
    
    # Memasukkan logika rumus Close Won & Potensi
    status_won = ['Dealing', 'Pelaksanaan Pekerjaan', 'Closing / selesai Pekerjaan']
    status_potensi = ['Probing', 'Penawaran', 'Negosiasi']
    
    df['Close Won (Rp)'] = df.apply(lambda x: x[col_nominal] if str(x[col_status]).strip() in status_won else 0, axis=1)
    df['Potensi (Rp)'] = df.apply(lambda x: x[col_nominal] if str(x[col_status]).strip() in status_potensi else 0, axis=1)
    
    return df

# Asumsi nama file Excel Anda
try:
    df = load_data("Data_IBS.xlsx")
    
    # 3. SIDEBAR UNTUK FILTER
    st.sidebar.header("Filter Data")
    pilih_up3 = st.sidebar.multiselect("Pilih UP3:", options=df['UP3'].dropna().unique())
    pilih_klaster = st.sidebar.multiselect("Pilih Klaster Produk:", options=df['Klaster Produk'].dropna().unique())
    
    # Terapkan filter
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
    
    # 6. INTEGRASI GOOGLE AI STUDIO (Insight Otomatis)
    st.subheader("🤖 AI Executive Summary & Evaluasi Strategis")
    if st.button("Generate Narasi Evaluasi dengan AI"):
        with st.spinner("Menganalisis data..."):
            # Siapkan ringkasan data untuk dibaca AI
            data_ringkas = f"Total Revenue: {total_revenue}, Close Won: {total_won}, Potensi: {total_potensi}. Produk teratas: {rekap_klaster.to_dict()}."
            
            # Prompt cerdas untuk AI
            prompt = f"Berdasarkan data performa agregat berikut: {data_ringkas}. Buatkan narasi evaluasi analitis singkat dan terstruktur untuk manajemen UID Jatim. Fokus pada evaluasi faktor pendorong (push/pull factor) dari pencapaian ini dan berikan rekomendasi strategis untuk mengeksekusi nilai 'Potensi' agar menjadi 'Close Won'."
            
            response = model.generate_content(prompt)
            st.info(response.text)

    # 7. TABEL DETAIL
    st.subheader("Data Detail")
    st.dataframe(df_filtered)

except FileNotFoundError:
    st.warning("Silakan letakkan file 'Data_IBS.xlsx' di folder yang sama dengan app.py")

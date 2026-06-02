import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import requests
from io import BytesIO

# Konfigurasi Halaman Streamlit
st.set_page_config(page_title="Dashboard IBS UID Jatim", layout="wide")
st.title("📊 Dashboard IBS 2026 UID Jatim")

# 1. Setup API Google AI Studio (Gemini)
genai.configure(api_key="MASUKKAN_API_KEY_ANDA_DISINI")
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Fungsi Load Data dari Google Sheets
@st.cache_data(ttl=600)
def load_data_from_gsheets():
    sheet_id = "1f4uh89R_DTC1qAAJxsBvcDIgKvsMt4yq_sJQNBd9jAw"

    # Link export Excel, bukan link edit Google Sheets
    export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"

    try:
        response = requests.get(export_url)
        response.raise_for_status()

        # Validasi sederhana agar tidak membaca HTML sebagai Excel
        if "text/html" in response.headers.get("Content-Type", ""):
            st.error("Google Sheets belum bisa diakses publik. Ubah akses menjadi: Siapa saja yang memiliki link - Viewer.")
            return pd.DataFrame()

        xls = pd.ExcelFile(BytesIO(response.content), engine="openpyxl")

        # Sheet UP3 yang akan digabung
        target_sheets = [
            "BJN", "BWI", "KDR", "MDN", "MLG", "MJK", "JBR", "STB",
            "PNG", "MDR", "PSR", "GSK", "SDA", "SBU", "SBB", "SBS"
        ]

        df_list = []

        for sheet in target_sheets:
            if sheet in xls.sheet_names:
                temp_df = pd.read_excel(xls, sheet_name=sheet, engine="openpyxl")
                temp_df["Source Sheet"] = sheet
                df_list.append(temp_df)

        if not df_list:
            st.error("Tidak ada sheet UP3 yang ditemukan. Pastikan nama sheet BJN sampai SBS sudah sesuai.")
            return pd.DataFrame()

        df = pd.concat(df_list, ignore_index=True)

        # Hapus baris kosong
        df = df.dropna(how="all")

        col_nominal = "Nominal Kontrak / Revenue (Rp)"
        col_status = "Status Terupdate"

        # Pastikan kolom tersedia
        required_cols = [col_nominal, col_status, "UP3", "Klaster Produk"]
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            st.error(f"Kolom berikut belum ditemukan di file: {missing_cols}")
            return pd.DataFrame()

        # Bersihkan nominal agar bisa dijumlahkan
        df[col_nominal] = (
            df[col_nominal]
            .astype(str)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .str.replace("Rp", "", regex=False)
            .str.strip()
        )

        df[col_nominal] = pd.to_numeric(df[col_nominal], errors="coerce").fillna(0)

        # Bersihkan status
        df[col_status] = df[col_status].astype(str).str.strip()

        status_won = [
            "Dealing",
            "Pelaksanaan Pekerjaan",
            "Closing / selesai Pekerjaan"
        ]

        status_potensi = [
            "Probing",
            "Penawaran",
            "Negosiasi"
        ]

        df["Close Won (Rp)"] = df.apply(
            lambda x: x[col_nominal] if x[col_status] in status_won else 0,
            axis=1
        )

        df["Potensi (Rp)"] = df.apply(
            lambda x: x[col_nominal] if x[col_status] in status_potensi else 0,
            axis=1
        )

        return df

    except Exception as e:
        st.error(f"Gagal mengambil data dari Google Sheets. Error: {e}")
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

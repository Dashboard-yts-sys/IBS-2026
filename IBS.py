import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import requests
from io import BytesIO

# =========================
# KONFIGURASI HALAMAN
# =========================
st.set_page_config(
    page_title="Dashboard IBS 2026 UID Jatim",
    layout="wide"
)

st.title("📊 Dashboard IBS 2026 UID Jatim")


# =========================
# FUNGSI FORMAT ANGKA
# =========================
def format_miliar(value):
    try:
        value = float(value)
        return f"Rp {value / 1_000_000_000:,.2f} M"
    except:
        return "Rp 0,00 M"


def format_angka(value):
    try:
        return f"{float(value):,.0f}"
    except:
        return "0"


def clean_rupiah(value):
    """
    Membersihkan format rupiah dari Google Sheets.
    Contoh:
    799.344.000,00 -> 799344000
    Rp 799.344.000,00 -> 799344000
    """
    if pd.isna(value):
        return 0

    if isinstance(value, (int, float)):
        return value

    value = str(value)
    value = value.replace("Rp", "")
    value = value.replace(" ", "")
    value = value.replace(".", "")
    value = value.replace(",", ".")
    value = value.strip()

    return pd.to_numeric(value, errors="coerce")


# =========================
# SETUP GEMINI
# =========================
# Lebih aman pakai st.secrets di Streamlit Cloud.
# Jika belum pakai secrets, isi langsung API key di bawah.
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    GEMINI_API_KEY = "MASUKKAN_API_KEY_ANDA_DISINI"

if GEMINI_API_KEY != "MASUKKAN_API_KEY_ANDA_DISINI":
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
else:
    model = None


# =========================
# LOAD DATA GOOGLE SHEETS
# =========================
@st.cache_data(ttl=600)
def load_data_from_gsheets():
    sheet_id = "1f4uh89R_DTC1qAAJxsBvcDIgKvsMt4yq_sJQNBd9jAw"

    # Link export Excel
    export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"

    try:
        response = requests.get(export_url)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")

        if "text/html" in content_type:
            st.error(
                "Google Sheets belum bisa diakses publik. "
                "Ubah akses menjadi: Siapa saja yang memiliki link - Viewer."
            )
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
                temp_df["SOURCE_SHEET"] = sheet
                df_list.append(temp_df)

        if not df_list:
            st.error("Tidak ada sheet UP3 yang ditemukan. Pastikan nama sheet BJN sampai SBS sudah sesuai.")
            return pd.DataFrame()

        df = pd.concat(df_list, ignore_index=True)

        # Bersihkan nama kolom
        df.columns = df.columns.astype(str).str.strip()

        # Hapus baris kosong total
        df = df.dropna(how="all")

        # Kolom utama
        col_nominal = "Nominal Kontrak / Revenue (Rp)"
        col_status = "Status Terupdate"
        col_up3 = "UP3"
        col_klaster = "Klaster Produk"
        col_anak_perusahaan = "ANAK PERUSAHAAN"

        required_cols = [
            col_nominal,
            col_status,
            col_up3,
            col_klaster,
            col_anak_perusahaan
        ]

        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            st.error(f"Kolom berikut belum ditemukan di Google Sheets: {missing_cols}")
            st.write("Kolom yang terbaca:", list(df.columns))
            return pd.DataFrame()

        # Bersihkan kolom nominal
        df[col_nominal] = df[col_nominal].apply(clean_rupiah)
        df[col_nominal] = pd.to_numeric(df[col_nominal], errors="coerce").fillna(0)

        # Bersihkan kolom teks
        df[col_status] = df[col_status].astype(str).str.strip()
        df[col_up3] = df[col_up3].astype(str).str.strip()
        df[col_klaster] = df[col_klaster].astype(str).str.strip()
        df[col_anak_perusahaan] = df[col_anak_perusahaan].astype(str).str.strip()

        # Hapus baris tanpa nama pelanggan atau tanpa data penting
        if "Nama Pelanggan" in df.columns:
            df = df[df["Nama Pelanggan"].notna()]

        # Status klasifikasi
        status_won = [
            "Dealing",
            "Pelaksanaan Pekerjaan",
            "Closing / selesai Pekerjaan",
            "Closing",
            "Selesai Pekerjaan"
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


# =========================
# PANGGIL DATA
# =========================
df = load_data_from_gsheets()


# =========================
# DASHBOARD
# =========================
if not df.empty:

    # =========================
    # SIDEBAR FILTER
    # =========================
    st.sidebar.header("Filter Data")

    pilih_up3 = st.sidebar.multiselect(
        "Pilih UP3:",
        options=sorted(df["UP3"].dropna().unique())
    )

    pilih_klaster = st.sidebar.multiselect(
        "Pilih Klaster Produk:",
        options=sorted(df["Klaster Produk"].dropna().unique())
    )

    pilih_anak_perusahaan = st.sidebar.multiselect(
        "Pilih Anak Perusahaan / Subholding:",
        options=sorted(df["ANAK PERUSAHAAN"].dropna().unique())
    )

    pilih_status = st.sidebar.multiselect(
        "Pilih Status Terupdate:",
        options=sorted(df["Status Terupdate"].dropna().unique())
    )

    df_filtered = df.copy()

    if pilih_up3:
        df_filtered = df_filtered[df_filtered["UP3"].isin(pilih_up3)]

    if pilih_klaster:
        df_filtered = df_filtered[df_filtered["Klaster Produk"].isin(pilih_klaster)]

    if pilih_anak_perusahaan:
        df_filtered = df_filtered[df_filtered["ANAK PERUSAHAAN"].isin(pilih_anak_perusahaan)]

    if pilih_status:
        df_filtered = df_filtered[df_filtered["Status Terupdate"].isin(pilih_status)]


    # =========================
    # KPI UTAMA
    # =========================
    total_project = len(df_filtered)
    total_revenue = df_filtered["Nominal Kontrak / Revenue (Rp)"].sum()
    total_won = df_filtered["Close Won (Rp)"].sum()
    total_potensi = df_filtered["Potensi (Rp)"].sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Project", f"{total_project:,.0f} Unit")
    col2.metric("Total Revenue", format_miliar(total_revenue))
    col3.metric("Close Won", format_miliar(total_won))
    col4.metric("Potensi", format_miliar(total_potensi))


    # =========================
    # GRAFIK KLASTER PRODUK
    # =========================
    st.subheader("Distribusi Revenue per Klaster Produk")

    rekap_klaster = (
        df_filtered
        .groupby("Klaster Produk", dropna=False)["Nominal Kontrak / Revenue (Rp)"]
        .sum()
        .reset_index()
    )

    rekap_klaster["Revenue (Miliar Rp)"] = (
        rekap_klaster["Nominal Kontrak / Revenue (Rp)"] / 1_000_000_000
    )

    fig1 = px.bar(
        rekap_klaster,
        x="Klaster Produk",
        y="Revenue (Miliar Rp)",
        color="Klaster Produk",
        text=rekap_klaster["Revenue (Miliar Rp)"].apply(lambda x: f"{x:,.2f} M")
    )

    fig1.update_traces(textposition="outside")

    fig1.update_layout(
        yaxis_title="Revenue (Miliar Rp)",
        xaxis_title="Klaster Produk",
        showlegend=True,
        height=500
    )

    st.plotly_chart(fig1, use_container_width=True)


    # =========================
    # GRAFIK ANAK PERUSAHAAN
    # =========================
    st.subheader("Distribusi Revenue per Anak Perusahaan / Subholding")

    rekap_anak = (
        df_filtered
        .groupby("ANAK PERUSAHAAN", dropna=False)["Nominal Kontrak / Revenue (Rp)"]
        .sum()
        .reset_index()
        .sort_values("Nominal Kontrak / Revenue (Rp)", ascending=False)
    )

    rekap_anak["Revenue (Miliar Rp)"] = (
        rekap_anak["Nominal Kontrak / Revenue (Rp)"] / 1_000_000_000
    )

    fig2 = px.bar(
        rekap_anak,
        x="ANAK PERUSAHAAN",
        y="Revenue (Miliar Rp)",
        color="ANAK PERUSAHAAN",
        text=rekap_anak["Revenue (Miliar Rp)"].apply(lambda x: f"{x:,.2f} M")
    )

    fig2.update_traces(textposition="outside")

    fig2.update_layout(
        yaxis_title="Revenue (Miliar Rp)",
        xaxis_title="Anak Perusahaan / Subholding",
        showlegend=True,
        height=500
    )

    st.plotly_chart(fig2, use_container_width=True)


    # =========================
    # REKAP PER UP3
    # =========================
    st.subheader("Rekap Revenue per UP3")
    
    rekap_up3 = (
        df_filtered
        .groupby("UP3", dropna=False)
        .agg(
            Jumlah_Project=("UP3", "count"),
            Total_Revenue_Rp=("Nominal Kontrak / Revenue (Rp)", "sum"),
            Close_Won_Rp=("Close Won (Rp)", "sum"),
            Potensi_Rp=("Potensi (Rp)", "sum")
        )
        .reset_index()
    )
    
    # Urutkan dari Total Revenue tertinggi ke terendah
    rekap_up3 = rekap_up3.sort_values(
        by="Total_Revenue_Rp",
        ascending=False
    ).reset_index(drop=True)
    
    # Tambahkan nomor urut
    rekap_up3.insert(0, "No", range(1, len(rekap_up3) + 1))
    
    # Format tampilan Rupiah Miliar
    rekap_up3["Total Revenue"] = rekap_up3["Total_Revenue_Rp"].apply(format_miliar)
    rekap_up3["Close Won"] = rekap_up3["Close_Won_Rp"].apply(format_miliar)
    rekap_up3["Potensi"] = rekap_up3["Potensi_Rp"].apply(format_miliar)
    
    st.dataframe(
        rekap_up3[
            [
                "No",
                "UP3",
                "Jumlah_Project",
                "Total Revenue",
                "Close Won",
                "Potensi"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    # =========================
    # AI EXECUTIVE SUMMARY
    # =========================
    st.subheader("🤖 AI Executive Summary")

    if st.button("Generate Narasi Evaluasi dengan AI"):
        if model is None:
            st.warning("API Key Gemini belum diisi. Silakan isi GEMINI_API_KEY di Streamlit Secrets atau langsung di kode.")
        else:
            with st.spinner("Menganalisis data..."):
                data_ringkas = f"""
                Total Project: {total_project}
                Total Revenue: {format_miliar(total_revenue)}
                Close Won: {format_miliar(total_won)}
                Potensi: {format_miliar(total_potensi)}

                Rekap Klaster:
                {rekap_klaster.to_dict(orient='records')}

                Rekap Anak Perusahaan:
                {rekap_anak.to_dict(orient='records')}

                Rekap UP3:
                {rekap_up3.to_dict(orient='records')}
                """

                prompt = f"""
                Berdasarkan data performa IBS UID Jawa Timur berikut:
                {data_ringkas}

                Buatkan narasi executive summary singkat, analitis, dan terstruktur untuk manajemen.
                Gunakan bahasa Indonesia formal.
                Fokus pada:
                1. Gambaran pencapaian revenue dan close won.
                2. Klaster produk yang dominan.
                3. Peran anak perusahaan/subholding.
                4. Potensi yang perlu dikonversi menjadi close won.
                5. Rekomendasi tindak lanjut strategis.
                """

                response = model.generate_content(prompt)
                st.info(response.text)


    # =========================
    # DATA DETAIL
    # =========================
    st.subheader("Data Detail")
    
    df_tampil = df_filtered.copy()
    
    # Reset index agar tidak muncul nomor bawaan dataframe
    df_tampil = df_tampil.reset_index(drop=True)
    
    # Hapus kolom No lama jika sudah ada dari Google Sheets
    if "No" in df_tampil.columns:
        df_tampil = df_tampil.drop(columns=["No"])
    
    # Tambahkan nomor urut baru
    df_tampil.insert(0, "No", range(1, len(df_tampil) + 1))
    
    # Tambahkan kolom nominal dalam miliar
    df_tampil["Nominal Revenue (Miliar Rp)"] = (
        df_tampil["Nominal Kontrak / Revenue (Rp)"] / 1_000_000_000
    )
    
    df_tampil["Close Won (Miliar Rp)"] = (
        df_tampil["Close Won (Rp)"] / 1_000_000_000
    )
    
    df_tampil["Potensi (Miliar Rp)"] = (
        df_tampil["Potensi (Rp)"] / 1_000_000_000
    )
    
    st.dataframe(
        df_tampil,
        use_container_width=True,
        hide_index=True
    )

else:
    st.warning("Data belum berhasil dimuat.")

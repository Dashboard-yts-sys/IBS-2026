import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import requests
from io import BytesIO
from datetime import datetime
from zoneinfo import ZoneInfo

# =====================================================
# KONFIGURASI HALAMAN
# =====================================================
st.set_page_config(
    page_title="Dashboard COREBOOST 2.0 UID JATIM",
    layout="wide"
)

# =====================================================
# CUSTOM CSS
# =====================================================
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1.2rem;
        padding-bottom: 1.5rem;
        max-width: 1450px;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f5f7fb 0%, #eef3ff 100%);
    }

    .hero-box {
        background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 50%, #22c55e 100%);
        padding: 24px 28px;
        border-radius: 22px;
        color: white;
        margin-bottom: 18px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }

    .hero-title-main {
        font-size: 2.8rem;
        font-weight: 900;
        line-height: 1.15;
        margin-bottom: 10px;
        letter-spacing: 0.3px;
    }
    
    .hero-title-sub {
        font-size: 1.45rem;
        font-weight: 700;
        line-height: 1.25;
        margin-bottom: 10px;
        opacity: 0.95;
    }
    
    .hero-subtitle {
        font-size: 0.95rem;
        opacity: 0.92;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 700;
        margin: 8px 0 14px 0;
        color: #0f172a;
    }

    .metric-card {
        padding: 18px 20px;
        border-radius: 18px;
        color: white;
        box-shadow: 0 8px 24px rgba(0,0,0,0.10);
        min-height: 120px;
    }

    .metric-title {
        font-size: 0.95rem;
        opacity: 0.95;
        margin-bottom: 10px;
    }

    .metric-value {
        font-size: 1.85rem;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 8px;
    }

    .metric-sub {
        font-size: 0.85rem;
        opacity: 0.95;
    }

    .card-blue {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
    }

    .card-green {
        background: linear-gradient(135deg, #16a34a, #22c55e);
    }

    .card-orange {
        background: linear-gradient(135deg, #ea580c, #f97316);
    }

    .card-purple {
        background: linear-gradient(135deg, #7c3aed, #a855f7);
    }

    .mini-note {
        padding: 12px 16px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        color: #334155;
        margin-top: 10px;
        margin-bottom: 15px;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# FUNGSI BANTUAN
# =====================================================
def waktu_update_wib():
    bulan_id = {
        1: "Januari",
        2: "Februari",
        3: "Maret",
        4: "April",
        5: "Mei",
        6: "Juni",
        7: "Juli",
        8: "Agustus",
        9: "September",
        10: "Oktober",
        11: "November",
        12: "Desember"
    }

    waktu = datetime.now(ZoneInfo("Asia/Jakarta"))
    return f"{waktu.day:02d} {bulan_id[waktu.month]} {waktu.year}, {waktu.hour:02d}:{waktu.minute:02d} WIB"


def format_miliar(value):
    """
    Format angka menjadi miliar dengan format Indonesia.
    Contoh:
    66860482197 -> Rp 66,86 M
    """
    try:
        value = float(value) / 1_000_000_000
        hasil = f"{value:,.2f}"
        hasil = hasil.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"Rp {hasil} M"
    except:
        return "Rp 0,00 M"


def clean_rupiah(value):
    """
    Membersihkan format rupiah/angka dari Google Sheets.
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


def format_akuntansi(value, desimal=2):
    """
    Format angka menjadi format akuntansi Indonesia:
    titik sebagai pemisah ribuan dan koma sebagai pemisah desimal.
    Contoh:
    252717225 -> 252.717.225,00
    167480000 -> 167.480.000,00
    0 -> 0,00
    """
    try:
        if pd.isna(value):
            return "0,00"

        if isinstance(value, str):
            value = clean_rupiah(value)

        value = float(value)
        hasil = f"{value:,.{desimal}f}"
        hasil = hasil.replace(",", "X").replace(".", ",").replace("X", ".")

        return hasil
    except:
        return "0,00"


def metric_card(title, value, subtitle, css_class):
    st.markdown(
        f"""
        <div class="metric-card {css_class}">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def bersihkan_teks_kosong(series):
    return (
        series
        .astype(str)
        .str.strip()
        .replace(["nan", "None", "NaN", "", "-", "0"], "Belum Terisi")
    )


def standarkan_nama_kolom(df):
    """
    Merapikan nama kolom dari Google Sheets, terutama yang punya enter/baris baru.
    Contoh:
    TANGGAL
    PROBING
    (TGL/BLN/THN)
    menjadi:
    TANGGAL PROBING (TGL/BLN/THN)
    """
    df.columns = (
        df.columns
        .astype(str)
        .str.replace("\n", " ", regex=False)
        .str.replace("\r", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
    return df


def kelompok_produk_keyword(nama_produk):
    """
    Pengelompokan produk IBS berbasis keyword.
    Disusun untuk variasi nama produk yang banyak dan tidak seragam.
    """

    if pd.isna(nama_produk):
        return "Lainnya / Perlu Review"

    teks = str(nama_produk).lower().strip()

    if teks == "" or teks in ["nan", "none", "-", "0"]:
        return "Lainnya / Perlu Review"

    # Normalisasi typo umum
    teks = teks.replace("cubicke", "cubicle")
    teks = teks.replace("cubical", "cubicle")
    teks = teks.replace("kubikle", "kubikel")
    teks = teks.replace("trafokubikel", "trafo kubikel")
    teks = teks.replace("intalasi", "instalasi")
    teks = teks.replace("aksess", "access")
    teks = teks.replace("di gital", "digital")
    teks = teks.replace("kompatible", "compatible")

    # =====================================================
    # URUTAN PENTING:
    # Produk spesifik dicek dulu, baru kategori umum.
    # =====================================================

    # 1. SPKLU / EV Charging
    if any(k in teks for k in [
        "spklu",
        "ev charger",
        "charging station",
        "home charger",
        "private charger",
        "charger dc",
        "charger 30",
        "charger 60",
        "charger 120",
        "mesin spklu",
        "om mesin spklu",
        "uji compatible mesin spklu",
        "uji kompatible mesin spklu",
        "pb kwh meter untuk spklu"
    ]):
        return "SPKLU / EV Charging"

    # 2. Forklift Electric
    if any(k in teks for k in [
        "forklift",
        "forklift listrik",
        "forklift electric",
        "forklift ev"
    ]):
        return "Forklift Electric"

    # 3. Sewa Kendaraan Listrik / EV
    if any(k in teks for k in [
        "mobil listrik",
        "kendaraan listrik",
        "kendaraan ev",
        "sewa ev",
        "sewa mobil listrik",
        "sewa kendaraan",
        "electric ambulance",
        "ambulance",
        "mobil pick up ev",
        " ev",
        "ev ",
        "probing mobil listrik"
    ]):
        return "Sewa Kendaraan Listrik / EV"

    # 4. PLTS / PV Rooftop
    if any(k in teks for k in [
        "plts",
        "pv rooftop",
        "solar",
        "surya",
        "rooftop"
    ]):
        return "PLTS / PV Rooftop"

    # 5. REC
    if any(k in teks for k in [
        "rec",
        "renewable energy certificate"
    ]):
        return "REC"

    # 6. Power Quality / BESS / DRUPS / RUPS
    if any(k in teks for k in [
        "drups",
        "rups",
        "bess",
        "battery energy storage",
        "power quality",
        "ups",
        "onshore connection"
    ]):
        return "Power Quality / BESS / DRUPS / RUPS"

    # 7. Genset / Backup Power
    if any(k in teks for k in [
        "genset",
        "backup",
        "captive power",
        "sewa genset"
    ]):
        return "Genset / Backup Power"

    # 8. Maintenance Trafo & Kubikel
    if any(k in teks for k in [
        "maintenance trafo",
        "maintenance kubikel",
        "pemeliharaan trafo",
        "pemeliharaan kubikel",
        "perbaikan iml",
        "treatment oil",
        "treatment trafo",
        "test semua alat",
        "layanan maintenance",
        "maintenance cubicle",
        "maintenance cubical",
        "maintenance cubikel",
        "pemeliharaan trafo & kubikel",
        "pemeliharaan trafo dan kubikel"
    ]):
        return "Maintenance Trafo & Kubikel"

    # 9. Internet & Connectivity
    if any(k in teks for k in [
        "internet",
        "iconnet",
        "icon+",
        "icon plus",
        "bandwidth",
        "broadband",
        "dedicated",
        "corporate",
        "ftth",
        "ip publik",
        "access point",
        "i-win",
        "koneksi internet"
    ]):
        return "Internet & Connectivity"

    # 10. CCTV & Security
    if any(k in teks for k in [
        "cctv",
        "i-see",
        "firewall",
        "fortigate",
        "security",
        "camera",
        "surveillance"
    ]):
        return "CCTV & Security"

    # 11. Digital Solution / ICT
    if any(k in teks for k in [
        "digital",
        "zoom",
        "aplikasi",
        "server",
        "hardisk",
        "perangkat digital",
        "smart switch",
        "rekening",
        "manage service"
    ]):
        return "Digital Solution / ICT"

    # 12. IML / Instalasi / NIDI / SLO
    if any(k in teks for k in [
        "iml",
        "instalasi",
        "nidi",
        "slo",
        "sertifikat laik operasi",
        "sertifikat laik fungsi",
        "slf",
        "pasang baru",
        "penyambungan",
        "tambah daya",
        "penyambungan sementara",
        "cabling",
        "penarikan kabel",
        "acos"
    ]):
        return "IML / Instalasi / NIDI / SLO"

    # 13. Trafo / Kubikel / Gardu / Power Equipment
    if any(k in teks for k in [
        "trafo",
        "kubikel",
        "cubicle",
        "gardu",
        "capacitor",
        "capasitor",
        "capasitor bank",
        "kapasitor",
        "pengadaan tiang",
        "tiang beton",
        "bushing",
        "incoming",
        "outgoing",
        "kwh meter",
        "pembangunan gardu",
        "power equipment"
    ]):
        return "Trafo / Kubikel / Gardu / Power Equipment"

    # 14. PJU / Public Lighting
    if any(k in teks for k in [
        "pju",
        "lampu jalan",
        "public lighting"
    ]):
        return "PJU / Public Lighting"

    # 15. Voucher Listrik
    if any(k in teks for k in [
        "voucher listrik",
        "voucher pln",
        "token listrik"
    ]):
        return "Voucher Listrik"

    # 16. Asuransi
    if any(k in teks for k in [
        "asuransi"
    ]):
        return "Asuransi"

    # 17. Konstruksi
    if any(k in teks for k in [
        "konstruksi",
        "pembangunan",
        "gedung baru"
    ]):
        return "Konstruksi"

    # 18. Boiler / Electrifying Lifestyle Industrial
    if any(k in teks for k in [
        "electric steam boiler",
        "steam boiler",
        "heater",
        "konversi heater"
    ]):
        return "Electrifying Lifestyle Industrial"

    return "Lainnya / Perlu Review"


def kelompok_produk_ai(nama_produk):
    """
    AI dipakai hanya untuk produk yang tidak terbaca rule keyword.
    Jika GEMINI_API_KEY belum diisi, hasilnya tetap Perlu Review Manual.
    """

    if model is None:
        return "Lainnya / Perlu Review"

    try:
        prompt = f"""
        Klasifikasikan nama produk IBS berikut ke dalam satu kelompok produk yang paling sesuai.

        Nama produk:
        "{nama_produk}"

        Pilih hanya satu dari daftar berikut:
        1. SPKLU / EV Charging
        2. Sewa Kendaraan Listrik / EV
        3. Forklift Electric
        4. PLTS / PV Rooftop
        5. REC
        6. Internet & Connectivity
        7. CCTV & Security
        8. Digital Solution / ICT
        9. IML / Instalasi / NIDI / SLO
        10. Trafo / Kubikel / Gardu / Power Equipment
        11. Maintenance Trafo & Kubikel
        12. Genset / Backup Power
        13. Power Quality / BESS / DRUPS / RUPS
        14. PJU / Public Lighting
        15. Voucher Listrik
        16. Asuransi
        17. Konstruksi
        18. Electrifying Lifestyle Industrial
        19. Lainnya / Perlu Review

        Jawab hanya nama kelompoknya saja, tanpa penjelasan.
        """

        response = model.generate_content(prompt)
        hasil = response.text.strip()

        daftar_kelompok = [
            "SPKLU / EV Charging",
            "Sewa Kendaraan Listrik / EV",
            "Forklift Electric",
            "PLTS / PV Rooftop",
            "REC",
            "Internet & Connectivity",
            "CCTV & Security",
            "Digital Solution / ICT",
            "IML / Instalasi / NIDI / SLO",
            "Trafo / Kubikel / Gardu / Power Equipment",
            "Maintenance Trafo & Kubikel",
            "Genset / Backup Power",
            "Power Quality / BESS / DRUPS / RUPS",
            "PJU / Public Lighting",
            "Voucher Listrik",
            "Asuransi",
            "Konstruksi",
            "Electrifying Lifestyle Industrial",
            "Lainnya / Perlu Review"
        ]

        for kelompok in daftar_kelompok:
            if kelompok.lower() in hasil.lower():
                return kelompok

        return "Lainnya / Perlu Review"

    except:
        return "Lainnya / Perlu Review"


# =====================================================
# SETUP GEMINI
# =====================================================
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    GEMINI_API_KEY = "MASUKKAN_API_KEY_ANDA_DISINI"

if GEMINI_API_KEY != "MASUKKAN_API_KEY_ANDA_DISINI":
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
else:
    model = None


# =====================================================
# LOAD DATA GOOGLE SHEETS
# =====================================================
@st.cache_data(ttl=600)
def load_data_from_gsheets():
    sheet_id = "1f4uh89R_DTC1qAAJxsBvcDIgKvsMt4yq_sJQNBd9jAw"
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
        df = standarkan_nama_kolom(df)

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

        # Bersihkan nominal utama
        df[col_nominal] = df[col_nominal].apply(clean_rupiah)
        df[col_nominal] = pd.to_numeric(df[col_nominal], errors="coerce").fillna(0)

        # Bersihkan kolom Daya jika ada
        if "Daya (VA)" in df.columns:
            df["Daya (VA)"] = df["Daya (VA)"].apply(clean_rupiah)
            df["Daya (VA)"] = pd.to_numeric(df["Daya (VA)"], errors="coerce").fillna(0)

        # Bersihkan kolom Nominal Revenue jika ada
        if "Nominal Revenue (Rp)" in df.columns:
            df["Nominal Revenue (Rp)"] = df["Nominal Revenue (Rp)"].apply(clean_rupiah)
            df["Nominal Revenue (Rp)"] = pd.to_numeric(df["Nominal Revenue (Rp)"], errors="coerce").fillna(0)

        # Bersihkan kolom teks
        df[col_status] = bersihkan_teks_kosong(df[col_status])
        df[col_up3] = bersihkan_teks_kosong(df[col_up3])
        df[col_klaster] = bersihkan_teks_kosong(df[col_klaster])
        df[col_anak_perusahaan] = bersihkan_teks_kosong(df[col_anak_perusahaan])

        if "Nama Produk" in df.columns:
            df["Nama Produk"] = bersihkan_teks_kosong(df["Nama Produk"])

        # Hapus baris tanpa nama pelanggan
        if "Nama Pelanggan" in df.columns:
            df = df[df["Nama Pelanggan"].notna()]
            df["Nama Pelanggan"] = df["Nama Pelanggan"].astype(str).str.strip()
            df = df[df["Nama Pelanggan"] != ""]

        # =====================================================
        # KELOMPOK PRODUK AI
        # =====================================================
        if "Nama Produk" in df.columns:
            # Tahap 1: klasifikasi cepat berbasis keyword
            df["Kelompok Produk AI"] = df["Nama Produk"].apply(kelompok_produk_keyword)

            # Tahap 2: jika masih perlu review dan API Gemini aktif, bantu klasifikasi dengan AI
            if model is not None:
                mask_ai = df["Kelompok Produk AI"] == "Lainnya / Perlu Review"

                produk_unik_ai = (
                    df.loc[mask_ai, "Nama Produk"]
                    .dropna()
                    .astype(str)
                    .drop_duplicates()
                    .tolist()
                )

                mapping_ai = {}

                for produk in produk_unik_ai:
                    mapping_ai[produk] = kelompok_produk_ai(produk)

                if mapping_ai:
                    df.loc[mask_ai, "Kelompok Produk AI"] = df.loc[mask_ai, "Nama Produk"].map(mapping_ai)

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


# =====================================================
# PANGGIL DATA
# =====================================================
df = load_data_from_gsheets()


# =====================================================
# DASHBOARD
# =====================================================
if not df.empty:

    # =====================================================
    # SIDEBAR FILTER
    # =====================================================
    st.sidebar.header("Filter Data")

    pilih_up3 = st.sidebar.multiselect(
        "Pilih UP3:",
        options=sorted(df["UP3"].dropna().unique())
    )

    pilih_klaster = st.sidebar.multiselect(
        "Pilih Klaster Produk:",
        options=sorted(df["Klaster Produk"].dropna().unique())
    )

    pilih_kelompok_produk_ai = st.sidebar.multiselect(
        "Pilih Kelompok Produk AI:",
        options=sorted(df["Kelompok Produk AI"].dropna().unique()) if "Kelompok Produk AI" in df.columns else []
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

    if pilih_kelompok_produk_ai and "Kelompok Produk AI" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["Kelompok Produk AI"].isin(pilih_kelompok_produk_ai)]

    if pilih_anak_perusahaan:
        df_filtered = df_filtered[df_filtered["ANAK PERUSAHAAN"].isin(pilih_anak_perusahaan)]

    if pilih_status:
        df_filtered = df_filtered[df_filtered["Status Terupdate"].isin(pilih_status)]

    # =====================================================
    # KPI
    # =====================================================
    total_project = len(df_filtered)
    total_revenue = df_filtered["Nominal Kontrak / Revenue (Rp)"].sum()
    total_won = df_filtered["Close Won (Rp)"].sum()
    total_potensi = df_filtered["Potensi (Rp)"].sum()
    
    won_ratio = (total_won / total_revenue * 100) if total_revenue > 0 else 0
    potensi_ratio = (total_potensi / total_revenue * 100) if total_revenue > 0 else 0
    avg_project = (total_revenue / total_project) if total_project > 0 else 0
    
    last_update = waktu_update_wib()

    st.markdown(
        f"""
        <div class="hero-box">
            <div class="hero-title-main">📊 Dashboard COREBOOST 2.0 UID JATIM</div>
            <div class="hero-title-sub">Integrated Bussines Solution (IBS) 2026</div>
            <div class="hero-subtitle">
                Monitoring Revenue, Close Won, Potensi, Klaster Produk, Anak Perusahaan/Subholding, dan Project IBS.
                <br>
                <span style="font-size:0.92rem; opacity:0.95;">
                    🕒 Update dashboard: <b>{last_update}</b>
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        metric_card(
            "Total Project",
            f"{total_project:,.0f} Unit",
            f"Rata-rata revenue/proyek: {format_miliar(avg_project)}",
            "card-blue"
        )

    with k2:
        metric_card(
            "Total Revenue",
            format_miliar(total_revenue),
            "Akumulasi seluruh project terfilter",
            "card-green"
        )

    with k3:
        metric_card(
            "Close Won",
            format_miliar(total_won),
            f"Kontribusi {won_ratio:.1f}% dari total revenue",
            "card-orange"
        )

    with k4:
        metric_card(
            "Potensi",
            format_miliar(total_potensi),
            f"Setara {potensi_ratio:.1f}% dari total revenue",
            "card-purple"
        )

    st.markdown(
        f"""
        <div class="mini-note">
        💡 <b>Insight cepat:</b> gunakan filter di sisi kiri untuk memantau performa per UP3, klaster produk, kelompok produk AI, anak perusahaan/subholding, dan status pipeline.
        <br>
        🕒 <b>Data terakhir dimuat:</b> {last_update}
        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # DATA REKAP DASAR
    # =====================================================
    rekap_klaster = (
        df_filtered
        .groupby("Klaster Produk", dropna=False)["Nominal Kontrak / Revenue (Rp)"]
        .sum()
        .reset_index()
    )

    rekap_klaster["Klaster Produk"] = bersihkan_teks_kosong(rekap_klaster["Klaster Produk"])
    rekap_klaster["Revenue_M"] = rekap_klaster["Nominal Kontrak / Revenue (Rp)"] / 1_000_000_000
    rekap_klaster = rekap_klaster.sort_values("Revenue_M", ascending=False)

    rekap_anak = (
        df_filtered
        .groupby("ANAK PERUSAHAAN", dropna=False)["Nominal Kontrak / Revenue (Rp)"]
        .sum()
        .reset_index()
    )

    rekap_anak["ANAK PERUSAHAAN"] = bersihkan_teks_kosong(rekap_anak["ANAK PERUSAHAAN"])
    rekap_anak["Revenue_M"] = rekap_anak["Nominal Kontrak / Revenue (Rp)"] / 1_000_000_000
    rekap_anak = rekap_anak.sort_values("Revenue_M", ascending=False)

    rekap_status = (
        df_filtered
        .groupby("Status Terupdate", dropna=False)["Nominal Kontrak / Revenue (Rp)"]
        .sum()
        .reset_index()
    )

    rekap_status["Status Terupdate"] = bersihkan_teks_kosong(rekap_status["Status Terupdate"])
    rekap_status["Revenue_M"] = rekap_status["Nominal Kontrak / Revenue (Rp)"] / 1_000_000_000
    rekap_status = rekap_status.sort_values("Revenue_M", ascending=False)

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

    rekap_up3["UP3"] = bersihkan_teks_kosong(rekap_up3["UP3"])
    rekap_up3 = rekap_up3.sort_values(
        by="Total_Revenue_Rp",
        ascending=False
    ).reset_index(drop=True)

    if "Kelompok Produk AI" in df_filtered.columns:
        rekap_kelompok_ai = (
            df_filtered
            .groupby("Kelompok Produk AI", dropna=False)["Nominal Kontrak / Revenue (Rp)"]
            .sum()
            .reset_index()
        )

        rekap_kelompok_ai["Kelompok Produk AI"] = bersihkan_teks_kosong(rekap_kelompok_ai["Kelompok Produk AI"])
        rekap_kelompok_ai["Revenue_M"] = rekap_kelompok_ai["Nominal Kontrak / Revenue (Rp)"] / 1_000_000_000
        rekap_kelompok_ai = rekap_kelompok_ai.sort_values("Revenue_M", ascending=False)
    else:
        rekap_kelompok_ai = pd.DataFrame()

    # =====================================================
    # TAB DASHBOARD
    # =====================================================
    tab1, tab2, tab3 = st.tabs(["📈 Overview", "📊 Analisis", "📋 Detail Data"])

    # =====================================================
    # TAB 1 OVERVIEW
    # =====================================================
    with tab1:
        st.markdown('<div class="section-title">Distribusi Revenue</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)

        with c1:
            if rekap_klaster.empty or rekap_klaster["Revenue_M"].sum() <= 0:
                st.info("Belum ada data revenue klaster yang dapat divisualisasikan.")
            else:
                fig_donut = px.pie(
                    rekap_klaster,
                    names="Klaster Produk",
                    values="Revenue_M",
                    hole=0.55,
                    title="Komposisi Revenue per Klaster Produk"
                )

                fig_donut.update_traces(
                    textinfo="percent",
                    textposition="inside",
                    hovertemplate="<b>%{label}</b><br>Revenue: %{value:.2f} M<br>Persentase: %{percent}<extra></extra>"
                )

                fig_donut.update_layout(
                    height=430,
                    legend_title="Klaster Produk",
                    margin=dict(t=60, l=10, r=10, b=10)
                )

                st.plotly_chart(fig_donut, use_container_width=True)

        with c2:
            rekap_anak_bar = rekap_anak[rekap_anak["Revenue_M"] > 0].copy()
        
            rekap_anak_bar["ANAK PERUSAHAAN"] = (
                rekap_anak_bar["ANAK PERUSAHAAN"]
                .astype(str)
                .str.strip()
                .replace(["nan", "None", "NaN", "", "-", "0"], "Belum Terisi")
            )
        
            rekap_anak_bar = (
                rekap_anak_bar
                .sort_values("Revenue_M", ascending=False)
                .head(10)
            )
        
            if rekap_anak_bar.empty:
                st.info("Belum ada data revenue Anak Perusahaan/Subholding yang dapat divisualisasikan.")
            else:
                fig_anak_bar = px.bar(
                    rekap_anak_bar.sort_values("Revenue_M", ascending=True),
                    x="Revenue_M",
                    y="ANAK PERUSAHAAN",
                    orientation="h",
                    text="Revenue_M",
                    color="Revenue_M",
                    color_continuous_scale="Blues",
                    title="Top SHAP Berdasarkan Revenue"
                )
        
                fig_anak_bar.update_traces(
                    texttemplate="%{text:.2f} M",
                    textposition="outside",
                    hovertemplate="<b>%{y}</b><br>Revenue: %{x:.2f} M<extra></extra>"
                )
        
                fig_anak_bar.update_layout(
                    height=430,
                    xaxis_title="Revenue (Miliar Rp)",
                    yaxis_title="",
                    showlegend=False,
                    margin=dict(t=60, l=10, r=30, b=10)
                )
        
                st.plotly_chart(fig_anak_bar, use_container_width=True)

        st.markdown('<div class="section-title">Top 10 UP3 Berdasarkan Revenue</div>', unsafe_allow_html=True)

        rekap_up3_chart = rekap_up3.copy()
        rekap_up3_chart["Revenue_M"] = rekap_up3_chart["Total_Revenue_Rp"] / 1_000_000_000
        rekap_up3_chart = rekap_up3_chart.sort_values("Revenue_M", ascending=False).head(10)

        if rekap_up3_chart.empty or rekap_up3_chart["Revenue_M"].sum() <= 0:
            st.info("Belum ada data revenue UP3 yang dapat divisualisasikan.")
        else:
            fig_top_up3 = px.bar(
                rekap_up3_chart.sort_values("Revenue_M", ascending=True),
                x="Revenue_M",
                y="UP3",
                orientation="h",
                text="Revenue_M",
                color="Revenue_M",
                color_continuous_scale="Viridis",
                title="Top 10 UP3 Berdasarkan Revenue"
            )

            fig_top_up3.update_traces(
                texttemplate="%{text:.2f} M",
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Revenue: %{x:.2f} M<extra></extra>"
            )

            fig_top_up3.update_layout(
                height=500,
                xaxis_title="Revenue (Miliar Rp)",
                yaxis_title="",
                margin=dict(t=60, l=10, r=10, b=10)
            )

            st.plotly_chart(fig_top_up3, use_container_width=True)

        st.markdown('<div class="section-title">Revenue Berdasarkan Kelompok Produk AI</div>', unsafe_allow_html=True)

        if rekap_kelompok_ai.empty or rekap_kelompok_ai["Revenue_M"].sum() <= 0:
            st.info("Belum ada data revenue berdasarkan Kelompok Produk AI.")
        else:
            fig_kelompok_ai = px.bar(
                rekap_kelompok_ai.sort_values("Revenue_M", ascending=True),
                x="Revenue_M",
                y="Kelompok Produk AI",
                orientation="h",
                text="Revenue_M",
                color="Revenue_M",
                color_continuous_scale="Blues",
                title="Revenue per Kelompok Produk AI"
            )

            fig_kelompok_ai.update_traces(
                texttemplate="%{text:.2f} M",
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Revenue: %{x:.2f} M<extra></extra>"
            )

            fig_kelompok_ai.update_layout(
                height=550,
                xaxis_title="Revenue (Miliar Rp)",
                yaxis_title="",
                showlegend=False,
                margin=dict(t=60, l=10, r=30, b=10)
            )

            st.plotly_chart(fig_kelompok_ai, use_container_width=True)

    # =====================================================
    # TAB 2 ANALISIS
    # =====================================================
    with tab2:
        st.markdown('<div class="section-title">Analisis Pipeline dan Komposisi Revenue</div>', unsafe_allow_html=True)

        c3, c4 = st.columns(2)

        with c3:
            if rekap_klaster.empty or rekap_klaster["Revenue_M"].sum() <= 0:
                st.info("Belum ada data revenue klaster yang dapat divisualisasikan.")
            else:
                fig_klaster_bar = px.bar(
                    rekap_klaster,
                    x="Klaster Produk",
                    y="Revenue_M",
                    text="Revenue_M",
                    color="Klaster Produk",
                    title="Revenue per Klaster Produk"
                )

                fig_klaster_bar.update_traces(
                    texttemplate="%{text:.2f} M",
                    textposition="outside"
                )

                fig_klaster_bar.update_layout(
                    height=450,
                    yaxis_title="Revenue (Miliar Rp)",
                    xaxis_title="",
                    margin=dict(t=60, l=10, r=10, b=10)
                )

                st.plotly_chart(fig_klaster_bar, use_container_width=True)

        with c4:
            if rekap_status.empty or rekap_status["Revenue_M"].sum() <= 0:
                st.info("Belum ada data revenue status yang dapat divisualisasikan.")
            else:
                fig_status = px.bar(
                    rekap_status,
                    x="Status Terupdate",
                    y="Revenue_M",
                    text="Revenue_M",
                    color="Status Terupdate",
                    title="Komposisi Revenue per Status"
                )

                fig_status.update_traces(
                    texttemplate="%{text:.2f} M",
                    textposition="outside"
                )

                fig_status.update_layout(
                    height=450,
                    yaxis_title="Revenue (Miliar Rp)",
                    xaxis_title="",
                    margin=dict(t=60, l=10, r=10, b=10)
                )

                st.plotly_chart(fig_status, use_container_width=True)

        st.markdown('<div class="section-title">Rekap Revenue per UP3</div>', unsafe_allow_html=True)

        rekap_up3_tampil = rekap_up3.copy()
        rekap_up3_tampil.insert(0, "No", range(1, len(rekap_up3_tampil) + 1))
        rekap_up3_tampil["Total Revenue"] = rekap_up3_tampil["Total_Revenue_Rp"].apply(format_miliar)
        rekap_up3_tampil["Close Won"] = rekap_up3_tampil["Close_Won_Rp"].apply(format_miliar)
        rekap_up3_tampil["Potensi"] = rekap_up3_tampil["Potensi_Rp"].apply(format_miliar)

        st.dataframe(
            rekap_up3_tampil[
                ["No", "UP3", "Jumlah_Project", "Total Revenue", "Close Won", "Potensi"]
            ],
            use_container_width=True,
            hide_index=True
        )

        st.markdown('<div class="section-title">Rekap Revenue per Kelompok Produk AI</div>', unsafe_allow_html=True)

        if not rekap_kelompok_ai.empty:
            rekap_kelompok_ai_tampil = rekap_kelompok_ai.copy()
            rekap_kelompok_ai_tampil.insert(0, "No", range(1, len(rekap_kelompok_ai_tampil) + 1))
            rekap_kelompok_ai_tampil["Revenue"] = rekap_kelompok_ai_tampil["Nominal Kontrak / Revenue (Rp)"].apply(format_miliar)

            st.dataframe(
                rekap_kelompok_ai_tampil[
                    ["No", "Kelompok Produk AI", "Revenue"]
                ],
                use_container_width=True,
                hide_index=True
            )

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
                    Rasio Close Won: {won_ratio:.1f}%
                    Rasio Potensi: {potensi_ratio:.1f}%

                    Rekap Klaster:
                    {rekap_klaster.to_dict(orient='records')}

                    Rekap Kelompok Produk AI:
                    {rekap_kelompok_ai.to_dict(orient='records') if not rekap_kelompok_ai.empty else []}

                    Rekap Anak Perusahaan:
                    {rekap_anak.to_dict(orient='records')}

                    Rekap Status:
                    {rekap_status.to_dict(orient='records')}

                    Rekap UP3:
                    {rekap_up3_tampil.to_dict(orient='records')}
                    """

                    prompt = f"""
                    Berdasarkan data performa IBS UID Jawa Timur berikut:
                    {data_ringkas}

                    Buatkan narasi executive summary singkat, analitis, dan terstruktur untuk manajemen.
                    Gunakan bahasa Indonesia formal.
                    Fokus pada:
                    1. Gambaran pencapaian revenue dan close won.
                    2. Klaster produk yang dominan.
                    3. Kelompok Produk AI yang paling berkontribusi.
                    4. Peran anak perusahaan/subholding.
                    5. Potensi yang perlu dikonversi menjadi close won.
                    6. Rekomendasi tindak lanjut strategis.
                    """

                    response = model.generate_content(prompt)
                    st.info(response.text)

    # =====================================================
    # TAB 3 DETAIL DATA
    # =====================================================
    with tab3:
        st.markdown('<div class="section-title">Data Detail</div>', unsafe_allow_html=True)

        df_tampil = df_filtered.copy().reset_index(drop=True)

        if "No" in df_tampil.columns:
            df_tampil = df_tampil.drop(columns=["No"])

        df_tampil.insert(0, "No", range(1, len(df_tampil) + 1))

        # =====================================================
        # KOLOM DETAIL DISESUAIKAN DENGAN SOURCE GOOGLE SHEETS
        # =====================================================
        kolom_detail_source = [
            "No",
            "Nama Pelanggan",
            "IDPEL",
            "Daya (VA)",
            "Nama Produk",
            "Kelompok Produk AI",
            "Klaster Produk",
            "ANAK PERUSAHAAN",
            "UP3",
            "ULP",
            "Nama PIC/PAE",
            "No. WA PIC / PAE",
            "Nominal Kontrak / Revenue (Rp)",
            "Nominal Revenue (Rp)",
            "Status Terupdate",
            "Kendala yang dihadapi",
            "Bulan Kunjungan",
            "TANGGAL PROBING (TGL/BLN/THN)",
            "TANGGAL PENAWARAN (TGL/BLN/THN)",
            "TANGGAL CLOSE WON (TGL/BLN/THN)",
            "TANGGAL ENERGIZE/SELESAI PEKERJAAN (TGL/BLN/THN)",
            "Close Won (Rp)",
            "Potensi (Rp)"
        ]

        kolom_tersedia = [kolom for kolom in kolom_detail_source if kolom in df_tampil.columns]
        df_tampil = df_tampil[kolom_tersedia]

        search_nama = st.text_input("🔍 Cari Nama Pelanggan / Produk / UP3 / Status", "")

        if search_nama:
            df_tampil = df_tampil[
                df_tampil.astype(str).apply(
                    lambda row: row.str.contains(search_nama, case=False, na=False).any(),
                    axis=1
                )
            ]

        # =====================================================
        # FORMAT AKUNTANSI UNTUK TAMPILAN DATA DETAIL
        # =====================================================
        kolom_format_akuntansi = [
            "Daya (VA)",
            "Nominal Kontrak / Revenue (Rp)",
            "Close Won (Rp)",
            "Potensi (Rp)",
            "Nominal Revenue (Rp)"
        ]

        df_tampil_display = df_tampil.copy()

        for kolom in kolom_format_akuntansi:
            if kolom in df_tampil_display.columns:
                df_tampil_display[kolom] = df_tampil_display[kolom].apply(format_akuntansi)

        st.dataframe(
            df_tampil_display,
            use_container_width=True,
            hide_index=True
        )

        # CSV tetap menggunakan data asli agar angka masih bisa dihitung di Excel
        csv = df_tampil.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇️ Download Data Filtered (CSV)",
            data=csv,
            file_name="dashboard_ibs_filtered.csv",
            mime="text/csv"
        )

else:
    st.warning("Data belum berhasil dimuat.")

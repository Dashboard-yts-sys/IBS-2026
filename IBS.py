import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

PLOTLY_CONFIG = {
    "displaylogo": False,
    "modeBarButtonsToRemove": [
        "zoom2d", "pan2d", "select2d", "lasso2d",
        "zoomIn2d", "zoomOut2d", "autoScale2d", "resetScale2d"
    ]
}

# =====================================================
# CUSTOM CSS
# =====================================================
st.markdown("""
<style>
    :root {
        --navy: #071B3A;
        --blue: #005BAC;
        --cyan: #00AEEF;
        --green: #00A859;
        --yellow: #FFD200;
        --orange: #F97316;
        --red: #EF4444;
        --purple: #8B5CF6;
        --slate: #64748B;
        --line: #D8E2EE;
        --bg-soft: #F4F8FC;
        --panel: #FFFFFF;
    }

    html, body, [class*="css"] {
        font-family: "Segoe UI", "Inter", Arial, sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 85% 12%, rgba(0,174,239,0.08), transparent 25%),
            radial-gradient(circle at 15% 0%, rgba(0,91,172,0.07), transparent 20%),
            linear-gradient(180deg, #F8FBFF 0%, #F2F7FB 42%, #FFFFFF 100%);
    }

    .main .block-container {
        max-width: 1520px;
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #EFF5FD 0%, #F7FAFD 100%);
        border-right: 1px solid rgba(148,163,184,0.20);
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 1rem;
    }

    .sidebar-box {
        padding: 10px 0 4px 0;
    }

    .sidebar-title {
        font-size: 1.2rem;
        font-weight: 900;
        color: var(--navy);
        margin-bottom: 0.3rem;
    }

    .sidebar-subtitle {
        font-size: 0.78rem;
        color: var(--slate);
        line-height: 1.45;
        margin-bottom: 0.9rem;
    }

    .hero {
        border-radius: 28px;
        padding: 28px 30px;
        color: white;
        margin-bottom: 18px;
        position: relative;
        overflow: hidden;
        background:
            radial-gradient(circle at 80% 20%, rgba(0,174,239,0.20), transparent 20%),
            radial-gradient(circle at 95% 80%, rgba(34,197,94,0.24), transparent 20%),
            linear-gradient(135deg, #061733 0%, #143EA8 50%, #118E5D 100%);
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.18);
    }

    .hero:before {
        content: "";
        position: absolute;
        width: 420px;
        height: 420px;
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 50%;
        right: -120px;
        top: -120px;
    }

    .hero:after {
        content: "";
        position: absolute;
        width: 260px;
        height: 260px;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 50%;
        left: 48%;
        bottom: -150px;
    }

    .hero-grid {
        position: relative;
        z-index: 2;
        display: grid;
        grid-template-columns: 1.5fr 0.8fr;
        gap: 20px;
        align-items: center;
    }

    .hero-left {
        min-width: 0;
    }

    .hero-title-row {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 8px;
    }

    .hero-badge-icon {
        width: 58px;
        height: 58px;
        border-radius: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(255,255,255,0.14);
        border: 1px solid rgba(255,255,255,0.14);
        font-size: 1.7rem;
        box-shadow: inset 0 0 18px rgba(255,255,255,0.10);
    }

    .hero-title {
        font-size: 3rem;
        font-weight: 950;
        line-height: 1.02;
        margin: 0;
        letter-spacing: -0.4px;
    }

    .hero-subtitle {
        font-size: 1.45rem;
        font-weight: 800;
        margin-top: 4px;
        line-height: 1.25;
    }

    .hero-desc {
        margin-top: 12px;
        font-size: 0.95rem;
        color: rgba(255,255,255,0.88);
        line-height: 1.55;
        max-width: 900px;
    }

    .hero-pills {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-top: 14px;
    }

    .hero-pill {
        padding: 8px 12px;
        border-radius: 999px;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.14);
        font-size: 0.78rem;
        font-weight: 800;
        color: rgba(255,255,255,0.96);
    }

    .hero-right {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        align-content: center;
    }

    .floating-card {
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.16);
        border-radius: 22px;
        padding: 16px 14px;
        box-shadow: 0 12px 28px rgba(0,0,0,0.10);
        backdrop-filter: blur(8px);
        min-height: 112px;
    }

    .floating-card.big {
        grid-column: span 2;
        min-height: 108px;
    }

    .floating-icon {
        font-size: 1.7rem;
        margin-bottom: 8px;
    }

    .floating-title {
        font-size: 0.78rem;
        font-weight: 800;
        color: rgba(255,255,255,0.85);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }

    .floating-value {
        font-size: 1.15rem;
        font-weight: 900;
        line-height: 1.2;
        color: white;
    }

    .floating-caption {
        margin-top: 4px;
        font-size: 0.76rem;
        color: rgba(255,255,255,0.82);
        line-height: 1.3;
    }

    .kpi-card {
        position: relative;
        overflow: hidden;
        padding: 18px 18px;
        border-radius: 22px;
        color: white;
        min-height: 126px;
        box-shadow: 0 14px 28px rgba(15, 23, 42, 0.10);
    }

    .kpi-card:after {
        content: "";
        position: absolute;
        width: 120px;
        height: 120px;
        right: -35px;
        top: -35px;
        border-radius: 50%;
        background: rgba(255,255,255,0.16);
    }

    .kpi-blue {
        background: linear-gradient(135deg, #0E56D8 0%, #1AA3E8 100%);
    }

    .kpi-green {
        background: linear-gradient(135deg, #089451 0%, #22C55E 100%);
    }

    .kpi-orange {
        background: linear-gradient(135deg, #EA580C 0%, #F97316 100%);
    }

    .kpi-purple {
        background: linear-gradient(135deg, #7C3AED 0%, #A855F7 100%);
    }

    .kpi-title {
        position: relative;
        z-index: 2;
        font-size: 0.88rem;
        font-weight: 800;
        opacity: 0.98;
        margin-bottom: 10px;
    }

    .kpi-value {
        position: relative;
        z-index: 2;
        font-size: 2rem;
        font-weight: 950;
        line-height: 1.05;
        margin-bottom: 7px;
    }

    .kpi-subtitle {
        position: relative;
        z-index: 2;
        font-size: 0.8rem;
        opacity: 0.94;
        line-height: 1.35;
    }

    .insight-box {
        margin-top: 10px;
        margin-bottom: 14px;
        padding: 14px 16px;
        background: rgba(255,255,255,0.92);
        border: 1px solid rgba(148,163,184,0.24);
        border-radius: 18px;
        color: #334155;
        box-shadow: 0 10px 22px rgba(15, 23, 42, 0.05);
        line-height: 1.55;
        font-size: 0.92rem;
    }

    .mini-stat {
        padding: 16px 18px;
        border-radius: 20px;
        background: rgba(255,255,255,0.94);
        border: 1px solid rgba(148,163,184,0.22);
        box-shadow: 0 10px 22px rgba(15, 23, 42, 0.05);
        min-height: 104px;
    }

    .mini-label {
        color: var(--slate);
        font-size: 0.78rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 5px;
    }

    .mini-value {
        color: var(--navy);
        font-size: 1.35rem;
        font-weight: 950;
        line-height: 1.15;
    }

    .mini-caption {
        margin-top: 6px;
        color: var(--slate);
        font-size: 0.8rem;
        line-height: 1.35;
    }

    .section-title {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 18px;
        margin-bottom: 6px;
    }

    .section-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: linear-gradient(135deg, #005BAC, #00AEEF);
        box-shadow: 0 0 0 7px rgba(0,91,172,0.08);
    }

    .section-title h3 {
        margin: 0;
        color: var(--navy);
        font-size: 1.5rem;
        font-weight: 950;
        letter-spacing: -0.2px;
    }

    .section-subtitle {
        margin-bottom: 14px;
        color: var(--slate);
        font-size: 0.88rem;
    }

    .panel {
        background: rgba(255,255,255,0.96);
        border: 1px solid rgba(148,163,184,0.22);
        border-radius: 24px;
        padding: 14px 16px 6px 16px;
        box-shadow: 0 12px 28px rgba(15, 23, 42, 0.05);
        height: 100%;
    }

    .panel-title {
        font-size: 1rem;
        font-weight: 900;
        color: var(--navy);
        margin-bottom: 2px;
    }

    .panel-subtitle {
        font-size: 0.79rem;
        color: var(--slate);
        margin-bottom: 10px;
        line-height: 1.35;
    }

    .stDataFrame {
        border-radius: 16px;
        overflow: hidden;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(148,163,184,0.22);
        border-radius: 18px;
        overflow: hidden;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
    }

    div[data-baseweb="tab-list"] {
        gap: 10px;
        border-bottom: 1px solid rgba(148,163,184,0.24);
        margin-bottom: 4px;
    }

    button[data-baseweb="tab"] {
        border-radius: 12px 12px 0 0;
        padding-top: 10px;
        padding-bottom: 10px;
        font-weight: 850;
    }

    @media (max-width: 1100px) {
        .hero-grid {
            grid-template-columns: 1fr;
        }

        .hero-title {
            font-size: 2.4rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# FUNGSI BANTUAN
# =====================================================
def waktu_update_wib():
    bulan_id = {
        1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
        5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
        9: "September", 10: "Oktober", 11: "November", 12: "Desember"
    }
    waktu = datetime.now(ZoneInfo("Asia/Jakarta"))
    return f"{waktu.day:02d} {bulan_id[waktu.month]} {waktu.year}, {waktu.hour:02d}:{waktu.minute:02d} WIB"


def format_miliar(value):
    try:
        value = float(value) / 1_000_000_000
        hasil = f"{value:,.2f}"
        hasil = hasil.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"Rp {hasil} M"
    except:
        return "Rp 0,00 M"


def format_chart_miliar(value):
    try:
        hasil = f"{float(value):,.2f}"
        hasil = hasil.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{hasil} M"
    except:
        return "0,00 M"


def format_persen(value):
    try:
        hasil = f"{float(value):,.1f}"
        hasil = hasil.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{hasil}%"
    except:
        return "0,0%"


def clean_rupiah(value):
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


def bersihkan_teks_kosong(series):
    return (
        series.astype(str)
        .str.strip()
        .replace(["nan", "None", "NaN", "", "-", "0"], "Belum Terisi")
    )


def standarkan_nama_kolom(df):
    df.columns = (
        df.columns.astype(str)
        .str.replace("\n", " ", regex=False)
        .str.replace("\r", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
    return df


def render_kpi_card(title, value, subtitle, color_class):
    st.markdown(
        f"""
        <div class="kpi-card {color_class}">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_mini_stat(label, value, caption):
    st.markdown(
        f"""
        <div class="mini-stat">
            <div class="mini-label">{label}</div>
            <div class="mini-value">{value}</div>
            <div class="mini-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_section(title, subtitle=""):
    st.markdown(
        f"""
        <div class="section-title">
            <div class="section-dot"></div>
            <h3>{title}</h3>
        </div>
        <div class="section-subtitle">{subtitle}</div>
        """,
        unsafe_allow_html=True
    )


def render_panel_header(title, subtitle=""):
    st.markdown(
        f"""
        <div class="panel-title">{title}</div>
        <div class="panel-subtitle">{subtitle}</div>
        """,
        unsafe_allow_html=True
    )


def apply_plotly_style(fig, height=420):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(t=10, l=10, r=10, b=10),
        font=dict(family="Segoe UI, Arial", size=12, color="#334155"),
        showlegend=True
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(148,163,184,0.18)",
        zeroline=False
    )
    fig.update_yaxes(
        showgrid=False,
        zeroline=False
    )
    return fig


def safe_top_value(df_in, label_col, value_col):
    if df_in.empty or label_col not in df_in.columns or value_col not in df_in.columns:
        return "-", 0
    temp = df_in.sort_values(value_col, ascending=False)
    if temp.empty:
        return "-", 0
    return str(temp.iloc[0][label_col]), float(temp.iloc[0][value_col])


# =====================================================
# PENGELOMPOKAN PRODUK
# =====================================================
def kelompok_produk_keyword(nama_produk):
    if pd.isna(nama_produk):
        return "Lainnya / Perlu Review"

    teks = str(nama_produk).lower().strip()

    if teks == "" or teks in ["nan", "none", "-", "0"]:
        return "Lainnya / Perlu Review"

    teks = teks.replace("cubicke", "cubicle")
    teks = teks.replace("cubical", "cubicle")
    teks = teks.replace("kubikle", "kubikel")
    teks = teks.replace("trafokubikel", "trafo kubikel")
    teks = teks.replace("intalasi", "instalasi")
    teks = teks.replace("aksess", "access")
    teks = teks.replace("kompatible", "compatible")

    if any(k in teks for k in [
        "spklu", "ev charger", "charging station", "home charger",
        "private charger", "charger dc", "charger 30", "charger 60",
        "charger 120", "mesin spklu", "om mesin spklu",
        "uji compatible mesin spklu", "uji kompatible mesin spklu",
        "pb kwh meter untuk spklu"
    ]):
        return "SPKLU / EV Charging"

    if any(k in teks for k in [
        "forklift", "forklift listrik", "forklift electric", "forklift ev"
    ]):
        return "Forklift Electric"

    if any(k in teks for k in [
        "mobil listrik", "kendaraan listrik", "kendaraan ev", "sewa ev",
        "sewa mobil listrik", "sewa kendaraan", "electric ambulance",
        "ambulance", "mobil pick up ev", " ev", "ev ", "probing mobil listrik"
    ]):
        return "Sewa Kendaraan Listrik / EV"

    if any(k in teks for k in [
        "plts", "pv rooftop", "solar", "surya", "rooftop"
    ]):
        return "PLTS / PV Rooftop"

    if any(k in teks for k in ["rec", "renewable energy certificate"]):
        return "REC"

    if any(k in teks for k in [
        "drups", "rups", "bess", "battery energy storage",
        "power quality", "ups", "onshore connection"
    ]):
        return "Power Quality / BESS / DRUPS / RUPS"

    if any(k in teks for k in ["genset", "backup", "captive power", "sewa genset"]):
        return "Genset / Backup Power"

    if any(k in teks for k in [
        "maintenance trafo", "maintenance kubikel", "pemeliharaan trafo",
        "pemeliharaan kubikel", "perbaikan iml", "treatment oil",
        "treatment trafo", "test semua alat", "layanan maintenance",
        "maintenance cubicle", "maintenance cubical", "maintenance cubikel",
        "pemeliharaan trafo & kubikel", "pemeliharaan trafo dan kubikel"
    ]):
        return "Maintenance Trafo & Kubikel"

    if any(k in teks for k in [
        "internet", "iconnet", "icon+", "icon plus", "bandwidth",
        "broadband", "dedicated", "corporate", "ftth", "ip publik",
        "access point", "i-win", "koneksi internet"
    ]):
        return "Internet & Connectivity"

    if any(k in teks for k in [
        "cctv", "i-see", "firewall", "fortigate", "security", "camera", "surveillance"
    ]):
        return "CCTV & Security"

    if any(k in teks for k in [
        "digital", "zoom", "aplikasi", "server", "hardisk",
        "perangkat digital", "smart switch", "rekening", "manage service"
    ]):
        return "Digital Solution / ICT"

    if any(k in teks for k in [
        "iml", "instalasi", "nidi", "slo", "sertifikat laik operasi",
        "sertifikat laik fungsi", "slf", "pasang baru", "penyambungan",
        "tambah daya", "penyambungan sementara", "cabling", "penarikan kabel", "acos"
    ]):
        return "IML / Instalasi / NIDI / SLO"

    if any(k in teks for k in [
        "trafo", "kubikel", "cubicle", "gardu", "capacitor",
        "capasitor", "capasitor bank", "kapasitor", "pengadaan tiang",
        "tiang beton", "bushing", "incoming", "outgoing", "kwh meter",
        "pembangunan gardu", "power equipment"
    ]):
        return "Trafo / Kubikel / Gardu / Power Equipment"

    if any(k in teks for k in ["pju", "lampu jalan", "public lighting"]):
        return "PJU / Public Lighting"

    if any(k in teks for k in ["voucher listrik", "voucher pln", "token listrik"]):
        return "Voucher Listrik"

    if "asuransi" in teks:
        return "Asuransi"

    if any(k in teks for k in ["konstruksi", "pembangunan", "gedung baru"]):
        return "Konstruksi"

    if any(k in teks for k in ["electric steam boiler", "steam boiler", "heater", "konversi heater"]):
        return "Electrifying Lifestyle Industrial"

    return "Lainnya / Perlu Review"


def kelompok_produk_ai(nama_produk):
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

        daftar = [
            "SPKLU / EV Charging", "Sewa Kendaraan Listrik / EV", "Forklift Electric",
            "PLTS / PV Rooftop", "REC", "Internet & Connectivity", "CCTV & Security",
            "Digital Solution / ICT", "IML / Instalasi / NIDI / SLO",
            "Trafo / Kubikel / Gardu / Power Equipment", "Maintenance Trafo & Kubikel",
            "Genset / Backup Power", "Power Quality / BESS / DRUPS / RUPS",
            "PJU / Public Lighting", "Voucher Listrik", "Asuransi",
            "Konstruksi", "Electrifying Lifestyle Industrial", "Lainnya / Perlu Review"
        ]

        for x in daftar:
            if x.lower() in hasil.lower():
                return x

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
            st.error("Google Sheets belum bisa diakses publik. Ubah akses menjadi: Siapa saja yang memiliki link - Viewer.")
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
            st.error("Tidak ada sheet UP3 yang ditemukan.")
            return pd.DataFrame()

        df = pd.concat(df_list, ignore_index=True)
        df = standarkan_nama_kolom(df)
        df = df.dropna(how="all")

        col_nominal = "Nominal Kontrak / Revenue (Rp)"
        col_status = "Status Terupdate"
        col_up3 = "UP3"
        col_klaster = "Klaster Produk"
        col_anak = "ANAK PERUSAHAAN"

        required_cols = [col_nominal, col_status, col_up3, col_klaster, col_anak]
        missing = [col for col in required_cols if col not in df.columns]

        if missing:
            st.error(f"Kolom berikut belum ditemukan di Google Sheets: {missing}")
            st.write("Kolom yang terbaca:", list(df.columns))
            return pd.DataFrame()

        df[col_nominal] = df[col_nominal].apply(clean_rupiah)
        df[col_nominal] = pd.to_numeric(df[col_nominal], errors="coerce").fillna(0)

        if "Daya (VA)" in df.columns:
            df["Daya (VA)"] = df["Daya (VA)"].apply(clean_rupiah)
            df["Daya (VA)"] = pd.to_numeric(df["Daya (VA)"], errors="coerce").fillna(0)

        if "Nominal Revenue (Rp)" in df.columns:
            df["Nominal Revenue (Rp)"] = df["Nominal Revenue (Rp)"].apply(clean_rupiah)
            df["Nominal Revenue (Rp)"] = pd.to_numeric(df["Nominal Revenue (Rp)"], errors="coerce").fillna(0)

        df[col_status] = bersihkan_teks_kosong(df[col_status])
        df[col_up3] = bersihkan_teks_kosong(df[col_up3])
        df[col_klaster] = bersihkan_teks_kosong(df[col_klaster])
        df[col_anak] = bersihkan_teks_kosong(df[col_anak])

        if "Nama Produk" in df.columns:
            df["Nama Produk"] = bersihkan_teks_kosong(df["Nama Produk"])

        if "Nama Pelanggan" in df.columns:
            df = df[df["Nama Pelanggan"].notna()]
            df["Nama Pelanggan"] = df["Nama Pelanggan"].astype(str).str.strip()
            df = df[df["Nama Pelanggan"] != ""]

        if "Nama Produk" in df.columns:
            df["Kelompok Produk"] = df["Nama Produk"].apply(kelompok_produk_keyword)

            if model is not None:
                mask_ai = df["Kelompok Produk"] == "Lainnya / Perlu Review"

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
                    df.loc[mask_ai, "Kelompok Produk"] = df.loc[mask_ai, "Nama Produk"].map(mapping_ai)

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
# AMBIL DATA
# =====================================================
df = load_data_from_gsheets()

# =====================================================
# DASHBOARD
# =====================================================
if not df.empty:

    # =====================================================
    # SIDEBAR
    # =====================================================
    st.sidebar.markdown(
        """
        <div class="sidebar-box">
            <div class="sidebar-title">🔎 Filter Data</div>
            <div class="sidebar-subtitle">
                Gunakan filter untuk melihat performa IBS berdasarkan wilayah, klaster produk,
                kelompok produk, subholding/anak perusahaan, dan status pipeline.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    pilih_up3 = st.sidebar.multiselect(
        "Pilih UP3:",
        options=sorted(df["UP3"].dropna().unique())
    )

    pilih_klaster = st.sidebar.multiselect(
        "Pilih Klaster Produk:",
        options=sorted(df["Klaster Produk"].dropna().unique())
    )

    pilih_kelompok = st.sidebar.multiselect(
        "Pilih Kelompok Produk:",
        options=sorted(df["Kelompok Produk"].dropna().unique()) if "Kelompok Produk" in df.columns else []
    )

    pilih_anak = st.sidebar.multiselect(
        "Pilih Anak Perusahaan / Subholding:",
        options=sorted(df["ANAK PERUSAHAAN"].dropna().unique())
    )

    pilih_status = st.sidebar.multiselect(
        "Pilih Status Terupdate:",
        options=sorted(df["Status Terupdate"].dropna().unique())
    )

    if st.sidebar.button("🔄 Reset Cache Data"):
        st.cache_data.clear()
        st.rerun()

    # =====================================================
    # FILTER DATA
    # =====================================================
    df_filtered = df.copy()

    if pilih_up3:
        df_filtered = df_filtered[df_filtered["UP3"].isin(pilih_up3)]

    if pilih_klaster:
        df_filtered = df_filtered[df_filtered["Klaster Produk"].isin(pilih_klaster)]

    if pilih_kelompok:
        df_filtered = df_filtered[df_filtered["Kelompok Produk"].isin(pilih_kelompok)]

    if pilih_anak:
        df_filtered = df_filtered[df_filtered["ANAK PERUSAHAAN"].isin(pilih_anak)]

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

    # =====================================================
    # REKAP DASAR
    # =====================================================
    rekap_klaster = (
        df_filtered
        .groupby("Klaster Produk", dropna=False)["Nominal Kontrak / Revenue (Rp)"]
        .sum()
        .reset_index()
    )
    rekap_klaster["Revenue_M"] = rekap_klaster["Nominal Kontrak / Revenue (Rp)"] / 1_000_000_000
    rekap_klaster = rekap_klaster.sort_values("Revenue_M", ascending=False)

    rekap_anak = (
        df_filtered
        .groupby("ANAK PERUSAHAAN", dropna=False)["Nominal Kontrak / Revenue (Rp)"]
        .sum()
        .reset_index()
    )
    rekap_anak["Revenue_M"] = rekap_anak["Nominal Kontrak / Revenue (Rp)"] / 1_000_000_000
    rekap_anak = rekap_anak.sort_values("Revenue_M", ascending=False)

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
    rekap_up3["Revenue_M"] = rekap_up3["Total_Revenue_Rp"] / 1_000_000_000
    rekap_up3 = rekap_up3.sort_values("Total_Revenue_Rp", ascending=False)

    rekap_status_revenue = (
        df_filtered
        .groupby("Status Terupdate", dropna=False)["Nominal Kontrak / Revenue (Rp)"]
        .sum()
        .reset_index()
    )
    rekap_status_revenue["Revenue_M"] = rekap_status_revenue["Nominal Kontrak / Revenue (Rp)"] / 1_000_000_000
    rekap_status_revenue = rekap_status_revenue.sort_values("Revenue_M", ascending=False)

    rekap_status_count = (
        df_filtered
        .groupby("Status Terupdate", dropna=False)
        .size()
        .reset_index(name="Jumlah_Project")
    )
    rekap_status_count = rekap_status_count.sort_values("Jumlah_Project", ascending=False)

    rekap_kelompok = (
        df_filtered
        .groupby("Kelompok Produk", dropna=False)
        .agg(
            Revenue_Rp=("Nominal Kontrak / Revenue (Rp)", "sum"),
            Jumlah_Project=("Kelompok Produk", "count"),
            Close_Won_Rp=("Close Won (Rp)", "sum"),
            Potensi_Rp=("Potensi (Rp)", "sum")
        )
        .reset_index()
    )
    rekap_kelompok["Revenue_M"] = rekap_kelompok["Revenue_Rp"] / 1_000_000_000
    rekap_kelompok["CloseWonRatio"] = rekap_kelompok.apply(
        lambda x: (x["Close_Won_Rp"] / x["Revenue_Rp"] * 100) if x["Revenue_Rp"] > 0 else 0,
        axis=1
    )
    rekap_kelompok = rekap_kelompok.sort_values("Revenue_M", ascending=False)

    top_up3, top_up3_val = safe_top_value(rekap_up3, "UP3", "Total_Revenue_Rp")
    top_shap, top_shap_val = safe_top_value(rekap_anak, "ANAK PERUSAHAAN", "Nominal Kontrak / Revenue (Rp)")
    top_kelompok, top_kelompok_val = safe_top_value(rekap_kelompok, "Kelompok Produk", "Revenue_Rp")

    # =====================================================
    # HERO
    # =====================================================
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-grid">
                <div class="hero-left">
                    <div class="hero-title-row">
                        <div class="hero-badge-icon">📊</div>
                        <div>
                            <div class="hero-title">Dashboard COREBOOST 2.0 UID JATIM</div>
                            <div class="hero-subtitle">Integrated Business Solution (IBS) 2026</div>
                        </div>
                    </div>

                    <div class="hero-desc">
                        Dashboard eksekutif untuk memantau revenue, close won, potensi,
                        kelompok produk, kontribusi SHAP, performa UP3, dan status pipeline IBS
                        secara lebih rapi, informatif, dan mudah dibaca.
                    </div>

                    <div class="hero-pills">
                        <div class="hero-pill">🕒 Update: {last_update}</div>
                        <div class="hero-pill">🏢 Top UP3: {top_up3}</div>
                        <div class="hero-pill">🤝 Top SHAP: {top_shap}</div>
                        <div class="hero-pill">⚡ Top Produk: {top_kelompok}</div>
                    </div>
                </div>

                <div class="hero-right">
                    <div class="floating-card">
                        <div class="floating-icon">⚡</div>
                        <div class="floating-title">Green & Energy</div>
                        <div class="floating-value">PLTS • REC • Power Quality</div>
                        <div class="floating-caption">Mencerminkan portofolio solusi energi dan elektrifikasi.</div>
                    </div>

                    <div class="floating-card">
                        <div class="floating-icon">🚗</div>
                        <div class="floating-title">EV Ecosystem</div>
                        <div class="floating-value">SPKLU • EV • Forklift</div>
                        <div class="floating-caption">Memperlihatkan akselerasi produk EV dan charging.</div>
                    </div>

                    <div class="floating-card big">
                        <div class="floating-icon">📡</div>
                        <div class="floating-title">Connectivity & Services</div>
                        <div class="floating-value">Internet • Digital • Instalasi • Maintenance</div>
                        <div class="floating-caption">Representasi layanan IBS yang beragam dalam satu tampilan dashboard.</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # KPI CARDS
    # =====================================================
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        render_kpi_card(
            "📌 Total Project",
            f"{total_project:,.0f} Unit",
            f"Rata-rata revenue/proyek {format_miliar(avg_project)}",
            "kpi-blue"
        )

    with k2:
        render_kpi_card(
            "💰 Total Revenue",
            format_miliar(total_revenue),
            "Akumulasi seluruh project terfilter",
            "kpi-green"
        )

    with k3:
        render_kpi_card(
            "🏆 Close Won",
            format_miliar(total_won),
            f"Kontribusi {format_persen(won_ratio)} dari total revenue",
            "kpi-orange"
        )

    with k4:
        render_kpi_card(
            "🚀 Potensi",
            format_miliar(total_potensi),
            f"Setara {format_persen(potensi_ratio)} dari total revenue",
            "kpi-purple"
        )

    # =====================================================
    # INSIGHT STRIP
    # =====================================================
    st.markdown(
        f"""
        <div class="insight-box">
            💡 <b>Insight cepat:</b>
            Top UP3 saat ini <b>{top_up3}</b> dengan kontribusi <b>{format_miliar(top_up3_val)}</b>.
            Top SHAP adalah <b>{top_shap}</b> dengan revenue <b>{format_miliar(top_shap_val)}</b>.
            Kelompok produk terbesar adalah <b>{top_kelompok}</b> dengan revenue <b>{format_miliar(top_kelompok_val)}</b>.
            <br>
            🕒 <b>Data terakhir dimuat:</b> {last_update}
        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # MINI STATS
    # =====================================================
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        render_mini_stat("Top UP3", top_up3, f"Revenue {format_miliar(top_up3_val)}")

    with m2:
        render_mini_stat("Top SHAP", top_shap, f"Revenue {format_miliar(top_shap_val)}")

    with m3:
        render_mini_stat("Top Kelompok Produk", top_kelompok, f"Revenue {format_miliar(top_kelompok_val)}")

    with m4:
        render_mini_stat("Rasio Close Won", format_persen(won_ratio), "Indikator konversi terhadap total revenue")

    # =====================================================
    # TABS
    # =====================================================
    tab1, tab2, tab3 = st.tabs(["📈 Overview", "📊 Analisis", "📋 Detail Data"])

    # =====================================================
    # TAB 1 - OVERVIEW
    # =====================================================
    with tab1:
        render_section(
            "Distribusi Revenue",
            "Komposisi revenue berdasarkan klaster produk, SHAP, UP3, status pipeline, dan kelompok produk."
        )

        row1_col1, row1_col2 = st.columns(2)

        with row1_col1:
            with st.container():
                st.markdown('<div class="panel">', unsafe_allow_html=True)
                render_panel_header(
                    "Komposisi Revenue per Klaster Produk",
                    "Menunjukkan proporsi revenue tiap klaster IBS."
                )

                if not rekap_klaster.empty and rekap_klaster["Revenue_M"].sum() > 0:
                    warna_klaster = {
                        "GREEN ENERGY SOLUTION": "#00A859",
                        "OPERATION EXCELLENT SOLUTION": "#005BAC",
                        "DIGITAL TECHNOLOGY SOLUTION": "#00AEEF",
                        "POWER CONNECTION SOLUTION": "#FFD200",
                        "MANAGEMENT SYSTEM SOLUTION": "#8B5CF6"
                    }

                    fig_donut = px.pie(
                        rekap_klaster,
                        names="Klaster Produk",
                        values="Revenue_M",
                        hole=0.62,
                        color="Klaster Produk",
                        color_discrete_map=warna_klaster
                    )

                    fig_donut.update_traces(
                        textinfo="percent",
                        textposition="inside",
                        marker=dict(line=dict(color="white", width=2)),
                        hovertemplate="<b>%{label}</b><br>Revenue: %{value:.2f} M<br>Persentase: %{percent}<extra></extra>"
                    )

                    fig_donut.update_layout(
                        template="plotly_white",
                        paper_bgcolor="rgba(0,0,0,0)",
                        height=420,
                        margin=dict(t=10, l=10, r=10, b=10),
                        legend=dict(
                            orientation="v",
                            x=1.02,
                            y=0.5,
                            xanchor="left",
                            yanchor="middle"
                        )
                    )

                    fig_donut.add_annotation(
                        text=f"<b>{format_chart_miliar(total_revenue / 1_000_000_000)}</b><br><span style='font-size:12px'>Total</span>",
                        showarrow=False,
                        x=0.5,
                        y=0.5,
                        font=dict(size=18, color="#071B3A")
                    )

                    st.plotly_chart(fig_donut, use_container_width=True, config=PLOTLY_CONFIG)
                else:
                    st.info("Belum ada data revenue klaster.")

                st.markdown('</div>', unsafe_allow_html=True)

        with row1_col2:
            with st.container():
                st.markdown('<div class="panel">', unsafe_allow_html=True)
                render_panel_header(
                    "Top SHAP Berdasarkan Revenue",
                    "Subholding / anak perusahaan dengan kontribusi revenue terbesar."
                )

                if not rekap_anak.empty and rekap_anak["Revenue_M"].sum() > 0:
                    temp = rekap_anak.sort_values("Revenue_M", ascending=False).head(8).copy()
                    temp["Label"] = temp["Revenue_M"].apply(format_chart_miliar)

                    fig_shap = px.bar(
                        temp.sort_values("Revenue_M", ascending=True),
                        x="Revenue_M",
                        y="ANAK PERUSAHAAN",
                        orientation="h",
                        text="Label",
                        color="Revenue_M",
                        color_continuous_scale=["#DCEFFF", "#00AEEF", "#0C3E94"]
                    )

                    fig_shap.update_traces(
                        textposition="outside",
                        cliponaxis=False,
                        hovertemplate="<b>%{y}</b><br>Revenue: %{x:.2f} M<extra></extra>"
                    )

                    fig_shap.update_layout(coloraxis_showscale=False)
                    fig_shap = apply_plotly_style(fig_shap, height=420)
                    fig_shap.update_xaxes(title="Revenue (Miliar Rp)")
                    fig_shap.update_yaxes(title="")

                    st.plotly_chart(fig_shap, use_container_width=True, config=PLOTLY_CONFIG)
                else:
                    st.info("Belum ada data SHAP.")

                st.markdown('</div>', unsafe_allow_html=True)

        row2_col1, row2_col2 = st.columns(2)

        with row2_col1:
            with st.container():
                st.markdown('<div class="panel">', unsafe_allow_html=True)
                render_panel_header(
                    "Top 10 UP3 Berdasarkan Revenue",
                    "Peringkat UP3 berdasarkan total revenue project IBS."
                )

                if not rekap_up3.empty and rekap_up3["Revenue_M"].sum() > 0:
                    temp = rekap_up3.sort_values("Revenue_M", ascending=False).head(10).copy()
                    temp["Label"] = temp["Revenue_M"].apply(format_chart_miliar)

                    fig_up3 = px.bar(
                        temp.sort_values("Revenue_M", ascending=True),
                        x="Revenue_M",
                        y="UP3",
                        orientation="h",
                        text="Label",
                        color="Revenue_M",
                        color_continuous_scale=["#DCEFFF", "#00AEEF", "#005BAC"]
                    )

                    fig_up3.update_traces(
                        textposition="outside",
                        cliponaxis=False,
                        hovertemplate="<b>%{y}</b><br>Revenue: %{x:.2f} M<extra></extra>"
                    )

                    fig_up3.update_layout(coloraxis_showscale=False)
                    fig_up3 = apply_plotly_style(fig_up3, height=470)
                    fig_up3.update_xaxes(title="Revenue (Miliar Rp)")
                    fig_up3.update_yaxes(title="")

                    st.plotly_chart(fig_up3, use_container_width=True, config=PLOTLY_CONFIG)
                else:
                    st.info("Belum ada data UP3.")

                st.markdown('</div>', unsafe_allow_html=True)

        with row2_col2:
            with st.container():
                st.markdown('<div class="panel">', unsafe_allow_html=True)
                render_panel_header(
                    "Pipeline per Status",
                    "Distribusi jumlah project berdasarkan status terupdate."
                )

                if not rekap_status_count.empty:
                    order_status = [
                        "Probing", "Penawaran", "Negosiasi", "Dealing",
                        "Pelaksanaan Pekerjaan", "Closing / selesai Pekerjaan",
                        "Closing", "Selesai Pekerjaan"
                    ]

                    temp = rekap_status_count.copy()
                    temp["Status Terupdate"] = pd.Categorical(
                        temp["Status Terupdate"],
                        categories=order_status,
                        ordered=True
                    )
                    temp = temp.sort_values("Status Terupdate").dropna()

                    fig_funnel = go.Figure(
                        go.Funnel(
                            y=temp["Status Terupdate"],
                            x=temp["Jumlah_Project"],
                            textinfo="value",
                            textposition="inside",
                            marker=dict(
                                color=["#7DD3FC", "#38BDF8", "#0EA5E9", "#22C55E", "#F59E0B", "#F97316", "#8B5CF6", "#005BAC"],
                                line=dict(width=1, color="white")
                            ),
                            opacity=0.95
                        )
                    )

                    fig_funnel.update_layout(
                        template="plotly_white",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        height=470,
                        margin=dict(t=10, l=10, r=10, b=10),
                        font=dict(family="Segoe UI, Arial", size=12, color="#334155")
                    )

                    st.plotly_chart(fig_funnel, use_container_width=True, config=PLOTLY_CONFIG)
                else:
                    st.info("Belum ada data status pipeline.")

                st.markdown('</div>', unsafe_allow_html=True)

        with st.container():
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            render_panel_header(
                "Revenue Berdasarkan Kelompok Produk",
                "Kelompok produk disusun dari normalisasi nama produk yang bervariasi."
            )

            if not rekap_kelompok.empty and rekap_kelompok["Revenue_M"].sum() > 0:
                temp = rekap_kelompok.sort_values("Revenue_M", ascending=False).head(18).copy()
                temp["Label"] = temp["Revenue_M"].apply(format_chart_miliar)

                fig_kelompok = px.bar(
                    temp.sort_values("Revenue_M", ascending=True),
                    x="Revenue_M",
                    y="Kelompok Produk",
                    orientation="h",
                    text="Label",
                    color="Revenue_M",
                    color_continuous_scale=["#E8F5FF", "#4FC3F7", "#0A2A63"]
                )

                fig_kelompok.update_traces(
                    textposition="outside",
                    cliponaxis=False,
                    hovertemplate="<b>%{y}</b><br>Revenue: %{x:.2f} M<extra></extra>"
                )

                fig_kelompok.update_layout(coloraxis_showscale=False)
                fig_kelompok = apply_plotly_style(fig_kelompok, height=620)
                fig_kelompok.update_xaxes(title="Revenue (Miliar Rp)")
                fig_kelompok.update_yaxes(title="")

                st.plotly_chart(fig_kelompok, use_container_width=True, config=PLOTLY_CONFIG)
            else:
                st.info("Belum ada data kelompok produk.")

            st.markdown('</div>', unsafe_allow_html=True)

    # =====================================================
    # TAB 2 - ANALISIS
    # =====================================================
    with tab2:
        render_section(
            "Analisis Pipeline dan Portofolio",
            "Analisis lanjutan untuk mendukung evaluasi manajemen dan tindak lanjut."
        )

        anal_col1, anal_col2 = st.columns(2)

        with anal_col1:
            with st.container():
                st.markdown('<div class="panel">', unsafe_allow_html=True)
                render_panel_header(
                    "Revenue per Status Terupdate",
                    "Melihat nilai revenue pada masing-masing tahap pipeline."
                )

                if not rekap_status_revenue.empty and rekap_status_revenue["Revenue_M"].sum() > 0:
                    temp = rekap_status_revenue.copy()
                    temp["Label"] = temp["Revenue_M"].apply(format_chart_miliar)

                    fig_status = px.bar(
                        temp.sort_values("Revenue_M", ascending=True),
                        x="Revenue_M",
                        y="Status Terupdate",
                        orientation="h",
                        text="Label",
                        color="Revenue_M",
                        color_continuous_scale=["#E8F5FF", "#7DD3FC", "#0284C7"]
                    )

                    fig_status.update_traces(
                        textposition="outside",
                        cliponaxis=False,
                        hovertemplate="<b>%{y}</b><br>Revenue: %{x:.2f} M<extra></extra>"
                    )

                    fig_status.update_layout(coloraxis_showscale=False)
                    fig_status = apply_plotly_style(fig_status, height=420)
                    fig_status.update_xaxes(title="Revenue (Miliar Rp)")
                    fig_status.update_yaxes(title="")

                    st.plotly_chart(fig_status, use_container_width=True, config=PLOTLY_CONFIG)
                else:
                    st.info("Belum ada data revenue per status.")

                st.markdown('</div>', unsafe_allow_html=True)

        with anal_col2:
            with st.container():
                st.markdown('<div class="panel">', unsafe_allow_html=True)
                render_panel_header(
                    "Treemap Portofolio Kelompok Produk",
                    "Visualisasi kontribusi revenue dan rasio close won per kelompok produk."
                )

                if not rekap_kelompok.empty and rekap_kelompok["Revenue_Rp"].sum() > 0:
                    temp = rekap_kelompok.copy()

                    fig_tree = px.treemap(
                        temp,
                        path=["Kelompok Produk"],
                        values="Revenue_Rp",
                        color="CloseWonRatio",
                        color_continuous_scale=["#E5F9F0", "#22C55E", "#0B7A43"],
                        custom_data=["Revenue_M", "CloseWonRatio", "Jumlah_Project"]
                    )

                    fig_tree.update_traces(
                        textinfo="label+value",
                        hovertemplate=(
                            "<b>%{label}</b><br>"
                            "Revenue: Rp %{customdata[0]:.2f} M<br>"
                            "Rasio Close Won: %{customdata[1]:.1f}%<br>"
                            "Jumlah Project: %{customdata[2]}<extra></extra>"
                        )
                    )

                    fig_tree.update_layout(
                        template="plotly_white",
                        paper_bgcolor="rgba(0,0,0,0)",
                        height=420,
                        margin=dict(t=10, l=10, r=10, b=10),
                        coloraxis_colorbar=dict(title="CW Ratio")
                    )

                    st.plotly_chart(fig_tree, use_container_width=True, config=PLOTLY_CONFIG)
                else:
                    st.info("Belum ada data kelompok produk.")

                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("### Rekap Revenue per UP3")
        rekap_up3_tampil = rekap_up3.copy()
        rekap_up3_tampil.insert(0, "No", range(1, len(rekap_up3_tampil) + 1))
        rekap_up3_tampil["Total Revenue"] = rekap_up3_tampil["Total_Revenue_Rp"].apply(format_miliar)
        rekap_up3_tampil["Close Won"] = rekap_up3_tampil["Close_Won_Rp"].apply(format_miliar)
        rekap_up3_tampil["Potensi"] = rekap_up3_tampil["Potensi_Rp"].apply(format_miliar)

        st.dataframe(
            rekap_up3_tampil[["No", "UP3", "Jumlah_Project", "Total Revenue", "Close Won", "Potensi"]],
            use_container_width=True,
            hide_index=True
        )

        st.markdown("### Rekap Revenue per Kelompok Produk")
        rekap_kelompok_tampil = rekap_kelompok.copy()
        rekap_kelompok_tampil.insert(0, "No", range(1, len(rekap_kelompok_tampil) + 1))
        rekap_kelompok_tampil["Revenue"] = rekap_kelompok_tampil["Revenue_Rp"].apply(format_miliar)
        rekap_kelompok_tampil["Close Won"] = rekap_kelompok_tampil["Close_Won_Rp"].apply(format_miliar)
        rekap_kelompok_tampil["Potensi"] = rekap_kelompok_tampil["Potensi_Rp"].apply(format_miliar)

        st.dataframe(
            rekap_kelompok_tampil[["No", "Kelompok Produk", "Jumlah_Project", "Revenue", "Close Won", "Potensi"]],
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
                    Rasio Close Won: {format_persen(won_ratio)}
                    Rasio Potensi: {format_persen(potensi_ratio)}
                    Top UP3: {top_up3} - {format_miliar(top_up3_val)}
                    Top SHAP: {top_shap} - {format_miliar(top_shap_val)}
                    Top Kelompok Produk: {top_kelompok} - {format_miliar(top_kelompok_val)}

                    Rekap Klaster:
                    {rekap_klaster.to_dict(orient='records')}

                    Rekap Kelompok Produk:
                    {rekap_kelompok.to_dict(orient='records')}

                    Rekap SHAP:
                    {rekap_anak.to_dict(orient='records')}

                    Rekap Status Revenue:
                    {rekap_status_revenue.to_dict(orient='records')}

                    Rekap UP3:
                    {rekap_up3.to_dict(orient='records')}
                    """

                    prompt = f"""
                    Berdasarkan data performa IBS UID Jawa Timur berikut:
                    {data_ringkas}

                    Buatkan narasi executive summary singkat, analitis, dan terstruktur untuk manajemen.
                    Gunakan bahasa Indonesia formal.
                    Fokus pada:
                    1. Gambaran pencapaian revenue, close won, dan potensi
                    2. Klaster dan kelompok produk yang dominan
                    3. Peran SHAP/anak perusahaan
                    4. UP3 yang paling berkontribusi
                    5. Area pipeline yang perlu dikonversi
                    6. Rekomendasi tindak lanjut strategis
                    """

                    response = model.generate_content(prompt)
                    st.info(response.text)

    # =====================================================
    # TAB 3 - DETAIL DATA
    # =====================================================
    with tab3:
        render_section(
            "Data Detail",
            "Data detail mengikuti struktur source Google Sheet dan diformat agar lebih mudah dibaca."
        )

        df_tampil = df_filtered.copy().reset_index(drop=True)

        if "No" in df_tampil.columns:
            df_tampil = df_tampil.drop(columns=["No"])

        df_tampil.insert(0, "No", range(1, len(df_tampil) + 1))

        kolom_detail_source = [
            "No",
            "Nama Pelanggan",
            "IDPEL",
            "Daya (VA)",
            "Nama Produk",
            "Kelompok Produk",
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

        csv = df_tampil.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇️ Download Data Filtered (CSV)",
            data=csv,
            file_name="dashboard_ibs_filtered.csv",
            mime="text/csv"
        )

else:
    st.warning("Data belum berhasil dimuat.")

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
import requests
from io import BytesIO
from datetime import datetime
from zoneinfo import ZoneInfo
import math

# =====================================================
# KONFIGURASI HALAMAN
# =====================================================
st.set_page_config(
    page_title="Dashboard COREBOOST 2.0 UID JATIM",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CUSTOM CSS - TAMPILAN BARU
# =====================================================
st.markdown("""
<style>
    :root {
        --pln-navy: #071B3A;
        --pln-blue: #005BAC;
        --pln-cyan: #00AEEF;
        --pln-green: #00A859;
        --pln-yellow: #FFD200;
        --pln-orange: #F97316;
        --pln-red: #EF4444;
        --ink: #0F172A;
        --muted: #64748B;
        --panel: #FFFFFF;
        --soft: #F8FAFC;
        --line: #E2E8F0;
    }

    html, body, [class*="css"] {
        font-family: "Inter", "Segoe UI", Arial, sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 85% 10%, rgba(0,174,239,0.10), transparent 28%),
            radial-gradient(circle at 15% 0%, rgba(0,91,172,0.08), transparent 25%),
            linear-gradient(180deg, #F8FBFF 0%, #F4F7FB 45%, #FFFFFF 100%);
    }

    .main .block-container {
        padding-top: 1.15rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F1F6FF 0%, #E9F2FF 48%, #F8FAFC 100%);
        border-right: 1px solid rgba(148, 163, 184, 0.25);
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: #0F172A !important;
    }

    .sidebar-title {
        font-size: 1.1rem;
        font-weight: 900;
        color: #0F172A;
        margin-bottom: 0.35rem;
    }

    .sidebar-note {
        font-size: 0.78rem;
        color: #64748B;
        line-height: 1.35;
        margin-bottom: 0.75rem;
    }

    .hero-box {
        position: relative;
        overflow: hidden;
        color: white;
        border-radius: 28px;
        padding: 26px 30px;
        margin-bottom: 18px;
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.22);
        background:
            radial-gradient(circle at 78% 24%, rgba(34, 197, 94, 0.28), transparent 24%),
            radial-gradient(circle at 90% 70%, rgba(0, 174, 239, 0.22), transparent 22%),
            linear-gradient(135deg, #08142E 0%, #143DA8 45%, #16A34A 100%);
    }

    .hero-box::before {
        content: "";
        position: absolute;
        width: 520px;
        height: 520px;
        top: -260px;
        right: -160px;
        border: 1px solid rgba(255, 255, 255, 0.22);
        border-radius: 50%;
    }

    .hero-box::after {
        content: "";
        position: absolute;
        width: 380px;
        height: 380px;
        bottom: -240px;
        left: 45%;
        border: 1px solid rgba(255, 255, 255, 0.14);
        border-radius: 50%;
    }

    .hero-content {
        position: relative;
        z-index: 2;
        display: grid;
        grid-template-columns: minmax(0, 1.35fr) minmax(290px, 0.65fr);
        gap: 20px;
        align-items: center;
    }

    .hero-title-row {
        display: flex;
        gap: 14px;
        align-items: center;
    }

    .hero-icon {
        width: 56px;
        height: 56px;
        min-width: 56px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.16);
        border: 1px solid rgba(255, 255, 255, 0.18);
        box-shadow: inset 0 0 22px rgba(255,255,255,0.10);
        font-size: 1.7rem;
    }

    .hero-title-main {
        font-size: clamp(2rem, 3.3vw, 3.2rem);
        font-weight: 950;
        line-height: 1.05;
        margin: 0;
        letter-spacing: 0.1px;
    }

    .hero-title-sub {
        margin-top: 9px;
        font-size: clamp(1.05rem, 1.7vw, 1.5rem);
        font-weight: 800;
        line-height: 1.25;
        opacity: 0.98;
    }

    .hero-subtitle {
        margin-top: 12px;
        max-width: 900px;
        font-size: 0.95rem;
        line-height: 1.55;
        color: rgba(255,255,255,0.86);
    }

    .hero-pill-wrap {
        margin-top: 14px;
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
    }

    .hero-pill {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        padding: 7px 11px;
        border-radius: 999px;
        background: rgba(255,255,255,0.14);
        border: 1px solid rgba(255,255,255,0.16);
        font-size: 0.78rem;
        font-weight: 800;
        color: rgba(255,255,255,0.94);
    }

    .hero-illustration {
        position: relative;
        min-height: 176px;
        border-radius: 24px;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.16);
        backdrop-filter: blur(8px);
        padding: 16px;
    }

    .hero-illustration svg {
        width: 100%;
        height: 172px;
        display: block;
    }

    .metric-card {
        position: relative;
        overflow: hidden;
        min-height: 132px;
        padding: 18px 18px;
        border-radius: 22px;
        color: white;
        box-shadow: 0 14px 32px rgba(15, 23, 42, 0.14);
    }

    .metric-card::after {
        content: "";
        position: absolute;
        right: -44px;
        top: -46px;
        width: 135px;
        height: 135px;
        border-radius: 50%;
        background: rgba(255,255,255,0.16);
    }

    .metric-title {
        position: relative;
        z-index: 2;
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.88rem;
        font-weight: 800;
        opacity: 0.98;
        margin-bottom: 12px;
    }

    .metric-value {
        position: relative;
        z-index: 2;
        font-size: 2rem;
        font-weight: 950;
        line-height: 1.02;
        margin-bottom: 9px;
        letter-spacing: -0.3px;
    }

    .metric-sub {
        position: relative;
        z-index: 2;
        font-size: 0.80rem;
        opacity: 0.92;
        line-height: 1.35;
    }

    .card-blue {
        background: linear-gradient(135deg, #0B4DD8 0%, #0EA5E9 100%);
    }

    .card-green {
        background: linear-gradient(135deg, #038B4A 0%, #22C55E 100%);
    }

    .card-orange {
        background: linear-gradient(135deg, #EA580C 0%, #F97316 100%);
    }

    .card-purple {
        background: linear-gradient(135deg, #7C3AED 0%, #A855F7 100%);
    }

    .insight-strip {
        padding: 14px 16px;
        background: rgba(255,255,255,0.88);
        border: 1px solid rgba(148,163,184,0.28);
        border-radius: 18px;
        color: #334155;
        margin-top: 12px;
        margin-bottom: 16px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
    }

    .insight-strip b {
        color: #0F172A;
    }

    .section-heading {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 22px 0 12px 0;
    }

    .section-heading .dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: linear-gradient(135deg, #005BAC, #00AEEF);
        box-shadow: 0 0 0 7px rgba(0,91,172,0.08);
    }

    .section-heading h3 {
        margin: 0;
        color: #071B3A;
        font-size: 1.35rem;
        font-weight: 950;
        letter-spacing: -0.2px;
    }

    .section-heading p {
        margin: 2px 0 0 0;
        color: #64748B;
        font-size: 0.86rem;
    }

    .mini-card {
        height: 100%;
        padding: 17px 18px;
        border-radius: 22px;
        background: rgba(255,255,255,0.90);
        border: 1px solid rgba(148,163,184,0.26);
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.07);
    }

    .mini-card-label {
        color: #64748B;
        font-size: 0.78rem;
        font-weight: 850;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }

    .mini-card-value {
        color: #0F172A;
        font-size: 1.35rem;
        font-weight: 950;
        line-height: 1.15;
    }

    .mini-card-caption {
        margin-top: 7px;
        color: #64748B;
        font-size: 0.80rem;
        line-height: 1.35;
    }

    .chart-card {
        padding: 16px 18px 8px 18px;
        border-radius: 24px;
        background: rgba(255,255,255,0.92);
        border: 1px solid rgba(148,163,184,0.24);
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.07);
        margin-bottom: 18px;
    }

    .chart-card h4 {
        margin: 0 0 3px 0;
        font-size: 1rem;
        font-weight: 950;
        color: #071B3A;
    }

    .chart-card p {
        margin: 0 0 8px 0;
        font-size: 0.80rem;
        color: #64748B;
    }

    .dataframe {
        font-size: 0.86rem !important;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid rgba(148,163,184,0.26);
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
    }

    div[data-baseweb="tab-list"] {
        gap: 10px;
        border-bottom: 1px solid rgba(148,163,184,0.26);
    }

    button[data-baseweb="tab"] {
        border-radius: 13px 13px 0 0;
        padding-top: 12px;
        padding-bottom: 12px;
        font-weight: 850;
    }

    @media (max-width: 1000px) {
        .hero-content {
            grid-template-columns: 1fr;
        }

        .hero-illustration {
            min-height: 140px;
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
    except Exception:
        return "Rp 0,00 M"


def format_miliar_chart(value):
    try:
        value = float(value)
        hasil = f"{value:,.2f}"
        hasil = hasil.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{hasil} M"
    except Exception:
        return "0,00 M"


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
    except Exception:
        return "0,00"


def format_persen(value):
    try:
        hasil = f"{float(value):,.1f}"
        hasil = hasil.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{hasil}%"
    except Exception:
        return "0,0%"


def metric_card(title, value, subtitle, css_class, icon="●"):
    st.markdown(
        f"""
        <div class="metric-card {css_class}">
            <div class="metric-title"><span>{icon}</span><span>{title}</span></div>
            <div class="metric-value">{value}</div>
            <div class="metric-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def section_heading(title, subtitle="", icon_dot=True):
    dot = '<div class="dot"></div>' if icon_dot else ""
    st.markdown(
        f"""
        <div class="section-heading">
            {dot}
            <div>
                <h3>{title}</h3>
                <p>{subtitle}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def mini_card(label, value, caption):
    st.markdown(
        f"""
        <div class="mini-card">
            <div class="mini-card-label">{label}</div>
            <div class="mini-card-value">{value}</div>
            <div class="mini-card-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def chart_card_open(title, subtitle=""):
    st.markdown(
        f"""
        <div class="chart-card">
            <h4>{title}</h4>
            <p>{subtitle}</p>
        """,
        unsafe_allow_html=True
    )


def chart_card_close():
    st.markdown("</div>", unsafe_allow_html=True)


def bersihkan_teks_kosong(series):
    return (
        series
        .astype(str)
        .str.strip()
        .replace(["nan", "None", "NaN", "", "-", "0"], "Belum Terisi")
    )


def standarkan_nama_kolom(df):
    df.columns = (
        df.columns
        .astype(str)
        .str.replace("\n", " ", regex=False)
        .str.replace("\r", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
    return df


def style_plotly(fig, height=430, showlegend=True):
    fig.update_layout(
        template="plotly_white",
        height=height,
        font=dict(family="Inter, Segoe UI, Arial", size=12, color="#334155"),
        title=dict(font=dict(size=15, color="#071B3A"), x=0.01, xanchor="left"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=48, l=10, r=30, b=20),
        showlegend=showlegend,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            font=dict(size=11)
        )
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(148,163,184,0.22)",
        zeroline=False,
        linecolor="rgba(148,163,184,0.35)"
    )
    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
        linecolor="rgba(148,163,184,0.35)"
    )
    return fig


def build_empty_message(text):
    st.info(text)


def safe_headline_value(df_in, label_col, value_col):
    if df_in is None or df_in.empty or value_col not in df_in.columns:
        return "-", 0
    temp = df_in.dropna(subset=[label_col]).sort_values(value_col, ascending=False)
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
    teks = teks.replace("di gital", "digital")
    teks = teks.replace("kompatible", "compatible")

    if any(k in teks for k in [
        "spklu", "ev charger", "charging station", "home charger",
        "private charger", "charger dc", "charger 30", "charger 60",
        "charger 120", "mesin spklu", "om mesin spklu",
        "uji compatible mesin spklu", "uji kompatible mesin spklu",
        "pb kwh meter untuk spklu"
    ]):
        return "SPKLU / EV Charging"

    if any(k in teks for k in ["forklift", "forklift listrik", "forklift electric", "forklift ev"]):
        return "Forklift Electric"

    if any(k in teks for k in [
        "mobil listrik", "kendaraan listrik", "kendaraan ev", "sewa ev",
        "sewa mobil listrik", "sewa kendaraan", "electric ambulance",
        "ambulance", "mobil pick up ev", " ev", "ev ", "probing mobil listrik"
    ]):
        return "Sewa Kendaraan Listrik / EV"

    if any(k in teks for k in ["plts", "pv rooftop", "solar", "surya", "rooftop"]):
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
        "broadband", "dedicated", "corporate", "ftth",
        "ip publik", "access point", "i-win", "koneksi internet"
    ]):
        return "Internet & Connectivity"

    if any(k in teks for k in ["cctv", "i-see", "firewall", "fortigate", "security", "camera", "surveillance"]):
        return "CCTV & Security"

    if any(k in teks for k in [
        "digital", "zoom", "aplikasi", "server", "hardisk",
        "perangkat digital", "smart switch", "rekening", "manage service"
    ]):
        return "Digital Solution / ICT"

    if any(k in teks for k in [
        "iml", "instalasi", "nidi", "slo", "sertifikat laik operasi",
        "sertifikat laik fungsi", "slf", "pasang baru", "penyambungan",
        "tambah daya", "penyambungan sementara", "cabling",
        "penarikan kabel", "acos"
    ]):
        return "IML / Instalasi / NIDI / SLO"

    if any(k in teks for k in [
        "trafo", "kubikel", "cubicle", "gardu", "capacitor",
        "capasitor", "capasitor bank", "kapasitor", "pengadaan tiang",
        "tiang beton", "bushing", "incoming", "outgoing",
        "kwh meter", "pembangunan gardu", "power equipment"
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

        daftar_kelompok = [
            "SPKLU / EV Charging", "Sewa Kendaraan Listrik / EV",
            "Forklift Electric", "PLTS / PV Rooftop", "REC",
            "Internet & Connectivity", "CCTV & Security", "Digital Solution / ICT",
            "IML / Instalasi / NIDI / SLO",
            "Trafo / Kubikel / Gardu / Power Equipment",
            "Maintenance Trafo & Kubikel", "Genset / Backup Power",
            "Power Quality / BESS / DRUPS / RUPS", "PJU / Public Lighting",
            "Voucher Listrik", "Asuransi", "Konstruksi",
            "Electrifying Lifestyle Industrial", "Lainnya / Perlu Review"
        ]

        for kelompok in daftar_kelompok:
            if kelompok.lower() in hasil.lower():
                return kelompok

        return "Lainnya / Perlu Review"

    except Exception:
        return "Lainnya / Perlu Review"


# =====================================================
# SETUP GEMINI
# =====================================================
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
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
        df = standarkan_nama_kolom(df)
        df = df.dropna(how="all")

        col_nominal = "Nominal Kontrak / Revenue (Rp)"
        col_status = "Status Terupdate"
        col_up3 = "UP3"
        col_klaster = "Klaster Produk"
        col_anak_perusahaan = "ANAK PERUSAHAAN"

        required_cols = [col_nominal, col_status, col_up3, col_klaster, col_anak_perusahaan]
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            st.error(f"Kolom berikut belum ditemukan di Google Sheets: {missing_cols}")
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
        df[col_anak_perusahaan] = bersihkan_teks_kosong(df[col_anak_perusahaan])

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

        status_potensi = ["Probing", "Penawaran", "Negosiasi"]

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
    st.sidebar.markdown(
        """
        <div class="sidebar-title">🔎 Filter Data</div>
        <div class="sidebar-note">
        Gunakan filter untuk melihat performa IBS berdasarkan wilayah, klaster, kelompok produk, SHAP, dan status pipeline.
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

    pilih_kelompok_produk = st.sidebar.multiselect(
        "Pilih Kelompok Produk:",
        options=sorted(df["Kelompok Produk"].dropna().unique()) if "Kelompok Produk" in df.columns else []
    )

    pilih_anak_perusahaan = st.sidebar.multiselect(
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

    df_filtered = df.copy()

    if pilih_up3:
        df_filtered = df_filtered[df_filtered["UP3"].isin(pilih_up3)]

    if pilih_klaster:
        df_filtered = df_filtered[df_filtered["Klaster Produk"].isin(pilih_klaster)]

    if pilih_kelompok_produk and "Kelompok Produk" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["Kelompok Produk"].isin(pilih_kelompok_produk)]

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

    rekap_status_count = (
        df_filtered
        .groupby("Status Terupdate", dropna=False)
        .agg(
            Jumlah_Project=("Status Terupdate", "count"),
            Revenue_Rp=("Nominal Kontrak / Revenue (Rp)", "sum")
        )
        .reset_index()
        .sort_values("Revenue_Rp", ascending=False)
    )
    rekap_status_count["Revenue_M"] = rekap_status_count["Revenue_Rp"] / 1_000_000_000

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
    rekap_up3 = rekap_up3.sort_values(by="Total_Revenue_Rp", ascending=False).reset_index(drop=True)

    if "Kelompok Produk" in df_filtered.columns:
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
        rekap_kelompok["Kelompok Produk"] = bersihkan_teks_kosong(rekap_kelompok["Kelompok Produk"])
        rekap_kelompok["Revenue_M"] = rekap_kelompok["Revenue_Rp"] / 1_000_000_000
        rekap_kelompok = rekap_kelompok.sort_values("Revenue_M", ascending=False)
    else:
        rekap_kelompok = pd.DataFrame()

    top_up3, top_up3_val = safe_headline_value(rekap_up3, "UP3", "Total_Revenue_Rp")
    top_shap, top_shap_val = safe_headline_value(rekap_anak, "ANAK PERUSAHAAN", "Nominal Kontrak / Revenue (Rp)")
    top_kelompok, top_kelompok_val = safe_headline_value(rekap_kelompok, "Kelompok Produk", "Revenue_Rp") if not rekap_kelompok.empty else ("-", 0)

    # =====================================================
    # HERO
    # =====================================================
    st.markdown(
        f"""
        <div class="hero-box">
            <div class="hero-content">
                <div>
                    <div class="hero-title-row">
                        <div class="hero-icon">📊</div>
                        <div>
                            <div class="hero-title-main">Dashboard COREBOOST 2.0 UID JATIM</div>
                            <div class="hero-title-sub">Integrated Business Solution (IBS) 2026</div>
                        </div>
                    </div>
                    <div class="hero-subtitle">
                        Executive dashboard untuk memantau revenue, close won, potensi, kelompok produk, SHAP, UP3, dan status pipeline IBS secara ringkas dan informatif.
                    </div>
                    <div class="hero-pill-wrap">
                        <div class="hero-pill">🕒 Update: {last_update}</div>
                        <div class="hero-pill">🏢 Top UP3: {top_up3}</div>
                        <div class="hero-pill">🤝 Top SHAP: {top_shap}</div>
                        <div class="hero-pill">⚡ Top Produk: {top_kelompok}</div>
                    </div>
                </div>
                <div class="hero-illustration">
                    <svg viewBox="0 0 520 260" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <defs>
                            <linearGradient id="g1" x1="0" y1="0" x2="520" y2="260" gradientUnits="userSpaceOnUse">
                                <stop stop-color="#00AEEF" stop-opacity="0.95"/>
                                <stop offset="1" stop-color="#22C55E" stop-opacity="0.90"/>
                            </linearGradient>
                            <linearGradient id="g2" x1="0" y1="0" x2="0" y2="210" gradientUnits="userSpaceOnUse">
                                <stop stop-color="white" stop-opacity="0.95"/>
                                <stop offset="1" stop-color="white" stop-opacity="0.32"/>
                            </linearGradient>
                        </defs>
                        <rect x="20" y="28" width="150" height="174" rx="22" fill="white" fill-opacity="0.14" stroke="white" stroke-opacity="0.22"/>
                        <rect x="48" y="128" width="22" height="48" rx="8" fill="#FFD200"/>
                        <rect x="82" y="96" width="22" height="80" rx="8" fill="#00AEEF"/>
                        <rect x="116" y="66" width="22" height="110" rx="8" fill="#22C55E"/>
                        <path d="M48 72C75 56 105 45 142 42" stroke="white" stroke-width="8" stroke-linecap="round" opacity="0.88"/>
                        <path d="M142 42L128 31M142 42L131 58" stroke="white" stroke-width="8" stroke-linecap="round" opacity="0.88"/>

                        <rect x="204" y="42" width="130" height="78" rx="20" fill="white" fill-opacity="0.15" stroke="white" stroke-opacity="0.22"/>
                        <path d="M238 92h52c11 0 20-9 20-20s-9-20-20-20h-52c-11 0-20 9-20 20s9 20 20 20z" stroke="white" stroke-width="8"/>
                        <path d="M252 52v-17M276 52v-17M252 109v-17M276 109v-17" stroke="white" stroke-width="8" stroke-linecap="round"/>
                        <circle cx="246" cy="72" r="7" fill="#FFD200"/>
                        <circle cx="282" cy="72" r="7" fill="#22C55E"/>

                        <rect x="366" y="52" width="108" height="150" rx="20" fill="white" fill-opacity="0.14" stroke="white" stroke-opacity="0.22"/>
                        <path d="M398 150L420 102L442 150H398Z" fill="url(#g2)"/>
                        <circle cx="420" cy="92" r="24" fill="#FFD200" fill-opacity="0.95"/>
                        <path d="M385 170H455" stroke="white" stroke-width="8" stroke-linecap="round" opacity="0.85"/>

                        <path d="M170 178C232 214 302 208 366 170" stroke="url(#g1)" stroke-width="12" stroke-linecap="round"/>
                        <circle cx="172" cy="178" r="8" fill="white"/>
                        <circle cx="366" cy="170" r="8" fill="white"/>
                    </svg>
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
        metric_card(
            "Total Project",
            f"{total_project:,.0f} Unit",
            f"Rata-rata revenue/proyek: {format_miliar(avg_project)}",
            "card-blue",
            icon="📌"
        )

    with k2:
        metric_card(
            "Total Revenue",
            format_miliar(total_revenue),
            "Akumulasi seluruh project terfilter",
            "card-green",
            icon="💰"
        )

    with k3:
        metric_card(
            "Close Won",
            format_miliar(total_won),
            f"Kontribusi {format_persen(won_ratio)} dari total revenue",
            "card-orange",
            icon="🏆"
        )

    with k4:
        metric_card(
            "Potensi",
            format_miliar(total_potensi),
            f"Setara {format_persen(potensi_ratio)} dari total revenue",
            "card-purple",
            icon="🚀"
        )

    st.markdown(
        f"""
        <div class="insight-strip">
            💡 <b>Insight cepat:</b> Top UP3 saat ini <b>{top_up3}</b> dengan kontribusi <b>{format_miliar(top_up3_val)}</b>.
            Top SHAP <b>{top_shap}</b> dengan revenue <b>{format_miliar(top_shap_val)}</b>.
            Kelompok produk terbesar adalah <b>{top_kelompok}</b> dengan revenue <b>{format_miliar(top_kelompok_val)}</b>.
            <br>
            🕒 <b>Data terakhir dimuat:</b> {last_update}
        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # QUICK INSIGHT CARDS
    # =====================================================
    c_top1, c_top2, c_top3, c_top4 = st.columns(4)

    with c_top1:
        mini_card("Top UP3", top_up3, f"Revenue {format_miliar(top_up3_val)}")

    with c_top2:
        mini_card("Top SHAP", top_shap, f"Revenue {format_miliar(top_shap_val)}")

    with c_top3:
        mini_card("Top Kelompok Produk", top_kelompok, f"Revenue {format_miliar(top_kelompok_val)}")

    with c_top4:
        mini_card("Rasio Close Won", format_persen(won_ratio), "Indikator konversi terhadap total revenue")

    # =====================================================
    # TAB DASHBOARD
    # =====================================================
    tab1, tab2, tab3 = st.tabs(["📈 Overview", "📊 Analisis", "📋 Detail Data"])

    # =====================================================
    # TAB 1 OVERVIEW
    # =====================================================
    with tab1:
        section_heading(
            "Distribusi Revenue",
            "Komposisi revenue berdasarkan klaster, SHAP, UP3, dan kelompok produk."
        )

        c1, c2 = st.columns([0.95, 1.05])

        with c1:
            chart_card_open("Komposisi Revenue per Klaster Produk", "Menunjukkan share revenue setiap klaster IBS.")
            if rekap_klaster.empty or rekap_klaster["Revenue_M"].sum() <= 0:
                build_empty_message("Belum ada data revenue klaster yang dapat divisualisasikan.")
            else:
                warna_klaster = {
                    "GREEN ENERGY SOLUTION": "#00A859",
                    "OPERATION EXCELLENT SOLUTION": "#005BAC",
                    "DIGITAL TECHNOLOGY SOLUTION": "#00AEEF",
                    "POWER CONNECTION SOLUTION": "#FFD200",
                    "MANAGEMENT SYSTEM SOLUTION": "#7C3AED",
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
                    height=420,
                    font=dict(family="Inter, Segoe UI, Arial", size=12),
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=10, l=10, r=10, b=10),
                    legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02)
                )

                fig_donut.add_annotation(
                    text=f"<b>{format_miliar_chart(total_revenue / 1_000_000_000)}</b><br><span style='font-size:12px'>Total</span>",
                    showarrow=False,
                    x=0.5,
                    y=0.5,
                    font=dict(size=16, color="#071B3A")
                )

                st.plotly_chart(fig_donut, use_container_width=True)
            chart_card_close()

        with c2:
            chart_card_open("Top SHAP Berdasarkan Revenue", "Subholding / anak perusahaan dengan kontribusi revenue terbesar.")
            rekap_anak_bar = rekap_anak[rekap_anak["Revenue_M"] > 0].copy()
            rekap_anak_bar = rekap_anak_bar.sort_values("Revenue_M", ascending=False).head(8)

            if rekap_anak_bar.empty:
                build_empty_message("Belum ada data revenue Anak Perusahaan/Subholding yang dapat divisualisasikan.")
            else:
                rekap_anak_bar["Label"] = rekap_anak_bar["Revenue_M"].apply(format_miliar_chart)

                fig_anak_bar = px.bar(
                    rekap_anak_bar.sort_values("Revenue_M", ascending=True),
                    x="Revenue_M",
                    y="ANAK PERUSAHAAN",
                    orientation="h",
                    text="Label",
                    color="Revenue_M",
                    color_continuous_scale=["#DBEAFE", "#38BDF8", "#0B3B82"],
                )

                fig_anak_bar.update_traces(
                    textposition="outside",
                    cliponaxis=False,
                    hovertemplate="<b>%{y}</b><br>Revenue: %{x:.2f} M<extra></extra>"
                )

                max_val = rekap_anak_bar["Revenue_M"].max()
                fig_anak_bar.update_layout(
                    xaxis_range=[0, max_val * 1.18 if max_val > 0 else 1],
                    coloraxis_showscale=False
                )

                fig_anak_bar = style_plotly(fig_anak_bar, height=420, showlegend=False)
                fig_anak_bar.update_xaxes(title="Revenue (Miliar Rp)")
                fig_anak_bar.update_yaxes(title="")
                st.plotly_chart(fig_anak_bar, use_container_width=True)
            chart_card_close()

        c3, c4 = st.columns([1.05, 0.95])

        with c3:
            chart_card_open("Top 10 UP3 Berdasarkan Revenue", "Peringkat UP3 berdasarkan total revenue project IBS.")
            rekap_up3_chart = rekap_up3.copy()
            rekap_up3_chart["Revenue_M"] = rekap_up3_chart["Total_Revenue_Rp"] / 1_000_000_000
            rekap_up3_chart = rekap_up3_chart.sort_values("Revenue_M", ascending=False).head(10)

            if rekap_up3_chart.empty or rekap_up3_chart["Revenue_M"].sum() <= 0:
                build_empty_message("Belum ada data revenue UP3 yang dapat divisualisasikan.")
            else:
                rekap_up3_chart["Label"] = rekap_up3_chart["Revenue_M"].apply(format_miliar_chart)

                fig_top_up3 = px.bar(
                    rekap_up3_chart.sort_values("Revenue_M", ascending=True),
                    x="Revenue_M",
                    y="UP3",
                    orientation="h",
                    text="Label",
                    color="Revenue_M",
                    color_continuous_scale=["#DBEAFE", "#00AEEF", "#005BAC"],
                )

                fig_top_up3.update_traces(
                    textposition="outside",
                    cliponaxis=False,
                    hovertemplate="<b>%{y}</b><br>Revenue: %{x:.2f} M<extra></extra>"
                )

                max_val = rekap_up3_chart["Revenue_M"].max()
                fig_top_up3.update_layout(
                    xaxis_range=[0, max_val * 1.16 if max_val > 0 else 1],
                    coloraxis_showscale=False
                )

                fig_top_up3 = style_plotly(fig_top_up3, height=470, showlegend=False)
                fig_top_up3.update_xaxes(title="Revenue (Miliar Rp)")
                fig_top_up3.update_yaxes(title="")
                st.plotly_chart(fig_top_up3, use_container_width=True)
            chart_card_close()

        with c4:
            chart_card_open("Pipeline per Status", "Distribusi jumlah project berdasarkan status terupdate.")
            if rekap_status_count.empty:
                build_empty_message("Belum ada data status yang dapat divisualisasikan.")
            else:
                fig_status_count = px.bar(
                    rekap_status_count.sort_values("Jumlah_Project", ascending=True),
                    x="Jumlah_Project",
                    y="Status Terupdate",
                    orientation="h",
                    text="Jumlah_Project",
                    color="Status Terupdate",
                    color_discrete_sequence=["#005BAC", "#00AEEF", "#00A859", "#F97316", "#7C3AED", "#EF4444"]
                )

                fig_status_count.update_traces(
                    textposition="outside",
                    cliponaxis=False,
                    hovertemplate="<b>%{y}</b><br>Jumlah Project: %{x}<extra></extra>"
                )

                max_val = rekap_status_count["Jumlah_Project"].max()
                fig_status_count.update_layout(
                    xaxis_range=[0, max_val * 1.18 if max_val > 0 else 1]
                )

                fig_status_count = style_plotly(fig_status_count, height=470, showlegend=False)
                fig_status_count.update_xaxes(title="Jumlah Project")
                fig_status_count.update_yaxes(title="")
                st.plotly_chart(fig_status_count, use_container_width=True)
            chart_card_close()

        chart_card_open("Revenue Berdasarkan Kelompok Produk", "Kelompok produk disusun dari normalisasi nama produk yang bervariasi.")
        if rekap_kelompok.empty or rekap_kelompok["Revenue_M"].sum() <= 0:
            build_empty_message("Belum ada data revenue berdasarkan Kelompok Produk.")
        else:
            rekap_kelompok_chart = rekap_kelompok.copy()
            rekap_kelompok_chart = rekap_kelompok_chart.sort_values("Revenue_M", ascending=False).head(18)
            rekap_kelompok_chart["Label"] = rekap_kelompok_chart["Revenue_M"].apply(format_miliar_chart)

            fig_kelompok = px.bar(
                rekap_kelompok_chart.sort_values("Revenue_M", ascending=True),
                x="Revenue_M",
                y="Kelompok Produk",
                orientation="h",
                text="Label",
                color="Revenue_M",
                color_continuous_scale=["#E0F2FE", "#00AEEF", "#071B3A"]
            )

            fig_kelompok.update_traces(
                textposition="outside",
                cliponaxis=False,
                hovertemplate="<b>%{y}</b><br>Revenue: %{x:.2f} M<extra></extra>"
            )

            max_val = rekap_kelompok_chart["Revenue_M"].max()
            fig_kelompok.update_layout(
                xaxis_range=[0, max_val * 1.15 if max_val > 0 else 1],
                coloraxis_showscale=False
            )

            fig_kelompok = style_plotly(fig_kelompok, height=650, showlegend=False)
            fig_kelompok.update_xaxes(title="Revenue (Miliar Rp)")
            fig_kelompok.update_yaxes(title="")
            st.plotly_chart(fig_kelompok, use_container_width=True)
        chart_card_close()

    # =====================================================
    # TAB 2 ANALISIS
    # =====================================================
    with tab2:
        section_heading(
            "Analisis Pipeline dan Kontribusi",
            "Membandingkan klaster, status pipeline, UP3, dan kelompok produk."
        )

        c5, c6 = st.columns(2)

        with c5:
            chart_card_open("Revenue per Klaster Produk", "Nilai revenue masing-masing klaster produk.")
            if rekap_klaster.empty or rekap_klaster["Revenue_M"].sum() <= 0:
                build_empty_message("Belum ada data revenue klaster yang dapat divisualisasikan.")
            else:
                rekap_klaster_bar = rekap_klaster.copy()
                rekap_klaster_bar["Label"] = rekap_klaster_bar["Revenue_M"].apply(format_miliar_chart)

                fig_klaster_bar = px.bar(
                    rekap_klaster_bar.sort_values("Revenue_M", ascending=True),
                    x="Revenue_M",
                    y="Klaster Produk",
                    orientation="h",
                    text="Label",
                    color="Klaster Produk",
                    color_discrete_sequence=["#005BAC", "#00A859", "#00AEEF", "#FFD200", "#7C3AED"]
                )

                fig_klaster_bar.update_traces(textposition="outside", cliponaxis=False)
                max_val = rekap_klaster_bar["Revenue_M"].max()
                fig_klaster_bar.update_layout(xaxis_range=[0, max_val * 1.18 if max_val > 0 else 1])
                fig_klaster_bar = style_plotly(fig_klaster_bar, height=430, showlegend=False)
                fig_klaster_bar.update_xaxes(title="Revenue (Miliar Rp)")
                fig_klaster_bar.update_yaxes(title="")
                st.plotly_chart(fig_klaster_bar, use_container_width=True)
            chart_card_close()

        with c6:
            chart_card_open("Revenue per Status Terupdate", "Mengukur nilai pipeline berdasarkan tahap status.")
            if rekap_status.empty or rekap_status["Revenue_M"].sum() <= 0:
                build_empty_message("Belum ada data revenue status yang dapat divisualisasikan.")
            else:
                rekap_status_bar = rekap_status.copy()
                rekap_status_bar["Label"] = rekap_status_bar["Revenue_M"].apply(format_miliar_chart)

                fig_status = px.bar(
                    rekap_status_bar.sort_values("Revenue_M", ascending=True),
                    x="Revenue_M",
                    y="Status Terupdate",
                    orientation="h",
                    text="Label",
                    color="Status Terupdate",
                    color_discrete_sequence=["#005BAC", "#00AEEF", "#00A859", "#F97316", "#7C3AED", "#EF4444"]
                )

                fig_status.update_traces(textposition="outside", cliponaxis=False)
                max_val = rekap_status_bar["Revenue_M"].max()
                fig_status.update_layout(xaxis_range=[0, max_val * 1.18 if max_val > 0 else 1])
                fig_status = style_plotly(fig_status, height=430, showlegend=False)
                fig_status.update_xaxes(title="Revenue (Miliar Rp)")
                fig_status.update_yaxes(title="")
                st.plotly_chart(fig_status, use_container_width=True)
            chart_card_close()

        section_heading(
            "Tabel Rekap",
            "Ringkasan numerik untuk mendukung evaluasi dan tindak lanjut."
        )

        c7, c8 = st.columns([1.1, 0.9])

        with c7:
            st.markdown("#### Rekap Revenue per UP3")
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

        with c8:
            st.markdown("#### Rekap Revenue per Kelompok Produk")
            if not rekap_kelompok.empty:
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
            else:
                st.info("Belum ada data kelompok produk.")

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
                    {rekap_kelompok.to_dict(orient='records') if not rekap_kelompok.empty else []}

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
                    3. Kelompok produk yang paling berkontribusi.
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
        section_heading(
            "Data Detail",
            "Data detail disesuaikan dengan struktur Google Sheet dan sudah diformat akuntansi."
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

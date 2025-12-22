import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import json

# ==============================
# KONFIGURASI DASHBOARD
# ==============================
st.set_page_config(page_title="Dashboard Kasus HIV - Jawa Barat 2024", layout="wide")

# Custom CSS untuk tampilan modern seperti dashboard TBC
st.markdown("""
<style>

    /* ============================= */
    /* SIDEBAR */
    /* ============================= */
    [data-testid="stSidebar"] {
        background-color: #003566;
        width: 340px !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] a,
    [data-testid="stSidebar"] label {
        color: white !important;
        font-size: 22px !important;
    }

    [data-testid="stSidebar"] .stButton > button {
        background-color: transparent;
        color: #ffffff;
        border: 1px solid #ffffff33;
        border-radius: 12px;
        width: 100%;
        text-align: center;
        font-weight: 600;
        margin-top: 8px;
        padding: 16px;
        font-size: 22px;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #ffc300;
        color: #000000;
    }

    /* ============================= */
    /* METRIC (ANGKA + JUDUL) */
    /* ============================= */

    /* Judul metric: Total Kasus HIV, dll */
    div[data-testid="stMetric"] p {
        font-size: 24px !important;
        font-weight: 600 !important;
    }

    /* Angka metric */
    div[data-testid="stMetricValue"] {
        font-size: 52px !important;
        font-weight: 600 !important;
    }

    /* ============================= */
    /* JUDUL DASHBOARD */
    /* ============================= */
    .stApp h1 {
        font-size: 56px !important;
        font-weight: 800 !important;
    }

    .stApp h2 {
        font-size: 35px !important;
    }

    /* ============================= */
    /* ISI DASHBOARD */
    /* ============================= */

    /* Sumber data / caption */
    .stCaption,
    div[data-testid="stMarkdown"] span {
        font-size: 16px !important;
        color: #6b7280;
    }

    /* Paragraf markdown */
    div[data-testid="stMarkdown"] p {
        font-size: 21px !important;
        line-height: 1.6;
    }

    /* Heading markdown (###) */
    div[data-testid="stMarkdown"] h3 {
        font-size: 28px !important;
        font-weight: 600;
        margin-top: 20px;
    }

    /* Bullet list */
    div[data-testid="stMarkdown"] li {
        font-size: 21px !important;
        line-height: 1.6;
    }

    /* ============================= */
    /* TABEL & DROPDOWN */
    /* ============================= */
    .stDataFrame {
        font-size: 25px !important;
    }

    .stSelectbox label {
        font-size: 25px !important;
    }

</style>
""", unsafe_allow_html=True)

# ==============================
# SIDEBAR NAVIGATION
# ==============================
menu = ["Home", "Deskripsi Penyakit", "Karakteristik Wilayah dan Kasus HIV", "Ukuran Epidemiologi", "About Research"]

if "selected" not in st.session_state:
    st.session_state["selected"] = "Home"

# Tombol Home dengan highlight
if st.sidebar.button("🏠 Home", key="home", use_container_width=True):
    st.session_state["selected"] = "Home"

# Highlight tombol Home jika aktif
if st.session_state["selected"] == "Home":
    st.markdown(
        """<style>
            div[data-testid="stSidebar"] div[data-testid="stButton"]:nth-child(1) button {
                background-color: #ffc300 !important;
                color: #000 !important;
                font-weight: 700 !important;
                border: none !important;
            }
        </style>""",
        unsafe_allow_html=True
    )

# Tombol lainnya dengan emoji
emoji_map = {
    "Deskripsi Penyakit": "🧬",
    "Karakteristik Wilayah dan Kasus HIV": "🧩",
    "Ukuran Epidemiologi": "🔬",
    "About Research": "ℹ️"
}

for item in menu[1:]:
    if st.sidebar.button(f"{emoji_map.get(item, '📌')} {item}", key=item, use_container_width=True):
        st.session_state["selected"] = item

selected = st.session_state["selected"]

# ==============================
# LOAD DATA
# ==============================
@st.cache_data
def load_data():
    df = pd.read_excel(
        "data hiv jabar 2024.xlsx",
        engine="openpyxl")
    df.columns = df.columns.str.strip()  # Bersihkan nama kolom
    # ===== NORMALISASI NAMA KAB/KOTA =====
    df["KABKOT_MAP"] = (
        df["Kabupaten/Kota"]
        .str.upper()
        .str.replace("KABUPATEN ", "", regex=False)
        .str.replace("KOTA ", "KOTA ", regex=False)
    )
    # Hitung prevalensi jika ada kolom populasi (opsional, jika data punya)
    if 'Jumlah Penduduk (Ribu)' in df.columns:
        df['Prevalensi per 100k'] = (df['Jumlah Kasus HIV'] / (df['Jumlah Penduduk (Ribu)'] * 1000)) * 100000
    return df

# ==============================
# LOAD DATA TREN (2018–2024)
# ==============================
@st.cache_data
def load_trend_data():
    df_trend = pd.read_excel(
        "data tren hiv jabar.xlsx",
        engine="openpyxl")
    df_trend.columns = df_trend.columns.str.strip()

    df_trend["Tahun"] = df_trend["Tahun"].astype(int)
    df_trend["Jumlah Kasus"] = pd.to_numeric(
        df_trend["Jumlah Kasus"], errors="coerce"
    )
    df_trend["Kabupaten/Kota"] = df_trend["Kabupaten/Kota"].astype(str)

    return df_trend

df = load_data()

# ==============================
# LOAD GEOJSON
# ==============================
@st.cache_data
def load_geojson():
    with open("Jabar_By_Kab.geojson", "r", encoding="utf-8") as f:
        geojson = json.load(f)
    return geojson

geojson_jabar = load_geojson()


# ==============================
# PAGE CONTENT
# ==============================
if selected == "Home":
    st.title("📊 Dashboard Kasus HIV — Jawa Barat (2024)")
    st.caption("Sumber data: Dinas Kesehatan Jawa Barat")

    # Statistik ringkas dengan font besar
    total_kasus = int(df["Jumlah Kasus HIV"].sum())
    rata_rata = int(df["Jumlah Kasus HIV"].mean())
    median_kasus = int(df["Jumlah Kasus HIV"].median())
    min_kasus = int(df["Jumlah Kasus HIV"].min())
    max_kasus = int(df["Jumlah Kasus HIV"].max())
    range_kasus = f"{min_kasus} – {max_kasus}"

    # 4 kolom metric dengan angka super besar
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Kasus HIV (2024)", f"{total_kasus:,}".replace(",", "."))
    col2.metric("Rata-rata Kasus per Kab/Kota", f"{rata_rata:,}".replace(",", "."))
    col3.metric("Rentang Kasus", range_kasus)

    st.markdown("---")

    # Top 10 tabel dengan font besar
    st.subheader("🔝 10 Kabupaten/Kota dengan Kasus Tertinggi (2024)")
    df["Prevalensi per 100.000 Penduduk"] = (
        df["Jumlah Kasus HIV"] / df["Jumlah Penduduk (Ribu)"] * 100
    ).round(2)
    df["Jumlah Penduduk"] = (
        df["Jumlah Penduduk (Ribu)"] * 1000
    )
    top10 = df.sort_values("Jumlah Kasus HIV", ascending=False).head(10)
    st.dataframe(
        top10[[
            "Kabupaten/Kota",
            "Jumlah Kasus HIV",
            "Jumlah Penduduk",
            "Prevalensi per 100.000 Penduduk"
    ]],
    hide_index=True,
    use_container_width=True
    )

    st.markdown("---")

    # Bar chart distribusi dengan judul besar
    st.subheader("📌 Distribusi Kasus HIV per Kabupaten/Kota")
    fig_bar = px.bar(
        df.sort_values("Jumlah Kasus HIV", ascending=False),
        x="Kabupaten/Kota",
        y="Jumlah Kasus HIV",
        labels={"Kabupaten/Kota": "Kabupaten/Kota", "Jumlah Kasus HIV": "Jumlah Kasus"},
        title="Kasus HIV 2024 per Kabupaten/Kota",
        color="Jumlah Kasus HIV",
        color_continuous_scale="Reds"
    )
    fig_bar.update_layout(
        xaxis_tickangle=-45,
        height=450,
        title=dict(
            text="Kasus HIV 2024 per Kabupaten/Kota",
            x=0.5,
            xanchor="center",
            font=dict(size=20)
        )
    )    
    st.plotly_chart(fig_bar, use_container_width=True)

    # ==============================
    # TREN KASUS HIV PER TAHUN
    # ==============================
    st.markdown("---")
    st.subheader("⏳ Tren Kasus HIV per Tahun (2018–2024)")

    df_trend = load_trend_data()

    # ==============================
    # GRAFIK TOTAL PROVINSI
    # ==============================
    total_per_year = (
        df_trend
        .groupby("Tahun", as_index=False)["Jumlah Kasus"]
        .sum()
        .sort_values("Tahun")
    )

    fig_total = px.line(
        total_per_year,
        x="Tahun",
        y="Jumlah Kasus",
        markers=True,
        title="Total Kasus HIV Provinsi Jawa Barat per Tahun",
        labels={
            "Jumlah Kasus": "Jumlah Kasus",
            "Tahun": "Tahun"
        }
    )

    fig_total.update_layout(
        height=420,
        title=dict(
            text="Total Kasus HIV Provinsi Jawa Barat per Tahun",
            x=0.5,
            xanchor="center",
            font=dict(size=20)
        ),
        xaxis=dict(dtick=1),
        yaxis=dict(
            tickformat=".",
            title="Jumlah Kasus"
        )
    )

    st.plotly_chart(fig_total, use_container_width=True)

    st.markdown("---")

    # ==============================
    # GRAFIK PER KABUPATEN / KOTA
    # ==============================
    st.subheader("📈 Tren Kasus HIV per Kabupaten/Kota")

    # ==============================
    # FILTER KABUPATEN / KOTA
    # ==============================
    kabupaten_filter = st.selectbox(
        "Pilih Kabupaten/Kota:",
        ["Semua Kabupaten/Kota"] + sorted(df_trend["Kabupaten/Kota"].unique()),
        key="filter_tren_kab"
    )

    if kabupaten_filter == "Semua Kabupaten/Kota":
        fig_kab = px.line(
            df_trend,
            x="Tahun",
            y="Jumlah Kasus",
            color="Kabupaten/Kota",
            markers=False,
            title="Perubahan Kasus HIV per Kabupaten/Kota",
            labels={
                "Jumlah Kasus": "Jumlah Kasus",
                "Kabupaten/Kota": "Kabupaten/Kota"
            }
        )
    else:
        df_kab = df_trend[df_trend["Kabupaten/Kota"] == kabupaten_filter]

        fig_kab = px.line(
            df_kab,
            x="Tahun",
            y="Jumlah Kasus",
            markers=True,
            title=f"Tren Kasus HIV — {kabupaten_filter}",
            labels={
                "Jumlah Kasus": "Jumlah Kasus",
                "Tahun": "Tahun"
            }
        )

    if kabupaten_filter == "Semua Kabupaten/Kota":
        judul = "Perubahan Kasus HIV per Kabupaten/Kota"
    else:
        judul = f"Tren Kasus HIV — {kabupaten_filter}"

    fig_kab.update_layout(
        height=520,
        title=dict(
            text=judul,
            x=0.5,
            xanchor="center",
            font=dict(size=20)
        ),
        xaxis=dict(dtick=1),
        legend_title_text="Kabupaten/Kota"
    )

    st.plotly_chart(fig_kab, use_container_width=True)

    # ==============================
    # PETA INTERAKTIF KASUS HIV JABAR 2024
    # ==============================
    st.markdown("---")
    st.subheader("🗺️ Peta Sebaran Kasus HIV Jawa Barat (2024)")

    # Load GeoJSON
    import json
    with open("Jabar_By_Kab.geojson", "r", encoding="utf-8") as f:
        geojson = json.load(f)

    # ==============================
    # FILTER
    # ==============================
    col1, col2 = st.columns([1, 2])

    with col1:
        kab_filter = st.selectbox(
            "Pilih Kabupaten/Kota:",
            ["Semua Kabupaten/Kota"] + sorted(df["Kabupaten/Kota"].unique()),
            key="filter_peta_kab"
        )

    with col2:
        kasus_range = st.slider(
            "Range Jumlah Kasus",
            int(df["Jumlah Kasus HIV"].min()),
            int(df["Jumlah Kasus HIV"].max()),
            (
                int(df["Jumlah Kasus HIV"].min()),
                int(df["Jumlah Kasus HIV"].max())
            )
        )

    # ==============================
    # APPLY FILTER
    # ==============================
    df_map = df.copy()

    if kab_filter != "Semua Kabupaten/Kota":
        df_map = df_map[df_map["Kabupaten/Kota"] == kab_filter]

    df_map = df_map[
        (df_map["Jumlah Kasus HIV"] >= kasus_range[0]) &
        (df_map["Jumlah Kasus HIV"] <= kasus_range[1])
    ]

    # ==============================
    # CHOROPLETH MAP
    # ==============================
    df_map["_Jumlah_Penduduk_Display"] = df_map["Jumlah Penduduk (Ribu)"] * 1000
    fig_map = px.choropleth(
        df_map,
        geojson=geojson,
        locations="KABKOT_MAP",
        featureidkey="properties.KABKOT",
        color="Jumlah Kasus HIV",
        color_continuous_scale="Reds",
        hover_name="Kabupaten/Kota",
        custom_data=[
            "Jumlah Kasus HIV",
            "_Jumlah_Penduduk_Display",
            "Kepadatan Penduduk per km persegi (Km2)",
            "Rasio Jenis Kelamin Penduduk",
            "Tingkat Pengangguran Terbuka",
            "Persentase Penduduk Miskin"
        ]
    )

    fig_map.update_traces(
        hovertemplate=
        "<b>%{hovertext}</b><br><br>"
        "Jumlah Kasus HIV: %{customdata[0]:,.0f}<br>"
        "Jumlah Penduduk: %{customdata[1]:,.0f}<br>"
        "Kepadatan Penduduk: %{customdata[2]:,.0f}<br>"
        "Rasio Jenis Kelamin Penduduk: %{customdata[3]:.2f}<br>"
        "Tingkat Pengangguran Terbuka: %{customdata[4]:.2f}%<br>"
        "Persentase Penduduk Miskin: %{customdata[5]:.2f}%<br>"
        "<extra></extra>"
    )

    fig_map.update_coloraxes(colorbar_title="Jumlah Kasus")

    fig_map.update_geos(
        fitbounds="geojson",
        visible=False
    )

    if kab_filter == "Semua Kabupaten/Kota":
        judul = "Sebaran Kasus HIV 2024 per Kabupaten/Kota"
    else:
        judul = f"Sebaran Kasus HIV 2024 — {kab_filter}"

    fig_map.update_layout(
        height=600,
        margin={"r":0,"t":40,"l":0,"b":0},
        title=judul,
        title_font_size=20
    )

    st.plotly_chart(fig_map, use_container_width=True)

elif selected == "Deskripsi Penyakit":
    st.title("🧬 Deskripsi Penyakit HIV")
    # Konten teks dengan font lebih besar via CSS di atas

    st.markdown("---")
    st.markdown("""
    ### 📘 Definisi
    HIV (Human Immunodeficiency Virus) adalah virus yang merusak sel-sel sistem kekebalan tubuh yang berguna
                untuk melindungi tubuh dari serangan penyakit. Jika sel-sel tersebut rusak dan jumlahnya berkurang,
                daya tahan tubuh akan melemah dan penderitanya mudah terkena infeksi dan penyakit lainnya.
                
    Jika tidak ditangani dengan tepat, HIV dapat berkembang menjadi AIDS (Acquired Immunodeficiency Syndrome)
                dalam kurun waktu sekitar 10 tahun. AIDS merupakan stadium akhir dan paling serius dari infeksi HIV,
                yang ditandai dengan sistem kekebalan tubuh sudah sangat lemah dan tidak mampu melawan infeksi.
    """)

    st.markdown("---")
    st.markdown("""
    ### 🦠 Penyebab Terinfeksi
    - Hubungan seksual, baik melalui vaginal, anus, atau mulut, tanpa pengaman dengan penderita HIV
    - Penggunaan jarum suntik yang tidak steril secara bergantian
    - Transfusi darah yang terkontaminasi HIV
    - Kehamilan, persalinan, atau menyusui, pada ibu positif HIV yang menularkan ke bayinya
    """)

    st.markdown("---")
    col1, col2 = st.columns(2)
                
    with col1:
        st.subheader("🩺 Gejala Umum")
        st.markdown("""
        - Demam
        - Batuk-batuk
        - Sakit kepala
        - Nyeri otot dan sendi
        - Ruam kulit
        - Sakit tenggorokan
        - Sariawan yang terasa sangat sakit
        - Pembengkakan kelenjar getah bening, terutama di leher
        - Diare
        - Berkeringat pada malam hari
        """)

    with col2:
        st.subheader("🚨 Gejala Stadium Lanjut")
        st.markdown("""
        - Berkeringat terus-menerus
        - Demam berulang
        - Menggigil
        - Diare kronis
        - Bercak putih atau luka yang terus-menerus muncul di lidah atau mulut
        - Sering kelelahan
        - Tubuh terasa lemas
        - Berat badan turun drastis (cachexia)
        - Ruam atau benjolan di kulit
        """)

    st.markdown("---")
    st.markdown("""
    ### ⚠️ Faktor Risiko
    - Memiliki pasangan seksual lebih dari satu
    - Berhubungan intim, baik melalui vagina, anus, atau mulut, tanpa mengenakan kondom
    - Menderita penyakit menular seksual lainnya, seperti sifilis, klamidia, atau gonore
    - Berbagi jarum suntik pada penggunaan obat-obatan terlarang 
    - Menerima transfusi darah atau transplantasi organ dari pendonor yang terinfeksi HIV
    - Menjalani prosedur medis dengan alat yang tidak steril
    - Bekerja sebagai tenaga kesehatan, yang melibatkan kontak langsung dengan cairan tubuh manusia
    """)

    st.markdown("---")
    st.markdown("""
    ### 🛡️ Upaya Pencegahan
    - Tidak berganti-ganti pasangan seksual
    - Menggunakan kondom setiap berhubungan intim
    - Menjalani sunat
    - Memastikan pasangan tidak menderita penyakit menular seksual, termasuk HIV
    - Tidak berbagi penggunaan jarum suntik atau alat tajam lain
    - Melakukan pemeriksaan HIV secara rutin, terutama untuk individu yang berisiko terkena penyakit ini
    """)

    st.markdown("---")
    st.markdown("""        
    ### 📚 Sumber
    Alodokter - "HIV dan AIDS" [link](https://www.alodokter.com/hiv-aids)
    """)

elif selected == "Karakteristik Wilayah dan Kasus HIV":
    st.title("🧩 Karakteristik Wilayah dan Kasus HIV")

    # ==============================
    # NARASI PEMBUKA
    # ==============================
    st.markdown("""
    Tab ini menyajikan gambaran **karakteristik wilayah** kabupaten/kota di Provinsi Jawa Barat
    serta keterkaitannya dengan **jumlah kasus HIV tahun 2024**.  
    Analisis dilakukan pada **tingkat wilayah (ekologis)** dengan meninjau kondisi
    demografi dan sosial-ekonomi, sehingga **berbeda dengan faktor risiko individu**
    yang dibahas pada tab *Deskripsi Penyakit*.
    """)

    st.markdown("---")

    # ==============================
    # RINGKASAN INDIKATOR (5 GRAFIK)
    # ==============================
    st.subheader("📌 Ringkasan Karakteristik Demografi & Sosial-Ekonomi")

    fig_demo = make_subplots(
        rows=3,
        cols=2,
        vertical_spacing=0.25,
        specs=[
            [{}, {}],
            [{}, {}],
            [{"colspan": 2}, None]
        ],
        subplot_titles=[
            "👥 Jumlah Penduduk (Ribu)",
            "📍 Kepadatan Penduduk (/km²)",
            "💼 Tingkat Pengangguran Terbuka (%)",
            "📉 Persentase Penduduk Miskin (%)",
            "⚖️ Rasio Jenis Kelamin Penduduk"
        ]
    )

    # 1️⃣ Jumlah Penduduk
    fig_demo.add_trace(
        go.Bar(
            x=df["Kabupaten/Kota"],
            y=df["Jumlah Penduduk (Ribu)"]
        ),
        row=1, col=1
    )

    # 2️⃣ Kepadatan Penduduk
    fig_demo.add_trace(
        go.Bar(
            x=df["Kabupaten/Kota"],
            y=df["Kepadatan Penduduk per km persegi (Km2)"]
        ),
        row=1, col=2
    )

    # 3️⃣ Pengangguran
    fig_demo.add_trace(
        go.Bar(
            x=df["Kabupaten/Kota"],
            y=df["Tingkat Pengangguran Terbuka"]
        ),
        row=2, col=1
    )

    # 4️⃣ Kemiskinan
    fig_demo.add_trace(
        go.Bar(
            x=df["Kabupaten/Kota"],
            y=df["Persentase Penduduk Miskin"]
        ),
        row=2, col=2
    )

    # 5. Rasio Jenis Kelamin
    fig_demo.add_trace(
        go.Bar(
            x=df["Kabupaten/Kota"],
            y=df["Rasio Jenis Kelamin Penduduk"]
        ),
    row=3, col=1
    )

    # ==============================
    # LAYOUT
    # ==============================
    fig_demo.update_layout(
        height=1000,
        showlegend=False,
        title=dict(
            text="Indikator Demografi & Sosial-Ekonomi per Kabupaten/Kota",
            font=dict(size=30)
        ),
        margin=dict(t=100)
    )

    fig_demo.update_xaxes(tickangle=-45)

    st.plotly_chart(fig_demo, use_container_width=True)

    st.markdown("---")

    # ==============================
    # HUBUNGAN VARIABEL WILAYAH DENGAN KASUS HIV
    # ==============================
    st.subheader("🔍 Hubungan Karakteristik Wilayah dengan Jumlah Kasus HIV")

    variabel = st.selectbox(
        "Pilih Variabel Karakteristik Wilayah:",
        ["Jumlah Penduduk (Ribu)", "Kepadatan Penduduk per km persegi (Km2)",
         "Tingkat Pengangguran Terbuka", "Persentase Penduduk Miskin", "Rasio Jenis Kelamin Penduduk"]
    )

    fig_scatter = px.scatter(
        df,
        x=variabel,
        y="Jumlah Kasus HIV",
        text="Kabupaten/Kota",
        title=f"Jumlah Kasus HIV vs {variabel}",
        hover_data=["Kabupaten/Kota"]
    )
    fig_scatter.update_traces(textposition='top center')
    fig_scatter.update_layout(title_font_size=30)
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("""
    Pola sebaran titik menunjukkan bahwa **jumlah kasus HIV cenderung meningkat**
    pada wilayah dengan karakteristik tertentu, khususnya pada daerah dengan
    jumlah penduduk dan kepadatan penduduk yang lebih tinggi.  
    Temuan ini menjadi dasar eksplorasi lebih lanjut menggunakan **pemodelan regresi**
    pada analisis statistik.
    """)

    st.markdown("---")

    # ==============================
    # TABEL RINGKAS STATISTIK DESKRIPTIF
    # ==============================
    st.subheader("📋 Ringkasan Statistik Variabel Wilayah")

    tabel_ringkas = (
        df[[
            "Jumlah Kasus HIV",
            "Jumlah Penduduk (Ribu)",
            "Kepadatan Penduduk per km persegi (Km2)",
            "Rasio Jenis Kelamin Penduduk",
            "Tingkat Pengangguran Terbuka",
            "Persentase Penduduk Miskin"
        ]]
        .agg(["min", "max", "mean"])
        .T
        .rename(columns={
            "min": "Minimum",
            "max": "Maksimum",
            "mean": "Rata-rata"
        })
        .round(2)
    )

    st.dataframe(
        tabel_ringkas,
        use_container_width=True
    )

    st.caption(
        "Catatan: Statistik disajikan untuk menggambarkan "
        "variasi karakteristik wilayah kabupaten/kota sebelum dilakukan analisis pemodelan."
    )

elif selected == "Ukuran Epidemiologi":
    st.title("🔬 Ukuran Epidemiologi")

    # ==============================
    # 1️⃣ PREVALENSI (Ukuran Frekuensi)
    # ==============================
    st.subheader("📌 Ukuran Frekuensi — Prevalensi HIV")

    st.markdown("""
    **Pengertian:**  
    Prevalensi menggambarkan proporsi individu dalam populasi yang hidup dengan HIV pada suatu waktu tertentu.
    Pada dashboard ini, prevalensi dihitung berdasarkan jumlah kasus HIV tahun 2024 per 100.000 penduduk di Provinsi Jawa Barat.
    """)

    st.markdown("**Rumus Prevalensi:**")
    st.latex(r"\text{Prevalensi} = \frac{\text{Jumlah Kasus HIV}}{\text{Populasi}} \times 100.000")

    # --- Hitung prevalensi provinsi
    total_kasus = df["Jumlah Kasus HIV"].sum()
    total_populasi = (df["Jumlah Penduduk (Ribu)"] * 1000).sum()

    prevalensi_rasio = total_kasus / total_populasi
    prevalensi_per_100k = prevalensi_rasio * 100000
    prevalensi_persen = prevalensi_rasio * 100

    # --- Tampilkan indikator
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "Prevalensi HIV (per 100.000 penduduk)",
            f"{prevalensi_per_100k:,.2f}".replace(",", ".")
        )
    with col2:
        st.metric(
            "Prevalensi HIV (%)",
            f"{prevalensi_persen:.4f}%"
        )

    # --- Prevalensi per kabupaten/kota
    df_prev = df.copy()
    df_prev["Jumlah Penduduk"] = df_prev["Jumlah Penduduk (Ribu)"] * 1000
    df_prev["Prevalensi per 100.000"] = (
        df_prev["Jumlah Kasus HIV"] / df_prev["Jumlah Penduduk"] * 100000
    ).round(2)

    st.subheader("📊 Prevalensi HIV per Kabupaten/Kota (2024)")
    st.dataframe(
        df_prev[[
            "Kabupaten/Kota",
            "Jumlah Kasus HIV",
            "Jumlah Penduduk",
            "Prevalensi per 100.000"
        ]],
        hide_index=True,
        use_container_width=True
    )

    st.markdown(f"""
    **Interpretasi:**  
    Prevalensi HIV di Provinsi Jawa Barat tahun 2024 sebesar {prevalensi_per_100k:,.2f} per 100.000 penduduk, atau setara dengan {prevalensi_persen:.4f}% dari total populasi.
    Artinya, dari setiap 100.000 penduduk, terdapat sekitar {prevalensi_per_100k:.0f} individu yang hidup dengan HIV.
    Nilai ini menunjukkan bahwa HIV masih menjadi masalah kesehatan masyarakat yang perlu mendapatkan perhatian serius.
    """)

    st.markdown("---")

    # ==============================
    # 2️⃣ UKURAN ASOSIASI (PR & POR)
    # ==============================
    st.subheader("📌 Ukuran Asosiasi — PR dan POR")

    st.markdown("""
    **Pengertian:**  
    Ukuran asosiasi digunakan untuk menilai hubungan antara paparan (exposure) dan kejadian penyakit (outcome).
    Pada analisis ini, paparan yang digunakan adalah kepadatan penduduk, sedangkan outcome adalah kejadian HIV.
    """)

    # --- Klasifikasi paparan: kepadatan tinggi vs rendah
    rata_kepadatan = df["Kepadatan Penduduk per km persegi (Km2)"].mean()

    df_asos = df.copy()
    df_asos["Paparan"] = df_asos["Kepadatan Penduduk per km persegi (Km2)"] >= rata_kepadatan
    df_asos["HIV_Pos"] = df_asos["Jumlah Kasus HIV"]
    df_asos["HIV_Neg"] = (df_asos["Jumlah Penduduk (Ribu)"] * 1000) - df_asos["Jumlah Kasus HIV"]

    # --- Tabel 2x2
    a = df_asos.loc[df_asos["Paparan"], "HIV_Pos"].sum()
    b = df_asos.loc[df_asos["Paparan"], "HIV_Neg"].sum()
    c = df_asos.loc[~df_asos["Paparan"], "HIV_Pos"].sum()
    d = df_asos.loc[~df_asos["Paparan"], "HIV_Neg"].sum()

    tabel_2x2 = pd.DataFrame(
        {
            "HIV (+)": [a, c],
            "HIV (-)": [b, d]
        },
        index=["Kepadatan Tinggi", "Kepadatan Rendah"]
    )

    # Tambahin total baris & kolom (opsional tapi rapi)
    tabel_2x2.loc["Total"] = tabel_2x2.sum(axis=0)
    tabel_2x2["Total"] = tabel_2x2.sum(axis=1)

    st.subheader("📋 Tabel Kontingensi 2×2")
    st.dataframe(tabel_2x2, use_container_width=True)

    # --- Hitung PR dan POR
    PR = (a / (a + b)) / (c / (c + d))
    POR = (a * d) / (b * c)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Prevalence Ratio (PR)", f"{PR:.2f}")
    with col2:
        st.metric("Prevalence Odds Ratio (POR)", f"{POR:.2f}")

    st.markdown("**Rumus yang digunakan:**")
    st.latex(r"PR = \frac{\frac{a}{a+b}}{\frac{c}{c+d}}")
    st.latex(r"POR = \frac{a \times d}{b \times c}")

    st.markdown(f"""
    **Interpretasi:**  
    - Nilai Prevalence Ratio (PR) sebesar {PR:.2f} menunjukkan bahwa wilayah dengan
    kepadatan penduduk tinggi memiliki prevalensi HIV sekitar {PR:.2f} kali lebih besar
    dibandingkan wilayah dengan kepadatan penduduk rendah.  

    - Nilai Prevalence Odds Ratio (POR) sebesar {POR:.2f} mengindikasikan bahwa
    peluang terjadinya HIV di wilayah padat penduduk juga lebih tinggi.
    
    Nilai PR dan POR yang lebih besar dari satu menandakan adanya hubungan positif
    antara kepadatan penduduk dengan kejadian HIV di Jawa Barat tahun 2024.
    """)

elif selected == "About Research":
    st.title("ℹ️ About Research")
    st.markdown("""
    ## Dashboard Kasus HIV — Jawa Barat (2024)
    **🧪 Judul:** *Analisis Epidemiologi Kasus HIV di Jawa Barat Tahun 2024*
                
    **👩‍🎓 Disusun oleh:** Gina Kustiana

    **👨‍🏫 Dosen Pembimbing:** Dr. I Gede Nyoman Mindra Jaya, S.Si., M.Si          

    **🏛️ Institusi:** Universitas Padjadjaran
                
    **📅 Tahun:** 2025
    
    ---
    ### Tujuan Penelitian
    Penelitian ini bertujuan untuk menyajikan **analisis deskriptif** kasus Tuberkulosis (TBC) di tingkat kabupaten/kota
    Provinsi Jawa Barat, termasuk ukuran frekuensi penyakit (*prevalensi per 100.000 penduduk*), ukur
    serta tren kasus selama tahun **2022–2024**.

    ---
    ### Sumber Data
    - **Dinas Kesehatan Provinsi Jawa Barat** — Jumlah Kasus HIV (2018–2024)  
    - **BPS Provinsi Jawa Barat** — Jumlah Penduduk, Kepadatan Penduduk, Rasio Jenis Kelamin Penduduk, Tingkat Pengangguran Terbuka, Persentase Penduduk Miskin (2024)
    
    ---           
    ### Acknowledgement
    Penyusunan dashboard ini turut dibantu oleh **ChatGPT (OpenAI, model GPT-5)** dalam proses penulisan kode dan perancangan visualisasi. Seluruh hasil akhir telah diperiksa, disunting, dan disesuaikan oleh penulis.
                
    ---
    ### Hak Cipta & Lisensi
    Dashboard ini dibuat untuk keperluan **akademik dan edukasi**.  
    Seluruh data bersumber dari **publikasi resmi instansi pemerintah**.  

    © 2025 — *Gina Kustiana*.  

    """)

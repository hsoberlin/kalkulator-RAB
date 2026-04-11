import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
import streamlit_authenticator as stauth

# Konfigurasi Portrait untuk HP (Tema Elegan & Bersih)
st.set_page_config(page_title="Estimator RAB SGL", layout="centered")

# CSS Kustom untuk menyembunyikan elemen bawaan Streamlit & Memperbaiki Kontras Warna Teks
st.markdown("""
    <style>
        /* Mengubah Warna Dasar Aplikasi */
        :root {
            --primary-color: #F1C40F; /* Kuning/Emas SGL */
            --background-color: #0A192F; /* Biru Sangat Gelap */
            --secondary-background-color: #172A45; /* Biru Gelap (untuk card/input) */
            --text-color: #E6F1FF; /* Putih Kebiruan terang */
            --font: 'sans-serif';
        }

        /* Mewarnai Background Utama */
        .stApp {
            background-color: var(--background-color);
            color: var(--text-color);
        }

        /* Styling Input Widgets */
        .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div, .stTextArea>div>textarea {
            background-color: var(--secondary-background-color) !important;
            color: var(--text-color) !important;
            border-color: #1E3A8A !important;
        }
        
        /* Warna label judul dropdown & number input */
        .stTextInput>label, .stNumberInput>label, .stSelectbox>label, .stSlider>label {
            color: #8892B0 !important;
        }

        /* PERBAIKAN: Memaksa SEMUA tulisan di Radio Button dan Checkbox menjadi putih terang */
        div[role="radiogroup"] > label > div > p,
        label[data-baseweb="checkbox"] > div > p,
        label[data-baseweb="radio"] > div > p,
        div[data-testid="stRadio"] > label > div > p,
        .stCheckbox label p, .stRadio label p {
            color: #E6F1FF !important;
            font-weight: 500;
        }
        
        /* Memaksa Judul Radio (Metode Pelaksanaan:) agar kontras */
        div[data-testid="stRadio"] > label {
            color: #F1C40F !important;
        }

        /* Styling Tombol UTAMA */
        div.stButton > button:first-child {
            background-color: var(--primary-color) !important;
            color: #0A192F !important;
            border: none !important;
            font-weight: bold !important;
            width: 100%;
        }
        
        div.stButton > button:first-child:hover {
            background-color: #FFD700 !important;
            color: #000000 !important;
        }

        /* Styling Tombol SEKUNDER */
        div.stButton > button {
            background-color: var(--secondary-background-color);
            color: var(--primary-color);
            border: 1px solid var(--primary-color);
        }

        /* Styling Expander (Menu Lipat) */
        .streamlit-expanderHeader {
            background-color: var(--secondary-background-color) !important;
            color: var(--primary-color) !important;
            border-radius: 5px;
        }
        .streamlit-expanderHeader p {
            color: var(--primary-color) !important;
            font-weight: bold;
        }
        .streamlit-expanderContent {
            background-color: #112240 !important;
            border: 1px solid #1E3A8A;
        }
        
        /* Styling Info Box agar teks di dalamnya putih kontras */
        .stAlert {
            background-color: #112240 !important;
            border: 1px solid var(--primary-color) !important;
        }
        .stAlert p, .stAlert div {
            color: #E6F1FF !important;
        }

        /* Menyembunyikan elemen bawaan Streamlit */
        .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Set tema grafik Matplotlib ke Dark
plt.style.use('dark_background')

# =====================================================================
# SISTEM KEAMANAN (LOGIN HANYA 1 AKUN)
# =====================================================================
names = ['Pemeliharaan Sipil SGL']
usernames = ['harsipilsgl']
passwords_asli = ['harsipilsgl_2026']

# Menggunakan perintah .generate() yang terbukti jalan di sistem Anda
@st.cache_data
def get_hashed_passwords(passwords):
    return stauth.Hasher(passwords).generate()

hashed_passwords = get_hashed_passwords(passwords_asli)

credentials = {"usernames": {}}
for i in range(len(usernames)):
    credentials["usernames"][usernames[i]] = {"name": names[i], "password": hashed_passwords[i]}

authenticator = stauth.Authenticate(
    credentials,
    "rab_sgl_cookie",
    "signature_key_12345",
    cookie_expiry_days=30
)

# Tampilkan Form Login
name, authentication_status, username = authenticator.login("main")

# =====================================================================
# JIKA BERHASIL LOGIN, TAMPILKAN APLIKASI
# =====================================================================
if authentication_status:
    
    col_sapa, col_logout = st.columns([3, 1])
    with col_sapa:
        st.caption(f"Selamat bekerja, **{name}**!")
    with col_logout:
        authenticator.logout("Keluar", "main")

    if 'rekap_proyek' not in st.session_state:
        st.session_state.rekap_proyek = []

    # =====================================================================
    # HEADER APLIKASI
    # =====================================================================
    st.markdown("### Aplikasi Estimator RAB")
    st.caption("Sistem perhitungan teknis volume dan biaya konstruksi terpadu **by Pemeliharaan Sipil SGL**.")
    st.divider()

    # =====================================================================
    # BLOK 1: TAMBAH PEKERJAAN
    # =====================================================================
    st.markdown("#### ➕ Tambah Pekerjaan")

    jenis_bangunan = st.selectbox(
        "Pilih Jenis Pekerjaan:",
        [
            "1. Pekerjaan Persiapan",
            "2. Saluran Trapesium (Beton)", 
            "3. Saluran Pasangan Batu (Drainase)",
            "4. Jalan Perkerasan Lentur (Aspal)", 
            "5. Jalan Perkerasan Kaku (Rigid)",
            "6. Pondasi Telapak",
            "7. Dinding Penahan Tanah (Kantilever)",
            "8. Pondasi Bore Pile"
        ],
        key="navigasi_utama"
    )

    mode_proyek = st.radio(
        "Metode Pelaksanaan:", 
        ["Bangunan Baru", "Rehabilitasi Struktur"],
        horizontal=True,
        key="mode_global"
    )

    with st.expander("⚙️ Pengaturan Keuangan (OAT & PPN)"):
        overhead_pct = st.number_input("Overhead & Profit (%)", value=10.0, step=1.0, key="global_oh")
        ppn_pct = st.number_input("PPN / Pajak (%)", value=11.0, step=1.0, key="global_ppn")

    st.markdown("---")
    item_to_add = []
    kategori_pekerjaan = jenis_bangunan 

    # =====================================================================
    # LOGIKA 1. PEKERJAAN PERSIAPAN
    # =====================================================================
    if jenis_bangunan == "1. Pekerjaan Persiapan":
        st.markdown("**Input Item Persiapan (Lump Sum)**")
        
        show_survey = st.checkbox("Survey, Pengukuran & Pasang Bowplank", value=True, key="1_cb_surv")
        h_survey = st.number_input("Biaya Survey (Rp)", value=5000000, key="1_h_surv") if show_survey else 0

        show_k3 = st.checkbox("Penyelenggaraan SMK3 (K3 Konstruksi)", value=True, key="1_cb_k3")
        h_k3 = st.number_input("Biaya K3 (Rp)", value=3500000, key="1_h_k3") if show_k3 else 0

        show_mob = st.checkbox("Mobilisasi & Demobilisasi Alat Berat", value=True, key="1_cb_mob")
        h_mob = st.number_input("Biaya Mob-Demob (Rp)", value=12000000, key="1_h_mob") if show_mob else 0

        show_direksi = st.checkbox("Sewa/Pembuatan Direksi Keet", value=True, key="1_cb_dir")
        h_direksi = st.number_input("Biaya Direksi Keet (Rp)", value=7500000, key="1_h_dir") if show_direksi else 0

        if show_survey: item_to_add.append(["Survey, Pengukuran & Bowplank", 1.0, "LS", h_survey])
        if show_k3: item_to_add.append(["Penyelenggaraan SMK3", 1.0, "LS", h_k3])
        if show_mob: item_to_add.append(["Mobilisasi & Demobilisasi", 1.0, "LS", h_mob])
        if show_direksi: item_to_add.append(["Fasilitas Proyek/Direksi Keet", 1.0, "LS", h_direksi])

        fig, ax = plt.subplots(figsize=(4, 2))
        fig.patch.set_facecolor('#0A192F')
        ax.set_facecolor('#0A192F')
        ax.text(0.5, 0.5, 'Pekerjaan Persiapan & Umum\n(Non-Struktural)', horizontalalignment='center', verticalalignment='center', fontsize=12, fontweight='bold', color='#F1C40F')
        ax.set_axis_off()

    # =====================================================================
    # LOGIKA 2. SALURAN TRAPESIUM (BETON)
    # =====================================================================
    elif jenis_bangunan == "2. Saluran Trapesium (Beton)":
        st.markdown("**Input Dimensi Saluran**")
        l_atas = st.number_input("Lebar Dalam Atas (m)", value=1.2, key="2_la")
        l_bawah = st.number_input("Lebar Dalam Bawah (m)", value=0.8, key="2_lb")
        tinggi = st.number_input("Tinggi Saluran (m)", value=5.0, key="2_t")
        panjang = st.number_input("Panjang Saluran (m)", value=100.0, key="2_p")
        t_atas = st.number_input("Tebal Atas (m)", value=0.15, key="2_ta")
        t_bawah = st.number_input("Tebal Bawah (m)", value=0.25, key="2_tb")
        t_dasar = st.number_input("Tebal Dasar (m)", value=0.30, key="2_td")

        dist = (l_atas - l_bawah) / 2
        s_miring = np.sqrt(dist**2 + tinggi**2)
        vol_beton = (((t_atas + t_bawah) / 2 * s_miring * 2) + (l_bawah * t_dasar)) * panjang
        vol_tanah = (((l_atas+(2*t_atas) + l_bawah+(2*t_bawah))/2) * (tinggi+t_dasar)) * panjang
        vol_rongga = (((l_atas + l_bawah) / 2) * tinggi) * panjang

        st.markdown("**Input Pekerjaan & AHSP**")
        if mode_proyek == "Bangunan Baru":
            show_galian = st.checkbox("Galian Tanah Profil", value=True, key="2_cb_gal")
            h_galian = st.number_input("AHSP Galian (Rp/m³)", value=75000, key="2_h_gal") if show_galian else 0
            if show_galian: item_to_add.append(["Galian Tanah Profil Baru", vol_tanah, "m³", h_galian])
        else:
            p_bongkar = st.slider("Persen Bongkaran (%)", 0, 100, 100, key="2_sl_bongk")
            p_sedimen = st.slider("Persen Sedimen (%)", 0, 100, 30, key="2_sl_sed")
            show_bongkar = st.checkbox("Bongkaran Beton Eksisting", value=True, key="2_cb_bongk")
            h_bongkar = st.number_input("AHSP Bongkaran (Rp/m³)", value=250000, key="2_h_bongk") if show_bongkar else 0
            show_sedimen = st.checkbox("Galian Sedimen Saluran", value=True, key="2_cb_sed")
            h_sedimen = st.number_input("AHSP Galian Sedimen (Rp/m³)", value=85000, key="2_h_sed") if show_sedimen else 0
            if show_bongkar: item_to_add.append([f"Bongkaran Beton ({p_bongkar}%)", vol_beton*(p_bongkar/100), "m³", h_bongkar])
            if show_sedimen: item_to_add.append(["Galian Sedimen/Lumpur", vol_rongga*(p_sedimen/100), "m³", h_sedimen])

        show_bekisting = st.checkbox("Bekisting Dinding Saluran", value=True, key="2_cb_bek")
        h_bekisting = st.number_input("AHSP Bekisting (Rp/m²)", value=125000, key="2_h_bek") if show_bekisting else 0
        show_cor = st.checkbox("Pengecoran Beton Saluran", value=True, key="2_cb_cor")
        h_cor = st.number_input("AHSP Cor Beton (Rp/m³)", value=1200000, key="2_h_cor") if show_cor else 0
        show_besi = st.checkbox("Pembesian Saluran", value=True, key="2_cb_besi")
        r_besi = st.number_input("Rasio Besi (kg/m³)", value=110, key="2_r_besi") if show_besi else 0
        h_besi = st.number_input("AHSP Besi (Rp/kg)", value=18500, key="2_h_besi") if show_besi else 0

        if show_bekisting: item_to_add.append(["Bekisting Dinding Saluran", (s_miring * 2) * panjang, "m²", h_bekisting])
        if show_cor: item_to_add.append(["Beton Struktur Saluran", vol_beton, "m³", h_cor])
        if show_besi: item_to_add.append(["Pembesian Saluran", vol_beton * r_besi, "kg", h_besi])

        fig, ax = plt.subplots(figsize=(5, 3))
        fig.patch.set_facecolor('#0A192F')
        ax.set_facecolor('#0A192F')
        ax.add_patch(plt.Rectangle((-2, -tinggi-1), 4, tinggi+2, color='saddlebrown', alpha=0.3))
        ax.plot([-l_atas/2, -l_bawah/2, l_bawah/2, l_atas/2], [0, -tinggi, -tinggi, 0], color='white', lw=2)
        ax.set_aspect('equal')

    # =====================================================================
    # LOGIKA 3. SALURAN PASANGAN BATU
    # =====================================================================
    elif jenis_bangunan == "3. Saluran Pasangan Batu (Drainase)":
        st.markdown("**Input Dimensi Drainase**")
        l_atas = st.number_input("Lebar Atas (m)", value=1.0, key="3_la")
        l_bawah = st.number_input("Lebar Bawah (m)", value=0.6, key="3_lb")
        tinggi = st.number_input("Tinggi (m)", value=1.2, key="3_t")
        tebal = st.number_input("Tebal Batu (m)", value=0.25, key="3_tb")
        panjang = st.number_input("Panjang (m)", value=100.0, key="3_p")

        dist = (l_atas - l_bawah) / 2
        keliling = (2 * np.sqrt(dist**2 + tinggi**2)) + l_bawah
        vol_batu = keliling * tebal * panjang

        st.markdown("**Input Pekerjaan & AHSP**")
        if mode_proyek == "Bangunan Baru":
            vol_galian = (((l_atas+(2*tebal)) + (l_bawah+(2*tebal)))/2 * (tinggi+tebal)) * panjang
            show_galian = st.checkbox("Galian Tanah Drainase", value=True, key="3_cb_gal")
            h_galian = st.number_input("AHSP Galian (Rp/m³)", value=75000, key="3_h_gal") if show_galian else 0
            if show_galian: item_to_add.append(["Galian Tanah Drainase", vol_galian, "m³", h_galian])
        else:
            p_bongkar = st.slider("Persen Bongkaran (%)", 0, 100, 100, key="3_sl_bongk")
            show_bongkar = st.checkbox("Bongkaran Batu Eksisting", value=True, key="3_cb_bongk")
            h_bongkar = st.number_input("AHSP Bongkaran (Rp/m³)", value=150000, key="3_h_bongk") if show_bongkar else 0
            if show_bongkar: item_to_add.append([f"Bongkaran Batu Eksisting ({p_bongkar}%)", vol_batu * (p_bongkar/100), "m³", h_bongkar])

        show_pasangan = st.checkbox("Pasangan Batu Kali (1:4)", value=True, key="3_cb_pas")
        h_pasangan = st.number_input("AHSP Pasangan Batu (Rp/m³)", value=950000, key="3_h_pas") if show_pasangan else 0
        show_plester = st.checkbox("Plesteran + Acian", value=True, key="3_cb_ples")
        h_plester = st.number_input("AHSP Plesteran (Rp/m²)", value=65000, key="3_h_ples") if show_plester else 0

        if show_pasangan: item_to_add.append(["Pasangan Batu Kali (1:4)", vol_batu, "m³", h_pasangan])
        if show_plester: item_to_add.append(["Plesteran + Acian", keliling * panjang, "m²", h_plester])

        fig, ax = plt.subplots(figsize=(5, 3))
        fig.patch.set_facecolor('#0A192F')
        ax.set_facecolor('#0A192F')
        ax.plot([0, dist, dist+l_bawah, l_atas], [0, -tinggi, -tinggi, 0], color='white', lw=3)
        ax.set_aspect('equal')

    # =====================================================================
    # LOGIKA 4. JALAN PERKERASAN LENTUR (ASPAL)
    # =====================================================================
    elif jenis_bangunan == "4. Jalan Perkerasan Lentur (Aspal)":
        st.markdown("**Input Dimensi Jalan**")
        lebar = st.number_input("Lebar (m)", value=6.0, key="4_l")
        panjang = st.number_input("Panjang (m)", value=1000.0, key="4_p")
        t_aspal = st.number_input("Tebal Aspal (m)", value=0.05, key="4_tasp")
        t_base = st.number_input("Tebal Agregat (m)", value=0.15, key="4_tbase")

        st.markdown("**Input Pekerjaan & AHSP**")
        if mode_proyek == "Bangunan Baru":
            show_grading = st.checkbox("Penyiapan Badan Jalan", value=True, key="4_cb_grad")
            h_grading = st.number_input("AHSP Penyiapan (Rp/m²)", value=12000, key="4_h_grad") if show_grading else 0
            show_base = st.checkbox("Lapis Pondasi Agregat A", value=True, key="4_cb_base")
            h_base = st.number_input("AHSP Agregat A (Rp/m³)", value=450000, key="4_h_base") if show_base else 0
            if show_grading: item_to_add.append(["Penyiapan Badan Jalan", lebar * panjang, "m²", h_grading])
            if show_base: item_to_add.append(["Lapis Pondasi Agregat A", lebar * panjang * t_base, "m³", h_base])
        else:
            p_bongkar = st.slider("Persen Area Dikupas (%)", 0, 100, 100, key="4_sl_bongk")
            show_milling = st.checkbox("Cold Milling (Kupas Aspal)", value=True, key="4_cb_mill")
            h_milling = st.number_input("AHSP Milling (Rp/m³)", value=350000, key="4_h_mill") if show_milling else 0
            show_tack = st.checkbox("Lapis Perekat (Tack Coat)", value=True, key="4_cb_tack")
            h_tack = st.number_input("AHSP Tack Coat (Rp/Liter)", value=15000, key="4_h_tack") if show_tack else 0
            if show_milling: item_to_add.append([f"Cold Milling Kupas Aspal ({p_bongkar}%)", (lebar * panjang * t_aspal) * (p_bongkar/100), "m³", h_milling])
            if show_tack: item_to_add.append(["Lapis Perekat (Tack Coat)", lebar * panjang * 0.35, "Liter", h_tack])

        show_aspal = st.checkbox("Aspal Hotmix AC-WC", value=True, key="4_cb_asp")
        h_aspal = st.number_input("AHSP Aspal (Rp/m³)", value=2500000, key="4_h_asp") if show_aspal else 0
        if show_aspal: item_to_add.append(["Aspal Hotmix AC-WC", lebar * panjang * t_aspal, "m³", h_aspal])

        fig, ax = plt.subplots(figsize=(5, 3))
        fig.patch.set_facecolor('#0A192F')
        ax.set_facecolor('#0A192F')
        ax.add_patch(plt.Rectangle((0, -t_aspal), lebar, t_aspal, color='#F1C40F'))
        ax.set_xlim(-1, lebar+1); ax.set_ylim(-0.2, 0.1); ax.set_aspect('equal')

    # =====================================================================
    # LOGIKA 5. JALAN PERKERASAN KAKU (RIGID)
    # =====================================================================
    elif jenis_bangunan == "5. Jalan Perkerasan Kaku (Rigid)":
        st.markdown("**Input Dimensi Rigid**")
        lebar = st.number_input("Lebar (m)", value=5.0, key="5_l")
        panjang = st.number_input("Panjang (m)", value=500.0, key="5_p")
        t_rigid = st.number_input("Tebal Rigid (m)", value=0.25, key="5_trig")
        t_lc = st.number_input("Tebal Lantai Kerja (m)", value=0.10, key="5_tlc")

        st.markdown("**Input Pekerjaan & AHSP**")
        if mode_proyek == "Bangunan Baru":
            show_grading = st.checkbox("Penyiapan Badan Jalan", value=True, key="5_cb_grad")
            h_grading = st.number_input("AHSP Penyiapan (Rp/m²)", value=12000, key="5_h_grad") if show_grading else 0
            if show_grading: item_to_add.append(["Penyiapan Badan Jalan", lebar * panjang, "m²", h_grading])
        else:
            p_bongkar = st.slider("Persen Bongkaran (%)", 0, 100, 100, key="5_sl_bongk")
            show_bongkar = st.checkbox("Bongkaran Rigid Eksisting", value=True, key="5_cb_bongk")
            h_bongkar = st.number_input("AHSP Bongkaran Rigid (Rp/m³)", value=450000, key="5_h_bongk") if show_bongkar else 0
            if show_bongkar: item_to_add.append([f"Bongkaran Rigid Eksisting ({p_bongkar}%)", (lebar * panjang * t_rigid) * (p_bongkar/100), "m³", h_bongkar])

        show_lc = st.checkbox("Lantai Kerja (LC)", value=True, key="5_cb_lc")
        h_lc = st.number_input("AHSP Lantai Kerja (Rp/m³)", value=950000, key="5_h_lc") if show_lc else 0
        show_bekisting = st.checkbox("Bekisting Sisi Jalan", value=True, key="5_cb_bek")
        h_bekisting = st.number_input("AHSP Bekisting (Rp/m²)", value=125000, key="5_h_bek") if show_bekisting else 0
        show_rigid = st.checkbox("Beton Rigid K-350", value=True, key="5_cb_rig")
        h_rigid = st.number_input("AHSP Beton Rigid (Rp/m³)", value=1450000, key="5_h_rig") if show_rigid else 0
        show_besi = st.checkbox("Pembesian (Dowel/Wiremesh)", value=True, key="5_cb_besi")
        r_besi = st.number_input("Rasio Besi (kg/m³)", value=60, key="5_r_besi") if show_besi else 0
        h_besi = st.number_input("AHSP Besi (Rp/kg)", value=18500, key="5_h_besi") if show_besi else 0

        if show_lc: item_to_add.append(["Lantai Kerja (LC)", lebar * panjang * t_lc, "m³", h_lc])
        if show_bekisting: item_to_add.append(["Bekisting Sisi Jalan", (t_rigid + t_lc) * panjang * 2, "m²", h_bekisting])
        if show_rigid: item_to_add.append(["Beton Rigid K-350", lebar * panjang * t_rigid, "m³", h_rigid])
        if show_besi: item_to_add.append(["Pembesian (Dowel/Wiremesh)", (lebar * panjang * t_rigid) * r_besi, "kg", h_besi])

        fig, ax = plt.subplots(figsize=(5, 3))
        fig.patch.set_facecolor('#0A192F')
        ax.set_facecolor('#0A192F')
        ax.add_patch(plt.Rectangle((0, 0), lebar, t_rigid, color='#A0A0A0', hatch='//'))
        ax.add_patch(plt.Rectangle((0, -t_lc), lebar, t_lc, color='#F1C40F', alpha=0.5))
        ax.set_xlim(-1, lebar+1); ax.set_ylim(-0.3, 0.4); ax.set_aspect('equal')

    # =====================================================================
    # LOGIKA 6. PONDASI TELAPAK
    # =====================================================================
    elif jenis_bangunan == "6. Pondasi Telapak":
        st.markdown("**Input Dimensi Pondasi**")
        p = st.number_input("Panjang Plat (m)", value=1.5, key="6_p")
        l = st.number_input("Lebar Plat (m)", value=1.5, key="6_l")
        t = st.number_input("Tebal Plat (m)", value=0.3, key="6_t")
        jml = st.number_input("Jumlah Titik", value=10, key="6_jml")
        vol_beton = p * l * t * jml

        st.markdown("**Input Pekerjaan & AHSP**")
        if mode_proyek != "Bangunan Baru":
            p_bongkar = st.slider("Persen Bongkaran (%)", 0, 100, 100, key="6_sl_bongk")
            show_bongkar = st.checkbox("Bongkaran Struktur Lama", value=True, key="6_cb_bongk")
            h_bongkar = st.number_input("AHSP Bongkaran (Rp/m³)", value=350000, key="6_h_bongk") if show_bongkar else 0
            if show_bongkar: item_to_add.append([f"Bongkaran Struktur Lama ({p_bongkar}%)", vol_beton * (p_bongkar/100), "m³", h_bongkar])

        show_galian = st.checkbox("Galian Tanah Pondasi", value=True, key="6_cb_gal")
        h_galian = st.number_input("AHSP Galian (Rp/m³)", value=75000, key="6_h_gal") if show_galian else 0
        show_lc = st.checkbox("Lantai Kerja Pondasi", value=True, key="6_cb_lc")
        h_lc = st.number_input("AHSP Lantai Kerja (Rp/m³)", value=950000, key="6_h_lc") if show_lc else 0
        show_bekisting = st.checkbox("Bekisting Plat Pondasi", value=True, key="6_cb_bek")
        h_bekisting = st.number_input("AHSP Bekisting (Rp/m²)", value=145000, key="6_h_bek") if show_bekisting else 0
        show_cor = st.checkbox("Beton Plat Pondasi", value=True, key="6_cb_cor")
        h_cor = st.number_input("AHSP Beton (Rp/m³)", value=4500000, key="6_h_cor") if show_cor else 0
        show_besi = st.checkbox("Pembesian Pondasi", value=True, key="6_cb_besi")
        r_besi = st.number_input("Rasio Besi (kg/m³)", value=150, key="6_r_besi") if show_besi else 0
        h_besi = st.number_input("AHSP Besi (Rp/kg)", value=18500, key="6_h_besi") if show_besi else 0

        if show_galian: item_to_add.append(["Galian Tanah Pondasi", (p+0.4)*(l+0.4)*t*jml, "m³", h_galian])
        if show_lc: item_to_add.append(["Lantai Kerja Pondasi", p*l*0.05*jml, "m³", h_lc])
        if show_bekisting: item_to_add.append(["Bekisting Plat Pondasi", (p+l)*2*t*jml, "m²", h_bekisting])
        if show_cor: item_to_add.append(["Beton Plat Pondasi", vol_beton, "m³", h_cor])
        if show_besi: item_to_add.append(["Pembesian Pondasi", vol_beton * r_besi, "kg", h_besi])

        fig, ax = plt.subplots(figsize=(5, 3))
        fig.patch.set_facecolor('#0A192F')
        ax.set_facecolor('#0A192F')
        ax.add_patch(plt.Rectangle((-p/2, 0), p, t, color='#A0A0A0'))
        ax.set_xlim(-1, 1); ax.set_ylim(-0.2, 0.5); ax.set_aspect('equal')

    # =====================================================================
    # LOGIKA 7. DINDING PENAHAN TANAH (DPT)
    # =====================================================================
    elif jenis_bangunan == "7. Dinding Penahan Tanah (Kantilever)":
        st.markdown("**Input Dimensi DPT**")
        h = st.number_input("Tinggi Dinding (m)", value=4.0, key="7_h")
        l_base = st.number_input("Lebar Base (m)", value=2.5, key="7_lb")
        panjang = st.number_input("Panjang DPT (m)", value=50.0, key="7_p")
        vol_beton = ((0.4 * h) + (l_base * 0.4)) * panjang

        st.markdown("**Input Pekerjaan & AHSP**")
        if mode_proyek != "Bangunan Baru":
            p_bongkar = st.slider("Persen Bongkaran (%)", 0, 100, 100, key="7_sl_bongk")
            show_bongkar = st.checkbox("Bongkaran DPT Eksisting", value=True, key="7_cb_bongk")
            h_bongkar = st.number_input("AHSP Bongkaran (Rp/m³)", value=350000, key="7_h_bongk") if show_bongkar else 0
            if show_bongkar: item_to_add.append([f"Bongkaran DPT Eksisting ({p_bongkar}%)", vol_beton * (p_bongkar/100), "m³", h_bongkar])

        show_galian = st.checkbox("Galian Struktur DPT", value=True, key="7_cb_gal")
        h_galian = st.number_input("AHSP Galian (Rp/m³)", value=75000, key="7_h_gal") if show_galian else 0
        show_bekisting = st.checkbox("Bekisting DPT", value=True, key="7_cb_bek")
        h_bekisting = st.number_input("AHSP Bekisting (Rp/m²)", value=145000, key="7_h_bek") if show_bekisting else 0
        show_cor = st.checkbox("Pengecoran Beton DPT", value=True, key="7_cb_cor")
        h_cor = st.number_input("AHSP Beton (Rp/m³)", value=4200000, key="7_h_cor") if show_cor else 0
        show_besi = st.checkbox("Pembesian Struktur DPT", value=True, key="7_cb_besi")
        r_besi = st.number_input("Rasio Besi (kg/m³)", value=125, key="7_r_besi") if show_besi else 0
        h_besi = st.number_input("AHSP Besi (Rp/kg)", value=18500, key="7_h_besi") if show_besi else 0
        show_timbunan = st.checkbox("Timbunan Tanah Kembali", value=True, key="7_cb_timb")
        h_timbunan = st.number_input("AHSP Timbunan (Rp/m³)", value=115000, key="7_h_timb") if show_timbunan else 0

        if show_galian: item_to_add.append(["Galian Struktur DPT", l_base * 1.0 * panjang, "m³", h_galian])
        if show_bekisting: item_to_add.append(["Bekisting DPT", (h*2*panjang) + (0.4*2*panjang), "m²", h_bekisting])
        if show_cor: item_to_add.append(["Pengecoran Beton DPT", vol_beton, "m³", h_cor])
        if show_besi: item_to_add.append(["Pembesian Struktur DPT", vol_beton * r_besi, "kg", h_besi])
        if show_timbunan: item_to_add.append(["Timbunan Tanah Kembali", (l_base/2) * h * panjang, "m³", h_timbunan])

        fig, ax = plt.subplots(figsize=(5, 3))
        fig.patch.set_facecolor('#0A192F')
        ax.set_facecolor('#0A192F')
        ax.add_patch(plt.Rectangle((0, -0.4), l_base, 0.4, color='#A0A0A0'))
        ax.add_patch(plt.Rectangle((0.5, 0), 0.4, h, color='#A0A0A0'))
        ax.set_xlim(-0.5, l_base+0.5); ax.set_ylim(-1, h+1); ax.set_aspect('equal')

    # =====================================================================
    # LOGIKA 8. PONDASI BORE PILE
    # =====================================================================
    elif jenis_bangunan == "8. Pondasi Bore Pile":
        st.markdown("**Input Dimensi Bore Pile**")
        diameter = st.number_input("Diameter Pile (m)", value=0.6, key="8_d")
        kedalaman = st.number_input("Kedalaman Pile (m)", value=12.0, key="8_ked")
        jml_titik = st.number_input("Jumlah Titik", value=20, step=1, key="8_jml")
        
        area = np.pi * (diameter / 2)**2
        vol_total_beton = area * kedalaman * jml_titik
        vol_pengeboran = area * kedalaman * jml_titik

        st.markdown("**Input Pekerjaan & AHSP**")
        if mode_proyek == "Rehabilitasi Struktur":
            p_bongkar = st.slider("Persen Titik Dibongkar (%)", 0, 100, 100, key="8_sl_bongk")
            show_bongkar = st.checkbox("Pembersihan Lokasi/Bongkar Kepala", value=True, key="8_cb_bongk")
            h_bongkar = st.number_input("AHSP Pembersihan (Rp/Titik)", value=500000, key="8_h_bongk") if show_bongkar else 0
            if show_bongkar: item_to_add.append([f"Pembersihan Lokasi/Bongkar Kepala ({p_bongkar}%)", jml_titik * (p_bongkar/100), "Titik", h_bongkar])

        show_bor = st.checkbox("Pengeboran Bore Pile", value=True, key="8_cb_bor")
        h_bor = st.number_input("AHSP Pengeboran (Rp/m³)", value=450000, key="8_h_bor") if show_bor else 0
        show_casing = st.checkbox("Instalasi Temporary Casing", value=True, key="8_cb_cas")
        h_casing = st.number_input("AHSP Casing (Rp/m')", value=150000, key="8_h_cas") if show_casing else 0
        show_cor = st.checkbox("Pengecoran Beton K-350", value=True, key="8_cb_cor")
        h_cor = st.number_input("AHSP Beton (Rp/m³)", value=1350000, key="8_h_cor") if show_cor else 0
        show_besi = st.checkbox("Pembesian Tulangan", value=True, key="8_cb_besi")
        r_besi = st.number_input("Rasio Besi (kg/m³)", value=180, key="8_r_besi") if show_besi else 0
        h_besi = st.number_input("AHSP Besi (Rp/kg)", value=18500, key="8_h_besi") if show_besi else 0

        if show_bor: item_to_add.append(["Pengeboran Bore Pile", vol_pengeboran, "m³", h_bor])
        if show_casing: item_to_add.append(["Instalasi Temporary Casing", diameter * 2 * jml_titik, "m'", h_casing])
        if show_cor: item_to_add.append(["Pengecoran Beton K-350 (Bore Pile)", vol_total_beton, "m³", h_cor])
        if show_besi: item_to_add.append(["Pembesian Tulangan Bore Pile", vol_total_beton * r_besi, "kg", h_besi])

        fig, ax = plt.subplots(figsize=(5, 3))
        fig.patch.set_facecolor('#0A192F')
        ax.set_facecolor('#0A192F')
        ax.add_patch(plt.Rectangle((-1, -kedalaman), 2, kedalaman, color='saddlebrown', alpha=0.2))
        ax.add_patch(plt.Rectangle((-diameter/2, -kedalaman), diameter, color='#A0A0A0'))
        ax.set_xlim(-1, 1); ax.set_ylim(-kedalaman-1, 1); ax.set_aspect('equal')


    # =====================================================================
    # BLOK 2: REVIEW ESTIMASI SEMENTARA
    # =====================================================================
    st.divider()
    st.markdown(f"### 📝 Review Estimasi Sementara")
    st.caption(f"**Kategori Saat Ini:** {kategori_pekerjaan}")
    st.caption("⚠️ *Perhatian: Ini adalah rincian hitungan sementara. Anda **WAJIB** mengklik tombol **Tambahkan ke Master Rekap** di bawah agar data ini tersimpan ke Laporan Final.*")

    subtotal_now = 0
    for item in item_to_add:
        biaya = item[1] * item[3]
        subtotal_now += biaya
        st.markdown(f"- **{item[0]}**<br><span style='color:#E6F1FF; font-size:14px'>{item[1]:,.2f} {item[2]} x Rp {item[3]:,.0f} = <b style='color:var(--primary-color)'>Rp {biaya:,.0f}</b></span>", unsafe_allow_html=True)

    st.info(f"**Sub-Total Rincian Ini: Rp {subtotal_now:,.0f}**")

    if len(item_to_add) > 0:
        if st.button("TAMBAHKAN KE MASTER REKAP", use_container_width=True):
            for item in item_to_add:
                st.session_state.rekap_proyek.append({
                    "Kategori": kategori_pekerjaan, "Pekerjaan": item[0],
                    "Volume": round(item[1], 2), "Satuan": item[2],
                    "AHSP": item[3], "Total": item[1] * item[3]
                })
            st.success("Data berhasil ditambahkan ke tabel RAB di bawah.")

    st.pyplot(fig)


    # =====================================================================
    # BLOK 3: REKAP & MANAJEMEN DATA
    # =====================================================================
    st.divider()
    st.markdown("### 📁 Rekap & Manajemen Data")

    if st.session_state.rekap_proyek:
        
        with st.expander("✏️ Edit/Hapus Item Tersimpan"):
            st.caption("Pilih item di bawah ini untuk menyesuaikan ulang Volumenya:")
            opsi_edit = [f"{i+1}. {item['Pekerjaan']} ({item['Kategori'].split('.')[0]})" for i, item in enumerate(st.session_state.rekap_proyek)]
            pilihan_edit = st.selectbox("Pilih Item:", ["-- Pilih Item --"] + opsi_edit, key="select_edit")
            
            if pilihan_edit != "-- Pilih Item --":
                idx_edit = int(pilihan_edit.split(".")[0]) - 1
                item_terpilih = st.session_state.rekap_proyek[idx_edit]
                
                st.info(f"**Data Saat Ini:**\n- Vol: {item_terpilih['Volume']} {item_terpilih['Satuan']}\n- AHSP: Rp {item_terpilih['AHSP']:,.0f}")
                
                persen_adj = st.slider("Persentase Penyesuaian Volume (%)", 0, 200, 100, step=1, key=f"adj_{idx_edit}")
                vol_hitung = float(item_terpilih['Volume']) * (persen_adj / 100.0)
                
                val_vol = st.number_input(f"Edit Volume Akhir ({item_terpilih['Satuan']})", value=float(vol_hitung), key=f"ev_{idx_edit}_{persen_adj}")
                val_ahsp = st.number_input("Edit AHSP Akhir (Rp)", value=float(item_terpilih['AHSP']), key=f"ea_{idx_edit}")
                
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    if st.button("💾 Update", key=f"upd_{idx_edit}", use_container_width=True):
                        st.session_state.rekap_proyek[idx_edit]['Volume'] = val_vol
                        st.session_state.rekap_proyek[idx_edit]['AHSP'] = val_ahsp
                        st.session_state.rekap_proyek[idx_edit]['Total'] = val_vol * val_ahsp
                        st.rerun()
                with col_e2:
                    if st.button("🗑️ Hapus", key=f"del_{idx_edit}", use_container_width=True):
                        st.session_state.rekap_proyek.pop(idx_edit)
                        st.rerun()

        with st.expander("📂 Simpan/Buka Draft Proyek"):
            uploaded_file = st.file_uploader("Buka Draft RAB (.json)", type="json")
            if uploaded_file is not None:
                if st.button("📂 Muat File Draft Ini", use_container_width=True):
                    try:
                        draft_data = json.load(uploaded_file)
                        st.session_state.rekap_proyek = draft_data
                        st.success("Draft berhasil dimuat!")
                        st.rerun()
                    except Exception as e:
                        st.error("File draft tidak valid atau rusak.")
            
            if st.session_state.rekap_proyek:
                draft_json = json.dumps(st.session_state.rekap_proyek, indent=4)
                st.download_button(
                    label="💾 Simpan Draft Saat Ini (.json)",
                    data=draft_json,
                    file_name="Draft_RAB_Pemeliharaan_Sipil.json",
                    mime="application/json",
                    use_container_width=True
                )

        # =====================================================================
        # BLOK 4: LAPORAN RAB FINAL
        # =====================================================================
        st.divider()
        st.markdown("### 📊 Laporan Rencana Anggaran Biaya (RAB)")

        df = pd.DataFrame(st.session_state.rekap_proyek).sort_values(by="Kategori")
        display_data = []
        biaya_langsung = 0

        for kat in df['Kategori'].unique():
            df_kat = df[df['Kategori'] == kat]
            sub = df_kat['Total'].sum()
            biaya_langsung += sub
            
            nama_kat_bersih = kat.split(". ")[1] if ". " in kat else kat

            for _, row in df_kat.iterrows():
                display_data.append({
                    "Uraian Pekerjaan": row['Pekerjaan'], 
                    "Volume": f"{row['Volume']} {row['Satuan']}", 
                    "Harga Satuan": f"Rp {row['AHSP']:,.0f}", 
                    "Jumlah Harga": f"Rp {row['Total']:,.0f}"
                })
            display_data.append({
                "Uraian Pekerjaan": f"SUB-TOTAL {nama_kat_bersih.upper()}", 
                "Volume": "", "Harga Satuan": "", "Jumlah Harga": f"Rp {sub:,.0f}"
            })
            display_data.append({
                "Uraian Pekerjaan": "", "Volume": "", "Harga Satuan": "", "Jumlah Harga": ""
            })

        oh = biaya_langsung * (overhead_pct/100)
        ppn = (biaya_langsung + oh) * (ppn_pct/100)
        total_akhir = biaya_langsung + oh + ppn

        export_data = display_data.copy()
        export_data.append({"Uraian Pekerjaan": "========================================", "Volume": "", "Harga Satuan": "", "Jumlah Harga": ""})
        export_data.append({"Uraian Pekerjaan": "A. TOTAL BIAYA LANGSUNG", "Volume": "", "Harga Satuan": "", "Jumlah Harga": f"Rp {biaya_langsung:,.0f}"})
        export_data.append({"Uraian Pekerjaan": f"B. OVERHEAD & PROFIT ({overhead_pct}%)", "Volume": "", "Harga Satuan": "", "Jumlah Harga": f"Rp {oh:,.0f}"})
        export_data.append({"Uraian Pekerjaan": "C. TOTAL (A + B)", "Volume": "", "Harga Satuan": "", "Jumlah Harga": f"Rp {biaya_langsung + oh:,.0f}"})
        export_data.append({"Uraian Pekerjaan": f"D. PPN / PAJAK ({ppn_pct}%)", "Volume": "", "Harga Satuan": "", "Jumlah Harga": f"Rp {ppn:,.0f}"})
        export_data.append({"Uraian Pekerjaan": "GRAND TOTAL KONTRAK", "Volume": "", "Harga Satuan": "", "Jumlah Harga": f"Rp {total_akhir:,.0f}"})

        df_export = pd.DataFrame(export_data)
        st.dataframe(df_export, use_container_width=True, hide_index=True)

        st.write("---")
        if st.button("🗑️ Kosongkan Master Rekap / Buat Proyek Baru", use_container_width=True):
            st.session_state.rekap_proyek = []
            st.rerun()
    else:
        st.info("Tabel RAB masih kosong. Silakan tambah rincian estimasi di atas.")

# =====================================================================
# PESAN ERROR LOGIN
# =====================================================================
elif authentication_status is False:
    st.error("Username atau Password salah. Silakan coba lagi.")
elif authentication_status is None:
    st.warning("Silakan masukkan Username dan Password Anda.")
    st.info("Aplikasi Internal Pemeliharaan Sipil SGL. Akses Dibatasi. Tanpa Logo.")

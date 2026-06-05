import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json

# Konfigurasi Portrait untuk HP (Tema Elegan & Bersih)
st.set_page_config(page_title="KERAS - Estimator RAB", layout="centered")

# CSS Kustom untuk menyembunyikan elemen bawaan Streamlit
st.markdown("""
    <style>
        .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# SISTEM LOGIN (1 PINTU)
# =====================================================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #005c9a;'>🔒 LOGIN AKSES</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Kalkulator Estimasi RAB Sipil (KERAS) - PLTA Saguling</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.divider()
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("🔑 Masuk", use_container_width=True):
            if username == "sipil.saguling" and password == "Sipil2026!":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("❌ Username atau Password salah!")
    st.stop()

# =====================================================================
# INISIALISASI VARIABEL GLOBAL SETELAH LOGIN
# =====================================================================
if 'rekap_proyek' not in st.session_state:
    st.session_state.rekap_proyek = []

st.markdown("### Aplikasi Estimator RAB")
st.caption("Sistem perhitungan teknis volume dan biaya konstruksi terpadu **by Pemeliharaan Sipil SGL**.")
st.divider()

col_out1, col_out2 = st.columns([3, 1])
with col_out2:
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

# =====================================================================
# BLOK 1: TAMBAH PEKERJAAN
# =====================================================================
st.markdown("### ➕ Tambah Pekerjaan")

jenis_bangunan = st.selectbox(
    "Pilih Jenis Pekerjaan:",
    [
        "0. Pekerjaan Persiapan",
        "1. Saluran Air (Batu/Beton/Siklop)", 
        "2. Jalan Perkerasan Lentur (Aspal)", 
        "3. Jalan Perkerasan Kaku (Rigid)",
        "4. Pondasi Telapak",
        "5. Dinding Penahan Tanah (Stabilisasi Tebing)",
        "6. Pondasi Bore Pile",
        "7. Proteksi Lereng (Shotcrete & Soil Nailing)"
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
# LOGIKA 0. PEKERJAAN PERSIAPAN
# =====================================================================
if jenis_bangunan == "0. Pekerjaan Persiapan":
    st.markdown("**Item Persiapan**")
    
    show_survey = st.checkbox("Pekerjaan Pengukuran & Positioning", value=True, key="0_cb_surv")
    h_survey = st.number_input("Biaya Pengukuran (Rp)", value=13549401.09, key="0_h_surv") if show_survey else 0

    show_k3 = st.checkbox("Penyelenggaraan SMK3 (K3)", value=True, key="0_cb_k3")
    h_k3 = st.number_input("Biaya K3 (Rp)", value=43583110.75, key="0_h_k3") if show_k3 else 0

    show_mob = st.checkbox("Mobilisasi & Demobilisasi Alat", value=True, key="0_cb_mob")
    h_mob = st.number_input("Biaya Mob-Demob (Rp)", value=9865747.23, key="0_h_mob") if show_mob else 0

    show_direksi = st.checkbox("Fasilitas Penunjang Pekerjaan", value=True, key="0_cb_dir")
    h_direksi = st.number_input("Biaya Fasilitas (Rp)", value=27098802.18, key="0_h_dir") if show_direksi else 0
    
    show_desain = st.checkbox("Pekerjaan Desain Enjiniring", value=True, key="0_cb_des")
    h_desain = st.number_input("Biaya Desain (Rp)", value=55552544.46, key="0_h_des") if show_desain else 0
    
    show_admin = st.checkbox("Pekerjaan Administrasi", value=True, key="0_cb_adm")
    h_admin = st.number_input("Biaya Administrasi (Rp)", value=15600545.83, key="0_h_adm") if show_admin else 0
    
    show_sondir = st.checkbox("Pekerjaan Sondir", value=True, key="0_cb_son")
    vol_sondir = st.number_input("Jumlah Titik Sondir", value=2.0, key="0_v_son") if show_sondir else 0
    h_sondir = st.number_input("Biaya Sondir (Rp/Titik)", value=2438892.20, key="0_h_son") if show_sondir else 0

    if show_desain: item_to_add.append(["Pekerjaan Desain Enjiniring", 1.0, "LS", h_desain])
    if show_admin: item_to_add.append(["Pekerjaan Administrasi", 1.0, "LS", h_admin])
    if show_sondir: item_to_add.append(["Pekerjaan Sondir", vol_sondir, "Titik", h_sondir])
    if show_survey: item_to_add.append(["Pekerjaan Pengukuran dan Positioning", 1.0, "LS", h_survey])
    if show_k3: item_to_add.append(["Penyelenggaraan SMK3 (K3)", 1.0, "LS", h_k3])
    if show_mob: item_to_add.append(["Mobilisasi & Demobilisasi", 1.0, "LS", h_mob])
    if show_direksi: item_to_add.append(["Fasilitas Penunjang Pekerjaan", 1.0, "LS", h_direksi])

    fig, ax = plt.subplots(figsize=(4, 2))
    ax.text(0.5, 0.5, 'Pekerjaan Persiapan & Umum', horizontalalignment='center', verticalalignment='center', fontsize=12, fontweight='bold', color='gray')
    ax.set_axis_off()

# =====================================================================
# LOGIKA 1. SALURAN AIR (TERINTEGRASI)
# =====================================================================
elif jenis_bangunan == "1. Saluran Air (Batu/Beton/Siklop)":
    st.markdown("**Material & Lokasi Perbaikan**")
    tipe_saluran = st.radio("Pilih Tipe Struktur:", ["Pasangan Batu", "Beton Bertulang", "Beton Siklop"], horizontal=True, key="1_tipe")
    
    st.markdown("Pilih Sisi Kerusakan/Pekerjaan:")
    col_s1, col_s2, col_s3 = st.columns(3)
    c_kiri = col_s1.checkbox("Dinding Kiri", True, key="1_ckiri")
    c_lantai = col_s2.checkbox("Lantai Dasar", True, key="1_clantai")
    c_kanan = col_s3.checkbox("Dinding Kanan", True, key="1_ckanan")

    st.markdown("**Dimensi Saluran**")
    l_atas = st.number_input("Lebar Dalam Atas (m)", value=1.2, key="1_la")
    l_bawah = st.number_input("Lebar Dalam Bawah (m)", value=0.8, key="1_lb")
    tinggi = st.number_input("Tinggi Saluran (m)", value=1.5, key="1_t")
    panjang = st.number_input("Panjang Pekerjaan (m)", value=50.0, key="1_p")
    t_atas = st.number_input("Tebal Dinding Atas (m)", value=0.25, key="1_ta")
    t_bawah = st.number_input("Tebal Dinding Bawah (m)", value=0.40, key="1_tb")
    t_dasar = st.number_input("Tebal Lantai Dasar (m)", value=0.30, key="1_td")

    sisi_miring = np.sqrt(((l_atas - l_bawah) / 2)**2 + tinggi**2)
    vol_1_dinding = ((t_atas + t_bawah) / 2) * sisi_miring * panjang
    vol_lantai_m = l_bawah * t_dasar * panjang

    vol_aktif_kiri = vol_1_dinding if c_kiri else 0
    vol_aktif_kanan = vol_1_dinding if c_kanan else 0
    vol_aktif_lantai = vol_lantai_m if c_lantai else 0
    vol_total = vol_aktif_kiri + vol_aktif_kanan + vol_aktif_lantai

    luas_plester_bekisting = (sisi_miring * panjang if c_kiri else 0) + (sisi_miring * panjang if c_kanan else 0)
    luas_plester_lantai = (l_bawah * panjang if c_lantai else 0)

    st.markdown("**Pekerjaan & AHSP**")
    if mode_proyek != "Bangunan Baru":
        p_bongkar = st.slider("Persen Bongkaran Area Rusak (%)", 0, 100, 100, key="1_sl_bongk")
        show_bongkar = st.checkbox(f"Pembongkaran Struktur Eksisting", value=True, key="1_cb_bongk")
        h_bongkar = st.number_input("AHSP Bongkaran (Rp/m³)", value=380080.60, key="1_h_bongk") if show_bongkar else 0
        if show_bongkar: item_to_add.append([f"Pembongkaran Struktur Eksisting ({p_bongkar}%)", vol_total*(p_bongkar/100), "m³", h_bongkar])

    show_galian = st.checkbox("Pekerjaan Galian", value=True, key="1_cb_gal")
    vol_gal_kiri = (t_bawah * tinggi * panjang) if c_kiri else 0
    vol_gal_kanan = (t_bawah * tinggi * panjang) if c_kanan else 0
    vol_gal_lantai = (l_bawah * t_dasar * panjang) if c_lantai else 0
    h_galian = st.number_input("AHSP Galian (Rp/m³)", value=174954.45, key="1_h_gal") if show_galian else 0
    if show_galian: item_to_add.append(["Pekerjaan Galian", vol_gal_kiri+vol_gal_kanan+vol_gal_lantai, "m³", h_galian])

    if tipe_saluran == "Pasangan Batu":
        show_batu = st.checkbox("Pasangan Batu Kali (1:4)", value=True, key="1_cb_batu")
        h_batu = st.number_input("AHSP Pas. Batu (Rp/m³)", value=950000.0, key="1_h_batu") if show_batu else 0
        show_plester = st.checkbox("Plesteran + Acian", value=True, key="1_cb_ples")
        h_plester = st.number_input("AHSP Plesteran (Rp/m²)", value=65000.0, key="1_h_ples") if show_plester else 0
        
        if show_batu: item_to_add.append(["Pasangan Batu Kali (1:4)", vol_total, "m³", h_batu])
        if show_plester: item_to_add.append(["Plesteran Saluran Dalam", luas_plester_bekisting + luas_plester_lantai, "m²", h_plester])

    elif tipe_saluran == "Beton Bertulang":
        show_bek = st.checkbox("Pekerjaan Bekisting", value=True, key="1_cb_bek")
        h_bek = st.number_input("AHSP Bekisting (Rp/m²)", value=316349.06, key="1_h_bek") if show_bek else 0
        show_cor = st.checkbox("Beton", value=True, key="1_cb_cor")
        h_cor = st.number_input("AHSP Beton (Rp/m³)", value=1723402.09, key="1_h_cor") if show_cor else 0
        show_besi = st.checkbox("Tulangan Utama D16-200", value=True, key="1_cb_besi")
        r_besi = st.number_input("Rasio Besi (kg/m³)", value=110.0, key="1_r_besi") if show_besi else 0
        h_besi = st.number_input("AHSP Besi (Rp/kg)", value=23662.00, key="1_h_besi") if show_besi else 0

        if show_bek: item_to_add.append(["Pekerjaan Bekisting Saluran", luas_plester_bekisting, "m²", h_bek])
        if show_cor: item_to_add.append(["Beton Struktur Saluran", vol_total, "m³", h_cor])
        if show_besi: item_to_add.append(["Tulangan Utama D16-200 Saluran", vol_total * r_besi, "kg", h_besi])

    elif tipe_saluran == "Beton Siklop":
        show_bek = st.checkbox("Pekerjaan Bekisting", value=True, key="1_cb_bek")
        h_bek = st.number_input("AHSP Bekisting (Rp/m²)", value=316349.06, key="1_h_bek") if show_bek else 0
        show_cor = st.checkbox("Beton Siklop", value=True, key="1_cb_cor")
        h_cor = st.number_input("AHSP Beton Siklop (Rp/m³)", value=1723402.09, key="1_h_cor") if show_cor else 0

        if show_bek: item_to_add.append(["Pekerjaan Bekisting Saluran Siklop", luas_plester_bekisting, "m²", h_bek])
        if show_cor: item_to_add.append(["Beton Siklop Saluran", vol_total, "m³", h_cor])

    fig, ax = plt.subplots(figsize=(6, 4))
    x_kiri = -l_bawah/2
    x_kanan = l_bawah/2
    dx_atas = (l_atas - l_bawah)/2

    col_kiri = 'saddlebrown' if c_kiri else '#e0e0e0'
    col_kanan = 'saddlebrown' if c_kanan else '#e0e0e0'
    col_lantai = 'saddlebrown' if c_lantai else '#e0e0e0'

    pts_kiri = [[x_kiri, 0], [x_kiri - t_bawah, 0], [x_kiri - dx_atas - t_atas, tinggi], [x_kiri - dx_atas, tinggi]]
    ax.add_patch(plt.Polygon(pts_kiri, color=col_kiri, ec='black', alpha=0.8))
    pts_kanan = [[x_kanan, 0], [x_kanan + t_bawah, 0], [x_kanan + dx_atas + t_atas, tinggi], [x_kanan + dx_atas, tinggi]]
    ax.add_patch(plt.Polygon(pts_kanan, color=col_kanan, ec='black', alpha=0.8))
    pts_lantai = [[x_kiri, 0], [x_kanan, 0], [x_kanan, -t_dasar], [x_kiri, -t_dasar]]
    ax.add_patch(plt.Polygon(pts_lantai, color=col_lantai, ec='black', alpha=0.8))

    ax.text(0, tinggi/2, f'Ruang Air\nL:{l_atas}m', ha='center', va='center', color='blue', alpha=0.5)
    
    ax.set_xlim(-l_atas/2 - max(t_atas, t_bawah) - 0.5, l_atas/2 + max(t_atas, t_bawah) + 0.5)
    ax.set_ylim(-t_dasar - 0.5, tinggi + 0.5)
    ax.set_aspect('equal')
    ax.set_xlabel("Lebar Saluran (m)")
    ax.set_ylabel("Tinggi/Kedalaman (m)")
    ax.grid(True, linestyle='--', alpha=0.6)

# =====================================================================
# LOGIKA 2. JALAN PERKERASAN LENTUR (ASPAL)
# =====================================================================
elif jenis_bangunan == "2. Jalan Perkerasan Lentur (Aspal)":
    st.markdown("**Dimensi Jalan**")
    lebar = st.number_input("Lebar (m)", value=6.0, key="2_l")
    panjang = st.number_input("Panjang (m)", value=1000.0, key="2_p")
    t_aspal = st.number_input("Tebal Aspal (m)", value=0.05, key="2_tasp")
    t_base = st.number_input("Tebal Agregat (m)", value=0.15, key="2_tbase")

    st.markdown("**Pekerjaan & AHSP**")
    if mode_proyek == "Bangunan Baru":
        show_grading = st.checkbox("Pekerjaan Pemadatan Tanah / Badan Jalan", value=True, key="2_cb_grad")
        h_grading = st.number_input("AHSP Pemadatan (Rp/m²)", value=98640.49, key="2_h_grad") if show_grading else 0
        show_base = st.checkbox("Pekerjaan Lapis Pondasi A", value=True, key="2_cb_base")
        h_base = st.number_input("AHSP Lapis Pondasi A (Rp/m³)", value=527814.19, key="2_h_base") if show_base else 0
        if show_grading: item_to_add.append(["Pekerjaan Pemadatan Tanah / Badan Jalan", lebar * panjang, "m²", h_grading])
        if show_base: item_to_add.append(["Pekerjaan Lapis Pondasi A", lebar * panjang * t_base, "m³", h_base])
    else:
        p_bongkar = st.slider("Persen Area Dikupas (%)", 0, 100, 100, key="2_sl_bongk")
        show_milling = st.checkbox("Pembongkaran dan Pengangkutan Bongkaran Jalan", value=True, key="2_cb_mill")
        h_milling = st.number_input("AHSP Bongkaran Jalan (Rp/m³)", value=380080.60, key="2_h_mill") if show_milling else 0
        show_tack = st.checkbox("Lapis Perekat (Tack Coat)", value=True, key="2_cb_tack")
        h_tack = st.number_input("AHSP Tack Coat (Rp/Liter)", value=15000.0, key="2_h_tack") if show_tack else 0
        if show_milling: item_to_add.append([f"Pembongkaran dan Pengangkutan Bongkaran Jalan Eksisting ({p_bongkar}%)", (lebar * panjang * t_aspal) * (p_bongkar/100), "m³", h_milling])
        if show_tack: item_to_add.append(["Lapis Perekat (Tack Coat)", lebar * panjang * 0.35, "Liter", h_tack])

    show_aspal = st.checkbox("Aspal Hotmix AC-WC", value=True, key="2_cb_asp")
    h_aspal = st.number_input("AHSP Aspal (Rp/m³)", value=2500000.0, key="2_h_asp") if show_aspal else 0
    if show_aspal: item_to_add.append(["Aspal Hotmix AC-WC", lebar * panjang * t_aspal, "m³", h_aspal])
    
    show_guard = st.checkbox("Pemasangan Guard Rail", value=False, key="2_cb_gr")
    panjang_gr = st.number_input("Panjang Guard Rail (m')", value=100.0, key="2_p_gr") if show_guard else 0
    h_guard = st.number_input("AHSP Guard Rail (Rp/m')", value=2941333.18, key="2_h_gr") if show_guard else 0
    if show_guard: item_to_add.append(["Pemasangan Guard Rail", panjang_gr, "m'", h_guard])

    fig, ax = plt.subplots(figsize=(5, 3))
    ax.add_patch(plt.Rectangle((0, -t_aspal), lebar, t_aspal, color='black'))
    ax.set_xlim(-1, lebar+1); ax.set_ylim(-0.2, 0.1); ax.set_aspect('equal')
    ax.set_xlabel("Lebar Jalan (m)")
    ax.set_ylabel("Ketebalan (m)")
    ax.grid(True, linestyle='--', alpha=0.6)

# =====================================================================
# LOGIKA 3. JALAN PERKERASAN KAKU (RIGID)
# =====================================================================
elif jenis_bangunan == "3. Jalan Perkerasan Kaku (Rigid)":
    st.markdown("**Dimensi Rigid**")
    lebar = st.number_input("Lebar (m)", value=5.0, key="3_l")
    panjang = st.number_input("Panjang (m)", value=500.0, key="3_p")
    t_rigid = st.number_input("Tebal Rigid (m)", value=0.25, key="3_trig")
    t_lc = st.number_input("Tebal Lantai Kerja (m)", value=0.10, key="3_tlc")

    st.markdown("**Pekerjaan & AHSP**")
    if mode_proyek == "Bangunan Baru":
        show_grading = st.checkbox("Pekerjaan Pemadatan Tanah / Badan Jalan", value=True, key="3_cb_grad")
        h_grading = st.number_input("AHSP Pemadatan (Rp/m²)", value=98640.49, key="3_h_grad") if show_grading else 0
        if show_grading: item_to_add.append(["Pekerjaan Pemadatan Tanah / Badan Jalan", lebar * panjang, "m²", h_grading])
    else:
        p_bongkar = st.slider("Persen Bongkaran (%)", 0, 100, 100, key="3_sl_bongk")
        show_bongkar = st.checkbox("Pembongkaran Jalan Eksisting", value=True, key="3_cb_bongk")
        h_bongkar = st.number_input("AHSP Bongkaran (Rp/m³)", value=380080.60, key="3_h_bongk") if show_bongkar else 0
        if show_bongkar: item_to_add.append([f"Pembongkaran dan Pengangkutan Bongkaran Jalan Eksisting ({p_bongkar}%)", (lebar * panjang * t_rigid) * (p_bongkar/100), "m³", h_bongkar])

    show_lc = st.checkbox("Pekerjaan Lean Concrete (K125)", value=True, key="3_cb_lc")
    h_lc = st.number_input("AHSP Lean Concrete (Rp/m³)", value=1598159.55, key="3_h_lc") if show_lc else 0
    show_bekisting = st.checkbox("Pekerjaan Bekisting", value=True, key="3_cb_bek")
    h_bekisting = st.number_input("AHSP Bekisting (Rp/m²)", value=316349.06, key="3_h_bek") if show_bekisting else 0
    show_rigid = st.checkbox("Pekerjaan Beton FS 45", value=True, key="3_cb_rig")
    h_rigid = st.number_input("AHSP Beton FS 45 (Rp/m³)", value=2029697.10, key="3_h_rig") if show_rigid else 0
    show_wiremesh = st.checkbox("Pekerjaan Wiremesh M10 / Dowel", value=True, key="3_cb_besi")
    h_wiremesh = st.number_input("AHSP Wiremesh/Dowel", value=21973.22, key="3_h_besi") if show_wiremesh else 0
    r_besi = st.number_input("Estimasi Kebutuhan Besi Rigid", value=1.0, key="3_r_besi") if show_wiremesh else 0

    if show_lc: item_to_add.append(["Pekerjaan Lean Concrete (K125)", lebar * panjang * t_lc, "m³", h_lc])
    if show_bekisting: item_to_add.append(["Pekerjaan Bekisting", (t_rigid + t_lc) * panjang * 2, "m²", h_bekisting])
    if show_rigid: item_to_add.append(["Pekerjaan Beton FS 45", lebar * panjang * t_rigid, "m³", h_rigid])
    if show_wiremesh: item_to_add.append(["Pekerjaan Wiremesh M10 / Pemasangan Dowel", r_besi, "Satuan", h_wiremesh])

    show_guard = st.checkbox("Pemasangan Guard Rail", value=False, key="3_cb_gr")
    panjang_gr = st.number_input("Panjang Guard Rail (m')", value=100.0, key="3_p_gr") if show_guard else 0
    h_guard = st.number_input("AHSP Guard Rail (Rp/m')", value=2941333.18, key="3_h_gr") if show_guard else 0
    if show_guard: item_to_add.append(["Pemasangan Guard Rail", panjang_gr, "m'", h_guard])

    fig, ax = plt.subplots(figsize=(5, 3))
    ax.add_patch(plt.Rectangle((0, 0), lebar, t_rigid, color='gray', hatch='//'))
    ax.add_patch(plt.Rectangle((0, -t_lc), lebar, t_lc, color='orange', alpha=0.4))
    ax.set_xlim(-1, lebar+1); ax.set_ylim(-0.3, 0.4); ax.set_aspect('equal')
    ax.set_xlabel("Lebar Jalan (m)")
    ax.set_ylabel("Ketebalan (m)")
    ax.grid(True, linestyle='--', alpha=0.6)

# =====================================================================
# LOGIKA 4. PONDASI TELAPAK
# =====================================================================
elif jenis_bangunan == "4. Pondasi Telapak":
    st.markdown("**Dimensi Pondasi**")
    p = st.number_input("Panjang Plat (m)", value=1.5, key="4_p")
    l = st.number_input("Lebar Plat (m)", value=1.5, key="4_l")
    t = st.number_input("Tebal Plat (m)", value=0.3, key="4_t")
    jml = st.number_input("Jumlah Titik", value=10, key="4_jml")
    vol_beton = p * l * t * jml

    st.markdown("**Pekerjaan & AHSP**")
    if mode_proyek != "Bangunan Baru":
        p_bongkar = st.slider("Persen Bongkaran (%)", 0, 100, 100, key="4_sl_bongk")
        show_bongkar = st.checkbox("Pembongkaran Struktur Eksisting", value=True, key="4_cb_bongk")
        h_bongkar = st.number_input("AHSP Bongkaran (Rp/m³)", value=380080.60, key="4_h_bongk") if show_bongkar else 0
        if show_bongkar: item_to_add.append([f"Pembongkaran Struktur Eksisting ({p_bongkar}%)", vol_beton * (p_bongkar/100), "m³", h_bongkar])

    show_galian = st.checkbox("Pekerjaan Galian", value=True, key="4_cb_gal")
    h_galian = st.number_input("AHSP Galian (Rp/m³)", value=174954.45, key="4_h_gal") if show_galian else 0
    show_lc = st.checkbox("Pekerjaan Lean Concrete (K125)", value=True, key="4_cb_lc")
    h_lc = st.number_input("AHSP Lean Concrete (Rp/m³)", value=1598159.55, key="4_h_lc") if show_lc else 0
    show_bekisting = st.checkbox("Pekerjaan Bekisting", value=True, key="4_cb_bek")
    h_bekisting = st.number_input("AHSP Bekisting (Rp/m²)", value=316349.06, key="4_h_bek") if show_bekisting else 0
    show_cor = st.checkbox("Beton", value=True, key="4_cb_cor")
    h_cor = st.number_input("AHSP Beton (Rp/m³)", value=1723402.09, key="4_h_cor") if show_cor else 0
    show_besi = st.checkbox("Tulangan Utama D16-200", value=True, key="4_cb_besi")
    r_besi = st.number_input("Rasio Besi (kg/m³)", value=150.0, key="4_r_besi") if show_besi else 0
    h_besi = st.number_input("AHSP Besi (Rp/kg)", value=23662.00, key="4_h_besi") if show_besi else 0

    if show_galian: item_to_add.append(["Pekerjaan Galian Pondasi", (p+0.4)*(l+0.4)*t*jml, "m³", h_galian])
    if show_lc: item_to_add.append(["Pekerjaan Lean Concrete (K125)", p*l*0.05*jml, "m³", h_lc])
    if show_bekisting: item_to_add.append(["Pekerjaan Bekisting Plat Pondasi", (p+l)*2*t*jml, "m²", h_bekisting])
    if show_cor: item_to_add.append(["Beton Plat Pondasi", vol_beton, "m³", h_cor])
    if show_besi: item_to_add.append(["Tulangan Utama D16-200 Pondasi", vol_beton * r_besi, "kg", h_besi])

    fig, ax = plt.subplots(figsize=(5, 3))
    ax.add_patch(plt.Rectangle((-p/2, 0), p, t, color='gray'))
    ax.set_xlim(-1, 1); ax.set_ylim(-0.2, 0.5); ax.set_aspect('equal')
    ax.set_xlabel("Panjang Pondasi (m)")
    ax.set_ylabel("Ketebalan Plat (m)")
    ax.grid(True, linestyle='--', alpha=0.6)

# =====================================================================
# LOGIKA 5. DINDING PENAHAN TANAH (STABILISASI TEBING)
# =====================================================================
elif jenis_bangunan == "5. Dinding Penahan Tanah (Stabilisasi Tebing)":
    st.markdown("**Tipe Struktur & Dimensi**")
    tipe_dpt = st.radio("Pilih Tipe Struktur DPT:", [
        "Pasangan Batu (Gravity Wall)", 
        "Pasangan Batu Bertingkat (Terasering)",
        "Beton Siklop (Gravity Wall)",
        "Beton Siklop Bertingkat (Terasering)",
        "Beton Bertulang (Cantilever)"
    ], key="5_tipe")
    
    panjang = st.number_input("Panjang Total DPT (m)", value=50.0, key="5_p")

    if tipe_dpt in ["Pasangan Batu (Gravity Wall)", "Beton Siklop (Gravity Wall)"]:
        is_siklop = "Siklop" in tipe_dpt
        st.markdown("**Dimensi DPT Gravity Wall**")
        h = st.number_input("Tinggi Dinding (m)", value=4.0, key="5_g_h")
        l_bawah = st.number_input("Lebar Dasar/Bawah (m)", value=1.5, key="5_g_lb")
        l_atas = st.number_input("Lebar Atas (m)", value=0.4, key="5_g_la")
        offset_depan = st.number_input("Kemiringan Sisi Depan (m)", value=0.3, help="Jarak horizontal kemiringan dari ujung bawah ke ujung atas sisi depan.", key="5_g_off")
        
        vol_material = ((l_atas + l_bawah) / 2) * h * panjang
        
        # Hitung sisi miring untuk kebutuhan luasan plesteran/bekisting
        sisi_miring_depan = np.sqrt(h**2 + offset_depan**2)
        offset_belakang = l_bawah - offset_depan - l_atas
        sisi_miring_belakang = np.sqrt(h**2 + offset_belakang**2)
        luas_sisi_luar = (sisi_miring_depan + sisi_miring_belakang) * panjang
        
        vol_galian = l_bawah * h * panjang
        
        st.markdown("**Pekerjaan & AHSP**")
        if mode_proyek != "Bangunan Baru":
            p_bongkar = st.slider("Persen Bongkaran (%)", 0, 100, 100, key="5_g_sl_bongk")
            show_bongkar = st.checkbox("Pembongkaran Struktur Eksisting", value=True, key="5_g_cb_bongk")
            h_bongkar = st.number_input("AHSP Bongkaran (Rp/m³)", value=380080.60, key="5_g_h_bongk") if show_bongkar else 0
            if show_bongkar: item_to_add.append([f"Pembongkaran Struktur Eksisting ({p_bongkar}%)", vol_material * (p_bongkar/100), "m³", h_bongkar])

        show_galian = st.checkbox("Pekerjaan Galian", value=True, key="5_g_cb_gal")
        h_galian = st.number_input("AHSP Galian (Rp/m³)", value=174954.45, key="5_g_h_gal") if show_galian else 0
        
        show_timbunan = st.checkbox("Pekerjaan Urugan Kembali (Backfill)", value=True, key="5_g_cb_timb")
        h_timbunan = st.number_input("AHSP Urugan (Rp/m³)", value=94351.17, key="5_g_h_timb") if show_timbunan else 0
        
        # Volume timbunan wedge di sisi belakang dinding
        vol_timbunan = (0.5 * offset_belakang * h * panjang) if offset_belakang > 0 else 0
        
        if not is_siklop:
            show_mat = st.checkbox("Pasangan Batu Kali (1:4)", value=True, key="5_g_cb_mat")
            h_mat = st.number_input("AHSP Pasangan Batu (Rp/m³)", value=950000.0, key="5_g_h_mat") if show_mat else 0
            show_plester = st.checkbox("Plesteran & Siaran DPT", value=True, key="5_g_cb_ples")
            h_plester = st.number_input("AHSP Plesteran (Rp/m²)", value=65000.0, key="5_g_h_ples") if show_plester else 0
            
            if show_galian: item_to_add.append(["Pekerjaan Galian Tebing", vol_galian, "m³", h_galian])
            if show_mat: item_to_add.append(["Pasangan Batu Kali (1:4)", vol_material, "m³", h_mat])
            if show_plester: item_to_add.append(["Plesteran & Siaran Permukaan", luas_sisi_luar, "m²", h_plester])
            if show_timbunan: item_to_add.append(["Pekerjaan Urugan Kembali (Backfill)", vol_timbunan, "m³", h_timbunan])
        else:
            show_bekisting = st.checkbox("Pekerjaan Bekisting", value=True, key="5_g_cb_bek")
            h_bekisting = st.number_input("AHSP Bekisting (Rp/m²)", value=316349.06, key="5_g_h_bek") if show_bekisting else 0
            show_mat = st.checkbox("Beton Siklop", value=True, key="5_g_cb_mat")
            h_mat = st.number_input("AHSP Beton Siklop (Rp/m³)", value=1723402.09, key="5_g_h_mat") if show_mat else 0
            
            if show_galian: item_to_add.append(["Pekerjaan Galian Tebing", vol_galian, "m³", h_galian])
            if show_bekisting: item_to_add.append(["Pekerjaan Bekisting DPT Siklop", luas_sisi_luar, "m²", h_bekisting])
            if show_mat: item_to_add.append(["Beton Siklop DPT", vol_material, "m³", h_mat])
            if show_timbunan: item_to_add.append(["Pekerjaan Urugan Kembali (Backfill)", vol_timbunan, "m³", h_timbunan])

        show_suling = st.checkbox("Pipa Suling-Suling PVC 2\" + Ijuk", value=True, key="5_g_cb_suling")
        h_suling = st.number_input("AHSP Suling-suling (Rp/Titik)", value=45000.0, key="5_g_h_suling") if show_suling else 0
        if show_suling: item_to_add.append(["Instalasi Pipa Suling PVC 2\" + Ijuk", (luas_sisi_luar/2), "Titik", h_suling])

        # Visualisasi
        fig, ax = plt.subplots(figsize=(6, 5))
        pts_dinding = [
            [0, 0], 
            [l_bawah, 0], 
            [offset_depan + l_atas, h], 
            [offset_depan, h]
        ]
        ax.add_patch(plt.Polygon(pts_dinding, color='#8b9ea8' if is_siklop else 'slategray', ec='black', alpha=0.9))
        
        lebar_timbunan = max(1.0, offset_belakang + 0.5)
        pts_timbunan = [
            [l_bawah, 0],
            [l_bawah + lebar_timbunan, 0],
            [l_bawah + lebar_timbunan, h],
            [offset_depan + l_atas, h]
        ]
        ax.add_patch(plt.Polygon(pts_timbunan, color='saddlebrown', alpha=0.3, label='Timbunan Tebing'))
        ax.plot([-0.5, l_bawah + lebar_timbunan], [0, 0], color='saddlebrown', lw=3)
        
        ax.text(l_bawah/2, 0.2, f'{l_bawah}m', ha='center', va='bottom', fontsize=9, color='white')
        ax.text(offset_depan + l_atas/2, h - 0.3, f'{l_atas}m', ha='center', va='top', fontsize=9, color='white')
        
        ax.set_xlim(-1.0, l_bawah + lebar_timbunan + 0.5); ax.set_ylim(-0.5, h+1.0); ax.set_aspect('equal')
        ax.set_xlabel("Lebar Struktur (m)"); ax.set_ylabel("Tinggi/Elevasi (m)")
        ax.grid(True, linestyle='--', alpha=0.6); ax.legend(loc='upper right')

    elif tipe_dpt in ["Pasangan Batu Bertingkat (Terasering)", "Beton Siklop Bertingkat (Terasering)"]:
        is_siklop = "Siklop" in tipe_dpt
        jml_tingkat = st.number_input("Jumlah Tingkat (Trap)", value=3, step=1, min_value=1, key="5_ter_jml")
        h_trap = st.number_input("Tinggi per Tingkat (m)", value=2.0, key="5_ter_h")
        l_atas = st.number_input("Lebar Atas per Tingkat (m)", value=0.4, key="5_ter_la")
        l_bawah = st.number_input("Lebar Bawah per Tingkat (m)", value=1.0, key="5_ter_lb")
        l_berm = st.number_input("Lebar Pijakan/Berm antar Tingkat (m)", value=0.5, key="5_ter_berm")

        vol_per_trap = ((l_atas + l_bawah) / 2) * h_trap * panjang
        vol_total_mat = vol_per_trap * jml_tingkat
        sisi_miring = np.sqrt(h_trap**2 + (l_bawah - l_atas)**2)
        luas_sisi_luar = (sisi_miring * panjang * jml_tingkat) + (l_berm * panjang * (jml_tingkat - 1))
        
        lebar_galian_total = l_bawah + (l_berm * (jml_tingkat - 1))
        tinggi_total = h_trap * jml_tingkat
        vol_galian = lebar_galian_total * tinggi_total * panjang

        st.markdown("**Pekerjaan & AHSP**")
        if mode_proyek != "Bangunan Baru":
            p_bongkar = st.slider("Persen Bongkaran (%)", 0, 100, 100, key="5_ter_sl_bongk")
            show_bongkar = st.checkbox("Pembongkaran Struktur Eksisting", value=True, key="5_ter_cb_bongk")
            h_bongkar = st.number_input("AHSP Bongkaran (Rp/m³)", value=380080.60, key="5_ter_h_bongk") if show_bongkar else 0
            if show_bongkar: item_to_add.append([f"Pembongkaran Struktur Eksisting ({p_bongkar}%)", vol_total_mat * (p_bongkar/100), "m³", h_bongkar])

        show_galian = st.checkbox("Pekerjaan Galian", value=True, key="5_ter_cb_gal")
        h_galian = st.number_input("AHSP Galian (Rp/m³)", value=174954.45, key="5_ter_h_gal") if show_galian else 0
        
        if not is_siklop:
            show_mat = st.checkbox("Pasangan Batu Kali (1:4)", value=True, key="5_ter_cb_mat")
            h_mat = st.number_input("AHSP Pasangan Batu (Rp/m³)", value=950000.0, key="5_ter_h_mat") if show_mat else 0
            show_plester = st.checkbox("Plesteran & Siaran DPT", value=True, key="5_ter_cb_ples")
            h_plester = st.number_input("AHSP Plesteran (Rp/m²)", value=65000.0, key="5_ter_h_ples") if show_plester else 0
            
            if show_galian: item_to_add.append(["Pekerjaan Galian Tebing (Terasering)", vol_galian, "m³", h_galian])
            if show_mat: item_to_add.append(["Pasangan Batu Kali (Terasering)", vol_total_mat, "m³", h_mat])
            if show_plester: item_to_add.append(["Plesteran & Siaran Permukaan (Termasuk Berm)", luas_sisi_luar, "m²", h_plester])
        else:
            show_bekisting = st.checkbox("Pekerjaan Bekisting", value=True, key="5_ter_cb_bek")
            h_bekisting = st.number_input("AHSP Bekisting (Rp/m²)", value=316349.06, key="5_ter_h_bek") if show_bekisting else 0
            show_mat = st.checkbox("Beton Siklop", value=True, key="5_ter_cb_mat")
            h_mat = st.number_input("AHSP Beton Siklop (Rp/m³)", value=1723402.09, key="5_ter_h_mat") if show_mat else 0

            if show_galian: item_to_add.append(["Pekerjaan Galian Tebing (Terasering)", vol_galian, "m³", h_galian])
            if show_bekisting: item_to_add.append(["Pekerjaan Bekisting Terasering Siklop", luas_sisi_luar, "m²", h_bekisting])
            if show_mat: item_to_add.append(["Beton Siklop Terasering", vol_total_mat, "m³", h_mat])

        show_suling = st.checkbox("Pipa Suling-Suling PVC 2\" + Ijuk", value=True, key="5_ter_cb_suling")
        h_suling = st.number_input("AHSP Suling-suling (Rp/Titik)", value=45000.0, key="5_ter_h_suling") if show_suling else 0
        if show_suling: item_to_add.append(["Instalasi Pipa Suling PVC 2\" + Ijuk", ((sisi_miring * panjang * jml_tingkat)/2), "Titik", h_suling])

        fig, ax = plt.subplots(figsize=(6, 5))
        x_heel = 0; y_bottom = 0
        max_x = 0; min_x = 0
        soil_pts = [[0, 0]]
        for i in range(int(jml_tingkat)):
            x_toe = x_heel + l_bawah
            pts = np.array([[x_heel, y_bottom], [x_toe, y_bottom], [x_heel + l_atas, y_bottom + h_trap], [x_heel, y_bottom + h_trap]])
            ax.add_patch(plt.Polygon(pts, color='#8b9ea8' if is_siklop else 'slategray', alpha=0.9, ec='black', lw=1.5))
            
            ax.text(x_heel + l_bawah/2, y_bottom + 0.1, f'{l_bawah}m', ha='center', va='bottom', fontsize=8, color='white')
            ax.text(x_heel + l_atas/2, y_bottom + h_trap - 0.3, f'{l_atas}m', ha='center', va='top', fontsize=8, color='white')
            
            soil_pts.append([x_heel, y_bottom])
            soil_pts.append([x_heel, y_bottom + h_trap])

            if i < jml_tingkat - 1:
                next_x_toe = x_heel - l_berm
                next_x_heel = next_x_toe - l_bawah
                soil_pts.append([next_x_toe, y_bottom + h_trap])
                ax.text(x_heel - l_berm/2, y_bottom + h_trap + 0.1, f'Berm {l_berm}m', ha='center', va='bottom', fontsize=8, color='saddlebrown')
                x_heel = next_x_heel

            y_bottom += h_trap
            min_x = min(min_x, x_heel); max_x = max(max_x, x_toe)

        soil_pts.append([min_x - 2, y_bottom]); soil_pts.append([min_x - 2, 0])
        ax.add_patch(plt.Polygon(soil_pts, color='saddlebrown', alpha=0.2))
        x_s, y_s = zip(*soil_pts[:-2])
        ax.plot(x_s, y_s, color='saddlebrown', lw=3, label='Tanah / Tebing')

        ax.set_xlim(min_x - 1.5, max_x + 1.5); ax.set_ylim(-1, y_bottom + 1.5); ax.set_aspect('equal')
        ax.set_xlabel("Jarak Horizontal (m)"); ax.set_ylabel("Tinggi Elevasi (m)")
        ax.grid(True, linestyle='--', alpha=0.6); ax.legend(loc='upper left')

    else: # Beton Bertulang (Cantilever)
        st.markdown("**Dimensi Dinding Cantilever & Tapak**")
        h = st.number_input("Tinggi Dinding (Stem) (m)", value=4.0, key="5_c_h")
        l_base = st.number_input("Lebar Total Base/Tapak (m)", value=2.5, key="5_c_lb")
        t_base = st.number_input("Tebal Base/Tapak (m)", value=0.4, key="5_c_tb")
        l_toe = st.number_input("Jarak Ujung Depan ke Dinding (Toe) (m)", value=0.5, key="5_c_ltoe")
        t_bawah = st.number_input("Tebal Dinding Bawah (m)", value=0.5, key="5_c_tbwh")
        t_atas = st.number_input("Tebal Dinding Atas (m)", value=0.3, key="5_c_tats")

        use_counterfort = st.checkbox("Gunakan Sirip Penahan (Counterfort)", value=False, key="5_c_cf")
        vol_sirip_total = 0
        luas_bekisting_sirip = 0
        l_heel = l_base - l_toe - t_bawah

        if use_counterfort:
            col_cf1, col_cf2, col_cf3 = st.columns(3)
            t_bawah_sirip = col_cf1.number_input("Lebar Bawah Sirip (m)", value=l_heel, key="5_c_tsb")
            t_atas_sirip = col_cf2.number_input("Lebar Atas Sirip (m)", value=0.0, help="Isi 0 untuk bentuk Segitiga", key="5_c_tsa")
            t_tebal_sirip = col_cf3.number_input("Tebal Sirip (m)", value=0.3, key="5_c_tsirip")
            jarak_sirip = st.number_input("Jarak Antar Sirip (m)", value=2.5, key="5_c_jsirip")
            
            n_sirip = int(panjang / jarak_sirip) + 1
            vol_sirip_total = ((t_bawah_sirip + t_atas_sirip) / 2) * h * t_tebal_sirip * n_sirip
            sisi_miring_sirip = np.sqrt((t_bawah_sirip - t_atas_sirip)**2 + h**2)
            luas_bekisting_sirip = ((t_bawah_sirip + t_atas_sirip) * h) * n_sirip + (sisi_miring_sirip * t_tebal_sirip * n_sirip)

        vol_dinding = ((t_atas + t_bawah) / 2) * h * panjang
        vol_base = l_base * t_base * panjang
        vol_beton = vol_dinding + vol_base + vol_sirip_total
        
        # Galian dengan working space 1 meter (0.5m di setiap sisi)
        h_galian_input = st.number_input("Kedalaman Galian (m)", value=t_base + 0.5, key="5_c_hgal_in")
        vol_galian = (l_base + 1.0) * h_galian_input * panjang 
        
        sisi_miring_dinding = np.sqrt(h**2 + (t_bawah - t_atas)**2)
        luas_bekisting = (h + sisi_miring_dinding) * panjang + (t_base * 2 * panjang) + luas_bekisting_sirip

        st.markdown("**Pekerjaan & AHSP**")
        if mode_proyek != "Bangunan Baru":
            p_bongkar = st.slider("Persen Bongkaran (%)", 0, 100, 100, key="5_c_sl_bongk")
            show_bongkar = st.checkbox("Pembongkaran Struktur Eksisting", value=True, key="5_c_cb_bongk")
            h_bongkar = st.number_input("AHSP Bongkaran (Rp/m³)", value=380080.60, key="5_c_h_bongk") if show_bongkar else 0
            if show_bongkar: item_to_add.append([f"Pembongkaran Struktur Eksisting ({p_bongkar}%)", vol_beton * (p_bongkar/100), "m³", h_bongkar])

        show_galian = st.checkbox("Pekerjaan Galian (Termasuk Working Space 1m)", value=True, key="5_c_cb_gal")
        h_galian = st.number_input("AHSP Galian (Rp/m³)", value=174954.45, key="5_c_h_gal") if show_galian else 0
        show_bekisting = st.checkbox("Pekerjaan Bekisting", value=True, key="5_c_cb_bek")
        h_bekisting = st.number_input("AHSP Bekisting (Rp/m²)", value=316349.06, key="5_c_h_bek") if show_bekisting else 0
        show_cor = st.checkbox("Beton", value=True, key="5_c_cb_cor")
        h_cor = st.number_input("AHSP Beton (Rp/m³)", value=1723402.09, key="5_c_h_cor") if show_cor else 0
        show_besi = st.checkbox("Tulangan Utama D16-200", value=True, key="5_c_cb_besi")
        r_besi = st.number_input("Rasio Besi (kg/m³)", value=150.0 if use_counterfort else 125.0, key="5_c_r_besi") if show_besi else 0
        h_besi = st.number_input("AHSP Besi (Rp/kg)", value=23662.00, key="5_c_h_besi") if show_besi else 0
        
        st.markdown("**Material Timbunan**")
        jenis_timbunan = st.radio("Pilih Jenis Timbunan:", ["Tanah Kembali", "Sirtu / Material Pilihan"], horizontal=True, key="5_c_jtimb")
        show_timbunan = st.checkbox(f"Pekerjaan Urugan ({jenis_timbunan})", value=True, key="5_c_cb_timb")
        h_timbunan = st.number_input("AHSP Urugan (Rp/m³)", value=94351.17 if jenis_timbunan == "Tanah Kembali" else 527814.0, key="5_c_h_timb") if show_timbunan else 0

        if show_galian: item_to_add.append(["Pekerjaan Galian Struktur Tebing", vol_galian, "m³", h_galian])
        if show_bekisting: item_to_add.append(["Pekerjaan Bekisting DPT", luas_bekisting, "m²", h_bekisting])
        if show_cor: item_to_add.append([f"Beton DPT {'& Counterfort' if use_counterfort else ''}", vol_beton, "m³", h_cor])
        if show_besi: item_to_add.append(["Tulangan Utama Struktur DPT", vol_beton * r_besi, "kg", h_besi])
        
        vol_ruang_timbunan = (l_heel * h * panjang) + (0.5 * (t_bawah - t_atas) * h * panjang)
        vol_timbunan_netto = max(0, vol_ruang_timbunan - vol_sirip_total)

        if show_timbunan: item_to_add.append([f"Pekerjaan Urugan {jenis_timbunan}", vol_timbunan_netto, "m³", h_timbunan])

        show_suling = st.checkbox("Pipa Suling-Suling PVC 2\" + Ijuk", value=True, key="5_c_cb_suling")
        h_suling = st.number_input("AHSP Suling-suling (Rp/Titik)", value=45000.0, key="5_c_h_suling") if show_suling else 0
        if show_suling: item_to_add.append(["Instalasi Pipa Suling PVC 2\" + Ijuk", ((h*panjang)/2), "Titik", h_suling])

        fig, ax = plt.subplots(figsize=(6, 5))
        
        ax.add_patch(plt.Rectangle((0, -t_base), l_base, t_base, color='darkgray', ec='black'))
        pts_dinding = [
            [l_toe, 0], 
            [l_toe + t_bawah, 0], 
            [l_toe + t_atas, h], 
            [l_toe, h]
        ]
        ax.add_patch(plt.Polygon(pts_dinding, color='darkgray', ec='black'))
        
        if use_counterfort:
            pts_sirip = [
                [l_toe + t_bawah, 0],
                [l_toe + t_bawah + t_bawah_sirip, 0],
                [l_toe + t_atas + t_atas_sirip, h],
                [l_toe + t_atas, h]
            ]
            ax.add_patch(plt.Polygon(pts_sirip, color='gray', ec='black', alpha=0.5, label='Sirip Counterfort'))
        
        pts_timbunan = [
            [l_toe + t_bawah, 0],
            [l_base, 0],
            [l_base, h],
            [l_toe + t_atas, h]
        ]
        ax.add_patch(plt.Polygon(pts_timbunan, color='saddlebrown', alpha=0.3, hatch='//' if jenis_timbunan != "Tanah Kembali" else '', label=f'Timbunan ({jenis_timbunan.split(" ")[0]})'))
        
        ax.text(l_base/2, -t_base/2, f'{l_base}m', ha='center', va='center', fontsize=9, color='white')
        ax.text(l_toe + t_atas/2, h/2, f'{h}m', ha='center', va='center', fontsize=9, color='white', rotation=90)
        ax.text(l_toe + (t_bawah+t_atas)/2, h+0.2, f'{t_atas}m', ha='center', va='bottom', fontsize=9)
        ax.text(l_toe + t_bawah/2, 0.2, f'{t_bawah}m', ha='center', va='bottom', fontsize=9)
        
        ax.set_xlim(-1.0, l_base+1.0); ax.set_ylim(-t_base-1.0, h+1); ax.set_aspect('equal')
        ax.set_xlabel("Lebar Struktur (m)"); ax.set_ylabel("Tinggi/Elevasi (m)")
        ax.grid(True, linestyle='--', alpha=0.6); ax.legend(loc='upper right')

# =====================================================================
# LOGIKA 6. PONDASI BORE PILE
# =====================================================================
elif jenis_bangunan == "6. Pondasi Bore Pile":
    st.markdown("**Dimensi Bore Pile**")
    diameter = st.number_input("Diameter Pile (m)", value=0.6, key="6_d")
    kedalaman = st.number_input("Kedalaman Pile (m)", value=12.0, key="6_ked")
    jml_titik = st.number_input("Jumlah Titik", value=20, step=1, key="6_jml")
    
    area = np.pi * (diameter / 2)**2
    vol_total_beton = area * kedalaman * jml_titik
    vol_pengeboran = area * kedalaman * jml_titik

    st.markdown("**Pekerjaan & AHSP**")
    if mode_proyek == "Rehabilitasi Struktur":
        p_bongkar = st.slider("Persen Titik Dibongkar (%)", 0, 100, 100, key="6_sl_bongk")
        show_bongkar = st.checkbox("Pembongkaran Struktur Eksisting", value=True, key="6_cb_bongk")
        h_bongkar = st.number_input("AHSP Pembongkaran (Rp/Titik)", value=380080.60, key="6_h_bongk") if show_bongkar else 0
        if show_bongkar: item_to_add.append([f"Pembongkaran Struktur Eksisting / Kepala ({p_bongkar}%)", jml_titik * (p_bongkar/100), "Titik", h_bongkar])

    show_bor = st.checkbox("Bore Pile", value=True, key="6_cb_bor")
    h_bor = st.number_input("AHSP Pengeboran (Rp/m³)", value=935537.29, key="6_h_bor") if show_bor else 0
    show_casing = st.checkbox("Instalasi Temporary Casing", value=True, key="6_cb_cas")
    h_casing = st.number_input("AHSP Casing (Rp/m')", value=150000.0, key="6_h_cas") if show_casing else 0
    show_cor = st.checkbox("Beton", value=True, key="6_cb_cor")
    h_cor = st.number_input("AHSP Beton (Rp/m³)", value=1723402.09, key="6_h_cor") if show_cor else 0
    show_besi = st.checkbox("Tulangan Utama D16-200", value=True, key="6_cb_besi")
    r_besi = st.number_input("Rasio Besi (kg/m³)", value=180.0, key="6_r_besi") if show_besi else 0
    h_besi = st.number_input("AHSP Besi (Rp/kg)", value=23662.00, key="6_h_besi") if show_besi else 0

    if show_bor: item_to_add.append(["Bore Pile", vol_pengeboran, "m³", h_bor])
    if show_casing: item_to_add.append(["Instalasi Temporary Casing", diameter * 2 * jml_titik, "m'", h_casing])
    if show_cor: item_to_add.append(["Beton (Bore Pile)", vol_total_beton, "m³", h_cor])
    if show_besi: item_to_add.append(["Tulangan Utama D16-200 Bore Pile", vol_total_beton * r_besi, "kg", h_besi])

    fig, ax = plt.subplots(figsize=(5, 4))
    ax.add_patch(plt.Rectangle((-1, -kedalaman), 2, kedalaman, color='saddlebrown', alpha=0.1))
    ax.add_patch(plt.Rectangle((-diameter/2, -kedalaman), diameter, kedalaman, color='gray'))
    ax.set_xlim(-1, 1); ax.set_ylim(-kedalaman-1, 1); ax.set_aspect('equal')
    ax.set_xlabel("Lebar Galian/Diameter (m)"); ax.set_ylabel("Kedalaman (m)")
    ax.grid(True, linestyle='--', alpha=0.6)

# =====================================================================
# LOGIKA 7. PROTEKSI LERENG (SHOTCRETE & SOIL NAILING)
# =====================================================================
elif jenis_bangunan == "7. Proteksi Lereng (Shotcrete & Soil Nailing)":
    st.markdown("**Dimensi Lereng/Tebing**")
    col_l1, col_l2 = st.columns(2)
    panjang = col_l1.number_input("Panjang Memanjang Lereng (m)", value=50.0, key="7_p")
    tinggi_miring = col_l2.number_input("Panjang Miring Lereng (m)", value=15.0, help="Jarak dari kaki lereng ke puncak secara miring", key="7_tm")
    luas_lereng = panjang * tinggi_miring
    
    st.info(f"**Total Luas Permukaan Lereng:** {luas_lereng:,.2f} m²")

    st.markdown("**Spesifikasi Shotcrete / Facing Beton**")
    col_s1, col_s2 = st.columns(2)
    t_bawah_shot = col_s1.number_input("Tebal Facing Bawah (m)", value=0.20, key="7_tbwh")
    t_atas_shot = col_s2.number_input("Tebal Facing Atas (m)", value=0.10, help="Jika 0, penampang menjadi segitiga.", key="7_tats")
    t_rata_rata = (t_bawah_shot + t_atas_shot) / 2
    lapis_wiremesh = st.number_input("Jumlah Lapis Wiremesh M10", value=1, step=1, key="7_wm")
    
    st.markdown("**Spesifikasi Soil Nailing**")
    pakai_nailing = st.checkbox("Gunakan Soil Nailing?", value=True, key="7_cb_nail")
    
    if pakai_nailing:
        col_n1, col_n2 = st.columns(2)
        jarak_h = col_n1.number_input("Jarak Horizontal (m)", value=1.5, key="7_jh")
        jarak_v = col_n2.number_input("Jarak Vertikal (m)", value=1.5, key="7_jv")
        panjang_nail = st.number_input("Kedalaman Masuk Tanah (L) (m)", value=6.0, key="7_pn")
        
        jml_nailing = np.ceil(luas_lereng / (jarak_h * jarak_v))
        st.caption(f"*Estimasi kebutuhan: {int(jml_nailing)} Titik Soil Nailing*")
    else:
        jml_nailing = 0
        panjang_nail = 0

    st.markdown("**Pekerjaan & AHSP**")
    show_perapihan = st.checkbox("Pekerjaan Kupas/Perapihan Permukaan Lereng", value=True, key="7_cb_kupas")
    h_perapihan = st.number_input("AHSP Perapihan Lereng (Rp/m²)", value=25000.0, key="7_h_kupas") if show_perapihan else 0

    show_shotcrete = st.checkbox("Pekerjaan Shotcrete / Pengecoran Facing K-300", value=True, key="7_cb_shot")
    h_shotcrete = st.number_input("AHSP Shotcrete (Rp/m³)", value=2850000.0, key="7_h_shot") if show_shotcrete else 0
    
    show_wiremesh = st.checkbox(f"Pemasangan Wiremesh M10 ({lapis_wiremesh} Lapis)", value=True, key="7_cb_wm")
    h_wiremesh = st.number_input("AHSP Wiremesh (Rp/m²)", value=115000.0, key="7_h_wm") if show_wiremesh else 0

    if pakai_nailing:
        show_nailing = st.checkbox("Pekerjaan Soil Nailing D25 Terpasang", value=True, key="7_cb_do_nail")
        h_nailing = st.number_input("AHSP Soil Nailing (Rp/Titik)", value=1250000.0, help="Harga per titik mencakup Pengeboran, Besi D25, Grouting Epoxy/Semen, Bearing Plate, & Mur.", key="7_h_nail") if show_nailing else 0

    if show_perapihan: item_to_add.append(["Perapihan & Pembersihan Permukaan Lereng", luas_lereng, "m²", h_perapihan])
    if show_shotcrete: item_to_add.append(["Pekerjaan Shotcrete / Facing Beton", luas_lereng * t_rata_rata, "m³", h_shotcrete])
    if show_wiremesh: item_to_add.append([f"Pemasangan Wiremesh M10 ({lapis_wiremesh} Lapis + Overlap)", luas_lereng * lapis_wiremesh * 1.1, "m²", h_wiremesh]) 
    if pakai_nailing and show_nailing:
        item_to_add.append([f"Soil Nailing D25 (Kedalaman {panjang_nail}m)", jml_nailing, "Titik", h_nailing])

    fig, ax = plt.subplots(figsize=(6, 5))
    sudut = np.radians(60)
    h_visual = tinggi_miring * np.sin(sudut)
    w_visual = tinggi_miring * np.cos(sudut)
    
    ax.add_patch(plt.Polygon([[0, h_visual], [w_visual, 0], [w_visual + 10, 0], [w_visual + 10, h_visual + 10], [0, h_visual + 10]], color='saddlebrown', alpha=0.3, label="Tanah/Tebing Asli"))
    
    dx_atas = t_atas_shot * np.sin(sudut)
    dy_atas = t_atas_shot * np.cos(sudut)
    dx_bawah = t_bawah_shot * np.sin(sudut)
    dy_bawah = t_bawah_shot * np.cos(sudut)
    
    pts_shot = [
        [0, h_visual], 
        [w_visual, 0], 
        [w_visual - dx_bawah, -dy_bawah], 
        [-dx_atas, h_visual - dy_atas]
    ]
    ax.add_patch(plt.Polygon(pts_shot, color='gray', label=f'Facing (B:{t_bawah_shot}m, A:{t_atas_shot}m)'))
    
    if pakai_nailing:
        jarak_visual_v = tinggi_miring / 5
        for i in range(1, 5):
            L_tempuh = i * jarak_visual_v
            x_surf = L_tempuh * np.cos(sudut)
            y_surf = h_visual - (L_tempuh * np.sin(sudut))
            x_dalam = x_surf + (panjang_nail * np.sin(sudut))
            y_dalam = y_surf + (panjang_nail * np.cos(sudut))
            ax.plot([x_surf, x_dalam], [y_surf, y_dalam], color='black', lw=3)
            ax.plot([x_surf, x_dalam], [y_surf, y_dalam], color='red', lw=1.5, linestyle='--')
            ax.scatter([x_surf - (dx_atas+dx_bawah)/4], [y_surf - (dy_atas+dy_bawah)/4], color='blue', s=80, zorder=5)
            
        ax.plot([], [], color='red', linestyle='--', label=f'Soil Nail D25 (L={panjang_nail}m)')
        ax.scatter([], [], color='blue', label='Bearing Plate')

    ax.set_xlim(-max(2.0, t_atas_shot + 1), w_visual + panjang_nail + 2)
    ax.set_ylim(-max(2.0, t_bawah_shot + 1), h_visual + panjang_nail)
    ax.set_aspect('equal')
    ax.set_title("Visualisasi Penampang Proteksi Lereng")
    ax.grid(True, linestyle='--', alpha=0.6); ax.legend(loc='lower right')

# =====================================================================
# BLOK 2: REVIEW ESTIMASI SEMENTARA
# =====================================================================
st.markdown("---")
st.markdown(f"### 📝 Rincian Estimasi Sementara")
st.caption(f"**Kategori Saat Ini:** {kategori_pekerjaan}")
st.caption("⚠️ *Perhatian: Ini adalah rincian hitungan sementara. Anda **WAJIB** mengklik tombol **Tambahkan ke Master Rekap** di bawah agar data ini tersimpan ke Laporan Final.*")

subtotal_now = 0
for item in item_to_add:
    biaya = item[1] * item[3]
    subtotal_now += biaya
    st.markdown(f"- **{item[0]}**<br><span style='color:gray; font-size:14px'>{item[1]:,.2f} {item[2]} x Rp {item[3]:,.0f} = **Rp {biaya:,.0f}**</span>", unsafe_allow_html=True)

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

st.markdown("---")
st.pyplot(fig)


# =====================================================================
# BLOK 3: LAPORAN RAB & MANAJEMEN DATA
# =====================================================================
st.divider()
st.markdown("### 📊 Laporan Rencana Anggaran Biaya")

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

    with st.expander("📁 Manajemen Draft Proyek (Simpan/Buka)"):
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
        display_data.append({"Uraian Pekerjaan": f"SUB-TOTAL {nama_kat_bersih.upper()}", "Volume": "", "Harga Satuan": "", "Jumlah Harga": f"Rp {sub:,.0f}"})
        display_data.append({"Uraian Pekerjaan": "", "Volume": "", "Harga Satuan": "", "Jumlah Harga": ""})

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
    st.dataframe(df_export, use_container_width=True)

    st.write("---")
    if st.button("🗑️ Kosongkan Master Rekap / Buat Proyek Baru", use_container_width=True):
        st.session_state.rekap_proyek = []
        st.rerun()
else:
    st.info("Tabel RAB masih kosong. Silakan tambah rincian estimasi di atas.")

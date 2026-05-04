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
        "6. Pondasi Bore Pile"
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
    st.markdown("**Item Persiapan (Lump Sum)**")
    
    show_survey = st.checkbox("Survey, Pengukuran & Pasang Bowplank", value=True, key="0_cb_surv")
    h_survey = st.number_input("Biaya Survey (Rp)", value=5000000, key="0_h_surv") if show_survey else 0

    show_k3 = st.checkbox("Penyelenggaraan SMK3 (K3 Konstruksi)", value=True, key="0_cb_k3")
    h_k3 = st.number_input("Biaya K3 (Rp)", value=3500000, key="0_h_k3") if show_k3 else 0

    show_mob = st.checkbox("Mobilisasi & Demobilisasi Alat Berat", value=True, key="0_cb_mob")
    h_mob = st.number_input("Biaya Mob-Demob (Rp)", value=12000000, key="0_h_mob") if show_mob else 0

    show_direksi = st.checkbox("Sewa/Pembuatan Direksi Keet", value=True, key="0_cb_dir")
    h_direksi = st.number_input("Biaya Direksi Keet (Rp)", value=7500000, key="0_h_dir") if show_direksi else 0

    if show_survey: item_to_add.append(["Survey, Pengukuran & Bowplank", 1.0, "LS", h_survey])
    if show_k3: item_to_add.append(["Penyelenggaraan SMK3", 1.0, "LS", h_k3])
    if show_mob: item_to_add.append(["Mobilisasi & Demobilisasi", 1.0, "LS", h_mob])
    if show_direksi: item_to_add.append(["Fasilitas Proyek/Direksi Keet", 1.0, "LS", h_direksi])

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

    # Hitung Volume Terpisah
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
        show_bongkar = st.checkbox(f"Bongkaran Struktur Eksisting", value=True, key="1_cb_bongk")
        h_bongkar = st.number_input("AHSP Bongkaran (Rp/m³)", value=250000 if tipe_saluran!="Pasangan Batu" else 150000, key="1_h_bongk") if show_bongkar else 0
        if show_bongkar: item_to_add.append([f"Bongkaran {tipe_saluran} ({p_bongkar}%)", vol_total*(p_bongkar/100), "m³", h_bongkar])

    show_galian = st.checkbox("Galian Tanah", value=True, key="1_cb_gal")
    vol_gal_kiri = (t_bawah * tinggi * panjang) if c_kiri else 0
    vol_gal_kanan = (t_bawah * tinggi * panjang) if c_kanan else 0
    vol_gal_lantai = (l_bawah * t_dasar * panjang) if c_lantai else 0
    h_galian = st.number_input("AHSP Galian (Rp/m³)", value=75000, key="1_h_gal") if show_galian else 0
    if show_galian: item_to_add.append(["Galian Tanah Saluran", vol_gal_kiri+vol_gal_kanan+vol_gal_lantai, "m³", h_galian])

    # Logika Material
    if tipe_saluran == "Pasangan Batu":
        show_batu = st.checkbox("Pasangan Batu Kali (1:4)", value=True, key="1_cb_batu")
        h_batu = st.number_input("AHSP Pas. Batu (Rp/m³)", value=950000, key="1_h_batu") if show_batu else 0
        show_plester = st.checkbox("Plesteran + Acian", value=True, key="1_cb_ples")
        h_plester = st.number_input("AHSP Plesteran (Rp/m²)", value=65000, key="1_h_ples") if show_plester else 0
        
        if show_batu: item_to_add.append(["Pasangan Batu Kali (1:4)", vol_total, "m³", h_batu])
        if show_plester: item_to_add.append(["Plesteran Saluran Dalam", luas_plester_bekisting + luas_plester_lantai, "m²", h_plester])

    elif tipe_saluran == "Beton Bertulang":
        show_bek = st.checkbox("Bekisting Saluran", value=True, key="1_cb_bek")
        h_bek = st.number_input("AHSP Bekisting (Rp/m²)", value=125000, key="1_h_bek") if show_bek else 0
        show_cor = st.checkbox("Cor Beton K-225/K-250", value=True, key="1_cb_cor")
        h_cor = st.number_input("AHSP Cor Beton (Rp/m³)", value=1200000, key="1_h_cor") if show_cor else 0
        show_besi = st.checkbox("Pembesian", value=True, key="1_cb_besi")
        r_besi = st.number_input("Rasio Besi (kg/m³)", value=110, key="1_r_besi") if show_besi else 0
        h_besi = st.number_input("AHSP Besi (Rp/kg)", value=18500, key="1_h_besi") if show_besi else 0

        if show_bek: item_to_add.append(["Bekisting Permukaan Saluran", luas_plester_bekisting, "m²", h_bek])
        if show_cor: item_to_add.append(["Cor Beton Struktur Saluran", vol_total, "m³", h_cor])
        if show_besi: item_to_add.append(["Pembesian Saluran", vol_total * r_besi, "kg", h_besi])

    elif tipe_saluran == "Beton Siklop":
        show_bek = st.checkbox("Bekisting Saluran Siklop", value=True, key="1_cb_bek")
        h_bek = st.number_input("AHSP Bekisting (Rp/m²)", value=125000, key="1_h_bek") if show_bek else 0
        show_cor = st.checkbox("Cor Beton Siklop (60% Beton : 40% Batu)", value=True, key="1_cb_cor")
        h_cor = st.number_input("AHSP Cor Siklop (Rp/m³)", value=1050000, key="1_h_cor") if show_cor else 0

        if show_bek: item_to_add.append(["Bekisting Permukaan Saluran Siklop", luas_plester_bekisting, "m²", h_bek])
        if show_cor: item_to_add.append(["Cor Beton Siklop Saluran", vol_total, "m³", h_cor])

    # Plot Saluran Terpisah
    fig, ax = plt.subplots(figsize=(6, 4))
    x_kiri = -l_bawah/2
    x_kanan = l_bawah/2
    dx_atas = (l_atas - l_bawah)/2

    col_kiri = 'saddlebrown' if c_kiri else '#e0e0e0'
    col_kanan = 'saddlebrown' if c_kanan else '#e0e0e0'
    col_lantai = 'saddlebrown' if c_lantai else '#e0e0e0'

    # Dinding Kiri
    pts_kiri = [[x_kiri, 0], [x_kiri - t_bawah, 0], [x_kiri - dx_atas - t_atas, tinggi], [x_kiri - dx_atas, tinggi]]
    ax.add_patch(plt.Polygon(pts_kiri, color=col_kiri, ec='black', alpha=0.8))
    # Dinding Kanan
    pts_kanan = [[x_kanan, 0], [x_kanan + t_bawah, 0], [x_kanan + dx_atas + t_atas, tinggi], [x_kanan + dx_atas, tinggi]]
    ax.add_patch(plt.Polygon(pts_kanan, color=col_kanan, ec='black', alpha=0.8))
    # Lantai
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
        show_grading = st.checkbox("Penyiapan Badan Jalan", value=True, key="2_cb_grad")
        h_grading = st.number_input("AHSP Penyiapan (Rp/m²)", value=12000, key="2_h_grad") if show_grading else 0
        show_base = st.checkbox("Lapis Pondasi Agregat A", value=True, key="2_cb_base")
        h_base = st.number_input("AHSP Agregat A (Rp/m³)", value=450000, key="2_h_base") if show_base else 0
        if show_grading: item_to_add.append(["Penyiapan Badan Jalan", lebar * panjang, "m²", h_grading])
        if show_base: item_to_add.append(["Lapis Pondasi Agregat A", lebar * panjang * t_base, "m³", h_base])
    else:
        p_bongkar = st.slider("Persen Area Dikupas (%)", 0, 100, 100, key="2_sl_bongk")
        show_milling = st.checkbox("Cold Milling (Kupas Aspal)", value=True, key="2_cb_mill")
        h_milling = st.number_input("AHSP Milling (Rp/m³)", value=350000, key="2_h_mill") if show_milling else 0
        show_tack = st.checkbox("Lapis Perekat (Tack Coat)", value=True, key="2_cb_tack")
        h_tack = st.number_input("AHSP Tack Coat (Rp/Liter)", value=15000, key="2_h_tack") if show_tack else 0
        if show_milling: item_to_add.append([f"Cold Milling Kupas Aspal ({p_bongkar}%)", (lebar * panjang * t_aspal) * (p_bongkar/100), "m³", h_milling])
        if show_tack: item_to_add.append(["Lapis Perekat (Tack Coat)", lebar * panjang * 0.35, "Liter", h_tack])

    show_aspal = st.checkbox("Aspal Hotmix AC-WC", value=True, key="2_cb_asp")
    h_aspal = st.number_input("AHSP Aspal (Rp/m³)", value=2500000, key="2_h_asp") if show_aspal else 0
    if show_aspal: item_to_add.append(["Aspal Hotmix AC-WC", lebar * panjang * t_aspal, "m³", h_aspal])

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
        show_grading = st.checkbox("Penyiapan Badan Jalan", value=True, key="3_cb_grad")
        h_grading = st.number_input("AHSP Penyiapan (Rp/m²)", value=12000, key="3_h_grad") if show_grading else 0
        if show_grading: item_to_add.append(["Penyiapan Badan Jalan", lebar * panjang, "m²", h_grading])
    else:
        p_bongkar = st.slider("Persen Bongkaran (%)", 0, 100, 100, key="3_sl_bongk")
        show_bongkar = st.checkbox("Bongkaran Rigid Eksisting", value=True, key="3_cb_bongk")
        h_bongkar = st.number_input("AHSP Bongkaran Rigid (Rp/m³)", value=450000, key="3_h_bongk") if show_bongkar else 0
        if show_bongkar: item_to_add.append([f"Bongkaran Rigid Eksisting ({p_bongkar}%)", (lebar * panjang * t_rigid) * (p_bongkar/100), "m³", h_bongkar])

    show_lc = st.checkbox("Lantai Kerja (LC)", value=True, key="3_cb_lc")
    h_lc = st.number_input("AHSP Lantai Kerja (Rp/m³)", value=950000, key="3_h_lc") if show_lc else 0
    show_bekisting = st.checkbox("Bekisting Sisi Jalan", value=True, key="3_cb_bek")
    h_bekisting = st.number_input("AHSP Bekisting (Rp/m²)", value=125000, key="3_h_bek") if show_bekisting else 0
    show_rigid = st.checkbox("Beton Rigid K-350", value=True, key="3_cb_rig")
    h_rigid = st.number_input("AHSP Beton Rigid (Rp/m³)", value=1450000, key="3_h_rig") if show_rigid else 0
    show_besi = st.checkbox("Pembesian (Dowel/Wiremesh)", value=True, key="3_cb_besi")
    r_besi = st.number_input("Rasio Besi (kg/m³)", value=60, key="3_r_besi") if show_besi else 0
    h_besi = st.number_input("AHSP Besi (Rp/kg)", value=18500, key="3_h_besi") if show_besi else 0

    if show_lc: item_to_add.append(["Lantai Kerja (LC)", lebar * panjang * t_lc, "m³", h_lc])
    if show_bekisting: item_to_add.append(["Bekisting Sisi Jalan", (t_rigid + t_lc) * panjang * 2, "m²", h_bekisting])
    if show_rigid: item_to_add.append(["Beton Rigid K-350", lebar * panjang * t_rigid, "m³", h_rigid])
    if show_besi: item_to_add.append(["Pembesian (Dowel/Wiremesh)", (lebar * panjang * t_rigid) * r_besi, "kg", h_besi])

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
        show_bongkar = st.checkbox("Bongkaran Struktur Lama", value=True, key="4_cb_bongk")
        h_bongkar = st.number_input("AHSP Bongkaran (Rp/m³)", value=350000, key="4_h_bongk") if show_bongkar else 0
        if show_bongkar: item_to_add.append([f"Bongkaran Struktur Lama ({p_bongkar}%)", vol_beton * (p_bongkar/100), "m³", h_bongkar])

    show_galian = st.checkbox("Galian Tanah Pondasi", value=True, key="4_cb_gal")
    h_galian = st.number_input("AHSP Galian (Rp/m³)", value=75000, key="4_h_gal") if show_galian else 0
    show_lc = st.checkbox("Lantai Kerja Pondasi", value=True, key="4_cb_lc")
    h_lc = st.number_input("AHSP Lantai Kerja (Rp/m³)", value=950000, key="4_h_lc") if show_lc else 0
    show_bekisting = st.checkbox("Bekisting Plat Pondasi", value=True, key="4_cb_bek")
    h_bekisting = st.number_input("AHSP Bekisting (Rp/m²)", value=145000, key="4_h_bek") if show_bekisting else 0
    show_cor = st.checkbox("Beton Plat Pondasi", value=True, key="4_cb_cor")
    h_cor = st.number_input("AHSP Beton (Rp/m³)", value=4500000, key="4_h_cor") if show_cor else 0
    show_besi = st.checkbox("Pembesian Pondasi", value=True, key="4_cb_besi")
    r_besi = st.number_input("Rasio Besi (kg/m³)", value=150, key="4_r_besi") if show_besi else 0
    h_besi = st.number_input("AHSP Besi (Rp/kg)", value=18500, key="4_h_besi") if show_besi else 0

    if show_galian: item_to_add.append(["Galian Tanah Pondasi", (p+0.4)*(l+0.4)*t*jml, "m³", h_galian])
    if show_lc: item_to_add.append(["Lantai Kerja Pondasi", p*l*0.05*jml, "m³", h_lc])
    if show_bekisting: item_to_add.append(["Bekisting Plat Pondasi", (p+l)*2*t*jml, "m²", h_bekisting])
    if show_cor: item_to_add.append(["Beton Plat Pondasi", vol_beton, "m³", h_cor])
    if show_besi: item_to_add.append(["Pembesian Pondasi", vol_beton * r_besi, "kg", h_besi])

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
        h = st.number_input("Tinggi Dinding (m)", value=4.0, key="5_h")
        l_atas = st.number_input("Lebar Atas (m)", value=0.4, key="5_g_la")
        l_bawah = st.number_input("Lebar Bawah (m)", value=1.5, key="5_g_lb")
        
        vol_material = ((l_atas + l_bawah) / 2) * h * panjang
        sisi_miring = np.sqrt(h**2 + (l_bawah - l_atas)**2)
        luas_sisi_luar = sisi_miring * panjang
        vol_galian = l_bawah * h * panjang
        
        st.markdown("**Pekerjaan & AHSP**")
        if mode_proyek != "Bangunan Baru":
            p_bongkar = st.slider("Persen Bongkaran (%)", 0, 100, 100, key="5_g_sl_bongk")
            show_bongkar = st.checkbox("Bongkaran Struktur Lama", value=True, key="5_g_cb_bongk")
            h_bongkar = st.number_input("AHSP Bongkaran (Rp/m³)", value=350000 if is_siklop else 150000, key="5_g_h_bongk") if show_bongkar else 0
            if show_bongkar: item_to_add.append([f"Bongkaran DPT Eksisting ({p_bongkar}%)", vol_material * (p_bongkar/100), "m³", h_bongkar])

        show_galian = st.checkbox("Galian Tanah Tebing", value=True, key="5_g_cb_gal")
        h_galian = st.number_input("AHSP Galian (Rp/m³)", value=75000, key="5_g_h_gal") if show_galian else 0
        
        if not is_siklop:
            show_mat = st.checkbox("Pasangan Batu Kali (1:4)", value=True, key="5_g_cb_mat")
            h_mat = st.number_input("AHSP Pasangan Batu (Rp/m³)", value=950000, key="5_g_h_mat") if show_mat else 0
            show_plester = st.checkbox("Plesteran & Siaran DPT", value=True, key="5_g_cb_ples")
            h_plester = st.number_input("AHSP Plesteran (Rp/m²)", value=65000, key="5_g_h_ples") if show_plester else 0
            
            if show_galian: item_to_add.append(["Galian Tanah Tebing", vol_galian, "m³", h_galian])
            if show_mat: item_to_add.append(["Pasangan Batu Kali (1:4)", vol_material, "m³", h_mat])
            if show_plester: item_to_add.append(["Plesteran & Siaran Permukaan", luas_sisi_luar, "m²", h_plester])
        else:
            show_bekisting = st.checkbox("Bekisting DPT Siklop", value=True, key="5_g_cb_bek")
            h_bekisting = st.number_input("AHSP Bekisting (Rp/m²)", value=125000, key="5_g_h_bek") if show_bekisting else 0
            show_mat = st.checkbox("Cor Beton Siklop", value=True, key="5_g_cb_mat")
            h_mat = st.number_input("AHSP Beton Siklop (Rp/m³)", value=1050000, key="5_g_h_mat") if show_mat else 0
            
            if show_galian: item_to_add.append(["Galian Tanah Tebing", vol_galian, "m³", h_galian])
            if show_bekisting: item_to_add.append(["Bekisting Permukaan DPT Siklop", luas_sisi_luar, "m²", h_bekisting])
            if show_mat: item_to_add.append(["Cor Beton Siklop DPT", vol_material, "m³", h_mat])

        show_suling = st.checkbox("Pipa Suling-Suling PVC 2\" + Ijuk", value=True, key="5_g_cb_suling")
        h_suling = st.number_input("AHSP Suling-suling (Rp/Titik)", value=45000, key="5_g_h_suling") if show_suling else 0
        if show_suling: item_to_add.append(["Instalasi Pipa Suling PVC 2\" + Ijuk", (luas_sisi_luar/2), "Titik", h_suling])

        fig, ax = plt.subplots(figsize=(5, 4))
        ax.add_patch(plt.Polygon([[0, 0], [l_bawah, 0], [l_atas, h], [0, h]], color='#8b9ea8' if is_siklop else 'slategray', alpha=0.9))
        ax.plot([0, 0], [0, h], color='saddlebrown', lw=4, label='Tebing/Tanah')
        
        ax.text(l_bawah/2, 0.1, f'{l_bawah}m', ha='center', va='bottom', fontsize=9, color='white')
        ax.text(l_atas/2, h - 0.3, f'{l_atas}m', ha='center', va='top', fontsize=9, color='white')
        
        ax.set_xlim(-0.5, max(l_bawah, l_atas) + 0.5); ax.set_ylim(-0.5, h+0.5); ax.set_aspect('equal')
        ax.set_xlabel("Lebar Struktur (m)"); ax.set_ylabel("Tinggi Total (m)")
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
            show_bongkar = st.checkbox("Bongkaran DPT Lama", value=True, key="5_ter_cb_bongk")
            h_bongkar = st.number_input("AHSP Bongkaran (Rp/m³)", value=350000 if is_siklop else 150000, key="5_ter_h_bongk") if show_bongkar else 0
            if show_bongkar: item_to_add.append([f"Bongkaran DPT Eksisting ({p_bongkar}%)", vol_total_mat * (p_bongkar/100), "m³", h_bongkar])

        show_galian = st.checkbox("Galian Tanah Tebing", value=True, key="5_ter_cb_gal")
        h_galian = st.number_input("AHSP Galian (Rp/m³)", value=75000, key="5_ter_h_gal") if show_galian else 0
        
        if not is_siklop:
            show_mat = st.checkbox("Pasangan Batu Kali (1:4)", value=True, key="5_ter_cb_mat")
            h_mat = st.number_input("AHSP Pasangan Batu (Rp/m³)", value=950000, key="5_ter_h_mat") if show_mat else 0
            show_plester = st.checkbox("Plesteran & Siaran DPT", value=True, key="5_ter_cb_ples")
            h_plester = st.number_input("AHSP Plesteran (Rp/m²)", value=65000, key="5_ter_h_ples") if show_plester else 0
            
            if show_galian: item_to_add.append(["Galian Tanah Tebing (Terasering)", vol_galian, "m³", h_galian])
            if show_mat: item_to_add.append(["Pasangan Batu Kali (Terasering)", vol_total_mat, "m³", h_mat])
            if show_plester: item_to_add.append(["Plesteran & Siaran Permukaan (Termasuk Berm)", luas_sisi_luar, "m²", h_plester])
        else:
            show_bekisting = st.checkbox("Bekisting Terasering Siklop", value=True, key="5_ter_cb_bek")
            h_bekisting = st.number_input("AHSP Bekisting (Rp/m²)", value=125000, key="5_ter_h_bek") if show_bekisting else 0
            show_mat = st.checkbox("Cor Beton Siklop Terasering", value=True, key="5_ter_cb_mat")
            h_mat = st.number_input("AHSP Beton Siklop (Rp/m³)", value=1050000, key="5_ter_h_mat") if show_mat else 0

            if show_galian: item_to_add.append(["Galian Tanah Tebing (Terasering)", vol_galian, "m³", h_galian])
            if show_bekisting: item_to_add.append(["Bekisting Permukaan Siklop Terasering (Sisi Miring & Berm)", luas_sisi_luar, "m²", h_bekisting])
            if show_mat: item_to_add.append(["Cor Beton Siklop Terasering", vol_total_mat, "m³", h_mat])

        show_suling = st.checkbox("Pipa Suling-Suling PVC 2\" + Ijuk", value=True, key="5_ter_cb_suling")
        h_suling = st.number_input("AHSP Suling-suling (Rp/Titik)", value=45000, key="5_ter_h_suling") if show_suling else 0
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
        h = st.number_input("Tinggi Dinding (m)", value=4.0, key="5_c_h")
        l_base = st.number_input("Lebar Base/Lantai (m)", value=2.5, key="5_c_lb")
        vol_beton = ((0.4 * h) + (l_base * 0.4)) * panjang
        vol_galian = l_base * 1.5 * panjang

        st.markdown("**Pekerjaan & AHSP**")
        if mode_proyek != "Bangunan Baru":
            p_bongkar = st.slider("Persen Bongkaran (%)", 0, 100, 100, key="5_c_sl_bongk")
            show_bongkar = st.checkbox("Bongkaran DPT Beton Lama", value=True, key="5_c_cb_bongk")
            h_bongkar = st.number_input("AHSP Bongkaran (Rp/m³)", value=350000, key="5_c_h_bongk") if show_bongkar else 0
            if show_bongkar: item_to_add.append([f"Bongkaran DPT Eksisting ({p_bongkar}%)", vol_beton * (p_bongkar/100), "m³", h_bongkar])

        show_galian = st.checkbox("Galian Struktur Tebing", value=True, key="5_c_cb_gal")
        h_galian = st.number_input("AHSP Galian (Rp/m³)", value=75000, key="5_c_h_gal") if show_galian else 0
        show_bekisting = st.checkbox("Bekisting DPT", value=True, key="5_c_cb_bek")
        h_bekisting = st.number_input("AHSP Bekisting (Rp/m²)", value=145000, key="5_c_h_bek") if show_bekisting else 0
        show_cor = st.checkbox("Pengecoran Beton DPT", value=True, key="5_c_cb_cor")
        h_cor = st.number_input("AHSP Beton (Rp/m³)", value=4200000, key="5_c_h_cor") if show_cor else 0
        show_besi = st.checkbox("Pembesian Struktur DPT", value=True, key="5_c_cb_besi")
        r_besi = st.number_input("Rasio Besi (kg/m³)", value=125, key="5_c_r_besi") if show_besi else 0
        h_besi = st.number_input("AHSP Besi (Rp/kg)", value=18500, key="5_c_h_besi") if show_besi else 0
        show_timbunan = st.checkbox("Timbunan Tanah Kembali (Backfill)", value=True, key="5_c_cb_timb")
        h_timbunan = st.number_input("AHSP Timbunan (Rp/m³)", value=115000, key="5_c_h_timb") if show_timbunan else 0

        if show_galian: item_to_add.append(["Galian Struktur Tebing", vol_galian, "m³", h_galian])
        if show_bekisting: item_to_add.append(["Bekisting DPT", (h*2*panjang) + (0.4*2*panjang), "m²", h_bekisting])
        if show_cor: item_to_add.append(["Pengecoran Beton DPT", vol_beton, "m³", h_cor])
        if show_besi: item_to_add.append(["Pembesian Struktur DPT", vol_beton * r_besi, "kg", h_besi])
        if show_timbunan: item_to_add.append(["Timbunan Tanah Kembali (Backfill)", (l_base/2) * h * panjang, "m³", h_timbunan])

        show_suling = st.checkbox("Pipa Suling-Suling PVC 2\" + Ijuk", value=True, key="5_c_cb_suling")
        h_suling = st.number_input("AHSP Suling-suling (Rp/Titik)", value=45000, key="5_c_h_suling") if show_suling else 0
        if show_suling: item_to_add.append(["Instalasi Pipa Suling PVC 2\" + Ijuk", ((h*panjang)/2), "Titik", h_suling])

        fig, ax = plt.subplots(figsize=(5, 4))
        ax.add_patch(plt.Rectangle((0, -0.4), l_base, 0.4, color='darkgray'))
        ax.add_patch(plt.Rectangle((0.5, 0), 0.4, h, color='darkgray'))
        ax.add_patch(plt.Rectangle((0.9, 0), l_base-0.9, h, color='saddlebrown', alpha=0.3, label='Timbunan Tebing'))
        
        ax.text(l_base/2, -0.2, f'{l_base}m', ha='center', va='center', fontsize=9, color='white')
        ax.text(0.7, h/2, f'{h}m', ha='center', va='center', fontsize=9, color='white', rotation=90)
        
        ax.set_xlim(-0.5, l_base+0.5); ax.set_ylim(-1, h+1); ax.set_aspect('equal')
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
        show_bongkar = st.checkbox("Pembersihan Lokasi/Bongkar Kepala", value=True, key="6_cb_bongk")
        h_bongkar = st.number_input("AHSP Pembersihan (Rp/Titik)", value=500000, key="6_h_bongk") if show_bongkar else 0
        if show_bongkar: item_to_add.append([f"Pembersihan Lokasi/Bongkar Kepala ({p_bongkar}%)", jml_titik * (p_bongkar/100), "Titik", h_bongkar])

    show_bor = st.checkbox("Pengeboran Bore Pile", value=True, key="6_cb_bor")
    h_bor = st.number_input("AHSP Pengeboran (Rp/m³)", value=450000, key="6_h_bor") if show_bor else 0
    show_casing = st.checkbox("Instalasi Temporary Casing", value=True, key="6_cb_cas")
    h_casing = st.number_input("AHSP Casing (Rp/m')", value=150000, key="6_h_cas") if show_casing else 0
    show_cor = st.checkbox("Pengecoran Beton K-350", value=True, key="6_cb_cor")
    h_cor = st.number_input("AHSP Beton (Rp/m³)", value=1350000, key="6_h_cor") if show_cor else 0
    show_besi = st.checkbox("Pembesian Tulangan", value=True, key="6_cb_besi")
    r_besi = st.number_input("Rasio Besi (kg/m³)", value=180, key="6_r_besi") if show_besi else 0
    h_besi = st.number_input("AHSP Besi (Rp/kg)", value=18500, key="6_h_besi") if show_besi else 0

    if show_bor: item_to_add.append(["Pengeboran Bore Pile", vol_pengeboran, "m³", h_bor])
    if show_casing: item_to_add.append(["Instalasi Temporary Casing", diameter * 2 * jml_titik, "m'", h_casing])
    if show_cor: item_to_add.append(["Pengecoran Beton K-350 (Bore Pile)", vol_total_beton, "m³", h_cor])
    if show_besi: item_to_add.append(["Pembesian Tulangan Bore Pile", vol_total_beton * r_besi, "kg", h_besi])

    fig, ax = plt.subplots(figsize=(5, 4))
    ax.add_patch(plt.Rectangle((-1, -kedalaman), 2, kedalaman, color='saddlebrown', alpha=0.1))
    ax.add_patch(plt.Rectangle((-diameter/2, -kedalaman), diameter, kedalaman, color='gray'))
    ax.set_xlim(-1, 1); ax.set_ylim(-kedalaman-1, 1); ax.set_aspect('equal')
    ax.set_xlabel("Lebar Galian/Diameter (m)"); ax.set_ylabel("Kedalaman (m)")
    ax.grid(True, linestyle='--', alpha=0.6)

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

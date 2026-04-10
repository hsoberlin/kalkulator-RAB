import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.subplots as plt
import io
import json # Modul baru untuk menyimpan dan membuka Draft

# Konfigurasi Portrait untuk HP
st.set_page_config(page_title="Estimator RAB Konstruksi", layout="centered")

if 'rekap_proyek' not in st.session_state:
    st.session_state.rekap_proyek = []

st.title("Aplikasi Estimator Rencana Anggaran Biaya")
st.write("Sistem perhitungan teknis volume dan biaya konstruksi terpadu **by Pemeliharaan Sipil SGL**.")

# --- SIDEBAR MENU UTAMA ---
st.sidebar.title("Navigasi Proyek")
jenis_bangunan = st.sidebar.selectbox(
    "Pilih Jenis Pekerjaan:",
    [
        "0. Pekerjaan Persiapan",
        "1. Saluran Trapesium (Beton)", 
        "2. Saluran Pasangan Batu (Drainase)",
        "3. Jalan Perkerasan Lentur (Aspal)", 
        "4. Jalan Perkerasan Kaku (Rigid)",
        "5. Pondasi Telapak",
        "6. Dinding Penahan Tanah (Kantilever)",
        "7. Pondasi Bore Pile"
    ],
    key="navigasi_utama"
)

st.sidebar.divider()

# --- KONDISI LAHAN ---
st.sidebar.title("Kondisi Lahan Awal")
mode_proyek = st.sidebar.radio(
    "Metode Pelaksanaan:", 
    ["Bangunan Baru", "Rehabilitasi Struktur"],
    key="mode_global"
)

st.sidebar.divider()

# --- PENGATURAN KEUANGAN ---
st.sidebar.title("Pengaturan Keuangan")
overhead_pct = st.sidebar.number_input("Overhead & Profit (%)", value=10.0, step=1.0, key="global_oh")
ppn_pct = st.sidebar.number_input("PPN / Pajak (%)", value=11.0, step=1.0, key="global_ppn")

st.sidebar.divider()

item_to_add = []
kategori_pekerjaan = jenis_bangunan 

# =====================================================================
# 0. PEKERJAAN PERSIAPAN
# =====================================================================
if jenis_bangunan == "0. Pekerjaan Persiapan":
    st.sidebar.header("Item Persiapan (Lump Sum)")
    
    show_survey = st.sidebar.checkbox("Survey, Pengukuran & Pasang Bowplank", value=True, key="0_cb_surv")
    h_survey = st.sidebar.number_input("Biaya Survey (Rp)", value=5000000, key="0_h_surv") if show_survey else 0

    show_k3 = st.sidebar.checkbox("Penyelenggaraan SMK3 (K3 Konstruksi)", value=True, key="0_cb_k3")
    h_k3 = st.sidebar.number_input("Biaya K3 (Rp)", value=3500000, key="0_h_k3") if show_k3 else 0

    show_mob = st.sidebar.checkbox("Mobilisasi & Demobilisasi Alat Berat", value=True, key="0_cb_mob")
    h_mob = st.sidebar.number_input("Biaya Mob-Demob (Rp)", value=12000000, key="0_h_mob") if show_mob else 0

    show_direksi = st.sidebar.checkbox("Sewa/Pembuatan Direksi Keet", value=True, key="0_cb_dir")
    h_direksi = st.sidebar.number_input("Biaya Direksi Keet (Rp)", value=7500000, key="0_h_dir") if show_direksi else 0

    if show_survey: item_to_add.append(["Survey, Pengukuran & Bowplank", 1.0, "LS", h_survey])
    if show_k3: item_to_add.append(["Penyelenggaraan SMK3", 1.0, "LS", h_k3])
    if show_mob: item_to_add.append(["Mobilisasi & Demobilisasi", 1.0, "LS", h_mob])
    if show_direksi: item_to_add.append(["Fasilitas Proyek/Direksi Keet", 1.0, "LS", h_direksi])

    fig, ax = plt.subplots()
    ax.text(0.5, 0.5, 'Pekerjaan Persiapan & Umum\n(Non-Struktural)', horizontalalignment='center', verticalalignment='center', fontsize=14, fontweight='bold', color='gray')
    ax.set_axis_off()

# =====================================================================
# 1. SALURAN TRAPESIUM (BETON)
# =====================================================================
elif jenis_bangunan == "1. Saluran Trapesium (Beton)":
    st.sidebar.header("Dimensi Saluran")
    l_atas = st.sidebar.number_input("Lebar Dalam Atas (m)", value=1.2, key="1_la")
    l_bawah = st.sidebar.number_input("Lebar Dalam Bawah (m)", value=0.8, key="1_lb")
    tinggi = st.sidebar.number_input("Tinggi Saluran (m)", value=5.0, key="1_t")
    panjang = st.sidebar.number_input("Panjang Saluran (m)", value=100.0, key="1_p")
    t_atas = st.sidebar.number_input("Tebal Atas (m)", value=0.15, key="1_ta")
    t_bawah = st.sidebar.number_input("Tebal Bawah (m)", value=0.25, key="1_tb")
    t_dasar = st.sidebar.number_input("Tebal Dasar (m)", value=0.30, key="1_td")

    dist = (l_atas - l_bawah) / 2
    s_miring = np.sqrt(dist**2 + tinggi**2)
    vol_beton = (((t_atas + t_bawah) / 2 * s_miring * 2) + (l_bawah * t_dasar)) * panjang
    vol_tanah = (((l_atas+(2*t_atas) + l_bawah+(2*t_bawah))/2) * (tinggi+t_dasar)) * panjang
    vol_rongga = (((l_atas + l_bawah) / 2) * tinggi) * panjang

    st.sidebar.header("Pekerjaan & AHSP")
    if mode_proyek == "Bangunan Baru":
        show_galian = st.sidebar.checkbox("Galian Tanah Profil", value=True, key="1_cb_gal")
        h_galian = st.sidebar.number_input("AHSP Galian (Rp/m³)", value=75000, key="1_h_gal") if show_galian else 0
        if show_galian: item_to_add.append(["Galian Tanah Profil Baru", vol_tanah, "m³", h_galian])
    else:
        p_bongkar = st.sidebar.slider("Persen Bongkaran (%)", 0, 100, 100, key="1_sl_bongk")
        p_sedimen = st.sidebar.slider("Persen Sedimen (%)", 0, 100, 30, key="1_sl_sed")
        show_bongkar = st.sidebar.checkbox("Bongkaran Beton Eksisting", value=True, key="1_cb_bongk")
        h_bongkar = st.sidebar.number_input("AHSP Bongkaran (Rp/m³)", value=250000, key="1_h_bongk") if show_bongkar else 0
        show_sedimen = st.sidebar.checkbox("Galian Sedimen Saluran", value=True, key="1_cb_sed")
        h_sedimen = st.sidebar.number_input("AHSP Galian Sedimen (Rp/m³)", value=85000, key="1_h_sed") if show_sedimen else 0
        if show_bongkar: item_to_add.append([f"Bongkaran Beton ({p_bongkar}%)", vol_beton*(p_bongkar/100), "m³", h_bongkar])
        if show_sedimen: item_to_add.append(["Galian Sedimen/Lumpur", vol_rongga*(p_sedimen/100), "m³", h_sedimen])

    show_bekisting = st.sidebar.checkbox("Bekisting Dinding Saluran", value=True, key="1_cb_bek")
    h_bekisting = st.sidebar.number_input("AHSP Bekisting (Rp/m²)", value=125000, key="1_h_bek") if show_bekisting else 0
    show_cor = st.sidebar.checkbox("Pengecoran Beton Saluran", value=True, key="1_cb_cor")
    h_cor = st.sidebar.number_input("AHSP Cor Beton (Rp/m³)", value=1200000, key="1_h_cor") if show_cor else 0
    show_besi = st.sidebar.checkbox("Pembesian Saluran", value=True, key="1_cb_besi")
    r_besi = st.sidebar.number_input("Rasio Besi (kg/m³)", value=110, key="1_r_besi") if show_besi else 0
    h_besi = st.sidebar.number_input("AHSP Besi (Rp/kg)", value=18500, key="1_h_besi") if show_besi else 0

    if show_bekisting: item_to_add.append(["Bekisting Dinding Saluran", (s_miring * 2) * panjang, "m²", h_bekisting])
    if show_cor: item_to_add.append(["Beton Struktur Saluran", vol_beton, "m³", h_cor])
    if show_besi: item_to_add.append(["Pembesian Saluran", vol_beton * r_besi, "kg", h_besi])

    fig, ax = plt.subplots()
    ax.add_patch(plt.Rectangle((-2, -tinggi-1), 4, tinggi+2, color='saddlebrown', alpha=0.2))
    ax.plot([-l_atas/2, -l_bawah/2, l_bawah/2, l_atas/2], [0, -tinggi, -tinggi, 0], color='black', lw=2)
    ax.set_aspect('equal')

# =====================================================================
# 2. SALURAN PASANGAN BATU
# =====================================================================
elif jenis_bangunan == "2. Saluran Pasangan Batu (Drainase)":
    st.sidebar.header("Dimensi Drainase")
    l_atas = st.sidebar.number_input("Lebar Atas (m)", value=1.0, key="2_la")
    l_bawah = st.sidebar.number_input("Lebar Bawah (m)", value=0.6, key="2_lb")
    tinggi = st.sidebar.number_input("Tinggi (m)", value=1.2, key="2_t")
    tebal = st.sidebar.number_input("Tebal Batu (m)", value=0.25, key="2_tb")
    panjang = st.sidebar.number_input("Panjang (m)", value=100.0, key="2_p")

    dist = (l_atas - l_bawah) / 2
    keliling = (2 * np.sqrt(dist**2 + tinggi**2)) + l_bawah
    vol_batu = keliling * tebal * panjang

    st.sidebar.header("Pekerjaan & AHSP")
    if mode_proyek == "Bangunan Baru":
        vol_galian = (((l_atas+(2*tebal)) + (l_bawah+(2*tebal)))/2 * (tinggi+tebal)) * panjang
        show_galian = st.sidebar.checkbox("Galian Tanah Drainase", value=True, key="2_cb_gal")
        h_galian = st.sidebar.number_input("AHSP Galian (Rp/m³)", value=75000, key="2_h_gal") if show_galian else 0
        if show_galian: item_to_add.append(["Galian Tanah Drainase", vol_galian, "m³", h_galian])
    else:
        p_bongkar = st.sidebar.slider("Persen Bongkaran (%)", 0, 100, 100, key="2_sl_bongk")
        show_bongkar = st.sidebar.checkbox("Bongkaran Batu Eksisting", value=True, key="2_cb_bongk")
        h_bongkar = st.sidebar.number_input("AHSP Bongkaran (Rp/m³)", value=150000, key="2_h_bongk") if show_bongkar else 0
        if show_bongkar: item_to_add.append([f"Bongkaran Batu Eksisting ({p_bongkar}%)", vol_batu * (p_bongkar/100), "m³", h_bongkar])

    show_pasangan = st.sidebar.checkbox("Pasangan Batu Kali (1:4)", value=True, key="2_cb_pas")
    h_pasangan = st.sidebar.number_input("AHSP Pasangan Batu (Rp/m³)", value=950000, key="2_h_pas") if show_pasangan else 0
    show_plester = st.sidebar.checkbox("Plesteran + Acian", value=True, key="2_cb_ples")
    h_plester = st.sidebar.number_input("AHSP Plesteran (Rp/m²)", value=65000, key="2_h_ples") if show_plester else 0

    if show_pasangan: item_to_add.append(["Pasangan Batu Kali (1:4)", vol_batu, "m³", h_pasangan])
    if show_plester: item_to_add.append(["Plesteran + Acian", keliling * panjang, "m²", h_plester])

    fig, ax = plt.subplots()
    ax.plot([0, dist, dist+l_bawah, l_atas], [0, -tinggi, -tinggi, 0], color='black', lw=3)
    ax.set_aspect('equal')

# =====================================================================
# 3. JALAN PERKERASAN LENTUR (ASPAL)
# =====================================================================
elif jenis_bangunan == "3. Jalan Perkerasan Lentur (Aspal)":
    st.sidebar.header("Dimensi Jalan")
    lebar = st.sidebar.number_input("Lebar (m)", value=6.0, key="3_l")
    panjang = st.sidebar.number_input("Panjang (m)", value=1000.0, key="3_p")
    t_aspal = st.sidebar.number_input("Tebal Aspal (m)", value=0.05, key="3_tasp")
    t_base = st.sidebar.number_input("Tebal Agregat (m)", value=0.15, key="3_tbase")

    st.sidebar.header("Pekerjaan & AHSP")
    if mode_proyek == "Bangunan Baru":
        show_grading = st.sidebar.checkbox("Penyiapan Badan Jalan", value=True, key="3_cb_grad")
        h_grading = st.sidebar.number_input("AHSP Penyiapan (Rp/m²)", value=12000, key="3_h_grad") if show_grading else 0
        show_base = st.sidebar.checkbox("Lapis Pondasi Agregat A", value=True, key="3_cb_base")
        h_base = st.sidebar.number_input("AHSP Agregat A (Rp/m³)", value=450000, key="3_h_base") if show_base else 0
        if show_grading: item_to_add.append(["Penyiapan Badan Jalan", lebar * panjang, "m²", h_grading])
        if show_base: item_to_add.append(["Lapis Pondasi Agregat A", lebar * panjang * t_base, "m³", h_base])
    else:
        p_bongkar = st.sidebar.slider("Persen Area Dikupas (%)", 0, 100, 100, key="3_sl_bongk")
        show_milling = st.sidebar.checkbox("Cold Milling (Kupas Aspal)", value=True, key="3_cb_mill")
        h_milling = st.sidebar.number_input("AHSP Milling (Rp/m³)", value=350000, key="3_h_mill") if show_milling else 0
        show_tack = st.sidebar.checkbox("Lapis Perekat (Tack Coat)", value=True, key="3_cb_tack")
        h_tack = st.sidebar.number_input("AHSP Tack Coat (Rp/Liter)", value=15000, key="3_h_tack") if show_tack else 0
        if show_milling: item_to_add.append([f"Cold Milling Kupas Aspal ({p_bongkar}%)", (lebar * panjang * t_aspal) * (p_bongkar/100), "m³", h_milling])
        if show_tack: item_to_add.append(["Lapis Perekat (Tack Coat)", lebar * panjang * 0.35, "Liter", h_tack])

    show_aspal = st.sidebar.checkbox("Aspal Hotmix AC-WC", value=True, key="3_cb_asp")
    h_aspal = st.sidebar.number_input("AHSP Aspal (Rp/m³)", value=2500000, key="3_h_asp") if show_aspal else 0
    if show_aspal: item_to_add.append(["Aspal Hotmix AC-WC", lebar * panjang * t_aspal, "m³", h_aspal])

    fig, ax = plt.subplots()
    ax.add_patch(plt.Rectangle((0, -t_aspal), lebar, t_aspal, color='black'))
    ax.set_xlim(-1, lebar+1); ax.set_ylim(-0.2, 0.1); ax.set_aspect('equal')

# =====================================================================
# 4. JALAN PERKERASAN KAKU (RIGID)
# =====================================================================
elif jenis_bangunan == "4. Jalan Perkerasan Kaku (Rigid)":
    st.sidebar.header("Dimensi Rigid")
    lebar = st.sidebar.number_input("Lebar (m)", value=5.0, key="4_l")
    panjang = st.sidebar.number_input("Panjang (m)", value=500.0, key="4_p")
    t_rigid = st.sidebar.number_input("Tebal Rigid (m)", value=0.25, key="4_trig")
    t_lc = st.sidebar.number_input("Tebal Lantai Kerja (m)", value=0.10, key="4_tlc")

    st.sidebar.header("Pekerjaan & AHSP")
    if mode_proyek == "Bangunan Baru":
        show_grading = st.sidebar.checkbox("Penyiapan Badan Jalan", value=True, key="4_cb_grad")
        h_grading = st.sidebar.number_input("AHSP Penyiapan (Rp/m²)", value=12000, key="4_h_grad") if show_grading else 0
        if show_grading: item_to_add.append(["Penyiapan Badan Jalan", lebar * panjang, "m²", h_grading])
    else:
        p_bongkar = st.sidebar.slider("Persen Bongkaran (%)", 0, 100, 100, key="4_sl_bongk")
        show_bongkar = st.sidebar.checkbox("Bongkaran Rigid Eksisting", value=True, key="4_cb_bongk")
        h_bongkar = st.sidebar.number_input("AHSP Bongkaran Rigid (Rp/m³)", value=450000, key="4_h_bongk") if show_bongkar else 0
        if show_bongkar: item_to_add.append([f"Bongkaran Rigid Eksisting ({p_bongkar}%)", (lebar * panjang * t_rigid) * (p_bongkar/100), "m³", h_bongkar])

    show_lc = st.sidebar.checkbox("Lantai Kerja (LC)", value=True, key="4_cb_lc")
    h_lc = st.sidebar.number_input("AHSP Lantai Kerja (Rp/m³)", value=950000, key="4_h_lc") if show_lc else 0
    show_bekisting = st.sidebar.checkbox("Bekisting Sisi Jalan", value=True, key="4_cb_bek")
    h_bekisting = st.sidebar.number_input("AHSP Bekisting (Rp/m²)", value=125000, key="4_h_bek") if show_bekisting else 0
    show_rigid = st.sidebar.checkbox("Beton Rigid K-350", value=True, key="4_cb_rig")
    h_rigid = st.sidebar.number_input("AHSP Beton Rigid (Rp/m³)", value=1450000, key="4_h_rig") if show_rigid else 0
    show_besi = st.sidebar.checkbox("Pembesian (Dowel/Wiremesh)", value=True, key="4_cb_besi")
    r_besi = st.sidebar.number_input("Rasio Besi (kg/m³)", value=60, key="4_r_besi") if show_besi else 0
    h_besi = st.sidebar.number_input("AHSP Besi (Rp/kg)", value=18500, key="4_h_besi") if show_besi else 0

    if show_lc: item_to_add.append(["Lantai Kerja (LC)", lebar * panjang * t_lc, "m³", h_lc])
    if show_bekisting: item_to_add.append(["Bekisting Sisi Jalan", (t_rigid + t_lc) * panjang * 2, "m²", h_bekisting])
    if show_rigid: item_to_add.append(["Beton Rigid K-350", lebar * panjang * t_rigid, "m³", h_rigid])
    if show_besi: item_to_add.append(["Pembesian (Dowel/Wiremesh)", (lebar * panjang * t_rigid) * r_besi, "kg", h_besi])

    fig, ax = plt.subplots()
    ax.add_patch(plt.Rectangle((0, 0), lebar, t_rigid, color='gray', hatch='//'))
    ax.add_patch(plt.Rectangle((0, -t_lc), lebar, t_lc, color='orange', alpha=0.4))
    ax.set_xlim(-1, lebar+1); ax.set_ylim(-0.3, 0.4); ax.set_aspect('equal')

# =====================================================================
# 5. PONDASI TELAPAK
# =====================================================================
elif jenis_bangunan == "5. Pondasi Telapak":
    st.sidebar.header("Dimensi Pondasi")
    p = st.sidebar.number_input("Panjang Plat (m)", value=1.5, key="5_p")
    l = st.sidebar.number_input("Lebar Plat (m)", value=1.5, key="5_l")
    t = st.sidebar.number_input("Tebal Plat (m)", value=0.3, key="5_t")
    jml = st.sidebar.number_input("Jumlah Titik", value=10, key="5_jml")
    vol_beton = p * l * t * jml

    st.sidebar.header("Pekerjaan & AHSP")
    if mode_proyek != "Bangunan Baru":
        p_bongkar = st.sidebar.slider("Persen Bongkaran (%)", 0, 100, 100, key="5_sl_bongk")
        show_bongkar = st.sidebar.checkbox("Bongkaran Struktur Lama", value=True, key="5_cb_bongk")
        h_bongkar = st.sidebar.number_input("AHSP Bongkaran (Rp/m³)", value=350000, key="5_h_bongk") if show_bongkar else 0
        if show_bongkar: item_to_add.append([f"Bongkaran Struktur Lama ({p_bongkar}%)", vol_beton * (p_bongkar/100), "m³", h_bongkar])

    show_galian = st.sidebar.checkbox("Galian Tanah Pondasi", value=True, key="5_cb_gal")
    h_galian = st.sidebar.number_input("AHSP Galian (Rp/m³)", value=75000, key="5_h_gal") if show_galian else 0
    show_lc = st.sidebar.checkbox("Lantai Kerja Pondasi", value=True, key="5_cb_lc")
    h_lc = st.sidebar.number_input("AHSP Lantai Kerja (Rp/m³)", value=950000, key="5_h_lc") if show_lc else 0
    show_bekisting = st.sidebar.checkbox("Bekisting Plat Pondasi", value=True, key="5_cb_bek")
    h_bekisting = st.sidebar.number_input("AHSP Bekisting (Rp/m²)", value=145000, key="5_h_bek") if show_bekisting else 0
    show_cor = st.sidebar.checkbox("Beton Plat Pondasi", value=True, key="5_cb_cor")
    h_cor = st.sidebar.number_input("AHSP Beton (Rp/m³)", value=4500000, key="5_h_cor") if show_cor else 0
    show_besi = st.sidebar.checkbox("Pembesian Pondasi", value=True, key="5_cb_besi")
    r_besi = st.sidebar.number_input("Rasio Besi (kg/m³)", value=150, key="5_r_besi") if show_besi else 0
    h_besi = st.sidebar.number_input("AHSP Besi (Rp/kg)", value=18500, key="5_h_besi") if show_besi else 0

    if show_galian: item_to_add.append(["Galian Tanah Pondasi", (p+0.4)*(l+0.4)*t*jml, "m³", h_galian])
    if show_lc: item_to_add.append(["Lantai Kerja Pondasi", p*l*0.05*jml, "m³", h_lc])
    if show_bekisting: item_to_add.append(["Bekisting Plat Pondasi", (p+l)*2*t*jml, "m²", h_bekisting])
    if show_cor: item_to_add.append(["Beton Plat Pondasi", vol_beton, "m³", h_cor])
    if show_besi: item_to_add.append(["Pembesian Pondasi", vol_beton * r_besi, "kg", h_besi])

    fig, ax = plt.subplots()
    ax.add_patch(plt.Rectangle((-p/2, 0), p, t, color='gray'))
    ax.set_xlim(-1, 1); ax.set_ylim(-0.2, 0.5); ax.set_aspect('equal')

# =====================================================================
# 6. DINDING PENAHAN TANAH (DPT)
# =====================================================================
elif jenis_bangunan == "6. Dinding Penahan Tanah (Kantilever)":
    st.sidebar.header("Dimensi DPT")
    h = st.sidebar.number_input("Tinggi Dinding (m)", value=4.0, key="6_h")
    l_base = st.sidebar.number_input("Lebar Base (m)", value=2.5, key="6_lb")
    panjang = st.sidebar.number_input("Panjang DPT (m)", value=50.0, key="6_p")
    vol_beton = ((0.4 * h) + (l_base * 0.4)) * panjang

    st.sidebar.header("Pekerjaan & AHSP")
    if mode_proyek != "Bangunan Baru":
        p_bongkar = st.sidebar.slider("Persen Bongkaran (%)", 0, 100, 100, key="6_sl_bongk")
        show_bongkar = st.sidebar.checkbox("Bongkaran DPT Eksisting", value=True, key="6_cb_bongk")
        h_bongkar = st.sidebar.number_input("AHSP Bongkaran (Rp/m³)", value=350000, key="6_h_bongk") if show_bongkar else 0
        if show_bongkar: item_to_add.append([f"Bongkaran DPT Eksisting ({p_bongkar}%)", vol_beton * (p_bongkar/100), "m³", h_bongkar])

    show_galian = st.sidebar.checkbox("Galian Struktur DPT", value=True, key="6_cb_gal")
    h_galian = st.sidebar.number_input("AHSP Galian (Rp/m³)", value=75000, key="6_h_gal") if show_galian else 0
    show_bekisting = st.sidebar.checkbox("Bekisting DPT", value=True, key="6_cb_bek")
    h_bekisting = st.sidebar.number_input("AHSP Bekisting (Rp/m²)", value=145000, key="6_h_bek") if show_bekisting else 0
    show_cor = st.sidebar.checkbox("Pengecoran Beton DPT", value=True, key="6_cb_cor")
    h_cor = st.sidebar.number_input("AHSP Beton (Rp/m³)", value=4200000, key="6_h_cor") if show_cor else 0
    show_besi = st.sidebar.checkbox("Pembesian Struktur DPT", value=True, key="6_cb_besi")
    r_besi = st.sidebar.number_input("Rasio Besi (kg/m³)", value=125, key="6_r_besi") if show_besi else 0
    h_besi = st.sidebar.number_input("AHSP Besi (Rp/kg)", value=18500, key="6_h_besi") if show_besi else 0
    show_timbunan = st.sidebar.checkbox("Timbunan Tanah Kembali", value=True, key="6_cb_timb")
    h_timbunan = st.sidebar.number_input("AHSP Timbunan (Rp/m³)", value=115000, key="6_h_timb") if show_timbunan else 0

    if show_galian: item_to_add.append(["Galian Struktur DPT", l_base * 1.0 * panjang, "m³", h_galian])
    if show_bekisting: item_to_add.append(["Bekisting DPT", (h*2*panjang) + (0.4*2*panjang), "m²", h_bekisting])
    if show_cor: item_to_add.append(["Pengecoran Beton DPT", vol_beton, "m³", h_cor])
    if show_besi: item_to_add.append(["Pembesian Struktur DPT", vol_beton * r_besi, "kg", h_besi])
    if show_timbunan: item_to_add.append(["Timbunan Tanah Kembali", (l_base/2) * h * panjang, "m³", h_timbunan])

    fig, ax = plt.subplots()
    ax.add_patch(plt.Rectangle((0, -0.4), l_base, 0.4, color='gray'))
    ax.add_patch(plt.Rectangle((0.5, 0), 0.4, h, color='gray'))
    ax.set_xlim(-0.5, l_base+0.5); ax.set_ylim(-1, h+1); ax.set_aspect('equal')

# =====================================================================
# 7. PONDASI BORE PILE
# =====================================================================
elif jenis_bangunan == "7. Pondasi Bore Pile":
    st.sidebar.header("Dimensi Bore Pile")
    diameter = st.sidebar.number_input("Diameter Pile (m)", value=0.6, key="7_d")
    kedalaman = st.sidebar.number_input("Kedalaman Pile (m)", value=12.0, key="7_ked")
    jml_titik = st.sidebar.number_input("Jumlah Titik", value=20, step=1, key="7_jml")
    
    area = np.pi * (diameter / 2)**2
    vol_total_beton = area * kedalaman * jml_titik
    vol_pengeboran = area * kedalaman * jml_titik

    st.sidebar.header("Pekerjaan & AHSP")
    if mode_proyek == "Rehabilitasi Struktur":
        p_bongkar = st.sidebar.slider("Persen Titik Dibongkar (%)", 0, 100, 100, key="7_sl_bongk")
        show_bongkar = st.sidebar.checkbox("Pembersihan Lokasi/Bongkar Kepala", value=True, key="7_cb_bongk")
        h_bongkar = st.sidebar.number_input("AHSP Pembersihan (Rp/Titik)", value=500000, key="7_h_bongk") if show_bongkar else 0
        if show_bongkar: item_to_add.append([f"Pembersihan Lokasi/Bongkar Kepala ({p_bongkar}%)", jml_titik * (p_bongkar/100), "Titik", h_bongkar])

    show_bor = st.sidebar.checkbox("Pengeboran Bore Pile", value=True, key="7_cb_bor")
    h_bor = st.sidebar.number_input("AHSP Pengeboran (Rp/m³)", value=450000, key="7_h_bor") if show_bor else 0
    show_casing = st.sidebar.checkbox("Instalasi Temporary Casing", value=True, key="7_cb_cas")
    h_casing = st.sidebar.number_input("AHSP Casing (Rp/m')", value=150000, key="7_h_cas") if show_casing else 0
    show_cor = st.sidebar.checkbox("Pengecoran Beton K-350", value=True, key="7_cb_cor")
    h_cor = st.sidebar.number_input("AHSP Beton (Rp/m³)", value=1350000, key="7_h_cor") if show_cor else 0
    show_besi = st.sidebar.checkbox("Pembesian Tulangan", value=True, key="7_cb_besi")
    r_besi = st.sidebar.number_input("Rasio Besi (kg/m³)", value=180, key="7_r_besi") if show_besi else 0
    h_besi = st.sidebar.number_input("AHSP Besi (Rp/kg)", value=18500, key="7_h_besi") if show_besi else 0

    if show_bor: item_to_add.append(["Pengeboran Bore Pile", vol_pengeboran, "m³", h_bor])
    if show_casing: item_to_add.append(["Instalasi Temporary Casing", diameter * 2 * jml_titik, "m'", h_casing])
    if show_cor: item_to_add.append(["Pengecoran Beton K-350 (Bore Pile)", vol_total_beton, "m³", h_cor])
    if show_besi: item_to_add.append(["Pembesian Tulangan Bore Pile", vol_total_beton * r_besi, "kg", h_besi])

    fig, ax = plt.subplots()
    ax.add_patch(plt.Rectangle((-1, -kedalaman), 2, kedalaman, color='saddlebrown', alpha=0.1))
    ax.add_patch(plt.Rectangle((-diameter/2, -kedalaman), diameter, kedalaman, color='gray'))
    ax.set_xlim(-1, 1); ax.set_ylim(-kedalaman-1, 1); ax.set_aspect('equal')

# =====================================================================
# EDIT / HAPUS ITEM (DI SIDEBAR KIRI BAWAH)
# =====================================================================
if st.session_state.rekap_proyek:
    st.sidebar.divider()
    st.sidebar.header("✏️ Edit Item Tersimpan")
    st.sidebar.write("Pilih item di bawah ini untuk mengubah Volume atau AHSP-nya:")
    
    opsi_edit = [f"{i+1}. {item['Pekerjaan']} ({item['Kategori'].split('.')[0]})" for i, item in enumerate(st.session_state.rekap_proyek)]
    pilihan_edit = st.sidebar.selectbox("Pilih Item:", ["-- Pilih Item --"] + opsi_edit, key="select_edit")
    
    if pilihan_edit != "-- Pilih Item --":
        idx_edit = int(pilihan_edit.split(".")[0]) - 1
        item_terpilih = st.session_state.rekap_proyek[idx_edit]
        
        # Tampilkan data awal yang terekap
        st.sidebar.info(f"**Data Saat Ini:**\n- Volume Awal: {item_terpilih['Volume']} {item_terpilih['Satuan']}\n- AHSP Awal: Rp {item_terpilih['AHSP']:,.0f}")
        
        # Slider persentase perubahan volume
        persen_adj = st.sidebar.slider("Persentase Penyesuaian Volume (%)", 0, 200, 100, step=1, key="edit_adj")
        vol_hitung = float(item_terpilih['Volume']) * (persen_adj / 100.0)
        
        # Input yang otomatis terupdate berdasarkan slider (tapi tetap bisa diketik manual)
        val_vol = st.sidebar.number_input(f"Edit Volume Akhir ({item_terpilih['Satuan']})", value=float(vol_hitung), key="edit_vol")
        val_ahsp = st.sidebar.number_input("Edit AHSP Akhir (Rp)", value=float(item_terpilih['AHSP']), key="edit_ahsp")
        
        col_e1, col_e2 = st.sidebar.columns(2)
        with col_e1:
            if st.button("💾 Update Data", key="btn_update"):
                st.session_state.rekap_proyek[idx_edit]['Volume'] = val_vol
                st.session_state.rekap_proyek[idx_edit]['AHSP'] = val_ahsp
                st.session_state.rekap_proyek[idx_edit]['Total'] = val_vol * val_ahsp
                st.success("Data Diperbarui!")
                st.rerun()
        with col_e2:
            if st.button("🗑️ Hapus Item", key="btn_hapus"):
                st.session_state.rekap_proyek.pop(idx_edit)
                st.success("Data Dihapus!")
                st.rerun()

# =====================================================================
# MANAJEMEN DRAFT PROYEK (SAVE/LOAD) DI SIDEBAR BAWAH
# =====================================================================
st.sidebar.divider()
st.sidebar.header("📁 Manajemen Draft Proyek")

# 1. Upload Draft (Buka File .json)
uploaded_file = st.sidebar.file_uploader("Buka Draft RAB (.json)", type="json")
if uploaded_file is not None:
    if st.sidebar.button("📂 Muat File Draft Ini", use_container_width=True):
        try:
            draft_data = json.load(uploaded_file)
            st.session_state.rekap_proyek = draft_data
            st.sidebar.success("Draft berhasil dimuat!")
            st.rerun()
        except Exception as e:
            st.sidebar.error("File draft tidak valid atau rusak.")

# 2. Download Draft (Simpan ke .json)
if st.session_state.rekap_proyek:
    draft_json = json.dumps(st.session_state.rekap_proyek, indent=4)
    st.sidebar.download_button(
        label="💾 Simpan Draft Proyek (.json)",
        data=draft_json,
        file_name="Draft_RAB_Pemeliharaan_Sipil.json",
        mime="application/json",
        use_container_width=True
    )
    st.sidebar.info("Gunakan file `.json` ini untuk melanjutkan perhitungan Anda besok hari.")

# =====================================================================
# TAMPILAN PREVIEW & REKAP (PORTRAIT HP)
# =====================================================================
st.write("---")
st.subheader(f"Estimasi Item: {kategori_pekerjaan}")

subtotal_now = 0
for item in item_to_add:
    biaya = item[1] * item[3]
    subtotal_now += biaya
    st.write(f"**{item[0]}**")
    st.write(f"{item[1]:,.2f} {item[2]} | Rp {biaya:,.0f}")

st.info(f"Sub-Total Item Ini: Rp {subtotal_now:,.0f}")

if len(item_to_add) > 0:
    if st.button("TAMBAHKAN KE MASTER REKAP", use_container_width=True):
        for item in item_to_add:
            st.session_state.rekap_proyek.append({
                "Kategori": kategori_pekerjaan, "Pekerjaan": item[0],
                "Volume": round(item[1], 2), "Satuan": item[2],
                "AHSP": item[3], "Total": item[1] * item[3]
            })
        st.success("Data berhasil ditambahkan ke tabel RAB di bawah.")

st.write("---")
st.pyplot(fig)

# =====================================================================
# MASTER RAB FINAL (MURNI LAPORAN)
# =====================================================================
st.divider()
st.header("Laporan Rencana Anggaran Biaya (RAB)")

if st.session_state.rekap_proyek:
    # --- TAMPILAN TABEL RAB (HANYA DISPLAY) ---
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

    # Data tambahan untuk Tampilan Akhir
    export_data = display_data.copy()
    export_data.append({"Uraian Pekerjaan": "========================================", "Volume": "", "Harga Satuan": "", "Jumlah Harga": ""})
    export_data.append({"Uraian Pekerjaan": "A. TOTAL BIAYA LANGSUNG", "Volume": "", "Harga Satuan": "", "Jumlah Harga": f"Rp {biaya_langsung:,.0f}"})
    export_data.append({"Uraian Pekerjaan": f"B. OVERHEAD & PROFIT ({overhead_pct}%)", "Volume": "", "Harga Satuan": "", "Jumlah Harga": f"Rp {oh:,.0f}"})
    export_data.append({"Uraian Pekerjaan": "C. TOTAL (A + B)", "Volume": "", "Harga Satuan": "", "Jumlah Harga": f"Rp {biaya_langsung + oh:,.0f}"})
    export_data.append({"Uraian Pekerjaan": f"D. PPN / PAJAK ({ppn_pct}%)", "Volume": "", "Harga Satuan": "", "Jumlah Harga": f"Rp {ppn:,.0f}"})
    export_data.append({"Uraian Pekerjaan": "GRAND TOTAL KONTRAK", "Volume": "", "Harga Satuan": "", "Jumlah Harga": f"Rp {total_akhir:,.0f}"})

    df_export = pd.DataFrame(export_data)
    
    # Tampilkan di Streamlit
    st.dataframe(df_export, use_container_width=True)

    st.write("---")
    if st.button("🗑️ Kosongkan Master Rekap / Buat Proyek Baru", use_container_width=True):
        st.session_state.rekap_proyek = []
        st.rerun()
else:
    st.info("Silakan proses perhitungan melalui menu navigasi di atas dan tekan 'Tambahkan ke Master Rekap' untuk memunculkan tabel laporan RAB.")

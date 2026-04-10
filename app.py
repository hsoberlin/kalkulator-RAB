import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Estimator Proyek Terpadu", layout="wide")

if 'rekap_proyek' not in st.session_state:
    st.session_state.rekap_proyek = []

st.title("🏗️ Kalkulator Konstruksi Terpadu (Versi Lengkap)")
st.write("Menghitung detail Rencana Anggaran Biaya (RAB) lengkap dengan pekerjaan persiapan, struktur, dan penyelesaian.")

# --- SIDEBAR: NAVIGASI & PENGATURAN GLOBAL ---
st.sidebar.title("Navigasi Proyek")
jenis_bangunan = st.sidebar.selectbox(
    "Pilih Jenis Pekerjaan:",
    [
        "1. Saluran Trapesium (Beton)", 
        "2. Saluran Pasangan Batu (Drainase)",
        "3. Jalan Perkerasan Lentur (Aspal)", 
        "4. Jalan Perkerasan Kaku (Rigid)",
        "5. Pondasi Telapak",
        "6. Dinding Penahan Tanah (Kantilever)"
    ]
)

st.sidebar.divider()
st.sidebar.title("🌍 Kondisi Lahan Awal")
mode_proyek = st.sidebar.radio("Metode Pelaksanaan:", ["Bangunan Baru (Lahan Kosong/Tanah Asli)", "Rehabilitasi (Ada Struktur Lama)"])

persen_bongkar = 100
if mode_proyek == "Rehabilitasi (Ada Struktur Lama)":
    persen_bongkar = st.sidebar.slider("Persentase Bongkaran Struktur Lama (%)", 0, 100, 100)

st.sidebar.divider()
st.sidebar.title("⚙️ Pengaturan Keuangan")
overhead_pct = st.sidebar.number_input("Overhead & Profit (%)", value=10.0, step=1.0)
ppn_pct = st.sidebar.number_input("PPN / Pajak (%)", value=11.0, step=1.0)

item_to_add = []
kategori_pekerjaan = jenis_bangunan.split(". ")[1]

# =====================================================================
# 1. SALURAN TRAPESIUM (BETON)
# =====================================================================
if jenis_bangunan == "1. Saluran Trapesium (Beton)":
    st.sidebar.header("📐 Dimensi Saluran")
    l_atas = st.sidebar.number_input("Lebar Dalam Atas (m)", value=1.2)
    l_bawah = st.sidebar.number_input("Lebar Dalam Bawah (m)", value=0.8)
    tinggi = st.sidebar.number_input("Tinggi Saluran (m)", value=5.0)
    panjang = st.sidebar.number_input("Panjang Saluran (m)", value=100.0)
    t_atas = st.sidebar.number_input("Tebal Dinding Atas (m)", value=0.15)
    t_bawah = st.sidebar.number_input("Tebal Dinding Bawah (m)", value=0.25)
    t_dasar = st.sidebar.number_input("Tebal Pelat Dasar (m)", value=0.30)

    # Perhitungan Volume
    dist_dalam = (l_atas - l_bawah) / 2
    sisi_miring = np.sqrt(dist_dalam**2 + tinggi**2)
    luas_dinding_sisi = sisi_miring * ((t_atas + t_bawah) / 2)
    vol_beton = ((2 * luas_dinding_sisi) + (l_bawah * t_dasar)) * panjang
    
    vol_tanah_baru = (((l_atas+(2*t_atas) + l_bawah+(2*t_bawah))/2) * (tinggi+t_dasar)) * panjang
    vol_rongga = (((l_atas + l_bawah) / 2) * tinggi) * panjang
    luas_bekisting = (sisi_miring * 2) * panjang # Hanya bekisting dalam

    st.sidebar.header("🛠️ Pekerjaan & AHSP")
    if mode_proyek == "Bangunan Baru (Lahan Kosong/Tanah Asli)":
        show_galian = st.sidebar.checkbox("Galian Tanah Profil", value=True)
        h_galian = st.sidebar.number_input("AHSP Galian (Rp/m³)", value=75000) if show_galian else 0
        if show_galian: item_to_add.append(["Galian Tanah Profil Saluran", vol_tanah_baru, "m³", h_galian])
    else:
        show_bongkar = st.sidebar.checkbox("Bongkaran Beton Eksisting", value=True)
        h_bongkar = st.sidebar.number_input("AHSP Bongkaran (Rp/m³)", value=250000) if show_bongkar else 0
        show_sedimen = st.sidebar.checkbox("Galian Sedimen/Normalisasi", value=True)
        p_sedimen = st.sidebar.slider("Volume Sedimen (%)", 0, 100, 30, key='sed_sal') if show_sedimen else 0
        h_sedimen = st.sidebar.number_input("AHSP Galian Sedimen (Rp/m³)", value=85000) if show_sedimen else 0
        
        if show_bongkar: item_to_add.append([f"Bongkaran Beton Lama ({persen_bongkar}%)", vol_beton * (persen_bongkar/100), "m³", h_bongkar])
        if show_sedimen: item_to_add.append(["Galian Sedimen/Tanah Normalisasi", vol_rongga * (p_sedimen/100), "m³", h_sedimen])

    show_cor = st.sidebar.checkbox("Pengecoran Beton Baru", value=True)
    h_cor = st.sidebar.number_input("AHSP Cor (Rp/m³)", value=1200000) if show_cor else 0
    show_besi = st.sidebar.checkbox("Pembesian Saluran", value=True)
    r_besi = st.sidebar.number_input("Rasio Besi (kg/m³ beton)", value=110) if show_besi else 0
    h_besi = st.sidebar.number_input("AHSP Besi (Rp/kg)", value=18500) if show_besi else 0
    show_bekisting = st.sidebar.checkbox("Bekisting Dinding Saluran", value=True)
    h_bekisting = st.sidebar.number_input("AHSP Bekisting (Rp/m²)", value=125000) if show_bekisting else 0

    if show_cor: item_to_add.append(["Pengecoran Beton Dinding & Lantai", vol_beton, "m³", h_cor])
    if show_besi: item_to_add.append(["Pembesian Penulangan Saluran", vol_beton * r_besi, "kg", h_besi])
    if show_bekisting: item_to_add.append(["Pemasangan Bekisting", luas_bekisting, "m²", h_bekisting])

    fig, ax = plt.subplots()
    ax.plot([-l_atas/2, -l_bawah/2, l_bawah/2, l_atas/2], [0, -tinggi, -tinggi, 0], marker='o', color='brown', lw=3)
    ax.set_aspect('equal')
    ax.set_title("Saluran Trapesium Beton")

# =====================================================================
# 2. SALURAN PASANGAN BATU (DRAINASE)
# =====================================================================
elif jenis_bangunan == "2. Saluran Pasangan Batu (Drainase)":
    st.sidebar.header("📐 Dimensi Drainase")
    l_atas = st.sidebar.number_input("Lebar Atas (m)", value=1.0)
    l_bawah = st.sidebar.number_input("Lebar Bawah (m)", value=0.6)
    tinggi = st.sidebar.number_input("Tinggi (m)", value=1.2)
    t_batu = st.sidebar.number_input("Tebal Pasangan Batu (m)", value=0.25)
    panjang = st.sidebar.number_input("Panjang Saluran (m)", value=100.0)

    dist = (l_atas - l_bawah) / 2
    keliling_dalam = (2 * np.sqrt(dist**2 + tinggi**2)) + l_bawah
    vol_batu = keliling_dalam * t_batu * panjang
    vol_galian = (((l_atas+(2*t_batu)) + (l_bawah+(2*t_batu)))/2 * (tinggi+t_batu)) * panjang
    vol_rongga = (((l_atas + l_bawah) / 2) * tinggi) * panjang
    luas_plester = keliling_dalam * panjang

    st.sidebar.header("🛠️ Pekerjaan & AHSP")
    if mode_proyek == "Bangunan Baru (Lahan Kosong/Tanah Asli)":
        show_galian = st.sidebar.checkbox("Galian Tanah", value=True)
        h_galian = st.sidebar.number_input("AHSP Galian (Rp/m³)", value=75000) if show_galian else 0
        if show_galian: item_to_add.append(["Galian Tanah Drainase", vol_galian, "m³", h_galian])
    else:
        show_bongkar = st.sidebar.checkbox("Bongkaran Batu Eksisting", value=True)
        h_bongkar = st.sidebar.number_input("AHSP Bongkaran Batu (Rp/m³)", value=150000) if show_bongkar else 0
        show_sedimen = st.sidebar.checkbox("Galian Sedimen (Normalisasi)", value=True)
        p_sedimen = st.sidebar.slider("Volume Sedimen (%)", 0, 100, 30, key='sed_pb') if show_sedimen else 0
        h_sedimen = st.sidebar.number_input("AHSP Galian Sedimen (Rp/m³)", value=85000) if show_sedimen else 0
        
        if show_bongkar: item_to_add.append([f"Bongkaran Pasangan Batu ({persen_bongkar}%)", vol_batu * (persen_bongkar/100), "m³", h_bongkar])
        if show_sedimen: item_to_add.append(["Galian Sedimen Drainase", vol_rongga * (p_sedimen/100), "m³", h_sedimen])

    show_pasangan = st.sidebar.checkbox("Pasangan Batu Kali (1:4)", value=True)
    h_pasangan = st.sidebar.number_input("AHSP Pasangan Batu (Rp/m³)", value=950000) if show_pasangan else 0
    show_plester = st.sidebar.checkbox("Plesteran & Acian Permukaan", value=True)
    h_plester = st.sidebar.number_input("AHSP Plesteran (Rp/m²)", value=65000) if show_plester else 0

    if show_pasangan: item_to_add.append(["Pekerjaan Pasangan Batu Kali", vol_batu, "m³", h_pasangan])
    if show_plester: item_to_add.append(["Plesteran & Acian Saluran", luas_plester, "m²", h_plester])

    fig, ax = plt.subplots()
    ax.plot([0, dist, dist + l_bawah, l_atas], [0, -tinggi, -tinggi, 0], color='black', lw=4)
    ax.set_aspect('equal')
    ax.set_title("Saluran Pasangan Batu (Drainase)")

# =====================================================================
# 3. JALAN PERKERASAN LENTUR (ASPAL)
# =====================================================================
elif jenis_bangunan == "3. Jalan Perkerasan Lentur (Aspal)":
    st.sidebar.header("📐 Dimensi Jalan")
    lebar = st.sidebar.number_input("Lebar Jalan (m)", value=6.0)
    panjang = st.sidebar.number_input("Panjang Jalan (m)", value=1000.0)
    t_aspal = st.sidebar.number_input("Tebal Aspal (m)", value=0.05)

    st.sidebar.header("🛠️ Pekerjaan & AHSP")
    if mode_proyek == "Bangunan Baru (Lahan Kosong/Tanah Asli)":
        t_base = st.sidebar.number_input("Tebal Lapis Pondasi/Base A (m)", value=0.15)
        show_grading = st.sidebar.checkbox("Penyiapan Badan Jalan", value=True)
        h_grading = st.sidebar.number_input("AHSP Penyiapan (Rp/m²)", value=12000) if show_grading else 0
        show_base = st.sidebar.checkbox("Lapis Pondasi (Agregat A)", value=True)
        h_base = st.sidebar.number_input("AHSP Agregat A (Rp/m³)", value=450000) if show_base else 0
        
        if show_grading: item_to_add.append(["Penyiapan Badan Jalan (Grading)", lebar * panjang, "m²", h_grading])
        if show_base: item_to_add.append(["Lapis Pondasi Agregat Kelas A", lebar * panjang * t_base, "m³", h_base])
    else:
        show_milling = st.sidebar.checkbox("Kupas Aspal (Cold Milling)", value=True)
        t_milling = st.sidebar.number_input("Tebal Kupasan (m)", value=0.04) if show_milling else 0
        h_milling = st.sidebar.number_input("AHSP Milling (Rp/m²)", value=35000) if show_milling else 0
        show_tack = st.sidebar.checkbox("Lapis Perekat (Tack Coat)", value=True)
        h_tack = st.sidebar.number_input("AHSP Tack Coat (Rp/Liter)", value=15000) if show_tack else 0
        
        if show_milling: item_to_add.append([f"Cold Milling Aspal ({persen_bongkar}%)", (lebar * panjang * t_milling) * (persen_bongkar/100), "m³", h_milling])
        if show_tack: item_to_add.append(["Lapis Perekat (Tack Coat)", (lebar * panjang) * 0.35, "Liter", h_tack]) # Asumsi 0.35 L/m2

    show_aspal = st.sidebar.checkbox("Hampar Aspal (AC-WC)", value=True)
    h_aspal = st.sidebar.number_input("AHSP Aspal AC-WC (Rp/m³)", value=2500000) if show_aspal else 0
    if show_aspal: item_to_add.append(["Lapis Permukaan Aspal (AC-WC)", lebar * panjang * t_aspal, "m³", h_aspal])

    fig, ax = plt.subplots()
    ax.add_patch(plt.Rectangle((0, -t_aspal), lebar, t_aspal, color='black', alpha=0.8))
    ax.set_xlim(-1, lebar + 1); ax.set_ylim(-0.3, 0.1); ax.set_aspect('equal')
    ax.set_title("Perkerasan Lentur (Aspal)")

# =====================================================================
# 4. JALAN PERKERASAN KAKU (RIGID)
# =====================================================================
elif jenis_bangunan == "4. Jalan Perkerasan Kaku (Rigid)":
    st.sidebar.header("📐 Dimensi Jalan Rigid")
    lebar = st.sidebar.number_input("Lebar Perkerasan (m)", value=5.0)
    panjang = st.sidebar.number_input("Panjang Jalan (m)", value=500.0)
    t_rigid = st.sidebar.number_input("Tebal Beton Rigid (m)", value=0.25)
    t_lc = st.sidebar.number_input("Tebal Lantai Kerja/LC (m)", value=0.10)
    vol_rigid = lebar * panjang * t_rigid
    vol_lc = lebar * panjang * t_lc
    luas_bekisting = (t_rigid + t_lc) * panjang * 2 # Dua sisi jalan

    st.sidebar.header("🛠️ Pekerjaan & AHSP")
    if mode_proyek == "Bangunan Baru (Lahan Kosong/Tanah Asli)":
        show_grading = st.sidebar.checkbox("Penyiapan Badan Jalan", value=True)
        h_grading = st.sidebar.number_input("AHSP Penyiapan (Rp/m²)", value=12000) if show_grading else 0
        if show_grading: item_to_add.append(["Penyiapan Badan Jalan", lebar * panjang, "m²", h_grading])
    else:
        show_bongkar = st.sidebar.checkbox("Bongkaran Rigid Lama", value=True)
        h_bongkar = st.sidebar.number_input("AHSP Bongkaran Rigid (Rp/m³)", value=450000) if show_bongkar else 0
        if show_bongkar: item_to_add.append([f"Bongkaran Beton Rigid Lama ({persen_bongkar}%)", vol_rigid * (persen_bongkar/100), "m³", h_bongkar])

    show_lc = st.sidebar.checkbox("Lantai Kerja (LC)", value=True)
    h_lc = st.sidebar.number_input("AHSP Lantai Kerja (Rp/m³)", value=950000) if show_lc else 0
    show_bekisting = st.sidebar.checkbox("Bekisting Jalan", value=True)
    h_bekisting = st.sidebar.number_input("AHSP Bekisting (Rp/m²)", value=125000) if show_bekisting else 0
    show_rigid = st.sidebar.checkbox("Pengecoran Beton Rigid", value=True)
    h_rigid = st.sidebar.number_input("AHSP Beton Rigid (Rp/m³)", value=1450000) if show_rigid else 0
    show_besi = st.sidebar.checkbox("Pembesian (Dowel/Wiremesh)", value=True)
    r_besi = st.sidebar.number_input("Rasio Besi (kg/m³)", value=60) if show_besi else 0
    h_besi = st.sidebar.number_input("AHSP Besi (Rp/kg)", value=18500) if show_besi else 0

    if show_lc: item_to_add.append(["Pengecoran Lantai Kerja (LC)", vol_lc, "m³", h_lc])
    if show_bekisting: item_to_add.append(["Pemasangan Bekisting Jalan", luas_bekisting, "m²", h_bekisting])
    if show_rigid: item_to_add.append(["Pengecoran Beton Rigid K-350", vol_rigid, "m³", h_rigid])
    if show_besi: item_to_add.append(["Pembesian (Dowel/Tie-bar/Wiremesh)", vol_rigid * r_besi, "kg", h_besi])

    fig, ax = plt.subplots()
    ax.add_patch(plt.Rectangle((0, 0), lebar, t_rigid, color='lightgray', ec='black', hatch='//'))
    ax.add_patch(plt.Rectangle((0, -t_lc), lebar, t_lc, color='orange', alpha=0.4))
    ax.set_xlim(-1, lebar + 1); ax.set_ylim(-0.3, 0.4); ax.set_aspect('equal')
    ax.set_title("Perkerasan Kaku (Rigid Pavement)")

# =====================================================================
# 5. PONDASI TELAPAK
# =====================================================================
elif jenis_bangunan == "5. Pondasi Telapak":
    st.sidebar.header("📐 Dimensi Pondasi")
    p_telapak = st.sidebar.number_input("Panjang (m)", value=1.5)
    l_telapak = st.sidebar.number_input("Lebar (m)", value=1.5)
    t_telapak = st.sidebar.number_input("Tebal Plat Pondasi (m)", value=0.3)
    sisi_kolom = st.sidebar.number_input("Sisi Kolom Pedestal (m)", value=0.4)
    t_kolom = st.sidebar.number_input("Tinggi Kolom (m)", value=1.0)
    jml_titik = st.sidebar.number_input("Jumlah Titik", value=10)
    
    vol_beton = ((p_telapak * l_telapak * t_telapak) + (sisi_kolom * sisi_kolom * t_kolom)) * jml_titik
    vol_galian = (p_telapak + 0.4) * (l_telapak + 0.4) * (t_telapak + t_kolom) * jml_titik # space kerja 20cm keliling
    vol_lc = p_telapak * l_telapak * 0.05 * jml_titik # tebal LC 5cm
    luas_bekisting = (((p_telapak + l_telapak) * 2 * t_telapak) + ((sisi_kolom * 4) * t_kolom)) * jml_titik

    st.sidebar.header("🛠️ Pekerjaan & AHSP")
    if mode_proyek != "Bangunan Baru (Lahan Kosong/Tanah Asli)":
        show_bongkar = st.sidebar.checkbox("Bongkaran Pondasi Lama", value=True)
        h_bongkar = st.sidebar.number_input("AHSP Bongkaran (Rp/m³)", value=350000) if show_bongkar else 0
        if show_bongkar: item_to_add.append([f"Bongkaran Struktur Lama ({persen_bongkar}%)", vol_beton * (persen_bongkar/100), "m³", h_bongkar])

    show_galian = st.sidebar.checkbox("Galian Tanah Pondasi", value=True)
    h_galian = st.sidebar.number_input("AHSP Galian (Rp/m³)", value=75000) if show_galian else 0
    show_lc = st.sidebar.checkbox("Lantai Kerja (tebal 5cm)", value=True)
    h_lc = st.sidebar.number_input("AHSP Lantai Kerja (Rp/m³)", value=950000) if show_lc else 0
    show_bekisting = st.sidebar.checkbox("Bekisting Pondasi & Kolom", value=True)
    h_bekisting = st.sidebar.number_input("AHSP Bekisting (Rp/m²)", value=145000) if show_bekisting else 0
    show_cor = st.sidebar.checkbox("Beton Bertulang", value=True)
    h_cor = st.sidebar.number_input("AHSP Beton (Rp/m³)", value=4500000) if show_cor else 0
    show_besi = st.sidebar.checkbox("Pembesian", value=True)
    r_besi = st.sidebar.number_input("Rasio Besi (kg/m³)", value=150) if show_besi else 0
    h_besi = st.sidebar.number_input("AHSP Besi (Rp/kg)", value=18500) if show_besi else 0

    if show_galian: item_to_add.append(["Galian Tanah Pondasi", vol_galian, "m³", h_galian])
    if show_lc: item_to_add.append(["Lantai Kerja Pondasi (LC)", vol_lc, "m³", h_lc])
    if show_bekisting: item_to_add.append(["Bekisting Plat & Kolom", luas_bekisting, "m²", h_bekisting])
    if show_cor: item_to_add.append(["Pengecoran Beton Pondasi", vol_beton, "m³", h_cor])
    if show_besi: item_to_add.append(["Pembesian Pondasi", vol_beton * r_besi, "kg", h_besi])

    fig, ax = plt.subplots()
    ax.add_patch(plt.Rectangle((-(p_telapak/2), 0), p_telapak, t_telapak, color='gray'))
    ax.add_patch(plt.Rectangle((-(sisi_kolom/2), t_telapak), sisi_kolom, t_kolom, color='darkgray'))
    ax.set_xlim(-2, 2); ax.set_ylim(-0.5, t_telapak + t_kolom + 0.5); ax.set_aspect('equal')
    ax.set_title("Pondasi Telapak + Kolom Pedestal")

# =====================================================================
# 6. DINDING PENAHAN TANAH (DPT)
# =====================================================================
elif jenis_bangunan == "6. Dinding Penahan Tanah (Kantilever)":
    st.sidebar.header("📐 Dimensi Dinding")
    tinggi = st.sidebar.number_input("Tinggi Dinding/Stem (m)", value=4.0)
    t_atas = st.sidebar.number_input("Tebal Dinding Atas (m)", value=0.3)
    t_bawah = st.sidebar.number_input("Tebal Dinding Bawah (m)", value=0.5)
    l_base = st.sidebar.number_input("Lebar Pelat Dasar (m)", value=2.5)
    t_base = st.sidebar.number_input("Tebal Pelat Dasar (m)", value=0.4)
    l_heel = st.sidebar.number_input("Lebar Heel/Belakang (m)", value=1.2)
    panjang = st.sidebar.number_input("Panjang Total DPT (m)", value=50.0)

    vol_beton_stem = ((t_atas + t_bawah) / 2 * tinggi) * panjang
    vol_beton_base = (l_base * t_base) * panjang
    vol_beton = vol_beton_stem + vol_beton_base
    vol_galian = (l_base + 0.5) * t_base * panjang
    vol_timbunan = l_heel * tinggi * panjang # Tanah backfill
    luas_bekisting = (tinggi * 2 * panjang) + (t_base * 2 * panjang) # Sederhana: depan belakang dinding + sisi base

    st.sidebar.header("🛠️ Pekerjaan & AHSP")
    if mode_proyek != "Bangunan Baru (Lahan Kosong/Tanah Asli)":
        show_bongkar = st.sidebar.checkbox("Bongkaran DPT Lama", value=True)
        h_bongkar = st.sidebar.number_input("AHSP Bongkaran (Rp/m³)", value=350000) if show_bongkar else 0
        if show_bongkar: item_to_add.append([f"Bongkaran DPT Eksisting ({persen_bongkar}%)", vol_beton * (persen_bongkar/100), "m³", h_bongkar])

    show_galian = st.sidebar.checkbox("Galian Tanah Struktur", value=True)
    h_galian = st.sidebar.number_input("AHSP Galian (Rp/m³)", value=75000) if show_galian else 0
    show_bekisting = st.sidebar.checkbox("Bekisting Dinding & Base", value=True)
    h_bekisting = st.sidebar.number_input("AHSP Bekisting (Rp/m²)", value=145000) if show_bekisting else 0
    show_cor = st.sidebar.checkbox("Beton Bertulang", value=True)
    h_cor = st.sidebar.number_input("AHSP Beton (Rp/m³)", value=4200000) if show_cor else 0
    show_besi = st.sidebar.checkbox("Pembesian DPT", value=True)
    r_besi = st.sidebar.number_input("Rasio Besi (kg/m³)", value=125) if show_besi else 0
    h_besi = st.sidebar.number_input("AHSP Besi (Rp/kg)", value=18500) if show_besi else 0
    show_timbunan = st.sidebar.checkbox("Timbunan Kembali (Backfill)", value=True)
    h_timbunan = st.sidebar.number_input("AHSP Timbunan (Rp/m³)", value=115000) if show_timbunan else 0

    if show_galian: item_to_add.append(["Galian Tanah Struktur", vol_galian, "m³", h_galian])
    if show_bekisting: item_to_add.append(["Pemasangan Bekisting DPT", luas_bekisting, "m²", h_bekisting])
    if show_cor: item_to_add.append(["Pengecoran Beton DPT", vol_beton, "m³", h_cor])
    if show_besi: item_to_add.append(["Pembesian Struktur DPT", vol_beton * r_besi, "kg", h_besi])
    if show_timbunan: item_to_add.append(["Timbunan Tanah Backfill", vol_timbunan, "m³", h_timbunan])

    fig, ax = plt.subplots()
    l_toe = l_base - l_heel - t_bawah
    ax.add_patch(plt.Rectangle((0, -t_base), l_base, t_base, color='gray')) # Base
    ax.fill([l_toe, l_toe + t_bawah, l_toe + t_bawah - (t_bawah-t_atas), l_toe], [0, 0, tinggi, tinggi], color='gray') # Stem
    ax.add_patch(plt.Rectangle((l_toe + t_bawah, 0), l_heel, tinggi, color='saddlebrown', alpha=0.4)) # Backfill
    ax.set_xlim(-1, l_base + 1); ax.set_ylim(-1, tinggi + 1); ax.set_aspect('equal')
    ax.set_title("Dinding Penahan Tanah Kantilever")

# =====================================================================
# PREVIEW & ADD BUTTON
# =====================================================================
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader(f"Preview: {kategori_pekerjaan}")
    total_preview = 0
    for item in item_to_add:
        total_preview += (item[1] * item[3])
        st.write(f"- **{item[0]}**: {item[1]:.2f} {item[2]} (Rp {item[1]*item[3]:,.0f})")
    
    if len(item_to_add) > 0:
        if st.button("➕ TAMBAHKAN KE MASTER REKAP", use_container_width=True):
            for item in item_to_add:
                st.session_state.rekap_proyek.append({
                    "Kategori": kategori_pekerjaan,
                    "Pekerjaan": item[0],
                    "Volume": round(item[1], 2),
                    "Satuan": item[2],
                    "AHSP": item[3],
                    "Total Biaya": item[1] * item[3]
                })
            st.success("Berhasil ditambahkan ke Master Rekap!")

with col2:
    st.pyplot(fig)

# =====================================================================
# MASTER REKAPITULASI BIAYA (DENGAN OVERHEAD & PPN)
# =====================================================================
st.divider()
st.header("🛒 Master Rekapitulasi Proyek (RAB Final)")

if st.session_state.rekap_proyek:
    df_rekap = pd.DataFrame(st.session_state.rekap_proyek)
    rab_display_data = []
    
    total_biaya_langsung = 0
    for kat in df_rekap['Kategori'].unique():
        df_kat = df_rekap[df_rekap['Kategori'] == kat]
        subtotal_kat = df_kat['Total Biaya'].sum()
        total_biaya_langsung += subtotal_kat
        
        for _, row in df_kat.iterrows():
            rab_display_data.append({
                "Uraian Pekerjaan": row['Pekerjaan'], "Volume": f"{row['Volume']} {row['Satuan']}",
                "Harga Satuan": f"Rp {row['AHSP']:,.0f}", "Jumlah Harga": f"Rp {row['Total Biaya']:,.0f}"
            })
        rab_display_data.append({"Uraian Pekerjaan": f"➡️ SUB-TOTAL {kat.upper()}", "Volume": "", "Harga Satuan": "", "Jumlah Harga": f"Rp {subtotal_kat:,.0f}"})
        rab_display_data.append({"Uraian Pekerjaan": "", "Volume": "", "Harga Satuan": "", "Jumlah Harga": ""})

    nilai_overhead = total_biaya_langsung * (overhead_pct / 100)
    total_plus_overhead = total_biaya_langsung + nilai_overhead
    nilai_ppn = total_plus_overhead * (ppn_pct / 100)
    grand_total_final = total_plus_overhead + nilai_ppn

    rab_display_data.append({"Uraian Pekerjaan": "========================================", "Volume": "", "Harga Satuan": "", "Jumlah Harga": ""})
    rab_display_data.append({"Uraian Pekerjaan": "A. TOTAL BIAYA LANGSUNG", "Volume": "", "Harga Satuan": "", "Jumlah Harga": f"Rp {total_biaya_langsung:,.0f}"})
    rab_display_data.append({"Uraian Pekerjaan": f"B. OVERHEAD & PROFIT ({overhead_pct}%)", "Volume": "", "Harga Satuan": "", "Jumlah Harga": f"Rp {nilai_overhead:,.0f}"})
    rab_display_data.append({"Uraian Pekerjaan": "C. TOTAL (A + B)", "Volume": "", "Harga Satuan": "", "Jumlah Harga": f"Rp {total_plus_overhead:,.0f}"})
    rab_display_data.append({"Uraian Pekerjaan": f"D. PPN / PAJAK ({ppn_pct}%)", "Volume": "", "Harga Satuan": "", "Jumlah Harga": f"Rp {nilai_ppn:,.0f}"})

    st.subheader("📋 Laporan Rencana Anggaran Biaya (RAB)")
    st.dataframe(pd.DataFrame(rab_display_data), use_container_width=True)
    st.metric("💰 GRAND TOTAL PROYEK (Termasuk OAT & PPN)", f"Rp {grand_total_final:,.0f}")
    
    if st.button("🗑️ Kosongkan Master Rekap"):
        st.session_state.rekap_proyek = []
        st.rerun()
else:
    st.info("Silakan proses perhitungan di atas lalu klik 'Tambahkan ke Master Rekap'.")

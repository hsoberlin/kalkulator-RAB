import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Konfigurasi Portrait untuk HP
st.set_page_config(page_title="Estimator RAB Konstruksi", layout="centered")

if 'rekap_proyek' not in st.session_state:
    st.session_state.rekap_proyek = []

st.title("Aplikasi Estimator Rencana Anggaran Biaya")
st.write("Sistem perhitungan teknis volume dan biaya konstruksi terpadu (Versi Master Lengkap).")

# --- SIDEBAR MENU UTAMA ---
st.sidebar.title("Navigasi Proyek")
jenis_bangunan = st.sidebar.selectbox(
    "Pilih Jenis Pekerjaan:",
    [
        "0. Pekerjaan Persiapan (Divisi 1)",
        "1. Saluran Trapesium (Beton)", 
        "2. Saluran Pasangan Batu (Drainase)",
        "3. Jalan Perkerasan Lentur (Aspal)", 
        "4. Jalan Perkerasan Kaku (Rigid)",
        "5. Pondasi Telapak",
        "6. Dinding Penahan Tanah (Kantilever)",
        "7. Pondasi Bore Pile"
    ]
)

st.sidebar.divider()

# --- KONDISI LAHAN ---
st.sidebar.title("Kondisi Lahan Awal")
mode_proyek = st.sidebar.radio(
    "Metode Pelaksanaan:", 
    ["Bangunan Baru", "Rehabilitasi Struktur"]
)

st.sidebar.divider()

# --- PENGATURAN KEUANGAN ---
st.sidebar.title("Pengaturan Keuangan")
overhead_pct = st.sidebar.number_input("Overhead & Profit (%)", value=10.0, step=1.0)
ppn_pct = st.sidebar.number_input("PPN / Pajak (%)", value=11.0, step=1.0)

st.sidebar.divider()

item_to_add = []
kategori_pekerjaan = jenis_bangunan # Menggunakan nama lengkap agar berurutan di RAB (0, 1, 2, dst)

# =====================================================================
# 0. PEKERJAAN PERSIAPAN (DIVISI 1)
# =====================================================================
if jenis_bangunan == "0. Pekerjaan Persiapan (Divisi 1)":
    st.sidebar.header("Item Persiapan (Lump Sum)")
    
    show_survey = st.sidebar.checkbox("Survey, Pengukuran & Pasang Bowplank", value=True)
    h_survey = st.sidebar.number_input("Biaya Survey (Rp)", value=5000000) if show_survey else 0

    show_k3 = st.sidebar.checkbox("Penyelenggaraan SMK3 (K3 Konstruksi)", value=True)
    h_k3 = st.sidebar.number_input("Biaya K3 (Rp)", value=3500000) if show_k3 else 0

    show_mob = st.sidebar.checkbox("Mobilisasi & Demobilisasi Alat Berat", value=True)
    h_mob = st.sidebar.number_input("Biaya Mob-Demob (Rp)", value=12000000) if show_mob else 0

    show_direksi = st.sidebar.checkbox("Sewa/Pembuatan Direksi Keet", value=True)
    h_direksi = st.sidebar.number_input("Biaya Direksi Keet (Rp)", value=7500000) if show_direksi else 0

    if show_survey: item_to_add.append(["Survey, Pengukuran & Bowplank", 1.0, "LS", h_survey])
    if show_k3: item_to_add.append(["Penyelenggaraan SMK3", 1.0, "LS", h_k3])
    if show_mob: item_to_add.append(["Mobilisasi & Demobilisasi", 1.0, "LS", h_mob])
    if show_direksi: item_to_add.append(["Fasilitas Proyek/Direksi Keet", 1.0, "LS", h_direksi])

    fig, ax = plt.subplots()
    ax.text(0.5, 0.5, 'Divisi 1:\nPekerjaan Persiapan & Umum\n(Non-Struktural)', horizontalalignment='center', verticalalignment='center', fontsize=14, fontweight='bold', color='gray')
    ax.set_axis_off()

# =====================================================================
# 1. SALURAN TRAPESIUM (BETON)
# =====================================================================
elif jenis_bangunan == "1. Saluran Trapesium (Beton)":
    st.sidebar.header("Dimensi Saluran")
    l_atas = st.sidebar.number_input("Lebar Dalam Atas (m)", value=1.2)
    l_bawah = st.sidebar.number_input("Lebar Dalam Bawah (m)", value=0.8)
    tinggi = st.sidebar.number_input("Tinggi Saluran (m)", value=5.0)
    panjang = st.sidebar.number_input("Panjang Saluran (m)", value=100.0)
    t_atas = st.sidebar.number_input("Tebal Atas (m)", value=0.15)
    t_bawah = st.sidebar.number_input("Tebal Bawah (m)", value=0.25)
    t_dasar = st.sidebar.number_input("Tebal Dasar (m)", value=0.30)

    dist = (l_atas - l_bawah) / 2
    s_miring = np.sqrt(dist**2 + tinggi**2)
    vol_beton = (((t_atas + t_bawah) / 2 * s_miring * 2) + (l_bawah * t_dasar)) * panjang
    vol_tanah = (((l_atas+(2*t_atas) + l_bawah+(2*t_bawah))/2) * (tinggi+t_dasar)) * panjang
    vol_rongga = (((l_atas + l_bawah) / 2) * tinggi) * panjang

    st.sidebar.header("Pekerjaan & AHSP")
    if mode_proyek == "Bangunan Baru":
        show_galian = st.sidebar.checkbox("Galian Tanah Profil", value=True)
        h_galian = st.sidebar.number_input("AHSP Galian (Rp/m³)", value=75000) if show_galian else 0
        if show_galian: item_to_add.append(["Galian Tanah Profil Baru", vol_tanah, "m³", h_galian])
    else:
        p_bongkar = st.sidebar.slider("Persen Bongkaran (%)", 0, 100, 100)
        p_sedimen = st.sidebar.slider("Persen Sedimen (%)", 0, 100, 30)
        show_bongkar = st.sidebar.checkbox("Bongkaran Beton Eksisting", value=True)
        h_bongkar = st.sidebar.number_input("AHSP Bongkaran (Rp/m³)", value=250000) if show_bongkar else 0
        show_sedimen = st.sidebar.checkbox("Galian Sedimen Saluran", value=True)
        h_sedimen = st.sidebar.number_input("AHSP Galian Sedimen (Rp/m³)", value=85000) if show_sedimen else 0
        if show_bongkar: item_to_add.append([f"Bongkaran Beton ({p_bongkar}%)", vol_beton*(p_bongkar/100), "m³", h_bongkar])
        if show_sedimen: item_to_add.append(["Galian Sedimen/Lumpur", vol_rongga*(p_sedimen/100), "m³", h_sedimen])

    show_bekisting = st.sidebar.checkbox("Bekisting Dinding Saluran", value=True)
    h_bekisting = st.sidebar.number_input("AHSP Bekisting (Rp/m²)", value=125000) if show_bekisting else 0
    show_cor = st.sidebar.checkbox("Pengecoran Beton Saluran", value=True)
    h_cor = st.sidebar.number_input("AHSP Cor Beton (Rp/m³)", value=1200000) if show_cor else 0
    show_besi = st.sidebar.checkbox("Pembesian Saluran", value=True)
    r_besi = st.sidebar.number_input("Rasio Besi (kg/m³)", value=110) if show_besi else 0
    h_besi = st.sidebar.number_input("AHSP Besi (Rp/kg)", value=18500) if show_besi else 0

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
    l_atas = st.sidebar.number_input("Lebar Atas (m)", value=1.0)
    l_bawah = st.sidebar.number_input("Lebar Bawah (m)", value=0.6)
    tinggi = st.sidebar.number_input("Tinggi (m)", value=1.2)
    tebal = st.sidebar.number_input("Tebal Batu (m)", value=0.25)
    panjang = st.sidebar.number_input("Panjang (m)", value=100.0)

    dist = (l_atas - l_bawah) / 2
    keliling = (2 * np.sqrt(dist**2 + tinggi**2)) + l_bawah
    vol_batu = keliling * tebal * panjang

    st.sidebar.header("Pekerjaan & AHSP")
    if mode_proyek == "Bangunan Baru":
        vol_galian = (((l_atas+(2*tebal)) + (l_bawah+(2*tebal)))/2 * (tinggi+tebal)) * panjang
        show_galian = st.sidebar.checkbox("Galian Tanah Drainase", value=True)
        h_galian = st.sidebar.number_input("AHSP Galian (Rp/m³)", value=75000) if show_galian else 0
        if show_galian: item_to_add.append(["Galian Tanah Drainase", vol_galian, "m³", h_galian])
    else:
        p_bongkar = st.sidebar.slider("Persen Bongkaran (%)", 0, 100, 100, key="b_batu")
        show_bongkar = st.sidebar.checkbox("Bongkaran Batu Eksisting", value=True)
        h_bongkar = st.sidebar.number_input("AHSP Bongkaran (Rp/m³)", value=150000) if show_bongkar else 0
        if show_bongkar: item_to_add.append([f"Bongkaran Batu Eksisting ({p_bongkar}%)", vol_batu * (p_bongkar/100), "m³", h_bongkar])

    show_pasangan = st.sidebar.checkbox("Pasangan Batu Kali (1:4)", value=True)
    h_pasangan = st.sidebar.number_input("AHSP Pasangan Batu (Rp/m³)", value=950000) if show_pasangan else 0
    show_plester = st.sidebar.checkbox("Plesteran + Acian", value=True)
    h_plester = st.sidebar.number_input("AHSP Plesteran (Rp/m²)", value=65000) if show_plester else 0

    if show_pasangan: item_to_add.append(["Pasangan Batu Kali (1:4)", vol_batu, "m³", h_pasangan])
    if show_plester: item_to_add.append(["Plesteran + Acian", keliling * panjang, "m²", h_plester])

    fig, ax = plt.subplots()
    ax.plot([0, dist, dist+l_bawah, l_atas], [0, -tinggi, -tinggi, 0], color='black', lw=3)
    ax.set_aspect('equal')

# =====================================================================
# 3. JALAN PERKERASAN LENTUR (ASPAl)
# =====================================================================
elif jenis_bangunan == "3. Jalan Perkerasan Lentur (Aspal)":
    st.sidebar.header("Dimensi Jalan")
    lebar = st.sidebar.number_input("Lebar (m)", value=6.0)
    panjang = st.sidebar.number_input("Panjang (m)", value=1000.0)
    t_aspal = st.sidebar.number_input("Tebal Aspal (m)", value=0.05)
    t_base = st.sidebar.number_input("Tebal Agregat (m)", value=0.15)

    st.sidebar.header("Pekerjaan & AHSP")
    if mode_proyek == "Bangunan Baru":
        show_grading = st.sidebar.checkbox("Penyiapan Badan Jalan", value=True)
        h_grading = st.sidebar.number_input("AHSP Penyiapan (Rp/m²)", value=12000) if show_grading else 0
        show_base = st.sidebar.checkbox("Lapis Pondasi Agregat A", value=True)
        h_base = st.sidebar.number_input("AHSP Agregat A (Rp/m³)", value=450000) if show_base else 0
        if show_grading: item_to_add.append(["Penyiapan Badan Jalan", lebar * panjang, "m²", h_grading])
        if show_base: item_to_add.append(["Lapis Pondasi Agregat A", lebar * panjang * t_base, "m³", h_base])
    else:
        show_milling = st.sidebar.checkbox("Cold Milling (Kupas Aspal)", value=True)
        h_milling = st.sidebar.number_input("AHSP Milling (Rp/m³)", value=350000) if show_milling else 0
        show_tack = st.sidebar.checkbox("Lapis Perekat (Tack Coat)", value=True)
        h_tack = st.sidebar.number_input("AHSP Tack Coat (Rp/Liter)", value=15000) if show_tack else 0
        if show_milling: item_to_add.append(["Cold Milling (Kupas Aspal)", lebar * panjang * t_aspal, "m³", h_milling])
        if show_tack: item_to_add.append(["Lapis Perekat (Tack Coat)", lebar * panjang * 0.35, "Liter", h_tack])

    show_aspal = st.sidebar.checkbox("Aspal Hotmix AC-WC", value=True)
    h_aspal = st.sidebar.number_input("AHSP Aspal (Rp/m³)", value=2500000) if show_aspal else 0
    if show_aspal: item_to_add.append(["Aspal Hotmix AC-WC", lebar * panjang * t_aspal, "m³", h_aspal])

    fig, ax = plt.subplots()
    ax.add_patch(plt.Rectangle((0, -t_aspal), lebar, t_aspal, color='black'))
    ax.set_xlim(-1, lebar+1); ax.set_ylim(-0.2, 0.1); ax.set_aspect('equal')

# =====================================================================
# 4. JALAN PERKERASAN KAKU (RIGID)
# =====================================================================
elif jenis_bangunan == "4. Jalan Perkerasan Kaku (Rigid)":
    st.sidebar.header("Dimensi Rigid")
    lebar = st.sidebar.number_input("Lebar (m)", value=5.0)
    panjang = st.sidebar.number_input("Panjang (m)", value=500.0)
    t_rigid = st.sidebar.number_input("Tebal Rigid (m)", value=0.25)
    t_lc = st.sidebar.number_input("Tebal Lantai Kerja (m)", value=0.10)

    st.sidebar.header("Pekerjaan & AHSP")
    if mode_proyek == "Bangunan Baru":
        show_grading = st.sidebar.checkbox("Penyiapan Badan Jalan", value=True)
        h_grading = st.sidebar.number_input("AHSP Penyiapan (Rp/m²)", value=12000) if show_grading else 0
        if show_grading: item_to_add.append(["Penyiapan Badan Jalan", lebar * panjang, "m²", h_grading])
    else:
        p_bongkar = st.sidebar.slider("Persen Bongkaran (%)", 0, 100, 100, key="b_rig")
        show_bongkar = st.sidebar.checkbox("Bongkaran Rigid Eksisting", value=True)
        h_bongkar = st.sidebar.number_input("AHSP Bongkaran Rigid (Rp/m³)", value=450000) if show_bongkar else 0
        if show_bongkar: item_to_add.append([f"Bongkaran Rigid Eksisting ({p_bongkar}%)", (lebar * panjang * t_rigid) * (p_bongkar/100), "m³", h_bongkar])

    show_lc = st.sidebar.checkbox("Lantai Kerja (LC)", value=True)
    h_lc = st.sidebar.number_input("AHSP Lantai Kerja (Rp/m³)", value=950000) if show_lc else 0
    show_bekisting = st.sidebar.checkbox("Bekisting Sisi Jalan", value=True)
    h_bekisting = st.sidebar.number_input("AHSP Bekisting (Rp/m²)", value=125000) if show_bekisting else 0
    show_rigid = st.sidebar.checkbox("Beton Rigid K-350", value=True)
    h_rigid = st.sidebar.number_input("AHSP Beton Rigid (Rp/m³)", value=1450000) if show_rigid else 0
    show_besi = st.sidebar.checkbox("Pembesian (Dowel/Wiremesh)", value=True)
    r_besi = st.sidebar.number_input("Rasio Besi (kg/m³)", value=60) if show_besi else 0
    h_besi = st.sidebar.number_input("AHSP Besi (Rp/kg)", value=18500) if show_besi else 0

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
    p = st.sidebar.number_input("Panjang Plat (m)", value=1.5)
    l = st.sidebar.number_input("Lebar Plat (m)", value=1.5)
    t = st.sidebar.number_input("Tebal Plat (m)", value=0.3)
    jml = st.sidebar.number_input("Jumlah Titik", value=10)
    vol_beton = p * l * t * jml

    st.sidebar.header("Pekerjaan & AHSP")
    if mode_proyek != "Bangunan Baru":
        show_bongkar = st.sidebar.checkbox("Bongkaran Struktur Lama", value=True)
        h_bongkar = st.sidebar.number_input("AHSP Bongkaran (Rp/m³)", value=350000) if show_bongkar else 0
        if show_bongkar: item_to_add.append(["Bongkaran Struktur Lama", vol_beton, "m³", h_bongkar])

    show_galian = st.sidebar.checkbox("Galian Tanah Pondasi", value=True)
    h_galian = st.sidebar.number_input("AHSP Galian (Rp/m³)", value=75000) if show_galian else 0
    show_lc = st.sidebar.checkbox("Lantai Kerja Pondasi", value=True)
    h_lc = st.sidebar.number_input("AHSP Lantai Kerja (Rp/m³)", value=950000) if show_lc else 0
    show_bekisting = st.sidebar.checkbox("Bekisting Plat Pondasi", value=True)
    h_bekisting = st.sidebar.number_input("AHSP Bekisting (Rp/m²)", value=145000) if show_bekisting else 0
    show_cor = st.sidebar.checkbox("Beton Plat Pondasi", value=True)
    h_cor = st.sidebar.number_input("AHSP Beton (Rp/m³)", value=4500000) if show_cor else 0
    show_besi = st.sidebar.checkbox("Pembesian Pondasi", value=True)
    r_besi = st.sidebar.number_input("Rasio Besi (kg/m³)", value=150) if show_besi else 0
    h_besi = st.sidebar.number_input("AHSP Besi (Rp/kg)", value=18500) if show_besi else 0

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
    h = st.sidebar.number_input("Tinggi Dinding (m)", value=4.0)
    l_base = st.sidebar.number_input("Lebar Base (m)", value=2.5)
    panjang = st.sidebar.number_input("Panjang DPT (m)", value=50.0)
    vol_beton = ((0.4 * h) + (l_base * 0.4)) * panjang

    st.sidebar.header("Pekerjaan & AHSP")
    if mode_proyek != "Bangunan Baru":
        show_bongkar = st.sidebar.checkbox("Bongkaran DPT Eksisting", value=True)
        h_bongkar = st.sidebar.number_input("AHSP Bongkaran (Rp/m³)", value=350000) if show_bongkar else 0
        if show_bongkar: item_to_add.append(["Bongkaran DPT Eksisting", vol_beton, "m³", h_bongkar])

    show_galian = st.sidebar.checkbox("Galian Struktur DPT", value=True)
    h_galian = st.sidebar.number_input("AHSP Galian (Rp/m³)", value=75000) if show_galian else 0
    show_bekisting = st.sidebar.checkbox("Bekisting DPT", value=True)
    h_bekisting = st.sidebar.number_input("AHSP Bekisting (Rp/m²)", value=145000) if show_bekisting else 0
    show_cor = st.sidebar.checkbox("Pengecoran Beton DPT", value=True)
    h_cor = st.sidebar.number_input("AHSP Beton (Rp/m³)", value=4200000) if show_cor else 0
    show_besi = st.sidebar.checkbox("Pembesian Struktur DPT", value=True)
    r_besi = st.sidebar.number_input("Rasio Besi (kg/m³)", value=125) if show_besi else 0
    h_besi = st.sidebar.number_input("AHSP Besi (Rp/kg)", value=18500) if show_besi else 0
    show_timbunan = st.sidebar.checkbox("Timbunan Tanah Kembali", value=True)
    h_timbunan = st.sidebar.number_input("AHSP Timbunan (Rp/m³)", value=115000) if show_timbunan else 0

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
    diameter = st.sidebar.number_input("Diameter Pile (m)", value=0.6)
    kedalaman = st.sidebar.number_input("Kedalaman Pile (m)", value=12.0)
    jml_titik = st.sidebar.number_input("Jumlah Titik", value=20, step=1)
    
    area = np.pi * (diameter / 2)**2
    vol_total_beton = area * kedalaman * jml_titik
    vol_pengeboran = area * kedalaman * jml_titik

    st.sidebar.header("Pekerjaan & AHSP")
    if mode_proyek == "Rehabilitasi Struktur":
        show_bongkar = st.sidebar.checkbox("Pembersihan Lokasi/Bongkar Kepala", value=True)
        h_bongkar = st.sidebar.number_input("AHSP Pembersihan (Rp/Titik)", value=500000) if show_bongkar else 0
        if show_bongkar: item_to_add.append(["Pembersihan Lokasi/Bongkar Kepala Pile", jml_titik, "Titik", h_bongkar])

    show_bor = st.sidebar.checkbox("Pengeboran Bore Pile", value=True)
    h_bor = st.sidebar.number_input("AHSP Pengeboran (Rp/m³)", value=450000) if show_bor else 0
    show_casing = st.sidebar.checkbox("Instalasi Temporary Casing", value=True)
    h_casing = st.sidebar.number_input("AHSP Casing (Rp/m')", value=150000) if show_casing else 0
    show_cor = st.sidebar.checkbox("Pengecoran Beton K-350", value=True)
    h_cor = st.sidebar.number_input("AHSP Beton (Rp/m³)", value=1350000) if show_cor else 0
    show_besi = st.sidebar.checkbox("Pembesian Tulangan", value=True)
    r_besi = st.sidebar.number_input("Rasio Besi (kg/m³)", value=180) if show_besi else 0
    h_besi = st.sidebar.number_input("AHSP Besi (Rp/kg)", value=18500) if show_besi else 0

    if show_bor: item_to_add.append(["Pengeboran Bore Pile", vol_pengeboran, "m³", h_bor])
    if show_casing: item_to_add.append(["Instalasi Temporary Casing", diameter * 2 * jml_titik, "m'", h_casing])
    if show_cor: item_to_add.append(["Pengecoran Beton K-350 (Bore Pile)", vol_total_beton, "m³", h_cor])
    if show_besi: item_to_add.append(["Pembesian Tulangan Bore Pile", vol_total_beton * r_besi, "kg", h_besi])

    fig, ax = plt.subplots()
    ax.add_patch(plt.Rectangle((-1, -kedalaman), 2, kedalaman, color='saddlebrown', alpha=0.1))
    ax.add_patch(plt.Rectangle((-diameter/2, -kedalaman), diameter, kedalaman, color='gray'))
    ax.set_xlim(-1, 1); ax.set_ylim(-kedalaman-1, 1); ax.set_aspect('equal')

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
# MASTER RAB FINAL
# =====================================================================
st.divider()
st.header("Laporan Rencana Anggaran Biaya (RAB)")

if st.session_state.rekap_proyek:
    # Urutkan DataFrame berdasarkan Kategori (0, 1, 2, dst agar Persiapan di atas)
    df = pd.DataFrame(st.session_state.rekap_proyek).sort_values(by="Kategori")
    display_data = []
    biaya_langsung = 0

    for kat in df['Kategori'].unique():
        df_kat = df[df['Kategori'] == kat]
        sub = df_kat['Total'].sum()
        biaya_langsung += sub
        
        # Hilangkan angka urutan di tampilan akhir tabel
        nama_kat_bersih = kat.split(". ")[1] if ". " in kat else kat

        for _, row in df_kat.iterrows():
            display_data.append({"Uraian": row['Pekerjaan'], "Volume": f"{row['Volume']} {row['Satuan']}", "Harga": f"Rp {row['AHSP']:,.0f}", "Jumlah": f"Rp {row['Total']:,.0f}"})
        display_data.append({"Uraian": f"SUB-TOTAL {nama_kat_bersih.upper()}", "Volume": "", "Harga": "", "Jumlah": f"Rp {sub:,.0f}"})
        display_data.append({"Uraian": "", "Volume": "", "Harga": "", "Jumlah": ""})

    oh = biaya_langsung * (overhead_pct/100)
    ppn = (biaya_langsung + oh) * (ppn_pct/100)
    total_akhir = biaya_langsung + oh + ppn

    st.dataframe(pd.DataFrame(display_data), use_container_width=True)
    
    st.metric("A. TOTAL BIAYA LANGSUNG", f"Rp {biaya_langsung:,.0f}")
    st.metric(f"B. OVERHEAD & PROFIT ({overhead_pct}%)", f"Rp {oh:,.0f}")
    st.metric(f"C. PPN ({ppn_pct}%)", f"Rp {ppn:,.0f}")
    st.divider()
    st.metric("GRAND TOTAL KONTRAK", f"Rp {total_akhir:,.0f}")

    if st.button("Kosongkan Master Rekap", use_container_width=True):
        st.session_state.rekap_proyek = []; st.rerun()
else:
    st.info("Belum ada data di rekapitulasi.")

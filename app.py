import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Estimator Proyek Terpadu", layout="wide")

if 'rekap_proyek' not in st.session_state:
    st.session_state.rekap_proyek = []

st.title("🏗️ Kalkulator Volume & Biaya Konstruksi Terpadu")
st.write("Dilengkapi Logika Bangunan Baru vs Rehabilitasi, Pembesian, dan Format RAB Profesional.")

# --- SIDEBAR MENU UTAMA ---
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

# --- GLOBAL: KONDISI LAHAN AWAL ---
st.sidebar.title("🌍 Kondisi Lahan Awal")
mode_proyek = st.sidebar.radio(
    "Metode Pelaksanaan:", 
    ["Bangunan Baru (Lahan Kosong/Tanah Asli)", "Rehabilitasi (Ada Bangunan Eksisting)"]
)

st.sidebar.divider()

# --- PENGATURAN KEUANGAN ---
st.sidebar.title("⚙️ Pengaturan Keuangan")
overhead_pct = st.sidebar.number_input("Overhead & Profit (%)", value=10.0, step=1.0)
ppn_pct = st.sidebar.number_input("PPN / Pajak (%)", value=11.0, step=1.0)

st.sidebar.divider()

item_to_add = []
kategori_pekerjaan = jenis_bangunan.split(". ")[1]

# =====================================================================
# 1. LOGIKA SALURAN TRAPESIUM (BETON)
# =====================================================================
if jenis_bangunan == "1. Saluran Trapesium (Beton)":
    st.sidebar.header("📐 Dimensi Saluran")
    lebar_atas = st.sidebar.number_input("Lebar Dalam Atas (m)", value=1.2)
    lebar_bawah = st.sidebar.number_input("Lebar Dalam Bawah (m)", value=0.8)
    tinggi = st.sidebar.number_input("Tinggi Saluran (m)", value=5.0)
    panjang = st.sidebar.number_input("Panjang Saluran (m)", value=100.0)
    t_atas = st.sidebar.number_input("Tebal Dinding Atas (m)", value=0.15)
    t_bawah = st.sidebar.number_input("Tebal Dinding Bawah (m)", value=0.25)
    t_dasar = st.sidebar.number_input("Tebal Pelat Dasar (m)", value=0.30)

    # Perhitungan Geometri
    dist_dalam = (lebar_atas - lebar_bawah) / 2
    sisi_miring = np.sqrt(dist_dalam**2 + tinggi**2)
    vol_beton = (((t_atas + t_bawah) / 2 * sisi_miring * 2) + (lebar_bawah * t_dasar)) * panjang
    vol_tanah_full = (((lebar_atas+(2*t_atas) + lebar_bawah+(2*t_bawah))/2) * (tinggi+t_dasar)) * panjang
    vol_rongga = (((lebar_atas + lebar_bawah) / 2) * tinggi) * panjang

    st.sidebar.header("🛠️ Pekerjaan & AHSP")
    if mode_proyek == "Bangunan Baru (Lahan Kosong/Tanah Asli)":
        show_galian = st.sidebar.checkbox("Galian Tanah Profil", value=True)
        h_galian = st.sidebar.number_input("AHSP Galian (Rp/m³)", value=75000) if show_galian else 0
        if show_galian: item_to_add.append(["Galian Tanah Saluran Baru", vol_tanah_full, "m³", h_galian])
    else:
        show_bongkar = st.sidebar.checkbox("Bongkaran Beton Eksisting", value=True)
        h_bongkar = st.sidebar.number_input("AHSP Bongkaran (Rp/m³)", value=250000) if show_bongkar else 0
        show_sedimen = st.sidebar.checkbox("Galian Sedimen (Normalisasi)", value=True)
        p_sedimen = st.sidebar.slider("Volume Sedimen (%)", 0, 100, 30) if show_sedimen else 0
        h_sedimen = st.sidebar.number_input("AHSP Galian Sedimen (Rp/m³)", value=85000) if show_sedimen else 0
        if show_bongkar: item_to_add.append(["Bongkaran Beton Saluran Lama", vol_beton, "m³", h_bongkar])
        if show_sedimen: item_to_add.append(["Galian Sedimen Saluran", vol_rongga * (p_sedimen/100), "m³", h_sedimen])

    show_cor = st.sidebar.checkbox("Pengecoran Beton", value=True)
    h_cor = st.sidebar.number_input("AHSP Cor Beton (Rp/m³)", value=1200000) if show_cor else 0
    show_besi = st.sidebar.checkbox("Pembesian", value=True)
    r_besi = st.sidebar.number_input("Rasio Besi (kg/m³)", value=110) if show_besi else 0
    h_besi = st.sidebar.number_input("AHSP Besi (Rp/kg)", value=18500) if show_besi else 0

    if show_cor: item_to_add.append(["Pengecoran Beton Saluran", vol_beton, "m³", h_cor])
    if show_besi: item_to_add.append(["Pembesian Saluran", vol_beton * r_besi, "kg", h_besi])

    fig, ax = plt.subplots()
    ax.add_patch(plt.Rectangle((-2, -tinggi-1), 4, tinggi+2, color='saddlebrown', alpha=0.2)) # Ground
    ax.plot([-lebar_atas/2, -lebar_bawah/2, lebar_bawah/2, lebar_atas/2], [0, -tinggi, -tinggi, 0], color='black', lw=2)
    ax.set_title(f"Saluran Trapesium - {mode_proyek.split(' ')[0]}")
    ax.set_aspect('equal')

# =====================================================================
# 2. LOGIKA SALURAN PASANGAN BATU
# =====================================================================
elif jenis_bangunan == "2. Saluran Pasangan Batu (Drainase)":
    st.sidebar.header("📐 Dimensi Drainase")
    lebar_atas = st.sidebar.number_input("Lebar Atas (m)", value=1.0)
    lebar_bawah = st.sidebar.number_input("Lebar Bawah (m)", value=0.6)
    tinggi = st.sidebar.number_input("Tinggi (m)", value=1.2)
    tebal_batu = st.sidebar.number_input("Tebal Pasangan Batu (m)", value=0.25)
    panjang = st.sidebar.number_input("Panjang Saluran (m)", value=100.0)

    dist = (lebar_atas - lebar_bawah) / 2
    vol_galian = (((lebar_atas+(2*tebal_batu)) + (lebar_bawah+(2*tebal_batu)))/2 * (tinggi+tebal_batu)) * panjang
    vol_batu = ((2 * np.sqrt(dist**2 + tinggi**2)) + lebar_bawah) * tebal_batu * panjang
    vol_rongga = (((lebar_atas + lebar_bawah) / 2) * tinggi) * panjang

    st.sidebar.header("🛠️ Pekerjaan & AHSP")
    if mode_proyek == "Bangunan Baru (Lahan Kosong/Tanah Asli)":
        show_galian = st.sidebar.checkbox("Galian Tanah Total", value=True)
        h_galian = st.sidebar.number_input("AHSP Galian (Rp/m³)", value=75000) if show_galian else 0
        if show_galian: item_to_add.append(["Galian Tanah Drainase", vol_galian, "m³", h_galian])
    else:
        show_bongkar = st.sidebar.checkbox("Bongkaran Pasangan Batu Lama", value=True)
        h_bongkar = st.sidebar.number_input("AHSP Bongkaran (Rp/m³)", value=150000) if show_bongkar else 0
        show_sedimen = st.sidebar.checkbox("Galian Sedimen (Normalisasi)", value=True)
        p_sedimen = st.sidebar.slider("Volume Sedimen (%)", 0, 100, 30, key='pb_sed') if show_sedimen else 0
        h_sedimen = st.sidebar.number_input("AHSP Galian Sedimen (Rp/m³)", value=85000, key='pb_sed_h') if show_sedimen else 0
        
        if show_bongkar: item_to_add.append(["Bongkaran Batu Eksisting", vol_batu, "m³", h_bongkar])
        if show_sedimen: item_to_add.append(["Galian Sedimen Drainase", vol_rongga * (p_sedimen/100), "m³", h_sedimen])

    show_pasangan = st.sidebar.checkbox("Pasangan Batu Kali (1:4)", value=True)
    h_pasangan = st.sidebar.number_input("AHSP Pasangan Batu (Rp/m³)", value=950000) if show_pasangan else 0
    if show_pasangan: item_to_add.append(["Pasangan Batu Kali", vol_batu, "m³", h_pasangan])

    fig, ax = plt.subplots()
    ax.plot([0, dist, dist + lebar_bawah, lebar_atas], [0, -tinggi, -tinggi, 0], marker='o', color='black', linewidth=4)
    ax.set_title(f"Drainase Batu - {mode_proyek.split(' ')[0]}")
    ax.set_aspect('equal')

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
        t_base = st.sidebar.number_input("Tebal Base A (m)", value=0.15)
        
        show_grading = st.sidebar.checkbox("Penyiapan Badan Jalan", value=True)
        h_grading = st.sidebar.number_input("AHSP Pemadatan (Rp/m²)", value=12000) if show_grading else 0
        show_base = st.sidebar.checkbox("Lapis Pondasi Agregat", value=True)
        h_base = st.sidebar.number_input("AHSP Agregat A (Rp/m³)", value=450000) if show_base else 0
        
        if show_grading: item_to_add.append(["Penyiapan Badan Jalan", lebar * panjang, "m²", h_grading])
        if show_base: item_to_add.append(["Lapis Pondasi Agregat A", lebar * panjang * t_base, "m³", h_base])
    else:
        st.sidebar.info("Mode Overlay: Melapisi aspal lama yang sudah rusak.")
        show_milling = st.sidebar.checkbox("Kupas Aspal Lama (Cold Milling)", value=True)
        t_milling = st.sidebar.number_input("Tebal Kupasan (m)", value=0.04) if show_milling else 0
        h_milling = st.sidebar.number_input("AHSP Cold Milling (Rp/m²)", value=35000) if show_milling else 0
        
        show_tack = st.sidebar.checkbox("Lapis Perekat (Tack Coat)", value=True)
        h_tack = st.sidebar.number_input("AHSP Tack Coat (Rp/Liter)", value=15000) if show_tack else 0
        vol_tack = (lebar * panjang) * 0.35 # Asumsi 0.35 Liter per m2
        
        if show_milling: item_to_add.append(["Cold Milling Aspal Lama", lebar * panjang * t_milling, "m³", h_milling])
        if show_tack: item_to_add.append(["Lapis Perekat (Tack Coat)", vol_tack, "Liter", h_tack])

    show_aspal = st.sidebar.checkbox("Hampar Aspal (AC-WC)", value=True)
    h_aspal = st.sidebar.number_input("AHSP Aspal (Rp/m³)", value=2500000) if show_aspal else 0
    if show_aspal: item_to_add.append(["Lapis Permukaan AC-WC", lebar * panjang * t_aspal, "m³", h_aspal])

    fig, ax = plt.subplots()
    ax.add_patch(plt.Rectangle((0, -t_aspal), lebar, t_aspal, color='black', label='Aspal Baru'))
    if mode_proyek != "Bangunan Baru (Lahan Kosong/Tanah Asli)":
        ax.add_patch(plt.Rectangle((0, -(t_aspal+0.05)), lebar, 0.05, color='gray', hatch='//', label='Aspal Eksisting'))
    ax.set_xlim(-1, lebar + 1); ax.set_ylim(-0.3, 0.1); ax.set_aspect('equal'); ax.legend()

# =====================================================================
# 4. JALAN PERKERASAN KAKU (RIGID PAVEMENT)
# =====================================================================
elif jenis_bangunan == "4. Jalan Perkerasan Kaku (Rigid)":
    st.sidebar.header("📐 Dimensi Jalan Rigid")
    lebar = st.sidebar.number_input("Lebar Perkerasan (m)", value=5.0)
    panjang = st.sidebar.number_input("Panjang Jalan (m)", value=500.0)
    t_rigid = st.sidebar.number_input("Tebal Beton Rigid (m)", value=0.25)
    t_lc = st.sidebar.number_input("Tebal Lantai Kerja/LC (m)", value=0.10)

    st.sidebar.header("🛠️ Pekerjaan & AHSP")
    if mode_proyek == "Bangunan Baru (Lahan Kosong/Tanah Asli)":
        show_grading = st.sidebar.checkbox("Penyiapan Badan Jalan", value=True)
        h_grading = st.sidebar.number_input("AHSP Penyiapan (Rp/m²)", value=12000) if show_grading else 0
        if show_grading: item_to_add.append(["Penyiapan Badan Jalan", lebar * panjang, "m²", h_grading])
    else:
        show_bongkar = st.sidebar.checkbox("Bongkaran Rigid Lama (Breaker)", value=True)
        h_bongkar = st.sidebar.number_input("AHSP Bongkaran Rigid (Rp/m³)", value=450000) if show_bongkar else 0
        if show_bongkar: item_to_add.append(["Bongkaran Beton Rigid Lama", lebar * panjang * t_rigid, "m³", h_bongkar])

    show_lc = st.sidebar.checkbox("Lantai Kerja (LC)", value=True)
    h_lc = st.sidebar.number_input("AHSP Lantai Kerja (Rp/m³)", value=950000) if show_lc else 0
    show_rigid = st.sidebar.checkbox("Beton Rigid", value=True)
    h_rigid = st.sidebar.number_input("AHSP Beton Rigid (Rp/m³)", value=1450000) if show_rigid else 0
    show_besi = st.sidebar.checkbox("Pembesian (Dowel/Tie-bar)", value=True)
    h_besi = st.sidebar.number_input("AHSP Besi (Rp/kg)", value=18500) if show_besi else 0

    if show_lc: item_to_add.append(["Lantai Kerja (LC)", lebar * panjang * t_lc, "m³", h_lc])
    if show_rigid: item_to_add.append(["Beton Rigid K-350", lebar * panjang * t_rigid, "m³", h_rigid])
    if show_besi: item_to_add.append(["Pembesian Dowel/Tie-bar", (lebar * panjang * t_rigid) * 60, "kg", h_besi])

    fig, ax = plt.subplots()
    ax.add_patch(plt.Rectangle((0, 0), lebar, t_rigid, color='lightgray', ec='black', hatch='//'))
    ax.set_xlim(-1, lebar + 1); ax.set_ylim(-0.2, 0.4); ax.set_aspect('equal')

# =====================================================================
# 5. PONDASI TELAPAK
# =====================================================================
elif jenis_bangunan == "5. Pondasi Telapak":
    st.sidebar.header("📐 Dimensi Pondasi")
    p_telapak = st.sidebar.number_input("Panjang (m)", value=1.5)
    l_telapak = st.sidebar.number_input("Lebar (m)", value=1.5)
    t_telapak = st.sidebar.number_input("Tebal Plat (m)", value=0.3)
    jml_titik = st.sidebar.number_input("Jumlah Titik", value=10)
    vol_beton = (p_telapak * l_telapak * t_telapak) * jml_titik
    vol_galian = (p_telapak + 0.4) * (l_telapak + 0.4) * t_telapak * jml_titik # space kerja

    st.sidebar.header("🛠️ Pekerjaan & AHSP")
    if mode_proyek != "Bangunan Baru (Lahan Kosong/Tanah Asli)":
        show_bongkar = st.sidebar.checkbox("Bongkaran Struktur Lama", value=True)
        h_bongkar = st.sidebar.number_input("AHSP Bongkaran (Rp/m³)", value=350000) if show_bongkar else 0
        if show_bongkar: item_to_add.append(["Bongkaran Pondasi Eksisting", vol_beton, "m³", h_bongkar])

    show_galian = st.sidebar.checkbox("Galian Tanah Pondasi", value=True)
    h_galian = st.sidebar.number_input("AHSP Galian (Rp/m³)", value=75000) if show_galian else 0
    show_cor = st.sidebar.checkbox("Beton Bertulang", value=True)
    h_cor = st.sidebar.number_input("AHSP Beton (Rp/m³)", value=4500000) if show_cor else 0
    show_besi = st.sidebar.checkbox("Pembesian Pondasi", value=True)
    h_besi = st.sidebar.number_input("AHSP Besi (Rp/kg)", value=18500) if show_besi else 0

    if show_galian: item_to_add.append(["Galian Tanah Titik Pondasi", vol_galian, "m³", h_galian])
    if show_cor: item_to_add.append(["Beton Plat Pondasi", vol_beton, "m³", h_cor])
    if show_besi: item_to_add.append(["Pembesian Pondasi", vol_beton * 150, "kg", h_besi])

    fig, ax = plt.subplots()
    ax.add_patch(plt.Rectangle((-(p_telapak/2), 0), p_telapak, t_telapak, color='gray'))
    ax.set_xlim(-2, 2); ax.set_ylim(-0.5, 1); ax.set_aspect('equal')

# =====================================================================
# 6. DINDING PENAHAN TANAH
# =====================================================================
elif jenis_bangunan == "6. Dinding Penahan Tanah (Kantilever)":
    st.sidebar.header("📐 Dimensi Dinding")
    tinggi = st.sidebar.number_input("Tinggi Dinding (m)", value=4.0)
    lebar_base = st.sidebar.number_input("Lebar Dasar (m)", value=2.5)
    panjang = st.sidebar.number_input("Panjang Total (m)", value=50.0)
    vol_beton = ((0.4 * tinggi) + (lebar_base * 0.4)) * panjang
    vol_galian = lebar_base * 1.0 * panjang # Asumsi kedalaman galian 1m

    st.sidebar.header("🛠️ Pekerjaan & AHSP")
    if mode_proyek != "Bangunan Baru (Lahan Kosong/Tanah Asli)":
        show_bongkar = st.sidebar.checkbox("Bongkaran DPT Lama", value=True)
        h_bongkar = st.sidebar.number_input("AHSP Bongkaran (Rp/m³)", value=350000) if show_bongkar else 0
        if show_bongkar: item_to_add.append(["Bongkaran DPT Eksisting", vol_beton, "m³", h_bongkar])

    show_galian = st.sidebar.checkbox("Galian & Backfill", value=True)
    h_galian = st.sidebar.number_input("AHSP Galian (Rp/m³)", value=75000) if show_galian else 0
    show_cor = st.sidebar.checkbox("Beton Dinding & Base", value=True)
    h_cor = st.sidebar.number_input("AHSP Beton (Rp/m³)", value=4200000) if show_cor else 0
    show_besi = st.sidebar.checkbox("Pembesian DPT", value=True)
    h_besi = st.sidebar.number_input("AHSP Besi (Rp/kg)", value=18500) if show_besi else 0

    if show_galian: item_to_add.append(["Galian Tanah DPT", vol_galian, "m³", h_galian])
    if show_cor: item_to_add.append(["Pengecoran Beton DPT", vol_beton, "m³", h_cor])
    if show_besi: item_to_add.append(["Pembesian Struktur DPT", vol_beton * 125, "kg", h_besi])

    fig, ax = plt.subplots()
    ax.add_patch(plt.Rectangle((0, -0.4), lebar_base, 0.4, color='gray'))
    ax.add_patch(plt.Rectangle((0.5, 0), 0.4, tinggi, color='gray'))
    ax.set_xlim(-1, lebar_base + 1); ax.set_ylim(-1, tinggi + 1); ax.set_aspect('equal')

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
            st.success("Berhasil ditambahkan!")

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

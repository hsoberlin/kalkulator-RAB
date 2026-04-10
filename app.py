import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Estimator Proyek Terpadu", layout="wide")

# --- INISIALISASI SESSION STATE ---
if 'rekap_proyek' not in st.session_state:
    st.session_state.rekap_proyek = []

st.title("🏗️ Kalkulator Volume & Biaya Konstruksi Terpadu")
st.write("Dilengkapi dengan detail Pekerjaan Persiapan, Ketebalan Dinamis, dan Format RAB Profesional.")

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

item_to_add = []
kategori_pekerjaan = jenis_bangunan.split(". ")[1]

# =====================================================================
# 1. LOGIKA SALURAN TRAPESIUM (BETON) - KETEBALAN DINAMIS
# =====================================================================
if jenis_bangunan == "1. Saluran Trapesium (Beton)":
    st.sidebar.header("📐 Dimensi Saluran")
    lebar_atas = st.sidebar.number_input("Lebar Dalam Atas (m)", value=1.2)
    lebar_bawah = st.sidebar.number_input("Lebar Dalam Bawah (m)", value=0.8)
    tinggi = st.sidebar.number_input("Tinggi Saluran (m)", value=5.0)
    panjang = st.sidebar.number_input("Panjang Saluran (m)", value=100.0)
    
    st.sidebar.subheader("Ketebalan Beton")
    t_atas = st.sidebar.number_input("Tebal Dinding Atas (m)", value=0.15)
    t_bawah = st.sidebar.number_input("Tebal Dinding Bawah (m)", value=0.25)
    t_dasar = st.sidebar.number_input("Tebal Pelat Dasar (m)", value=0.30)

    st.sidebar.header("🛠️ Pilih Pekerjaan & AHSP")
    show_galian = st.sidebar.checkbox("Galian Tanah (Sesuai Profil Luar)", value=True)
    h_galian = st.sidebar.number_input("AHSP Galian (Rp/m³)", value=75000, step=5000) if show_galian else 0
    
    show_cor = st.sidebar.checkbox("Pengecoran Beton Dinding & Dasar", value=True)
    h_cor = st.sidebar.number_input("AHSP Cor (Rp/m³)", value=1200000, step=50000) if show_cor else 0

    # Perhitungan Volume
    dist_dalam = (lebar_atas - lebar_bawah) / 2
    sisi_miring = np.sqrt(dist_dalam**2 + tinggi**2)
    
    # Luas penampang beton = (2 x luas trapesium dinding) + luas persegi panjang dasar
    luas_dinding_satu_sisi = sisi_miring * ((t_atas + t_bawah) / 2)
    luas_dasar = lebar_bawah * t_dasar
    vol_beton = ((2 * luas_dinding_satu_sisi) + luas_dasar) * panjang
    
    # Galian tanah dihitung dari dimensi TERLUAR beton
    l_luar_atas = lebar_atas + (2 * t_atas)
    l_luar_bawah = lebar_bawah + (2 * t_bawah)
    vol_tanah = (((l_luar_atas + l_luar_bawah) / 2) * (tinggi + t_dasar)) * panjang

    if show_galian: item_to_add.append(["Galian Tanah Profil", vol_tanah, "m³", h_galian])
    if show_cor: item_to_add.append(["Pengecoran Beton", vol_beton, "m³", h_cor])

    # Visualisasi (Koordinat di-center di X=0 agar simetris)
    fig, ax = plt.subplots()
    
    # Polygon Luar (Batas Tanah/Galian)
    x_luar = [-(l_luar_atas/2), -(l_luar_bawah/2), (l_luar_bawah/2), (l_luar_atas/2)]
    y_luar = [0, -(tinggi + t_dasar), -(tinggi + t_dasar), 0]
    ax.fill(x_luar, y_luar, color='saddlebrown', alpha=0.3, label='Galian Tanah')
    
    # Polygon Penampang Beton
    x_beton_luar = x_luar
    y_beton_luar = y_luar
    x_beton_dalam = [-(lebar_atas/2), -(lebar_bawah/2), (lebar_bawah/2), (lebar_atas/2)]
    y_beton_dalam = [0, -tinggi, -tinggi, 0]
    
    # Gambar outline
    ax.plot(x_luar, y_luar, color='black', linewidth=1)
    ax.plot(x_beton_dalam, y_beton_dalam, color='black', linewidth=1)
    
    # Fill rongga di antara garis luar dan dalam
    ax.fill_between(x_luar[:2], y_luar[:2], y_beton_dalam[:2], color='gray', alpha=0.8, label='Beton')
    ax.fill_between(x_luar[2:], y_luar[2:], y_beton_dalam[2:], color='gray', alpha=0.8)
    ax.fill_between([-(l_luar_bawah/2), (l_luar_bawah/2)], [-(tinggi + t_dasar), -(tinggi + t_dasar)], [-tinggi, -tinggi], color='gray', alpha=0.8)

    ax.set_aspect('equal')
    ax.legend()
    ax.set_title("Profil Saluran Trapesium (Tebal Variabel)")

# =====================================================================
# 2. LOGIKA SALURAN PASANGAN BATU
# =====================================================================
elif jenis_bangunan == "2. Saluran Pasangan Batu (Drainase)":
    # (Kode tetap sama seperti versi sebelumnya)
    st.sidebar.header("📐 Dimensi Drainase")
    lebar_atas = st.sidebar.number_input("Lebar Atas (m)", value=1.0)
    lebar_bawah = st.sidebar.number_input("Lebar Bawah (m)", value=0.6)
    tinggi = st.sidebar.number_input("Tinggi (m)", value=1.2)
    tebal_batu = st.sidebar.number_input("Tebal Pasangan Batu (m)", value=0.25)
    panjang = st.sidebar.number_input("Panjang Saluran (m)", value=100.0)

    st.sidebar.header("🛠️ Pilih Pekerjaan & AHSP")
    show_galian = st.sidebar.checkbox("Galian Tanah", value=True)
    h_galian = st.sidebar.number_input("AHSP Galian (Rp/m³)", value=75000) if show_galian else 0
    show_pasangan = st.sidebar.checkbox("Pasangan Batu Kali (1:4)", value=True)
    h_pasangan = st.sidebar.number_input("AHSP Pasangan Batu (Rp/m³)", value=950000) if show_pasangan else 0

    dist = (lebar_atas - lebar_bawah) / 2
    keliling_dalam = (2 * np.sqrt(dist**2 + tinggi**2)) + lebar_bawah
    vol_galian = (((lebar_atas+(2*tebal_batu)) + (lebar_bawah+(2*tebal_batu)))/2 * (tinggi+tebal_batu)) * panjang
    vol_batu = keliling_dalam * tebal_batu * panjang

    if show_galian: item_to_add.append(["Galian Tanah Drainase", vol_galian, "m³", h_galian])
    if show_pasangan: item_to_add.append(["Pasangan Batu Kali", vol_batu, "m³", h_pasangan])

    fig, ax = plt.subplots()
    x_coords = [0, dist, dist + lebar_bawah, lebar_atas]
    y_coords = [0, -tinggi, -tinggi, 0]
    ax.plot(x_coords, y_coords, marker='o', color='black', linewidth=4)
    ax.set_aspect('equal')
    ax.set_title("Saluran Pasangan Batu")

# =====================================================================
# 3. JALAN PERKERASAN LENTUR (ASPAL) - DENGAN PERSIAPAN
# =====================================================================
elif jenis_bangunan == "3. Jalan Perkerasan Lentur (Aspal)":
    st.sidebar.header("📐 Dimensi Jalan")
    lebar = st.sidebar.number_input("Lebar Jalan (m)", value=6.0)
    panjang = st.sidebar.number_input("Panjang Jalan (m)", value=1000.0)
    t_aspal = st.sidebar.number_input("Tebal Aspal (m)", value=0.05)
    t_base = st.sidebar.number_input("Tebal Lapis Pondasi (m)", value=0.15)

    st.sidebar.header("🚜 Pekerjaan Persiapan")
    show_kupas = st.sidebar.checkbox("Kupas Tanah / Galian Existing", value=False)
    t_kupas = st.sidebar.number_input("Tebal Kupasan (m)", value=0.20) if show_kupas else 0
    h_kupas = st.sidebar.number_input("AHSP Kupas (Rp/m³)", value=45000) if show_kupas else 0
    
    show_grading = st.sidebar.checkbox("Penyiapan Badan Jalan (Pemadatan)", value=True)
    h_grading = st.sidebar.number_input("AHSP Pemadatan (Rp/m²)", value=12000) if show_grading else 0

    st.sidebar.header("🛠️ Pekerjaan Perkerasan")
    show_base = st.sidebar.checkbox("Lapis Pondasi (Agregat A)", value=True)
    h_base = st.sidebar.number_input("AHSP Agregat A (Rp/m³)", value=450000) if show_base else 0
    show_aspal = st.sidebar.checkbox("Aspal (AC-WC)", value=True)
    h_aspal = st.sidebar.number_input("AHSP Aspal AC-WC (Rp/m³)", value=2500000) if show_aspal else 0

    if show_kupas: item_to_add.append(["Kupas Tanah Existing", lebar * panjang * t_kupas, "m³", h_kupas])
    if show_grading: item_to_add.append(["Penyiapan Badan Jalan", lebar * panjang, "m²", h_grading])
    if show_base: item_to_add.append(["Lapis Pondasi Agregat A", lebar * panjang * t_base, "m³", h_base])
    if show_aspal: item_to_add.append(["Lapis Permukaan AC-WC", lebar * panjang * t_aspal, "m³", h_aspal])

    fig, ax = plt.subplots()
    if show_kupas: ax.add_patch(plt.Rectangle((0, -(t_aspal+t_base+t_kupas)), lebar, t_kupas, color='saddlebrown', alpha=0.3, label='Kupasan'))
    ax.add_patch(plt.Rectangle((0, -t_aspal), lebar, t_aspal, color='black', alpha=0.8, label='Aspal'))
    ax.add_patch(plt.Rectangle((0, -(t_aspal+t_base)), lebar, t_base, color='gray', alpha=0.5, label='Base A'))
    ax.set_xlim(-0.5, lebar + 0.5)
    ax.set_ylim(-(t_aspal+t_base+t_kupas) - 0.1, 0.1)
    ax.set_aspect('equal')
    ax.legend()
    ax.set_title("Penampang Jalan Lentur")

# =====================================================================
# 4. JALAN PERKERASAN KAKU (RIGID PAVEMENT) - DENGAN PERSIAPAN
# =====================================================================
elif jenis_bangunan == "4. Jalan Perkerasan Kaku (Rigid)":
    st.sidebar.header("📐 Dimensi Jalan Rigid")
    lebar = st.sidebar.number_input("Lebar Perkerasan (m)", value=5.0)
    panjang = st.sidebar.number_input("Panjang Jalan (m)", value=500.0)
    t_rigid = st.sidebar.number_input("Tebal Beton Rigid (m)", value=0.25)
    t_lc = st.sidebar.number_input("Tebal Lantai Kerja/LC (m)", value=0.10)

    st.sidebar.header("🚜 Pekerjaan Persiapan")
    show_grading = st.sidebar.checkbox("Penyiapan Badan Jalan", value=True)
    h_grading = st.sidebar.number_input("AHSP Penyiapan (Rp/m²)", value=12000) if show_grading else 0

    st.sidebar.header("🛠️ Pekerjaan Perkerasan")
    show_lc = st.sidebar.checkbox("Lantai Kerja (Lean Concrete)", value=True)
    h_lc = st.sidebar.number_input("AHSP Lantai Kerja (Rp/m³)", value=950000) if show_lc else 0
    show_rigid = st.sidebar.checkbox("Beton Rigid", value=True)
    h_rigid = st.sidebar.number_input("AHSP Beton Rigid (Rp/m³)", value=1450000) if show_rigid else 0

    if show_grading: item_to_add.append(["Penyiapan Badan Jalan", lebar * panjang, "m²", h_grading])
    if show_lc: item_to_add.append(["Lantai Kerja (LC)", lebar * panjang * t_lc, "m³", h_lc])
    if show_rigid: item_to_add.append(["Beton Rigid", lebar * panjang * t_rigid, "m³", h_rigid])

    fig, ax = plt.subplots()
    ax.add_patch(plt.Rectangle((0, 0), lebar, t_rigid, color='lightgray', ec='black', hatch='//', label='Beton Rigid'))
    ax.add_patch(plt.Rectangle((0, -t_lc), lebar, t_lc, color='orange', alpha=0.4, label='Lantai Kerja'))
    ax.set_xlim(-0.5, lebar + 0.5)
    ax.set_ylim(-t_lc - 0.1, t_rigid + 0.1)
    ax.set_aspect('equal')
    ax.legend()
    ax.set_title("Penampang Jalan Kaku")

# =====================================================================
# 5 & 6 (PONDASI & DINDING PENAHAN - Logika standar disederhanakan untuk space)
# =====================================================================
else:
    st.info("Pilih Saluran atau Jalan di Sidebar untuk melihat update fitur terbaru.")
    fig, ax = plt.subplots()

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
    
    st.info(f"**Total Sub-Pekerjaan Ini: Rp {total_preview:,.0f}**")
    
    if len(item_to_add) > 0:
        if st.button("➕ TAMBAHKAN KE MASTER REKAP", use_container_width=True):
            for item in item_to_add:
                nama, vol, sat, ahsp = item
                st.session_state.rekap_proyek.append({
                    "Kategori": kategori_pekerjaan,
                    "Pekerjaan": nama,
                    "Volume": round(vol, 2),
                    "Satuan": sat,
                    "AHSP": ahsp,
                    "Total Biaya": vol * ahsp
                })
            st.success("Berhasil ditambahkan!")

with col2:
    st.pyplot(fig)

# =====================================================================
# MASTER REKAPITULASI BIAYA (DENGAN BARIS SUB-TOTAL)
# =====================================================================
st.divider()
st.header("🛒 Master Rekapitulasi Proyek (RAB)")

if st.session_state.rekap_proyek:
    df_rekap = pd.DataFrame(st.session_state.rekap_proyek)
    
    # 1. Menyiapkan Tabel RAB dengan Baris Pemisah (Sub-Total)
    rab_display_data = []
    kategori_unik = df_rekap['Kategori'].unique()

    for kat in kategori_unik:
        df_kat = df_rekap[df_rekap['Kategori'] == kat]
        subtotal_kat = df_kat['Total Biaya'].sum()
        
        # Masukkan item pekerjaan aslinya
        for _, row in df_kat.iterrows():
            rab_display_data.append({
                "Kategori": row['Kategori'],
                "Uraian Pekerjaan": row['Pekerjaan'],
                "Volume": f"{row['Volume']} {row['Satuan']}",
                "Harga Satuan": f"Rp {row['AHSP']:,.0f}",
                "Jumlah Harga": f"Rp {row['Total Biaya']:,.0f}"
            })
        
        # Tambahkan Baris SUB-TOTAL
        rab_display_data.append({
            "Kategori": "",
            "Uraian Pekerjaan": f"➡️ SUB-TOTAL {kat.upper()}",
            "Volume": "",
            "Harga Satuan": "",
            "Jumlah Harga": f"Rp {subtotal_kat:,.0f}"
        })
        
        # Tambahkan Baris Kosong untuk Jarak antar kategori
        rab_display_data.append({
            "Kategori": "", "Uraian Pekerjaan": "", "Volume": "", "Harga Satuan": "", "Jumlah Harga": ""
        })

    # Tampilkan DataFrame
    st.subheader("📋 Format Laporan Rencana Anggaran Biaya")
    df_rab_final = pd.DataFrame(rab_display_data)
    
    # Gunakan st.dataframe agar tabel rapi
    st.dataframe(df_rab_final, use_container_width=True)
    
    # 2. Grand Total Keseluruhan
    grand_total = df_rekap["Total Biaya"].sum()
    st.metric("💰 GRAND TOTAL KESELURUHAN", f"Rp {grand_total:,.0f}")
    
    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("🗑️ Kosongkan Master Rekap"):
            st.session_state.rekap_proyek = []
            st.rerun()
else:
    st.info("Belum ada data di rekapitulasi. Silakan proses perhitungan di atas lalu klik 'Tambahkan ke Master Rekap'.")

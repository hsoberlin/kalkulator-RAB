import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Estimator Proyek Terpadu", layout="wide")

if 'rekap_proyek' not in st.session_state:
    st.session_state.rekap_proyek = []

st.title("🏗️ Kalkulator Volume & Biaya Konstruksi Terpadu")
st.write("Hitung detail per item pekerjaan, visualisasikan, dan tambahkan ke Master Rekapitulasi Proyek.")

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
# 1. LOGIKA SALURAN TRAPESIUM (BETON)
# =====================================================================
if jenis_bangunan == "1. Saluran Trapesium (Beton)":
    st.sidebar.header("📐 Dimensi Saluran")
    lebar_atas = st.sidebar.number_input("Lebar Atas (m)", value=1.2)
    lebar_bawah = st.sidebar.number_input("Lebar Bawah (m)", value=0.8)
    tinggi = st.sidebar.number_input("Tinggi (m)", value=5.0)
    tebal_beton = st.sidebar.number_input("Tebal Beton (m)", value=0.2)
    panjang = st.sidebar.number_input("Panjang Saluran (m)", value=100.0)

    st.sidebar.header("🛠️ Pilih Pekerjaan & AHSP")
    show_bongkar = st.sidebar.checkbox("Bongkaran Beton Eksisting", value=True)
    h_bongkar = st.sidebar.number_input("AHSP Bongkaran (Rp/m³)", value=250000, step=10000) if show_bongkar else 0
    
    show_galian = st.sidebar.checkbox("Galian Tanah", value=True)
    h_galian = st.sidebar.number_input("AHSP Galian (Rp/m³)", value=75000, step=5000) if show_galian else 0
    
    show_cor = st.sidebar.checkbox("Pengecoran Beton", value=True)
    h_cor = st.sidebar.number_input("AHSP Cor (Rp/m³)", value=1200000, step=50000) if show_cor else 0

    dist = (lebar_atas - lebar_bawah) / 2
    keliling = (2 * np.sqrt(dist**2 + tinggi**2)) + lebar_bawah
    
    vol_beton = keliling * tebal_beton * panjang
    vol_tanah = ((lebar_atas + lebar_bawah) / 2 * tinggi) * panjang

    if show_bongkar: item_to_add.append(["Bongkaran Beton", vol_beton, "m³", h_bongkar])
    if show_galian: item_to_add.append(["Galian Tanah", vol_tanah, "m³", h_galian])
    if show_cor: item_to_add.append(["Pengecoran Beton", vol_beton, "m³", h_cor])

    fig, ax = plt.subplots()
    x_coords = [0, dist, dist + lebar_bawah, lebar_atas]
    y_coords = [0, -tinggi, -tinggi, 0]
    ax.plot(x_coords, y_coords, marker='o', color='brown', linewidth=2)
    ax.fill(x_coords, y_coords, color='cyan', alpha=0.3)
    ax.set_aspect('equal')
    ax.set_title("Saluran Trapesium Beton")

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

    st.sidebar.header("🛠️ Pilih Pekerjaan & AHSP")
    show_galian = st.sidebar.checkbox("Galian Tanah", value=True)
    h_galian = st.sidebar.number_input("AHSP Galian (Rp/m³)", value=75000, step=5000) if show_galian else 0
    
    show_pasangan = st.sidebar.checkbox("Pasangan Batu Kali (1:4)", value=True)
    h_pasangan = st.sidebar.number_input("AHSP Pasangan Batu (Rp/m³)", value=950000, step=10000) if show_pasangan else 0
    
    show_plesteran = st.sidebar.checkbox("Plesteran & Acian", value=True)
    h_plesteran = st.sidebar.number_input("AHSP Plesteran (Rp/m²)", value=65000, step=5000) if show_plesteran else 0

    dist = (lebar_atas - lebar_bawah) / 2
    keliling_dalam = (2 * np.sqrt(dist**2 + tinggi**2)) + lebar_bawah
    
    vol_galian = (((lebar_atas+(2*tebal_batu)) + (lebar_bawah+(2*tebal_batu)))/2 * (tinggi+tebal_batu)) * panjang
    vol_batu = keliling_dalam * tebal_batu * panjang
    luas_plesteran = keliling_dalam * panjang

    if show_galian: item_to_add.append(["Galian Tanah Drainase", vol_galian, "m³", h_galian])
    if show_pasangan: item_to_add.append(["Pasangan Batu Kali", vol_batu, "m³", h_pasangan])
    if show_plesteran: item_to_add.append(["Plesteran Permukaan", luas_plesteran, "m²", h_plesteran])

    fig, ax = plt.subplots()
    x_coords = [0, dist, dist + lebar_bawah, lebar_atas]
    y_coords = [0, -tinggi, -tinggi, 0]
    ax.plot(x_coords, y_coords, marker='o', color='black', linewidth=4, label='Pasangan Batu')
    ax.fill(x_coords, y_coords, color='blue', alpha=0.1)
    ax.set_aspect('equal')
    ax.set_title("Saluran Pasangan Batu")

# =====================================================================
# 3. LOGIKA JALAN PERKERASAN LENTUR (ASPAL)
# =====================================================================
elif jenis_bangunan == "3. Jalan Perkerasan Lentur (Aspal)":
    st.sidebar.header("📐 Dimensi Jalan")
    lebar = st.sidebar.number_input("Lebar Jalan (m)", value=6.0)
    panjang = st.sidebar.number_input("Panjang Jalan (m)", value=1000.0)
    t_aspal = st.sidebar.number_input("Tebal Aspal (m)", value=0.05)
    t_base = st.sidebar.number_input("Tebal Lapis Pondasi Atas (m)", value=0.15)

    st.sidebar.header("🛠️ Pilih Pekerjaan & AHSP")
    show_base = st.sidebar.checkbox("Lapis Pondasi (Agregat A)", value=True)
    h_base = st.sidebar.number_input("AHSP Agregat A (Rp/m³)", value=450000, step=10000) if show_base else 0
    
    show_aspal = st.sidebar.checkbox("Aspal (AC-WC)", value=True)
    h_aspal = st.sidebar.number_input("AHSP Aspal AC-WC (Rp/m³)", value=2500000, step=50000) if show_aspal else 0

    vol_base = lebar * panjang * t_base
    vol_aspal = lebar * panjang * t_aspal

    if show_base: item_to_add.append(["Lapis Pondasi Agregat A", vol_base, "m³", h_base])
    if show_aspal: item_to_add.append(["Lapis Permukaan AC-WC", vol_aspal, "m³", h_aspal])

    fig, ax = plt.subplots()
    ax.add_patch(plt.Rectangle((0, -t_aspal), lebar, t_aspal, color='black', alpha=0.8, label='Aspal'))
    ax.add_patch(plt.Rectangle((0, -(t_aspal+t_base)), lebar, t_base, color='gray', alpha=0.5, label='Base A'))
    ax.set_xlim(-0.5, lebar + 0.5)
    ax.set_ylim(-(t_aspal+t_base) - 0.1, 0.1)
    ax.set_aspect('equal')
    ax.legend()

# =====================================================================
# 4. LOGIKA JALAN PERKERASAN KAKU (RIGID PAVEMENT)
# =====================================================================
elif jenis_bangunan == "4. Jalan Perkerasan Kaku (Rigid)":
    st.sidebar.header("📐 Dimensi Jalan Rigid")
    lebar = st.sidebar.number_input("Lebar Perkerasan (m)", value=5.0)
    panjang = st.sidebar.number_input("Panjang Jalan (m)", value=500.0)
    t_rigid = st.sidebar.number_input("Tebal Beton Rigid (m)", value=0.25)
    t_lc = st.sidebar.number_input("Tebal Lantai Kerja/LC (m)", value=0.10)

    st.sidebar.header("🛠️ Pilih Pekerjaan & AHSP")
    show_lc = st.sidebar.checkbox("Lantai Kerja (Lean Concrete)", value=True)
    h_lc = st.sidebar.number_input("AHSP Lantai Kerja (Rp/m³)", value=950000, step=10000) if show_lc else 0
    
    show_rigid = st.sidebar.checkbox("Beton Rigid (K-350 / FS 45)", value=True)
    h_rigid = st.sidebar.number_input("AHSP Beton Rigid (Rp/m³)", value=1450000, step=50000) if show_rigid else 0

    show_bekisting = st.sidebar.checkbox("Bekisting Jalan", value=True)
    h_bekisting = st.sidebar.number_input("AHSP Bekisting (Rp/m²)", value=120000, step=5000) if show_bekisting else 0

    vol_lc = lebar * panjang * t_lc
    vol_rigid = lebar * panjang * t_rigid
    luas_bekisting = (t_rigid + t_lc) * panjang * 2

    if show_lc: item_to_add.append(["Lantai Kerja (Lean Concrete)", vol_lc, "m³", h_lc])
    if show_rigid: item_to_add.append(["Beton Rigid", vol_rigid, "m³", h_rigid])
    if show_bekisting: item_to_add.append(["Bekisting Sisi Jalan", luas_bekisting, "m²", h_bekisting])

    fig, ax = plt.subplots()
    ax.add_patch(plt.Rectangle((0, 0), lebar, t_rigid, color='lightgray', ec='black', hatch='//', label='Beton Rigid'))
    ax.add_patch(plt.Rectangle((0, -t_lc), lebar, t_lc, color='orange', alpha=0.4, label='Lantai Kerja (LC)'))
    ax.set_xlim(-0.5, lebar + 0.5)
    ax.set_ylim(-t_lc - 0.1, t_rigid + 0.1)
    ax.set_aspect('equal')
    ax.legend()
    ax.set_title("Potongan Jalan Rigid Pavement")

# =====================================================================
# 5. LOGIKA PONDASI TELAPAK
# =====================================================================
elif jenis_bangunan == "5. Pondasi Telapak":
    st.sidebar.header("📐 Dimensi Pondasi")
    p_telapak = st.sidebar.number_input("Panjang (m)", value=1.5)
    l_telapak = st.sidebar.number_input("Lebar (m)", value=1.5)
    t_telapak = st.sidebar.number_input("Tebal Plat (m)", value=0.3)
    jml_titik = st.sidebar.number_input("Jumlah Titik", value=10, step=1)

    st.sidebar.header("🛠️ Pilih Pekerjaan & AHSP")
    show_galian = st.sidebar.checkbox("Galian Pondasi", value=True)
    h_galian = st.sidebar.number_input("AHSP Galian (Rp/m³)", value=75000, step=5000) if show_galian else 0
    
    show_cor = st.sidebar.checkbox("Beton Bertulang", value=True)
    h_cor = st.sidebar.number_input("AHSP Beton (Rp/m³)", value=4500000, step=50000) if show_cor else 0

    vol_galian = (p_telapak + 0.2) * (l_telapak + 0.2) * t_telapak * jml_titik
    vol_beton = (p_telapak * l_telapak * t_telapak) * jml_titik

    if show_galian: item_to_add.append(["Galian Tanah Pondasi", vol_galian, "m³", h_galian])
    if show_cor: item_to_add.append(["Beton Plat Pondasi", vol_beton, "m³", h_cor])

    fig, ax = plt.subplots()
    ax.add_patch(plt.Rectangle((-(p_telapak/2), 0), p_telapak, t_telapak, color='gray', alpha=0.8))
    ax.set_xlim(-(p_telapak/2) - 0.5, (p_telapak/2) + 0.5)
    ax.set_ylim(-0.2, t_telapak + 0.5)
    ax.set_aspect('equal')
    ax.set_title("Pondasi Telapak")

# =====================================================================
# 6. LOGIKA DINDING PENAHAN TANAH (KANTILEVER)
# =====================================================================
elif jenis_bangunan == "6. Dinding Penahan Tanah (Kantilever)":
    st.sidebar.header("📐 Dimensi Dinding Penahan")
    tinggi_dinding = st.sidebar.number_input("Tinggi Dinding/Stem (m)", value=4.0)
    tebal_atas = st.sidebar.number_input("Tebal Dinding Atas (m)", value=0.3)
    tebal_bawah = st.sidebar.number_input("Tebal Dinding Bawah (m)", value=0.5)
    lebar_pelat = st.sidebar.number_input("Lebar Pelat Dasar/Base (m)", value=2.5)
    tebal_pelat = st.sidebar.number_input("Tebal Pelat Dasar (m)", value=0.4)
    lebar_heel = st.sidebar.number_input("Lebar Heel (Belakang Dinding) (m)", value=1.2)
    panjang_dpt = st.sidebar.number_input("Panjang Total Dinding (m)", value=50.0)

    st.sidebar.header("🛠️ Pilih Pekerjaan & AHSP")
    show_galian = st.sidebar.checkbox("Galian Tanah Dasar", value=True)
    h_galian = st.sidebar.number_input("AHSP Galian (Rp/m³)", value=75000, step=5000) if show_galian else 0
    
    show_cor = st.sidebar.checkbox("Beton Bertulang (Dinding + Pelat)", value=True)
    h_cor = st.sidebar.number_input("AHSP Beton Bertulang (Rp/m³)", value=4200000, step=50000) if show_cor else 0
    
    show_timbunan = st.sidebar.checkbox("Timbunan Kembali (Backfill)", value=True)
    h_timbunan = st.sidebar.number_input("AHSP Timbunan Tanah (Rp/m³)", value=115000, step=5000) if show_timbunan else 0

    # Perhitungan Volume
    vol_beton_stem = ((tebal_atas + tebal_bawah) / 2 * tinggi_dinding) * panjang_dpt
    vol_beton_base = (lebar_pelat * tebal_pelat) * panjang_dpt
    vol_beton_total = vol_beton_stem + vol_beton_base
    
    vol_galian = (lebar_pelat + 0.5) * tebal_pelat * panjang_dpt # Asumsi galian dilebihkan
    vol_timbunan = lebar_heel * tinggi_dinding * panjang_dpt # Tanah di atas heel

    if show_galian: item_to_add.append(["Galian Tanah Struktur", vol_galian, "m³", h_galian])
    if show_cor: item_to_add.append(["Pengecoran Beton DPT", vol_beton_total, "m³", h_cor])
    if show_timbunan: item_to_add.append(["Timbunan Tanah (Backfill)", vol_timbunan, "m³", h_timbunan])

    # Visualisasi
    fig, ax = plt.subplots()
    lebar_toe = lebar_pelat - lebar_heel - tebal_bawah
    # Pelat Dasar (Base)
    ax.add_patch(plt.Rectangle((0, -tebal_pelat), lebar_pelat, tebal_pelat, color='gray', label='Beton DPT'))
    # Dinding (Stem)
    x_stem = [lebar_toe, lebar_toe + tebal_bawah, lebar_toe + tebal_bawah - (tebal_bawah-tebal_atas), lebar_toe]
    y_stem = [0, 0, tinggi_dinding, tinggi_dinding]
    ax.fill(x_stem, y_stem, color='gray')
    # Timbunan (Backfill)
    ax.add_patch(plt.Rectangle((lebar_toe + tebal_bawah, 0), lebar_heel, tinggi_dinding, color='saddlebrown', alpha=0.4, label='Timbunan (Backfill)'))
    
    ax.set_xlim(-0.5, lebar_pelat + 0.5)
    ax.set_ylim(-tebal_pelat - 0.5, tinggi_dinding + 0.5)
    ax.set_aspect('equal')
    ax.legend()
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
# MASTER REKAPITULASI BIAYA & SUB-TOTAL
# =====================================================================
st.divider()
st.header("🛒 Master Rekapitulasi Proyek (RAB)")

if st.session_state.rekap_proyek:
    df_rekap = pd.DataFrame(st.session_state.rekap_proyek)
    
    st.subheader("📊 Rekapitulasi per Jenis Pekerjaan")
    summary_df = df_rekap.groupby('Kategori')['Total Biaya'].sum().reset_index()
    
    cols = st.columns(len(summary_df))
    for index, row in summary_df.iterrows():
        cols[index].metric(label=f"Total {row['Kategori']}", value=f"Rp {row['Total Biaya']:,.0f}")
    
    st.write("---")
    st.subheader("📋 Detail Rincian Anggaran")
    
    df_display = df_rekap.copy()
    df_display["AHSP"] = df_display["AHSP"].map("Rp {:,.0f}".format)
    df_display["Total Biaya"] = df_display["Total Biaya"].map("Rp {:,.0f}".format)
    st.dataframe(df_display, use_container_width=True)
    
    grand_total = df_rekap["Total Biaya"].sum()
    st.metric("💰 GRAND TOTAL KESELURUHAN", f"Rp {grand_total:,.0f}")
    
    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("🗑️ Hapus Rekap"):
            st.session_state.rekap_proyek = []
            st.rerun()
else:
    st.info("Belum ada data di rekapitulasi. Silakan proses perhitungan di atas lalu klik 'Tambahkan ke Master Rekap'.")

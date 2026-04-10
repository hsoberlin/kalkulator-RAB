import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Estimator Proyek Terpadu", layout="wide")

# --- INISIALISASI SESSION STATE UNTUK REKAP ---
if 'rekap_proyek' not in st.session_state:
    st.session_state.rekap_proyek = []

st.title("🏗️ Kalkulator Volume & Biaya Konstruksi Terpadu")
st.write("Hitung detail per item pekerjaan, visualisasikan, dan tambahkan ke dalam Master Rekapitulasi Proyek.")

# --- SIDEBAR MENU UTAMA ---
st.sidebar.title("Navigasi")
jenis_bangunan = st.sidebar.selectbox(
    "Pilih Jenis Pekerjaan:",
    ["1. Saluran Trapesium", "2. Jalan Perkerasan Lentur (Aspal)", "3. Pondasi Telapak"]
)

st.sidebar.divider()

# Variabel sementara penampung data untuk dimasukkan ke rekap
item_to_add = []

# =====================================================================
# 1. LOGIKA SALURAN TRAPESIUM
# =====================================================================
if jenis_bangunan == "1. Saluran Trapesium":
    st.sidebar.header("📐 Dimensi Saluran")
    lebar_atas = st.sidebar.number_input("Lebar Atas (m)", value=1.2)
    lebar_bawah = st.sidebar.number_input("Lebar Bawah (m)", value=0.8)
    tinggi = st.sidebar.number_input("Tinggi (m)", value=5.0)
    tebal_beton = st.sidebar.number_input("Tebal Beton (m)", value=0.2)
    panjang = st.sidebar.number_input("Panjang Saluran (m)", value=100.0)

    st.sidebar.header("🛠️ Pilih Pekerjaan & AHSP")
    show_bongkar = st.sidebar.checkbox("Bongkaran Beton", value=True)
    h_bongkar = st.sidebar.number_input("AHSP Bongkaran (Rp/m³)", value=250000, step=10000) if show_bongkar else 0
    
    show_galian = st.sidebar.checkbox("Galian Tanah", value=True)
    h_galian = st.sidebar.number_input("AHSP Galian (Rp/m³)", value=75000, step=5000) if show_galian else 0
    
    show_cor = st.sidebar.checkbox("Pengecoran Beton", value=True)
    h_cor = st.sidebar.number_input("AHSP Cor (Rp/m³)", value=1200000, step=50000) if show_cor else 0

    # Perhitungan
    dist = (lebar_atas - lebar_bawah) / 2
    sisi_miring = np.sqrt(dist**2 + tinggi**2)
    keliling = (2 * sisi_miring) + lebar_bawah
    
    vol_beton = keliling * tebal_beton * panjang
    vol_tanah = ((lebar_atas + lebar_bawah) / 2 * tinggi) * panjang

    # Menyiapkan data untuk rekap
    if show_bongkar: item_to_add.append(["Saluran - Bongkaran", vol_beton, "m³", h_bongkar])
    if show_galian: item_to_add.append(["Saluran - Galian", vol_tanah, "m³", h_galian])
    if show_cor: item_to_add.append(["Saluran - Pengecoran", vol_beton, "m³", h_cor])

    # Visualisasi
    x_coords = [0, dist, dist + lebar_bawah, lebar_atas]
    y_coords = [0, -tinggi, -tinggi, 0]
    
    fig, ax = plt.subplots()
    ax.plot(x_coords, y_coords, marker='o', color='brown', linewidth=2)
    ax.fill(x_coords, y_coords, color='cyan', alpha=0.3)
    ax.set_aspect('equal')
    ax.set_title("Potongan Melintang Saluran")

# =====================================================================
# 2. LOGIKA JALAN PERKERASAN LENTUR (ASPAL)
# =====================================================================
elif jenis_bangunan == "2. Jalan Perkerasan Lentur (Aspal)":
    st.sidebar.header("📐 Dimensi Jalan")
    lebar = st.sidebar.number_input("Lebar Jalan (m)", value=6.0)
    panjang = st.sidebar.number_input("Panjang Jalan (m)", value=1000.0)
    t_aspal = st.sidebar.number_input("Tebal Lapis Permukaan/Aspal (m)", value=0.05)
    t_base = st.sidebar.number_input("Tebal Lapis Pondasi Atas (m)", value=0.15)
    t_subbase = st.sidebar.number_input("Tebal Lapis Pondasi Bawah (m)", value=0.20)

    st.sidebar.header("🛠️ Pilih Pekerjaan & AHSP")
    show_subbase = st.sidebar.checkbox("Lapis Pondasi Bawah (Agregat B)", value=True)
    h_subbase = st.sidebar.number_input("AHSP Agregat B (Rp/m³)", value=350000, step=10000) if show_subbase else 0
    
    show_base = st.sidebar.checkbox("Lapis Pondasi Atas (Agregat A)", value=True)
    h_base = st.sidebar.number_input("AHSP Agregat A (Rp/m³)", value=450000, step=10000) if show_base else 0
    
    show_aspal = st.sidebar.checkbox("Lapis Permukaan (AC-WC)", value=True)
    h_aspal = st.sidebar.number_input("AHSP Aspal AC-WC (Rp/m³)", value=2500000, step=50000) if show_aspal else 0

    # Perhitungan
    vol_subbase = lebar * panjang * t_subbase
    vol_base = lebar * panjang * t_base
    vol_aspal = lebar * panjang * t_aspal

    # Menyiapkan data untuk rekap
    if show_subbase: item_to_add.append(["Jalan - Agregat B", vol_subbase, "m³", h_subbase])
    if show_base: item_to_add.append(["Jalan - Agregat A", vol_base, "m³", h_base])
    if show_aspal: item_to_add.append(["Jalan - Aspal AC-WC", vol_aspal, "m³", h_aspal])

    # Visualisasi
    fig, ax = plt.subplots()
    ax.add_patch(plt.Rectangle((0, -t_aspal), lebar, t_aspal, color='black', alpha=0.8, label='Aspal'))
    ax.add_patch(plt.Rectangle((0, -(t_aspal+t_base)), lebar, t_base, color='gray', alpha=0.5, label='Base (A)'))
    ax.add_patch(plt.Rectangle((0, -(t_aspal+t_base+t_subbase)), lebar, t_subbase, color='tan', alpha=0.5, label='Sub-base (B)'))
    ax.set_xlim(-0.5, lebar + 0.5)
    ax.set_ylim(-(t_aspal+t_base+t_subbase) - 0.1, 0.1)
    ax.set_aspect('equal')
    ax.legend()
    ax.set_title("Susunan Perkerasan Jalan")

# =====================================================================
# 3. LOGIKA PONDASI TELAPAK
# =====================================================================
elif jenis_bangunan == "3. Pondasi Telapak":
    st.sidebar.header("📐 Dimensi Pondasi")
    p_telapak = st.sidebar.number_input("Panjang Telapak (m)", value=1.5)
    l_telapak = st.sidebar.number_input("Lebar Telapak (m)", value=1.5)
    t_telapak = st.sidebar.number_input("Tebal Telapak (m)", value=0.3)
    lebar_kolom = st.sidebar.number_input("Sisi Kolom Pedestal (m)", value=0.4)
    t_kolom = st.sidebar.number_input("Tinggi Kolom (m)", value=1.0)
    jml_titik = st.sidebar.number_input("Jumlah Titik Pondasi", value=12, step=1)

    st.sidebar.header("🛠️ Pilih Pekerjaan & AHSP")
    show_galian = st.sidebar.checkbox("Galian Tanah (Dilebihkan 20cm)", value=True)
    h_galian = st.sidebar.number_input("AHSP Galian (Rp/m³)", value=75000, step=5000) if show_galian else 0
    
    show_lantai = st.sidebar.checkbox("Lantai Kerja (Tebal 5cm)", value=True)
    h_lantai = st.sidebar.number_input("AHSP Lantai Kerja (Rp/m³)", value=850000, step=10000) if show_lantai else 0
    
    show_cor = st.sidebar.checkbox("Beton Bertulang (Telapak + Kolom)", value=True)
    h_cor = st.sidebar.number_input("AHSP Beton Bertulang (Rp/m³)", value=4500000, step=50000) if show_cor else 0

    # Perhitungan
    vol_galian = (p_telapak + 0.4) * (l_telapak + 0.4) * (t_telapak + t_kolom) * jml_titik
    vol_lantai = p_telapak * l_telapak * 0.05 * jml_titik
    vol_beton = ((p_telapak * l_telapak * t_telapak) + (lebar_kolom * lebar_kolom * t_kolom)) * jml_titik

    # Menyiapkan data untuk rekap
    if show_galian: item_to_add.append(["Pondasi - Galian", vol_galian, "m³", h_galian])
    if show_lantai: item_to_add.append(["Pondasi - Lantai Kerja", vol_lantai, "m³", h_lantai])
    if show_cor: item_to_add.append(["Pondasi - Beton", vol_beton, "m³", h_cor])

    # Visualisasi
    fig, ax = plt.subplots()
    # Lantai kerja
    ax.add_patch(plt.Rectangle((-(p_telapak/2), -0.05), p_telapak, 0.05, color='orange', alpha=0.5, label='Lantai Kerja'))
    # Telapak
    ax.add_patch(plt.Rectangle((-(p_telapak/2), 0), p_telapak, t_telapak, color='gray', alpha=0.8, label='Plat Telapak'))
    # Kolom
    ax.add_patch(plt.Rectangle((-(lebar_kolom/2), t_telapak), lebar_kolom, t_kolom, color='darkgray', alpha=0.9, label='Kolom'))
    
    ax.set_xlim(-(p_telapak/2) - 0.5, (p_telapak/2) + 0.5)
    ax.set_ylim(-0.2, t_telapak + t_kolom + 0.2)
    ax.set_aspect('equal')
    ax.legend()
    ax.set_title("Potongan Pondasi Telapak")

# =====================================================================
# TAMPILAN UTAMA (PREVIEW & TAMBAH KE REKAP)
# =====================================================================
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader(f"Preview Estimasi: {jenis_bangunan}")
    preview_data = []
    total_preview = 0
    for item in item_to_add:
        nama, vol, sat, ahsp = item
        biaya = vol * ahsp
        total_preview += biaya
        preview_data.append([nama, f"{vol:.2f} {sat}", f"Rp {biaya:,.0f}"])
    
    if preview_data:
        df_preview = pd.DataFrame(preview_data, columns=["Sub Pekerjaan", "Volume", "Total Biaya"])
        st.table(df_preview)
        st.info(f"**Total Item Ini: Rp {total_preview:,.0f}**")
        
        if st.button("➕ TAMBAHKAN KE MASTER REKAP", use_container_width=True):
            for item in item_to_add:
                nama, vol, sat, ahsp = item
                st.session_state.rekap_proyek.append({
                    "Kategori": jenis_bangunan.split(". ")[1],
                    "Pekerjaan": nama,
                    "Volume": round(vol, 2),
                    "Satuan": sat,
                    "AHSP": f"Rp {ahsp:,.0f}",
                    "Total Biaya": vol * ahsp
                })
            st.success("Berhasil ditambahkan ke Keranjang/Rekap!")
    else:
        st.warning("Centang minimal satu pekerjaan di sidebar untuk melihat estimasi.")

with col2:
    st.subheader("Visualisasi Penampang")
    st.pyplot(fig)

# =====================================================================
# MASTER REKAPITULASI BIAYA
# =====================================================================
st.divider()
st.header("🛒 Master Rekapitulasi Proyek")

if st.session_state.rekap_proyek:
    df_rekap = pd.DataFrame(st.session_state.rekap_proyek)
    
    # Format mata uang untuk tampilan
    df_display = df_rekap.copy()
    df_display["Total Biaya"] = df_display["Total Biaya"].map("Rp {:,.0f}".format)
    
    st.dataframe(df_display, use_container_width=True)
    
    grand_total = df_rekap["Total Biaya"].sum()
    st.metric("GRAND TOTAL PROYEK", f"Rp {grand_total:,.0f}")
    
    if st.button("🗑️ Hapus Semua Data Rekap"):
        st.session_state.rekap_proyek = []
        st.rerun()
else:
    st.info("Belum ada data di rekapitulasi. Silakan proses perhitungan di atas lalu klik 'Tambahkan ke Master Rekap'.")

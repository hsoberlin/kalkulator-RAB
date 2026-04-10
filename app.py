import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Estimator Proyek Terpadu", layout="wide")

if 'rekap_proyek' not in st.session_state:
    st.session_state.rekap_proyek = []

st.title("🏗️ Kalkulator Konstruksi Terpadu")

# --- SIDEBAR NAVIGASI ---
st.sidebar.title("Navigasi Proyek")
jenis_bangunan = st.sidebar.selectbox("Jenis Pekerjaan:", ["1. Saluran Trapesium (Beton)", "2. Saluran Pasangan Batu (Drainase)", "3. Jalan Perkerasan Lentur (Aspal)", "4. Jalan Perkerasan Kaku (Rigid)", "5. Pondasi Telapak", "6. Dinding Penahan Tanah (Kantilever)"])
mode_proyek = st.sidebar.radio("Metode:", ["Bangunan Baru", "Rehabilitasi"])

# --- GLOBAL: PERSENTASE BONGKARAN (Hanya muncul jika mode Rehabilitasi) ---
persen_bongkar = 100
if mode_proyek == "Rehabilitasi":
    st.sidebar.divider()
    st.sidebar.subheader("⚙️ Kondisi Eksisting")
    persen_bongkar = st.sidebar.slider("Persentase Bongkaran Struktur Lama (%)", 0, 100, 100)

# --- PENGATURAN KEUANGAN ---
st.sidebar.divider()
overhead_pct = st.sidebar.number_input("Overhead & Profit (%)", value=10.0)
ppn_pct = st.sidebar.number_input("PPN (%)", value=11.0)

item_to_add = []
kategori_pekerjaan = jenis_bangunan.split(". ")[1]

# =====================================================================
# 1. SALURAN TRAPESIUM
# =====================================================================
if jenis_bangunan == "1. Saluran Trapesium (Beton)":
    st.sidebar.header("📐 Dimensi")
    l_atas = st.sidebar.number_input("Lebar Dalam Atas (m)", value=1.2)
    l_bawah = st.sidebar.number_input("Lebar Dalam Bawah (m)", value=0.8)
    tinggi = st.sidebar.number_input("Tinggi (m)", value=5.0)
    panjang = st.sidebar.number_input("Panjang (m)", value=100.0)
    t_atas = st.sidebar.number_input("Tebal Atas (m)", value=0.15)
    t_bawah = st.sidebar.number_input("Tebal Bawah (m)", value=0.25)
    t_dasar = st.sidebar.number_input("Tebal Dasar (m)", value=0.30)

    vol_beton = (((t_atas + t_bawah) / 2 * np.sqrt(((l_atas-l_bawah)/2)**2 + tinggi**2) * 2) + (l_bawah * t_dasar)) * panjang
    
    if mode_proyek == "Bangunan Baru":
        vol_tanah = (((l_atas+(2*t_atas) + l_bawah+(2*t_bawah))/2) * (tinggi+t_dasar)) * panjang
        item_to_add.append(["Galian Tanah Saluran Baru", vol_tanah, "m³", 75000])
    else:
        vol_bongkar = vol_beton * (persen_bongkar / 100)
        item_to_add.append([f"Bongkaran Beton ({persen_bongkar}%)", vol_bongkar, "m³", 250000])
        item_to_add.append(["Galian Sedimen/Normalisasi", (l_atas+l_bawah)/2 * tinggi * panjang * 0.3, "m³", 85000])

    item_to_add.append(["Pengecoran Beton Baru", vol_beton, "m³", 1200000])
    item_to_add.append(["Pembesian (110kg/m3)", vol_beton * 110, "kg", 18500])

# =====================================================================
# 4. JALAN RIGID
# =====================================================================
elif jenis_bangunan == "4. Jalan Perkerasan Kaku (Rigid)":
    lebar = st.sidebar.number_input("Lebar (m)", value=5.0)
    panjang = st.sidebar.number_input("Panjang (m)", value=500.0)
    tebal = st.sidebar.number_input("Tebal (m)", value=0.25)
    vol_rigid = lebar * panjang * tebal

    if mode_proyek == "Rehabilitasi":
        vol_bongkar = vol_rigid * (persen_bongkar / 100)
        item_to_add.append([f"Bongkaran Rigid Lama ({persen_bongkar}%)", vol_bongkar, "m³", 450000])
    else:
        item_to_add.append(["Penyiapan Badan Jalan", lebar * panjang, "m²", 12000])

    item_to_add.append(["Beton Rigid K-350", vol_rigid, "m³", 1450000])
    item_to_add.append(["Lantai Kerja (LC)", lebar * panjang * 0.1, "m³", 950000])

# --- PROSES REKAPITULASI ---
col1, col2 = st.columns([1, 1])
with col1:
    st.subheader(f"Preview: {kategori_pekerjaan}")
    total_preview = sum(i[1] * i[3] for i in item_to_add)
    for i in item_to_add:
        st.write(f"- {i[0]}: {i[1]:.2f} {i[2]} (Rp {i[1]*i[3]:,.0f})")
    
    if st.button("➕ TAMBAHKAN KE MASTER REKAP", use_container_width=True):
        for i in item_to_add:
            st.session_state.rekap_proyek.append({"Kategori": kategori_pekerjaan, "Pekerjaan": i[0], "Volume": round(i[1], 2), "Satuan": i[2], "AHSP": i[3], "Total": i[1]*i[3]})
        st.success("Ditambahkan!")

with col2:
    st.info(f"Sub-Total: Rp {total_preview:,.0f}")
    st.write("Visualisasi disesuaikan berdasarkan input dimensi di sidebar.")

# --- MASTER RAB ---
st.divider()
st.header("🛒 Master Rekapitulasi Proyek (RAB)")
if st.session_state.rekap_proyek:
    df = pd.DataFrame(st.session_state.rekap_proyek)
    
    # Tampilan Detail per Kategori
    for kat in df['Kategori'].unique():
        df_kat = df[df['Kategori'] == kat]
        st.markdown(f"### {kat}")
        st.table(df_kat[['Pekerjaan', 'Volume', 'Satuan', 'Total']].assign(Total=df_kat['Total'].map("Rp {:,.0f}".format)))
        st.write(f"**Sub-Total {kat}: Rp {df_kat['Total'].sum():,.0f}**")
    
    # Ringkasan Akhir
    biaya_langsung = df['Total'].sum()
    overhead = biaya_langsung * (overhead_pct/100)
    ppn = (biaya_langsung + overhead) * (ppn_pct/100)
    st.divider()
    st.metric("GRAND TOTAL (TERMASUK PPN)", f"Rp {biaya_langsung + overhead + ppn:,.0f}")
    if st.button("🗑️ Hapus Semua"):
        st.session_state.rekap_proyek = []; st.rerun()

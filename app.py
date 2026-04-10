import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Kalkulator Saluran Proyek", layout="wide")

st.title("📊 Kalkulator Volume & AHSP Saluran")

# --- SIDEBAR INPUT PARAMETER ---
st.sidebar.header("1. Dimensi Saluran")
lebar_atas = st.sidebar.number_input("Lebar Atas (m)", value=1.2)
lebar_bawah = st.sidebar.number_input("Lebar Bawah (m)", value=0.8)
tinggi = st.sidebar.number_input("Tinggi (m)", value=5.0)
tebal_beton = st.sidebar.number_input("Tebal Beton (m)", value=0.2)
panjang_saluran = st.sidebar.number_input("Panjang Saluran (m)", value=100.0)

st.sidebar.header("2. Pilih Volume yg Ditampilkan")
show_bongkaran = st.sidebar.checkbox("Volume Bongkaran Beton", value=True)
show_galian = st.sidebar.checkbox("Volume Galian Tanah", value=False)
show_pengecoran = st.sidebar.checkbox("Volume Pengecoran Baru", value=True)

st.sidebar.header("3. AHSP (Harga Satuan)")
harga_bongkar = st.sidebar.number_input("Harga Bongkar per m3 (Rp)", value=250000, step=10000)
harga_galian = st.sidebar.number_input("Harga Galian per m3 (Rp)", value=75000, step=5000)
harga_cor = st.sidebar.number_input("Harga Cor per m3 (Rp)", value=1200000, step=50000)

# --- LOGIKA PERHITUNGAN ---
dist = (lebar_atas - lebar_bawah) / 2
x_coords = [0, dist, dist + lebar_bawah, lebar_atas]
y_coords = [0, -tinggi, -tinggi, 0]

# Keliling Basah (Miring + Bawah + Miring)
sisi_miring = np.sqrt(dist**2 + tinggi**2)
keliling = (2 * sisi_miring) + lebar_bawah

vol_beton = keliling * tebal_beton * panjang_saluran
vol_tanah = ((lebar_atas + lebar_bawah) / 2 * tinggi) * panjang_saluran

# --- TAMPILAN UTAMA ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("💰 Estimasi Biaya & Volume")
    
    data_rekap = []
    
    if show_bongkaran:
        biaya = vol_beton * harga_bongkar
        data_rekap.append(["Bongkaran Beton", f"{vol_beton:.2f} m³", f"Rp {biaya:,.0f}"])
        st.metric("Volume Bongkaran", f"{vol_beton:.2f} m³", f"Biaya: Rp {biaya:,.0f}")

    if show_galian:
        biaya = vol_tanah * harga_galian
        data_rekap.append(["Galian Tanah", f"{vol_tanah:.2f} m³", f"Rp {biaya:,.0f}"])
        st.metric("Volume Galian Tanah", f"{vol_tanah:.2f} m³", f"Biaya: Rp {biaya:,.0f}")

    if show_pengecoran:
        biaya = vol_beton * harga_cor
        data_rekap.append(["Pengecoran Baru", f"{vol_beton:.2f} m³", f"Rp {biaya:,.0f}"])
        st.metric("Volume Pengecoran", f"{vol_beton:.2f} m³", f"Biaya: Rp {biaya:,.0f}")

    # Tabel Ringkasan
    if data_rekap:
        st.write("### Ringkasan Tabel")
        df = pd.DataFrame(data_rekap, columns=["Pekerjaan", "Volume", "Total Biaya"])
        st.table(df)

with col2:
    st.subheader("📈 Visualisasi Potongan Melintang")
    fig, ax = plt.subplots()
    ax.plot(x_coords, y_coords, marker='o', color='brown', linewidth=2)
    ax.fill(x_coords, y_coords, color='cyan', alpha=0.1)
    ax.set_aspect('equal')
    st.pyplot(fig)

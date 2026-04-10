import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Kalkulator Saluran Proyek PLTA", layout="wide")

st.title("📊 Aplikasi Perhitungan Volume Saluran (Tipikal 1)")
st.write("Masukkan parameter dimensi saluran untuk mendapatkan koordinat dan volume secara otomatis.")

# --- SIDEBAR INPUT ---
st.sidebar.header("Input Parameter")
lebar_atas = st.sidebar.number_input("Lebar Atas (m)", value=1.2, step=0.1)
lebar_bawah = st.sidebar.number_input("Lebar Bawah (m)", value=0.8, step=0.1)
tinggi = st.sidebar.number_input("Tinggi (m)", value=5.0, step=0.1)
tebal_beton = st.sidebar.number_input("Tebal Beton (m)", value=0.2, step=0.01)
panjang_saluran = st.sidebar.number_input("Panjang Saluran (m)", value=100.0, step=1.0)

# --- LOGIKA PERHITUNGAN KOORDINAT ---
dist = (lebar_atas - lebar_bawah) / 2
x_coords = [0, dist, dist + lebar_bawah, lebar_atas]
y_coords = [0, -tinggi, -tinggi, 0]

# Hitung Panjang Sisi (Keliling Basah)
sisi_miring_kiri = np.sqrt((x_coords[1]-x_coords[0])**2 + (y_coords[1]-y_coords[0])**2)
sisi_datar = lebar_bawah
sisi_miring_kanan = np.sqrt((x_coords[3]-x_coords[2])**2 + (y_coords[3]-y_coords[2])**2)
keliling_total = sisi_miring_kiri + sisi_datar + sisi_miring_kanan

# Hitung Volume
vol_bongkar_pasang = keliling_total * tebal_beton * panjang_saluran
vol_galian_tanah = ((lebar_atas + lebar_bawah) / 2 * tinggi) * panjang_saluran

# --- TAMPILAN UTAMA ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📍 Koordinat Penampang")
    df_coords = pd.DataFrame({
        'Titik': ['P1', 'P2', 'P3', 'P4'],
        'X (Horizontal)': x_coords,
        'Y (Vertical)': y_coords
    })
    st.table(df_coords)

    st.subheader("📦 Hasil Perhitungan Volume")
    st.metric("Volume Bongkaran Beton", f"{vol_bongkar_pasang:.2f} m³")
    st.metric("Volume Galian Tanah Tengah", f"{vol_galian_tanah:.2f} m³")
    st.metric("Volume Pengecoran Baru", f"{vol_bongkar_pasang:.2f} m³")

with col2:
    st.subheader("📈 Visualisasi Penampang")
    fig, ax = plt.subplots()
    ax.plot(x_coords, y_coords, marker='o', linestyle='-', color='#1f77b4', linewidth=3)
    ax.fill(x_coords, y_coords, color='#aec7e8', alpha=0.3)
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_xlabel("Lebar (m)")
    ax.set_ylabel("Kedalaman (m)")
    st.pyplot(fig)

st.divider()
st.info("💡 Tip: Anda bisa mengubah angka di sidebar kiri untuk langsung melihat perubahan volume dan grafik.")
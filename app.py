import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="Multi-Project Calculator", layout="wide")

# --- MENU UTAMA ---
st.title("🏗️ Kalkulator Konstruksi Multi-Fungsi")
jenis_bangunan = st.selectbox(
    "Pilih Jenis Pekerjaan:",
    ["Saluran Trapesium", "Jalan Perkerasan Lentur", "Jalan Perkerasan Kaku", "Pondasi Telapak", "Bangunan Gedung"]
)

st.divider()

# --- LOGIKA BERDASARKAN PILIHAN ---

if jenis_bangunan == "Saluran Trapesium":
    st.sidebar.header("Parameter Saluran")
    b2 = st.sidebar.number_input("Lebar Atas (m)", value=1.2)
    b3 = st.sidebar.number_input("Lebar Bawah (m)", value=0.8)
    b4 = st.sidebar.number_input("Tinggi (m)", value=5.0)
    b5 = st.sidebar.number_input("Tebal Beton (m)", value=0.2)
    b6 = st.sidebar.number_input("Panjang (m)", value=100.0)
    
    # Hitung
    dist = (b2 - b3) / 2
    keliling = (2 * np.sqrt(dist**2 + b4**2)) + b3
    vol_beton = keliling * b5 * b6
    
    st.subheader(f"Hasil Perhitungan {jenis_bangunan}")
    st.metric("Total Volume Beton", f"{vol_beton:.2f} m³")

elif jenis_bangunan == "Jalan Perkerasan Lentur":
    st.sidebar.header("Parameter Jalan Lentur")
    lebar = st.sidebar.number_input("Lebar Jalan (m)", value=7.0)
    panjang = st.sidebar.number_input("Panjang Jalan (m)", value=1000.0)
    t_aspal = st.sidebar.number_input("Tebal Aspal/AC-WC (m)", value=0.04)
    t_base = st.sidebar.number_input("Tebal Lapis Pondasi Atas (m)", value=0.15)
    
    vol_aspal = lebar * panjang * t_aspal
    vol_base = lebar * panjang * t_base
    
    st.subheader(f"Hasil Perhitungan {jenis_bangunan}")
    col1, col2 = st.columns(2)
    col1.metric("Volume Aspal (AC-WC)", f"{vol_aspal:.2f} m³")
    col2.metric("Volume Agregat Base A", f"{vol_base:.2f} m³")

elif jenis_bangunan == "Jalan Perkerasan Kaku":
    st.sidebar.header("Parameter Rigid Pavement")
    lebar = st.sidebar.number_input("Lebar Perkerasan (m)", value=3.5)
    panjang = st.sidebar.number_input("Panjang (m)", value=100.0)
    tebal = st.sidebar.number_input("Tebal Beton FS 45 (m)", value=0.25)
    
    vol_rigid = lebar * panjang * tebal
    st.subheader(f"Hasil Perhitungan {jenis_bangunan}")
    st.metric("Volume Beton Rigid", f"{vol_rigid:.2f} m³")

elif jenis_bangunan == "Pondasi Telapak":
    st.sidebar.header("Parameter Pondasi")
    p = st.sidebar.number_input("Panjang Pondasi (m)", value=1.5)
    l = st.sidebar.number_input("Lebar Pondasi (m)", value=1.5)
    t = st.sidebar.number_input("Tebal Plat Pondasi (m)", value=0.3)
    jumlah = st.sidebar.number_input("Jumlah Titik", value=10)
    
    vol_pondasi = p * l * t * jumlah
    st.subheader(f"Hasil Perhitungan {jenis_bangunan}")
    st.metric("Total Volume Beton Pondasi", f"{vol_pondasi:.2f} m³")

# Dan seterusnya untuk Bangunan Gedung...

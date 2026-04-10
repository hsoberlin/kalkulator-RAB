import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Rekapitulasi Proyek Konstruksi", layout="wide")

# --- INISIALISASI PENYIMPANAN DATA (SESSION STATE) ---
if 'rekap_proyek' not in st.session_state:
    st.session_state.rekap_proyek = []

st.title("📊 Kalkulator Kontruksi & Rekapitulasi Biaya")
st.write("Hitung volume per item, simpan, dan dapatkan total biaya keseluruhan proyek.")

# --- SIDEBAR: PEMILIHAN JENIS & INPUT DIMENSI ---
st.sidebar.header("🔧 Input Parameter")
jenis_bangunan = st.sidebar.selectbox(
    "Pilih Jenis Pekerjaan:",
    ["Saluran Trapesium", "Jalan Perkerasan Kaku (Rigid)", "Pondasi Telapak"]
)

# Variabel penampung hasil perhitungan sementara
nama_item = ""
volume_hitung = 0
satuan = "m³"

if jenis_bangunan == "Saluran Trapesium":
    l_atas = st.sidebar.number_input("Lebar Atas (m)", value=1.2)
    l_bawah = st.sidebar.number_input("Lebar Bawah (m)", value=0.8)
    tinggi = st.sidebar.number_input("Tinggi (m)", value=5.0)
    tebal = st.sidebar.number_input("Tebal Beton (m)", value=0.2)
    panjang = st.sidebar.number_input("Panjang Saluran (m)", value=100.0)
    
    dist = (l_atas - l_bawah) / 2
    keliling = (2 * np.sqrt(dist**2 + tinggi**2)) + l_bawah
    volume_hitung = keliling * tebal * panjang
    nama_item = f"Beton Saluran ({panjang}m)"

elif jenis_bangunan == "Jalan Perkerasan Kaku (Rigid)":
    lebar_jln = st.sidebar.number_input("Lebar Jalan (m)", value=3.5)
    panjang_jln = st.sidebar.number_input("Panjang Jalan (m)", value=100.0)
    tebal_rigid = st.sidebar.number_input("Tebal Beton (m)", value=0.25)
    volume_hitung = lebar_jln * panjang_jln * tebal_rigid
    nama_item = f"Beton Rigid ({panjang_jln}m)"

elif jenis_bangunan == "Pondasi Telapak":
    p_pdsi = st.sidebar.number_input("Panjang (m)", value=1.5)
    l_pdsi = st.sidebar.number_input("Lebar (m)", value=1.5)
    t_pdsi = st.sidebar.number_input("Tebal (m)", value=0.3)
    jumlah = st.sidebar.number_input("Jumlah Titik", value=10)
    volume_hitung = p_pdsi * l_pdsi * t_pdsi * jumlah
    nama_item = f"Pondasi Telapak ({jumlah} titik)"

# --- INPUT AHSP ---
st.sidebar.header("💰 Input AHSP (Harga Satuan)")
harga_satuan = st.sidebar.number_input(f"Harga Satuan {satuan} (Rp)", value=1200000, step=50000)
total_biaya_item = volume_hitung * harga_satuan

# --- TOMBOL SIMPAN KE REKAP ---
if st.sidebar.button("➕ Tambahkan ke Rekapitulasi"):
    new_data = {
        "Pekerjaan": jenis_bangunan,
        "Detail": nama_item,
        "Volume": round(volume_hitung, 2),
        "Satuan": satuan,
        "AHSP (Rp)": harga_satuan,
        "Total Harga (Rp)": total_biaya_item
    }
    st.session_state.rekap_proyek.append(new_data)
    st.success(f"{nama_item} berhasil ditambahkan!")

# --- TAMPILAN UTAMA: REKAPITULASI ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📋 Daftar Pekerjaan & Biaya")
    if st.session_state.rekap_proyek:
        df = pd.DataFrame(st.session_state.rekap_proyek)
        # Format Rupiah untuk tampilan tabel
        df_display = df.copy()
        df_display["AHSP (Rp)"] = df_display["AHSP (Rp)"].map("Rp {:,.0f}".format)
        df_display["Total Harga (Rp)"] = df_display["Total Harga (Rp)"].map("Rp {:,.0f}".format)
        st.table(df_display)
        
        if st.button("🗑️ Hapus Semua Data"):
            st.session_state.rekap_proyek = []
            st.rerun()
    else:
        st.info("Belum ada data. Silakan input dimensi dan klik 'Tambahkan ke Rekapitulasi'.")

with col2:
    st.subheader("💰 Ringkasan Biaya")
    grand_total = sum(item["Total Harga (Rp)"] for item in st.session_state.rekap_proyek)
    st.metric("GRAND TOTAL BIAYA", f"Rp {grand_total:,.0f}")
    
    st.write("---")
    st.write("**Detail Perhitungan Saat Ini:**")
    st.write(f"Item: {nama_item}")
    st.write(f"Volume: {volume_hitung:.2f} {satuan}")
    st.write(f"Estimasi Biaya: Rp {total_biaya_item:,.0f}")

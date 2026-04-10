import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Konfigurasi Portrait untuk HP
st.set_page_config(page_title="Estimator RAB Konstruksi", layout="centered")

if 'rekap_proyek' not in st.session_state:
    st.session_state.rekap_proyek = []

st.title("Aplikasi Estimator Rencana Anggaran Biaya")
st.write("Sistem perhitungan teknis volume dan biaya konstruksi terpadu.")

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
kategori_pekerjaan = jenis_bangunan.split(". ")[1]

# =====================================================================
# 1. SALURAN TRAPESIUM (BETON)
# =====================================================================
if jenis_bangunan == "1. Saluran Trapesium (Beton)":
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

    if mode_proyek == "Bangunan Baru":
        item_to_add.append(["Galian Tanah Profil Baru", vol_tanah, "m³", 75000])
    else:
        p_bongkar = st.sidebar.slider("Persen Bongkaran (%)", 0, 100, 100)
        p_sedimen = st.sidebar.slider("Persen Sedimen (%)", 0, 100, 30)
        item_to_add.append([f"Bongkaran Beton ({p_bongkar}%)", vol_beton*(p_bongkar/100), "m³", 250000])
        item_to_add.append(["Galian Sedimen/Lumpur", vol_rongga*(p_sedimen/100), "m³", 85000])

    item_to_add.append(["Beton Struktur Saluran", vol_beton, "m³", 1200000])
    item_to_add.append(["Pembesian Saluran (110kg/m3)", vol_beton * 110, "kg", 18500])
    item_to_add.append(["Bekisting Dinding Saluran", (s_miring * 2) * panjang, "m²", 125000])

    fig, ax = plt.subplots()
    ax.plot([-l_atas/2, -l_bawah/2, l_bawah/2, l_atas/2], [0, -tinggi, -tinggi, 0], color='black')
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

    if mode_proyek == "Bangunan Baru":
        vol_galian = (((l_atas+(2*tebal)) + (l_bawah+(2*tebal)))/2 * (tinggi+tebal)) * panjang
        item_to_add.append(["Galian Tanah Drainase", vol_galian, "m³", 75000])
    else:
        item_to_add.append(["Bongkaran Batu Eksisting", vol_batu, "m³", 150000])

    item_to_add.append(["Pasangan Batu Kali (1:4)", vol_batu, "m³", 950000])
    item_to_add.append(["Plesteran + Acian", keliling * panjang, "m²", 65000])

    fig, ax = plt.subplots()
    ax.plot([0, dist, dist+l_bawah, l_atas], [0, -tinggi, -tinggi, 0], color='black', lw=3)
    ax.set_aspect('equal')

# =====================================================================
# 3. JALAN PERKERASAN LENTUR (ASPAl)
# =====================================================================
elif jenis_bangunan == "3. Jalan Perkerasan Lentur (Aspal)":
    lebar = st.sidebar.number_input("Lebar (m)", value=6.0)
    panjang = st.sidebar.number_input("Panjang (m)", value=1000.0)
    t_aspal = st.sidebar.number_input("Tebal Aspal (m)", value=0.05)
    t_base = st.sidebar.number_input("Tebal Agregat (m)", value=0.15)

    if mode_proyek == "Bangunan Baru":
        item_to_add.append(["Penyiapan Badan Jalan", lebar * panjang, "m²", 12000])
        item_to_add.append(["Lapis Pondasi Agregat A", lebar * panjang * t_base, "m³", 450000])
    else:
        item_to_add.append(["Cold Milling (Kupas Aspal)", lebar * panjang * t_aspal, "m³", 350000])
        item_to_add.append(["Lapis Perekat (Tack Coat)", lebar * panjang * 0.35, "Liter", 15000])

    item_to_add.append(["Aspal Hotmix AC-WC", lebar * panjang * t_aspal, "m³", 2500000])

    fig, ax = plt.subplots()
    ax.add_patch(plt.Rectangle((0, -t_aspal), lebar, t_aspal, color='black'))
    ax.set_xlim(-1, lebar+1); ax.set_ylim(-0.2, 0.1); ax.set_aspect('equal')

# =====================================================================
# 4. JALAN PERKERASAN KAKU (RIGID)
# =====================================================================
elif jenis_bangunan == "4. Jalan Perkerasan Kaku (Rigid)":
    lebar = st.sidebar.number_input("Lebar (m)", value=5.0)
    panjang = st.sidebar.number_input("Panjang (m)", value=500.0)
    t_rigid = st.sidebar.number_input("Tebal Rigid (m)", value=0.25)
    t_lc = st.sidebar.number_input("Tebal Lantai Kerja (m)", value=0.10)

    if mode_proyek == "Bangunan Baru":
        item_to_add.append(["Penyiapan Badan Jalan", lebar * panjang, "m²", 12000])
    else:
        item_to_add.append(["Bongkaran Rigid Eksisting", lebar * panjang * t_rigid, "m³", 450000])

    item_to_add.append(["Lantai Kerja (LC)", lebar * panjang * t_lc, "m³", 950000])
    item_to_add.append(["Beton Rigid K-350", lebar * panjang * t_rigid, "m³", 1450000])
    item_to_add.append(["Pembesian (Dowel/Wiremesh)", (lebar * panjang * t_rigid) * 60, "kg", 18500])
    item_to_add.append(["Bekisting Sisi Jalan", (t_rigid + t_lc) * panjang * 2, "m²", 125000])

    fig, ax = plt.subplots()
    ax.add_patch(plt.Rectangle((0, 0), lebar, t_rigid, color='gray', hatch='//'))
    ax.set_xlim(-1, lebar+1); ax.set_ylim(-0.2, 0.4); ax.set_aspect('equal')

# =====================================================================
# 5. PONDASI TELAPAK
# =====================================================================
elif jenis_bangunan == "5. Pondasi Telapak":
    p = st.sidebar.number_input("Panjang Plat (m)", value=1.5)
    l = st.sidebar.number_input("Lebar Plat (m)", value=1.5)
    t = st.sidebar.number_input("Tebal Plat (m)", value=0.3)
    jml = st.sidebar.number_input("Jumlah Titik", value=10)
    vol_beton = p * l * t * jml

    if mode_proyek != "Bangunan Baru":
        item_to_add.append(["Bongkaran Struktur Lama", vol_beton, "m³", 350000])

    item_to_add.append(["Galian Tanah Pondasi", (p+0.4)*(l+0.4)*t*jml, "m³", 75000])
    item_to_add.append(["Lantai Kerja Pondasi", p*l*0.05*jml, "m³", 950000])
    item_to_add.append(["Beton Plat Pondasi", vol_beton, "m³", 4500000])
    item_to_add.append(["Pembesian Pondasi", vol_beton * 150, "kg", 18500])
    item_to_add.append(["Bekisting Plat Pondasi", (p+l)*2*t*jml, "m²", 145000])

    fig, ax = plt.subplots()
    ax.add_patch(plt.Rectangle((-p/2, 0), p, t, color='gray'))
    ax.set_xlim(-1, 1); ax.set_ylim(-0.2, 0.5); ax.set_aspect('equal')

# =====================================================================
# 6. DINDING PENAHAN TANAH (DPT)
# =====================================================================
elif jenis_bangunan == "6. Dinding Penahan Tanah (Kantilever)":
    h = st.sidebar.number_input("Tinggi Dinding (m)", value=4.0)
    l_base = st.sidebar.number_input("Lebar Base (m)", value=2.5)
    panjang = st.sidebar.number_input("Panjang DPT (m)", value=50.0)
    vol_beton = ((0.4 * h) + (l_base * 0.4)) * panjang

    if mode_proyek != "Bangunan Baru":
        item_to_add.append(["Bongkaran DPT Eksisting", vol_beton, "m³", 350000])

    item_to_add.append(["Galian Struktur DPT", l_base * 1.0 * panjang, "m³", 75000])
    item_to_add.append(["Pengecoran Beton DPT", vol_beton, "m³", 4200000])
    item_to_add.append(["Pembesian Struktur DPT", vol_beton * 125, "kg", 18500])
    item_to_add.append(["Timbunan Tanah Kembali", (l_base/2) * h * panjang, "m³", 115000])

    fig, ax = plt.subplots()
    ax.add_patch(plt.Rectangle((0, -0.4), l_base, 0.4, color='gray'))
    ax.add_patch(plt.Rectangle((0.5, 0), 0.4, h, color='gray'))
    ax.set_xlim(-0.5, l_base+0.5); ax.set_ylim(-1, h+1); ax.set_aspect('equal')

# =====================================================================
# 7. PONDASI BORE PILE (NEW ITEM)
# =====================================================================
elif jenis_bangunan == "7. Pondasi Bore Pile":
    st.sidebar.header("Dimensi Bore Pile")
    diameter = st.sidebar.number_input("Diameter Pile (m)", value=0.6)
    kedalaman = st.sidebar.number_input("Kedalaman Pile (m)", value=12.0)
    jml_titik = st.sidebar.number_input("Jumlah Titik", value=20, step=1)
    rasio_besi = st.sidebar.number_input("Rasio Besi (kg/m³)", value=180)

    # Perhitungan Geometri
    area = np.pi * (diameter / 2)**2
    vol_pile_per_titik = area * kedalaman
    vol_total_beton = vol_pile_per_titik * jml_titik
    vol_pengeboran = area * kedalaman * jml_titik # m3
    panjang_besi = kedalaman * jml_titik # m' (sebagai referensi galian)

    st.sidebar.header("Pekerjaan & AHSP")
    if mode_proyek == "Rehabilitasi Struktur":
        item_to_add.append(["Pembersihan Lokasi/Bongkar Kepala Pile", jml_titik, "Titik", 500000])

    item_to_add.append(["Pengeboran Bore Pile", vol_pengeboran, "m³", 450000])
    item_to_add.append(["Pengecoran Beton K-350 (Bore Pile)", vol_total_beton, "m³", 1350000])
    item_to_add.append(["Pembesian Tulangan Bore Pile", vol_total_beton * rasio_besi, "kg", 18500])
    item_to_add.append(["Instalasi Temporary Casing", diameter * 2 * jml_titik, "m'", 150000]) # Asumsi casing 2m

    fig, ax = plt.subplots()
    # Tanah
    ax.add_patch(plt.Rectangle((-1, -kedalaman), 2, kedalaman, color='saddlebrown', alpha=0.1))
    # Pile
    ax.add_patch(plt.Rectangle((-diameter/2, -kedalaman), diameter, kedalaman, color='gray', label='Bore Pile'))
    ax.set_xlim(-1, 1); ax.set_ylim(-kedalaman-1, 1); ax.set_aspect('equal')
    ax.set_title("Profil Kedalaman Bore Pile")

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
    st.success("Data berhasil ditambahkan.")

st.write("---")
st.pyplot(fig)

# =====================================================================
# MASTER RAB FINAL
# =====================================================================
st.divider()
st.header("Laporan Rekapitulasi Anggaran Biaya")

if st.session_state.rekap_proyek:
    df = pd.DataFrame(st.session_state.rekap_proyek)
    display_data = []
    biaya_langsung = 0

    for kat in df['Kategori'].unique():
        df_kat = df[df['Kategori'] == kat]
        sub = df_kat['Total'].sum()
        biaya_langsung += sub
        
        for _, row in df_kat.iterrows():
            display_data.append({"Uraian": row['Pekerjaan'], "Volume": f"{row['Volume']} {row['Satuan']}", "Harga": f"Rp {row['AHSP']:,.0f}", "Jumlah": f"Rp {row['Total']:,.0f}"})
        display_data.append({"Uraian": f"SUB-TOTAL {kat.upper()}", "Volume": "", "Harga": "", "Jumlah": f"Rp {sub:,.0f}"})
        display_data.append({"Uraian": "", "Volume": "", "Harga": "", "Jumlah": ""})

    oh = biaya_langsung * (overhead_pct/100)
    ppn = (biaya_langsung + oh) * (ppn_pct/100)
    total_akhir = biaya_langsung + oh + ppn

    st.dataframe(pd.DataFrame(display_data), use_container_width=True)
    
    st.metric("A. TOTAL BIAYA LANGSUNG", f"Rp {biaya_langsung:,.0f}")
    st.metric(f"B. OVERHEAD & PROFIT ({overhead_pct}%)", f"Rp {oh:,.0f}")
    st.metric(f"C. PPN ({ppn_pct}%)", f"Rp {ppn:,.0f}")
    st.divider()
    st.metric("GRAND TOTAL PROYEK", f"Rp {total_akhir:,.0f}")

    if st.button("Kosongkan Master Rekap", use_container_width=True):
        st.session_state.rekap_proyek = []; st.rerun()
else:
    st.info("Belum ada data di rekapitulasi.")

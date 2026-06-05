# =====================================================================
# LOGIKA 7. PROTEKSI LERENG (SHOTCRETE & SOIL NAILING)
# =====================================================================
elif jenis_bangunan == "7. Proteksi Lereng (Shotcrete & Soil Nailing)":
    st.markdown("**Dimensi Lereng/Tebing**")
    col_l1, col_l2 = st.columns(2)
    panjang = col_l1.number_input("Panjang Memanjang Lereng (m)", value=50.0, key="7_p")
    tinggi_miring = col_l2.number_input("Panjang Miring Lereng (m)", value=15.0, help="Jarak dari kaki lereng ke puncak secara miring", key="7_tm")
    luas_lereng = panjang * tinggi_miring
    
    st.info(f"**Total Luas Permukaan Lereng:** {luas_lereng:,.2f} m²")

    st.markdown("**Spesifikasi Shotcrete**")
    t_shotcrete = st.number_input("Tebal Shotcrete (m)", value=0.15, key="7_ts")
    lapis_wiremesh = st.number_input("Jumlah Lapis Wiremesh M10", value=1, step=1, key="7_wm")
    
    st.markdown("**Spesifikasi Soil Nailing**")
    pakai_nailing = st.checkbox("Gunakan Soil Nailing?", value=True, key="7_cb_nail")
    
    if pakai_nailing:
        col_n1, col_n2 = st.columns(2)
        jarak_h = col_n1.number_input("Jarak Horizontal (m)", value=1.5, key="7_jh")
        jarak_v = col_n2.number_input("Jarak Vertikal (m)", value=1.5, key="7_jv")
        panjang_nail = st.number_input("Kedalaman Masuk Tanah (L) (m)", value=6.0, key="7_pn")
        
        # Hitung jumlah titik aktual
        jml_nailing = np.ceil(luas_lereng / (jarak_h * jarak_v))
        st.caption(f"*Estimasi kebutuhan: {int(jml_nailing)} Titik Soil Nailing*")
    else:
        jml_nailing = 0
        panjang_nail = 0

    st.markdown("**Pekerjaan & AHSP**")
    
    show_perapihan = st.checkbox("Pekerjaan Kupas/Perapihan Permukaan Lereng", value=True, key="7_cb_kupas")
    h_perapihan = st.number_input("AHSP Perapihan Lereng (Rp/m²)", value=25000.0, key="7_h_kupas") if show_perapihan else 0

    show_shotcrete = st.checkbox("Pekerjaan Shotcrete K-300 / K-350", value=True, key="7_cb_shot")
    h_shotcrete = st.number_input("AHSP Shotcrete (Rp/m³)", value=2850000.0, key="7_h_shot") if show_shotcrete else 0
    
    show_wiremesh = st.checkbox(f"Pemasangan Wiremesh M10 ({lapis_wiremesh} Lapis)", value=True, key="7_cb_wm")
    h_wiremesh = st.number_input("AHSP Wiremesh (Rp/m²)", value=115000.0, key="7_h_wm") if show_wiremesh else 0

    if pakai_nailing:
        show_nailing = st.checkbox("Pekerjaan Soil Nailing D25 Terpasang", value=True, key="7_cb_do_nail")
        h_nailing = st.number_input("AHSP Soil Nailing (Rp/Titik)", value=1250000.0, help="Harga per titik: mencakup Pengeboran, Besi D25, Grouting Epoxy/Semen, Bearing Plate, & Mur.", key="7_h_nail") if show_nailing else 0
        
        # Alternatif jika proyek Anda menggunakan hitungan per-meter kedalaman:
        # h_nailing = st.number_input("AHSP Soil Nailing (Rp/m')", value=250000.0)
        # item_to_add.append(["Soil Nailing D25", jml_nailing * panjang_nail, "m'", h_nailing])

    if show_perapihan: item_to_add.append(["Perapihan & Pembersihan Permukaan Lereng", luas_lereng, "m²", h_perapihan])
    if show_shotcrete: item_to_add.append(["Pekerjaan Shotcrete Beton", luas_lereng * t_shotcrete, "m³", h_shotcrete])
    
    # Faktor 1.1 untuk overlap wiremesh (10%)
    if show_wiremesh: item_to_add.append([f"Pemasangan Wiremesh M10 ({lapis_wiremesh} Lapis + Overlap)", luas_lereng * lapis_wiremesh * 1.1, "m²", h_wiremesh]) 
    
    if pakai_nailing and show_nailing:
        item_to_add.append([f"Soil Nailing D25 (Kedalaman {panjang_nail}m)", jml_nailing, "Titik", h_nailing])

    # Visualisasi Profil Lereng & Nailing
    fig, ax = plt.subplots(figsize=(6, 5))
    
    # Asumsi visual kemiringan lereng 60 derajat
    sudut = np.radians(60)
    h_visual = tinggi_miring * np.sin(sudut)
    w_visual = tinggi_miring * np.cos(sudut)
    
    # Polygon Tanah
    ax.add_patch(plt.Polygon([[0, h_visual], [w_visual, 0], [w_visual + 10, 0], [w_visual + 10, h_visual + 10], [0, h_visual + 10]], color='saddlebrown', alpha=0.3, label="Tanah/Tebing Asli"))
    
    # Shotcrete (Ketebalan Visual)
    dx = t_shotcrete * np.sin(sudut)
    dy = t_shotcrete * np.cos(sudut)
    pts_shot = [
        [0, h_visual], [w_visual, 0],
        [w_visual - dx, -dy], [-dx, h_visual - dy]
    ]
    ax.add_patch(plt.Polygon(pts_shot, color='gray', label=f'Shotcrete {t_shotcrete*100:.0f}cm'))
    
    if pakai_nailing:
        jarak_visual_v = tinggi_miring / 5  # Menampilkan 5 paku sebagai ilustrasi
        for i in range(1, 5):
            L_tempuh = i * jarak_visual_v
            
            # Koordinat titik di permukaan lereng
            x_surf = L_tempuh * np.cos(sudut)
            y_surf = h_visual - (L_tempuh * np.sin(sudut))
            
            # Koordinat titik kedalaman paku (tegak lurus masuk ke tanah)
            x_dalam = x_surf + (panjang_nail * np.sin(sudut))
            y_dalam = y_surf + (panjang_nail * np.cos(sudut))
            
            ax.plot([x_surf, x_dalam], [y_surf, y_dalam], color='black', lw=3) # Lubang bor / Grouting
            ax.plot([x_surf, x_dalam], [y_surf, y_dalam], color='red', lw=1.5, linestyle='--') # Besi D25
            ax.scatter([x_surf], [y_surf], color='blue', s=80, zorder=5) # Bearing plate
            
        ax.plot([], [], color='red', linestyle='--', label=f'Soil Nail D25 (L={panjang_nail}m)')
        ax.scatter([], [], color='blue', label='Bearing Plate')

    ax.set_xlim(-2, w_visual + panjang_nail + 2); ax.set_ylim(-2, h_visual + panjang_nail); ax.set_aspect('equal')
    ax.set_title("Visualisasi Penampang Proteksi Lereng")
    ax.grid(True, linestyle='--', alpha=0.6); ax.legend(loc='lower right')

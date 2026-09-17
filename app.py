import streamlit as st

st.set_page_config(page_title="DASHBOARD PLN UP3", page_icon="⚡", layout="wide")

# =========================================================
# 1. CSS SAKTI UNTUK MENYULAP TOMBOL MENJADI KOTAK (CARD)
# =========================================================
st.markdown("""
<style>
    /* Menyembunyikan styling tombol bawaan dan mengubahnya jadi kotak */
    div.stButton > button {
        height: 120px; /* Ukuran dipendekkan agar pas dengan teks tunggal */
        width: 100%;
        border-radius: 15px;
        border: 1px solid #333;
        background-color: #1E1E2F;
        color: white;
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    /* Efek menyala saat kursor diarahkan ke kotak (Hover) */
    div.stButton > button:hover {
        border-color: #00BFA5;
        background-color: #2A2A3D;
        transform: translateY(-5px);
        box-shadow: 0px 10px 20px rgba(0, 191, 165, 0.2);
        color: #00BFA5;
    }
    
    /* Mengatur teks judul agar lebih besar dan tebal */
    div.stButton > button p {
        font-size: 18px;
        font-weight: bold;
        margin: 0;
        white-space: pre-wrap; 
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. HEADER HALAMAN UTAMA
# =========================================================
st.markdown("<h1 style='text-align: center; color: #00BFA5;'>⚡ DASHBOARD PLN UP3</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #a1a1aa;'>Pusat Kendali & Analisis Terpadu | Padangsidimpuan</p>", unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)

# =========================================================
# 3. KOTAK MENU YANG BISA DIKLIK (BARIS 1)
# =========================================================
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊\nRESUME GANGGUAN", use_container_width=True):
        st.switch_page("pages/Resume_Gangguan.py")

with col2:
    if st.button("🛠️\nRESUME PEMELIHARAAN", use_container_width=True):
        st.switch_page("pages/Resume_Pemeliharaan.py")

with col3:
    if st.button("📝\nRPT RCT", use_container_width=True):
        st.switch_page("pages/RPT_RCT.py")

st.markdown("<br>", unsafe_allow_html=True)

# =========================================================
# 4. KOTAK MENU YANG BISA DIKLIK (BARIS 2)
# =========================================================
col4, col5, col6 = st.columns(3)

with col4:
    if st.button("🔄\nRESUME RECLOSERS", use_container_width=True):
        st.switch_page("pages/Resume_Reclosers.py")

with col5:
    if st.button("🔍\nINSPEKSI", use_container_width=True):
        st.switch_page("pages/Inspeksi.py")

with col6:
    if st.button("🏆\nTOP 10 PENYULANG KRONIS", use_container_width=True):
        st.switch_page("pages/Infografis_Kronis.py")
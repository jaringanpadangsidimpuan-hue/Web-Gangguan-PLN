import streamlit as st
import pandas as pd
import plotly.express as px
import io 

st.set_page_config(page_title="Resume Pemeliharaan", page_icon="🛠️", layout="wide")

# =========================================================
# 1. LOAD DATA (SUDAH DISESUAIKAN DENGAN EXCEL ASLI)
# =========================================================
@st.cache_data(ttl=60)
def fetch_google_sheets():
    # TIMPA LINK LAMAMU DENGAN LINK YANG BARU INI:
    sheet_url = "https://docs.google.com/spreadsheets/d/1OtEMnkxNkh0KfsxhywreqozLGPZmhCt5ynBi-UlzYHM/export?format=xlsx"
    
    return pd.read_excel(sheet_url, sheet_name='ENTRY EMERGENCY DAN HAR')

def load_data():
    if 'uploaded_excel' in st.session_state:
        excel_data = io.BytesIO(st.session_state['uploaded_excel'])
        df = pd.read_excel(excel_data, sheet_name='ENTRY EMERGENCY DAN HAR')
    else:
        df = fetch_google_sheets()
        
    # FIX 1: Bersihkan spasi tersembunyi (Misal: 'BULAN ' otomatis jadi 'BULAN')
    df.columns = df.columns.str.strip().str.upper()
    
    # Proses pembersihan data baris kosong
    if 'TANGGAL PADAM' in df.columns and 'KODE PENYULANG' in df.columns:
        df = df.dropna(subset=['TANGGAL PADAM', 'KODE PENYULANG'])
        df['TANGGAL PADAM'] = pd.to_datetime(df['TANGGAL PADAM'], errors='coerce').dt.date
        
    # FIX 2: Menyulap teks "EMERGENCY"/"HAR" di Excel menjadi Angka 1 agar grafik bisa menjumlahkannya
    kategori_asli = ['EMERGENCY', 'HAR', 'DEFISIT', 'TRANSMISI', 'UFR']
    for col in kategori_asli:
        if col in df.columns:
            # Jika sel ada isinya (tidak kosong), hitung sebagai 1, kalau kosong 0
            df[col + '_VAL'] = df[col].notna().astype(int)
            
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Gagal menarik data! Error: {e}")
    st.stop()

# =========================================================
# 2. SUB-MENU KIRI ATAS
# =========================================================
sub_menu = st.radio(
    "Pilih Tampilan:",
    ["📊 Utama: Grafik & Logsheet", "🥧 Detail: Bulan & ULP"],
    horizontal=True,
    label_visibility="collapsed"
)

st.title("🛠️ RESUME PEMELIHARAAN")

# =========================================================
# 3. AREA FILTER
# =========================================================
col_f1, col_f2, col_f3, col_f4 = st.columns(4)
with col_f1:
    list_penyulang = ["Semua"] + list(df['KODE PENYULANG'].dropna().unique())
    filter_penyulang = st.selectbox("KODE PENYULANG", list_penyulang)
with col_f2:
    list_tanggal = ["Semua"] + list(df['TANGGAL PADAM'].dropna().unique())
    filter_tanggal = st.selectbox("TANGGAL", list_tanggal)
with col_f3:
    list_ulp = ["Semua"] + list(df['ULP'].dropna().unique())
    filter_ulp = st.selectbox("ULP", list_ulp)
with col_f4:
    list_bulan = ["Semua"] + list(df['BULAN'].dropna().unique())
    filter_bulan = st.selectbox("BULAN", list_bulan)

df_filtered = df.copy()
if filter_penyulang != "Semua": df_filtered = df_filtered[df_filtered['KODE PENYULANG'] == filter_penyulang]
if filter_tanggal != "Semua": df_filtered = df_filtered[df_filtered['TANGGAL PADAM'] == filter_tanggal]
if filter_ulp != "Semua": df_filtered = df_filtered[df_filtered['ULP'] == filter_ulp]
if filter_bulan != "Semua": df_filtered = df_filtered[df_filtered['BULAN'] == filter_bulan]

st.markdown("---")

# =========================================================
# 4. LOGIKA TAMPILAN BERDASARKAN MENU
# =========================================================
if sub_menu == "📊 Utama: Grafik & Logsheet":
    
    st.subheader("Grafik Total Pemeliharaan per Penyulang")
    kategori_val = ['EMERGENCY_VAL', 'HAR_VAL', 'DEFISIT_VAL', 'TRANSMISI_VAL', 'UFR_VAL']
    kategori_ada = [k for k in kategori_val if k in df_filtered.columns]
    
    if kategori_ada:
        bar_data = df_filtered.groupby('KODE PENYULANG')[kategori_ada].sum().reset_index()
        bar_data_melted = bar_data.melt(id_vars='KODE PENYULANG', value_vars=kategori_ada, 
                                        var_name='JENIS', value_name='JUMLAH')
        # Hilangkan kata '_VAL' agar nama grafik terlihat rapi
        bar_data_melted['JENIS'] = bar_data_melted['JENIS'].str.replace('_VAL', '')

        warna_custom = {
            'EMERGENCY': '#FF9900', 'HAR': '#2CA02C', 'DEFISIT': '#1F77B4', 
            'TRANSMISI': '#9467BD', 'UFR': '#17BECF'
        }

        fig_bar = px.bar(bar_data_melted, x='KODE PENYULANG', y='JUMLAH', color='JENIS',
                         barmode='stack', text_auto=True, color_discrete_map=warna_custom)
        fig_bar.update_layout(xaxis_title="PENYULANG", yaxis_title="JUMLAH")
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    st.subheader("LOGSHEET DATA")
    kolom_tabel = ['ULP', 'KODE PENYULANG', 'SECTION', 'TANGGAL PADAM', 'JAM PADAM', 'TANGGAL NYALA', 'JAM NYALA', 'EMERGENCY', 'HAR', 'TRANSMISI', 'UFR']
    kolom_tersedia = [k for k in kolom_tabel if k in df_filtered.columns]
    st.dataframe(df_filtered[kolom_tersedia], use_container_width=True)

elif sub_menu == "🥧 Detail: Bulan & ULP":
    
    st.info("💡 **Tips:** Klik langsung pada **WARNA POTONGAN BULATAN** untuk memfilter data tabel di bawah.")
    
    col_pie1, col_pie2 = st.columns(2)
    clicked_bulan = None
    clicked_ulp = None

    with col_pie1:
        st.subheader("BERDASARKAN BULAN")
        if 'BULAN' in df_filtered.columns:
            bulan_counts = df_filtered['BULAN'].value_counts().reset_index()
            bulan_counts.columns = ['BULAN', 'JUMLAH']
            fig_bulan = px.pie(bulan_counts, values='JUMLAH', names='BULAN', hole=0.4,
                               color_discrete_sequence=px.colors.qualitative.Pastel)
            
            event_bulan = st.plotly_chart(fig_bulan, use_container_width=True, on_select="rerun", selection_mode="points", key="pie_bulan")
            if event_bulan and len(event_bulan.selection.points) > 0:
                clicked_bulan = event_bulan.selection.points[0].get("label")

    with col_pie2:
        st.subheader("BERDASARKAN ULP")
        if 'ULP' in df_filtered.columns:
            ulp_counts = df_filtered['ULP'].value_counts().reset_index()
            ulp_counts.columns = ['ULP', 'JUMLAH']
            fig_ulp = px.pie(ulp_counts, values='JUMLAH', names='ULP', hole=0.4,
                             color_discrete_sequence=px.colors.qualitative.Set2)
            
            event_ulp = st.plotly_chart(fig_ulp, use_container_width=True, on_select="rerun", selection_mode="points", key="pie_ulp")
            if event_ulp and len(event_ulp.selection.points) > 0:
                clicked_ulp = event_ulp.selection.points[0].get("label")

    # Proses Filter Otomatis
    df_detail = df_filtered.copy()
    if clicked_bulan:
        st.success(f"✅ Filter Aktif - Bulan: **{clicked_bulan}**")
        df_detail = df_detail[df_detail['BULAN'] == clicked_bulan]
    if clicked_ulp:
        st.success(f"✅ Filter Aktif - ULP: **{clicked_ulp}**")
        df_detail = df_detail[df_detail['ULP'] == clicked_ulp]

    st.markdown("---")
    st.subheader("DATA TERKAIT (Tabel Otomatis Terfilter)")
    kolom_tabel_detail = ['ULP', 'KODE PENYULANG', 'TANGGAL PADAM', 'BULAN', 'EMERGENCY', 'HAR']
    kolom_tersedia_detail = [k for k in kolom_tabel_detail if k in df_detail.columns]
    
    if len(df_detail) == 0:
        st.warning("⚠️ Tidak ada data untuk filter tersebut.")
    else:
        st.dataframe(df_detail[kolom_tersedia_detail], use_container_width=True)
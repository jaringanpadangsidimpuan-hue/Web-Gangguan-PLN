import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi Halaman
st.set_page_config(page_title="Resume Recloser", page_icon="⚡", layout="wide")

# =========================================================
# 1. LOAD DATA GOOGLE SHEETS
# =========================================================
@st.cache_data(ttl=60)
def fetch_google_sheets():
    # Menggunakan link data gangguan yang sama
    sheet_url = "https://docs.google.com/spreadsheets/d/1OtEMnkxNkh0KfsxhywreqozLGPZmhCt5ynBi-UlzYHM/export?format=xlsx"
    return pd.read_excel(sheet_url, sheet_name='ENTRI GANGGUAN')

def load_data():
    df = fetch_google_sheets()
    df.columns = df.columns.str.strip().str.upper()
    
    if 'TANGGAL PADAM' in df.columns:
        df['TANGGAL PADAM'] = pd.to_datetime(df['TANGGAL PADAM'], errors='coerce').dt.date
        
    if 'TEMPORER' in df.columns: df['TEMPORER'] = df['TEMPORER'].fillna(0)
    if 'PERMANEN' in df.columns: df['PERMANEN'] = df['PERMANEN'].fillna(0)
    
    # Asumsi: Jika di excel nama kolomnya bukan RECLOSER tapi SECTION, kita buat salinannya agar rapi
    if 'NAMA SECTION' in df.columns and 'RECLOSER' not in df.columns:
        df['RECLOSER'] = df['NAMA SECTION']
        
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Gagal menarik data! Error: {e}")
    st.stop()

# =========================================================
# 2. MASTER DROPDOWN: PILIH ULP (REPLIKASI LOOKER STUDIO)
# =========================================================
st.markdown("### 📍 Pilih Lokasi Dashboard")
daftar_ulp = ["SIDIMPUAN KOTA", "SIPIROK", "SIBUHUAN", "GUNUNG TUA", "PANYABUNGAN", "KOTANOPAN", "NATAL"]

# Ini adalah dropdown utama yang akan mengubah seluruh isi halaman
selected_ulp = st.selectbox("Pilih ULP:", daftar_ulp, label_visibility="collapsed")

# =========================================================
# 3. JUDUL DINAMIS SESUAI ULP YANG DIPILIH
# =========================================================
st.markdown("---")
# Menggunakan HTML/CSS sedikit agar tampilannya mirip desain aslimu (warna dan logo PLN)
st.markdown(f"""
    <div style='background-color:#E8F5E9; padding:15px; border-radius:10px; border-left: 8px solid #00BFA5;'>
        <h2 style='color:#004D40; margin:0;'>⚡ ULP {selected_ulp}</h2>
    </div>
    <br>
""", unsafe_allow_html=True)

# Filter Dataframe UTAMA berdasarkan ULP yang dipilih
df_ulp = df[df['ULP'] == selected_ulp]

# =========================================================
# 4. FILTER TAMBAHAN (RECLOSER, TANGGAL, BULAN)
# =========================================================
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1: 
    filter_recloser = st.selectbox("RECLOSER", ["Semua"] + list(df_ulp['RECLOSER'].dropna().unique()))
with col_f2: 
    filter_tanggal = st.selectbox("TANGGAL", ["Semua"] + list(df_ulp['TANGGAL PADAM'].dropna().unique()))
with col_f3: 
    filter_bulan = st.selectbox("BULAN", ["Semua"] + list(df_ulp['BULAN'].dropna().unique()))

# Terapkan Filter Tambahan
df_filtered = df_ulp.copy()
if filter_recloser != "Semua": df_filtered = df_filtered[df_filtered['RECLOSER'] == filter_recloser]
if filter_tanggal != "Semua": df_filtered = df_filtered[df_filtered['TANGGAL PADAM'] == filter_tanggal]
if filter_bulan != "Semua": df_filtered = df_filtered[df_filtered['BULAN'] == filter_bulan]

st.markdown("---")

# =========================================================
# 5. VISUALISASI DATA (GRAFIK & TABEL)
# =========================================================

# ---> A. BAR CHART: MONITORING RECLOSER <---
st.markdown(f"<h3 style='text-align: center;'>MONITORING RECLOSER - ULP {selected_ulp}</h3>", unsafe_allow_html=True)

if not df_filtered.empty:
    bar_data = df_filtered.groupby('RECLOSER')[['TEMPORER', 'PERMANEN']].sum().reset_index()
    bar_data_melted = bar_data.melt(id_vars='RECLOSER', value_vars=['TEMPORER', 'PERMANEN'], var_name='JENIS', value_name='JUMLAH')
    
    fig_bar = px.bar(bar_data_melted, x='RECLOSER', y='JUMLAH', color='JENIS',
                     barmode='group', text_auto=True,
                     color_discrete_map={'TEMPORER': '#F5B041', 'PERMANEN': '#5DADE2'}) # Warna menyesuaikan video
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.warning(f"Belum ada data gangguan Recloser untuk ULP {selected_ulp}.")

st.markdown("---")

# ---> B. PIE CHART: INDIKASI & PENYEBAB <---
col_pie1, col_pie2 = st.columns(2)

with col_pie1:
    st.markdown("<h4 style='text-align: center;'>INDIKASI</h4>", unsafe_allow_html=True)
    if 'RELAY YANG BEKERJA' in df_filtered.columns and not df_filtered.empty:
        relay_counts = df_filtered['RELAY YANG BEKERJA'].value_counts().reset_index()
        relay_counts.columns = ['INDIKASI', 'JUMLAH']
        fig_relay = px.pie(relay_counts, values='JUMLAH', names='INDIKASI', hole=0.5,
                           color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_relay, use_container_width=True)

with col_pie2:
    st.markdown("<h4 style='text-align: center;'>PENYEBAB</h4>", unsafe_allow_html=True)
    if 'PENYEBAB' in df_filtered.columns and not df_filtered.empty:
        penyebab_counts = df_filtered['PENYEBAB'].value_counts().reset_index()
        penyebab_counts.columns = ['PENYEBAB', 'JUMLAH']
        fig_penyebab = px.pie(penyebab_counts, values='JUMLAH', names='PENYEBAB', hole=0.5,
                              color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig_penyebab, use_container_width=True)

st.markdown("---")

# ---> C. TABEL DETAIL GANGGUAN <---
st.markdown("<h3 style='text-align: center; background-color: #A3E4D7; padding: 10px; border-radius: 5px;'>DETAIL GANGGUAN</h3>", unsafe_allow_html=True)

kolom_tabel = ['TANGGAL PADAM', 'PENYULANG', 'RECLOSER', 'PENYEBAB', 'R', 'S', 'T', 'N']
kolom_tersedia = [k for k in kolom_tabel if k in df_filtered.columns]

if not df_filtered.empty:
    st.dataframe(df_filtered[kolom_tersedia], use_container_width=True, hide_index=True)
import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="RPT RCT", page_icon="📝", layout="wide")

# =========================================================
# URL WEBHOOK SUDAH DIPASANG SESUAI PERMINTAANMU LEKK!
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyQAbjD571sZCv7vr4YGaQsmGyhFnN2HeRNq9he4byJP8sKQwjhImrr3tElIbgs56_5/exec"
# =========================================================

@st.cache_data(ttl=60)
def fetch_data_rpt():
    sheet_url = "https://docs.google.com/spreadsheets/d/1SC5zEQdb59cjyaBvFNWG5USjP6rVsg4tHNb6iSd669U/export?format=xlsx"
    return pd.read_excel(sheet_url, sheet_name=0)

try:
    df_rpt = fetch_data_rpt()
    df_rpt.columns = df_rpt.columns.astype(str).str.strip().str.upper()
except Exception as e:
    st.error(f"❌ Gagal menarik data! Pastikan akses link Google Sheets sudah 'Siapa saja yang memiliki link'. Error: {e}")
    st.stop()

# Hanya ada 2 pilihan (Tanpa Input Baru)
sub_menu = st.radio("Pilih Tampilan:", ["📊 Tampilan Data RPT RCT", "✏️ Edit / Hapus Data"], horizontal=True, label_visibility="collapsed")

st.title("📝 LAPORAN RPT RCT")
st.markdown("---")

if sub_menu == "📊 Tampilan Data RPT RCT":
    st.info(f"📊 **Total Laporan:** {len(df_rpt)} baris data.")
    st.dataframe(df_rpt, use_container_width=True, hide_index=True)

elif sub_menu == "✏️ Edit / Hapus Data":
    if "akses_rpt" not in st.session_state: st.session_state["akses_rpt"] = False

    if not st.session_state["akses_rpt"]:
        st.error("🔒 **AREA TERBATAS ADMIN**")
        with st.form("form_login_rpt"):
            pin_input = st.text_input("🔑 Masukkan PIN Akses:", type="password")
            if st.form_submit_button("Buka Kunci"):
                if pin_input == "PLNUP3": 
                    st.session_state["akses_rpt"] = True
                    st.rerun()
                else: st.error("❌ PIN salah!")

    if st.session_state["akses_rpt"]:
        if st.button("🔒 Tutup Akses (Logout)"):
            st.session_state["akses_rpt"] = False
            st.rerun()

        st.warning("⚠️ **Mode Edit/Hapus Aktif.** Perubahan langsung memengaruhi Google Sheets RPT RCT!")
        
        # Menggunakan 2 Kolom Pertama di Excel-mu sebagai Kunci Pencarian Data
        kolom_1 = df_rpt.columns[0] if len(df_rpt.columns) > 0 else "KOLOM_1"
        kolom_2 = df_rpt.columns[1] if len(df_rpt.columns) > 1 else "KOLOM_2"
        
        st.markdown("### 🔍 1. Cari Data")
        pilih_k1 = st.selectbox(f"1. Pilih {kolom_1}", df_rpt[kolom_1].dropna().unique())
        df_filter_1 = df_rpt[df_rpt[kolom_1] == pilih_k1]
        pilih_k2 = st.selectbox(f"2. Pilih {kolom_2}", df_filter_1[kolom_2].astype(str).unique())
        df_target = df_filter_1[df_filter_1[kolom_2].astype(str) == pilih_k2]

        if not df_target.empty:
            data_asli = df_target.iloc[0]
            st.markdown("---")
            st.markdown("### 🛠️ 2. Edit Data")
            
            with st.form("form_edit_hapus_rpt"):
                # FITUR CANGGIH: Membuat Form Input Otomatis sebanyak Kolom yang ada di Excel
                edit_values = {}
                cols = st.columns(3)
                for i, col_name in enumerate(df_rpt.columns):
                    with cols[i % 3]:
                        val = data_asli.get(col_name, '')
                        val = "" if pd.isna(val) else str(val)
                        edit_values[col_name] = st.text_input(col_name, value=val)
                
                st.markdown("---")
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.form_submit_button("🔄 Update Perubahan", use_container_width=True):
                        with st.spinner("Memperbarui data..."):
                            payload_update = {
                                "action": "update", "kunci_pencarian_1": str(pilih_k1), "kunci_pencarian_2": str(pilih_k2), "data_baru": edit_values
                            }
                            try:
                                req = requests.post(WEBHOOK_URL, json=payload_update)
                                if "Success" in req.text: st.success("✅ Berhasil di-update!")
                                else: st.error(req.text)
                            except Exception as e: st.error(e)
                with col_btn2:
                    if st.form_submit_button("❌ Hapus Permanen", use_container_width=True):
                        with st.spinner("Menghapus data..."):
                            payload_delete = {
                                "action": "delete", "kunci_pencarian_1": str(pilih_k1), "kunci_pencarian_2": str(pilih_k2)
                            }
                            try:
                                req = requests.post(WEBHOOK_URL, json=payload_delete)
                                if "Success" in req.text: st.success("🗑️ Berhasil dihapus!")
                                else: st.error(req.text)
                            except Exception as e: st.error(e)
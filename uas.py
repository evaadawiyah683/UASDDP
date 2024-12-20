import streamlit as st
import datetime
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Tabungan:
    """
    A class to manage savings with transactions tracking.
    
    Attributes:
        tujuan (str): The savings goal
        saldo (float): Current balance
        rekapan (List[Dict]): List of transaction records
    """
    tujuan: str = ''
    saldo: float = 0
    rekapan: List[Dict] = field(default_factory=list)

    def setor(self, jumlah: float) -> str:
        """
        Deposit money into savings.
        """
        if jumlah <= 0:
            return "Jumlah setor harus lebih besar dari 0."
        
        self.saldo += jumlah
        self.rekapan.append({
            'Tipe': 'Setor', 
            'Jumlah': jumlah, 
            'Tanggal': datetime.date.today()
        })
        return f'Berhasil menyetor Rp {jumlah:,.0f}. Saldo sekarang: Rp {self.saldo:,.0f}.'

    def tarik(self, jumlah: float) -> str:
        """
        Withdraw money from savings.
        """
        if jumlah <= 0:
            return "Jumlah tarik harus lebih besar dari 0."
        
        if jumlah > self.saldo:
            return "Saldo tidak cukup untuk penarikan."
        
        self.saldo -= jumlah
        self.rekapan.append({
            'Tipe': 'Tarik', 
            'Jumlah': jumlah, 
            'Tanggal': datetime.date.today()
        })
        return f'Berhasil menarik Rp {jumlah:,.0f}. Saldo sekarang: Rp {self.saldo:,.0f}.'

# Initialize session state for savings
if 'tabungan' not in st.session_state:
    st.session_state.tabungan = Tabungan()

def halaman_beranda():
    """
    Beranda / Dashboard Halaman
    """
    st.title('Tabungan Impian')
    
    # Goal Setting Section
    st.header('Pengaturan Tujuan Tabungan')
    
    # Goal Input
    col1, col2 = st.columns(2)
    with col1:
        goal_name = st.text_input('Tujuan Tabungan', 
                                  value=st.session_state.tabungan.tujuan, 
                                  key='goal_input')
    with col2:
        goal_amount = st.number_input('Target Dana (Rp)', 
                                      min_value=0, 
                                      value=0)
    
    # Timeline Section
    col3, col4 = st.columns(2)
    with col3:
        months = st.number_input('Jangka Waktu (Bulan)', 
                                 min_value=1, 
                                 value=12)
    with col4:
        start_date = st.date_input('Tanggal Mulai', 
                                   datetime.date.today())
    
    # Save Goal Button
    if st.button('Simpan Tujuan'):
        # Update tabungan object with new goal
        st.session_state.tabungan.tujuan = goal_name
        
        # Calculate monthly savings recommendation
        if goal_amount > 0 and months > 0:
            monthly_savings = goal_amount / months
            st.success(f'Anda perlu menabung sebesar Rp {monthly_savings:,.0f} per bulan.')
        
        # Calculate end date
        end_date = start_date + datetime.timedelta(weeks=4*months)
        st.info(f'Target Pencapaian: {end_date.strftime("%d %B %Y")}')

def halaman_setor():
    """
    Halaman Setor Dana
    """
    st.title('Setor Dana')
    
    # Saldo Saat Ini
    st.metric('Saldo Saat Ini', f'Rp {st.session_state.tabungan.saldo:,.0f}')
    
    # Setor Dana Form
    with st.form('setor_form'):
        jumlah_setor = st.number_input('Jumlah Dana Disetor (Rp)', min_value=0)
        submitted = st.form_submit_button('Setor')
        
        if submitted:
            result = st.session_state.tabungan.setor(jumlah_setor)
            st.success(result)

def halaman_tarik():
    """
    Halaman Tarik Dana
    """
    st.title('Tarik Dana')
    
    # Saldo Saat Ini
    st.metric('Saldo Saat Ini', f'Rp {st.session_state.tabungan.saldo:,.0f}')
    
    # Tarik Dana Form
    with st.form('tarik_form'):
        jumlah_tarik = st.number_input('Jumlah Dana Ditarik (Rp)', min_value=0)
        submitted = st.form_submit_button('Tarik')
        
        if submitted:
            result = st.session_state.tabungan.tarik(jumlah_tarik)
            st.success(result)

def halaman_rekapan():
    """
    Halaman Rekapan Transaksi
    """
    st.title('Rekapan Transaksi')
    
    # Saldo Saat Ini
    st.metric('Total Saldo', f'Rp {st.session_state.tabungan.saldo:,.0f}')
    
    # Tabel Rekapan
    if st.session_state.tabungan.rekapan:
        df_rekapan = pd.DataFrame(st.session_state.tabungan.rekapan)
        
        # Format kolom
        df_rekapan['Jumlah'] = df_rekapan['Jumlah'].apply(lambda x: f'Rp {x:,.0f}')
        
        # Tampilkan tabel
        st.table(df_rekapan)
    else:
        st.write("Belum ada transaksi.")
    
    # Grafik Ringkasan
    if st.session_state.tabungan.rekapan:
        st.subheader('Ringkasan Transaksi')
        
        # Hitung total setor dan tarik
        total_setor = sum(t['Jumlah'] for t in st.session_state.tabungan.rekapan if t['Tipe'] == 'Setor')
        total_tarik = sum(t['Jumlah'] for t in st.session_state.tabungan.rekapan if t['Tipe'] == 'Tarik')
        
        # Buat DataFrame untuk pie chart
        summary_df = pd.DataFrame({
            'Jenis': ['Setor', 'Tarik'],
            'Jumlah': [total_setor, total_tarik]
        })
        
        # Tampilkan pie chart
        st.bar_chart(summary_df.set_index('Jenis'))

def main():
    """
    Fungsi utama untuk navigasi aplikasi
    """
    # Sidebar untuk navigasi
    st.sidebar.title('🏦 Menu Tabungan')
    
    # Pilihan navigasi
    menu = st.sidebar.radio('Pilih Halaman', [
        'Beranda', 
        'Setor Dana', 
        'Tarik Dana', 
        'Rekapan Transaksi'
    ])
    
    # Routing halaman
    if menu == 'Beranda':
        halaman_beranda()
    elif menu == 'Setor Dana':
        halaman_setor()
    elif menu == 'Tarik Dana':
        halaman_tarik()
    elif menu == 'Rekapan Transaksi':
        halaman_rekapan()

    # Tambahkan tips di bawah
    st.sidebar.markdown('### 💡 Tips Menabung')
    st.sidebar.markdown("""
    1. Tetapkan tujuan yang jelas
    2. Simpan secara konsisten
    3. Pantau perkembangan tabungan
    """)

if __name__ == "_main_":
    # Konfigurasi halaman Streamlit
    st.set_page_config(
        page_title='Aplikasi Tabungan Impian',
        page_icon='💰',
        layout='wide'
    )
    
    # Jalankan aplikasi utama
main()
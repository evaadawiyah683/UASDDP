import streamlit as st
import datetime
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Dict
import base64

@dataclass
class Tabungan:
    """
    A class to manage savings with transactions tracking.
    
    Attributes:
        tujuan (str): The savings goal
        saldo (float): Current balance
        bulan (int): Target month
        rekapan (List[Dict]): List of transaction records
    """
    tujuan: str = ''
    saldo: float = 0
    target: float = 0
    bulan: int = 0
    rekapan: List[Dict] = field(default_factory=list)

    def set_target(self, jumlah: float):
        self.target = jumlah

    def get_target(self):
        return self.target

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
    
# Streamlit UI

# Fungsi untuk memuat gambar dari file lokal dan mengkonversinya ke base64
def load_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()
    
# Memuat gambar latar belakang
image_path = "bank.jpg"
image_base64 = load_image(image_path)

# Menambahkan CSS untuk latar belakang gambar
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url('data:image/jpeg;base64,{image_base64}');
        background-size: cover;
        background-position: center;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state for savings
if 'tabungan_dict' not in st.session_state:
    st.session_state.tabungan_dict = {}

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
        goal_name = st.text_input('Tujuan Tabungan', key='goal_input')
    with col2:
        goal_amount = st.number_input('Target Dana (Rp)', min_value=0, value=0)
    
    # Timeline Section
    col3, col4 = st.columns(2)
    with col3:
        months = st.number_input('Jangka Waktu (Bulan)', min_value=1, value=12)
    with col4:
        start_date = st.date_input('Tanggal Mulai', datetime.date.today())
    
    # Save Goal Button
    if st.button('Simpan Tujuan'):
        if goal_name:
            # Create new Tabungan object and add to session state
            new_tabungan = Tabungan(tujuan=goal_name, target=goal_amount)
            st.session_state.tabungan_dict[goal_name] = new_tabungan
            new_tabungan.bulan = months

            # Calculate monthly savings recommendation
            if goal_amount > 0 and months > 0:
                monthly_savings = goal_amount / months
                st.success(f'Anda perlu menabung sebesar Rp {monthly_savings:,.0f} per bulan.')
            
            # Calculate end date
            end_date = start_date + datetime.timedelta(weeks=4*months)
            st.info(f'Target Pencapaian: {end_date.strftime("%d %B %Y")}')
        else:
            st.error('Nama tujuan tabungan tidak boleh kosong.')

def halaman_setor():
    """
    Halaman Setor Dana
    """
    st.title('Setor Dana')
    
    # Select Tabungan
    tabungan_list = list(st.session_state.tabungan_dict.keys())
    selected_tabungan = st.selectbox('Pilih Tabungan', tabungan_list)
    
    if selected_tabungan:
        tabungan = st.session_state.tabungan_dict[selected_tabungan]
        
        # Saldo Saat Ini
        st.metric('Saldo Saat Ini', f'Rp {tabungan.saldo:,.0f}')
        
        # Setor Dana Form
        with st.form('setor_form'):
            jumlah_setor = st.number_input('Jumlah Dana Disetor (Rp)', min_value=0)
            submitted = st.form_submit_button('Setor')
            
            if submitted:
                result = tabungan.setor(jumlah_setor)
                st.success(result)

def halaman_tarik():
    """
    Halaman Tarik Dana
    """
    st.title('Tarik Dana')
    
    # Select Tabungan
    tabungan_list = list(st.session_state.tabungan_dict.keys())
    selected_tabungan = st.selectbox('Pilih Tabungan', tabungan_list)
    
    if selected_tabungan:
        tabungan = st.session_state.tabungan_dict[selected_tabungan]
        
        # Saldo Saat Ini
        st.metric('Saldo Saat Ini', f'Rp {tabungan.saldo:,.0f}')
        
        # Tarik Dana Form
        with st.form('tarik_form'):
            jumlah_tarik = st.number_input('Jumlah Dana Ditarik (Rp)', min_value=0)
            submitted = st.form_submit_button('Tarik')
            
            if submitted:
                result = tabungan.tarik(jumlah_tarik)
                st.success(result)

def halaman_rekapan():
    """
    Halaman Rekapan Transaksi
    """
    st.title('Rekapan Transaksi')
    
    # Pastikan ada data tabungan
    if not st.session_state.tabungan_dict:
        st.write("Belum ada tabungan yang tercatat.")
        return

    # Loop untuk menampilkan semua tabungan
    for tabungan_name, tabungan in st.session_state.tabungan_dict.items():
        st.subheader(f'Tabungan: {tabungan_name}')
        
        total_saldo = tabungan.saldo
        target_saldo = tabungan.target
        bulan = tabungan.bulan  # Jangka waktu dalam bulan
        
        # Hitung tanggal target berdasarkan bulan
        if bulan > 0:
            today = datetime.date.today()
            target_date = today + datetime.timedelta(weeks=4 * bulan)  # Estimasi 4 minggu per bulan
            days_remaining = (target_date - today).days
            
            # Format pesan waktu tersisa
            if days_remaining > 0:
                time_remaining_msg = f"{days_remaining} hari lagi"
            elif days_remaining == 0:
                time_remaining_msg = "Hari ini adalah tanggal target."
            else:
                time_remaining_msg = f"Waktu target sudah lewat {abs(days_remaining)} hari."
        else:
            target_date = None
            time_remaining_msg = "Tidak ada jangka waktu yang ditetapkan."
        
        # Tampilkan metrik saldo dan target
        st.metric('Total Saldo', f'Rp {total_saldo:,.0f}')
        st.metric('Kurang Saldo', f'Rp {(total_saldo - target_saldo):,.0f}')
        st.metric('Tanggal Target', target_date.strftime('%d %B %Y') if target_date else "Belum ditetapkan")
        st.metric('Sisa Waktu', time_remaining_msg)
        
        # Tabel Rekapan
        if tabungan.rekapan:
            df_rekapan = pd.DataFrame(tabungan.rekapan)
            
            # Format kolom
            df_rekapan['Jumlah'] = df_rekapan['Jumlah'].apply(lambda x: f'Rp {x:,.0f}')
            df_rekapan['Tanggal'] = df_rekapan['Tanggal'].apply(lambda x: x.strftime('%d %B %Y'))
            
            # Tampilkan tabel
            st.table(df_rekapan)
        else:
            st.write("Belum ada transaksi.")


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

if __name__ == "__main__":
    # Konfigurasi halaman Streamlit
    # st.set_page_config(
    # page_title='Aplikasi Tabungan Impian',
    # page_icon='💰',
    # layout='wide'
    # )
    
    # Jalankan aplikasi utama
    main()
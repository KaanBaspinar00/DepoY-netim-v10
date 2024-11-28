import streamlit as st
import utils_11  # Adjusted import to utils_1

# The database and necessary files are initialized in utils_1.py when it's imported.

# Set up the main page
st.title("Depo Takip Sistemi")

st.write("""
Hoş geldiniz! Bu uygulama, depo yönetimini kolaylaştırmak ve varlıkları etkili bir şekilde takip etmek için tasarlanmıştır.

Lütfen sol taraftaki menüyü kullanarak istediğiniz sayfaya gidin:

- **Admin Paneli:** QR kodları oluşturabilir, varlıkları yönetebilir ve raporları görüntüleyebilirsiniz.
- **Çalışan Paneli:** QR kodlarını tarayarak varlıkları kullanabilir veya işlem için gönderebilirsiniz.
- **Asistanım:** Depo takibi hakkında yardımcı olabilecek yapay zeka aracı için kullanılabilir.
- **Is Takibi:** Yöneticiler arası hızlı iletişimi sağlamak ve iş kontrolünü sağlamak için kullanılabilir.
""")

# User Authentication
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.subheader("Giriş Yap")
    username = st.text_input("Kullanıcı Adı")
    password = st.text_input("Şifre", type="password")
    if st.button("Giriş"):
        role = utils_11.authenticate_user(username, password)
        if role:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = role
            st.success(f"Hoş geldiniz, {username}!")
            st.rerun()
        else:
            st.error("Geçersiz kullanıcı adı veya şifre.")
else:
    st.write(f"Hoş geldiniz, {st.session_state.username}!")
    if st.button("Çıkış Yap"):
        st.session_state.logged_in = False
        st.session_state.username = ''
        st.session_state.role = ''
        st.rerun()

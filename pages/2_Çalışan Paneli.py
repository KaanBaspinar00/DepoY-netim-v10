# 2_Çalışan Paneli.py

import streamlit as st
import utils_11
from pyzbar.pyzbar import decode
from PIL import Image
from datetime import datetime
from io import BytesIO
# User Authentication

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

USERNAME = ""
if not st.session_state.logged_in:
    st.subheader("Giriş Yap")
    username = st.text_input("Kullanıcı Adı")
    password = st.text_input("Şifre", type="password")
    if st.button("Giriş"):
        role = utils_11.authenticate_user(username, password)
        if role:
            USERNAME = username
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



# ---------------------- User Authentication Check ----------------------
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("Bu sayfayı görüntülemek için lütfen giriş yapın.")
    st.stop()
else:
    if st.session_state.role not in ['admin', 'worker']:
        st.error("Bu sayfayı görüntülemek için yetkiniz yok.")
        st.stop()

# ---------------------- Streamlit Page Configuration ----------------------
# Set up the title for the worker page
st.title("Çalışan Paneli - Varlık Tarama ve İşlemleri")


# ---------------------- Function to Display Asset Details ----------------------

def display_asset_details(asset):
    """Display asset details and provide options to perform actions."""
    try:
        st.write(f"**ID:** {asset.get('id', 'N/A')}")
        st.write(f"**Varlık Adı:** {asset.get('varlık_adı', 'N/A')}")
        st.write(f"**Gönderen:** {asset.get('gönderen', 'N/A')}")
        st.write(f"**Alıcı:** {asset.get('alıcı', 'N/A')}")
        st.write(f"**Miktar:** {asset.get('miktar', 0)} {asset.get('unit', '')}")
        st.write(f"**Zaman:** {asset.get('zaman', 'N/A')}")

        # Get the quantity from the asset data
        quantity = asset.get('quantity', asset.get('miktar', 0))

        # Display current stock
        st.write(f"**Mevcut Stok:** {quantity} {asset.get('unit', '')}")

        # Provide action options
        st.subheader("Aksiyon Seçin")
        action = st.selectbox(
            "Aksiyon",
            ["Seçiniz", "Kullan", "İşlem İçin Gönder", "İşlemden Gelen Malı Geri Al"]
        )

        if action != "Seçiniz":
            partner_firm = ""
            notes = st.text_area("Notlar")

            if action == "İşlem İçin Gönder":
                partner_firm = st.text_input("Firma Adı")
            elif action == "İşlemden Gelen Malı Geri Al":
                partner_firm = st.text_input("Gönderen Firma Adı")

            worker_name_2 = st.text_input("Çalışan Adı")
            worker_name = st.session_state.username + " - " + worker_name_2

            if st.button("Aksiyonu Kaydet"):
                if not worker_name:
                    st.error("Lütfen çalışan adını girin.")
                else:
                    action_code = ""
                    if action == "Kullan":
                        action_code = "Kullanıldı"
                    elif action == "İşlem İçin Gönder":
                        action_code = "İşlem İçin Gönderildi"
                    elif action == "İşlemden Gelen Malı Geri Al":
                        action_code = "Geri Alındı"
                    else:
                        st.error("Lütfen geçerli bir aksiyon seçin.")

                    if action_code:
                        if action_code == "İşlem İçin Gönderildi" and not partner_firm:
                            st.error("Lütfen firma adını girin.")
                        elif action_code == "Geri Alındı" and not partner_firm:
                            st.error("Lütfen gönderici firma adını girin.")
                        else:
                            utils_11.log_asset_movement(
                                asset['id'], action_code, quantity,  # Use fetched quantity
                                partner_firm, worker_name, notes
                            )
                            st.success("Aksiyon başarıyla kaydedildi.")
                            st.rerun()
    except Exception as e:
        st.error(f"Varlık detayları görüntülenirken bir hata oluştu: {e}")



# ---------------------- QR Code Scanning Section ----------------------

st.subheader("QR Kodunu Tara")
image = st.camera_input("QR kodunun fotoğrafını çekin veya yükleyin")

if image:
    try:
        # Decode the QR code
        qr_image = Image.open(image)
        decoded_info = decode(qr_image)

        if decoded_info:
            qr_code_data = decoded_info[0].data.decode('utf-8')
            st.write(f"**Tarandı:** {qr_code_data}")

            # Fetch asset information from the database using the full QR code data
            asset = utils_11.get_asset_by_qr(qr_code_data)

            if asset:
                # Display asset details and actions
                display_asset_details(asset)
            else:
                st.error("Varlık veritabanında bulunamadı.")
        else:
            st.error("QR kodu algılanamadı. Lütfen tekrar deneyin.")
    except Exception as e:
        st.error(f"Resim işlenirken bir hata oluştu: {e}")

# ---------------------- Search for Assets ----------------------

st.subheader("Varlık Ara")
search_option = st.selectbox("Arama Kriteri", ["ID", "Varlık Adı"])
search_query = st.text_input("Arama Değerini Girin")

if st.button("Varlık Ara"):
    try:
        if search_query:
            if search_option == "ID":
                asset = utils_11.get_asset_by_id(search_query)
            elif search_option == "Varlık Adı":
                asset = utils_11.get_asset_by_name(search_query)
            else:
                asset = None

            if asset:
                display_asset_details(asset)
            else:
                st.error("Varlık bulunamadı.")
        else:
            st.error("Lütfen arama değerini girin.")
    except Exception as e:
        st.error(f"Arama sırasında bir hata oluştu: {e}")

# ---------------------- View Asset Movement History ----------------------

st.subheader("Varlık Geçmişini Görüntüle")
asset_id_for_history = st.text_input("Varlık ID'sini Girin", key="history_asset_id")

if st.button("Geçmişi Göster"):
    try:
        if asset_id_for_history:
            history_data = utils_11.get_asset_history_by_id(asset_id_for_history)
            if not history_data.empty:
                st.dataframe(history_data)
            else:
                st.write("Bu varlık için hareket bulunamadı.")
        else:
            st.error("Lütfen Varlık ID'sini girin.")
    except Exception as e:
        st.error(f"Geçmiş görüntülenirken bir hata oluştu: {e}")

# ---------------------- Display Recent Asset Movements ----------------------

st.subheader("Son Varlık Hareketleri")
movements_data = utils_11.get_asset_movements()

if not movements_data.empty:
    # Display recent asset movements (e.g., last 10)
    recent_movements = movements_data.sort_values(by='Zaman', ascending=False).head(10)
    st.dataframe(recent_movements)
else:
    st.write("Henüz varlık hareketi yok.")

# ---------------------- Additional Worker Features ----------------------
st.subheader("Ek Çalışan Özellikleri")

# Example: View Personal Task Assignments
st.write("**Kendi Görevlerinizi Görüntüleyin**")
personal_tasks = utils_11.get_personal_tasks(st.session_state.username)

if not personal_tasks.empty:
    st.dataframe(personal_tasks)
else:
    st.write("Şu anda size atanmış görev bulunmamaktadır.")

# Example: Update Task Progress
st.write("**Görev İlerlemesini Güncelleyin**")
task_id_to_update = st.number_input("Güncellenecek Görev ID'sini Girin", min_value=1, step=1, key="update_task_id")
new_progress = st.slider("Yeni İlerleme Oranını Seçin (%)", min_value=0, max_value=100, step=10, key="new_progress")

if st.button("Görev İlerlemesini Güncelle"):
    try:
        if task_id_to_update and (0 <= new_progress <= 100):
            utils_11.update_task_progress(task_id_to_update, new_progress)
            st.success("Görev ilerlemesi başarıyla güncellendi.")
            st.rerun()
        else:
            st.error("Geçerli bir Görev ID'si ve ilerleme oranı girin.")
    except Exception as e:
        st.error(f"Görev ilerlemesi güncellenirken bir hata oluştu: {e}")

# Example: Complete Task
st.write("**Görevi Tamamla**")
task_id_to_complete = st.number_input("Tamamlanacak Görev ID'sini Girin", min_value=1, step=1,
                                      key="complete_task_id")

if st.button("Görevi Tamamla"):
    try:
        if task_id_to_complete:
            utils_11.complete_task(task_id_to_complete)
            st.success("Görev başarıyla tamamlandı.")
            st.rerun()
        else:
            st.error("Lütfen tamamlanacak Görev ID'sini girin.")
    except Exception as e:
        st.error(f"Görev tamamlanırken bir hata oluştu: {e}")

print(utils_11.get_admin_usernames())
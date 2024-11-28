# 1_Admin Paneli.py

import streamlit as st
import utils_11
import pandas as pd
from io import BytesIO
import os
from datetime import datetime

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
# ---------------------- File Paths ----------------------
main_excel_file = "Veriler/depo_veri12.xlsx"
qr_images_file = "Veriler/qr_images12.xlsx"
recent_qr_codes_file = "Veriler/recent_qr_codes12.xlsx"
qr_codes_folder = "Veriler/qr_codes12"
asset_movements_excel = "Veriler/asset_movements.xlsx"
qr_codes_output_excel = "Veriler/qr_codes_output.xlsx"
malzeme_uyari_file = "Veriler/Malzeme Uyarı.xlsx"  # Add this line

# ---------------------- Data Lists ----------------------
products = [
    "50 GR 165 CM ELYAF", "60 GR 65 CM ELYAF", "60 GR 140 CM ELYAF", "60 GR 150 CM ELYAF", "60 GR 160 CM ELYAF",
    "60 GR 210 CM ELYAF", "60 GR 240 CM ELYAF", "80 GR 70 CM ELYAF", "80 GR 75 CM ELYAF", "80 GR 85 CM ELYAF",
    "100 GR 75 CM ELYAF", "100 GR 70 CM ELYAF", "100 GR 210 CM ELYAF", "120 GR 85 CM ELYAF",
    "120 GR 160 CM ELYAF",
    "210 GÜLLÜ JAGAR", "210 YILANLI JAGAR", "210 DİAGONAL JAGAR", "210 NOKTALI JAGAR", "210 BAKLAVA JAGAR",
    "210 ÜÇ ÇİZGİLİ JAGAR", "210 EKRU 3 ÇİZGİLİ BEKART", "210 GRİ 3 ÇİZGİLİ BEKART", "210 EKRU DÜZ BEKART",
    "80 GR 240 CM MİKRO", "80 GR 80 CM MİKRO", "80 GR 90 CM MİKRO", "80 GR 75 CM MİKRO", "100 GR 300 CM MİKRO",
    "100 GR 90 CM MİKRO", "100 GR 80 CM MİKRO", "100 GR 75 CM MİKRO", "220 CM ASTAR", "46 CM BASKISIZ KOLİ",
    "30 CM BASKISIZ KOLİ", "35 CM BASKISIZ KOLİ", "42 CM BASKILI KOLİ", "50 CM BASKILI KOLİ", "GÖMLEK KOLİSİ",
    "ÇARŞAF KOLİSİ", "DANTEL SARIM KOLİSİ", "220 CM ASTAR", "250 CM BEYAZ İP", "160 CM ASTAR",
    "240 CM BEYAZ İP",
    "80 CM BEYAZ İP", "160 CM BEYAZ İP", "90 CM BEYAZ İP", "5,5 CM ASTAR", "75 CM ASTAR",
    "160 CM POLY PUANTİYE",
    "80 CM POLY PUANTİYE", "4,5 CM POLY PUANTİYE", "60 GR 70 CM TELA", "60 GR 80 CM TELA", "60 GR 160 CM TELA",
    "80 GR 160 CM TELA", "80 GR 80 CM TELA", "40 GR 160 CM TELA", "40 GR 120 CM TELA", "40 GR 90 CM TELA",
    "40 GR 67 CM TELA", "40 GR 80 CM TELA", "60 GR 65 CM TELA", "15 GR 75 CM TELA", "15 GR 80 CM TELA",
    "15 GR 210 CM TELA", "75 CM ASTAR", "75 CM ASTAR", "80 CM ASTAR", "90 CM ASTAR", "165 CM ASTAR",
    "210 CM ASTAR", "60 CM ASTAR", "65 CM ASTAR", "330 CM ASTAR", "280 CM ASTAR", "300 CM ASTAR",
    "280 CM ŞEKER KASAR", "90 CM ŞEKER KASAR", "80 CM ŞEKER KASAR", "5,5 CM ŞEKER KASAR"
]

suppliers = [
    "Metin Yüksel (Bursa)", "İsfa Faruk (Bursa)", "Pir Nakış (İzmir)", "Kesimci Gökhan (Bursa)",
    "Febay (İzmir)",
    "Serkan Lale", "Urba", "Jagar Naim", "Nevasan", "Malzem (Kisbu)", "Arzu Toprak (Tela- Bursa)", "Koli Halil",
    "Aykaya Poşetçi", "Doğa Elyaf", "Özsümer (Yedek Parça)", "Fütüre (Dantel)", "Afra Mehmet (Kurdela)",
    "Esra Dardokuma (Kordon)", "Karesi", "Şık Düğme (Düğme/Lastik/)", "Tarakçıoğlu (Gömlek İç Kağıt)",
    "Bekart (Tekirdağ)", "Depo"
]

# ---------------------- Streamlit Page Configuration ----------------------
# Set up the title for the admin page
st.title("Admin Panel - QR Kod ve Varlık Yönetimi")

# ---------------------- QR Code Creation Section ----------------------
st.subheader("QR Kod Oluşturma")

# Initialize QR code creation state
if 'qr_creation_started' not in st.session_state:
    st.session_state.qr_creation_started = False

# Button to start QR code creation
if not st.session_state.qr_creation_started:
    if st.button("QR kod yaratmaya başla"):
        # Reset recent QR codes Excel file
        utils_11.create_excel_file_if_missing(utils_11.recent_qr_codes_file, ["id", "QR-codes-text", "image_path"])
        st.session_state.qr_creation_started = True
        st.success("QR kod yaratma işlemi başlatıldı ve recent_qr_codes12.xlsx dosyası sıfırlandı.")
else:
    # QR code creation form
    st.write("QR kod yaratma işlemi başlatıldı.")
    with st.form("qr_code_creation_form"):
        assetname = st.selectbox("Varlık Seç", products)
        unit = st.selectbox("Ölçü unitini Seç", ["metre", "kg", "rulo"])
        miktar = st.number_input("Miktarı Girin", value=1, step=1)
        adet = st.number_input("Çarpan (adet)", value=1, step=1)
        gönderen = st.selectbox("Gönderen", suppliers)
        alıcı = st.selectbox("Alıcı", suppliers)
        submit = st.form_submit_button("QR Kod Oluştur")

    if submit:
        if not gönderen or not alıcı:
            st.error("Lütfen hem gönderen hem de alıcıyı belirtin.")
        else:
            qr_codes_info = utils_11.generate_qr_codes(assetname, unit, miktar, adet, gönderen, alıcı)
            if qr_codes_info:
                st.success(f"{adet} QR kod başarıyla oluşturuldu!")

                # Display generated QR codes and IDs
                st.subheader("Oluşturulan QR Kodları ve ID'leri")
                for qr_info in qr_codes_info:
                    st.image(qr_info['image_path'], width=100)
                    st.write(f"ID: {qr_info['id']}")

                # Provide option to download QR codes Excel file
                excel_qr_codes_file = "Veriler/qr_codes_output.xlsx"
                if os.path.exists(excel_qr_codes_file):
                    with open(excel_qr_codes_file, "rb") as f:
                        excel_data = f.read()
                        st.download_button(
                            label="QR Kodları Excel Olarak İndir",
                            data=excel_data,
                            file_name='qr_codes_output.xlsx',
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                else:
                    st.error("QR kodları Excel dosyası bulunamadı.")

    # Button to end QR code creation
    if st.button("QR kod yaratmayı bitir"):
        st.session_state.qr_creation_started = False
        st.success("QR kod yaratma işlemi tamamlandı ve recent_qr_codes12.xlsx dosyasına kaydedildi.")
        # Send notification to admins
        utils_11.send_pushbullet_notification(
            title="Admin Aksiyonu: QR Kod Yaratma Tamamlandı",
            message=f"QR kod yaratma işlemi {st.session_state.username} tarafından tamamlandı."
        )
# ---------------------- User Authentication Check ----------------------
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("Bu sayfayı görüntülemek için lütfen giriş yapın.")
    st.stop()
else:
    if st.session_state.role != 'admin':
        st.error("Bu sayfayı görüntülemek için yetkiniz yok.")
        st.stop()


history = utils_11.get_asset_history()


# ---------------------- Asset Addition Section ----------------------
st.subheader("Varlık Ekle")
if st.button("Varlık Ekle"):
    utils_11.add_assets_from_recent_qr_codes()
    st.success("Varlıklar başarıyla eklendi ve veritabanına kaydedildi.")
    # Send notification to admins
    utils_11.send_pushbullet_notification(
        title="Admin Aksiyonu: Varlık Eklendi",
        message=f"Varlıklar {st.session_state.username} tarafından eklendi."
    )

# ---------------------- Display Assets in Storage ----------------------
st.subheader("Depodaki Mevcut Varlıklar")
assets_df = utils_11.get_current_stock_levels()  # Get the current stock levels

if not assets_df.empty:
    # Display assets in a table
    st.dataframe(assets_df)
else:
    st.write("Depoda şu anda hiç varlık yok.")

# ---------------------- Asset Filtering Section ----------------------
st.subheader("Varlıkları Filtrele")
filter_option = st.selectbox("Filtreleme Kriteri", ["varlık_adı", "gönderen", "alıcı"])

if filter_option == "varlık_adı":
    filter_query = st.selectbox("Filtre Değerini Girin", products)
elif filter_option == "gönderen":
    filter_query = st.selectbox("Filtre Değerini Girin", suppliers)
elif filter_option == "alıcı":
    filter_query = st.selectbox("Filtre Değerini Girin", suppliers)
else:
    filter_query = st.text_input("Filtre Değerini Girin")

if st.button("Varlıkları Filtrele"):
    filtered_assets_df = utils_11.get_filtered_assets(filter_option, filter_query)
    if not filtered_assets_df.empty:
        st.dataframe(filtered_assets_df)

        # Add an export button for filtered assets
        excel_filtered_assets = "Veriler/filtered_assets.xlsx"
        try:
            filtered_assets_excel = utils_11.convert_df_to_excel(filtered_assets_df)
            if filtered_assets_excel:
                st.download_button(
                    label="Varlıkları Excel Olarak İndir",
                    data=filtered_assets_excel,
                    file_name='filtered_assets.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            else:
                st.error("Varlıkları Excel formatına dönüştürmede hata oluştu.")
        except Exception as e:
            st.error(f"Varlıkları Excel olarak indirme hatası: {e}")
    else:
        st.write("Kriterlere uyan varlık bulunamadı.")

# ---------------------- Asset Movements Section ----------------------
st.subheader("Varlık Hareketleri")

movements_data = utils_11.get_asset_movements()

if not movements_data.empty:
    st.dataframe(movements_data)

    # Add a selectbox to choose a movement to undo
    movement_id_to_undo = st.number_input("Geri Alınacak Hareket ID'sini Girin", min_value=1, step=1)
    if st.button("Hareketi Geri Al"):
        success = utils_11.undo_asset_movement(movement_id_to_undo)
        if success:
            st.success("Hareket başarıyla geri alındı.")
            st.rerun()
        else:
            st.error("Hareket geri alınamadı.")
else:
    st.write("Henüz varlık hareketi yok.")

# ---------------------- Movement Filtering Section ----------------------
st.subheader("Varlık Hareketlerini Filtrele")
action_type = st.selectbox("Aksiyon Türü", ["Hepsi", "Kullanıldı", "İşlem İçin Gönderildi", "Geri Alındı"])
start_date = st.date_input("Başlangıç Tarihi", value=datetime.now())
end_date = st.date_input("Bitiş Tarihi", value=datetime.now())

if st.button("Hareketleri Filtrele"):
    filtered_movements_data = utils_11.get_filtered_movements(action_type, start_date, end_date)
    if not filtered_movements_data.empty:
        st.dataframe(filtered_movements_data)

        # Add an export button for filtered movements
        excel_filtered_movements = "Veriler/filtered_movements.xlsx"
        try:
            filtered_movements_excel = utils_11.convert_df_to_excel(filtered_movements_data)
            if filtered_movements_excel:
                st.download_button(
                    label="Hareketleri Excel Olarak İndir",
                    data=filtered_movements_excel,
                    file_name='filtered_movements.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            else:
                st.error("Hareketleri Excel formatına dönüştürmede hata oluştu.")
        except Exception as e:
            st.error(f"Hareketleri Excel olarak indirme hatası: {e}")
    else:
        st.write("Kriterlere uyan hareket bulunamadı.")

# ---------------------- Additional Admin Features ----------------------
st.subheader("Ek Yönetici Özellikleri")

# Button to reset all data (use with caution)
if st.button("Tüm Verileri Sıfırla"):
    confirm_reset = st.checkbox("Emin misiniz? Tüm veriler silinecek!")
    if confirm_reset:
        utils_11.reset_all_data()

# Button to clear recent QR codes
if st.button("Recent QR Kodları Temizle"):
    confirm_clear = st.checkbox("Emin misiniz? Recent QR kodlar temizlenecek!")
    if confirm_clear:
        utils_11.clear_recent_qr_codes()

# ---------------------- Stock Summary Section ----------------------
st.subheader("Stok Özeti")

# Dropdown menus
display_option = st.selectbox("Görüntülenecek Bilgi", ["Depodaki Toplam Mal Miktarı", "Hepsi"])
filter_option = st.selectbox("Filtreleme Kriteri", ["Hepsi", "Malın Adı"])

# Input for filter value
if filter_option != "Hepsi":
    filter_value = st.selectbox("Malın Adı", products)
else:
    filter_value = None

# Get the stock summary DataFrame
stock_summary_df = utils_11.calculate_stock_summary()

if stock_summary_df.empty:
    st.write("Stok özeti mevcut değil.")
else:
    # Apply filters if any
    if filter_option == "Malın Adı" and filter_value:
        stock_summary_df = stock_summary_df[stock_summary_df['varlık_adı'].str.contains(filter_value, case=False)]

    # Select columns to display
    if display_option == "Depodaki Toplam Mal Miktarı":
        display_df = stock_summary_df[['varlık_adı', 'unit', 'Current Stock']]
    else:
        display_df = stock_summary_df[['varlık_adı', 'unit', 'Current Stock']]

    # Include 'minimum_stock' for highlighting
    display_df = display_df.merge(stock_summary_df[['varlık_adı', 'minimum_stock']], on='varlık_adı', how='left')

    # Highlight function
    def highlight_stock_levels(row):
        min_stock = row.get('minimum_stock', None)
        current_stock = row.get('Current Stock', None)
        if pd.notnull(min_stock) and current_stock is not None:
            if current_stock <= min_stock:
                return ['background-color: red'] * len(row)
            elif current_stock <= min_stock * 1.25:
                return ['background-color: yellow'] * len(row)
        return [''] * len(row)

    # Apply highlighting
    styled_df = display_df.style.apply(highlight_stock_levels, axis=1)

    st.dataframe(styled_df)

    # Notifications
    if 'notifications_sent' not in st.session_state:
        st.session_state.notifications_sent = {}

    for idx, row in stock_summary_df.iterrows():
        min_stock = row['minimum_stock']
        current_stock = row['Current Stock']
        asset_name = row['varlık_adı']
        if pd.notnull(min_stock) and current_stock <= min_stock:
            if asset_name not in st.session_state.notifications_sent:
                # Send notification
                title = f"Stok Uyarısı: {asset_name}"
                message = f"{asset_name} stoğu minimum seviyenin altında! (Mevcut: {current_stock}, Minimum: {min_stock})"
                utils_11.send_pushbullet_notification(title, message)
                st.session_state.notifications_sent[asset_name] = True
        elif pd.notnull(min_stock) and current_stock <= min_stock * 1.25:
            if asset_name not in st.session_state.notifications_sent:
                # Optionally send a notification for low stock but above minimum
                pass
        else:
            # Reset notification status
            if asset_name in st.session_state.notifications_sent:
                del st.session_state.notifications_sent[asset_name]

    # Download button
    st.download_button(
        label="Stok Özetini Excel Olarak İndir",
        data=utils_11.convert_df_to_excel(display_df),
        file_name='stock_summary.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    # Optional: Provide an export of the entire stock summary
    if st.button("Tüm Stok Özetini İndir"):
        try:
            excel_stock_summary = utils_11.convert_df_to_excel(stock_summary_df)
            if excel_stock_summary:
                st.download_button(
                    label="Tüm Stok Özetini Excel Olarak İndir",
                    data=excel_stock_summary,
                    file_name='all_stock_summary.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            else:
                st.error("Stok özetini Excel formatına dönüştürmede hata oluştu.")
        except Exception as e:
            st.error(f"Stok özetini Excel olarak indirme hatası: {e}")

# ---------------------- End of 1_Admin Paneli.py ----------------------

# 1_Admin Paneli.py

st.subheader("Varlık Yönetimi")

# Fetch current assets (including 'id')
assets_df = utils_11.get_all_assets()  # You need to define this function

if not assets_df.empty:
    # Display assets with delete buttons
    for index, asset in assets_df.iterrows():
        cols = st.columns([4, 1])  # Adjust column widths as needed
        with cols[0]:
            st.write(
                f"**ID:** {asset['id']} | **Adı:** {asset['varlık_adı']} | **Miktar:** {asset['Current Stock']} {asset['unit']}")
        with cols[1]:
            delete_button = st.button("❌", key=f"delete_{asset['id']}")
            if delete_button:
                confirm = st.warning("Bu varlığı silmek istediğinize emin misiniz? Bu işlem geri alınamaz.", icon="⚠️")
                confirm_yes = st.button("Evet, Sil", key=f"confirm_delete_{asset['id']}")
                confirm_no = st.button("Hayır", key=f"cancel_delete_{asset['id']}")

                if confirm_yes:
                    success, message = utils_11.remove_asset(asset['id'])
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                elif confirm_no:
                    st.info("Silme işlemi iptal edildi.")
else:
    st.write("Depoda şu anda hiç varlık yok.")



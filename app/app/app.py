import sys
import os

# Qovluq yollarını dinamik olaraq əlavə edirik (ImportError xətasını qəti həll edir)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)

sys.path.append(current_dir)
sys.path.append(parent_dir)
sys.path.append(grandparent_dir)
sys.path.append(os.path.join(current_dir, 'app'))

import streamlit as st
import pandas as pd
from datetime import datetime

# Modulları təhlükəsiz şəkildə çağırırıq
try:
    from database import DatabaseManager
except ImportError:
    try:
        from app.database import DatabaseManager
    except ImportError:
        from .database import DatabaseManager

db = DatabaseManager()

st.set_page_config(page_title="Universitet Tədbirləri Sistemi", page_icon="🎓", layout="wide")
st.title("🎓 Universitet Tədbirlərinin İdarə Edilməsi və Qeydiyyat Sistemi")
st.markdown("---")

menu = [
    "📅 Tədbirlər Siyahısı & Axtarış", 
    "➕ Yeni Tədbir Yarat", 
    "📝 Tədbirə Qeydiyyat", 
    "📊 İdarəetmə Paneli & Statistika",
    "📥 Əlavə: Fayla İxrac (CSV)"
]
choice = st.sidebar.selectbox("Naviqasiya", menu)

# --- 1. TƏDBİRLƏR SİYAHISI VƏ AXTARIŞ ---
if choice == "📅 Tədbirlər Siyahısı & Axtarış":
    st.header("📅 Mövcud Tədbirlər və Axtarış")
    conn = db.get_connection()
    categories_df = pd.read_sql("SELECT * FROM categories", conn)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        search_query = st.text_input("🔍 Tədbir adına görə axtarış:")
    with col2:
        cat_options = ["Bütün kateqoriyalar"] + list(categories_df["name"])
        selected_cat = st.selectbox("📂 Kateqoriya seçin:", cat_options)
    with col3:
        filter_status = st.selectbox("⏳ Zaman filtri:", ["Hamısı", "Gələcək tədbirlər", "Keçmiş tədbirlər"])

    query = """
        SELECT e.id, e.title, e.description, c.name as category, e.date, e.time, e.location, e.max_participants,
        (SELECT COUNT(*) FROM registrations r WHERE r.event_id = e.id) as current_registrations
        FROM events e 
        JOIN categories c ON e.category_id = c.id
    """
    df_events = pd.read_sql(query, conn)
    conn.close()

    if not df_events.empty:
        if search_query:
            df_events = df_events[df_events["title"].str.contains(search_query, case=False, na=False)]
        if selected_cat != "Bütün kateqoriyalar":
            df_events = df_events[df_events["category"] == selected_cat]
            
        now = datetime.now()
        def check_status(row):
            try:
                ev_date = datetime.strptime(f"{row['date']} {row['time']}", "%Y-%m-%d %H:%M")
                return "Gələcək" if ev_date > now else "Keçmiş"
            except:
                return "Gələcək"
                
        df_events["Status"] = df_events.apply(check_status, axis=1)
        
        if filter_status == "Gələcək tədbirlər":
            df_events = df_events[df_events["Status"] == "Gələcək"]
        elif filter_status == "Keçmiş tədbirlər":
            df_events = df_events[df_events["Status"] == "Keçmiş"]

        if df_events.empty:
            st.warning("⚠️ Axtarış şərtlərinə uyğun tədbir tapılmadı.")
        else:
            st.dataframe(df_events, use_container_width=True)
    else:
        st.info("Hələ ki sistemdə tədbir yoxdur.")

# --- 2. YENİ TƏDBİR YARAT ---
elif choice == "➕ Yeni Tədbir Yarat":
    st.header("➕ Yeni Tədbir Əlavə Et")
    conn = db.get_connection()
    categories_df = pd.read_sql("SELECT * FROM categories", conn)
    conn.close()
    
    with st.form("event_form"):
        title = st.text_input("Tədbirin Adı *")
        description = st.text_area("Təsviri")
        category_name = st.selectbox("Kateqoriya *", categories_df["name"].tolist())
        date = st.date_input("Keçirilmə Tarixi *")
        time = st.time_input("Keçirilmə Saatı *")
        location = st.text_input("Keçirilmə Yeri *")
        max_participants = st.number_input("Maksimum İştirakçı Sayı *", min_value=1, value=50)
        
        submit = st.form_submit_button("Tədbiri Yarat")
        if submit:
            if not title or not location:
                st.error("❌ Məcburi sahələri doldurun!")
            else:
                cat_id = categories_df[categories_df["name"] == category_name]["id"].values[0]
                conn = db.get_connection()
                cursor = conn.cursor()
                try:
                    cursor.execute("""
                        INSERT INTO events (title, description, category_id, date, time, location, max_participants)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (title, description, int(cat_id), str(date), str(time), location, int(max_participants)))
                    conn.commit()
                    st.success(f"✅ '{title}' adlı tədbir yaradıldı!")
                except Exception as e:
                    st.error(f"❌ Xəta: {e}")
                finally:
                    conn.close()

# --- 3. İŞTİRAKÇI QEYDİYYATI ---
elif choice == "📝 Tədbirə Qeydiyyat":
    st.header("📝 Tədbirə Qeydiyyatdan Keçmə")
    conn = db.get_connection()
    events_df = pd.read_sql("SELECT id, title, max_participants FROM events", conn)
    conn.close()
    
    if events_df.empty:
        st.warning("⚠️ Qeydiyyat üçün əvvəlcə tədbir yaradılmalıdır.")
    else:
        with st.form("registration_form"):
            full_name = st.text_input("Ad Soyad *")
            email = st.text_input("E-poçt ünvanı *")
            selected_event_title = st.selectbox("Tədbir Seçin *", events_df["title"].tolist())
            
            reg_submit = st.form_submit_button("Qeydiyyatı Tamamla")
            if reg_submit:
                if not full_name or not email:
                    st.error("❌ Ad və e-poçt boş ola bilməz!")
                else:
                    event_id = events_df[events_df["title"] == selected_event_title]["id"].values[0]
                    max_limit = events_df[events_df["title"] == selected_event_title]["max_participants"].values[0]
                    
                    conn = db.get_connection()
                    cursor = conn.cursor()
                    
                    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
                    user_row = cursor.fetchone()
                    if user_row:
                        user_id = user_row[0]
                    else:
                        cursor.execute("INSERT INTO users (full_name, email) VALUES (?, ?)", (full_name, email))
                        conn.commit()
                        user_id = cursor.lastrowid
                        
                    cursor.execute("SELECT COUNT(*) FROM registrations WHERE event_id = ?", (event_id,))
                    current_count = cursor.fetchone()[0]
                    
                    if current_count >= max_limit:
                        st.error("❌ Tədbirin limiti dolmuşdur!")
                    else:
                        try:
                            cursor.execute("""
                                INSERT INTO registrations (user_id, event_id, registration_date)
                                VALUES (?, ?, ?)
                            """, (user_id, event_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                            conn.commit()
                            st.success(f"🎉 Qeydiyyat uğurla tamamlandı!")
                        except sqlite3.IntegrityError:
                            st.warning("⚠️ Siz artıq bu tədbirə qeydiyyatdan keçmisiniz.")
                        finally:
                            conn.close()

# --- 4. İDARƏETMƏ PANELİ VƏ STATİSTİKA ---
elif choice == "📊 İdarəetmə Paneli & Statistika":
    st.header("📊 Sistem Statistikası")
    conn = db.get_connection()
    total_events = pd.read_sql("SELECT COUNT(*) as count FROM events", conn)["count"].iloc[0]
    total_regs = pd.read_sql("SELECT COUNT(*) as count FROM registrations", conn)["count"].iloc[0]
    total_users = pd.read_sql("SELECT COUNT(*) as count FROM users", conn)["count"].iloc[0]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Ümumi Tədbir", total_events)
    col2.metric("Ümumi Qeydiyyat", total_regs)
    col3.metric("İstifadəçilər", total_users)
    
    st.markdown("---")
    top_events_query = """
        SELECT e.title, c.name as category, COUNT(r.id) as qeydiyyat_sayi, e.max_participants
        FROM events e
        LEFT JOIN registrations r ON e.id = r.event_id
        JOIN categories c ON e.category_id = c.id
        GROUP BY e.id
        ORDER BY qeydiyyat_sayi DESC
    """
    df_top = pd.read_sql(top_events_query, conn)
    conn.close()
    if not df_top.empty:
        st.dataframe(df_top, use_container_width=True)

# --- 5. FƏRDİ ƏLAVƏ TAPŞIRIQ: FAYLA İXRAC ---
elif choice == "📥 Əlavə: Fayla İxrac (CSV)":
    st.header("📥 İştirakçı Siyahısını İxrac Et")
    conn = db.get_connection()
    events_df = pd.read_sql("SELECT id, title FROM events", conn)
    
    if events_df.empty:
        st.warning("İxrac olunacaq tədbir yoxdur.")
        conn.close()
    else:
        selected_event = st.selectbox("Tədbir seçin:", events_df["title"].tolist())
        event_id = events_df[events_df["title"] == selected_event]["id"].values[0]
        
        export_query = """
            SELECT u.full_name, u.email, r.registration_date 
            FROM registrations r
            JOIN users u ON r.user_id = u.id
            WHERE r.event_id = ?
        """
        df_participants = pd.read_sql(export_query, conn, params=(int(event_id),))
        conn.close()
        
        st.dataframe(df_participants, use_container_width=True)
        if not df_participants.empty:
            csv_data = df_participants.to_csv(index=False).encode('utf-8')
            st.download_button("📥 CSV Faylı Yüklə", data=csv_data, file_name=f"event_{event_id}_users.csv", mime="text/csv")

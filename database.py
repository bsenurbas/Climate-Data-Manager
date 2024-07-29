import sqlite3 as sql
import pandas as pd

class Database:
    # Veritabanı bağlantısını yönetir
    def __init__(self, db_path):
        self.conn = sql.connect(db_path)
    
    def execute(self, query, params=()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor
    
    def fetchone(self, query, params=()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()
    
    def fetchall(self, query, params=()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def close(self):
        self.conn.close()

class User:
    # Kullanıcı işlemleri yönetimi
    def __init__(self, db):
        self.db = db
    
    def create_table(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS USERS(
                id INTEGER PRIMARY KEY,
                name TEXT,
                lastname TEXT,
                username TEXT,
                password TEXT
            )
        """)
    
    def insert(self, name, lastname, username, password):
        self.db.execute("""INSERT INTO USERS (name, lastname, username, password) 
                           VALUES (?, ?, ?, ?)""", (name, lastname, username, password))
    
    def search(self, username):
        return self.db.fetchone("""SELECT * FROM USERS WHERE username = ?""", (username,))

import pandas as pd

class IklimData:
    # İklim verisi işlemleri yönetimi
    def __init__(self, db):
        self.db = db
    
    def create_table(self, excel_file_path):
        # Excel dosyasını oku ve temizle
        df = self.read_and_clean_excel(excel_file_path)
        
        # Tabloyu oluştur
        self.create_table_in_db(df)
    
    def read_and_clean_excel(self, excel_file_path):
        # Excel dosyasından verileri okuyarak başlıkları temizler
        df = pd.read_excel(excel_file_path)
        df.columns = [self.clean_header(col) for col in df.columns]
        df['tarih'] = pd.to_datetime(df['tarih'], errors='coerce').dt.date
        df['saat'] = pd.to_datetime(df['saat'], errors='coerce').dt.time
        return df
    
    def clean_header(self, header):
        # Başlıkları temizleyerek snake_case formatına dönüştürür
        header = header.lower().replace(" ", "_")
        header = header.replace("(", "").replace(")", "")
        header = header.replace("©", "").replace("kpa", "").replace("%", "")
        header = header.replace("/", "").replace("2", "").replace(":", "")
        header = header.replace("m/s", "").replace("degrees", "")
        return header
    
    def create_table_in_db(self, df):
        # Veriyi veritabanına yazar
        df.to_sql('iklim_data', self.db.conn, if_exists='replace', index=False)
    
    def insert_data(self, day, month, year, tarih, saat, dry_bulb_temperature, wet_bulb_temperature, 
                    atmospheric_pressure, relative_humidity, dew_point_temperature, 
                    global_solar, normal_solar, diffuse_solar, wind_speed, wind_direction):
        # İklim verilerini tabloya ekler
        self.db.execute("""
            INSERT INTO iklim_data (
                day, month, year, tarih, saat,
                dry_bulb_temperature, wet_bulb_temperature,
                atmospheric_pressure, relative_humidity,
                dew_point_temperature, global_solar, normal_solar,
                diffuse_solar, wind_speed, wind_direction
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (day, month, year, tarih, saat, dry_bulb_temperature, wet_bulb_temperature, 
              atmospheric_pressure, relative_humidity, dew_point_temperature, 
              global_solar, normal_solar, diffuse_solar, wind_speed, wind_direction))
    
    def delete_by_date(self, target_date,target_time):
        # Belirtilen tarihteki veriyi siler
        self.db.execute("DELETE FROM iklim_data WHERE tarih = ? AND saat = ?", (target_date,target_time))
    
    def search_data(self, target_date, target_time):
        # Belirtilen tarih ve saatteki veriyi arar
        return self.db.fetchone("SELECT * FROM iklim_data WHERE tarih = ? AND saat = ?", 
                                (target_date, target_time))
    
    def list_updatable_fields(self):
        # Güncellenebilir alanların listesini döndürür
        return [
            'day',
            'month',
            'year',
            'tarih',
            'saat',
            'dry_bulb_temperature',
            'wet_bulb_temperature',
            'atmospheric_pressure',
            'relative_humidity',
            'dew_point_temperature',
            'global_solar',
            'normal_solar',
            'diffuse_solar',
            'wind_speed',
            'wind_direction'
        ]
    
    def update_field(self, target_date, target_time, field, new_value):    # Güncellenebilecek alanları numaralarla listeler
        updatable_fields = self.list_updatable_fields()
        
        print("Güncellenebilir alanlar:")
        for idx, field in enumerate(updatable_fields, 1):
            print(f"{idx}. {field}")
        
        # Kullanıcıdan güncellenecek alanı seçmesini ister
        field_choice = int(input("Güncellenecek alanın numarasını girin: ")) - 1
        
        if 0 <= field_choice < len(updatable_fields):
            field = updatable_fields[field_choice]
            new_value = input(f"Yeni değer ({field}): ")
            
            # Verinin türüne göre uygun dönüşüm yapılır
            if field in ['dry_bulb_temperature', 'wet_bulb_temperature', 'atmospheric_pressure',
                        'relative_humidity', 'dew_point_temperature', 'global_solar',
                        'normal_solar', 'diffuse_solar', 'wind_speed', 'wind_direction']:
                new_value = float(new_value)
            elif field in ['day', 'month', 'year']:
                new_value = int(new_value)
            
            self.db.execute(f"UPDATE iklim_data SET {field} = ? WHERE tarih = ? AND saat = ?", 
                            (new_value, target_date, target_time))
            print(f"{field} başarıyla güncellendi!")
        else:
            print("Geçersiz seçim!")

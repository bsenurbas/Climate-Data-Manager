import locale

try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    # If 'en_US.UTF-8' is not available, fall back to the default 'C' locale
    locale.setlocale(locale.LC_ALL, 'C')

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from database import Database, User, IklimData
from datetime import datetime

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("İklim Verisi Uygulaması")
        self.root.geometry("800x600")

        # Tema ve stil ayarları
        self.style = ttk.Style(theme='darkly')
        self.style.configure('TButton', font=('Helvetica', 12))
        self.style.configure('TLabel', font=('Helvetica', 12))
        self.style.configure('TEntry', font=('Helvetica', 12))
        
        self.db = Database(r"C:\Users\Windows 10\OneDrive\Masaüstü\Staj\SQL\excel_proje\database.db")
        self.user_manager = User(self.db)
        self.iklim_manager = IklimData(self.db)

        self.entries = {}
        self.show_main_menu()
    
    def show_main_menu(self):
        self.clear_frame()
        
        title_label = ttk.Label(self.root, text="İklim Verisi Uygulaması", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=30)

        self.login_button = ttk.Button(self.root, text="Giriş Yap", bootstyle=PRIMARY, command=self.show_login)
        self.login_button.pack(pady=10, fill='x', padx=50)

        self.register_button = ttk.Button(self.root, text="Kayıt Ol", bootstyle=SUCCESS, command=self.show_register)
        self.register_button.pack(pady=10, fill='x', padx=50)

    def show_login(self):
        self.clear_frame()
        
        ttk.Label(self.root, text="Kullanıcı Adı:").pack(pady=5)
        self.username_entry = ttk.Entry(self.root, width=30)
        self.username_entry.pack(pady=5)

        ttk.Label(self.root, text="Şifre:").pack(pady=5)
        self.password_entry = ttk.Entry(self.root, show='*', width=30)
        self.password_entry.pack(pady=5)

        ttk.Button(self.root, text="Giriş", bootstyle=PRIMARY, command=self.login).pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user = self.user_manager.search(username)
        
        if user and password == user[4]:
            self.show_data_menu()
        else:
            messagebox.showerror("Hata", "Kullanıcı adı veya şifre yanlış!")

    def show_register(self):
        self.clear_frame()
        
        ttk.Label(self.root, text="Ad:").pack(pady=5)
        self.name_entry = ttk.Entry(self.root, width=30)
        self.name_entry.pack(pady=5)

        ttk.Label(self.root, text="Soyad:").pack(pady=5)
        self.lastname_entry = ttk.Entry(self.root, width=30)
        self.lastname_entry.pack(pady=5)

        ttk.Label(self.root, text="Kullanıcı Adı:").pack(pady=5)
        self.reg_username_entry = ttk.Entry(self.root, width=30)
        self.reg_username_entry.pack(pady=5)

        ttk.Label(self.root, text="Şifre:").pack(pady=5)
        self.reg_password_entry = ttk.Entry(self.root, show='*', width=30)
        self.reg_password_entry.pack(pady=5)

        ttk.Button(self.root, text="Kayıt Ol", bootstyle=SUCCESS, command=self.register).pack(pady=10)

    def register(self):
        name = self.name_entry.get()
        lastname = self.lastname_entry.get()
        username = self.reg_username_entry.get()
        password = self.reg_password_entry.get()
        
        if self.user_manager.search(username):
            messagebox.showerror("Hata", "Bu kullanıcı adı zaten kullanılıyor!")
        else:
            self.user_manager.insert(name, lastname, username, password)
            messagebox.showinfo("Başarı", "Kayıt başarılı!")
            self.show_login()  # Kayıttan sonra giriş ekranını göster

    def show_data_menu(self):
        self.clear_frame()
        
        ttk.Button(self.root, text="Veri Ekle", bootstyle=PRIMARY, command=self.add_data).pack(pady=10, fill='x', padx=50)
        ttk.Button(self.root, text="Veri Sil", bootstyle=DANGER, command=self.delete_data).pack(pady=10, fill='x', padx=50)
        ttk.Button(self.root, text="Veri Güncelle", bootstyle=WARNING, command=self.update_data).pack(pady=10, fill='x', padx=50)
        ttk.Button(self.root, text="Veri Ara", bootstyle=INFO, command=self.search_data).pack(pady=10, fill='x', padx=50)

        # Treeview ve Scrollbar oluştur
        self.tree_frame = ttk.Frame(self.root)
        self.tree_frame.pack(pady=10, padx=10, fill='both', expand=True)

        columns = ("day", "month", "year", "tarih", "saat",
                   "dry_bulb_temperature", "wet_bulb_temperature",
                   "atmospheric_pressure", "relative_humidity",
                   "dew_point_temperature", "global_solar", "normal_solar",
                   "diffuse_solar", "wind_speed", "wind_direction")

        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show='headings')
        self.tree.pack(side='left', fill='both', expand=True)

        # Sütun başlıklarını ve genişliklerini ayarla
        for col in columns:
            self.tree.heading(col, text=col.replace('_', ' ').title())
            self.tree.column(col, width=100, anchor='center')

        # Scrollbar ekle ve treeview'e bağla
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Verileri göster
        self.show_iklim_data()

    def show_iklim_data(self):
        # Tablodaki eski verileri temizle
        for row in self.tree.get_children():
            self.tree.delete(row)

        # İklim verilerini çek
        query = "SELECT * FROM iklim_data"
        data = self.iklim_manager.db.fetchall(query)

        # Verileri tabloya ekle
        for row in data:
            self.tree.insert("", "end", values=row)

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def add_data(self):
        self.clear_frame()
        
        # Başlık
        title = ttk.Label(self.root, text="Yeni Veri Ekle", font=("Helvetica", 16, "bold"))
        title.pack(pady=10)
        
        # Veri giriş alanları için çerçeve
        form_frame = ttk.Frame(self.root)
        form_frame.pack(pady=10, padx=10, fill='x')

        labels = [
            "Day", "Month", "Year", "Date (YYYY-MM-DD)", "Time (HH:MM)",
            "Dry Bulb Temperature", "Wet Bulb Temperature",
            "Atmospheric Pressure", "Relative Humidity", "Dew Point Temperature",
            "Global Solar Radiation", "Normal Solar Radiation", 
            "Diffuse Solar Radiation", "Wind Speed", "Wind Direction"
        ]
        
        self.entries = {}  

        # Etiket ve giriş kutuları
        for i, label_text in enumerate(labels):
            label = ttk.Label(form_frame, text=label_text)
            label.grid(row=i, column=0, sticky='e', padx=5, pady=5)
            
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            
            self.entries[label_text] = entry

        # Kaydet butonu
        save_button = ttk.Button(self.root, text="Save", bootstyle=PRIMARY, command=self.insert_data)
        save_button.pack(pady=20)

    def insert_data(self):
        try:
            # Kullanıcıdan alınan veriler
            day = int(self.entries["Day"].get())
            month = int(self.entries["Month"].get())
            year = int(self.entries["Year"].get())
            date = self.entries["Date (YYYY-MM-DD)"].get()
            time = self.entries["Time (HH:MM)"].get()

            dry_bulb_temperature = float(self.entries["Dry Bulb Temperature"].get())
            wet_bulb_temperature = float(self.entries["Wet Bulb Temperature"].get())
            atmospheric_pressure = float(self.entries["Atmospheric Pressure"].get())
            relative_humidity = float(self.entries["Relative Humidity"].get())
            dew_point_temperature = float(self.entries["Dew Point Temperature"].get())
            global_solar = float(self.entries["Global Solar Radiation"].get())
            normal_solar = float(self.entries["Normal Solar Radiation"].get())
            diffuse_solar = float(self.entries["Diffuse Solar Radiation"].get())
            wind_speed = float(self.entries["Wind Speed"].get())
            wind_direction = float(self.entries["Wind Direction"].get())

            # Tarih ve saat doğrulama
            datetime.strptime(date, "%Y-%m-%d")
            datetime.strptime(time, "%H:%M")

            # Saat formatını "HH:MM:SS.ffffff" formatına dönüştür
            time = f"{time}:00.000000"

            # Veritabanına ekle
            self.iklim_manager.insert_data(day, month, year, date, time, dry_bulb_temperature, wet_bulb_temperature, 
                                        atmospheric_pressure, relative_humidity, dew_point_temperature, 
                                        global_solar, normal_solar, diffuse_solar, wind_speed, wind_direction)
            messagebox.showinfo("Success", "Data successfully added!")
            self.show_data_menu()  # Veri menüsüne dön

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid data: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def delete_data(self):
        self.clear_frame()

        # Başlık
        title = ttk.Label(self.root, text="Delete Data", font=("Helvetica", 16, "bold"))
        title.pack(pady=10)

        # Veri giriş alanları için çerçeve
        form_frame = ttk.Frame(self.root)
        form_frame.pack(pady=10, padx=10, fill='x')

        # Tarih etiketi ve giriş kutusu
        ttk.Label(form_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.date_entry = ttk.Entry(form_frame, width=30)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)

        # Saat etiketi ve giriş kutusu
        ttk.Label(form_frame, text="Time (HH:MM):").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.time_entry = ttk.Entry(form_frame, width=30)
        self.time_entry.grid(row=1, column=1, padx=5, pady=5)

        # Silme butonu
        delete_button = ttk.Button(self.root, text="Delete", bootstyle=DANGER, command=self.delete_data_from_db)
        delete_button.pack(pady=20)

    def delete_data_from_db(self):
        try:
            date = self.date_entry.get()
            time = self.time_entry.get()

            # Tarih ve saat doğrulama
            datetime.strptime(date, "%Y-%m-%d")
            datetime.strptime(time, "%H:%M")

            # Saat formatını "HH:MM:SS.ffffff" formatına dönüştür
            time = f"{time}:00.000000"

            # Veritabanından veriyi sil
            self.iklim_manager.delete_by_date(date, time)
            messagebox.showinfo("Success", "Data successfully deleted!")
            self.show_data_menu()  # Veri menüsüne dön

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid data: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def update_data(self):
        self.clear_frame()

        # Başlık
        title = ttk.Label(self.root, text="Update Data", font=("Helvetica", 16, "bold"))
        title.pack(pady=10)

        # Veri giriş alanları için çerçeve
        form_frame = ttk.Frame(self.root)
        form_frame.pack(pady=10, padx=10, fill='x')

        # Tarih etiketi ve giriş kutusu
        ttk.Label(form_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.update_date_entry = ttk.Entry(form_frame, width=30)
        self.update_date_entry.grid(row=0, column=1, padx=5, pady=5)

        # Saat etiketi ve giriş kutusu
        ttk.Label(form_frame, text="Time (HH:MM):").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.update_time_entry = ttk.Entry(form_frame, width=30)
        self.update_time_entry.grid(row=1, column=1, padx=5, pady=5)

        # Güncellenecek alan etiketi ve combobox
        ttk.Label(form_frame, text="Field to Update:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        fields = [
            "day", "month", "year", "tarih", "saat",
            "dry_bulb_temperature", "wet_bulb_temperature",
            "atmospheric_pressure", "relative_humidity", "dew_point_temperature",
            "global_solar", "normal_solar", "diffuse_solar", "wind_speed", "wind_direction"
        ]
        self.field_combobox = ttk.Combobox(form_frame, values=fields, width=28)
        self.field_combobox.grid(row=2, column=1, padx=5, pady=5)

        # Yeni değer etiketi ve giriş kutusu
        ttk.Label(form_frame, text="New Value:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.new_value_entry = ttk.Entry(form_frame, width=30)
        self.new_value_entry.grid(row=3, column=1, padx=5, pady=5)

        # Güncelleme butonu
        update_button = ttk.Button(self.root, text="Update", bootstyle=WARNING, command=self.update_data_in_db)
        update_button.pack(pady=20)

    def update_data_in_db(self):
        try:
            date = self.update_date_entry.get()
            time = self.update_time_entry.get()
            field = self.field_combobox.get()
            new_value = self.new_value_entry.get()

            # Tarih ve saat doğrulama
            datetime.strptime(date, "%Y-%m-%d")
            datetime.strptime(time, "%H:%M")

            # Saat formatını "HH:MM:SS.ffffff" formatına dönüştür
            time = f"{time}:00.000000"

            # Yeni değeri uygun formata çevir
            if field in ["day", "month", "year"]:
                new_value = int(new_value)
            elif field in ["dry_bulb_temperature", "wet_bulb_temperature", "atmospheric_pressure",
                           "relative_humidity", "dew_point_temperature", "global_solar", "normal_solar",
                           "diffuse_solar", "wind_speed", "wind_direction"]:
                new_value = float(new_value)

            # Veritabanında güncelle
            self.iklim_manager.db.execute(f"UPDATE iklim_data SET {field} = ? WHERE tarih = ? AND saat = ?", 
                                          (new_value, date, time))
            messagebox.showinfo("Success", "Data successfully updated!")
            self.show_data_menu()  # Veri menüsüne dön

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid data: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def search_data(self):
        self.clear_frame()
        
        # Başlık
        title = ttk.Label(self.root, text="Search Data", font=("Helvetica", 16, "bold"))
        title.pack(pady=10)

        # Arama çubuğu
        search_frame = ttk.Frame(self.root)
        search_frame.pack(pady=10, padx=10, fill='x')

        ttk.Label(search_frame, text="Enter keyword or date (YYYY-MM-DD):").pack(side='left')
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side='left', padx=10)

        search_button = ttk.Button(search_frame, text="Search", bootstyle=INFO, command=self.perform_search)
        search_button.pack(side='left', padx=10)

        # Sonuçları göstermek için Treeview
        self.tree_frame = ttk.Frame(self.root)
        self.tree_frame.pack(pady=10, padx=10, fill='both', expand=True)

        columns = ("day", "month", "year", "tarih", "saat",
                   "dry_bulb_temperature", "wet_bulb_temperature",
                   "atmospheric_pressure", "relative_humidity",
                   "dew_point_temperature", "global_solar", "normal_solar",
                   "diffuse_solar", "wind_speed", "wind_direction")

        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show='headings')
        self.tree.pack(side='left', fill='both', expand=True)

        # Sütun başlıklarını ve genişliklerini ayarla
        for col in columns:
            self.tree.heading(col, text=col.replace('_', ' ').title())
            self.tree.column(col, width=100, anchor='center')

        # Scrollbar ekle ve treeview'e bağla
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)

    def perform_search(self):
        # Arama çubuğundaki anahtar kelimeyi al
        keyword = self.search_entry.get()

        # Treeview'i temizle
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Veritabanında arama yap ve sonuçları göster
        query = "SELECT * FROM iklim_data WHERE tarih LIKE ? OR saat LIKE ?"
        results = self.iklim_manager.db.fetchall(query, (f"%{keyword}%", f"%{keyword}%"))

        # Sonuçları Treeview'e ekle
        for row in results:
            self.tree.insert("", "end", values=row)

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")  # ttkbootstrap penceresi
    app = App(root)
    root.mainloop()

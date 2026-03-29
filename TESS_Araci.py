import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import lightkurve as lk
import threading
import os
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from astroquery.mast import conf as mast_conf
from astropy.utils.data import conf as astropy_conf

# MAST ve Astropy limitlerini genişletiyoruz
mast_conf.timeout = 3600
astropy_conf.remote_timeout = 3600

global_search_result = None
checkbutton_vars = []

def arama_yap():
    global global_search_result, checkbutton_vars
    hedef = giris_kutusu.get().strip()
    
    log_alani.delete(1.0, tk.END)
    log_alani.insert(tk.END, f"🔭 '{hedef}' için MAST sunucularında arama yapılıyor...\nLütfen bekleyin...\n")
    
    # Önceki checkbox'ları temizle
    for widget in checkbox_frame_inner.winfo_children():
        widget.destroy()
    checkbutton_vars = []
    
    try:
        hedefler = [h.strip() for h in hedef.split(',')] if ',' in hedef else [hedef]
        global_search_result = []
        for h in hedefler:
            res = lk.search_lightcurve(h)
            if len(res) > 0:
                for idx in range(len(res)):
                    global_search_result.append((h, res[idx]))
        
        if len(global_search_result) == 0:
            log_alani.insert(tk.END, "Sonuç bulunamadı.")
        else:
            log_alani.insert(tk.END, f"✅ Toplam {len(global_search_result)} sonuç bulundu!\n")
            
            # Başlık satırı
            baslik = tk.Label(checkbox_frame_inner, 
                              text=f"  {'İndeks':<8} {'Gök Cismi':<12} {'Misyon':<20} {'Yazar':<12} {'Exptime':<10}",
                              font=("Courier New", 9, "bold"), anchor="w", bg="white")
            baslik.pack(fill=tk.X, padx=2)
            
            ttk.Separator(checkbox_frame_inner, orient="horizontal").pack(fill=tk.X, padx=2, pady=2)
            
            # Her sonuç için checkbox oluştur
            for idx, (hedef_adi, satir) in enumerate(global_search_result):
                misyon = str(satir.mission[0])
                yazar = str(satir.author[0])
                exptime = str(satir.exptime[0])
                
                var = tk.IntVar(value=0)
                checkbutton_vars.append(var)
                
                metin = f"[{idx}]  {hedef_adi:<12} {misyon:<20} {yazar:<12} {exptime:<10}"
                cb = tk.Checkbutton(checkbox_frame_inner, text=metin, variable=var,
                                    font=("Courier New", 9), anchor="w", bg="white",
                                    activebackground="#e0f0ff", selectcolor="white")
                cb.pack(fill=tk.X, padx=5, pady=1)
            
            # Canvas scroll bölgesini güncelle
            checkbox_frame_inner.update_idletasks()
            checkbox_canvas.config(scrollregion=checkbox_canvas.bbox("all"))
    except Exception as e:
        log_alani.insert(tk.END, f"Arama sırasında hata oluştu:\n{e}")

def arama_thread():
    threading.Thread(target=arama_yap, daemon=True).start()

def tumunu_sec():
    for var in checkbutton_vars:
        var.set(1)

def tumunu_kaldir():
    for var in checkbutton_vars:
        var.set(0)

def indirme_yap():
    global global_search_result
    if global_search_result is None or len(global_search_result) == 0:
        messagebox.showwarning("Uyarı", "Lütfen önce arama yapın ve sonuç bulun!")
        return
    
    # Seçili indeksleri bul
    secili_indeksler = [i for i, var in enumerate(checkbutton_vars) if var.get() == 1]
    
    if len(secili_indeksler) == 0:
        messagebox.showwarning("Uyarı", "Lütfen indirmek istediğiniz verileri tik işaretiyle seçin!")
        return
    
    format_secimi = format_var.get()
    uzanti = "csv" if format_secimi == "CSV" else "fits"
    log_alani.insert(tk.END, f"\n\n⬇️ Seçilen {len(secili_indeksler)} veri ({format_secimi}) indiriliyor...\n")
    
    for i in secili_indeksler:
        hedef_adi, target = global_search_result[i]
        hedef_temiz = hedef_adi.replace(" ", "_")
        misyon_adi = str(target.mission[0]).replace(" ", "")
        yazar_adi = str(target.author[0])
        dosya_adi = f"{hedef_temiz}_{misyon_adi}_{yazar_adi}_indeks{i}.{uzanti}"
        
        log_alani.insert(tk.END, f"\n⏳ İndiriliyor: {dosya_adi} ...")
        log_alani.see(tk.END)
        
        try:
            lc = target.download()
            if lc is not None:
                lc_temiz = lc.normalize().remove_nans().remove_outliers()
                if format_secimi == "CSV":
                    lc_temiz.to_csv(dosya_adi)
                else:
                    lc_temiz.to_fits(dosya_adi, overwrite=True)
                log_alani.insert(tk.END, f" ✅ Kaydedildi!")
        except Exception as e:
            log_alani.insert(tk.END, f" ❌ Hata: {e}")
    
    log_alani.insert(tk.END, "\n\n🎉 Tüm seçili işlemler tamamlandı!\n")
    log_alani.see(tk.END)

def indirme_thread():
    threading.Thread(target=indirme_yap, daemon=True).start()

def goster_yap():
    global global_search_result
    if global_search_result is None or len(global_search_result) == 0:
        messagebox.showwarning("Uyarı", "Lütfen önce arama yapın ve sonuç bulun!")
        return
    secili_indeksler = [i for i, var in enumerate(checkbutton_vars) if var.get() == 1]
    if len(secili_indeksler) == 0:
        messagebox.showwarning("Uyarı", "Lütfen göstermek istediğiniz verileri seçin!")
        return
        
    log_alani.insert(tk.END, f"\n\n📈 Seçilen {len(secili_indeksler)} veri çiziliyor...\n")
    log_alani.see(tk.END)
    
    def worker():
        for i in secili_indeksler:
            hedef_adi, target = global_search_result[i]
            log_alani.insert(tk.END, f"\n⏳ İndiriliyor: {hedef_adi} ({target.mission[0]})...")
            log_alani.see(tk.END)
            try:
                lc = target.download()
                if lc is not None:
                    lc_temiz = lc.normalize().remove_nans().remove_outliers()
                    time_val = lc_temiz.time.value
                    flux_val = lc_temiz.flux.value
                    
                    def make_plot(t=time_val, f=flux_val, h_adi=hedef_adi, mis=str(target.mission[0])):
                        plot_win = tk.Toplevel(pencere)
                        plot_win.title(f"Işık Eğrisi: {h_adi} - {mis}")
                        plot_win.geometry("850x500")
                        
                        fig = Figure(figsize=(8, 4), dpi=100)
                        ax = fig.add_subplot(111)
                        ax.scatter(t, f, s=1, color='black')
                        ax.set_xlabel("Zaman (BTJD)")
                        ax.set_ylabel("Normalize Akı")
                        ax.set_title(f"{h_adi} - {mis}")
                        fig.tight_layout()
                        
                        canvas = FigureCanvasTkAgg(fig, master=plot_win)
                        canvas.draw()
                        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                        
                        toolbar = NavigationToolbar2Tk(canvas, plot_win)
                        toolbar.update()
                        
                    pencere.after(0, make_plot)
                    log_alani.insert(tk.END, " ✅ Çizildi!")
            except Exception as e:
                log_alani.insert(tk.END, f" ❌ Hata: {e}")
        
        log_alani.insert(tk.END, "\n\n🎉 Gösterim tamamlandı!\n")
        log_alani.see(tk.END)
        
    threading.Thread(target=worker, daemon=True).start()

def goster_thread():
    threading.Thread(target=goster_yap, daemon=True).start()

# =================== ARAYÜZ TASARIMI ===================
pencere = tk.Tk()
pencere.title("TESS Işık Eğrisi İndirme Aracı")
pencere.geometry("780x660")
pencere.configure(bg="#f0f0f0")

icon_path = r"C:\Users\Obi\TESS_Araci\dist\TESS_Araci\gemini.png"
if os.path.exists(icon_path):
    try:
        icon_img = tk.PhotoImage(file=icon_path)
        pencere.iconphoto(False, icon_img)
    except Exception as e:
        print("Ikon yuklenemedi:", e)

# Başlık
tk.Label(pencere, text="TESS Veri Arama ve İndirme Yöneticisi",
         font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=10)

# === Arama Bölümü ===
arama_frame = tk.Frame(pencere, bg="#f0f0f0")
arama_frame.pack(pady=5)
tk.Label(arama_frame, text="Gök Cismi: ", font=("Arial", 11), bg="#f0f0f0").pack(side=tk.LEFT)
giris_kutusu = tk.Entry(arama_frame, font=("Arial", 11), width=25)
giris_kutusu.insert(0, "TT And")
giris_kutusu.pack(side=tk.LEFT, padx=5)
tk.Button(arama_frame, text="🔍 Arama Yap", font=("Arial", 10, "bold"),
          bg="#4a90d9", fg="white", command=arama_thread).pack(side=tk.LEFT, padx=5)

# === Format Bölümü ===
format_frame = tk.Frame(pencere, bg="#f0f0f0")
format_frame.pack(pady=2)
tk.Label(format_frame, text="İndirme Formatı: ", bg="#f0f0f0", font=("Arial", 10)).pack(side=tk.LEFT)
format_var = tk.StringVar(value="CSV")
tk.Radiobutton(format_frame, text="CSV", variable=format_var, value="CSV", bg="#f0f0f0").pack(side=tk.LEFT)
tk.Radiobutton(format_frame, text="FITS", variable=format_var, value="FITS", bg="#f0f0f0").pack(side=tk.LEFT)

# === Sonuç Listesi (Checkbox'lı) ===
sonuc_label = tk.Label(pencere, text="Arama Sonuçları (indirmek istediklerinizi tiklayın):",
                       font=("Arial", 10, "bold"), bg="#f0f0f0")
sonuc_label.pack(anchor="w", padx=15, pady=(10, 2))

checkbox_container = tk.Frame(pencere, bd=1, relief=tk.SUNKEN)
checkbox_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=2)

checkbox_canvas = tk.Canvas(checkbox_container, bg="white", highlightthickness=0)
scrollbar = tk.Scrollbar(checkbox_container, orient="vertical", command=checkbox_canvas.yview)
checkbox_frame_inner = tk.Frame(checkbox_canvas, bg="white")

checkbox_frame_inner.bind("<Configure>",
    lambda e: checkbox_canvas.config(scrollregion=checkbox_canvas.bbox("all")))
checkbox_canvas.create_window((0, 0), window=checkbox_frame_inner, anchor="nw")
checkbox_canvas.config(yscrollcommand=scrollbar.set)

scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
checkbox_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Mouse wheel scroll
def _on_mousewheel(event):
    checkbox_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
checkbox_canvas.bind_all("<MouseWheel>", _on_mousewheel)

# === Seçim Butonları ===
secim_frame = tk.Frame(pencere, bg="#f0f0f0")
secim_frame.pack(pady=5)
tk.Button(secim_frame, text="✅ Tümünü Seç", font=("Arial", 9),
          bg="#a0d0a0", command=tumunu_sec).pack(side=tk.LEFT, padx=5)
tk.Button(secim_frame, text="❌ Tümünü Kaldır", font=("Arial", 9),
          bg="#d0a0a0", command=tumunu_kaldir).pack(side=tk.LEFT, padx=5)
tk.Button(secim_frame, text="📈 Seçilenleri Göster", font=("Arial", 10, "bold"),
          bg="#4fc3f7", command=goster_thread).pack(side=tk.LEFT, padx=5)
tk.Button(secim_frame, text="⬇️ Seçilenleri İndir", font=("Arial", 10, "bold"),
          bg="#5cb85c", fg="white", command=indirme_thread).pack(side=tk.LEFT, padx=10)

# === Log Alanı ===
tk.Label(pencere, text="İşlem Günlüğü:", font=("Arial", 10, "bold"),
         bg="#f0f0f0").pack(anchor="w", padx=15, pady=(5, 2))
log_alani = scrolledtext.ScrolledText(pencere, width=85, height=7, font=("Courier New", 9))
log_alani.pack(padx=15, pady=(0, 5))

# İmza
tk.Label(pencere, text="mustafa salman", font=("Arial", 8, "italic"),
         fg="gray", bg="#f0f0f0").pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=5)

pencere.mainloop()

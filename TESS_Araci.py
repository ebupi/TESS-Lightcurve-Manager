import sys
import os
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QComboBox, QCheckBox, QTextEdit, QMessageBox, QGroupBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import lightkurve as lk

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT

from astroquery.mast import conf as mast_conf
from astropy.utils.data import conf as astropy_conf

mast_conf.timeout = 3600
astropy_conf.remote_timeout = 3600

class SearchThread(QThread):
    log_signal = pyqtSignal(str)
    result_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)
    
    def __init__(self, target):
        super().__init__()
        self.target = target
        
    def run(self):
        self.log_signal.emit(f"🔍 '{self.target}' aranıyor...")
        try:
            results = []
            targets = [h.strip() for h in self.target.split(',')] if ',' in self.target else [self.target]
            for h in targets:
                res = lk.search_lightcurve(h)
                if len(res) > 0:
                    for idx in range(len(res)):
                        results.append((h, res[idx]))
            
            if len(results) == 0:
                self.log_signal.emit("❌ Sonuç bulunamadı.")
            else:
                self.log_signal.emit(f"✅ Toplam {len(results)} sonuç bulundu.")
            self.result_signal.emit(results)
        except Exception as e:
            self.error_signal.emit(str(e))

class DownloadThread(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    
    def __init__(self, data, fmt, sep, dec, cols):
        super().__init__()
        self.data = data # list of (hedef_adi, target, index)
        self.fmt = fmt
        self.sep = sep
        self.dec = dec
        self.cols = cols
        
    def run(self):
        self.log_signal.emit(f"⬇️ {len(self.data)} veri ({self.fmt}) formatında indiriliyor...")
        for h_adi, target, idx in self.data:
            hedef_temiz = h_adi.replace(" ", "_")
            misyon_adi = str(target.mission[0]).replace(" ", "")
            yazar_adi = str(target.author[0])
            uzanti = "csv" if self.fmt == "CSV" else "fits"
            dosya_adi = f"{hedef_temiz}_{misyon_adi}_{yazar_adi}_indeks{idx}.{uzanti}"
            
            self.log_signal.emit(f"⏳ İndiriliyor: {dosya_adi}")
            try:
                lc = target.download()
                if lc is not None:
                    lc_temiz = lc.normalize().remove_nans().remove_outliers()
                    
                    if self.fmt == "CSV":
                        df = lc_temiz.to_pandas()
                        available_cols = [c for c in self.cols if c in df.columns]
                        if not available_cols:
                            self.log_signal.emit(f"⚠️ {dosya_adi} için seçilen sütunlar bulunamadı. Tamamı kaydediliyor.")
                            df.to_csv(dosya_adi, sep=self.sep, decimal=self.dec)
                        else:
                            df[available_cols].to_csv(dosya_adi, sep=self.sep, decimal=self.dec, index=False)
                    else:
                        lc_temiz.to_fits(dosya_adi, overwrite=True)
                    self.log_signal.emit(f"✅ Kaydedildi: {dosya_adi}")
            except Exception as e:
                self.log_signal.emit(f"❌ Hata ({h_adi}): {e}")
                
        self.log_signal.emit("🎉 Tüm indirme/kaydetme işlemleri tamamlandı!")
        self.finished_signal.emit()

class PlotThread(QThread):
    log_signal = pyqtSignal(str)
    plot_data_signal = pyqtSignal(list)
    finished_signal = pyqtSignal()
    
    def __init__(self, data):
        super().__init__()
        self.data = data
        
    def run(self):
        self.log_signal.emit(f"📈 {len(self.data)} adet verinin ışık eğrisi çiziliyor...")
        plot_items = []
        for h_adi, target, idx in self.data:
            try:
                lc = target.download()
                if lc is not None:
                    lc_temiz = lc.normalize().remove_nans().remove_outliers()
                    plot_items.append((h_adi, str(target.mission[0]), lc_temiz.time.value, lc_temiz.flux.value, idx))
            except Exception as e:
                self.log_signal.emit(f"❌ Çizim hatası ({h_adi}): {e}")
        self.plot_data_signal.emit(plot_items)
        self.finished_signal.emit()

class TESSApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TESS Işık Eğrisi Yöneticisi (PyQt5)")
        self.resize(1300, 850)
        self.global_search_result = []
        self.initUI()
        
    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # SOL PANEL
        left_layout = QVBoxLayout()
        main_layout.addLayout(left_layout, stretch=3)
        
        # Arama Kısmı
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Gök cismi adı girin (Örn: TT And)")
        self.search_input.setText("TT And")
        self.search_input.setMinimumHeight(40)
        font = self.search_input.font()
        font.setPointSize(11)
        self.search_input.setFont(font)
        
        self.search_btn = QPushButton("🔍 Arama Yap")
        self.search_btn.setMinimumHeight(40)
        self.search_btn.setFont(QFont("Arial", 11, QFont.Bold))
        self.search_btn.clicked.connect(self.start_search)
        
        lbl_gokcismi = QLabel("Gök Cismi:")
        lbl_gokcismi.setFont(QFont("Arial", 11, QFont.Bold))
        search_layout.addWidget(lbl_gokcismi)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        left_layout.addLayout(search_layout)
        
        # Plot Kısmı
        self.fig = Figure(figsize=(9, 4.5), dpi=100)
        self.fig.patch.set_facecolor('#ffffff')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#f8f9fa')
        self.ax.set_xlabel("Zaman (BTJD)")
        self.ax.set_ylabel("Normalize Akı")
        self.ax.set_title("Birleştirilmiş Işık Eğrileri Grafiği")
        self.fig.tight_layout()
        
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        
        left_layout.addWidget(self.canvas, stretch=2)
        left_layout.addWidget(self.toolbar)
        
        # Sonuç Tablosu
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Seç", "İndeks", "Gök Cismi", "Misyon", "Yazar", "Exptime"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("QTableWidget { font-size: 13px; }")
        left_layout.addWidget(self.table, stretch=1)
        
        # SAĞ PANEL
        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout, stretch=1)
        
        settings_group = QGroupBox("⚙️ Dışa Aktarma Ayarları")
        settings_group.setFont(QFont("Arial", 11, QFont.Bold))
        set_layout = QVBoxLayout(settings_group)
        
        font_normal = QFont("Arial", 10)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["CSV", "FITS"])
        self.format_combo.setFont(font_normal)
        self.format_combo.setMinimumHeight(35)
        lbl_fmt = QLabel("Format:")
        lbl_fmt.setFont(font_normal)
        set_layout.addWidget(lbl_fmt)
        set_layout.addWidget(self.format_combo)
        
        self.sep_combo = QComboBox()
        self.sep_combo.addItems(["Virgül (,)", "Noktalı Virgül (;)", "Sekme (Tab)"])
        self.sep_combo.setFont(font_normal)
        self.sep_combo.setMinimumHeight(35)
        lbl_sep = QLabel("Ayırıcı (Separator):")
        lbl_sep.setFont(font_normal)
        set_layout.addWidget(lbl_sep)
        set_layout.addWidget(self.sep_combo)
        
        self.dec_combo = QComboBox()
        self.dec_combo.addItems(["Nokta (.)", "Virgül (,)"])
        self.dec_combo.setFont(font_normal)
        self.dec_combo.setMinimumHeight(35)
        lbl_dec = QLabel("Ondalık Ayırıcı (Decimal):")
        lbl_dec.setFont(font_normal)
        set_layout.addWidget(lbl_dec)
        set_layout.addWidget(self.dec_combo)
        
        lbl_cols = QLabel("Kaydedilecek Sütunlar:")
        lbl_cols.setFont(QFont("Arial", 10, QFont.Bold))
        set_layout.addWidget(lbl_cols)
        
        self.cb_time = QCheckBox("Zaman (time)")
        self.cb_time.setChecked(True)
        self.cb_time.setFont(font_normal)
        
        self.cb_flux = QCheckBox("Akı (flux)")
        self.cb_flux.setChecked(True)
        self.cb_flux.setFont(font_normal)
        
        self.cb_err = QCheckBox("Akı Hatası (flux_err)")
        self.cb_err.setChecked(True)
        self.cb_err.setFont(font_normal)
        
        set_layout.addWidget(self.cb_time)
        set_layout.addWidget(self.cb_flux)
        set_layout.addWidget(self.cb_err)
        
        right_layout.addWidget(settings_group)
        
        # Butonlar
        self.btn_select_all = QPushButton("☑ Tümünü Seç")
        self.btn_select_all.setMinimumHeight(35)
        self.btn_select_all.clicked.connect(self.select_all)
        
        self.btn_deselect_all = QPushButton("☐ Seçimi Temizle")
        self.btn_deselect_all.setMinimumHeight(35)
        self.btn_deselect_all.clicked.connect(self.deselect_all)
        
        self.btn_plot = QPushButton("📈 Seçilenleri Çiz")
        self.btn_plot.clicked.connect(self.start_plot)
        self.btn_plot.setMinimumHeight(45)
        
        self.btn_download = QPushButton("⬇️ Seçilenleri İndir / Kaydet")
        self.btn_download.clicked.connect(self.start_download)
        self.btn_download.setMinimumHeight(50)
        
        # PyQt stylesheets for styling buttons
        self.btn_plot.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8; 
                color: white; 
                font-weight: bold;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #138496; }
        """)
        
        self.btn_download.setStyleSheet("""
            QPushButton {
                background-color: #007bff; 
                color: white; 
                font-weight: bold;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #0069d9; }
        """)
        
        right_layout.addWidget(self.btn_select_all)
        right_layout.addWidget(self.btn_deselect_all)
        right_layout.addSpacing(15)
        right_layout.addWidget(self.btn_plot)
        right_layout.addWidget(self.btn_download)
        
        # Log 
        lbl_log = QLabel("İşlem Günlüğü:")
        lbl_log.setFont(QFont("Arial", 10, QFont.Bold))
        right_layout.addSpacing(15)
        right_layout.addWidget(lbl_log)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))
        right_layout.addWidget(self.log_text)
        
        self.log("🚀 Sistem hazır. (PyQt5 Framework)")
        
    def log(self, msg):
        self.log_text.append(msg)
        
    def start_search(self):
        target = self.search_input.text().strip()
        if not target:
            return
        self.search_btn.setEnabled(False)
        self.table.setRowCount(0)
        self.global_search_result = []
        
        self.search_thread = SearchThread(target)
        self.search_thread.log_signal.connect(self.log)
        self.search_thread.result_signal.connect(self.populate_table)
        self.search_thread.error_signal.connect(lambda e: self.log(f"❌ Hata: {e}"))
        self.search_thread.finished.connect(lambda: self.search_btn.setEnabled(True))
        self.search_thread.start()
        
    def populate_table(self, results):
        self.global_search_result = results
        self.table.setRowCount(len(results))
        for i, (h_adi, target) in enumerate(results):
            chkBoxItem = QTableWidgetItem()
            chkBoxItem.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            chkBoxItem.setCheckState(Qt.Unchecked)
            self.table.setItem(i, 0, chkBoxItem)
            
            self.table.setItem(i, 1, QTableWidgetItem(str(i)))
            self.table.setItem(i, 2, QTableWidgetItem(h_adi))
            self.table.setItem(i, 3, QTableWidgetItem(str(target.mission[0])))
            self.table.setItem(i, 4, QTableWidgetItem(str(target.author[0])))
            self.table.setItem(i, 5, QTableWidgetItem(str(target.exptime[0])))
            
    def get_selected_data(self):
        selected = []
        for i in range(self.table.rowCount()):
            if self.table.item(i, 0).checkState() == Qt.Checked:
                selected.append((self.global_search_result[i][0], self.global_search_result[i][1], i))
        return selected

    def select_all(self):
        for i in range(self.table.rowCount()):
            self.table.item(i, 0).setCheckState(Qt.Checked)

    def deselect_all(self):
        for i in range(self.table.rowCount()):
            self.table.item(i, 0).setCheckState(Qt.Unchecked)
            
    def start_plot(self):
        selected = self.get_selected_data()
        if not selected:
            self.log("⚠️ Çizim yapmak için veri seçmediniz.")
            return
            
        self.btn_plot.setEnabled(False)
        self.plot_thread = PlotThread(selected)
        self.plot_thread.log_signal.connect(self.log)
        self.plot_thread.plot_data_signal.connect(self.update_plot)
        self.plot_thread.finished_signal.connect(lambda: self.btn_plot.setEnabled(True))
        self.plot_thread.start()
        
    def update_plot(self, plot_items):
        self.ax.clear()
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        has_data = False
        
        for idx, (h_adi, misyon, time_val, flux_val, i) in enumerate(plot_items):
            color = colors[idx % len(colors)]
            self.ax.scatter(time_val, flux_val, s=2, label=f"[{i}] {h_adi} ({misyon})", color=color, alpha=0.8)
            has_data = True
            
        if has_data:
            self.ax.set_xlabel("Zaman (BTJD)")
            self.ax.set_ylabel("Normalize Akı")
            self.ax.legend(loc='upper right', fontsize='small')
            self.ax.set_title("Birleştirilmiş Işık Eğrileri")
            self.fig.tight_layout()
            self.canvas.draw()
            self.log("✅ Çizim tamamlandı.")
        else:
            self.log("⚠️ Çizilecek veri indirilemedi.")
            
    def start_download(self):
        selected = self.get_selected_data()
        if not selected:
            self.log("⚠️ İndirmek için veri seçmediniz.")
            return
            
        fmt = self.format_combo.currentText()
        sep_map = {"Virgül (,)": ",", "Noktalı Virgül (;)": ";", "Sekme (Tab)": "\t"}
        dec_map = {"Nokta (.)": ".", "Virgül (,)": ","}
        
        sep = sep_map.get(self.sep_combo.currentText(), ",")
        dec = dec_map.get(self.dec_combo.currentText(), ".")
        
        cols = []
        if self.cb_time.isChecked(): cols.append("time")
        if self.cb_flux.isChecked(): cols.append("flux")
        if self.cb_err.isChecked(): cols.append("flux_err")
        
        if fmt == "CSV" and not cols:
            self.log("❌ Hata: Kaydetmek için en az bir sütun seçmelisiniz!")
            return
            
        self.btn_download.setEnabled(False)
        self.download_thread = DownloadThread(selected, fmt, sep, dec, cols)
        self.download_thread.log_signal.connect(self.log)
        self.download_thread.finished_signal.connect(lambda: self.btn_download.setEnabled(True))
        self.download_thread.start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ex = TESSApp()
    ex.show()
    sys.exit(app.exec_())

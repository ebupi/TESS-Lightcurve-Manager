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

TRANSLATIONS = {
    "EN": {
        "title": "TESS Lightcurve Manager",
        "search_label": "Target Name (e.g. TT And):",
        "search_placeholder": "Enter target name...",
        "search_btn": "🔍 Search",
        "searching": "🔍 Searching for '{}'...",
        "not_found": "❌ No results found.",
        "found": "✅ Found {} results.",
        "error": "❌ Error: {}",
        "plot_title": "Combined Lightcurves",
        "xaxis": "Time (BTJD)",
        "yaxis": "Normalized Flux",
        "table_headers": ["Select", "Index", "Target", "Mission", "Author", "Exptime"],
        "settings_title": "⚙️ Export Settings",
        "format": "Format:",
        "separator": "Separator:",
        "decimal": "Decimal:",
        "cols_to_save": "Columns to Save:",
        "time": "Time",
        "flux": "Flux",
        "flux_err": "Flux Error",
        "cols_note": "(If none selected, all available columns will be saved)",
        "select_all": "☑ Select All",
        "deselect_all": "☐ Deselect All",
        "plot_btn": "📈 Plot Selected",
        "download_btn": "⬇️ Download / Save Selected",
        "log_title": "Operation Log:",
        "ready": "🚀 System ready. (PyQt5 Framework)",
        "plot_no_sel": "⚠️ No data selected for plotting.",
        "plot_start": "📈 Plotting {} lightcurves...",
        "plot_err": "❌ Plot error ({}): {}",
        "plot_done": "✅ Plotting completed.",
        "plot_fail": "⚠️ Could not download data for plotting.",
        "dl_no_sel": "⚠️ No data selected for download.",
        "dl_start": "⬇️ Downloading {} files in ({}) format...",
        "dl_progress": "⏳ Downloading: {}",
        "dl_warn_cols": "⚠️ Selected columns not found for {}. Saving all available columns.",
        "dl_done": "✅ Saved: {}",
        "dl_err": "❌ Error ({}): {}",
        "dl_complete": "🎉 All download/save operations completed!",
        "lang": "Language (Dil):",
        "sep_comma": "Comma (,)",
        "sep_semi": "Semicolon (;)",
        "sep_tab": "Tab (\\t)",
        "dec_dot": "Dot (.)",
        "dec_comma": "Comma (,)"
    },
    "TR": {
        "title": "TESS Işık Eğrisi Yöneticisi",
        "search_label": "Gök Cismi (Örn: TT And):",
        "search_placeholder": "Gök cismi adı girin...",
        "search_btn": "🔍 Arama Yap",
        "searching": "🔍 '{}' aranıyor...",
        "not_found": "❌ Sonuç bulunamadı.",
        "found": "✅ Toplam {} sonuç bulundu.",
        "error": "❌ Hata: {}",
        "plot_title": "Birleştirilmiş Işık Eğrileri",
        "xaxis": "Zaman (BTJD)",
        "yaxis": "Normalize Akı",
        "table_headers": ["Seç", "İndeks", "Gök Cismi", "Misyon", "Yazar", "Exptime"],
        "settings_title": "⚙️ Dışa Aktarma Ayarları",
        "format": "Format:",
        "separator": "Ayırıcı (Separator):",
        "decimal": "Ondalık Ayırıcı (Decimal):",
        "cols_to_save": "Kaydedilecek Sütunlar:",
        "time": "Zaman (time)",
        "flux": "Akı (flux)",
        "flux_err": "Akı Hatası (flux_err)",
        "cols_note": "(Tüm sütunları indirmek için hiçbirini seçmeyin)",
        "select_all": "☑ Tümünü Seç",
        "deselect_all": "☐ Seçimi Temizle",
        "plot_btn": "📈 Seçilenleri Çiz",
        "download_btn": "⬇️ Seçilenleri İndir / Kaydet",
        "log_title": "İşlem Günlüğü:",
        "ready": "🚀 Sistem hazır. (PyQt5 Framework)",
        "plot_no_sel": "⚠️ Çizim yapmak için veri seçmediniz.",
        "plot_start": "📈 {} adet verinin ışık eğrisi çiziliyor...",
        "plot_err": "❌ Çizim hatası ({}): {}",
        "plot_done": "✅ Çizim tamamlandı.",
        "plot_fail": "⚠️ Çizilecek veri indirilemedi.",
        "dl_no_sel": "⚠️ İndirmek için veri seçmediniz.",
        "dl_start": "⬇️ {} veri ({}) formatında indiriliyor...",
        "dl_progress": "⏳ İndiriliyor: {}",
        "dl_warn_cols": "⚠️ {} için seçilen sütunlar bulunamadı. Tamamı kaydediliyor.",
        "dl_done": "✅ Kaydedildi: {}",
        "dl_err": "❌ Hata ({}): {}",
        "dl_complete": "🎉 Tüm indirme/kaydetme işlemleri tamamlandı!",
        "lang": "Dil (Language):",
        "sep_comma": "Virgül (,)",
        "sep_semi": "Noktalı Virgül (;)",
        "sep_tab": "Sekme (Tab)",
        "dec_dot": "Nokta (.)",
        "dec_comma": "Virgül (,)"
    }
}

class SearchThread(QThread):
    log_signal = pyqtSignal(str)
    result_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)
    
    def __init__(self, target, app_ref):
        super().__init__()
        self.target = target
        self.app_ref = app_ref
        
    def run(self):
        self.log_signal.emit(self.app_ref.t("searching").format(self.target))
        try:
            results = []
            targets = [h.strip() for h in self.target.split(',')] if ',' in self.target else [self.target]
            for h in targets:
                res = lk.search_lightcurve(h)
                if len(res) > 0:
                    for idx in range(len(res)):
                        results.append((h, res[idx]))
            
            if len(results) == 0:
                self.log_signal.emit(self.app_ref.t("not_found"))
            else:
                self.log_signal.emit(self.app_ref.t("found").format(len(results)))
            self.result_signal.emit(results)
        except Exception as e:
            self.error_signal.emit(self.app_ref.t("error").format(e))

class DownloadThread(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    
    def __init__(self, data, fmt, sep, dec, cols, app_ref):
        super().__init__()
        self.data = data
        self.fmt = fmt
        self.sep = sep
        self.dec = dec
        self.cols = cols
        self.app_ref = app_ref
        
    def run(self):
        self.log_signal.emit(self.app_ref.t("dl_start").format(len(self.data), self.fmt))
        for h_adi, target, idx in self.data:
            hedef_temiz = h_adi.replace(" ", "_")
            misyon_adi = str(target.mission[0]).replace(" ", "")
            yazar_adi = str(target.author[0])
            uzanti = "csv" if self.fmt == "CSV" else "fits"
            dosya_adi = f"{hedef_temiz}_{misyon_adi}_{yazar_adi}_indeks{idx}.{uzanti}"
            
            self.log_signal.emit(self.app_ref.t("dl_progress").format(dosya_adi))
            try:
                lc = target.download()
                if lc is not None:
                    lc_temiz = lc.normalize().remove_nans().remove_outliers()
                    
                    if self.fmt == "CSV":
                        df = lc_temiz.to_pandas()
                        available_cols = [c for c in self.cols if c in df.columns]
                        
                        # IF no columns selected OR selected columns not in df -> save all
                        if not self.cols:
                            df.to_csv(dosya_adi, sep=self.sep, decimal=self.dec)
                        elif not available_cols:
                            self.log_signal.emit(self.app_ref.t("dl_warn_cols").format(dosya_adi))
                            df.to_csv(dosya_adi, sep=self.sep, decimal=self.dec)
                        else:
                            df[available_cols].to_csv(dosya_adi, sep=self.sep, decimal=self.dec, index=False)
                    else:
                        lc_temiz.to_fits(dosya_adi, overwrite=True)
                    self.log_signal.emit(self.app_ref.t("dl_done").format(dosya_adi))
            except Exception as e:
                self.log_signal.emit(self.app_ref.t("dl_err").format(h_adi, e))
                
        self.log_signal.emit(self.app_ref.t("dl_complete"))
        self.finished_signal.emit()

class PlotThread(QThread):
    log_signal = pyqtSignal(str)
    plot_data_signal = pyqtSignal(list)
    finished_signal = pyqtSignal()
    
    def __init__(self, data, app_ref):
        super().__init__()
        self.data = data
        self.app_ref = app_ref
        
    def run(self):
        self.log_signal.emit(self.app_ref.t("plot_start").format(len(self.data)))
        plot_items = []
        for h_adi, target, idx in self.data:
            try:
                lc = target.download()
                if lc is not None:
                    lc_temiz = lc.normalize().remove_nans().remove_outliers()
                    plot_items.append((h_adi, str(target.mission[0]), lc_temiz.time.value, lc_temiz.flux.value, idx))
            except Exception as e:
                self.log_signal.emit(self.app_ref.t("plot_err").format(h_adi, e))
        self.plot_data_signal.emit(plot_items)
        self.finished_signal.emit()

class TESSApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lang = "EN"
        self.global_search_result = []
        self.initUI()
        
    def t(self, key):
        return TRANSLATIONS[self.lang].get(key, key)
        
    def initUI(self):
        self.resize(1300, 850)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # LEFT PANEL
        left_layout = QVBoxLayout()
        main_layout.addLayout(left_layout, stretch=3)
        
        # Search layout
        search_layout = QHBoxLayout()
        self.lbl_gokcismi = QLabel()
        self.lbl_gokcismi.setFont(QFont("Arial", 11, QFont.Bold))
        
        self.search_input = QLineEdit()
        self.search_input.setText("TT And")
        self.search_input.setMinimumHeight(40)
        font = self.search_input.font()
        font.setPointSize(11)
        self.search_input.setFont(font)
        
        self.search_btn = QPushButton()
        self.search_btn.setMinimumHeight(40)
        self.search_btn.setFont(QFont("Arial", 11, QFont.Bold))
        self.search_btn.clicked.connect(self.start_search)
        
        search_layout.addWidget(self.lbl_gokcismi)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        left_layout.addLayout(search_layout)
        
        # Plot layout
        self.fig = Figure(figsize=(9, 4.5), dpi=100)
        self.fig.patch.set_facecolor('#ffffff')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#f8f9fa')
        
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        
        left_layout.addWidget(self.canvas, stretch=2)
        left_layout.addWidget(self.toolbar)
        
        # Table layout
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("QTableWidget { font-size: 13px; }")
        left_layout.addWidget(self.table, stretch=1)
        
        # RIGHT PANEL
        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout, stretch=1)
        
        # Language Selector
        lang_layout = QHBoxLayout()
        self.lbl_lang = QLabel()
        self.lbl_lang.setFont(QFont("Arial", 10, QFont.Bold))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["EN", "TR"])
        self.lang_combo.setCurrentText("EN")
        self.lang_combo.currentTextChanged.connect(self.change_language)
        lang_layout.addWidget(self.lbl_lang)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        right_layout.addLayout(lang_layout)
        
        self.settings_group = QGroupBox()
        self.settings_group.setFont(QFont("Arial", 11, QFont.Bold))
        set_layout = QVBoxLayout(self.settings_group)
        
        font_normal = QFont("Arial", 10)
        
        self.lbl_fmt = QLabel()
        self.lbl_fmt.setFont(font_normal)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["CSV", "FITS"])
        self.format_combo.setFont(font_normal)
        self.format_combo.setMinimumHeight(35)
        set_layout.addWidget(self.lbl_fmt)
        set_layout.addWidget(self.format_combo)
        
        self.lbl_sep = QLabel()
        self.lbl_sep.setFont(font_normal)
        self.sep_combo = QComboBox()
        self.sep_combo.setFont(font_normal)
        self.sep_combo.setMinimumHeight(35)
        set_layout.addWidget(self.lbl_sep)
        set_layout.addWidget(self.sep_combo)
        
        self.lbl_dec = QLabel()
        self.lbl_dec.setFont(font_normal)
        self.dec_combo = QComboBox()
        self.dec_combo.setFont(font_normal)
        self.dec_combo.setMinimumHeight(35)
        set_layout.addWidget(self.lbl_dec)
        set_layout.addWidget(self.dec_combo)
        
        self.lbl_cols = QLabel()
        self.lbl_cols.setFont(QFont("Arial", 10, QFont.Bold))
        set_layout.addWidget(self.lbl_cols)
        
        self.cb_time = QCheckBox()
        self.cb_time.setChecked(True)
        self.cb_time.setFont(font_normal)
        
        self.cb_flux = QCheckBox()
        self.cb_flux.setChecked(True)
        self.cb_flux.setFont(font_normal)
        
        self.cb_err = QCheckBox()
        self.cb_err.setChecked(True)
        self.cb_err.setFont(font_normal)
        
        set_layout.addWidget(self.cb_time)
        set_layout.addWidget(self.cb_flux)
        set_layout.addWidget(self.cb_err)
        
        self.lbl_cols_note = QLabel()
        self.lbl_cols_note.setFont(QFont("Arial", 8, QFont.StyleItalic))
        self.lbl_cols_note.setStyleSheet("color: gray;")
        self.lbl_cols_note.setWordWrap(True)
        set_layout.addWidget(self.lbl_cols_note)
        
        right_layout.addWidget(self.settings_group)
        
        # Buttons
        self.btn_select_all = QPushButton()
        self.btn_select_all.setMinimumHeight(35)
        self.btn_select_all.clicked.connect(self.select_all)
        
        self.btn_deselect_all = QPushButton()
        self.btn_deselect_all.setMinimumHeight(35)
        self.btn_deselect_all.clicked.connect(self.deselect_all)
        
        self.btn_plot = QPushButton()
        self.btn_plot.clicked.connect(self.start_plot)
        self.btn_plot.setMinimumHeight(45)
        
        self.btn_download = QPushButton()
        self.btn_download.clicked.connect(self.start_download)
        self.btn_download.setMinimumHeight(50)
        
        self.btn_plot.setStyleSheet("""
            QPushButton { background-color: #17a2b8; color: white; font-weight: bold; font-size: 14px; border-radius: 5px; }
            QPushButton:hover { background-color: #138496; }
        """)
        
        self.btn_download.setStyleSheet("""
            QPushButton { background-color: #007bff; color: white; font-weight: bold; font-size: 14px; border-radius: 5px; }
            QPushButton:hover { background-color: #0069d9; }
        """)
        
        right_layout.addWidget(self.btn_select_all)
        right_layout.addWidget(self.btn_deselect_all)
        right_layout.addSpacing(15)
        right_layout.addWidget(self.btn_plot)
        right_layout.addWidget(self.btn_download)
        
        # Log 
        self.lbl_log = QLabel()
        self.lbl_log.setFont(QFont("Arial", 10, QFont.Bold))
        right_layout.addSpacing(15)
        right_layout.addWidget(self.lbl_log)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))
        right_layout.addWidget(self.log_text)
        
        # Apply initial translation
        self.update_texts()
        self.log(self.t("ready"))
        
    def update_texts(self):
        self.setWindowTitle(self.t("title"))
        self.lbl_gokcismi.setText(self.t("search_label"))
        self.search_input.setPlaceholderText(self.t("search_placeholder"))
        self.search_btn.setText(self.t("search_btn"))
        
        self.ax.set_xlabel(self.t("xaxis"))
        self.ax.set_ylabel(self.t("yaxis"))
        if not self.ax.get_title():
            self.ax.set_title(self.t("plot_title"))
        else:
            # If it had a title, we just enforce the translation (might override specific dataset title, but it's ok for base plot)
            if self.ax.get_title() in [TRANSLATIONS["EN"]["plot_title"], TRANSLATIONS["TR"]["plot_title"]]:
                self.ax.set_title(self.t("plot_title"))
        self.fig.tight_layout()
        self.canvas.draw()
        
        self.table.setHorizontalHeaderLabels(self.t("table_headers"))
        
        self.settings_group.setTitle(self.t("settings_title"))
        self.lbl_fmt.setText(self.t("format"))
        
        # Update combo box items (save current index)
        sep_idx = self.sep_combo.currentIndex()
        if sep_idx == -1: sep_idx = 0
        self.sep_combo.clear()
        self.sep_combo.addItems([self.t("sep_comma"), self.t("sep_semi"), self.t("sep_tab")])
        self.sep_combo.setCurrentIndex(sep_idx)
        self.lbl_sep.setText(self.t("separator"))
        
        dec_idx = self.dec_combo.currentIndex()
        if dec_idx == -1: dec_idx = 0
        self.dec_combo.clear()
        self.dec_combo.addItems([self.t("dec_dot"), self.t("dec_comma")])
        self.dec_combo.setCurrentIndex(dec_idx)
        self.lbl_dec.setText(self.t("decimal"))
        
        self.lbl_cols.setText(self.t("cols_to_save"))
        self.cb_time.setText(self.t("time"))
        self.cb_flux.setText(self.t("flux"))
        self.cb_err.setText(self.t("flux_err"))
        self.lbl_cols_note.setText(self.t("cols_note"))
        
        self.btn_select_all.setText(self.t("select_all"))
        self.btn_deselect_all.setText(self.t("deselect_all"))
        self.btn_plot.setText(self.t("plot_btn"))
        self.btn_download.setText(self.t("download_btn"))
        self.lbl_log.setText(self.t("log_title"))
        self.lbl_lang.setText(self.t("lang"))
        
    def change_language(self, lang_code):
        self.lang = lang_code
        self.update_texts()
        
    def log(self, msg):
        self.log_text.append(msg)
        
    def start_search(self):
        target = self.search_input.text().strip()
        if not target:
            return
        self.search_btn.setEnabled(False)
        self.table.setRowCount(0)
        self.global_search_result = []
        
        self.search_thread = SearchThread(target, self)
        self.search_thread.log_signal.connect(self.log)
        self.search_thread.result_signal.connect(self.populate_table)
        self.search_thread.error_signal.connect(lambda e: self.log(e))
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
            self.log(self.t("plot_no_sel"))
            return
            
        self.btn_plot.setEnabled(False)
        self.plot_thread = PlotThread(selected, self)
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
            self.ax.set_xlabel(self.t("xaxis"))
            self.ax.set_ylabel(self.t("yaxis"))
            self.ax.legend(loc='upper right', fontsize='small')
            self.ax.set_title(self.t("plot_title"))
            self.fig.tight_layout()
            self.canvas.draw()
            self.log(self.t("plot_done"))
        else:
            self.log(self.t("plot_fail"))
            
    def start_download(self):
        selected = self.get_selected_data()
        if not selected:
            self.log(self.t("dl_no_sel"))
            return
            
        fmt = self.format_combo.currentText()
        sep = ","
        if self.sep_combo.currentIndex() == 1: sep = ";"
        elif self.sep_combo.currentIndex() == 2: sep = "\t"
        
        dec = "." if self.dec_combo.currentIndex() == 0 else ","
        
        cols = []
        if self.cb_time.isChecked(): cols.append("time")
        if self.cb_flux.isChecked(): cols.append("flux")
        if self.cb_err.isChecked(): cols.append("flux_err")
        
        self.btn_download.setEnabled(False)
        self.download_thread = DownloadThread(selected, fmt, sep, dec, cols, self)
        self.download_thread.log_signal.connect(self.log)
        self.download_thread.finished_signal.connect(lambda: self.btn_download.setEnabled(True))
        self.download_thread.start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ex = TESSApp()
    ex.show()
    sys.exit(app.exec_())

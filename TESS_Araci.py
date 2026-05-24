import sys
import os
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QComboBox, QCheckBox, QTextEdit, QMessageBox, QGroupBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView

import lightkurve as lk
import plotly.graph_objects as go
from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive
from astroquery.vizier import Vizier

from astroquery.mast import conf as mast_conf
from astropy.utils.data import conf as astropy_conf

mast_conf.timeout = 60
astropy_conf.remote_timeout = 60

TRANSLATIONS = {
    "EN": {
        "title": "TESS Lightcurve Studio",
        "search_label": "Target Name:",
        "search_placeholder": "e.g. TT And",
        "search_btn": "🔍 Search",
        "searching": "🔍 Searching for '{}'... (MAST servers may take 10-30s, please wait)",
        "not_found": "❌ No results found.",
        "found": "✅ Found {} results.",
        "error": "❌ Error: {}",
        "plot_title": "Combined Lightcurves",
        "xaxis": "Time (BTJD)",
        "plot_phase_axis": "Phase",
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
        "ready": "🚀 System ready. (PyQt5 + Plotly)",
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
        "dec_comma": "Comma (,)",
        "eph_t0": "Epoch T0 (BJD):",
        "eph_p": "Period (P):",
        "eph_find": "🔍 Find T0/P",
        "eph_searching": "🔍 Searching Ephemeris for '{}'...",
        "eph_found": "✅ Ephemeris found! T0: {}, P: {}",
        "eph_not_found": "❌ Ephemeris not found.",
        "plot_phase": "Phase Fold Plot"
    },
    "TR": {
        "title": "TESS Işık Eğrisi Studio",
        "search_label": "Gök Cismi:",
        "search_placeholder": "Örn: TT And",
        "search_btn": "🔍 Arama Yap",
        "searching": "🔍 '{}' aranıyor... (MAST sunucuları 10-30sn sürebilir, lütfen bekleyin)",
        "not_found": "❌ Sonuç bulunamadı.",
        "found": "✅ Toplam {} sonuç bulundu.",
        "error": "❌ Hata: {}",
        "plot_title": "Birleştirilmiş Işık Eğrileri",
        "xaxis": "Zaman (BTJD)",
        "plot_phase_axis": "Evre (Phase)",
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
        "ready": "🚀 Sistem hazır. (PyQt5 + Plotly)",
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
        "dec_comma": "Virgül (,)",
        "eph_t0": "Epok T0 (BJD):",
        "eph_p": "Periyot (P):",
        "eph_find": "🔍 T0/P Bul",
        "eph_searching": "🔍 '{}' için Ephemeris aranıyor...",
        "eph_found": "✅ Ephemeris bulundu! T0: {}, P: {}",
        "eph_not_found": "❌ Ephemeris bulunamadı.",
        "plot_phase": "Evre Grafiği (Phase Fold)"
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
                    results.append((h, res))
            
            if len(results) == 0:
                self.log_signal.emit(self.app_ref.t("not_found"))
            else:
                total_rows = sum([len(r[1]) for r in results])
                self.log_signal.emit(self.app_ref.t("found").format(total_rows))
            self.result_signal.emit(results)
        except Exception as e:
            self.error_signal.emit(self.app_ref.t("error").format(e))

class EphemerisThread(QThread):
    log_signal = pyqtSignal(str)
    result_signal = pyqtSignal(str, str)
    
    def __init__(self, target, app_ref):
        super().__init__()
        self.target = target
        self.app_ref = app_ref
        
    def run(self):
        self.log_signal.emit(self.app_ref.t("eph_searching").format(self.target))
        t0, p = None, None
        
        # 1. Try Exoplanet Archive
        try:
            res = NasaExoplanetArchive.query_object(self.target)
            if len(res) > 0:
                p_val = res["pl_orbper"][0]
                t0_val = res["pl_tranmid"][0]
                p = str(p_val.value if hasattr(p_val, 'value') else p_val)
                t0 = str(t0_val.value if hasattr(t0_val, 'value') else t0_val)
        except Exception:
            pass
            
        # 2. Try VizieR (AAVSO VSX) if not found
        if not t0 or not p:
            try:
                v = Vizier(columns=["Name", "Period", "Epoch"])
                res = v.query_object(self.target, catalog="B/vsx/vsx")
                if len(res) > 0 and len(res[0]) > 0:
                    p_val = res[0]["Period"][0]
                    t0_val = res[0]["Epoch"][0]
                    import pandas as pd
                    if not pd.isna(p_val) and not pd.isna(t0_val):
                        p = str(p_val.value if hasattr(p_val, 'value') else p_val)
                        t0 = str(t0_val.value if hasattr(t0_val, 'value') else t0_val)
            except Exception:
                pass
                
        if t0 and p:
            self.log_signal.emit(self.app_ref.t("eph_found").format(t0, p))
            self.result_signal.emit(t0, p)
        else:
            self.log_signal.emit(self.app_ref.t("eph_not_found"))


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
        for h_adi, res_obj, idx in self.data:
            target = res_obj[idx]
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
    
    def __init__(self, data, is_phase, t0, p, app_ref):
        super().__init__()
        self.data = data
        self.is_phase = is_phase
        self.t0 = t0
        self.p = p
        self.app_ref = app_ref
        
    def run(self):
        self.log_signal.emit(self.app_ref.t("plot_start").format(len(self.data)))
        plot_items = []
        for h_adi, res_obj, idx in self.data:
            target = res_obj[idx]
            try:
                lc = target.download()
                if lc is not None:
                    lc_temiz = lc.normalize().remove_nans().remove_outliers()
                    
                    if self.is_phase and self.t0 and self.p:
                        try:
                            t0_val = float(self.t0)
                            p_val = float(self.p)
                            if lc_temiz.time.format == 'btjd' and t0_val > 2450000:
                                t0_val -= 2457000.0
                            elif lc_temiz.time.format == 'bkjd' and t0_val > 2450000:
                                t0_val -= 2454833.0
                            elif lc_temiz.time.format == 'kbjd' and t0_val > 2450000:
                                t0_val -= 2454833.0
                            lc_temiz = lc_temiz.fold(period=p_val, epoch_time=t0_val)
                        except Exception as e:
                            self.log_signal.emit("Phase Fold error: " + str(e))
                            
                    time_val = lc_temiz.time.value
                    flux_val = lc_temiz.flux.value
                    
                    plot_items.append((h_adi, str(target.mission[0]), time_val, flux_val, idx))
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
        self.setWindowIcon(QIcon("tess_icon_v2.png"))
        self.resize(1400, 900)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # LEFT PANEL
        left_layout = QVBoxLayout()
        main_layout.addLayout(left_layout, stretch=3)
        
        # Top Search Layout
        search_layout = QHBoxLayout()
        self.lbl_gokcismi = QLabel()
        self.lbl_gokcismi.setFont(QFont("Arial", 11, QFont.Bold))
        
        self.search_input = QLineEdit()
        self.search_input.setText("Kepler-10")
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
        
        # Ephemeris Settings Group
        eph_layout = QHBoxLayout()
        
        self.lbl_eph_t0 = QLabel()
        self.input_t0 = QLineEdit()
        
        self.lbl_eph_p = QLabel()
        self.input_p = QLineEdit()
        
        self.btn_find_eph = QPushButton()
        self.btn_find_eph.clicked.connect(self.find_ephemeris)
        
        self.chk_phase = QCheckBox()
        self.chk_phase.setFont(QFont("Arial", 10, QFont.Bold))
        
        eph_layout.addWidget(self.lbl_eph_t0)
        eph_layout.addWidget(self.input_t0)
        eph_layout.addWidget(self.lbl_eph_p)
        eph_layout.addWidget(self.input_p)
        eph_layout.addWidget(self.btn_find_eph)
        eph_layout.addSpacing(20)
        eph_layout.addWidget(self.chk_phase)
        eph_layout.addStretch()
        left_layout.addLayout(eph_layout)
        
        # Plotly Web View
        self.web_view = QWebEngineView()
        self.reset_plot()
        left_layout.addWidget(self.web_view, stretch=2)
        
        # Table Controls
        table_controls_layout = QHBoxLayout()
        self.btn_select_all = QPushButton()
        self.btn_select_all.setMinimumHeight(35)
        self.btn_select_all.clicked.connect(self.select_all)
        
        self.btn_deselect_all = QPushButton()
        self.btn_deselect_all.setMinimumHeight(35)
        self.btn_deselect_all.clicked.connect(self.deselect_all)
        
        table_controls_layout.addWidget(self.btn_select_all)
        table_controls_layout.addWidget(self.btn_deselect_all)
        table_controls_layout.addStretch()
        
        left_layout.addLayout(table_controls_layout)
        
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
        self.log_text.setMinimumHeight(150)
        right_layout.addWidget(self.log_text)
        
        # Apply initial translation
        self.update_texts()
        self.log(self.t("ready"))
        
    def reset_plot(self):
        fig = go.Figure()
        fig.update_layout(
            title=self.t("plot_title"),
            xaxis_title=self.t("xaxis"),
            yaxis_title=self.t("yaxis"),
            margin=dict(l=20, r=20, t=40, b=20),
            template="plotly_white"
        )
        self.web_view.setHtml(fig.to_html(include_plotlyjs='cdn'))
        
    def update_texts(self):
        self.setWindowTitle(self.t("title"))
        self.lbl_gokcismi.setText(self.t("search_label"))
        self.search_input.setPlaceholderText(self.t("search_placeholder"))
        self.search_btn.setText(self.t("search_btn"))
        
        self.lbl_eph_t0.setText(self.t("eph_t0"))
        self.lbl_eph_p.setText(self.t("eph_p"))
        self.btn_find_eph.setText(self.t("eph_find"))
        self.chk_phase.setText(self.t("plot_phase"))
        
        self.table.setHorizontalHeaderLabels(self.t("table_headers"))
        
        self.settings_group.setTitle(self.t("settings_title"))
        self.lbl_fmt.setText(self.t("format"))
        
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
        
    def find_ephemeris(self):
        target = self.search_input.text().strip()
        if not target:
            return
        self.btn_find_eph.setEnabled(False)
        self.eph_thread = EphemerisThread(target, self)
        self.eph_thread.log_signal.connect(self.log)
        self.eph_thread.result_signal.connect(self.fill_ephemeris)
        self.eph_thread.finished.connect(lambda: self.btn_find_eph.setEnabled(True))
        self.eph_thread.start()
        
    def fill_ephemeris(self, t0, p):
        self.input_t0.setText(t0)
        self.input_p.setText(p)
        self.chk_phase.setChecked(True)
        
    def populate_table(self, results):
        self.global_search_result = []
        total_rows = sum([len(r[1]) for r in results])
        self.table.setRowCount(total_rows)
        
        row_idx = 0
        for h_adi, res_obj in results:
            for i in range(len(res_obj)):
                self.global_search_result.append((h_adi, res_obj, i))
                
                row_data = res_obj.table[i]
                
                chkBoxItem = QTableWidgetItem()
                chkBoxItem.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                chkBoxItem.setCheckState(Qt.Unchecked)
                self.table.setItem(row_idx, 0, chkBoxItem)
                
                misyon = str(row_data['mission']) if 'mission' in row_data.colnames else "-"
                yazar = str(row_data['author']) if 'author' in row_data.colnames else "-"
                exptime = str(row_data['exptime']) if 'exptime' in row_data.colnames else "-"
                
                self.table.setItem(row_idx, 1, QTableWidgetItem(str(row_idx)))
                self.table.setItem(row_idx, 2, QTableWidgetItem(h_adi))
                self.table.setItem(row_idx, 3, QTableWidgetItem(misyon))
                self.table.setItem(row_idx, 4, QTableWidgetItem(yazar))
                self.table.setItem(row_idx, 5, QTableWidgetItem(exptime))
                row_idx += 1
            
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
            
        is_phase = self.chk_phase.isChecked()
        t0 = self.input_t0.text().strip()
        p = self.input_p.text().strip()
            
        self.btn_plot.setEnabled(False)
        self.plot_thread = PlotThread(selected, is_phase, t0, p, self)
        self.plot_thread.log_signal.connect(self.log)
        self.plot_thread.plot_data_signal.connect(self.update_plot)
        self.plot_thread.finished_signal.connect(lambda: self.btn_plot.setEnabled(True))
        self.plot_thread.start()
        
    def update_plot(self, plot_items):
        fig = go.Figure()
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        has_data = False
        
        for idx, (h_adi, misyon, time_val, flux_val, i) in enumerate(plot_items):
            color = colors[idx % len(colors)]
            fig.add_trace(go.Scattergl(
                x=time_val, y=flux_val, mode='markers',
                marker=dict(size=3, color=color, opacity=0.8),
                name=f"[{i}] {h_adi} ({misyon})"
            ))
            has_data = True
            
        if has_data:
            xaxis_title = self.t("plot_phase_axis") if self.chk_phase.isChecked() else self.t("xaxis")
            fig.update_layout(
                title=self.t("plot_title"),
                xaxis_title=xaxis_title,
                yaxis_title=self.t("yaxis"),
                margin=dict(l=20, r=20, t=40, b=20),
                template="plotly_white",
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
            )
            self.web_view.setHtml(fig.to_html(include_plotlyjs='cdn'))
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
    app.setApplicationName("TESS Lightcurve Studio")
    app.setApplicationDisplayName("TESS Lightcurve Studio")
    app.setDesktopFileName("tess-manager.desktop")
    ex = TESSApp()
    ex.show()
    sys.exit(app.exec_())

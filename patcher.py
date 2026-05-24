import re

with open('TESS_Araci.py', 'r') as f:
    content = f.read()

# 1. Update EphemerisThread
eph_old = """        # 1. Try Exoplanet Archive
        try:
            res = NasaExoplanetArchive.query_object(self.target)
            if len(res) > 0:
                p = str(res["pl_orbper"][0])
                t0 = str(res["pl_tranmid"][0])
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
                    if not pd.isna(p_val) and not pd.isna(t0_val):
                        p = str(p_val)
                        t0 = str(t0_val)
            except Exception:
                pass"""

eph_new = """        # 1. Try Exoplanet Archive
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
                pass"""

content = content.replace(eph_old, eph_new)

# 2. Update SearchThread
search_old = """            for h in targets:
                res = lk.search_lightcurve(h)
                if len(res) > 0:
                    for idx in range(len(res)):
                        results.append((h, res[idx]))
            
            if len(results) == 0:
                self.log_signal.emit(self.app_ref.t("not_found"))
            else:
                self.log_signal.emit(self.app_ref.t("found").format(len(results)))"""

search_new = """            for h in targets:
                res = lk.search_lightcurve(h)
                if len(res) > 0:
                    results.append((h, res))
            
            if len(results) == 0:
                self.log_signal.emit(self.app_ref.t("not_found"))
            else:
                total_rows = sum([len(r[1]) for r in results])
                self.log_signal.emit(self.app_ref.t("found").format(total_rows))"""

content = content.replace(search_old, search_new)

# 3. Update DownloadThread
dl_old = """    def run(self):
        self.log_signal.emit(self.app_ref.t("dl_start").format(len(self.data), self.fmt))
        for h_adi, target, idx in self.data:"""

dl_new = """    def run(self):
        self.log_signal.emit(self.app_ref.t("dl_start").format(len(self.data), self.fmt))
        for h_adi, res_obj, idx in self.data:
            target = res_obj[idx]"""

content = content.replace(dl_old, dl_new)

# 4. Update PlotThread
plot_old = """    def run(self):
        self.log_signal.emit(self.app_ref.t("plot_start").format(len(self.data)))
        plot_items = []
        for h_adi, target, idx in self.data:
            try:
                lc = target.download()
                if lc is not None:
                    lc_temiz = lc.normalize().remove_nans().remove_outliers()
                    
                    if self.is_phase and self.t0 and self.p:
                        try:
                            # Lightkurve native fold function
                            lc_temiz = lc_temiz.fold(period=float(self.p), epoch_time=float(self.t0))
                        except Exception as e:
                            self.log_signal.emit("Phase Fold error: " + str(e))"""

plot_new = """    def run(self):
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
                            self.log_signal.emit("Phase Fold error: " + str(e))"""

content = content.replace(plot_old, plot_new)

# 5. Update populate_table
pop_old = """    def populate_table(self, results):
        self.global_search_result = results
        self.table.setRowCount(len(results))
        for i, (h_adi, target) in enumerate(results):
            chkBoxItem = QTableWidgetItem()
            chkBoxItem.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            chkBoxItem.setCheckState(Qt.Unchecked)
            self.table.setItem(i, 0, chkBoxItem)
            
            misyon = str(target.mission[0]) if hasattr(target, 'mission') else "-"
            yazar = str(target.author[0]) if hasattr(target, 'author') else "-"
            exptime = str(target.exptime[0]) if hasattr(target, 'exptime') else "-"
            
            self.table.setItem(i, 1, QTableWidgetItem(str(i)))
            self.table.setItem(i, 2, QTableWidgetItem(h_adi))
            self.table.setItem(i, 3, QTableWidgetItem(misyon))
            self.table.setItem(i, 4, QTableWidgetItem(yazar))
            self.table.setItem(i, 5, QTableWidgetItem(exptime))"""

pop_new = """    def populate_table(self, results):
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
                row_idx += 1"""

content = content.replace(pop_old, pop_new)

# Add BJD note to translations
t_old = """"eph_t0": "Epok (T0):","""
t_new = """"eph_t0": "Epok T0 (BJD):","""
content = content.replace(t_old, t_new)

t_old_en = """"eph_t0": "Epoch (T0):","""
t_new_en = """"eph_t0": "Epoch T0 (BJD):","""
content = content.replace(t_old_en, t_new_en)

with open('TESS_Araci.py', 'w') as f:
    f.write(content)

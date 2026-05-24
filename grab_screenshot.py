import sys
import time
from PyQt5.QtWidgets import QApplication, QTableWidgetItem
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from TESS_Araci import TESSApp
import numpy as np

def take_shot():
    # Mock data for table
    ex.table.setRowCount(3)
    data = [
        ("TT And", "TESS Sector 1", "SPOC", "120"),
        ("TT And", "TESS Sector 2", "TESS-SPOC", "120"),
        ("TT And", "TESS Sector 3", "QLP", "1800")
    ]
    for i, (name, mission, author, exp) in enumerate(data):
        chk = QTableWidgetItem()
        chk.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        chk.setCheckState(Qt.Checked if i < 2 else Qt.Unchecked)
        ex.table.setItem(i, 0, chk)
        ex.table.setItem(i, 1, QTableWidgetItem(str(i)))
        ex.table.setItem(i, 2, QTableWidgetItem(name))
        ex.table.setItem(i, 3, QTableWidgetItem(mission))
        ex.table.setItem(i, 4, QTableWidgetItem(author))
        ex.table.setItem(i, 5, QTableWidgetItem(exp))
    
    # Mock plot
    t = np.linspace(100, 120, 500)
    f1 = 1.0 + 0.01 * np.sin(2 * np.pi * t / 2.0) + np.random.normal(0, 0.002, len(t))
    f2 = 1.0 + 0.01 * np.sin(2 * np.pi * t / 2.0 + 0.5) + np.random.normal(0, 0.002, len(t))
    
    ex.ax.clear()
    ex.ax.scatter(t, f1, s=2, color='#1f77b4', label="[0] TT And (TESS Sector 1)", alpha=0.8)
    ex.ax.scatter(t, f2, s=2, color='#ff7f0e', label="[1] TT And (TESS Sector 2)", alpha=0.8)
    ex.ax.set_xlabel("Zaman (BTJD)")
    ex.ax.set_ylabel("Normalize Akı")
    ex.ax.legend(loc='upper right', fontsize='small')
    ex.ax.set_title("Birleştirilmiş Işık Eğrileri")
    ex.fig.tight_layout()
    ex.canvas.draw()
    
    ex.log("✅ Çizim tamamlandı.")
    
    # Process events to render
    QApplication.processEvents()
    
    # Grab screenshot
    pixmap = ex.grab()
    pixmap.save("screenshot.png", "PNG")
    print("Screenshot saved to screenshot.png")
    app.quit()

app = QApplication(sys.argv)
app.setStyle('Fusion')
ex = TESSApp()
ex.show()

QTimer.singleShot(1000, take_shot)
sys.exit(app.exec_())

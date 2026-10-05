import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QListWidget, QListWidgetItem, QLabel,
                             QFileDialog, QComboBox, QMessageBox, QFrame,
                             QLineEdit, QSlider, QGridLayout, QGroupBox)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import (QPixmap, QIcon, QColor, QLinearGradient, QBrush,
                         QPainter, QPen)
import vlc
from mutagen.mp3 import MP3

SAVE_FILE = os.path.join(os.path.expanduser("~"), "Documents", "mp3_player_save.json")
EQ_FILE = os.path.join(os.path.expanduser("~"), "Documents", "mp3_player_eq.json")
ICONS_DIR = os.path.join(os.path.expanduser("~"), "Documents", "player_icons")


def icon_path(name):
    png = os.path.join(ICONS_DIR, name + ".png")
    if os.path.exists(png):
        return png
    ico = os.path.join(ICONS_DIR, name + ".ico")
    if os.path.exists(ico):
        return ico
    return png


# --- Частоты эквалайзера VLC ---
EQ_FREQS = ["60", "170", "310", "600", "1000", "3000", "6000", "12000", "14000", "16000"]
EQ_PRESETS = {
    "Flat":       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    "Rock":       [5, 4, 3, 1, -1, -2, 0, 2, 3, 4],
    "Pop":        [-1, 2, 4, 4, 2, 0, -1, -1, -1, -1],
    "Jazz":       [3, 2, 1, 2, -1, -1, 0, 1, 2, 3],
    "Classical":  [4, 3, 2, 1, -1, -1, 0, 2, 3, 4],
    "Bass Boost": [8, 7, 6, 4, 2, 0, 0, 0, 0, 0],
    "Vocal":      [-2, -1, 0, 2, 4, 4, 3, 1, 0, -1],
    "Electronic": [4, 3, 1, 0, -1, 1, 0, 1, 3, 5],
    "Custom":     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
}


AERO_QSS = """
QWidget {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #d6ecff, stop:0.5 #a8d4f5, stop:1 #6a9fd4);
    font-family: "Segoe UI", "Calibri", Arial;
    font-size: 10pt;
    color: #002a55;
}
QLabel { background: transparent; color: #002a55; }

QListWidget {
    background: rgba(255,255,255,180);
    border: 1px solid rgba(120,170,220,200);
    border-radius: 10px;
    padding: 5px;
    color: #002a55;
}
QListWidget::item { padding: 4px; border-radius: 6px; }
QListWidget::item:selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(180,220,255,240),
                                stop:1 rgba(120,180,230,240));
    color: #001a33;
}
QListWidget::item:hover { background: rgba(210,235,255,180); }

QComboBox {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(255,255,255,230),
                                stop:1 rgba(200,230,255,230));
    border: 1px solid rgba(70,130,180,200);
    border-radius: 10px;
    padding: 5px 10px;
    color: #002a55;
}
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView {
    background: rgba(240,250,255,240);
    border: 1px solid rgba(70,130,180,200);
    selection-background-color: rgba(150,200,240,220);
    color: #002a55;
}

QLineEdit {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(255,255,255,230),
                                stop:1 rgba(220,240,255,230));
    border: 1px solid rgba(70,130,180,200);
    border-radius: 10px;
    padding: 5px 12px;
    color: #002a55;
    font-size: 10pt;
}
QLineEdit:focus {
    border: 1px solid rgba(100,160,220,255);
    background: rgba(255,255,255,240);
}

QSlider::groove:vertical {
    background: rgba(200,225,250,200);
    width: 8px;
    border-radius: 4px;
}
QSlider::handle:vertical {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 rgba(255,255,255,240),
                                stop:0.5 rgba(200,230,255,240),
                                stop:1 rgba(120,180,230,240));
    border: 1px solid rgba(70,130,180,220);
    height: 14px;
    width: 18px;
    margin: 0 -6px;
    border-radius: 6px;
}

QGroupBox {
    background: rgba(255,255,255,100);
    border: 1px solid rgba(120,170,220,180);
    border-radius: 10px;
    margin-top: 8px;
    padding-top: 12px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: #003a70;
}
"""


class IconButton(QPushButton):
    def __init__(self, icon_file, tooltip="", parent=None):
        super().__init__(parent)
        self.setMinimumHeight(46)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(tooltip)
        self.setIconSize(QSize(32, 32))
        self.set_icon(icon_file)

        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 rgba(255,255,255,220),
                                            stop:0.45 rgba(220,240,255,230),
                                            stop:0.5 rgba(180,220,255,230),
                                            stop:1 rgba(120,180,230,240));
                border: 1px solid rgba(70,130,180,200);
                border-radius: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 rgba(255,255,255,255),
                                            stop:0.45 rgba(235,245,255,255),
                                            stop:0.5 rgba(200,230,255,255),
                                            stop:1 rgba(150,200,240,255));
                border: 1px solid rgba(100,160,220,255);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 rgba(150,200,240,255),
                                            stop:0.5 rgba(200,230,255,255),
                                            stop:1 rgba(255,255,255,255));
            }
        """)

    def set_icon(self, name):
        path = icon_path(name)
        if os.path.exists(path):
            self.setIcon(QIcon(path))


class MP3Player(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aero MP3 Player")
        self.setGeometry(150, 60, 560, 980)
        self.setStyleSheet(AERO_QSS)

        # --- VLC ---
        self.instance = vlc.Instance("--no-video")
        self.player = self.instance.media_player_new()
        self.equalizer = vlc.AudioEqualizer()

        self.playlist = []
        self.liked = set()
        self.artists_cache = {}
        self.current = 0
        self.is_paused = False
        self.is_playing = False
        self.show_only_liked = False
        self.artist_filter = None
        self.visible_indices = []
        self.eq_sliders = []
        self.eq_enabled = False

        # --- Обложка ---
        self.cover_label = QLabel()
        self.cover_label.setAlignment(Qt.AlignCenter)
        self.cover_label.setFixedHeight(220)
        self.cover_label.setText("Нет обложки")
        self.cover_label.setStyleSheet(
            "color: #5a7a9a; font-size: 12pt; "
            "background: rgba(255,255,255,120); "
            "border-radius: 14px; border: 1px solid rgba(120,170,220,150);"
        )

        self.track_label = QLabel("Трек не выбран")
        self.track_label.setAlignment(Qt.AlignCenter)
        self.track_label.setStyleSheet(
            "font-size: 13pt; font-weight: bold; color: #002a55; background: transparent;"
        )
        self.artist_label = QLabel("")
        self.artist_label.setAlignment(Qt.AlignCenter)
        self.artist_label.setStyleSheet(
            "font-size: 10pt; color: #336699; background: transparent;"
        )

        # --- Лайк ---
        self.like_btn = IconButton("heart", "Лайк")
        self.like_btn.clicked.connect(self.toggle_like)

        # --- Поиск ---
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск...")
        self.search_input.setMinimumHeight(34)
        self.search_input.textChanged.connect(self.on_search_change)

        self.search_btn = IconButton("search", "Поиск")
        self.search_btn.setFixedSize(44, 38)
        self.search_btn.clicked.connect(lambda: self.search_input.setFocus())

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)

        # --- Фильтры ---
        filter_layout = QHBoxLayout()
        self.filter_btn = IconButton("star", "Избранное")
        self.filter_btn.clicked.connect(self.toggle_filter)

        self.artist_combo = QComboBox()
        self.artist_combo.addItem("Все исполнители")
        self.artist_combo.currentTextChanged.connect(self.on_artist_change)
        self.artist_combo.setMinimumHeight(34)

        filter_layout.addWidget(self.filter_btn)
        filter_layout.addWidget(self.artist_combo)

        # --- Эквалайзер ---
        eq_group = QGroupBox("Эквалайзер")
        eq_layout = QVBoxLayout()

        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Пресет:"))
        self.eq_preset_combo = QComboBox()
        for name in EQ_PRESETS.keys():
            self.eq_preset_combo.addItem(name)
        self.eq_preset_combo.currentTextChanged.connect(self.on_preset_change)
        preset_layout.addWidget(self.eq_preset_combo)

        self.eq_toggle_btn = QPushButton("Вкл")
        self.eq_toggle_btn.setCheckable(True)
        self.eq_toggle_btn.setFixedWidth(60)
        self.eq_toggle_btn.clicked.connect(self.toggle_eq)
        preset_layout.addWidget(self.eq_toggle_btn)
        eq_layout.addLayout(preset_layout)

        sliders_layout = QHBoxLayout()
        sliders_layout.setSpacing(2)
        for i, freq in enumerate(EQ_FREQS):
            col = QVBoxLayout()
            lbl_top = QLabel("+20")
            lbl_top.setAlignment(Qt.AlignCenter)
            lbl_top.setStyleSheet("font-size: 7pt; color: #5a7a9a;")
            col.addWidget(lbl_top)

            s = QSlider(Qt.Vertical)
            s.setRange(-20, 20)
            s.setValue(0)
            s.setFixedHeight(120)
            s.valueChanged.connect(self.on_eq_change)
            col.addWidget(s, alignment=Qt.AlignHCenter)
            self.eq_sliders.append(s)

            lbl_bot = QLabel(freq)
            lbl_bot.setAlignment(Qt.AlignCenter)
            lbl_bot.setStyleSheet("font-size: 7pt; color: #003a70;")
            col.addWidget(lbl_bot)

            sliders_layout.addLayout(col)
        eq_layout.addLayout(sliders_layout)
        eq_group.setLayout(eq_layout)

        # --- Плейлист ---
        self.listbox = QListWidget()
        self.listbox.itemDoubleClicked.connect(self.on_select)
        self.listbox.setMinimumHeight(160)

        # --- Кнопки управления ---
        btn_layout = QHBoxLayout()
        self.folder_btn = IconButton("folder", "Загрузить")
        self.prev_btn = IconButton("prev", "Предыдущий")
        self.play_btn = IconButton("play", "Играть / Пауза")
        self.next_btn = IconButton("next", "Следующий")
        self.stop_btn = IconButton("stop", "Стоп")

        self.folder_btn.clicked.connect(self.load_files)
        self.prev_btn.clicked.connect(self.prev_track)
        self.play_btn.clicked.connect(self.toggle_play)
        self.next_btn.clicked.connect(self.next_track)
        self.stop_btn.clicked.connect(self.stop)

        for b in (self.folder_btn, self.prev_btn, self.play_btn,
                  self.next_btn, self.stop_btn):
            b.setFixedHeight(46)
            btn_layout.addWidget(b)

        # --- Статус ---
        self.status_label = QLabel("Готов")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(
            "color: #5a7a9a; font-size: 9pt; background: transparent;"
        )

        # --- Сборка ---
        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.addWidget(self.cover_label)
        layout.addWidget(self.track_label)
        layout.addWidget(self.artist_label)
        layout.addWidget(self.like_btn)
        layout.addLayout(search_layout)
        layout.addLayout(filter_layout)
        layout.addWidget(eq_group)
        layout.addWidget(self.listbox)
        layout.addLayout(btn_layout)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

        # --- Таймер обновления ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_end)
        self.timer.start(1000)

        self.load_state()
        self.load_eq()

    # --- Эквалайзер ---
    def apply_eq(self):
        """Применяет текущие значения эквалайзера"""
        values = [s.value() for s in self.eq_sliders]
        try:
            for i, v in enumerate(values):
                # ВАЖНО: set_amp_at_index(amp: float, index: int)
                self.equalizer.set_amp_at_index(float(v), int(i))
            if self.eq_enabled:
                self.player.set_equalizer(self.equalizer)
        except Exception as e:
            print("EQ ошибка:", e)

    def on_eq_change(self):
        self.apply_eq()
        self.save_eq()

    def on_preset_change(self, name):
        values = EQ_PRESETS.get(name, [0]*10)
        for s, v in zip(self.eq_sliders, values):
            s.blockSignals(True)
            s.setValue(v)
            s.blockSignals(False)
        self.apply_eq()
        self.save_eq()

    def toggle_eq(self):
        self.eq_enabled = self.eq_toggle_btn.isChecked()
        self.eq_toggle_btn.setText("Вкл" if self.eq_enabled else "Выкл")
        if self.eq_enabled:
            self.apply_eq()
        else:
            try:
                self.player.set_equalizer(None)
            except Exception:
                pass
        self.save_eq()

    def save_eq(self):
        data = {
            "values": [s.value() for s in self.eq_sliders],
            "preset": self.eq_preset_combo.currentText(),
            "enabled": self.eq_enabled,
        }
        try:
            with open(EQ_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print("EQ сохранение:", e)

    def load_eq(self):
        if not os.path.exists(EQ_FILE):
            return
        try:
            with open(EQ_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            values = data.get("values", [0]*10)
            for s, v in zip(self.eq_sliders, values):
                s.blockSignals(True)
                s.setValue(v)
                s.blockSignals(False)
            preset = data.get("preset", "Flat")
            idx = self.eq_preset_combo.findText(preset)
            if idx >= 0:
                self.eq_preset_combo.blockSignals(True)
                self.eq_preset_combo.setCurrentIndex(idx)
                self.eq_preset_combo.blockSignals(False)
            enabled = data.get("enabled", False)
            self.eq_toggle_btn.setChecked(enabled)
            self.eq_enabled = enabled
            self.eq_toggle_btn.setText("Вкл" if enabled else "Выкл")
            self.apply_eq()
        except Exception as e:
            print("EQ загрузка:", e)

    # --- Теги ---
    def read_artist(self, path):
        if path in self.artists_cache:
            return self.artists_cache[path]
        try:
            audio = MP3(path)
            if audio.tags and "TPE1" in audio.tags:
                artist = str(audio.tags["TPE1"]).strip()
                self.artists_cache[path] = artist
                return artist
        except Exception:
            pass
        self.artists_cache[path] = ""
        return ""

    def get_all_artists(self):
        artists = set()
        for path in self.playlist:
            a = self.read_artist(path)
            if a:
                artists.add(a)
        return sorted(artists)

    # --- Сохранение ---
    def save_state(self):
        data = {"playlist": self.playlist, "current": self.current, "liked": list(self.liked)}
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Сохранение:", e)

    def load_state(self):
        if not os.path.exists(SAVE_FILE):
            return
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for path in data.get("playlist", []):
                if os.path.exists(path):
                    self.playlist.append(path)
            for path in data.get("liked", []):
                self.liked.add(path)
            self.current = data.get("current", 0)
            self.refresh_list()
            self.update_artist_combo()
            if self.playlist:
                self.status_label.setText(f"Восстановлено: {len(self.playlist)} трек(ов)")
        except Exception as e:
            print("Загрузка:", e)

    # --- Список ---
    def refresh_list(self):
        self.listbox.clear()
        self.visible_indices.clear()
        search = self.search_input.text().strip().lower()
        for i, path in enumerate(self.playlist):
            if self.show_only_liked and path not in self.liked:
                continue
            if self.artist_filter:
                a = self.read_artist(path)
                if a != self.artist_filter:
                    continue
            if search:
                name = os.path.basename(path).lower()
                artist = self.read_artist(path).lower()
                title = ""
                try:
                    audio = MP3(path)
                    if audio.tags and "TIT2" in audio.tags:
                        title = str(audio.tags["TIT2"]).lower()
                except Exception:
                    pass
                if search not in name and search not in artist and search not in title:
                    continue
            display = os.path.basename(path)
            if path in self.liked:
                display = "❤ " + display
            self.listbox.addItem(display)
            self.visible_indices.append(i)

    def update_artist_combo(self):
        current_text = self.artist_combo.currentText()
        self.artist_combo.blockSignals(True)
        self.artist_combo.clear()
        self.artist_combo.addItem("Все исполнители")
        for a in self.get_all_artists():
            self.artist_combo.addItem(a)
        idx = self.artist_combo.findText(current_text)
        if idx >= 0:
            self.artist_combo.setCurrentIndex(idx)
        self.artist_combo.blockSignals(False)

    def on_artist_change(self, value):
        if value == "Все исполнители":
            self.artist_filter = None
        else:
            self.artist_filter = value
        self.refresh_list()

    def on_search_change(self, text):
        self.refresh_list()

    # --- Лайк ---
    def toggle_like(self):
        if not self.playlist:
            return
        path = self.playlist[self.current]
        if path in self.liked:
            self.liked.discard(path)
        else:
            self.liked.add(path)
        self.refresh_list()
        self.save_state()

    def toggle_filter(self):
        self.show_only_liked = not self.show_only_liked
        self.refresh_list()

    # --- Загрузка ---
    def load_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Выбери MP3", "", "MP3 (*.mp3)")
        if not files:
            return
        for f in files:
            self.playlist.append(f)
            self.read_artist(f)
        self.refresh_list()
        self.update_artist_combo()
        self.status_label.setText(f"Загружено: {len(files)}")
        self.save_state()

    # --- Воспроизведение ---
    def play_current(self):
        if not self.playlist:
            return
        path = self.playlist[self.current]
        media = self.instance.media_new(path)
        self.player.set_media(media)
        self.player.play()
        self.is_playing = True
        self.is_paused = False
        self.status_label.setText("Играет")
        self.play_btn.set_icon("pause")

        if self.eq_enabled:
            self.apply_eq()

        title = os.path.basename(path)
        artist = self.read_artist(path)
        try:
            audio = MP3(path)
            if audio.tags and "TIT2" in audio.tags:
                title = str(audio.tags["TIT2"])
        except Exception as e:
            print("Теги:", e)

        self.track_label.setText("▶ " + title)
        self.artist_label.setText(artist)

        try:
            audio = MP3(path)
            if audio.tags:
                for key in audio.tags.keys():
                    if key.startswith("APIC"):
                        apic = audio.tags[key]
                        pix = QPixmap()
                        pix.loadFromData(apic.data)
                        pix = pix.scaled(220, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.cover_label.setPixmap(pix)
                        self.cover_label.setText("")
                        break
                else:
                    self.cover_label.setPixmap(QPixmap())
                    self.cover_label.setText("Нет обложки")
        except Exception as e:
            print("Обложка:", e)
            self.cover_label.setPixmap(QPixmap())
            self.cover_label.setText("Нет обложки")

        self.save_state()

    def on_select(self, item):
        row = self.listbox.row(item)
        if 0 <= row < len(self.visible_indices):
            self.current = self.visible_indices[row]
            self.play_current()

    def toggle_play(self):
        if not self.is_playing:
            self.play_current()
            return
        if self.is_paused:
            self.player.play()
            self.is_paused = False
            self.status_label.setText("Играет")
            self.play_btn.set_icon("pause")
        else:
            self.player.pause()
            self.is_paused = True
            self.status_label.setText("Пауза")
            self.play_btn.set_icon("play")

    def next_track(self):
        if not self.playlist:
            return
        self.current = (self.current + 1) % len(self.playlist)
        self.play_current()

    def prev_track(self):
        if not self.playlist:
            return
        self.current = (self.current - 1) % len(self.playlist)
        self.play_current()

    def stop(self):
        self.player.stop()
        self.is_playing = False
        self.is_paused = False
        self.status_label.setText("Остановлено")
        self.play_btn.set_icon("play")

    def check_end(self):
        if self.is_playing and not self.is_paused:
            state = self.player.get_state()
            if state == vlc.State.Ended:
                self.next_track()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = MP3Player()
    player.show()
    sys.exit(app.exec_())

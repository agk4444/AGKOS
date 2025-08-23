#!/usr/bin/env python3
"""
AGK Browser Full - PyQt5 / QtWebEngine implementation
Features:
 - Tabs (new/close)
 - Address bar, back/forward/reload/stop
 - Persistent bookmarks (bookmarks.json)
 - Persistent downloads with progress (downloads.json)
 - Session restore (session.json)
 - Download manager with save dialog and progress updates
"""

import sys, os, json, uuid
from PyQt5 import QtCore, QtWidgets, QtGui, QtWebEngineWidgets

APP_NAME = "AGKBrowserFull"
HOME_PAGE = "https://example.com"
BOOKMARKS_FILE = "bookmarks.json"
DOWNLOADS_FILE = "downloads.json"
SESSION_FILE = "session.json"


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


class DownloadsDialog(QtWidgets.QDialog):
    def __init__(self, downloads, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Downloads")
        self.resize(600, 300)
        self.downloads = downloads
        self.listw = QtWidgets.QListWidget()
        btn_close = QtWidgets.QPushButton("Close")
        btn_clear = QtWidgets.QPushButton("Clear Completed")

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.listw)
        h = QtWidgets.QHBoxLayout()
        h.addWidget(btn_clear)
        h.addStretch(1)
        h.addWidget(btn_close)
        layout.addLayout(h)

        btn_close.clicked.connect(self.accept)
        btn_clear.clicked.connect(self.clear_completed)
        self.refresh()

    def refresh(self):
        self.listw.clear()
        for d in self.downloads:
            total = d.get("total", 0) or 0
            received = d.get("bytes", 0) or 0
            status = d.get("status", "unknown")
            path = d.get("path", "")
            self.listw.addItem(f"{os.path.basename(path)} — {status} ({received}/{total})")

    def clear_completed(self):
        self.downloads[:] = [d for d in self.downloads if d.get("status") != "completed"]
        save_json(DOWNLOADS_FILE, self.downloads)
        self.refresh()


class BookmarksDialog(QtWidgets.QDialog):
    def __init__(self, bookmarks, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bookmarks")
        self.resize(600, 400)
        self.bookmarks = bookmarks
        self.listw = QtWidgets.QListWidget()
        btn_open = QtWidgets.QPushButton("Open")
        btn_delete = QtWidgets.QPushButton("Delete")
        btn_add = QtWidgets.QPushButton("Add Current")
        btn_close = QtWidgets.QPushButton("Close")

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.listw)
        h = QtWidgets.QHBoxLayout()
        h.addWidget(btn_add)
        h.addStretch(1)
        h.addWidget(btn_open)
        h.addWidget(btn_delete)
        h.addWidget(btn_close)
        layout.addLayout(h)

        btn_open.clicked.connect(self.open_selected)
        btn_delete.clicked.connect(self.delete_selected)
        btn_add.clicked.connect(self.add_current)
        btn_close.clicked.connect(self.accept)

        self.refresh()

    def refresh(self):
        self.listw.clear()
        for b in self.bookmarks:
            title = b.get("title") or b.get("url")
            self.listw.addItem(f"{title} — {b.get('url')}")

    def open_selected(self):
        row = self.listw.currentRow()
        if row >= 0:
            self.selected_url = self.bookmarks[row]["url"]
            self.accept()

    def delete_selected(self):
        row = self.listw.currentRow()
        if row >= 0:
            del self.bookmarks[row]
            save_json(BOOKMARKS_FILE, self.bookmarks)
            self.refresh()

    def add_current(self):
        # parent window should set self.current_url before opening dialog
        url = getattr(self, "current_url", None)
        if not url:
            QtWidgets.QMessageBox.information(self, "Add Bookmark", "No current URL available.")
            return
        title, ok = QtWidgets.QInputDialog.getText(self, "Bookmark Title", "Title:", text=url)
        if ok:
            self.bookmarks.append({"title": title or url, "url": url})
            save_json(BOOKMARKS_FILE, self.bookmarks)
            self.refresh()


class BrowserTabWidget(QtWebEngineWidgets.QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.download_item = None


class BrowserWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1200, 800)

        # persistent storage
        self.bookmarks = load_json(BOOKMARKS_FILE, [])
        self.downloads = load_json(DOWNLOADS_FILE, [])
        self.session = load_json(SESSION_FILE, [])

        # UI
        self.address = QtWidgets.QLineEdit()
        btn_go = QtWidgets.QToolButton(text="Go")
        btn_back = QtWidgets.QToolButton(text="◀")
        btn_forward = QtWidgets.QToolButton(text="▶")
        btn_reload = QtWidgets.QToolButton(text="⟳")
        btn_stop = QtWidgets.QToolButton(text="✖")
        btn_new = QtWidgets.QToolButton(text="＋")
        btn_close = QtWidgets.QToolButton(text="－")
        btn_bookmark = QtWidgets.QToolButton(text="★")
        btn_downloads = QtWidgets.QToolButton(text="▼")

        toolbar = QtWidgets.QHBoxLayout()
        toolbar.addWidget(btn_back)
        toolbar.addWidget(btn_forward)
        toolbar.addWidget(btn_reload)
        toolbar.addWidget(btn_stop)
        toolbar.addWidget(btn_new)
        toolbar.addWidget(btn_close)
        toolbar.addWidget(btn_bookmark)
        toolbar.addWidget(btn_downloads)
        toolbar.addWidget(self.address)
        toolbar.addWidget(btn_go)

        top_widget = QtWidgets.QWidget()
        top_widget.setLayout(toolbar)

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setDocumentMode(True)
        self.setCentralWidget(QtWidgets.QWidget())
        layout = QtWidgets.QVBoxLayout(self.centralWidget())
        layout.addWidget(top_widget)
        layout.addWidget(self.tabs)

        # Status
        self.status = self.statusBar()

        # Signals
        btn_go.clicked.connect(self.on_go)
        self.address.returnPressed.connect(self.on_go)
        btn_back.clicked.connect(self.on_back)
        btn_forward.clicked.connect(self.on_forward)
        btn_reload.clicked.connect(self.on_reload)
        btn_stop.clicked.connect(self.on_stop)
        btn_new.clicked.connect(self.on_new_tab)
        btn_close.clicked.connect(self.on_close_current_tab)
        btn_bookmark.clicked.connect(self.on_add_bookmark)
        btn_downloads.clicked.connect(self.on_show_downloads)

        self.tabs.tabCloseRequested.connect(self.on_tab_close_requested)
        self.tabs.currentChanged.connect(self.on_current_changed)
        self.tabs.setTabsClosable(True)

        # menus
        mbar = self.menuBar()
        file_menu = mbar.addMenu("&File")
        bm_menu = mbar.addMenu("&Bookmarks")
        dl_menu = mbar.addMenu("&Downloads")
        prefs_menu = mbar.addMenu("&Settings")

        act_manage_bm = QtWidgets.QAction("Manage Bookmarks", self)
        act_show_dl = QtWidgets.QAction("Show Downloads", self)
        act_prefs = QtWidgets.QAction("Preferences", self)
        file_menu.addAction("New Tab").triggered.connect(lambda: self.on_new_tab())
        file_menu.addAction("Exit").triggered.connect(self.close)
        bm_menu.addAction(act_manage_bm)
        dl_menu.addAction(act_show_dl)
        prefs_menu.addAction(act_prefs)

        act_manage_bm.triggered.connect(self.on_manage_bookmarks)
        act_show_dl.triggered.connect(self.on_show_downloads)
        act_prefs.triggered.connect(self.on_preferences)

        # Add initial tabs from session or home
        if self.session:
            for url in self.session:
                self.add_tab(url)
        else:
            self.add_tab(HOME_PAGE)

        # Ensure we save session on exit
        app.aboutToQuit.connect(self.save_session)

    def current_webview(self):
        widget = self.tabs.currentWidget()
        if isinstance(widget, BrowserTabWidget):
            return widget
        return None

    def add_tab(self, url=HOME_PAGE):
        webview = BrowserTabWidget()
        profile = webview.page().profile()
        # connect download handling on the profile so we handle downloads
        profile.downloadRequested.connect(self.on_download_requested)

        webview.setUrl(QtCore.QUrl(url))
        idx = self.tabs.addTab(webview, "New Tab")
        self.tabs.setCurrentIndex(idx)

        webview.titleChanged.connect(lambda title, w=webview: self.on_title_changed(w, title))
        webview.urlChanged.connect(lambda qurl, w=webview: self.on_url_changed(w, qurl))
        webview.loadProgress.connect(lambda p, w=webview: self.on_load_progress(w, p))
        webview.loadFinished.connect(lambda ok, w=webview: self.on_load_finished(w, ok))

    def on_go(self):
        url = self.address.text().strip()
        if not url:
            return
        if "." in url and not url.startswith("http"):
            url = "https://" + url if not url.startswith("http") else url
        elif " " in url:
            url = "https://www.google.com/search?q=" + QtCore.QUrl.toPercentEncoding(url).data().decode()
        self.current_webview().setUrl(QtCore.QUrl(url))
        self.address.setText(url)

    def on_back(self):
        w = self.current_webview()
        if w: w.back()

    def on_forward(self):
        w = self.current_webview()
        if w: w.forward()

    def on_reload(self):
        w = self.current_webview()
        if w: w.reload()

    def on_stop(self):
        w = self.current_webview()
        if w: w.stop()

    def on_new_tab(self):
        self.add_tab(HOME_PAGE)

    def on_close_current_tab(self):
        idx = self.tabs.currentIndex()
        if idx >= 0:
            self.tabs.removeTab(idx)

    def on_tab_close_requested(self, index):
        self.tabs.removeTab(index)

    def on_current_changed(self, index):
        w = self.current_webview()
        if w:
            self.address.setText(w.url().toString())

    def on_title_changed(self, webview, title):
        idx = self.tabs.indexOf(webview)
        if idx >= 0:
            self.tabs.setTabText(idx, title)
            self.setWindowTitle(f"{title} — {APP_NAME}")

    def on_url_changed(self, webview, qurl):
        if webview is self.current_webview():
            self.address.setText(qurl.toString())

    def on_load_progress(self, webview, progress):
        self.status.showMessage(f"Loading {progress}%")

    def on_load_finished(self, webview, ok):
        if ok:
            self.status.showMessage("Done", 2000)
        else:
            self.status.showMessage("Load error", 5000)

    # Bookmarks
    def on_add_bookmark(self):
        w = self.current_webview()
        if not w: return
        url = w.url().toString()
        title = w.title() or url
        self.bookmarks.append({"title": title, "url": url})
        save_json(BOOKMARKS_FILE, self.bookmarks)
        QtWidgets.QMessageBox.information(self, "Bookmark Added", f"Added bookmark for {url}")

    def on_manage_bookmarks(self):
        dlg = BookmarksDialog(self.bookmarks, self)
        dlg.current_url = self.current_webview().url().toString() if self.current_webview() else None
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            # open selected
            url = getattr(dlg, "selected_url", None)
            if url:
                self.add_tab(url)

    # Preferences dialog (simple)
    def on_preferences(self):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Preferences")
        layout = QtWidgets.QFormLayout(dlg)
        inp_home = QtWidgets.QLineEdit(self)
        inp_home.setText(self.session[0] if self.session else HOME_PAGE)
        layout.addRow("Home Page:", inp_home)
        btn_save = QtWidgets.QPushButton("Save")
        btn_cancel = QtWidgets.QPushButton("Cancel")
        h = QtWidgets.QHBoxLayout()
        h.addWidget(btn_save); h.addWidget(btn_cancel)
        layout.addRow(h)
        btn_save.clicked.connect(lambda: self._save_prefs(inp_home.text(), dlg))
        btn_cancel.clicked.connect(dlg.reject)
        dlg.exec()

    def _save_prefs(self, home_url, dlg):
        if home_url:
            self.session = [home_url] + self.session[1:]
            save_json(SESSION_FILE, self.session)
        dlg.accept()

    # Downloads handling
    def on_download_requested(self, download_item):
        suggested = download_item.path() or download_item.downloadFileName() or "download.bin"
        options = QtWidgets.QFileDialog.Options()
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", suggested, options=options)
        if not path:
            download_item.cancel()
            return
        download_item.setPath(path)
        download_item.accept()

        # add to tracking
        rec = {"id": str(uuid.uuid4()), "url": download_item.url().toString(), "path": path, "bytes": 0, "total": download_item.totalBytes(), "status": "in-progress"}
        self.downloads.append(rec)
        save_json(DOWNLOADS_FILE, self.downloads)
        self.downloads_dialog_refresh()

        # connect signals on the QWebEngineDownloadItem object
        download_item.downloadProgress.connect(lambda recv, total, dl=download_item, rid=rec["id"]: self._on_dl_progress(dl, rid, recv, total))
        download_item.finished.connect(lambda dl=download_item, rid=rec["id"]: self._on_dl_finished(dl, rid))

    def _find_download_record(self, rid):
        for d in self.downloads:
            if d.get("id") == rid:
                return d
        return None

    def _on_dl_progress(self, download_item, rid, received, total):
        rec = self._find_download_record(rid)
        if rec is not None:
            rec["bytes"] = received
            rec["total"] = total
            save_json(DOWNLOADS_FILE, self.downloads)
            self.downloads_dialog_refresh()

    def _on_dl_finished(self, download_item, rid):
        rec = self._find_download_record(rid)
        if rec is not None:
            rec["bytes"] = download_item.receivedBytes()
            rec["total"] = download_item.totalBytes()
            rec["status"] = "completed" if download_item.state() == QtWebEngineWidgets.QWebEngineDownloadItem.DownloadCompleted else "failed"
            save_json(DOWNLOADS_FILE, self.downloads)
            self.downloads_dialog_refresh()
            self.status.showMessage(f\"Download {rec['status']}: {rec['path']}\", 5000)

    def downloads_dialog_refresh(self):
        # ensure dialog exists or create one-off
        dlg = DownloadsDialog(self.downloads, self)
        dlg.exec()

    def on_show_downloads(self):
        dlg = DownloadsDialog(self.downloads, self)
        dlg.exec()

    # Session management
    def save_session(self):
        urls = []
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if isinstance(w, QtWebEngineWidgets.QWebEngineView):
                urls.append(w.url().toString())
        save_json(SESSION_FILE, urls)

    def closeEvent(self, event):
        # persist session/bookmarks/downloads before quitting
        save_json(BOOKMARKS_FILE, self.bookmarks)
        save_json(DOWNLOADS_FILE, self.downloads)
        self.save_session()
        super().closeEvent(event)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = BrowserWindow()
    window.show()
    sys.exit(app.exec_())

import json
import os
from threading import Lock
from typing import Optional, Dict, List

class JSONExporter:
    """
    Menyimpan trace log ke file JSON dengan thread-safe buffer.
    """

    def __init__(self, file_path: Optional[str] = None):
        self._file_path = file_path or os.environ.get("TRACE_LOG_FILE", "results.json")
        self._lock = Lock()
        self._buffer: List[Dict] = []

    def __call__(self, trace_record: Dict):
        """
        Menambahkan satu trace record ke buffer dan menyimpan seluruh buffer ke file.
        """
        with self._lock:
            self._buffer.append(trace_record)
            try:
                with open(self._file_path, "w", encoding="utf-8") as f:
                    json.dump(
                        sorted(self._buffer, key=lambda x: x["id"]),
                        f,
                        indent=4,
                        ensure_ascii=False
                    )
            except Exception as e:
                print(f"[JSONExporter] Failed to write to {self._file_path}: {e}")

    def reset(self):
        """
        Menghapus seluruh buffer trace yang tersimpan.
        """
        with self._lock:
            self._buffer.clear()

    def load(self) -> List[Dict]:
        """
        Memuat isi file JSON menjadi list of trace records.
        """
        if os.path.exists(self._file_path):
            try:
                with open(self._file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[JSONExporter] Failed to load file: {e}")
        return []

    def get_file_path(self) -> str:
        """
        Mengembalikan path file JSON tujuan penyimpanan.
        """
        return self._file_path


# Singleton exporter instance untuk dipakai di seluruh aplikasi
_exporter_instance = JSONExporter()


def export_trace_json(trace: Dict, path: Optional[str] = None):
    """
    Fungsi helper untuk ekspor satu trace ke file JSON.
    Jika `path` diberikan, buat instance baru hanya untuk satu kali simpan.
    """
    if path:
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(trace, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[export_trace_json] Failed to write to {path}: {e}")
    else:
        # Tambah ke buffer dan simpan seluruh buffer
        _exporter_instance(trace)

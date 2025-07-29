import os
import json
import threading
from itertools import count
from datetime import datetime


class TraceStore:
    """
    Menyimpan jejak eksekusi fungsi untuk debugging, visualisasi call graph, dan audit.
    """

    _traces = []
    _id_counter = count(0)
    _lock = threading.Lock()
    _handlers = {}

    # File log default (optional digunakan jika diperlukan)
    _log_file = os.environ.get("TRACE_LOG_FILE", "results.json")

    @classmethod
    def register_handler(cls, name, handler_func):
        """
        Mendaftarkan handler eksternal untuk setiap trace baru.
        """
        cls._handlers[name] = handler_func

    @classmethod
    def unregister_handler(cls, name):
        """
        Menghapus handler dari registry.
        """
        cls._handlers.pop(name, None)

    @classmethod
    def next_id(cls):
        """
        Mendapatkan ID unik berikutnya untuk trace baru.
        """
        with cls._lock:
            return next(cls._id_counter)

    @classmethod
    def log_call(cls, id, name, file, line, args, kwargs, result, duration, parent,
                 success, exception_message=None, category=None, level=None, status_code=None):
        """
        Menyimpan data trace pemanggilan fungsi.
        """

        timestamp = datetime.utcnow().isoformat()

        # Default level penanda trace
        if level is None:
            if not success:
                level = "error" if exception_message else "warning"
            elif status_code is not None:
                if status_code >= 500:
                    level = "error"
                elif status_code >= 400:
                    level = "warning"
                else:
                    level = "info"
            else:
                level = "info"

        trace_record = {
            "id": id,
            "name": name,
            "file": file,
            "line": line,
            "args": cls._safe_repr(args),
            "kwargs": cls._safe_repr(kwargs),
            "result": cls._safe_repr(result),
            "duration": duration,
            "parent": parent,
            "success": success,
            "exception_message": exception_message,
            "category": category,
            "level": level,
            "status_code": status_code,
            "timestamp": timestamp
        }

        print(f"[LOG CALL DEBUG] category={category}, level={level}, name={name}")

        # Simpan ke memory
        with cls._lock:
            cls._traces.append(trace_record)

        # Panggil semua handler yang terdaftar
        for handler_name, handler_func in cls._handlers.items():
            try:
                handler_func(trace_record)
            except Exception as e:
                print(f"[TraceStore] Handler '{handler_name}' error: {e}")

        # Optional: Simpan ke file (nonaktif secara default)
        # try:
        #     with cls._lock:
        #         with open(cls._log_file, "w", encoding="utf-8") as f:
        #             json.dump(sorted(cls._traces, key=lambda x: x["id"]), f, indent=4, ensure_ascii=False)
        # except Exception as e:
        #     print(f"[TraceStore] Failed to write to {cls._log_file}: {e}")

    @staticmethod
    def _safe_repr(obj):
        """
        Representasi aman dari objek agar tetap bisa di-serialisasi.
        """
        try:
            return repr(obj)
        except Exception as e:
            return f"<unserializable: {e}>"

    @classmethod
    def dump(cls):
        """
        Mendapatkan semua trace tersimpan.
        """
        with cls._lock:
            return sorted(cls._traces, key=lambda x: x["id"])

    @classmethod
    def get_by_id(cls, id):
        """
        Mendapatkan trace berdasarkan ID.
        """
        with cls._lock:
            return next((t for t in cls._traces if t["id"] == id), None)

    @classmethod
    def get_last(cls, n=1):
        """
        Mengambil n trace terakhir.
        """
        with cls._lock:
            return cls._traces[-n:] if n > 0 else []

    @classmethod
    def filtered_dump(cls, *, category=None, success=None, has_exception=None):
        """
        Filter trace berdasarkan kategori, status sukses, atau exception.
        """
        with cls._lock:
            filtered = cls._traces.copy()

        if category is not None:
            filtered = [t for t in filtered if t.get("category") == category]
        if success is not None:
            filtered = [t for t in filtered if t.get("success") == success]
        if has_exception is not None:
            filtered = [t for t in filtered if bool(t.get("exception_message")) == has_exception]

        return sorted(filtered, key=lambda x: x["id"])

    @classmethod
    def reset(cls):
        """
        Reset seluruh trace yang tersimpan (biasanya untuk test/reset state).
        """
        with cls._lock:
            cls._traces.clear()
            cls._id_counter = count(0)

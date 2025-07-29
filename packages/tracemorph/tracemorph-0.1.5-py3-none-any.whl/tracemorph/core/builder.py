from tracemorph.store.trace_log import TraceStore
from tracemorph.output.human_writer import generate_narrative
from tracemorph.output.json_exporter import export_trace_json
import os
from datetime import datetime
from colorama import Fore, Style, init

# Inisialisasi colorama (penting terutama di Windows)
init(autoreset=True)


class TraceBuilder:
    @staticmethod
    def get_last_trace():
        """Ambil trace terakhir lengkap dengan context dan narasi."""
        trace = TraceStore.get_last(1)
        return TraceBuilder._build(trace[0]) if trace else None

    @staticmethod
    def get_trace_by_id(trace_id):
        """Ambil trace berdasarkan ID-nya."""
        trace = TraceStore.get_by_id(trace_id)
        return TraceBuilder._build(trace) if trace else None

    @staticmethod
    def build_latest_and_export(path="./trace_output", filename=None):
        """
        Ambil trace terakhir, ekspor ke JSON + narrative TXT,
        dan kembalikan dict dengan tambahan narrative berwarna untuk terminal.
        """
        trace = TraceStore.get_last(1)
        if not trace:
            return None

        built = TraceBuilder._build(trace[0])
        os.makedirs(path, exist_ok=True)

        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        fname = filename or f"trace_{ts}"

        # Export ke file JSON
        export_trace_json(built, os.path.join(path, f"{fname}.json"))

        # Export narrative ke file TXT
        narrative_path = os.path.join(path, f"{fname}.txt")
        with open(narrative_path, "w", encoding="utf-8") as f:
            f.write(built["narrative"])

        # Tambahkan versi narrative yang sudah diwarnai untuk terminal
        colored_narrative = TraceBuilder._colorize_narrative(built)

        # Return lengkap dengan colored narrative
        return {**built, "colored_narrative": colored_narrative}

    @staticmethod
    def _colorize_narrative(built_trace: dict) -> str:
        """
        Beri warna pada bagian penting narasi untuk tampilan terminal:
        - Error: merah terang
        - Call chain: cyan terang
        - Lokasi file dan baris: kuning terang
        - Narasi: hijau
        """
        narrative = built_trace.get("narrative", "")
        error = built_trace.get("error") or "Unknown error"
        flow = " → ".join(built_trace.get("flow", [])) or "Unknown flow"
        file = built_trace["trace"].get("file", "unknown")
        line = built_trace["trace"].get("line", "?")

        RED = Fore.RED + Style.BRIGHT
        CYAN = Fore.CYAN + Style.BRIGHT
        YELLOW = Fore.YELLOW + Style.BRIGHT
        GREEN = Fore.GREEN
        RESET = Style.RESET_ALL

        colored = (
            f"{RED}Error: {error}{RESET}\n"
            f"{CYAN}Function call chain: {flow}{RESET}\n"
            f"{YELLOW}Crash location: {file} line {line}{RESET}\n\n"
            f"{GREEN}{narrative}{RESET}"
        )
        return colored

    @staticmethod
    def _build(trace: dict) -> dict:
        """Rakit dict trace lengkap dengan narasi."""
        flow = TraceBuilder._reconstruct_flow(trace)
        trace_with_flow = dict(trace)  # shallow copy
        trace_with_flow["flow"] = flow
        narrative = generate_narrative(trace_with_flow)

        return {
            "id": trace["id"],
            "flow": flow,
            "error": trace.get("exception_message"),
            "message": trace.get("exception_message"),
            "trace": trace,
            "narrative": narrative,
        }

    @staticmethod
    def _reconstruct_flow(trace: dict) -> list:
        """Bangun urutan call dari parent-child hingga root."""
        flow = []
        current = trace
        while current:
            flow.insert(0, current.get("name", "unknown"))
            parent_id = current.get("parent")
            if not parent_id:
                break
            current = TraceStore.get_by_id(parent_id)
        return flow

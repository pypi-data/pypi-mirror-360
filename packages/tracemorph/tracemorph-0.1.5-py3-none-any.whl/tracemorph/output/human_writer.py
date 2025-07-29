import requests
from typing import Dict


def generate_narrative(trace: Dict) -> str:
    """
    Menghasilkan narasi human-readable dari sebuah trace dict
    menggunakan Pollinations AI API berbasis prompt engineering.
    """
    prompt = build_prompt(trace)
    try:
        response = requests.get(f"https://text.pollinations.ai/{prompt}", timeout=10)
        if response.status_code == 200:
            return response.text.strip()
        return f"[Narrative Generation Failed] HTTP {response.status_code}: {response.text}"
    except Exception as e:
        return f"[Narrative Error] {str(e)}"


def build_prompt(trace: Dict) -> str:
    """
    Membentuk prompt deskriptif dari trace dict untuk dikirim ke LLM.
    Menggunakan penjelasan struktur JSON agar AI paham konteks data.
    """
    # Gunakan flow dari trace jika ada, kalau tidak bangun dari parents
    flow = " → ".join(trace.get("flow") or extract_call_chain(trace)) or "Unknown flow"
    error_message = trace.get("exception_message", "Unknown error")
    error_location = f"{trace.get('file', 'unknown')} line {trace.get('line', '?')}"

    # Susun prompt supaya AI paham arti setiap field dalam trace dict
    prompt = (
        "You are a senior software engineer. Explain this Python error trace JSON below.\n"
        "The JSON structure fields mean:\n"
        "- id: unique trace ID\n"
        "- name: error or function name\n"
        "- file: source file path\n"
        "- line: line number where error happened\n"
        "- args: function arguments\n"
        "- kwargs: keyword arguments\n"
        "- result: function result\n"
        "- duration: execution time\n"
        "- parent: parent trace ID\n"
        "- success: boolean success flag\n"
        "- exception_message: error message\n"
        "- category: error category\n"
        "- level: error severity\n"
        "- status_code: HTTP status if relevant\n"
        "- timestamp: error timestamp\n"
        "- flow: function call chain (if available)\n\n"
        "Now explain:\n"
        f"- Error: {error_message}\n"
        f"- Function call chain: {flow}\n"
        f"- Crash location: {error_location}\n"
        "- What likely caused it and how to fix it?"
    )

    return prompt


def extract_call_chain(trace: Dict) -> list:
    """
    Menelusuri chain pemanggilan fungsi berdasarkan parent trace ID.
    Asumsinya trace mungkin memiliki dict `parents` yang memetakan ID ke trace parent.
    Jika tidak ada, hanya gunakan current trace name.
    """
    chain = []
    current = trace
    while current:
        chain.insert(0, current.get("name", "unknown"))
        parent_id = current.get("parent")
        if not parent_id:
            break
        current = trace.get("parents", {}).get(parent_id)
        if current is None:
            break
    return chain

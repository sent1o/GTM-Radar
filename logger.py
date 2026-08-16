import os
import json
from datetime import datetime

BASE_LOG_DIR = "logs"

def save_log(startup_name: str, stage: str, data: dict):
    """
    stage: назва етапу (наприклад, 'links', 'router', 'extractor', 'comparator')
    data: словник з даними, які хочемо зберегти
    """
    # Створюємо папку для конкретного етапу, якщо її ще нема
    dir_path = os.path.join(BASE_LOG_DIR, stage)
    os.makedirs(dir_path, exist_ok=True)
    
    # Чистимо назву стартапу від спецсимволів, щоб файл зберігся без помилок
    safe_name = "".join(c if c.isalnum() else "_" for c in startup_name).strip("_")
    if not safe_name:
        safe_name = "unknown_startup"
        
    file_path = os.path.join(dir_path, f"{safe_name}.json")
    
    # Формуємо структуру логу
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "startup": startup_name,
        "stage": stage,
        "data": data
    }
    
    # Пишемо у файл (перезаписуємо старий лог цього ж стартапу на цьому ж етапі)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(log_entry, f, ensure_ascii=False, indent=2)
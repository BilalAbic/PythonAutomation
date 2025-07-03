#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Progress Monitor for PDF Processing
"""

import os
import time
from pathlib import Path
import json

def count_lines(file_path):
    """Count lines in file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except:
        return 0

def get_file_size_mb(file_path):
    """Get file size in MB"""
    try:
        return round(Path(file_path).stat().st_size / (1024 * 1024), 2)
    except:
        return 0

def show_progress():
    """Show current progress"""
    output_file = "output_json/toplam_egitim_veriseti.jsonl"
    
    qa_count = count_lines(output_file)
    file_size = get_file_size_mb(output_file)
    
    print(f"\n🤖 PDF TO SIMPLE DATASET MONITOR")
    print("=" * 50)
    print(f"📄 Total Q&A pairs: {qa_count}")
    print(f"💾 File size: {file_size} MB")
    print(f"⏰ Time: {time.strftime('%H:%M:%S')}")
    
    # Show last few questions if file exists
    if qa_count > 0:
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    data = json.loads(last_line)
                    print(f"\n📝 Last Question: {data['soru'][:100]}...")
        except:
            pass
    
    print("=" * 50)

if __name__ == "__main__":
    print("🔍 Starting simple monitor...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            show_progress()
            time.sleep(10)  # 10 saniyede bir güncelle
    except KeyboardInterrupt:
        print("\n👋 Monitor stopped") 
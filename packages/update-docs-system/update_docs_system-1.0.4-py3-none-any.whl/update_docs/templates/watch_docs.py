#!/usr/bin/env python3
"""
File Watcher для автоматического обновления документации при изменении .md файлов
Запуск: python watch_docs.py
"""

import os
import sys
import time
import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MarkdownHandler(FileSystemEventHandler):
    def __init__(self, docs_dir="docs", content_json="content/Content.json", description_md="content/Description_for_agents.md"):
        self.docs_dir = docs_dir
        self.content_json = content_json
        self.description_md = description_md
        self.last_update = 0
        self.update_delay = 2
        self.update_thread = None
        
        Path(content_json).parent.mkdir(parents=True, exist_ok=True)
        
    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.md'):
            self.schedule_update(event.src_path, "modified")
    
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.md'):
            self.schedule_update(event.src_path, "created")
    
    def on_deleted(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.md'):
            self.schedule_update(event.src_path, "deleted")
    
    def on_moved(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.md') or event.dest_path.endswith('.md'):
            self.schedule_update(f"{event.src_path} -> {event.dest_path}", "moved")
    
    def schedule_update(self, file_path, action):
        current_time = time.time()
        self.last_update = current_time
        
        print(f"📝 Detected {action}: {file_path}")
        
        if self.update_thread and self.update_thread.is_alive():
            return
        
        self.update_thread = threading.Timer(self.update_delay, self.update_documentation)
        self.update_thread.start()
    
    def update_documentation(self):
        try:
            print("🔄 Updating documentation...")
            
            try:
                from update_docs.core import update_content_system
                update_content_system(self.docs_dir, self.content_json, self.description_md)
                
                print("✅ Documentation updated successfully")
                print(f"📋 Updated: {self.content_json}")
                print(f"📖 Updated: {self.description_md}")
                
            except ImportError:
                print("❌ update_docs module not found")
                print("💡 Please install: pip install update-docs-system")
                return
                
        except Exception as e:
            print(f"❌ Error updating documentation: {e}")
            
        finally:
            print("=" * 60)

def main():
    print("👀 Starting documentation watcher...")
    print("🔍 Monitoring .md files for changes...")
    print("📁 Current directory:", os.getcwd())
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 60)
    
    event_handler = MarkdownHandler()
    
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping documentation watcher...")
        observer.stop()
    
    observer.join()
    print("✅ Documentation watcher stopped")

if __name__ == "__main__":
    main()

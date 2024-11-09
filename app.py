import os
import json
import psutil
import platform
import subprocess
from pathlib import Path

# Optional: For machine learning-based recommendations
# from sklearn.cluster import KMeans
# import numpy as np

class DeveloperEnvironmentOptimizer:
    def __init__(self):
        self.system_info = {}
        self.ide_settings_path = self.get_ide_settings_path()
        self.recommendations = []

    def get_ide_settings_path(self):
        # Example for VSCode
        home = Path.home()
        if platform.system() == "Windows":
            return home / "AppData" / "Roaming" / "Code" / "User" / "settings.json"
        elif platform.system() == "Darwin":  # macOS
            return home / "Library" / "Application Support" / "Code" / "User" / "settings.json"
        else:  # Linux and others
            return home / ".config" / "Code" / "User" / "settings.json"

    def analyze_system(self):
        print("Analyzing system resources...")
        self.system_info['cpu_percent'] = psutil.cpu_percent(interval=1)
        self.system_info['memory'] = psutil.virtual_memory()._asdict()
        self.system_info['disk'] = psutil.disk_usage('/')._asdict()
        self.system_info['os'] = platform.system()
        self.system_info['python_version'] = platform.python_version()
        # Add more system metrics as needed
        print("System analysis complete.")

    def analyze_running_processes(self):
        print("Analyzing running processes...")
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            processes.append(proc.info)
        self.system_info['processes'] = processes
        print("Process analysis complete.")

    def load_ide_settings(self):
        if self.ide_settings_path.exists():
            with open(self.ide_settings_path, 'r') as f:
                try:
                    settings = json.load(f)
                    self.system_info['ide_settings'] = settings
                    print("IDE settings loaded.")
                except json.JSONDecodeError:
                    self.system_info['ide_settings'] = {}
                    print("Failed to parse IDE settings. Using empty settings.")
        else:
            self.system_info['ide_settings'] = {}
            print("IDE settings file not found. Using empty settings.")

    def recommend_optimizations(self):
        print("Generating optimization recommendations...")
        # Example recommendations based on CPU usage
        if self.system_info['cpu_percent'] > 80:
            self.recommendations.append("High CPU usage detected. Consider closing unused applications or upgrading your CPU.")
        
        # Memory recommendations
        mem = self.system_info['memory']
        if mem['percent'] > 80:
            self.recommendations.append("High memory usage detected. Consider adding more RAM or optimizing running applications.")
        
        # Disk recommendations
        disk = self.system_info['disk']
        if disk['percent'] > 90:
            self.recommendations.append("Disk space is critically low. Consider cleaning up unnecessary files or expanding storage.")
        
        # IDE settings recommendations
        ide_settings = self.system_info.get('ide_settings', {})
        if ide_settings:
            if ide_settings.get("editor.renderWhitespace") != "all":
                self.recommendations.append("Enable 'Render Whitespace' in your IDE for better code readability.")
            if ide_settings.get("editor.fontSize", 12) < 14:
                self.recommendations.append("Consider increasing the font size in your IDE for better readability.")
        
        # Add more rules based on system_info and IDE settings
        print("Recommendations generated.")

    def display_recommendations(self):
        print("\nOptimization Recommendations:")
        for idx, rec in enumerate(self.recommendations, 1):
            print(f"{idx}. {rec}")

    def apply_ide_recommendations(self):
        settings = self.system_info.get('ide_settings', {})
        updated = False

        # Example: Enable renderWhitespace and set fontSize
        if settings.get("editor.renderWhitespace") != "all":
            settings["editor.renderWhitespace"] = "all"
            self.recommendations.append("Setting 'editor.renderWhitespace' to 'all'.")
            updated = True
        
        if settings.get("editor.fontSize", 12) < 14:
            settings["editor.fontSize"] = 14
            self.recommendations.append("Setting 'editor.fontSize' to 14.")
            updated = True

        if updated:
            with open(self.ide_settings_path, 'w') as f:
                json.dump(settings, f, indent=4)
            print("IDE settings updated.")
        else:
            print("No IDE settings changes needed.")

    def optimize_workflow(self):
        # Placeholder for workflow optimizations
        self.recommendations.append("Consider using keyboard shortcuts to improve coding efficiency.")
        self.recommendations.append("Automate repetitive tasks using scripts or tools like Make or npm scripts.")

    def run(self):
        self.analyze_system()
        self.analyze_running_processes()
        self.load_ide_settings()
        self.recommend_optimizations()
        self.optimize_workflow()
        self.display_recommendations()
        self.apply_ide_recommendations()

if __name__ == "__main__":
    optimizer = DeveloperEnvironmentOptimizer()
    optimizer.run()

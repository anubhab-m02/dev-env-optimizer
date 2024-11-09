import os
import json
import psutil
import platform
from pathlib import Path
import streamlit as st
import pandas as pd  # Ensure pandas is imported

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
        self.system_info['cpu_percent'] = psutil.cpu_percent(interval=1)
        self.system_info['memory'] = psutil.virtual_memory()._asdict()
        self.system_info['disk'] = psutil.disk_usage('/')._asdict()
        self.system_info['os'] = platform.system()
        self.system_info['python_version'] = platform.python_version()
        # Add more system metrics as needed

    def analyze_running_processes(self):
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        self.system_info['processes'] = processes

    def load_ide_settings(self):
        if self.ide_settings_path.exists():
            with open(self.ide_settings_path, 'r') as f:
                try:
                    settings = json.load(f)
                    self.system_info['ide_settings'] = settings
                except json.JSONDecodeError:
                    self.system_info['ide_settings'] = {}
        else:
            self.system_info['ide_settings'] = {}

    def recommend_optimizations(self):
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

    def apply_ide_recommendations(self):
        settings = self.system_info.get('ide_settings', {})
        updated = False
        applied_changes = []

        # Example: Enable renderWhitespace and set fontSize
        if settings.get("editor.renderWhitespace") != "all":
            settings["editor.renderWhitespace"] = "all"
            applied_changes.append("Set 'editor.renderWhitespace' to 'all'.")
            updated = True
        
        if settings.get("editor.fontSize", 12) < 14:
            settings["editor.fontSize"] = 14
            applied_changes.append("Set 'editor.fontSize' to 14.")
            updated = True

        if updated:
            try:
                with open(self.ide_settings_path, 'w') as f:
                    json.dump(settings, f, indent=4)
                return applied_changes
            except Exception as e:
                return [f"Failed to update IDE settings: {e}"]
        else:
            return ["No IDE settings changes needed."]

    def optimize_workflow(self):
        # Placeholder for workflow optimizations
        self.recommendations.append("Consider using keyboard shortcuts to improve coding efficiency.")
        self.recommendations.append("Automate repetitive tasks using scripts or tools like Make or npm scripts.")

    def run_analysis(self):
        self.analyze_system()
        self.analyze_running_processes()
        self.load_ide_settings()
        self.recommend_optimizations()
        self.optimize_workflow()

def main():
    st.set_page_config(page_title="Developer Environment Optimizer", layout="wide")
    st.title("🚀 Developer Environment Optimizer")

    optimizer = DeveloperEnvironmentOptimizer()

    # Initialize session state variables if they don't exist
    if 'analysis_done' not in st.session_state:
        st.session_state.analysis_done = False
    if 'applied_changes' not in st.session_state:
        st.session_state.applied_changes = []
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = []
    if 'system_info' not in st.session_state:
        st.session_state.system_info = {}

    st.sidebar.header("Options")
    if st.sidebar.button("Run Analysis"):
        with st.spinner("Analyzing your system..."):
            optimizer.run_analysis()
            st.session_state.recommendations = optimizer.recommendations
            st.session_state.system_info = optimizer.system_info
            st.session_state.analysis_done = True
        st.success("Analysis complete!")

    if st.session_state.analysis_done:
        st.header("📊 System Information")
        sys_info = st.session_state.system_info
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("CPU Usage")
            cpu_percent = sys_info.get('cpu_percent', 0) / 100  # Normalize to [0.0, 1.0]
            st.progress(cpu_percent)
            st.write(f"{sys_info.get('cpu_percent', 0)}%")

        with col2:
            st.subheader("Memory Usage")
            mem = sys_info.get('memory', {})
            mem_percent = mem.get('percent', 0) / 100  # Normalize to [0.0, 1.0]
            st.progress(mem_percent)
            st.write(f"{mem.get('percent', 0)}%")

        with col3:
            st.subheader("Disk Usage")
            disk = sys_info.get('disk', {})
            disk_percent = disk.get('percent', 0) / 100  # Normalize to [0.0, 1.0]
            st.progress(disk_percent)
            st.write(f"{disk.get('percent', 0)}%")

        st.markdown("---")
        st.header("💡 Optimization Recommendations")
        recommendations = st.session_state.recommendations
        if recommendations:
            for idx, rec in enumerate(recommendations, 1):
                st.markdown(f"**{idx}.** {rec}")
        else:
            st.write("No recommendations available.")

        st.markdown("---")
        st.header("⚙️ Apply IDE Recommendations")
        if st.button("Apply Recommendations to IDE Settings"):
            with st.spinner("Applying IDE settings..."):
                applied_changes = optimizer.apply_ide_recommendations()
                st.session_state.applied_changes = applied_changes
            for change in st.session_state.applied_changes:
                st.write(f"- {change}")
            st.success("IDE settings updated.")

        st.markdown("---")
        st.header("🔄 Refresh Analysis")
        if st.button("Refresh Analysis"):
            # Reset session state variables
            st.session_state.analysis_done = False
            st.session_state.recommendations = []
            st.session_state.system_info = {}
            st.session_state.applied_changes = []
            st.success("Analysis reset. Click 'Run Analysis' to start again.")

        st.markdown("---")
        st.header("📁 Running Processes")
        processes = sys_info.get('processes', [])
        if processes:
            # Convert the list of processes to a DataFrame
            df = pd.DataFrame(processes).head(100)
            # Display the DataFrame using Streamlit's data editor
            st.dataframe(df)
            st.write("Displaying top 100 running processes.")
        else:
            st.write("No process information available.")

if __name__ == "__main__":
    main()

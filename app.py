import os
import json
import psutil
import platform
from pathlib import Path
import streamlit as st
import pandas as pd
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Install the genai package before running: pip install genai
import google.generativeai as genai

# Optional: For GPU and screen info
try:
    import GPUtil
except ImportError:
    GPUtil = None

try:
    from screeninfo import get_monitors
except ImportError:
    get_monitors = None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeveloperEnvironmentOptimizer:
    def __init__(self):
        self.system_info = {}
        self.ide_settings_path = self.get_ide_settings_path()
        self.recommendations = ""
        self.api_key = self.get_gemini_api_key()
        self.model = self.initialize_gemini_model()

    def get_gemini_api_key(self):
        """
        Retrieve Gemini AI API key from environment variable.
        """
        api_key = os.getenv('GEMINI_API_KEY')  # Ensure this environment variable is set
        if not api_key:
            raise ValueError("Gemini AI API key not found. Please set the 'GEMINI_API_KEY' environment variable.")
        return api_key

    def initialize_gemini_model(self):
        """
        Initialize the Gemini AI Generative Model.
        """
        try:
            # Configure the API key globally
            genai.configure(api_key=self.api_key)
            # Initialize the GenerativeModel without passing the api_key
            model = genai.GenerativeModel('gemini-1.5-flash-002')
            return model  # Return the initialized model
        except AttributeError:
            logger.error("genai module does not have 'GenerativeModel' attribute.")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI model: {e}")
            raise

    def get_ide_settings_path(self):
        """
        Get the path to the IDE settings file.
        Example provided for VSCode. Modify if using a different IDE.
        """
        home = Path.home()
        if platform.system() == "Windows":
            return home / "AppData" / "Roaming" / "Code" / "User" / "settings.json"
        elif platform.system() == "Darwin":  # macOS
            return home / "Library" / "Application Support" / "Code" / "User" / "settings.json"
        else:  # Linux and others
            return home / ".config" / "Code" / "User" / "settings.json"

    def analyze_system(self):
        """
        Gather system information.
        """
        self.system_info['cpu_percent'] = psutil.cpu_percent(interval=1)
        self.system_info['memory'] = psutil.virtual_memory()._asdict()
        self.system_info['disk'] = psutil.disk_usage('/')._asdict()
        self.system_info['os'] = platform.system()
        self.system_info['python_version'] = platform.python_version()

        # Network Usage
        net_io = psutil.net_io_counters()
        self.system_info['network'] = {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv
        }

        # GPU Usage
        if GPUtil:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # Assuming single GPU for simplicity
                self.system_info['gpu'] = {
                    'name': gpu.name,
                    'load': gpu.load * 100,  # Convert to percentage
                    'memory_used': gpu.memoryUsed,
                    'memory_total': gpu.memoryTotal
                }
            else:
                self.system_info['gpu'] = {}
        else:
            self.system_info['gpu'] = {}

        # Screen Resolution
        if get_monitors:
            monitors = get_monitors()
            if monitors:
                primary = monitors[0]
                self.system_info['screen_resolution'] = (primary.width, primary.height)
            else:
                self.system_info['screen_resolution'] = (0, 0)
        else:
            self.system_info['screen_resolution'] = (0, 0)

    def analyze_running_processes(self):
        """
        Analyze currently running processes.
        """
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        self.system_info['processes'] = processes

    def load_ide_settings(self):
        """
        Load IDE settings from the settings.json file.
        """
        if self.ide_settings_path.exists():
            with open(self.ide_settings_path, 'r') as f:
                try:
                    settings = json.load(f)
                    self.system_info['ide_settings'] = settings
                except json.JSONDecodeError:
                    self.system_info['ide_settings'] = {}
        else:
            self.system_info['ide_settings'] = {}

    def generate_prompt(self):
        """
        Create a prompt for the Generative AI model based on system_info.
        """
        prompt = f"""
        Answer the question as detailed as possible from the provided context. Make sure to provide all the details.
        If the answer is not in the provided context, just say, "Answer is not available in the context." Don't provide a wrong answer.

        Context: {json.dumps(self.system_info, indent=2)}

        Question: Based on the above system information, provide at least five detailed and actionable recommendations to optimize the developer's environment for better efficiency and performance.

        Answer (Use markdown formatting for numbering and bullet points):
        """
        return prompt

    def get_generative_ai_recommendations(self):
        """
        Use Gemini AI's GenerativeModel to generate recommendations based on system info.
        """
        prompt = self.generate_prompt()
        try:
            response = self.model.generate_content(prompt)
            
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    reply = ' '.join(part.text for part in candidate.content.parts)
                    self.recommendations = reply  # Store the entire markdown string
                else:
                    self.recommendations = "No readable response generated from Gemini AI."
            else:
                self.recommendations = "No candidates returned from Gemini AI."
        except AttributeError as ae:
            logger.error(f"Attribute error: {ae}")
            self.recommendations = f"Attribute error: {ae}"
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            self.recommendations = f"Error generating response: {str(e)}"

    def apply_ide_recommendations(self):
        """
        Apply the AI-generated recommendations to the IDE settings.
        """
        settings = self.system_info.get('ide_settings', {})
        updated = False
        applied_changes = []

        # Example: Enable renderWhitespace and set fontSize based on AI recommendations
        # For simplicity, we assume AI has already recommended specific changes
        # Here, we can parse the recommendations to find actionable items or set them manually

        # This part can be enhanced to parse AI-generated text and apply specific settings
        # For demonstration, we'll manually set based on previous examples

        if settings.get("editor.renderWhitespace") != "all":
            settings["editor.renderWhitespace"] = "all"
            applied_changes.append("Set 'editor.renderWhitespace' to 'all'.")
            updated = True

        if settings.get("editor.fontSize", 12) < 14:
            settings["editor.fontSize"] = 14
            applied_changes.append("Set 'editor.fontSize' to 14.")
            updated = True

        # Example: Limit number of extensions
        extensions = settings.get("extensions", [])
        if len(extensions) > 10:
            # For simplicity, we won't automatically disable extensions.
            applied_changes.append(
                f"You have {len(extensions)} extensions installed. Consider disabling or uninstalling unused extensions to improve performance."
            )

        if updated:
            try:
                with open(self.ide_settings_path, 'w') as f:
                    json.dump(settings, f, indent=4)
                applied_changes.append("IDE settings updated successfully.")
                return applied_changes
            except Exception as e:
                return [f"Failed to update IDE settings: {e}"]
        else:
            return ["No IDE settings changes needed."]

    def run_analysis(self):
        """
        Run the full analysis and generate recommendations.
        """
        self.analyze_system()
        self.analyze_running_processes()
        self.load_ide_settings()
        self.get_generative_ai_recommendations()
        self.optimize_workflow()

    def optimize_workflow(self):
        """
        Placeholder for additional workflow optimizations.
        """
        # Placeholder for workflow optimizations
        self.recommendations

def main():
    st.set_page_config(page_title="Developer Environment Optimizer", layout="wide")
    st.title("🚀 Developer Environment Optimizer")

    # Initialize the optimizer
    try:
        optimizer = DeveloperEnvironmentOptimizer()
    except ValueError as ve:
        st.error(str(ve))
        st.stop()
    except Exception as e:
        st.error(f"Failed to initialize the optimizer: {e}")
        st.stop()

    # Initialize session state variables if they don't exist
    if 'analysis_done' not in st.session_state:
        st.session_state.analysis_done = False
    if 'applied_changes' not in st.session_state:
        st.session_state.applied_changes = []
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = ""
    if 'system_info' not in st.session_state:
        st.session_state.system_info = {}

    st.sidebar.header("Options")
    if st.sidebar.button("Run Analysis"):
        with st.spinner("Analyzing your system and generating recommendations..."):
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

        # Additional System Metrics Display
        st.markdown("---")
        st.header("📡 Network Usage")
        net = sys_info.get('network', {})
        total_net = net.get('bytes_sent', 0) + net.get('bytes_recv', 0)
        st.write(f"**Total Bytes Sent:** {net.get('bytes_sent', 0)} bytes")
        st.write(f"**Total Bytes Received:** {net.get('bytes_recv', 0)} bytes")
        st.write(f"**Total Network Usage:** {total_net} bytes")

        st.markdown("---")
        st.header("🎮 GPU Usage")
        gpu = sys_info.get('gpu', {})
        if gpu and gpu.get('load') is not None:
            st.write(f"**GPU Name:** {gpu.get('name', 'N/A')}")
            st.write(f"**GPU Load:** {gpu.get('load', 0)}%")
            st.write(f"**GPU Memory Used:** {gpu.get('memory_used', 0)} MB / {gpu.get('memory_total', 0)} MB")
        else:
            st.write("No GPU information available or GPUtil not installed.")

        st.markdown("---")
        st.header("🖥️ Screen Resolution")
        screen_res = sys_info.get('screen_resolution', (0, 0))
        st.write(f"**Width:** {screen_res[0]} px")
        st.write(f"**Height:** {screen_res[1]} px")

        st.markdown("---")
        st.header("💡 Optimization Recommendations")
        recommendations = st.session_state.recommendations
        if recommendations:
            st.markdown(recommendations, unsafe_allow_html=True)
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
            st.session_state.recommendations = ""
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

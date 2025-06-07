# 🚀 Developer Environment Optimizer

An interactive Streamlit application that analyzes your development environment and provides actionable recommendations to optimize it for better efficiency and performance, powered by Google's Gemini AI model.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Environment Variables](#environment-variables)
- [Requirements](#requirements)
- [Contributing](#contributing)

## Features

- **System Analysis**: Collects detailed system information including CPU, memory, disk usage, GPU stats, and running processes.
- **AI-Powered Recommendations**: Generates optimization recommendations using Google's Gemini AI model.
- **IDE Settings Optimization**: Applies recommended changes to your IDE settings (e.g., Visual Studio Code). (Work in Progress)
- **Interactive UI**: User-friendly interface built with Streamlit, including tabs for system info, recommendations, and processes.
- **Process Monitoring**: Displays running processes and their resource usage.

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/anubhab-m02/dev-env-optimizer.git
   cd dev-env-optimizer
   ```

2. **Create a Virtual Environment (Optional but Recommended)**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   If `requirements.txt` is not available, install dependencies manually:

   ```bash
   pip install streamlit psutil pandas dotenv google-generativeai
   ```

   Optional dependencies for GPU and screen info:

   ```bash
   pip install GPUtil screeninfo
   ```

## Usage

1. **Set Up Environment Variables**

   Create a `.env` file in the project root directory and add your Gemini AI API key:

   ```dotenv
   GEMINI_API_KEY=your_gemini_ai_api_key_here
   ```

2. **Run the Application**

   ```bash
   streamlit run main.py
   ```

3. **Navigate the App**

   - **Run Analysis**: Click on "Run Analysis" in the sidebar to analyze your system.
   - **View Recommendations**: Go to the "💡 Recommendations" tab to see AI-generated suggestions.
   - **Apply Recommendations**: Click on "Apply Recommendations to IDE Settings" to update your IDE settings.
   - **Refresh Analysis**: Click on "Refresh Analysis" to reset and start a new analysis.

## Environment Variables

- `GEMINI_API_KEY`: Your Gemini AI API key. Obtain it from [Google Generative AI](https://developers.generativeai.google/).

## Requirements

- **Python 3.7 or higher**
- **Operating System**: Windows, macOS, or Linux
- **IDE Supported**: Visual Studio Code (modify paths if using a different IDE)

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create your feature branch:

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. Commit your changes:

   ```bash
   git commit -m 'Add some feature'
   ```

4. Push to the branch:

   ```bash
   git push origin feature/your-feature-name
   ```

5. Open a pull request.

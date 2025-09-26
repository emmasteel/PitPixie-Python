# Pit Voids Analyzer

## Overview
The Pit Voids Analyzer is a Python application that utilizes Azure AI Search and the Azure AI Foundry o3-mini model to analyze "Pit Voids" within a given dataset. This application provides a chat interface for users to interact with the AI model and receive insights based on their queries.

## Prerequisites
Before you begin, ensure you have the following installed on your machine:
- Python 3.7 or higher
- pip (Python package installer)

## Setting Up the Project

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd pit-voids-analyzer
   ```

2. **Create a Virtual Environment**
   It is recommended to create a virtual environment to manage dependencies.
   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies**
   Install the required packages listed in `requirements.txt`.
   ```bash
   pip install -r requirements.txt
   ```

5. **Set Up Environment Variables**
   Copy the `.env.example` file to `.env` and fill in the necessary Azure credentials and configuration settings.
   ```bash
   cp .env.example .env
   ```

## Running the Application

To start the application, run the following command:
```bash
python src/main.py
```

Once the application is running, you will be prompted to enter a question related to "Pit Voids." The application will interact with the Azure AI Foundry model and provide responses in a chat format.

## Usage Instructions

- Type your question when prompted and press Enter.
- The application will display the response from the AI model.
- You can continue to ask questions in the same session.

## Additional Resources

- For prompt engineering instructions, refer to the `src/prompts/engineering.md` file.
- Ensure you have the necessary permissions and access to the Azure services used in this application.

## Troubleshooting

If you encounter any issues, please check the following:
- Ensure your Azure credentials are correctly set in the `.env` file.
- Verify that all dependencies are installed without errors.
- Check the console for any error messages that may provide clues to the issue.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
# ✨PitPixie✨ | Pit Void Analyser

## Overview
The PitPixie is a Python application that utilises Azure AI Search and the Azure AI Foundry o3-mini model to analyse "Pit Voids" within a given dataset. This application provides a chat interface for users to interact with the AI model and receive insights based on their queries.

## Prerequisites
Before you begin, ensure you have the following installed on your machine:
- Python 3.7 or higher
- pip (Python package installer)

## Setting Up the Project

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
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
   
   You'll need to configure the following environment variables in your `.env` file:
   
   **Azure Cognitive Search:**
   - `AZURE_SEARCH_ENDPOINT` - Your Azure Search service URL
   - `AZURE_SEARCH_KEY` - Admin or query key for the search service
   - `AZURE_SEARCH_INDEX` - Name of the search index containing Pit-Void documents
   - `AZURE_SEMANTIC_CONFIG` - Semantic configuration name for enhanced search
   
   **Azure AI Foundry (o3-mini model):**
   - `FOUNDARY_MODEL_ENDPOINT` - Complete endpoint URL for your o3-mini deployment
   - `FOUNDARY_API_KEY` - API key for the Foundry service
   
   **Azure OpenAI (for embeddings):**
   - `AZURE_OPENAI_ENDPOINT` - Azure OpenAI service endpoint for embeddings
   - `AZURE_OPENAI_KEY` - API key for Azure OpenAI service
   - `EMBEDDING_DEPLOYMENT` - Name of your text embedding deployment (e.g., text-embedding-3-small)

## Running the Application

### PitPixie Chat

To start the application, run the following command:
```bash
python src/main.py
```

Once the application is running, you will be prompted to enter a question related to "Pit Voids." The application will interact with the Azure AI Foundry model and provide responses in a chat format.

### PitPixie Batch Processing

The Batch Processing script processes a list of questions from a text file (`src/questions.txt`) and saves the responses to individual text files within the `output` directory.

To run batch processing out to individual TXT files, use the following command:
```bash
python src/batch_qas.py
```

To run the batch processing and output to a single JSON file, use:
```bash
python src/batch_qa_json.py
```

### PitPixie Convert to CSV

Once the batch processing is complete, you can convert the output text files into a single CSV file for easier analysis.

To run the conversion script, use the following command:
```bash
python src/transform_csv.py
```

## Chat Usage Instructions

- Type your question when prompted and press Enter.
- The application will display the response from the AI model.
- You can continue to ask questions in the same session.

## Additional Resources

- For prompt engineering instructions, refer to the `src/prompts/engineering.md` file.
- Ensure you have the necessary permissions and access to the Azure services used in this application.

## Troubleshooting

If you encounter any issues, please check the following:
- **Environment Variables**: Ensure all required Azure credentials are correctly set in the `.env` file:
  - Azure Search credentials (endpoint, key, index, semantic config)
  - Azure AI Foundry credentials (model endpoint, API key)  
  - Azure OpenAI credentials (endpoint, key, embedding deployment)
- **Dependencies**: Verify that all dependencies are installed without errors by running `pip install -r requirements.txt`
- **Virtual Environment**: Make sure you've activated your virtual environment before running the application
- **Azure Services**: Ensure you have the necessary permissions and access to the Azure services
- **Error Logs**: Check the console for any error messages that may provide clues to the issue

## Licence

This project is licensed under the MIT Licence - see the LICENCE file for details.
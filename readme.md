# AI Fact Checker API

This project implements an AI-powered Fact Checking API using FastAPI, LangChain, and various AI models and tools.

## Features

- Fact-checking of claims using Google Fact Check API
- News verification using GDELT API
- Image description capabilities
- Tweet generation based on fact-check results
- Supports multiple Language Models (OpenAI GPT-4 and Anthropic Claude)

## Demo

![AI Fact Checker Demo](path/to/your/demo.gif)

This GIF demonstrates the key features of our AI Fact Checker API:

1. **Input**: A user submits a claim or news article for fact-checking.
2. **Processing**: The system analyzes the input using various AI models and external APIs.
3. **Fact-Check Results**: The API returns a detailed fact-check report.
4. **Tweet Generation**: Based on the fact-check results, a concise tweet is generated.

[You can replace this text with a more detailed explanation of your specific workflow and key features as shown in your demo GIF or video.]

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.7+
- FastAPI
- LangChain
- OpenAI API key
- Anthropic API key
- Google Fact Check API key
- Tavily API key

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/ai-fact-checker-api.git
   cd ai-fact-checker-api
   ```

2. Install the required packages:

   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   Create a `.env` file in the root directory and add the following:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   GOOGLE_FACT_CHECK_API_KEY=your_google_fact_check_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```

## Configuration

You can configure the Language Model to use by editing the `settings.json` file:

```json
{
	"llm": "anthropic"
}
```

Options are "openai" or "anthropic".

## Usage

To run the server:

```
uvicorn app:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

### Endpoints

- `GET /`: Welcome message
- `GET /health`: Health check
- `POST /stream`: Main fact-checking endpoint
- `POST /generate_tweet`: Generate a tweet based on fact-check results

## Project Structure

- `app.py`: Main FastAPI application
- `prompt.py`: Fact-checking prompt generation
- `utils.py`: Utility functions
- `settings.json`: Configuration file
- `fact_checker.py`: Fact-checking tools
- `tweet_generator.py`: Tweet generation logic
- `vision.py`: Image description tool

## Contributing

Contributions to this project are welcome. Please ensure you follow these guidelines:

1. Fork the repository
2. Create a new branch: `git checkout -b feature-branch-name`
3. Make your changes and commit them: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-branch-name`
5. Create a pull request

## Contact

If you have any questions or feedback, please contact me at [simonesaletti@gmail.com] or DM me on twitter [https://x.com/Simo1028].

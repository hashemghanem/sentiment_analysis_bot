# Sentiment Analysis Bot

This is a practice project repository for sentiment analysis using FastAPI and scikit-learn.

## Getting Started

### Using GitHub Codespaces

GitHub Codespaces provides a complete, configurable dev environment on top of a powerful VM.

#### How to Create a GitHub Codespace:

1. **Navigate to the repository** on GitHub
2. Click the green **"Code"** button
3. Select the **"Codespaces"** tab
4. Click **"Create codespace on [branch-name]"**

Alternatively, you can:
- Click the **"+"** icon to create a new codespace
- Use the keyboard shortcut: press `.` (period) on the repository page to open in VS Code for the web

#### What happens when you create a Codespace:

1. GitHub will provision a cloud-based development environment
2. The environment will be configured based on `.devcontainer/devcontainer.json`
3. Python 3.9 and all dependencies from `requirements.txt` will be installed automatically
4. VS Code extensions for Python development will be pre-installed
5. Port 8000 will be forwarded for the FastAPI application

#### Running the Application in Codespaces:

Once your Codespace is ready:

```bash
# Start the FastAPI server
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

The application will be available on port 8000, and GitHub will provide a forwarded URL to access it.

### Local Development

If you prefer to develop locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn src.api.main:app --reload
```

## Project Structure

- `src/api/main.py` - FastAPI application with sentiment prediction endpoint
- `src/model/train.py` - Model training script
- `model.pkl` - Pre-trained sentiment analysis model
- `.devcontainer/` - GitHub Codespaces configuration

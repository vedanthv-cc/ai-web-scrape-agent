# ai-web-scrape-agent

## Building the Docker Image

To build the Docker image, open a terminal in the project root directory and run:

```bash
#Build image
docker build -t ocr-news-app .
```

## Run the Docker Image

```bash
# Run image
docker run -p 8501:8501 ocr-news-app
```

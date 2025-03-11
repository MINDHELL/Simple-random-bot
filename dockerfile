FROM python:3.9
WORKDIR /bot
COPY . /bot
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "main.py"]

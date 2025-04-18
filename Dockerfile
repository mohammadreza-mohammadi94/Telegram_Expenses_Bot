FROM python
WORKDIR /app
COPY . .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt
CMD ["python", "bot.py"]

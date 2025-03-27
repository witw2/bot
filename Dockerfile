# Pobieramy obraz bazowy z Pythonem i ffmpeg
FROM python:3.11-slim

# Instalujemy ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# Ustawiamy katalog roboczy
WORKDIR /bot

# Kopiujemy pliki do kontenera
COPY . .

# Instalujemy zależności z requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Ustawiamy zmienną środowiskową dla Discord Token (lepsza opcja niż plik DSCtoken.py)
ENV DISCORD_TOKEN=

# Uruchamiamy aplikację
CMD ["python", "Sveneusz.py"]

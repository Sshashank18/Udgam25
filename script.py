import requests
import soundfile as sf
import io
from flask import Flask, request, Response, send_from_directory
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
from pyngrok import ngrok
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from transformers import T5Tokenizer, T5ForConditionalGeneration
from gtts import gTTS
import torch
import librosa
import os
import time

# Flask app initialization
app = Flask(__name__)

# Directory for storing audio files
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Twilio credentials
TWILIO_ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
TWILIO_PHONE_NUMBER = os.environ["TWILIO_PHONE_NUMBER"]

# Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Load Wav2Vec2 model and processor
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-960h")
model_wav2vec = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h")

# Load T5 model for response generation
tokenizer = T5Tokenizer.from_pretrained("/home/soumajit/UDGAM/random")
model = T5ForConditionalGeneration.from_pretrained("/home/soumajit/UDGAM/random")

# Start ngrok
public_url = ngrok.connect(5000).public_url
print(f"Public URL: {public_url}")

# Update Twilio webhook
def update_twilio_webhook():
    try:
        client.incoming_phone_numbers.list(phone_number=TWILIO_PHONE_NUMBER)[0].update(
            voice_url=f"{public_url}/handle_call"
        )
        print("Twilio Webhook updated successfully!")  
    except Exception as e:
        print(f"Error updating Twilio webhook: {e}")

# Process audio with Wav2Vec2 and generate transcription
def transcribe_audio(recording_url):
    time.sleep(2)  # Add a 2-second delay to allow the recording to become available
    response = requests.get(recording_url)
    if response.status_code != 200:
        raise Exception(f"Failed to download audio: {response.status_code}")

    temp_file = "temp_recording.wav"
    with open(temp_file, "wb") as f:
        f.write(response.content)

    audio, sample_rate = librosa.load(temp_file, sr=None)
    if sample_rate != 16000:
        audio = librosa.resample(audio, orig_sr=sample_rate, target_sr=16000)
    
    inputs = processor(audio, sampling_rate=16000, return_tensors="pt", padding=True)
    logits = model_wav2vec(inputs.input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.decode(predicted_ids[0])
    return transcription

# Route to serve files
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)

# Handle incoming call
@app.route("/handle_call", methods=["POST"])
def handle_call():
    response = VoiceResponse()
    response.say("Welcome! Please describe your needs. Record your message after the beep.", voice="alice")
    response.record(action="/process_recording", max_length=10, play_beep=True)
    return str(response)

# Process recorded audio
@app.route("/process_recording", methods=["POST"])
def process_recording():
    recording_url = request.form.get("RecordingUrl")
    if not recording_url:
        return Response("No recording URL received.", status=400)

    try:
        transcription_text = transcribe_audio(recording_url)
        print(transcription_text)
        
        if "confirm" in transcription_text.lower():
            response = VoiceResponse()
            response.say("Thank you! Your order has been confirmed. Goodbye!", voice="alice")
            return str(response)

        inputs = tokenizer(transcription_text, return_tensors="pt", max_length=512, truncation=True)
        outputs = model.generate(inputs.input_ids, max_length=50)
        response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(response_text)

        tts = gTTS(text=response_text, lang="en", slow=False)
        response_audio_file = os.path.join(UPLOAD_DIR, "response.mp3")
        tts.save(response_audio_file)

        response = VoiceResponse()
        response.say("Here is my response.")
        response.play(f"{public_url}/uploads/response.mp3")

        # response.say("If this is correct, please say 'confirm' to confirm your order or describe further.", voice="alice")
        response.record(action="/process_recording", max_length=10, play_beep=True)

        return str(response)

    except Exception as e:
        print(f"Error processing recording: {e}")
        return Response("An error occurred while processing the recording.", status=500)

# Make outbound call
@app.route("/make_call", methods=["GET"])
def make_call():
    to_number = request.args.get("to")
    if not to_number:
        return Response("Please provide a 'to' phone number.", status=400)
    call = client.calls.create(
        to=to_number,
        from_=TWILIO_PHONE_NUMBER,
        url=f"{public_url}/handle_call"
    )
    return f"Call initiated. Call SID: {call.sid}"

update_twilio_webhook()
app.run(port=5000)
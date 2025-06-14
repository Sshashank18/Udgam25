# 📞 Udgam25: Voice-Based Automated Customer Care System

This repository contains the code for a **Voice-Based Automated Customer Care System**, developed as part of **Udgam '25**, the flagship event of **E-Cell, IIT Guwahati**. The system simulates a real-time customer-salesperson telephonic conversation using state-of-the-art **speech recognition**, **natural language understanding**, and **text-to-speech** generation — all integrated through **Twilio** for live call functionality.

---

## 🚀 Project Overview

### 📌 Objective
To create an **AI-powered voice agent** that:
- Listens to customer queries via phone call
- Understands and generates human-like responses
- Speaks the responses back to the customer
- Supports basic **negotiation, product queries, and customer support** simulation

---

## 🧠 System Pipeline

Incoming Call → Speech-to-Text → Response Generation → Text-to-Speech → Twilio Audio Response


### 1. **Speech-to-Text**
- **Model Used**: Facebook’s **Wav2Vec 2.0**
- **Library**: 🤗 `transformers`, `torchaudio`, `soundfile`
- Converts customer's spoken query to text in real-time

### 2. **Text Response Generation**
- **Model Used**: `T5ForConditionalGeneration` from HuggingFace
- **Training Dataset**: Dialogues between customer and salesperson
- **Function**: Generates context-aware responses simulating negotiation or support

### 3. **Text-to-Speech (TTS)**
- Converts generated response text back to audio
- **Tools Used**:
  - `gTTS` (Google Text-to-Speech)
  - `TTS` by Coqui.ai (for realistic voices)

### 4. **Call Integration**
- **Service Used**: [Twilio](https://www.twilio.com/)
- Handles:
  - Incoming customer calls
  - Audio streaming
  - Outgoing voice responses

---

## 🧱 Tech Stack

| Task | Tool/Library |
|------|--------------|
| Speech Recognition | `Wav2Vec2ForCTC`, `transformers`, `torchaudio`, `soundfile` |
| Dialogue Generation | `T5ForConditionalGeneration` |
| Text-to-Speech | `gTTS`, `TTS` |
| Telephony API | `twilio` |
| Programming Language | Python |

---



## 🧪 Sample Flow

1. **Customer Says**: “What’s the price of the redmi phone?”
2. **Wav2Vec2**: Transcribes to: `"what is the price of the redmi phone"`
3. **T5 Model**: Generates: `"The Redmi phone is priced at ₹12,999. Would you like a discount?"`
4. **TTS**: Speaks this back to the user over the phone using Twilio

---

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Sshashank18/Udgam25.git
```
### 2. Install Dependencies
```bash pip install -r requirements.txt```
### 3. Run Ipynb File Line By Line
### 4. Add .env File
```Create a .env file with the following:

TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=your_twilio_number
```
### 5. Run the Twilio Flask Server
```bash
python script.py
Expose the server using:
```
```bash
ngrok http 5000
Update the Twilio webhook with the ngrok URL (e.g., https://abcd.ngrok.io/voice).```

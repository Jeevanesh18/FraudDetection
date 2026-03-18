import xgboost as xgb
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
torch.set_num_threads(1)
from fastapi import FastAPI
import numpy as np
import time
import os
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

app = FastAPI()

# -----------------------
# Load XGBoost
# -----------------------
xgb_model = xgb.XGBClassifier()
xgb_model.load_model("models/fraud_shield_xgboost.json")

# -----------------------
# Lazy load FinBERT (IMPORTANT)
# -----------------------
finbert_model = None
tokenizer = None

#def load_finbert():
    #global finbert_model, tokenizer
   # if finbert_model is None:
      #  finbert_path = "models/finbert"
       # print("Loading tokenizer...")
       # tokenizer = AutoTokenizer.from_pretrained(finbert_path)
       # print("Loading model...")
       # finbert_model = AutoModelForSequenceClassification.from_pretrained(finbert_path)
       # print("Model loaded!")
       # finbert_model.eval()

# -----------------------
# FinBERT prediction
# -----------------------
def finbert_predict(text_data):
    text = (
        f"{text_data.get('beneficiary_alias', '')} "
        f"{text_data.get('recent_chat_log', '')} "
        f"{text_data.get('device_metadata', '')}"
    ).lower()

    score = 0.2  # base (safe)

    # 🚨 suspicious language
    suspicious_keywords = [
        "urgent", "asap", "now", "immediately",
        "transfer", "send", "quick", "emergency",
        "help", "please", "account blocked",
        
    ]

    for word in suspicious_keywords:
        if word in text:
            score += 0.1

    # 🚨 strong fraud signals
    strong_flags = [
        "otp", "one time password",
        "password", "bank officer",
        "click link", "verify account",
        "python","Postman"
    ]

    for word in strong_flags:
        if word in text:
            score += 0.2

    # 🚨 device anomaly
    if "new device" in text:
        score += 0.1

    # cap score
    return min(score, 0.95)

# -----------------------
# API endpoint
# -----------------------
@app.post("/predict")
def predict(data: dict):
    print("Start time")
    start = time.time()

    try:
        features = np.array(data["structured"]).reshape(1, -1)
    except:
        return {"error": "Invalid structured input"}
    print("Predicting XGBoost")
    xgb_prob = xgb_model.predict_proba(features)[0][1]

    finbert_score = None
    used_finbert = False

    # Decision logic
    if xgb_prob < 0.2:
        print("XGBoost approved")
        decision = "APPROVE"

   # elif xgb_prob > 0.8:
       # decision = "BLOCK"

    else:
        print("XGBoost not approved")
        used_finbert = True
        finbert_score = finbert_predict(data)

        if finbert_score > 0.7:
            decision = "BLOCK"
        else:
            decision = "APPROVE"

    latency = (time.time() - start) * 1000

    return {
        "xgb_score": float(xgb_prob),
        "finbert_score": finbert_score,
        "used_finbert": used_finbert,
        "decision": decision,
        "latency_ms": latency
    }
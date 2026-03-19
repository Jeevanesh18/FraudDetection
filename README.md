# 💳 Fraud Detection System (XGBoost + NLP)

A real-time fraud detection system that combines structured transaction data with unstructured contextual signals (chat logs, device metadata, beneficiary aliases) to make intelligent approval/block decisions.

---

## 🚀 Overview

This project simulates a **digital wallet fraud detection pipeline**:

- ⚡ Fast structured scoring using **XGBoost**
- 🧠 Context-aware analysis using **(mocked) FinBERT logic**
- 🌐 Deployed as a **real-time API**
- 📊 Integrated with a frontend dashboard

---

## 🧱 Architecture
<p align="center">
  <img src="pics/data_flow.jpeg" alt="Data flow" width="500">
  <br>
  <em>Figure 1: Data Flow</em>
</p>

Frontend (Lovable UI)  
        ↓  
FastAPI Backend (Railway)  
        ↓  
Fraud Detection Logic  
   ├── XGBoost (structured data)  
   └── NLP Layer (FinBERT / mocked)  

---

## 📊 Dataset & Feature Engineering

📎 Notebook:  
https://colab.research.google.com/drive/1rjSswCB3OrUZJz1SGBacZA3BTl-CfT5p?usp=sharing

### Source
- PaySim dataset (Kaggle)

### Feature Engineering

Created additional behavioral and contextual features:

- Transaction patterns:
  - `hour_of_day`
  - `is_night`
  - `day_of_week`
  - `is_weekend`

- Account behavior:
  - `nameOrig_NB_TX_7DAY_WINDOW`
  - `nameOrig_AVG_AMOUNT_7DAY_WINDOW`
  - `nameDest_NB_TX_7DAY_WINDOW`
  - `nameDest_AVG_AMOUNT_7DAY_WINDOW`

- Entity flags:
  - `isMerchant`
  - `isCustomer`

---

## 🧠 Unstructured Data (Simulated)

Added synthetic fields:

- `beneficiary_alias`
- `recent_chat_log`
- `device_metadata`

⚠️ Note:  
These were generated using LLMs and are **randomly simulated**.  
A real dataset with genuine user interaction data would significantly improve performance.

---

## 🤖 Model 1 — XGBoost (Structured Data)

📎 Training Notebook:  
https://colab.research.google.com/drive/10CA_fZ4w_O4feld1zlkFUBPutQ2Pe96m?usp=sharing

### Performance
Accuracy : 0.9972

Precision (Fraud) : 0.9396

Recall (Fraud) : 0.9939

F1-Score : 0.9660

ROC-AUC : 0.9994

PRC-AUC (AUPRC) : 0.9971


### Confusion Matrix
[[39895 105]
[ 10 1633]]


### Classification Report
precision    recall  f1-score   support

  1.00      1.00      1.00     40000
  
  0.94      0.99      0.97      1643


## 📊 Model Explainability (SHAP)

<p align="center">
  <img src="pics/SHAP.png" alt="SHAP" width="500">
  <br>
  <em>Figure 2: SHAP Analysis</em>
</p>

---

## 🧠 Model 2 — FinBERT (NLP Layer)

### 📎 Training Notebook:  
https://colab.research.google.com/drive/159lK-ZYVIzHCAYyCAblA_6-AqneoAA6o?usp=sharing

### Fine tuned model:
https://drive.google.com/drive/folders/1cA0fAGbrAvlowLslnzkwdVs3BRe8V2jC?usp=sharing

### 🎯 Objective
Enhance fraud detection by incorporating unstructured contextual signals such as:

- user chat logs

- beneficiary aliases

- device metadata

This layer is designed to detect social engineering patterns (e.g., impersonation, urgency, scam intent) that are not captured by structured transaction features.

## 🤖 Approach

Fine-tuned a transformer-based model (initially FinBERT) for binary classification:

- Fraudulent context

- Non-fraudulent context

### Performance
Accuracy: 0.6887

### ⚠️ Limitations

- Performance is constrained by synthetic, LLM-generated training data

- Task mismatch: FinBERT is optimized for financial sentiment analysis, not fraud intent detection

- Lack of real-world conversational fraud datasets significantly impacts generalization

### ⚙️ Deployment Decision

The NLP model was not deployed in production due to:

- Large model size (~400MB)

- High latency for real-time inference

Instead, a lightweight heuristic scoring function is used to simulate contextual risk scoring in the deployed system.

### 🧠 Design Insight

This NLP layer is intended as a secondary decision system, triggered only when the structured model (XGBoost) is uncertain.

This reflects real-world fraud detection systems, where:

- fast models handle high-confidence decisions

- deeper models analyze ambiguous cases

### 🔮 Future Improvements

- Replace FinBERT with lighter models (e.g., DistilBERT or MiniLM) for faster inference

- Train on real-world scam / social engineering datasets

- Apply model compression techniques (quantization, distillation) for deployment

- Expand to multi-class classification (e.g., impersonation, phishing, urgency detection)

- Integrate explainability for contextual predictions

---

## 🔍 Threshold Testing

📎 Notebook:  
https://colab.research.google.com/drive/1y2miA9TGnYPDs_bezJvK95boUvDxaLO4?usp=sharing

Used to identify transactions near decision thresholds (e.g., ~0.55) for testing hybrid logic.

---

## ⚙️ API (FastAPI)

Deployed using Railway.

### Endpoint
POST /predict

### API URL
https://web-production-c3c14.up.railway.app/predict

---

### 📥 Example Request

```json
{
  "structured": [
    9, 14003.98, 4657.0, 0.0, 0.0, 0.0, 0, 0,
    0, 0, 0, 0, 1, 9, 0, 0, 0,
    1.0, 14003.98, 1.0, 14003.98,
    1.0, 14003.98, 1.0, 14003.98,
    1.0, 14003.98, 1.0, 14003.98,
    5
  ],
  "beneficiary_alias": "Bank Negara Investigation",
  "recent_chat_log": "Why is my transaction taking longer than usual today?",
  "device_metadata": "Mozilla/5.0 (Linux; Android 14; Samsung SM-F946B)"
}
```

### 📤 Example Response
```json
{
  "xgb_score": 0.5880897045135498,
  "finbert_score": 0.2,
  "used_finbert": true,
  "decision": "APPROVE",
  "latency_ms": 2.22
}
```

## 🧠 Decision Logic

XGBoost Score lower than 0.2	=  APPROVE

XGBoost Score higher than 0.8	 =  BLOCK

XGBoost Score 0.2 – 0.8  =	Use NLP layer

## 🌐 Frontend Demo

https://digitalwalletfraud.lovable.app/

Simulates:

- transaction flows

- fraud detection responses

- real-time API interaction

## ⚡ Deployment

- Backend: Railway (FastAPI)

- Model: XGBoost (loaded at runtime)

- NLP: Mocked for latency + deployment constraints

## ⚠️ Limitations

- Synthetic NLP data reduces FinBERT performance

- FinBERT model not deployed due to:

-- large size (>400MB)

-- high latency

-- No real user behavioral dataset

## 🔮 Future Improvements

- Use real-world chat/device datasets

- Deploy optimized NLP model (quantized / distilled)

- Add explainability (SHAP in API responses)

- Improve threshold tuning dynamically

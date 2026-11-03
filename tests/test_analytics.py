"""
Unit Tests for Task C: Machine Learning, NLP Sentiment, and Computer Vision Modules.
"""
import pytest
from src.analytics.risk_predictor import PatientRiskPredictor
from src.analytics.sentiment_analyzer import PatientSentimentAnalyzer
from src.analytics.vision_triage import ComputerVisionTriageModule

def test_risk_predictor_accuracy():
    predictor = PatientRiskPredictor()
    assert predictor.is_trained is True
    # Assignment constraint: Minimum 90% accuracy in patient risk assessment
    assert predictor.accuracy >= 0.90, f"Expected accuracy >= 0.90, got {predictor.accuracy}"

def test_risk_predictor_high_risk_case():
    predictor = PatientRiskPredictor()
    high_risk_patient = {
        "age": 75,
        "heart_rate": 115,
        "systolic_bp": 165,
        "diastolic_bp": 98,
        "chronic_conditions": 3,
        "past_admissions_12m": 3,
        "symptom_severity_score": 9.0
    }
    result = predictor.predict_risk(high_risk_patient)
    assert result["is_high_risk"] is True
    assert result["risk_tier"] == "High Risk"
    assert result["risk_score"] >= 60.0
    assert "Immediate" in result["recommendation"] or "Priority" in result["recommendation"]

def test_risk_predictor_low_risk_case():
    predictor = PatientRiskPredictor()
    low_risk_patient = {
        "age": 25,
        "heart_rate": 68,
        "systolic_bp": 115,
        "diastolic_bp": 75,
        "chronic_conditions": 0,
        "past_admissions_12m": 0,
        "symptom_severity_score": 2.0
    }
    result = predictor.predict_risk(low_risk_patient)
    assert result["is_high_risk"] is False
    assert result["risk_tier"] == "Low Risk"
    assert result["risk_score"] < 50.0

def test_sentiment_analyzer_urgency():
    analyzer = PatientSentimentAnalyzer()
    res = analyzer.analyze("Help! I have severe chest pain and can't breathe!")
    assert "Urgent" in res["sentiment"] or "Critical" in res["priority_level"]
    assert res["requires_priority_routing"] is True

def test_sentiment_analyzer_frustration():
    analyzer = PatientSentimentAnalyzer()
    res = analyzer.analyze("I have been waiting too long, this service is terrible and frustrating!")
    assert "Frustrated" in res["sentiment"]
    assert res["score"] < 0

def test_sentiment_analyzer_positive():
    analyzer = PatientSentimentAnalyzer()
    res = analyzer.analyze("Thank you so much, your help was wonderful and great!")
    assert res["sentiment"] == "Positive"
    assert res["score"] > 0

def test_vision_triage_heuristics():
    vision = ComputerVisionTriageModule()
    # Test rash image classification
    res_rash = vision.analyze_image("skin_rash_photo.jpg", "Severe red itchy rash on arm")
    assert res_rash["image_analyzed"] is True
    assert "Dermatology" in res_rash["recommended_department"]
    assert "disclaimer" in res_rash

    # Test X-ray classification
    res_xray = vision.analyze_image("chest_xray_scan.png", "Chest scan review")
    assert res_xray["image_analyzed"] is True
    assert "Radiology" in res_xray["recommended_department"] or "Pulmonology" in res_xray["recommended_department"]


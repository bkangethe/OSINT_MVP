def check_alerts(profiles, threshold=70):
    alerts = []
    for p in profiles:
        if p["risk_score"] >= threshold:
            alerts.append({
                "user": p["name"],
                "risk": p["risk_score"],
                "reason": p["nlp"]["label"]
            })
    return alerts

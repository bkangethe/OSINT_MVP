import torch

detector = None

def detect_objects(image_path=None):
    """
    Returns detected objects and risk level.
    Lazy-loads YOLOv5 model.
    """
    global detector
    if detector is None:
        try:
            detector = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        except:
            detector = None

    if image_path is None or detector is None:
        return {"risk": "low", "thumbnail_url": "https://via.placeholder.com/150"}

    results = detector(image_path)
    risk = "low"
    for obj in results.pandas().xyxy[0]['name'].tolist():
        if obj.lower() in ["knife", "gun", "flag"]:
            risk = "high"
    return {"risk": risk, "thumbnail_url": "https://via.placeholder.com/150"}

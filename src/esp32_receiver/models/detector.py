import time
import cv2
import supervision as sv
from rfdetr import RFDETRMedium
from src.esp32_receiver.core.config import settings

class PhoneDetector:
    def __init__(self):
        print(f"Loading RFDETRMedium model from {settings.WEIGHTS_PATH}...")
        self.model = RFDETRMedium(pretrain_weights=str(settings.WEIGHTS_PATH))
        self.box_annotator = sv.BoxAnnotator()
        self.label_annotator = sv.LabelAnnotator()
        print("RFDETRMedium model loaded.")

    def analyze_frame(self, image_path: str, output_path: str) -> tuple[bool, str, float]:
        start_time = time.time()
        
        try:
            image = cv2.imread(image_path)
            if image is None:
                return False, "Could not decode image", time.time() - start_time

            detections = self.model.predict(image_path, threshold=0.5)

            raw_class_ids = getattr(detections, 'class_id', [])
            
            persons = []
            phones = []

            for i, cid in enumerate(raw_class_ids):
                if cid == 1: # person
                    persons.append(detections.xyxy[i])
                elif cid == 77: # cell phone
                    phones.append(detections.xyxy[i])

            usage_detected = False

            for person in persons:
                px1, py1, px2, py2 = person
                p_center_y = (py1 + py2) / 2
                p_width = px2 - px1
                p_height = py2 - py1

                for phone in phones:
                    phx1, phy1, phx2, phy2 = phone
                    ph_center_x = (phx1 + phx2) / 2
                    ph_center_y = (phy1 + phy2) / 2

                    h_margin = p_width * 0.3
                    v_margin = p_height * 0.2

                    if px1 - h_margin <= ph_center_x <= px2 + h_margin:
                        if ph_center_y <= p_center_y + v_margin:
                            usage_detected = True
                            break

                if usage_detected:
                    break

            label = "Phone Usage Detected" if usage_detected else "No Phone Usage"
            
            annotated = self.box_annotator.annotate(image.copy(), detections)
            annotated = self.label_annotator.annotate(annotated, detections)

            cv2.putText(
                annotated,
                f"Status: {label}",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (255, 255, 255),
                2,
            )

            cv2.imwrite(output_path, annotated)

            end_time = time.time()
            cumulated_time = end_time - start_time
            
            return usage_detected, label, cumulated_time
        except Exception as e:
            print(f"Error during RF-DETR inference: {e}")
            end_time = time.time()
            return False, str(e), end_time - start_time

detector = PhoneDetector()

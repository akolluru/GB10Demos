import cv2
import numpy as np
from PIL import Image
import torch
from ultralytics import YOLO
import os
import logging
import gc
import subprocess

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def get_gpu_info():
    """Get detailed GPU information using nvidia-smi."""
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error getting GPU info: {str(e)}"

def print_gpu_utilization():
    """Print current GPU utilization."""
    if torch.cuda.is_available():
        logger.info(f"CUDA Device: {torch.cuda.get_device_name(0)}")
        logger.info(f"CUDA Version: {torch.version.cuda}")
        logger.info(f"Current GPU Memory: {torch.cuda.memory_allocated(0) / 1024**2:.2f} MB")
        logger.info(f"Max GPU Memory: {torch.cuda.max_memory_allocated(0) / 1024**2:.2f} MB")
        logger.info(f"GPU Memory Cached: {torch.cuda.memory_reserved(0) / 1024**2:.2f} MB")
        logger.info("\nDetailed GPU Info:")
        logger.info(get_gpu_info())
    else:
        logger.warning("CUDA is not available. Running on CPU.")

def create_visualization(image, detections):
    """Create visualization of detections."""
    vis_image = image.copy()
    
    # Create a color map for different object types
    color_map = {
        'person': (0, 255, 0),    # Green for people
        'car': (255, 0, 0),       # Blue for vehicles
        'truck': (255, 0, 0),
        'bus': (255, 0, 0),
        'building': (0, 0, 255),  # Red for structures
        'house': (0, 0, 255),
        'bridge': (0, 0, 255),
        'fire': (0, 165, 255),    # Orange for hazards
        'smoke': (0, 165, 255),
        'debris': (0, 165, 255)
    }
    
    for det in detections:
        class_name = det['class'].lower()
        color = color_map.get(class_name, (128, 128, 128))  # Default to gray
        
        # Draw bounding box
        x1, y1, x2, y2 = map(int, det['bbox'])
        cv2.rectangle(vis_image, (x1, y1), (x2, y2), color, 2)
        
        # Add label
        label = f"{det['class']} {det['confidence']:.2f}"
        cv2.putText(vis_image, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    return vis_image

class VisionProcessor:
    def __init__(self):
        # Force CUDA initialization
        if torch.cuda.is_available():
            logger.info("Initializing CUDA...")
            torch.cuda.init()
            # Test CUDA functionality
            test_tensor = torch.zeros(1).cuda()
            logger.info(f"CUDA test tensor created: {test_tensor.device}")
            # Clear CUDA cache
            torch.cuda.empty_cache()
            self.device = torch.device("cuda")
            logger.info(f"Using GPU: {torch.cuda.get_device_name(0)}")
        else:
            logger.warning("CUDA not available. Please ensure:")
            logger.warning("1. NVIDIA drivers are properly installed")
            logger.warning("2. CUDA toolkit is installed")
            logger.warning("3. PyTorch is installed with CUDA support")
            logger.warning("Falling back to CPU")
            self.device = torch.device("cpu")

        try:
            logger.info("Loading YOLO model...")
            # Load YOLO model with GPU acceleration
            self.model = YOLO('yolov8x.pt')  # Using YOLOv8x for best accuracy
            if torch.cuda.is_available():
                self.model.to(self.device)
            
            # Enable CUDA optimizations
            if torch.cuda.is_available():
                torch.backends.cudnn.benchmark = True
                torch.backends.cuda.matmul.allow_tf32 = True
                torch.backends.cudnn.allow_tf32 = True
            
            print_gpu_utilization()
            
        except Exception as e:
            logger.error(f"Error initializing models: {str(e)}")
            raise

    def process_image(self, image_path):
        """Process an image and return detections."""
        try:
            logger.info(f"Processing image: {image_path}")
            
            # Clear GPU memory before processing
            if self.device.type == "cuda":
                torch.cuda.empty_cache()
                gc.collect()
            
            # Load and preprocess image
            logger.info("Loading image...")
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image from {image_path}")
            
            # Resize image for faster processing while maintaining aspect ratio
            max_size = 640
            h, w = image.shape[:2]
            scale = min(max_size / w, max_size / h)
            new_size = (int(w * scale), int(h * scale))
            image = cv2.resize(image, new_size)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            logger.info("Running YOLO detection...")
            # Run YOLO detection with optimized settings
            results = self.model(
                image,
                conf=0.25,  # Confidence threshold
                iou=0.45,   # NMS IoU threshold
                max_det=50, # Maximum detections
                verbose=False
            )
            
            # Process detections
            logger.info("Processing detections...")
            detections = results[0].boxes.data.cpu().numpy()
            
            objects_detected = []
            for det in detections:
                x1, y1, x2, y2, conf, cls = det
                class_name = results[0].names[int(cls)]
                objects_detected.append({
                    'class': class_name,
                    'confidence': float(conf),
                    'bbox': [float(x1), float(y1), float(x2), float(y2)],
                    'area_m2': (float(x2) - float(x1)) * (float(y2) - float(y1)) * 0.0001
                })
            
            # Create visualization
            logger.info("Creating visualization...")
            visualization = create_visualization(image, objects_detected)
            
            # Convert visualization to RGB for display
            visualization = cv2.cvtColor(visualization, cv2.COLOR_BGR2RGB)
            
            # Clear GPU memory after processing
            if self.device.type == "cuda":
                torch.cuda.empty_cache()
                gc.collect()
            
            logger.info(f"Processing complete. Detected {len(objects_detected)} objects.")
            return {
                "detections": objects_detected,
                "visualization": visualization,
                "image": image
            }
            
        except Exception as e:
            logger.error(f"Error in process_image: {str(e)}")
            logger.error(f"Error details: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def analyze_terrain(self, image_path):
        """Analyze terrain and return detailed description."""
        try:
            logger.info(f"Starting terrain analysis for: {image_path}")
            results = self.process_image(image_path)
            
            # Analyze detections for terrain-specific information
            terrain_analysis = {
                "obstacles": [],
                "hazards": [],
                "people": [],
                "vehicles": [],
                "structures": []
            }
            
            # Process detections
            logger.info("Categorizing detections...")
            for det in results["detections"]:
                class_name = det["class"].lower()
                if class_name in ["person", "human"]:
                    terrain_analysis["people"].append(det)
                elif class_name in ["car", "truck", "bus", "motorcycle"]:
                    terrain_analysis["vehicles"].append(det)
                elif class_name in ["building", "house", "bridge"]:
                    terrain_analysis["structures"].append(det)
                elif class_name in ["fire", "smoke", "debris"]:
                    terrain_analysis["hazards"].append(det)
                else:
                    terrain_analysis["obstacles"].append(det)
            
            logger.info("Terrain analysis complete")
            return {
                "terrain_analysis": terrain_analysis,
                "detections": results["detections"],
                "visualization": results["visualization"]
            }
            
        except Exception as e:
            logger.error(f"Error in analyze_terrain: {str(e)}")
            logger.error(f"Error details: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise 
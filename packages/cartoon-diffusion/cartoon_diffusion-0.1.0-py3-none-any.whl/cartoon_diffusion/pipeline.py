import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from PIL import Image
import cv2
import math
import warnings
from diffusers import DDPMScheduler
import mediapipe as mp
from huggingface_hub import hf_hub_download

warnings.filterwarnings('ignore')

class OptimizedMediaPipeExtractor:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        self.landmark_indices = {
            'face_outline': [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109],
            'left_eye': [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246],
            'right_eye': [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398],
            'left_eyebrow': [46, 53, 52, 51, 48, 115, 131, 134, 102, 49, 220, 305],
            'right_eyebrow': [276, 283, 282, 295, 285, 336, 296, 334, 293, 300, 276, 353],
            'nose': [1, 2, 5, 4, 6, 19, 94, 168, 8, 9, 10, 151, 195, 197, 196, 3],
            'lips': [61, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318],
            'chin': [175, 199, 428, 262, 18],
            'forehead': [9, 10, 151, 337, 299, 333, 298, 301]
        }
    
    def extract_features(self, image_path_or_array):
        try:
            features = self._extract_robust_features(image_path_or_array)
            return self._normalize_features(features)
        except Exception as e:
            print(f"Error in feature extraction: {e}")
            return self._get_default_features()

    def _extract_robust_features(self, image_path_or_array):
        if isinstance(image_path_or_array, str):
            image = cv2.imread(image_path_or_array)
            if image is None:
                raise ValueError(f"Failed to load image: {image_path_or_array}")
        else:
            image = image_path_or_array.copy()
            if image is None or image.size == 0:
                raise ValueError("Invalid image array provided")
        
        if len(image.shape) != 3 or image.shape[2] != 3:
            raise ValueError("Image must be a 3-channel color image")
        
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w = rgb_image.shape[:2]
        
        if h < 50 or w < 50:
            raise ValueError("Image too small for feature extraction")
        
        results = self.face_mesh.process(rgb_image)
        
        if not results.multi_face_landmarks:
            raise ValueError("No face detected in image")
        
        landmarks = results.multi_face_landmarks[0]
        face_landmarks = np.array([[lm.x * w, lm.y * h, lm.z] for lm in landmarks.landmark])
        
        if len(face_landmarks) == 0:
            raise ValueError("No valid landmarks detected")
        
        features = torch.zeros(18, dtype=torch.float32)
        
        try:
            left_corner = face_landmarks[33] if len(face_landmarks) > 33 else face_landmarks[0]
            right_corner = face_landmarks[263] if len(face_landmarks) > 263 else face_landmarks[-1]
            face_width = np.max(face_landmarks[:, 0]) - np.min(face_landmarks[:, 0])
            eye_angle = abs(left_corner[1] - right_corner[1]) / (face_width + 1e-8)
            features[0] = min(max(int(eye_angle * 20), 0), 2)
        except:
            features[0] = 1
        
        try:
            eye_openness = self._calculate_eye_openness(face_landmarks)
            features[1] = 1 if eye_openness > 10 else 0
        except:
            features[1] = 1
        
        try:
            eyelid_prominence = self._calculate_eyelid_prominence(face_landmarks)
            features[2] = 1 if eyelid_prominence > 5 else 0
        except:
            features[2] = 1
        
        try:
            face_height = np.max(face_landmarks[:, 1]) - np.min(face_landmarks[:, 1])
            nose_tip = face_landmarks[2] if len(face_landmarks) > 2 else face_landmarks[0]
            chin_bottom = face_landmarks[18] if len(face_landmarks) > 18 else face_landmarks[-1]
            chin_length = np.linalg.norm(nose_tip[:2] - chin_bottom[:2])
            chin_length_normalized = chin_length / (face_height + 1e-8)
            features[3] = min(max(int(chin_length_normalized * 6), 0), 2)
        except:
            features[3] = 1
        
        for i in range(4, 18):
            try:
                if i == 4:
                    features[i] = 1 if self._calculate_eyebrow_thickness(rgb_image, face_landmarks) > 0.3 else 0
                elif i == 5:
                    features[i] = 7
                elif i == 6:
                    features[i] = 2
                elif i == 7:
                    face_width = np.max(face_landmarks[:, 0]) - np.min(face_landmarks[:, 0])
                    face_height = np.max(face_landmarks[:, 1]) - np.min(face_landmarks[:, 1])
                    aspect_ratio = face_width / (face_height + 1e-8)
                    features[i] = min(max(int(aspect_ratio * 3.5), 0), 6)
                elif i == 8:
                    features[i] = 0
                elif i == 9:
                    features[i] = 55
                elif i == 10:
                    features[i] = 2
                elif i == 11:
                    features[i] = 5
                elif i == 12:
                    features[i] = 4
                elif i == 13:
                    features[i] = 0
                elif i == 14:
                    features[i] = 0
                elif i == 15:
                    features[i] = 1
                elif i == 16:
                    features[i] = 1
                elif i == 17:
                    features[i] = 1
            except:
                features[i] = 1
        
        return features

    def _normalize_features(self, features):
        normalized = torch.zeros_like(features, dtype=torch.float32)
        max_values = [2, 1, 1, 2, 1, 13, 3, 6, 14, 110, 4, 10, 9, 11, 6, 2, 2, 2]
        
        for i, max_val in enumerate(max_values):
            if max_val > 0:
                normalized[i] = torch.clamp(features[i] / max_val, 0.0, 1.0)
            else:
                normalized[i] = 0.0
        
        return normalized
    
    def _get_default_features(self):
        default_values = torch.tensor([3, 55, 7, 7, 6, 1, 1, 1, 1, 1, 2, 5, 5, 3, 1, 1, 2, 1], dtype=torch.float32)
        return self._normalize_features(default_values)
    
    def _calculate_eye_openness(self, landmarks):
        try:
            left_top = landmarks[159][1] if len(landmarks) > 159 else 0
            left_bottom = landmarks[145][1] if len(landmarks) > 145 else 0
            left_openness = abs(left_top - left_bottom)
            
            right_top = landmarks[386][1] if len(landmarks) > 386 else 0
            right_bottom = landmarks[374][1] if len(landmarks) > 374 else 0
            right_openness = abs(right_top - right_bottom)
            
            return (left_openness + right_openness) / 2
        except:
            return 10.0
    
    def _calculate_eyelid_prominence(self, landmarks):
        try:
            left_eyelid = landmarks[159][1] - landmarks[158][1] if len(landmarks) > 159 else 5
            right_eyelid = landmarks[386][1] - landmarks[385][1] if len(landmarks) > 386 else 5
            return abs(left_eyelid + right_eyelid) / 2
        except:
            return 5.0
    
    def _calculate_eyebrow_thickness(self, image, landmarks):
        try:
            left_brow_points = [landmarks[i] for i in self.landmark_indices['left_eyebrow'] if i < len(landmarks)]
            if len(left_brow_points) < 2:
                return 0.5
            
            y_coords = [p[1] for p in left_brow_points]
            thickness = (max(y_coords) - min(y_coords)) / image.shape[0]
            return min(thickness * 10, 1.0)
        except:
            return 0.5


class OptimizedConditionedUNet(nn.Module):
    def __init__(self, in_channels=3, out_channels=3, attr_dim=18, base_channels=56):
        super().__init__()
        
        self.time_embed_dim = 224
        self.time_embed = nn.Sequential(
            nn.Linear(self.time_embed_dim, 448),
            nn.SiLU(),
            nn.Linear(448, 448)
        )
        
        self.attr_embed = nn.Sequential(
            nn.Linear(attr_dim, 112),
            nn.ReLU(),
            nn.Dropout(0.05),
            nn.Linear(112, 224),
            nn.ReLU(),
            nn.Linear(224, 448)
        )
        
        self.conv_in = nn.Conv2d(in_channels, base_channels, 3, padding=1)
        
        self.down_blocks = nn.ModuleList([
            self._make_down_block(base_channels, base_channels * 2),
            self._make_down_block(base_channels * 2, base_channels * 4),
            self._make_down_block(base_channels * 4, base_channels * 8),
            self._make_down_block(base_channels * 8, base_channels * 8)
        ])
        
        self.mid_block = self._make_conv_block(base_channels * 8 + 448, base_channels * 8)
        
        self.up_blocks = nn.ModuleList([
            nn.Sequential(
                nn.Upsample(scale_factor=2, mode='bilinear', align_corners=False),
                self._make_conv_block(base_channels * 8 + base_channels * 8, base_channels * 8)
            ),
            nn.Sequential(
                nn.Upsample(scale_factor=2, mode='bilinear', align_corners=False),
                self._make_conv_block(base_channels * 8 + base_channels * 4, base_channels * 4)
            ),
            nn.Sequential(
                nn.Upsample(scale_factor=2, mode='bilinear', align_corners=False),
                self._make_conv_block(base_channels * 4 + base_channels * 2, base_channels * 2)
            ),
            nn.Sequential(
                nn.Upsample(scale_factor=2, mode='bilinear', align_corners=False),
                self._make_conv_block(base_channels * 2 + base_channels, base_channels)
            )
        ])
        
        self.conv_out = nn.Sequential(
            nn.GroupNorm(8, base_channels),
            nn.SiLU(),
            nn.Conv2d(base_channels, out_channels, 3, padding=1)
        )
    
    def _make_conv_block(self, in_ch, out_ch):
        return nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.GroupNorm(min(32, max(1, out_ch//4)), out_ch),
            nn.SiLU(),
            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.GroupNorm(min(32, max(1, out_ch//4)), out_ch),
            nn.SiLU()
        )
    
    def _make_down_block(self, in_ch, out_ch):
        return nn.Sequential(
            nn.MaxPool2d(2),
            self._make_conv_block(in_ch, out_ch)
        )
    
    def get_time_embedding(self, timesteps):
        half_dim = self.time_embed_dim // 2
        embeddings = math.log(10000) / (half_dim - 1)
        embeddings = torch.exp(torch.arange(half_dim, device=timesteps.device) * -embeddings)
        embeddings = timesteps[:, None] * embeddings[None, :]
        embeddings = torch.cat([torch.sin(embeddings), torch.cos(embeddings)], dim=1)
        return self.time_embed(embeddings)
    
    def forward(self, x, timesteps, attributes):
        t_emb = self.get_time_embedding(timesteps)
        attr_emb = self.attr_embed(attributes)
        
        combined_emb = t_emb + attr_emb
        
        x = self.conv_in(x)
        skip_connections = [x]
        
        for down_block in self.down_blocks:
            x = down_block(x)
            skip_connections.append(x)
        
        attr_spatial = combined_emb.unsqueeze(-1).unsqueeze(-1)
        attr_spatial = attr_spatial.expand(-1, -1, x.shape[2], x.shape[3])
        x = torch.cat([x, attr_spatial], dim=1)
        
        x = self.mid_block(x)
        
        skip_connections = skip_connections[:-1]
        skip_connections = skip_connections[::-1]
        
        for i, (up_block, skip) in enumerate(zip(self.up_blocks, skip_connections)):
            x = up_block[0](x)
            
            if x.shape[2:] != skip.shape[2:]:
                x = F.interpolate(x, size=skip.shape[2:], mode='bilinear', align_corners=False)
            
            x = torch.cat([x, skip], dim=1)
            x = up_block[1](x)
        
        return self.conv_out(x)


class CartoonifyDiffusionPipeline:
    def __init__(self, model_path=None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.noise_scheduler = None
        self.mp_extractor = OptimizedMediaPipeExtractor()
        if model_path:
            self.load_model(model_path)
    
    @classmethod
    def from_pretrained(cls, model_path):
        pipeline = cls()
        pipeline.load_model(model_path)
        return pipeline
    
    def load_model(self, model_path):
        try:
            model_file = hf_hub_download(
                repo_id=model_path,
                filename="image_to_cartoonify.pt",
                repo_type="model"
            )
            
            checkpoint = torch.load(model_file, map_location=self.device)
            
            self.model = OptimizedConditionedUNet(
                in_channels=3,
                out_channels=3,
                attr_dim=18,
                base_channels=64
            ).to(self.device)
            
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.eval()
            
            self.noise_scheduler = DDPMScheduler(
                num_train_timesteps=1000,
                beta_start=0.00085,
                beta_end=0.012,
                beta_schedule="scaled_linear",
                prediction_type="epsilon"
            )
            
            print(f"Model loaded successfully on {self.device}!")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    def __call__(self, image_path_or_pil):
        if self.model is None:
            raise ValueError("Model not loaded. Use from_pretrained() method first.")
        
        try:
            if isinstance(image_path_or_pil, str):
                image = Image.open(image_path_or_pil).convert('RGB')
            elif isinstance(image_path_or_pil, Image.Image):
                image = image_path_or_pil.convert('RGB')
            else:
                raise ValueError("Input must be a file path or PIL Image")
            
            image = image.resize((256, 256))
            image_np = np.array(image)
            
            features = self.mp_extractor.extract_features(image_np)
            features = features.unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                generated_image = torch.randn(1, 3, 256, 256).to(self.device)
                
                num_inference_steps = 25 if self.device.type == 'cuda' else 15
                self.noise_scheduler.set_timesteps(num_inference_steps)
                
                for i, t in enumerate(self.noise_scheduler.timesteps):
                    timesteps = torch.full((1,), t, device=self.device).long()
                    noise_pred = self.model(generated_image, timesteps, features)
                    generated_image = self.noise_scheduler.step(noise_pred, t, generated_image).prev_sample
                
                generated_image = (generated_image / 2 + 0.5).clamp(0, 1)
                generated_image = generated_image.cpu().squeeze(0).permute(1, 2, 0).numpy()
                generated_image = (generated_image * 255).astype(np.uint8)
                
                return Image.fromarray(generated_image)
                
        except Exception as e:
            print(f"Error processing image: {e}")
            raise
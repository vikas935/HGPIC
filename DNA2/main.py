#!/usr/bin/env python3
"""
FastAPI Backend for Gesture-Controlled 3D DNA Model Explorer
===========================================================
Provides API endpoints for:
- DNA sequence generation and validation
- Gesture processing and analysis
- Real-time configuration management
- Educational content about DNA structure

Dependencies:
pip install fastapi uvicorn websockets opencv-python numpy mediapipe
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import json
import numpy as np
import cv2
import base64
from typing import List, Dict, Optional
from pydantic import BaseModel
import asyncio
from datetime import datetime
import logging
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI(
    title="DNA Explorer API",
    description="Backend for Gesture-Controlled 3D DNA Model Explorer",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Models
class DNABase(BaseModel):
    """DNA base with position and properties"""
    base_type: str  # A, T, G, C
    position: List[float]  # [x, y, z]
    strand: int  # 1 or 2
    index: int
    pair_index: Optional[int] = None

class DNASequence(BaseModel):
    """Complete DNA sequence with metadata"""
    sequence: str
    length: int
    bases: List[DNABase]
    gc_content: float
    melting_temperature: float
    complementary_sequence: str

class GestureData(BaseModel):
    """Hand gesture data from MediaPipe"""
    landmarks: List[List[float]]  # Hand landmark coordinates
    gesture_type: str
    confidence: float
    timestamp: datetime

class VisualizationConfig(BaseModel):
    """Configuration for DNA visualization"""
    show_bonds: bool = False
    show_labels: bool = False
    show_backbone: bool = True
    show_atoms: bool = False
    animation_speed: float = 1.0
    helix_radius: float = 2.5
    base_pair_distance: float = 0.34
    rotation_speed: float = 0.005

# Global state
active_connections: List[WebSocket] = []
current_config = VisualizationConfig()
dna_data = None

# DNA utility functions
class DNAUtilities:
    """Utility functions for DNA sequence manipulation and analysis"""
    
    @staticmethod
    def generate_random_sequence(length: int = 20) -> str:
        """Generate a random DNA sequence"""
        bases = ['A', 'T', 'G', 'C']
        return ''.join(random.choices(bases, k=length))
    
    @staticmethod
    def get_complement(sequence: str) -> str:
        """Get complementary DNA sequence"""
        complement_map = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}
        return ''.join(complement_map.get(base, 'N') for base in sequence.upper())
    
    @staticmethod
    def calculate_gc_content(sequence: str) -> float:
        """Calculate GC content percentage"""
        gc_count = sequence.upper().count('G') + sequence.upper().count('C')
        return (gc_count / len(sequence)) * 100 if sequence else 0
    
    @staticmethod
    def calculate_melting_temperature(sequence: str) -> float:
        """Estimate melting temperature using Wallace rule (simplified)"""
        at_count = sequence.upper().count('A') + sequence.upper().count('T')
        gc_count = sequence.upper().count('G') + sequence.upper().count('C')
        return (at_count * 2) + (gc_count * 4)
    
    @staticmethod
    def generate_3d_coordinates(sequence: str, helix_radius: float = 2.5, 
                               base_pair_distance: float = 0.34) -> List[DNABase]:
        """Generate 3D coordinates for DNA bases"""
        bases = []
        complement_sequence = DNAUtilities.get_complement(sequence)
        total_pairs = len(sequence)
        
        for i, (base1, base2) in enumerate(zip(sequence, complement_sequence)):
            # Calculate helix positions
            angle = (i / total_pairs) * np.pi * 4
            y = (i - total_pairs / 2) * base_pair_distance
            
            # Strand 1 position
            x1 = helix_radius * np.cos(angle)
            z1 = helix_radius * np.sin(angle)
            
            # Strand 2 position (opposite side)
            x2 = helix_radius * np.cos(angle + np.pi)
            z2 = helix_radius * np.sin(angle + np.pi)
            
            # Create base objects
            base1_obj = DNABase(
                base_type=base1,
                position=[float(x1), float(y), float(z1)],
                strand=1,
                index=i,
                pair_index=i
            )
            
            base2_obj = DNABase(
                base_type=base2,
                position=[float(x2), float(y), float(z2)],
                strand=2,
                index=i,
                pair_index=i
            )
            
            bases.extend([base1_obj, base2_obj])
        
        return bases

class GestureProcessor:
    """Process and analyze hand gestures from MediaPipe"""
    
    @staticmethod
    def detect_gesture_type(landmarks: List[List[float]]) -> Dict:
        """Detect gesture type from hand landmarks"""
        if len(landmarks) != 21:
            return {"type": "unknown", "confidence": 0.0}
        
        # Convert to numpy array for easier processing
        points = np.array(landmarks)
        
        # Get key landmark indices
        thumb_tip = points[4]
        thumb_pip = points[3]
        index_tip = points[8]
        index_pip = points[6]
        middle_tip = points[12]
        middle_pip = points[10]
        ring_tip = points[16]
        ring_pip = points[14]
        pinky_tip = points[20]
        pinky_pip = points[18]
        
        # Check finger extensions
        is_thumb_up = thumb_tip[0] > thumb_pip[0]  # Simplified thumb check
        is_index_up = index_tip[1] < index_pip[1]
        is_middle_up = middle_tip[1] < middle_pip[1]
        is_ring_up = ring_tip[1] < ring_pip[1]
        is_pinky_up = pinky_tip[1] < pinky_pip[1]
        
        extended_fingers = [is_thumb_up, is_index_up, is_middle_up, is_ring_up, is_pinky_up]
        num_extended = sum(extended_fingers)
        
        # Calculate pinch distance
        pinch_distance = np.linalg.norm(thumb_tip - index_tip)
        
        # Gesture classification
        if pinch_distance < 0.05:
            return {"type": "pinch", "confidence": 0.9, "distance": float(pinch_distance)}
        elif num_extended == 1 and is_index_up:
            return {"type": "point", "confidence": 0.8, "position": index_tip.tolist()}
        elif num_extended == 5:
            return {"type": "open_hand", "confidence": 0.8}
        elif num_extended == 0:
            return {"type": "fist", "confidence": 0.8}
        else:
            return {"type": "unknown", "confidence": 0.3}
    
    @staticmethod
    def calculate_rotation_from_point(position: List[float]) -> Dict[str, float]:
        """Calculate rotation values from pointing gesture"""
        x, y = position[0], position[1]
        rotation_y = (x - 0.5) * 360  # Horizontal rotation
        rotation_x = (y - 0.5) * 180  # Vertical rotation
        return {"rotation_x": rotation_x, "rotation_y": rotation_y}
    
    @staticmethod
    def calculate_zoom_from_pinch(distance: float) -> float:
        """Calculate zoom level from pinch distance"""
        return max(0.5, min(3.0, 2.0 - distance * 10))

# API Endpoints

@app.get("/")
async def root():
    """Serve the main HTML file"""
    return FileResponse("index.html")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_connections": len(active_connections)
    }

@app.get("/api/dna/random/{length}")
async def generate_random_dna(length: int = 20) -> DNASequence:
    """Generate a random DNA sequence with analysis"""
    if length < 1 or length > 100:
        raise HTTPException(status_code=400, detail="Length must be between 1 and 100")
    
    sequence = DNAUtilities.generate_random_sequence(length)
    complement = DNAUtilities.get_complement(sequence)
    gc_content = DNAUtilities.calculate_gc_content(sequence)
    melting_temp = DNAUtilities.calculate_melting_temperature(sequence)
    bases = DNAUtilities.generate_3d_coordinates(sequence)
    
    dna_sequence = DNASequence(
        sequence=sequence,
        length=length,
        bases=bases,
        gc_content=gc_content,
        melting_temperature=melting_temp,
        complementary_sequence=complement
    )
    
    global dna_data
    dna_data = dna_sequence
    
    return dna_sequence

@app.post("/api/dna/validate")
async def validate_dna_sequence(sequence: str) -> Dict:
    """Validate a DNA sequence"""
    valid_bases = set('ATGC')
    sequence = sequence.upper().strip()
    
    if not sequence:
        raise HTTPException(status_code=400, detail="Sequence cannot be empty")
    
    invalid_bases = set(sequence) - valid_bases
    if invalid_bases:
        return {
            "valid": False,
            "errors": [f"Invalid bases found: {', '.join(invalid_bases)}"],
            "valid_bases": list(valid_bases)
        }
    
    return {
        "valid": True,
        "length": len(sequence),
        "gc_content": DNAUtilities.calculate_gc_content(sequence),
        "complement": DNAUtilities.get_complement(sequence)
    }

@app.get("/api/dna/info/{base}")
async def get_base_info(base: str) -> Dict:
    """Get detailed information about a DNA base"""
    base = base.upper()
    
    base_info = {
        'A': {
            "name": "Adenine",
            "type": "Purine",
            "formula": "C₅H₅N₅",
            "pairs_with": "Thymine",
            "bonds": 2,
            "color": "#ff6b6b",
            "description": "A purine base that pairs with thymine through two hydrogen bonds."
        },
        'T': {
            "name": "Thymine",
            "type": "Pyrimidine", 
            "formula": "C₅H₆N₂O₂",
            "pairs_with": "Adenine",
            "bonds": 2,
            "color": "#ffd93d",
            "description": "A pyrimidine base that pairs with adenine through two hydrogen bonds."
        },
        'G': {
            "name": "Guanine",
            "type": "Purine",
            "formula": "C₅H₅N₅O", 
            "pairs_with": "Cytosine",
            "bonds": 3,
            "color": "#6bcf7f",
            "description": "A purine base that pairs with cytosine through three hydrogen bonds."
        },
        'C': {
            "name": "Cytosine",
            "type": "Pyrimidine",
            "formula": "C₄H₅N₃O",
            "pairs_with": "Guanine", 
            "bonds": 3,
            "color": "#4dabf7",
            "description": "A pyrimidine base that pairs with guanine through three hydrogen bonds."
        }
    }
    
    if base not in base_info:
        raise HTTPException(status_code=404, detail=f"Base '{base}' not found")
    
    return base_info[base]

@app.get("/api/config")
async def get_config() -> VisualizationConfig:
    """Get current visualization configuration"""
    return current_config

@app.post("/api/config")
async def update_config(config: VisualizationConfig) -> Dict:
    """Update visualization configuration"""
    global current_config
    current_config = config
    
    # Broadcast config update to all connected clients
    message = {
        "type": "config_update",
        "config": config.dict(),
        "timestamp": datetime.now().isoformat()
    }
    
    await broadcast_to_clients(json.dumps(message))
    
    return {"status": "success", "message": "Configuration updated"}

@app.post("/api/gesture/process")
async def process_gesture(gesture_data: GestureData) -> Dict:
    """Process hand gesture data"""
    try:
        # Detect gesture type
        gesture_info = GestureProcessor.detect_gesture_type(gesture_data.landmarks)
        
        # Calculate transformations based on gesture
        transformations = {}
        
        if gesture_info["type"] == "point":
            transformations = GestureProcessor.calculate_rotation_from_point(
                gesture_info["position"]
            )
        elif gesture_info["type"] == "pinch":
            transformations["zoom"] = GestureProcessor.calculate_zoom_from_pinch(
                gesture_info["distance"]
            )
        elif gesture_info["type"] == "fist":
            transformations = {"reset": True}
        
        result = {
            "gesture": gesture_info,
            "transformations": transformations,
            "timestamp": datetime.now().isoformat()
        }
        
        # Broadcast to connected clients
        await broadcast_to_clients(json.dumps({
            "type": "gesture_update",
            "data": result
        }))
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing gesture: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket connection manager
async def broadcast_to_clients(message: str):
    """Broadcast message to all connected WebSocket clients"""
    if active_connections:
        disconnected = []
        for connection in active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            active_connections.remove(connection)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Send initial configuration
        await websocket.send_text(json.dumps({
            "type": "config_update",
            "config": current_config.dict(),
            "timestamp": datetime.now().isoformat()
        }))
        
        # Send current DNA data if available
        if dna_data:
            await websocket.send_text(json.dumps({
                "type": "dna_data",
                "data": dna_data.dict(),
                "timestamp": datetime.now().isoformat()
            }))
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message["type"] == "gesture_data":
                gesture_data = GestureData(**message["data"])
                result = await process_gesture(gesture_data)
                
                await websocket.send_text(json.dumps({
                    "type": "gesture_result",
                    "data": result
                }))
            
            elif message["type"] == "config_update":
                config = VisualizationConfig(**message["data"])
                await update_config(config)
    
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Active connections: {len(active_connections)}")
    
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        if websocket in active_connections:
            active_connections.remove(websocket)

# Educational endpoints
@app.get("/api/education/dna-facts")
async def get_dna_facts() -> List[Dict]:
    """Get interesting facts about DNA"""
    return [
        {
            "title": "DNA Structure",
            "fact": "DNA has a double helix structure, like a twisted ladder, discovered by Watson, Crick, Franklin, and Wilkins.",
            "category": "structure"
        },
        {
            "title": "Base Pairing",
            "fact": "Adenine always pairs with Thymine (2 H-bonds), and Guanine always pairs with Cytosine (3 H-bonds).",
            "category": "bonding"
        },
        {
            "title": "Human DNA",
            "fact": "Human DNA contains about 3 billion base pairs and would stretch about 2 meters if unwound from a single cell.",
            "category": "biology"
        },
        {
            "title": "Genetic Code",
            "fact": "The sequence of DNA bases determines the genetic instructions for all living organisms.",
            "category": "genetics"
        }
    ]

@app.get("/api/education/molecular-components")
async def get_molecular_components() -> Dict:
    """Get information about DNA molecular components"""
    return {
        "sugar_phosphate_backbone": {
            "description": "The structural framework of DNA, alternating sugar (deoxyribose) and phosphate groups",
            "function": "Provides structural stability and protection for the bases"
        },
        "nitrogenous_bases": {
            "description": "Four types of bases (A, T, G, C) that carry genetic information",
            "function": "Store genetic information through their sequence"
        },
        "hydrogen_bonds": {
            "description": "Weak bonds between complementary base pairs",
            "function": "Hold the two DNA strands together while allowing separation during replication"
        },
        "major_minor_grooves": {
            "description": "Spiral grooves in the DNA double helix",
            "function": "Provide binding sites for proteins that regulate gene expression"
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    print("Starting DNA Explorer API Server...")
    print("=" * 50)
    print("🧬 DNA Explorer Backend")
    print("📡 WebSocket support for real-time gesture control")
    print("🔬 Educational content and molecular data")
    print("🎮 Gesture processing and analysis")
    print()
    print("Endpoints:")
    print("• Web Interface: http://localhost:8000")
    print("• API Documentation: http://localhost:8000/api/docs")
    print("• WebSocket: ws://localhost:8000/ws")
    print()
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
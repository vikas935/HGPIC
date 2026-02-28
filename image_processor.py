from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
from PIL import Image
import io

app = Flask(__name__)
CORS(app)

def create_depth_map(image_array):
    """Convert image to depth map for 3D effect"""
    # Convert to grayscale
    gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    
    # Apply edge detection for depth
    edges = cv2.Canny(gray, 100, 200)
    
    # Create depth map (edges = high depth, smooth areas = low depth)
    depth = cv2.GaussianBlur(edges, (5, 5), 0)
    depth = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX)
    
    return depth

@app.route('/')
def home():
    return jsonify({"status": "Image Processor Server Running", "port": 5002})

@app.route('/api/convert-to-3d', methods=['POST'])
def convert_to_3d():
    """Convert uploaded image to 3D data"""
    try:
        # Get image data from request
        data = request.json
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'success': False, 'error': 'No image provided'}), 400
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data.split(',')[1])
        image = Image.open(io.BytesIO(image_bytes))
        image_array = np.array(image)
        
        # Create depth map
        depth_map = create_depth_map(image_array)
        
        # Convert depth map to base64
        _, buffer = cv2.imencode('.png', depth_map)
        depth_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Prepare 3D points
        height, width = depth_map.shape
        points = []
        
        # Sample points for 3D mesh (every 10th pixel for performance)
        for y in range(0, height, 10):
            for x in range(0, width, 10):
                depth_value = depth_map[y, x] / 255.0
                points.append({
                    'x': x - width/2,
                    'y': height/2 - y,
                    'z': depth_value * 50  # Scale depth
                })
        
        return jsonify({
            'success': True,
            'depth_map': f'data:image/png;base64,{depth_base64}',
            'points': points[:1000],  # Limit points for performance
            'original_size': {'width': width, 'height': height}
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Image Processor Server...")
    print("📡 http://localhost:5002")
    print("🎯 Advanced 3D conversion with OpenCV")
    print("=" * 50)
    app.run(debug=True, port=5002, host='0.0.0.0')

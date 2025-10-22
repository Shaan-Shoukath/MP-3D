"""
Hand-Controlled Music Player with Spotify Integration
======================================================

This application provides a gesture-based music player interface using:
- Spotify Web API for music playback and metadata
- MediaPipe for hand tracking and gesture recognition
- Pygame for rendering 3D graphics
- OpenCV for camera input processing

Features:
- Left hand controls a 3D rotating cube (visualizer)
- Right hand controls a puck-shaped music controller
- Screen is split into two zones for reliable hand detection
- Gesture-based controls: volume, track navigation
- Real-time Spotify playback with song/artist display
- Animated strings inside cube when music is playing

Author: Shaan
Date: October 2025
"""

# Core libraries for computer vision, hand tracking, graphics, and audio
import cv2              # OpenCV - Camera input and image processing
import mediapipe as mp  # Google MediaPipe - Hand landmark detection
import numpy as np      # NumPy - Mathematical operations and vector calculations
import pygame           # Pygame - Graphics rendering
import sys              # System operations - Clean exit handling
import math             # Math operations - Trigonometry for 3D rotations
import time             # Time operations - Animation timing
import random           # Random - String animation patterns

# Spotify integration
try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
    from spotify_config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI
    SPOTIFY_AVAILABLE = True
except ImportError:
    print("⚠️  Spotipy not installed. Install with: pip install spotipy")
    SPOTIFY_AVAILABLE = False
except Exception as e:
    print(f"⚠️  Spotify config error: {e}")
    SPOTIFY_AVAILABLE = False

# ================== MUSIC MANAGER MODULE ================== #
class MusicManager:
    """
    Music Playback Manager - Spotify Integration
    
    Manages Spotify playback, metadata fetching, and playback state
    
    Attributes:
        sp (Spotipy): Spotify API client
        current_song (dict): Current track metadata
        is_playing (bool): Playback state
    """
    def __init__(self):
        """Initialize Spotify connection"""
        self.sp = None
        self.current_song = None
        self.is_playing = False
        self.last_update = 0
        
        if SPOTIFY_AVAILABLE:
            try:
                self.connect_spotify()
            except Exception as e:
                print(f"❌ Spotify connection failed: {e}")
                print("💡 Make sure Spotify app is open and playing a track")
    
    def connect_spotify(self):
        """
        Initialize Spotify Web API connection
        
        Requires:
        - Spotify app open and playing
        - Valid credentials in spotify_config.py
        - Spotify Premium account
        """
        print("🔄 Connecting to Spotify...")
        
        scope = "user-read-playback-state,user-modify-playback-state,user-read-currently-playing"
        
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope=scope,
            open_browser=True
        ))
        
        # Verify connection
        current = self.sp.current_playback()
        if current and current.get('item'):
            self.is_playing = current.get('is_playing', False)
            self.current_song = self.get_spotify_metadata()
            device_name = current.get('device', {}).get('name', 'Unknown')
            print(f"✅ Connected to Spotify")
            print(f"📱 Device: {device_name}")
            print(f"🎵 Playing: {self.current_song['name']} - {self.current_song['artist']}")
        else:
            print("⚠️  No active playback. Please start playing a track in Spotify.")
            self.is_playing = False
    
    def update_playback_state(self):
        """Update current playback information from Spotify"""
        if not self.sp:
            return
        
        # Throttle updates to every 1 second
        current_time = time.time()
        if current_time - self.last_update < 1.0:
            return
        
        self.last_update = current_time
        
        try:
            current = self.sp.current_playback()
            if current and current.get('item'):
                self.is_playing = current.get('is_playing', False)
                self.current_song = self.get_spotify_metadata()
        except Exception as e:
            print(f"⚠️  Playback update error: {e}")
    
    def get_spotify_metadata(self):
        """
        Fetch current track metadata from Spotify
        
        Returns:
            dict: Track info (name, artist, album, duration, is_playing)
        """
        if not self.sp:
            return {'name': 'No Spotify', 'artist': 'Not Connected', 'is_playing': False}
        
        try:
            current = self.sp.current_playback()
            if current and current.get('item'):
                item = current['item']
                return {
                    'name': item['name'],
                    'artist': item['artists'][0]['name'],
                    'album': item['album']['name'],
                    'duration': item['duration_ms'],
                    'progress': current.get('progress_ms', 0),
                    'is_playing': current.get('is_playing', False)
                }
        except Exception as e:
            print(f"⚠️  Metadata fetch error: {e}")
        
        return {'name': 'Unknown', 'artist': 'Unknown', 'is_playing': False}
    
    def next_track(self):
        """Skip to next track (Spotify)"""
        if self.sp:
            try:
                self.sp.next_track()
                print("⏭️  Next track")
                time.sleep(0.3)  # Wait for Spotify to update
                self.update_playback_state()
            except Exception as e:
                print(f"❌ Next track error: {e}")
    
    def prev_track(self):
        """Go to previous track (Spotify)"""
        if self.sp:
            try:
                self.sp.previous_track()
                print("⏮️  Previous track")
                time.sleep(0.3)  # Wait for Spotify to update
                self.update_playback_state()
            except Exception as e:
                print(f"❌ Previous track error: {e}")
    
    def volume_up(self):
        """Increase volume by 10%"""
        if self.sp:
            try:
                current = self.sp.current_playback()
                if current:
                    current_vol = current['device']['volume_percent']
                    new_vol = min(current_vol + 10, 100)
                    self.sp.volume(new_vol)
                    print(f"🔊 Volume: {new_vol}%")
            except Exception as e:
                print(f"❌ Volume up error: {e}")
    
    def volume_down(self):
        """Decrease volume by 10%"""
        if self.sp:
            try:
                current = self.sp.current_playback()
                if current:
                    current_vol = current['device']['volume_percent']
                    new_vol = max(current_vol - 10, 0)
                    self.sp.volume(new_vol)
                    print(f"🔉 Volume: {new_vol}%")
            except Exception as e:
                print(f"❌ Volume down error: {e}")
    
    def get_current_song_name(self):
        """Get current song name"""
        if self.current_song:
            return self.current_song.get('name', 'Unknown')
        return 'No Track'
    
    def get_current_artist_name(self):
        """Get current artist name"""
        if self.current_song:
            return self.current_song.get('artist', 'Unknown')
        return 'No Artist'

# ================== AUDIO SETUP ================== #
# Initialize Spotify music manager
music_manager = MusicManager()

# ================== MEDIAPIPE SETUP ================== #
# MediaPipe Hands - Google's ML model for hand landmark detection
mp_hands = mp.solutions.hands

# Initialize hand detector
# max_num_hands=2: Detect up to 2 hands (left for cube, right for puck)
# min_detection_confidence=0.7: Confidence threshold (0.0-1.0)
hands_detector = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)

# Drawing utility for visualizing hand skeleton on camera feed
mp_draw = mp.solutions.drawing_utils

# ================== PYGAME WINDOW SETUP ================== #
pygame.init()  # Initialize all Pygame modules

# Screen dimensions (720p resolution for smooth performance)
WIDTH, HEIGHT = 1280, 720

# Create display window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hand-Controlled MP3 Player")

# Clock for controlling frame rate (30 FPS target)
clock = pygame.time.Clock()

# ================== 3D CUBE SETUP ================== #
# The cube is a music visualizer controlled by left hand rotation

# Cube geometry: 8 vertices in 3D space (unit cube from -1 to 1)
cube_vertices = [
    [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],  # Back face (4 vertices)
    [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]       # Front face (4 vertices)
]

# Cube wireframe: 12 edges connecting vertices
# Each edge is a tuple of (start_vertex_index, end_vertex_index)
cube_edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),  # Back face edges
    (4, 5), (5, 6), (6, 7), (7, 4),  # Front face edges
    (0, 4), (1, 5), (2, 6), (3, 7)   # Connecting edges between front and back
]

# Cube faces: 6 faces, each defined by 4 vertex indices (clockwise order)
# Used for rendering translucent colored polygons
cube_faces = [
    [0, 1, 2, 3],  # Back face (index 0)
    [4, 5, 6, 7],  # Front face (index 1) - displays song name
    [0, 1, 5, 4],  # Bottom face (index 2) - LOCKED (doesn't rotate)
    [2, 3, 7, 6],  # Top face (index 3)
    [0, 3, 7, 4],  # Left face (index 4)
    [1, 2, 6, 5]   # Right face (index 5)
]

# Face colors with transparency (Red, Green, Blue, Alpha)
# Alpha channel makes faces translucent for see-through effect
face_colors = [
    (255, 50, 80, 80),   # Back - Bright red, semi-transparent
    (255, 50, 80, 80),   # Front - Bright red (song name displayed here)
    (180, 30, 50, 100),  # Bottom - Dark red, slightly more opaque (locked base)
    (255, 50, 80, 80),   # Top - Bright red
    (255, 50, 80, 80),   # Left - Bright red
    (255, 50, 80, 80)    # Right - Bright red
]

# Cube state variables
cube_rotation = [0, 0, 0]        # Current rotation angles [X, Y, Z] in radians
smoothed_rotation = [0, 0, 0]    # Smoothed rotation (eliminates jitter)
cube_position = [200, 200]       # Screen position [X, Y] pixels
smoothed_position = [200, 200]   # Smoothed position (follows hand smoothly)

# Cube tuning parameters
SMOOTHING_FACTOR = 0.08     # Rotation smoothing (0.0-1.0): Lower = smoother, higher = more responsive
POSITION_SMOOTHING = 0.15   # Position smoothing: Controls how fast cube follows hand
ROTATION_SENSITIVITY = 1.2  # Rotation multiplier: Allows full 360° rotation range

# ================== PUCK CONTROLLER STATE ================== #
# The puck is a gesture-controlled music interface (right hand)

# Puck position on screen (starts at right side)
puck_position = [WIDTH - 200, HEIGHT // 2]         # Current position [X, Y]
smoothed_puck_position = [WIDTH - 200, HEIGHT // 2] # Smoothed position (follows hand)

# Puck appearance
puck_radius = 90  # Radius in pixels (3D circular controller)

# Gesture control state
active_control = None         # Currently active gesture ("UP", "DOWN", "LEFT", "RIGHT", or None)
last_gesture_time = 0         # Timestamp of last gesture (prevents rapid repeated triggers)
previous_hand_position = None # Previous palm position for movement detection

# Puck tuning parameters
GESTURE_COOLDOWN = 0.5          # Minimum seconds between gestures (prevents accidental spam)
PUCK_POSITION_SMOOTHING = 0.15  # Position smoothing factor (0.0-1.0)
GESTURE_THRESHOLD = 0.12        # Minimum hand extension to trigger gesture (0.0-1.0)
MOVEMENT_THRESHOLD = 0.05       # Minimum hand movement to count as gesture (not static)

# ================== ANIMATED STRINGS INSIDE CUBE ================== #
# Strings that flow through the cube when music is playing
class AnimatedString:
    """Animated line/string that flows through the cube"""
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset string to random starting position"""
        # Random starting position inside cube (-1 to 1 range)
        self.start = [random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)]
        self.end = [random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)]
        
        # Animation progress (0.0 to 1.0)
        self.progress = 0.0
        
        # Animation speed (random variation)
        self.speed = random.uniform(0.01, 0.03)
        
        # Color (vibrant colors)
        colors = [
            (255, 100, 100),  # Red
            (100, 255, 100),  # Green
            (100, 100, 255),  # Blue
            (255, 255, 100),  # Yellow
            (255, 100, 255),  # Magenta
            (100, 255, 255),  # Cyan
        ]
        self.color = random.choice(colors)
    
    def update(self):
        """Update animation progress"""
        self.progress += self.speed
        if self.progress >= 1.0:
            self.reset()  # Loop animation
    
    def get_current_points(self):
        """Get current line endpoints based on progress"""
        # Interpolate points along the path
        t = self.progress
        current_start = [
            self.start[0] * (1 - t) + self.end[0] * t,
            self.start[1] * (1 - t) + self.end[1] * t,
            self.start[2] * (1 - t) + self.end[2] * t
        ]
        
        # End point trails behind start
        trail_t = max(0, t - 0.3)
        current_end = [
            self.start[0] * (1 - trail_t) + self.end[0] * trail_t,
            self.start[1] * (1 - trail_t) + self.end[1] * trail_t,
            self.start[2] * (1 - trail_t) + self.end[2] * trail_t
        ]
        
        return current_start, current_end

# Create multiple animated strings
animated_strings = [AnimatedString() for _ in range(8)]  # 8 strings flowing through cube

def get_hand_rotation(landmarks):
    """
    Calculate 3D hand rotation angles from MediaPipe hand landmarks
    
    Uses wrist, middle finger base, and index finger base to determine
    hand orientation in 3D space. Returns angles suitable for rotating
    the 3D cube visualization.
    
    Args:
        landmarks: MediaPipe hand landmarks (21 points per hand)
                   Key landmarks used:
                   - 0: Wrist (base point)
                   - 5: Index finger base (side reference)
                   - 9: Middle finger base (forward reference)
    
    Returns:
        tuple: (angle_x, angle_y, angle_z) rotation angles in radians
               - angle_x: Up/down tilt (currently locked to 0)
               - angle_y: Left/right rotation (main control axis)
               - angle_z: Twist rotation (currently locked to 0)
    """
    # Extract 3D positions of key landmarks
    wrist = np.array([landmarks[0].x, landmarks[0].y, landmarks[0].z])
    middle_base = np.array([landmarks[9].x, landmarks[9].y, landmarks[9].z])
    index_base = np.array([landmarks[5].x, landmarks[5].y, landmarks[5].z])
    
    # Calculate directional vectors from wrist to finger bases
    forward = middle_base - wrist  # Vector pointing forward (middle finger direction)
    side = index_base - wrist      # Vector pointing sideways (index finger direction)
    
    # Normalize vectors to unit length (prevents magnitude from affecting angles)
    # Add small epsilon (0.0001) to avoid division by zero
    forward = forward / (np.linalg.norm(forward) + 0.0001)
    side = side / (np.linalg.norm(side) + 0.0001)
    
    # Calculate rotation angles using trigonometry
    
    # Y-axis rotation (horizontal left-right): Primary control axis
    # Uses arctan2 for full 360° range, multiplied by 1.8 for increased sensitivity
    angle_y = np.arctan2(forward[0], -forward[2]) * 1.8
    
    # X-axis rotation (vertical up-down tilt): Currently locked
    # Multiplied by 0.3 for minimal influence (stability)
    angle_x = np.arctan2(forward[1], np.sqrt(forward[0]**2 + forward[2]**2)) * 0.3
    
    # Z-axis rotation (twist): Locked to 0 for clean horizontal-only rotation
    angle_z = 0
    
    return angle_x, angle_y, angle_z

def detect_hand_direction(landmarks, previous_position=None):
    """
    Detect directional hand gestures (UP/DOWN/LEFT/RIGHT) for puck controls
    
    Analyzes hand landmark positions to determine if user is making a
    directional gesture. Requires actual hand movement to prevent false
    triggers when hand is stationary.
    
    Gesture Mappings:
        UP    (↑): Volume increase (index finger points up)
        DOWN  (↓): Volume decrease (index finger points down)
        LEFT  (←): Previous track (index finger points left)
        RIGHT (→): Next track (index finger points right)
    
    Args:
        landmarks: MediaPipe hand landmarks (21 points)
        previous_position: Previous palm position for movement detection
    
    Returns:
        tuple: (detected_direction, current_palm_position)
               - detected_direction: "UP"/"DOWN"/"LEFT"/"RIGHT" or None
               - current_palm_position: NumPy array [x, y] for next frame
    
    Algorithm:
        1. Calculate vector from wrist to index finger tip
        2. Check if hand has moved (not static)
        3. Determine dominant direction (horizontal vs vertical)
        4. Apply threshold to confirm intentional gesture
    """
    # Extract key landmark positions (normalized 0.0-1.0 coordinates)
    wrist = np.array([landmarks[0].x, landmarks[0].y])       # Landmark 0: Wrist base
    index_tip = np.array([landmarks[8].x, landmarks[8].y])   # Landmark 8: Index finger tip
    
    # Get current palm center position (middle finger base)
    palm_center = np.array([landmarks[9].x, landmarks[9].y]) # Landmark 9: Palm center
    
    # Movement detection: Prevent false triggers from stationary hand
    if previous_position is not None:
        # Calculate Euclidean distance between current and previous palm position
        movement = np.linalg.norm(palm_center - previous_position)
        
        if movement < MOVEMENT_THRESHOLD:
            # Hand is too static - no gesture detected
            return None, palm_center
    
    # Calculate direction vector from wrist to index finger tip
    # This represents where the hand is "pointing"
    direction = index_tip - wrist
    
    # Analyze direction vector components
    abs_x = abs(direction[0])  # Horizontal component magnitude
    abs_y = abs(direction[1])  # Vertical component magnitude
    
    # Determine primary direction with strict thresholds
    # Require 1.5x dominance to avoid diagonal confusion
    detected_direction = None
    
    if abs_x > abs_y * 1.5:  # Horizontal movement is dominant
        if direction[0] > GESTURE_THRESHOLD:
            detected_direction = "RIGHT"  # Hand pointing right
        elif direction[0] < -GESTURE_THRESHOLD:
            detected_direction = "LEFT"   # Hand pointing left
            
    elif abs_y > abs_x * 1.5:  # Vertical movement is dominant
        if direction[1] > GESTURE_THRESHOLD:
            detected_direction = "DOWN"   # Hand pointing down
        elif direction[1] < -GESTURE_THRESHOLD:
            detected_direction = "UP"     # Hand pointing up
    
    # Return detected direction and current position for next frame comparison
    return detected_direction, palm_center

def draw_puck_controller(surface, center, radius, active_direction=None):
    """Draw an enhanced 3D circular puck-shaped music controller with 4 directional switches"""
    cx, cy = int(center[0]), int(center[1])
    
    # Create 3D effect with layered circles (depth illusion)
    # Bottom shadow layer (larger, softer)
    shadow_offset = 10
    shadow_surf = pygame.Surface((radius * 2 + 30, radius * 2 + 30), pygame.SRCALPHA)
    for i in range(3):
        alpha = 40 - i * 10
        pygame.draw.circle(shadow_surf, (0, 0, 0, alpha), 
                         (radius + 15, radius + 15 + shadow_offset), 
                         radius + 5 - i * 2)
    surface.blit(shadow_surf, (cx - radius - 15, cy - radius - 15))
    
    # Base layer (dark rim for depth)
    base_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(base_surf, (20, 20, 30, 200), (radius, radius), radius)
    surface.blit(base_surf, (cx - radius, cy - radius))
    
    # Middle layer (darker, recessed look with gradient)
    mid_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(mid_surf, (35, 35, 50, 190), (radius, radius), int(radius * 0.96))
    # Add subtle gradient
    pygame.draw.circle(mid_surf, (45, 45, 60, 160), 
                      (int(radius * 0.6), int(radius * 0.6)), 
                      int(radius * 0.85))
    surface.blit(mid_surf, (cx - radius, cy - radius))
    
    # Top layer (main puck body) - glossy translucent
    puck_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    # Main body with glass-like effect
    pygame.draw.circle(puck_surf, (55, 55, 80, 160), (radius, radius), int(radius * 0.92))
    # Glossy highlight
    pygame.draw.circle(puck_surf, (90, 90, 120, 120), 
                      (int(radius * 0.6), int(radius * 0.5)), 
                      int(radius * 0.7))
    # Inner glow
    pygame.draw.circle(puck_surf, (70, 70, 100, 100), 
                      (radius, radius), 
                      int(radius * 0.8))
    surface.blit(puck_surf, (cx - radius, cy - radius))
    
    # Outer rim (metallic edge with multiple layers)
    pygame.draw.circle(surface, (140, 140, 180, 220), (cx, cy), radius, 5)
    pygame.draw.circle(surface, (180, 180, 220, 180), (cx, cy), int(radius * 0.96), 2)
    pygame.draw.circle(surface, (100, 100, 140, 160), (cx, cy), int(radius * 0.92), 1)
    
    # Inner decorative ring
    pygame.draw.circle(surface, (80, 80, 110, 120), (cx, cy), int(radius * 0.75), 2)
    
    # Draw center circle (3D button effect with more detail)
    center_radius = int(radius * 0.28)
    # Shadow for center
    pygame.draw.circle(surface, (15, 15, 25, 150), (cx + 3, cy + 3), center_radius)
    # Main center button with gradient
    pygame.draw.circle(surface, (50, 50, 70, 220), (cx, cy), center_radius)
    pygame.draw.circle(surface, (70, 70, 95, 180), (cx, cy), int(center_radius * 0.9))
    # Glossy highlight
    pygame.draw.circle(surface, (120, 120, 160, 140), 
                      (cx - int(center_radius * 0.3), cy - int(center_radius * 0.3)), 
                      int(center_radius * 0.5))
    # Edge
    pygame.draw.circle(surface, (160, 160, 200, 120), (cx, cy), center_radius, 2)
    
    # Define control positions (UP, DOWN, LEFT, RIGHT)
    control_distance = radius * 0.62
    controls = {
        'UP': (cx, int(cy - control_distance)),
        'DOWN': (cx, int(cy + control_distance)),
        'LEFT': (int(cx - control_distance), cy),
        'RIGHT': (int(cx + control_distance), cy)
    }
    
    # Control symbols and colors (enhanced)
    control_info = {
        'UP': ('▲', (120, 255, 130)),      # Bright Green - Volume Up
        'DOWN': ('▼', (255, 120, 130)),    # Bright Red - Volume Down
        'LEFT': ('◄', (255, 210, 120)),    # Bright Orange - Previous Track
        'RIGHT': ('►', (120, 210, 255))    # Bright Blue - Next Track
    }
    
    # Draw each control button with enhanced 3D effect
    for direction, pos in controls.items():
        symbol, base_color = control_info[direction]
        
        # Highlight if active
        if active_direction == direction:
            color = (255, 255, 120, 250)  # Bright yellow when active
            btn_radius = 22
            glow_radius = 35
            # Add strong glow effect when active
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            for i in range(3):
                alpha = 70 - i * 20
                pygame.draw.circle(glow_surf, (*color[:3], alpha), 
                                 (glow_radius, glow_radius), glow_radius - i * 5)
            surface.blit(glow_surf, (pos[0] - glow_radius, pos[1] - glow_radius))
        else:
            color = (*base_color, 220)
            btn_radius = 18
        
        # Button shadow (multi-layer)
        for i in range(2):
            shadow_alpha = 100 - i * 30
            pygame.draw.circle(surface, (0, 0, 0, shadow_alpha), 
                             (pos[0] + 2 + i, pos[1] + 2 + i), btn_radius)
        
        # Main button (translucent with gradient)
        btn_surf = pygame.Surface((btn_radius * 2, btn_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(btn_surf, color, (btn_radius, btn_radius), btn_radius)
        # Inner lighter circle for depth
        pygame.draw.circle(btn_surf, (*color[:3], int(color[3] * 0.7)), 
                         (btn_radius, btn_radius), int(btn_radius * 0.8))
        surface.blit(btn_surf, (pos[0] - btn_radius, pos[1] - btn_radius))
        
        # Button edge/rim (glossy)
        pygame.draw.circle(surface, (240, 240, 255, 200), pos, btn_radius, 3)
        pygame.draw.circle(surface, (255, 255, 255, 150), pos, int(btn_radius * 0.95), 1)
        
        # Highlight for 3D effect (stronger)
        highlight_offset = int(btn_radius * 0.35)
        pygame.draw.circle(surface, (255, 255, 255, 140), 
                         (pos[0] - highlight_offset, pos[1] - highlight_offset), 
                         int(btn_radius * 0.45))
        
        # Draw symbol with better font
        font = pygame.font.SysFont('Arial', 20, bold=True)
        text = font.render(symbol, True, (255, 255, 255))
        text_rect = text.get_rect(center=pos)
        # Text shadow (double layer)
        shadow_text = font.render(symbol, True, (0, 0, 0))
        shadow_rect = shadow_text.get_rect(center=(pos[0] + 2, pos[1] + 2))
        shadow_text2 = font.render(symbol, True, (50, 50, 50))
        shadow_rect2 = shadow_text2.get_rect(center=(pos[0] + 1, pos[1] + 1))
        surface.blit(shadow_text, shadow_rect)
        surface.blit(shadow_text2, shadow_rect2)
        surface.blit(text, text_rect)
    
    # Draw labels with better styling
    label_font = pygame.font.SysFont('Arial', 10, bold=True)
    labels = {
        'UP': 'Vol+',
        'DOWN': 'Vol-',
        'LEFT': 'Prev',
        'RIGHT': 'Next'
    }
    
    for direction, label_text in labels.items():
        pos = controls[direction]
        label = label_font.render(label_text, True, (230, 230, 250))
        shadow_label = label_font.render(label_text, True, (20, 20, 30))
        label_rect = label.get_rect(center=(pos[0], pos[1] + 32))
        shadow_rect = shadow_label.get_rect(center=(pos[0] + 1, pos[1] + 33))
        surface.blit(shadow_label, shadow_rect)
        surface.blit(label, label_rect)
    
    return controls

def rotate_point(point, angles):
    """Rotate a 3D point by given angles (x, y, z)"""
    x, y, z = point
    rx, ry, rz = angles
    
    # Rotate around X axis
    y_new = y * math.cos(rx) - z * math.sin(rx)
    z_new = y * math.sin(rx) + z * math.cos(rx)
    y, z = y_new, z_new
    
    # Rotate around Y axis
    x_new = x * math.cos(ry) + z * math.sin(ry)
    z_new = -x * math.sin(ry) + z * math.cos(ry)
    x, z = x_new, z_new
    
    # Rotate around Z axis
    x_new = x * math.cos(rz) - y * math.sin(rz)
    y_new = x * math.sin(rz) + y * math.cos(rz)
    x, y = x_new, y_new
    
    return [x, y, z]

def project_3d_to_2d(point, scale=100, offset_x=200, offset_y=200):
    """Project 3D point to 2D screen coordinates"""
    # Simple orthographic projection
    x, y, z = point
    screen_x = int(x * scale + offset_x)
    screen_y = int(y * scale + offset_y)
    return (screen_x, screen_y)

def draw_cube(surface, rotation, position=(200, 200), scale=100, color=(0, 255, 255), is_playing=False):
    """
    Draw a 3D wireframe cube with translucent colored faces, song/artist name, and animated strings
    
    Args:
        surface: Pygame surface to draw on
        rotation: [X, Y, Z] rotation angles in radians
        position: (X, Y) screen position for cube center
        scale: Cube size multiplier
        color: RGB color tuple (unused, kept for compatibility)
        is_playing: Boolean - whether music is currently playing (animates strings)
    """
    # Rotate all vertices
    rotated_vertices = [rotate_point(v, rotation) for v in cube_vertices]
    
    # Project to 2D
    projected_vertices = [project_3d_to_2d(v, scale, position[0], position[1]) for v in rotated_vertices]
    
    # For the base (bottom face), use unrotated vertices to keep it locked
    base_vertices = cube_vertices.copy()
    base_projected = [project_3d_to_2d(v, scale, position[0], position[1]) for v in base_vertices]
    
    # Calculate face depths for proper rendering order (painter's algorithm)
    face_depths = []
    for i, face in enumerate(cube_faces):
        # Calculate average Z depth of face vertices
        avg_z = sum(rotated_vertices[v][2] for v in face) / 4
        face_depths.append((avg_z, i))
    
    # Sort faces by depth (draw furthest first)
    face_depths.sort(reverse=True)
    
    # Draw faces (translucent polygons)
    for depth, face_idx in face_depths:
        face = cube_faces[face_idx]
        face_color = face_colors[face_idx]
        
        # Use locked base vertices for bottom face (index 2), rotated for others
        if face_idx == 2:  # Bottom face is locked
            face_points = [base_projected[v] for v in face]
        else:
            face_points = [projected_vertices[v] for v in face]
        
        # Create a surface for the translucent face
        face_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(face_surf, face_color, face_points)
        surface.blit(face_surf, (0, 0))
        
        # Draw song name and artist on front face (index 1)
        if face_idx == 1:
            # Get center of front face
            center_x = sum(p[0] for p in face_points) / 4
            center_y = sum(p[1] for p in face_points) / 4
            
            # Get song name and artist from music manager
            song_name = music_manager.get_current_song_name()
            artist_name = music_manager.get_current_artist_name()
            
            # Render song name (larger, bold)
            font_song = pygame.font.SysFont('Arial', 16, bold=True)
            font_artist = pygame.font.SysFont('Arial', 12, bold=False)
            
            # Split long song names into multiple lines
            max_chars = 15
            song_lines = []
            if len(song_name) > max_chars:
                words = song_name.split()
                current_line = ""
                for word in words:
                    if len(current_line + word) <= max_chars:
                        current_line += word + " "
                    else:
                        if current_line:
                            song_lines.append(current_line.strip())
                        current_line = word + " "
                if current_line:
                    song_lines.append(current_line.strip())
            else:
                song_lines = [song_name]
            
            # Limit to 2 lines for song name
            song_lines = song_lines[:2]
            
            # Draw song name lines
            y_offset = -25 if len(song_lines) > 1 else -15
            for i, line in enumerate(song_lines):
                text_surf = font_song.render(line, True, (255, 255, 255))
                text_rect = text_surf.get_rect(center=(int(center_x), int(center_y) + y_offset + i * 18))
                
                # Add text shadow for better visibility
                shadow_surf = font_song.render(line, True, (0, 0, 0))
                shadow_rect = shadow_surf.get_rect(center=(int(center_x) + 2, int(center_y) + y_offset + 1 + i * 18))
                surface.blit(shadow_surf, shadow_rect)
                surface.blit(text_surf, text_rect)
            
            # Draw artist name below song name
            artist_y = int(center_y) + y_offset + len(song_lines) * 18 + 5
            
            # Truncate artist name if too long
            if len(artist_name) > max_chars + 5:
                artist_name = artist_name[:max_chars + 2] + "..."
            
            artist_surf = font_artist.render(artist_name, True, (200, 200, 255))
            artist_rect = artist_surf.get_rect(center=(int(center_x), artist_y))
            
            # Artist text shadow
            artist_shadow = font_artist.render(artist_name, True, (0, 0, 0))
            artist_shadow_rect = artist_shadow.get_rect(center=(int(center_x) + 1, artist_y + 1))
            surface.blit(artist_shadow, artist_shadow_rect)
            surface.blit(artist_surf, artist_rect)
    
    # Draw animated strings INSIDE the cube (only if music is playing)
    if is_playing:
        for anim_string in animated_strings:
            anim_string.update()  # Update animation
            
            # Get current string endpoints
            start_3d, end_3d = anim_string.get_current_points()
            
            # Rotate string points with cube
            start_rotated = rotate_point(start_3d, rotation)
            end_rotated = rotate_point(end_3d, rotation)
            
            # Project to 2D
            start_2d = project_3d_to_2d(start_rotated, scale, position[0], position[1])
            end_2d = project_3d_to_2d(end_rotated, scale, position[0], position[1])
            
            # Draw string with glow effect
            # Outer glow
            pygame.draw.line(surface, (*anim_string.color, 50), start_2d, end_2d, 4)
            # Middle glow
            pygame.draw.line(surface, (*anim_string.color, 120), start_2d, end_2d, 2)
            # Core line
            pygame.draw.line(surface, (*anim_string.color, 255), start_2d, end_2d, 1)
    
    # Draw edges on top
    for edge in cube_edges:
        start = projected_vertices[edge[0]]
        end = projected_vertices[edge[1]]
        pygame.draw.line(surface, (200, 200, 200), start, end, 2)
    
    # Draw vertices as dots
    for vertex in projected_vertices:
        pygame.draw.circle(surface, (255, 255, 255), vertex, 4)

# ------------------ Camera Setup ------------------ #
cap = cv2.VideoCapture(0)
# Set camera resolution to 720p (1280x720)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

running = True

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                running = False

    ret, frame = cap.read()
    if not ret:
        print("Failed to read from camera")
        break

    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands_detector.process(frame_rgb)

    # Draw MediaPipe hand landmarks on the frame (BGR for OpenCV)
    frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
    active_control = None
    
    # Split screen in half: left side = cube, right side = puck
    screen_center_x = WIDTH // 2
    
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame_bgr, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            landmarks = hand_landmarks.landmark
            
            # Get hand center position (palm center)
            palm_x = landmarks[9].x  # Middle finger base (palm center approximation)
            palm_y = landmarks[9].y
            
            # Convert to screen coordinates
            hand_screen_x = int(palm_x * WIDTH)
            hand_screen_y = int(palm_y * HEIGHT)
            
            # Determine which side of screen the hand is on
            if hand_screen_x < screen_center_x:
                # LEFT SIDE OF SCREEN - Controls cube
                # Update cube position to follow hand
                cube_position[0] = hand_screen_x
                cube_position[1] = hand_screen_y
                
                # Get rotation
                angle_x, angle_y, angle_z = get_hand_rotation(landmarks)
                # Update cube rotation
                cube_rotation[0] = 0  # No up/down tilt - locked
                cube_rotation[1] = angle_y * ROTATION_SENSITIVITY  # Apply sensitivity scaling
                cube_rotation[2] = 0  # No twist
            
            else:
                # RIGHT SIDE OF SCREEN - Controls puck
                # Update puck position to follow hand
                puck_position[0] = hand_screen_x
                puck_position[1] = hand_screen_y
                
                # Detect gestures with movement check
                direction, current_palm = detect_hand_direction(landmarks, previous_hand_position)
                previous_hand_position = current_palm  # Update for next frame
                
                # Check cooldown and if direction was actually detected
                current_time = pygame.time.get_ticks() / 1000.0
                if direction and (current_time - last_gesture_time) > GESTURE_COOLDOWN:
                    active_control = direction
                    last_gesture_time = current_time
                    
                    # Execute control actions with Spotify integration
                    if direction == "UP":
                        music_manager.volume_up()
                    elif direction == "DOWN":
                        music_manager.volume_down()
                    elif direction == "LEFT":
                        music_manager.prev_track()
                    elif direction == "RIGHT":
                        music_manager.next_track()
    
    # Update Spotify playback state
    music_manager.update_playback_state()
    
    # Apply smoothing to reduce shake/jitter and slingshot effect
    for i in range(3):
        smoothed_rotation[i] += (cube_rotation[i] - smoothed_rotation[i]) * SMOOTHING_FACTOR
    
    # Apply smoothing to cube position for stable hand tracking
    for i in range(2):
        smoothed_position[i] += (cube_position[i] - smoothed_position[i]) * POSITION_SMOOTHING
    
    # Apply smoothing to puck position for stable hand tracking
    for i in range(2):
        smoothed_puck_position[i] += (puck_position[i] - smoothed_puck_position[i]) * PUCK_POSITION_SMOOTHING

    # Convert OpenCV frame with landmarks (BGR) back to RGB for Pygame
    frame_with_landmarks = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    
    # Convert to Pygame surface and blit
    try:
        frame_surface = pygame.image.frombuffer(frame_with_landmarks.tobytes(), (frame_with_landmarks.shape[1], frame_with_landmarks.shape[0]), "RGB")
    except Exception:
        # Fallback: convert via surfarray
        frame_surface = pygame.surfarray.make_surface(np.rot90(frame_with_landmarks))

    frame_surface = pygame.transform.scale(frame_surface, (WIDTH, HEIGHT))
    screen.blit(frame_surface, (0, 0))

    # Draw vertical divider line (subtle)
    divider_x = WIDTH // 2
    pygame.draw.line(screen, (80, 80, 100, 100), (divider_x, 0), (divider_x, HEIGHT), 2)
    
    # Draw zone labels at top
    font_label = pygame.font.SysFont('Arial', 14, bold=True)
    left_label = font_label.render('CUBE ZONE', True, (100, 255, 255))
    right_label = font_label.render('PUCK ZONE', True, (255, 150, 100))
    
    # Background for labels
    left_bg = pygame.Surface((left_label.get_width() + 20, 30), pygame.SRCALPHA)
    left_bg.fill((0, 0, 0, 120))
    right_bg = pygame.Surface((right_label.get_width() + 20, 30), pygame.SRCALPHA)
    right_bg.fill((0, 0, 0, 120))
    
    screen.blit(left_bg, (divider_x // 2 - left_label.get_width() // 2 - 10, 10))
    screen.blit(left_label, (divider_x // 2 - left_label.get_width() // 2, 15))
    screen.blit(right_bg, (divider_x + divider_x // 2 - right_label.get_width() // 2 - 10, 10))
    screen.blit(right_label, (divider_x + divider_x // 2 - right_label.get_width() // 2, 15))

    # Draw the 3D cube with smoothed rotation at smoothed hand position
    # Pass is_playing state to enable/disable animated strings
    is_playing = music_manager.is_playing if music_manager.sp else False
    draw_cube(screen, smoothed_rotation, 
              position=(int(smoothed_position[0]), int(smoothed_position[1])), 
              scale=80, 
              color=(0, 255, 255),
              is_playing=is_playing)
    
    # Draw the puck controller at smoothed hand position
    draw_puck_controller(screen, smoothed_puck_position, puck_radius, active_control)

    pygame.display.flip()
    clock.tick(30)

cap.release()
pygame.quit()
sys.exit(0)

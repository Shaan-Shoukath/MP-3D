# 🎵 Hand-Controlled MP3 Player

A gesture-based music player with 3D visual interface using computer vision and hand tracking. Control your music library with intuitive hand gestures - no mouse, no keyboard, just your hands!

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### 🎨 Visual Interface
- **3D Rotating Cube**: Music visualizer controlled by left hand rotation
- **Puck Controller**: Gesture-based controls with 3D translucent design
- **Real-time Hand Tracking**: MediaPipe skeleton overlay on camera feed
- **Split-Screen Zones**: Left zone for cube, right zone for puck (reliable hand detection)

### 🎮 Gesture Controls

#### Left Hand (Cube Zone)
- **Rotate Hand**: Cube rotates horizontally following your hand orientation
- **Move Hand**: Cube position follows your palm smoothly
- **Song Display**: Current track name displayed on front face of cube

#### Right Hand (Puck Zone)
- **Wave Up (↑)**: Increase volume
- **Wave Down (↓)**: Decrease volume
- **Wave Left (←)**: Previous track
- **Wave Right (→)**: Next track

### 🏗️ Architecture
- **Modular Design**: Music manager ready for Spotify API integration
- **Smooth Tracking**: Exponential smoothing eliminates jitter
- **Gesture Detection**: Movement-based detection prevents false triggers
- **Cooldown System**: Prevents accidental repeated activations

---

## 📋 Requirements

### System Requirements
- **Python**: 3.8 or higher
- **OS**: Windows, macOS, or Linux
- **Webcam**: 720p (1280x720) recommended
- **RAM**: 4GB minimum

### Python Dependencies
```
opencv-python>=4.8.0
mediapipe>=0.10.0
pygame>=2.5.0
numpy>=1.24.0
```

---

## 🚀 Installation

### 1. Clone or Download
```bash
cd "MP Game"
```

### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv mediapipe_env
mediapipe_env\Scripts\activate

# macOS/Linux
python3 -m venv mediapipe_env
source mediapipe_env/bin/activate
```

### 3. Install Dependencies
```bash
pip install opencv-python mediapipe pygame numpy spotipy
```

### 4. Add Your Music Files
Place your MP3 files in the project directory and update `mpsgame.py`:

```python
# Line 67: Replace with your track names
tracks = ["song1.mp3", "song2.mp3", "your_song.mp3"]
```

**Note:** With Spotify integration, local files are no longer required. The application streams directly from Spotify.

### 5. Configure Spotify API (Required)

**Create your own `spotify_config.py` file** (not included in repository for security):

```python
# spotify_config.py
SPOTIFY_CLIENT_ID = "your_actual_client_id_here"
SPOTIFY_CLIENT_SECRET = "your_actual_client_secret_here"
SPOTIFY_REDIRECT_URI = "http://localhost:8888/callback"
```

**How to get credentials:**
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click **"Create App"**
4. Fill in:
   - App name: "Hand Controlled Music Player"
   - App description: "Gesture-based music controller"
   - Redirect URI: `http://localhost:8888/callback`
5. Click **"Save"**
6. Copy **Client ID** and **Client Secret**
7. Paste them into your `spotify_config.py` file

**Security Warning:**
- ⚠️ Never commit `spotify_config.py` to Git
- ⚠️ Never share your Client Secret publicly
- ✅ The `.gitignore` file automatically excludes this file

---

## 🎯 Usage

### Running the Application

**Prerequisites:**
1. Spotify Desktop or Web app must be open
2. Start playing any track in Spotify
3. Ensure `spotify_config.py` has your valid credentials

```bash
# Activate virtual environment first
mediapipe_env\Scripts\activate  # Windows
source mediapipe_env/bin/activate  # macOS/Linux

# Run the application
python mpsgame.py
```

**First Run:**
- Browser will open for Spotify authorization
- Click "Agree" to grant permissions
- You'll be redirected (may show connection error - this is normal)
- Copy the full redirect URL from browser
- Paste it in the terminal when prompted
- Authorization is saved for future runs

### Controls
1. **Position your hands**:
   - Left hand in LEFT half of camera view → Controls cube
   - Right hand in RIGHT half of camera view → Controls puck

2. **Cube controls (Left Hand)**:
   - Rotate your hand left/right to rotate the cube
   - Move your hand to reposition the cube
   - Song name appears on the front face

3. **Puck controls (Right Hand)**:
   - Point index finger UP: Volume +
   - Point index finger DOWN: Volume -
   - Point index finger LEFT: Previous track
   - Point index finger RIGHT: Next track

4. **Exit**:
   - Press `Q` or `ESC`
   - Close the window

### Tips for Best Experience
- **Lighting**: Use good lighting for reliable hand tracking
- **Distance**: Position yourself 2-3 feet from camera
- **Hand Position**: Keep hands clearly separated (left/right zones)
- **Gestures**: Make deliberate movements for gestures
- **Cooldown**: Wait 0.5s between gestures to avoid spam

---

## 🔧 Configuration

### Tuning Parameters (mpsgame.py)

#### Cube Settings
```python
SMOOTHING_FACTOR = 0.08      # Rotation smoothing (0.0-1.0)
POSITION_SMOOTHING = 0.15    # Position smoothing
ROTATION_SENSITIVITY = 1.2   # Rotation multiplier
```

#### Puck Settings
```python
GESTURE_COOLDOWN = 0.5       # Seconds between gestures
GESTURE_THRESHOLD = 0.12     # Gesture detection sensitivity
MOVEMENT_THRESHOLD = 0.05    # Minimum movement to trigger
```

#### Display Settings
```python
WIDTH, HEIGHT = 1280, 720    # Screen resolution
clock.tick(30)               # Frame rate (FPS)
```

---

## 🎵 Spotify Integration Guide

The application is designed with modular architecture for easy Spotify integration. Follow these steps to connect to Spotify Web API:

### Prerequisites
1. **Spotify Developer Account**: Register at [developer.spotify.com](https://developer.spotify.com)
2. **Create Spotify App**: Get Client ID and Client Secret
3. **Install Spotipy**: `pip install spotipy`

### Implementation Steps

#### 1. Install Spotipy Library
```bash
pip install spotipy
```

#### 2. Add Spotify Credentials
Create a file `spotify_config.py`:

```python
# spotify_config.py
SPOTIFY_CLIENT_ID = "your_client_id_here"
SPOTIFY_CLIENT_SECRET = "your_client_secret_here"
SPOTIFY_REDIRECT_URI = "http://localhost:8888/callback"
```

#### 3. Uncomment Spotify Methods in MusicManager Class
In `mpsgame.py`, find the commented Spotify methods (lines ~100-150) and uncomment:

```python
def connect_spotify(self, client_id, client_secret):
    """Initialize Spotify Web API connection"""
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
    
    self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="http://localhost:8888/callback",
        scope="user-read-playback-state,user-modify-playback-state"
    ))
    
    # Check if Spotify app is active
    current = self.sp.current_playback()
    if not current:
        print("⚠️ Please open Spotify and start playing a track")
    else:
        print(f"✅ Connected to Spotify: {current['device']['name']}")

def get_spotify_metadata(self):
    """Fetch current track metadata from Spotify"""
    current = self.sp.current_playback()
    if current and current['item']:
        return {
            'name': current['item']['name'],
            'artist': current['item']['artists'][0]['name'],
            'album': current['item']['album']['name'],
            'duration': current['item']['duration_ms'],
            'artwork': current['item']['album']['images'][0]['url']
        }
    return None

def search_track(self, query):
    """Search Spotify catalog for tracks"""
    results = self.sp.search(q=query, type='track', limit=10)
    return results['tracks']['items']
```

#### 4. Modify Track Navigation for Spotify
Update `next_track()` and `prev_track()` methods:

```python
def next_track(self):
    """Skip to next track (Spotify version)"""
    if hasattr(self, 'sp'):
        # Use Spotify API
        self.sp.next_track()
        print("⏭️ Skipped to next track")
    else:
        # Fallback to local files
        self.current_track = (self.current_track + 1) % len(self.tracks)
        self.load_track(self.current_track)
        pygame.mixer.music.play(-1)

def prev_track(self):
    """Go to previous track (Spotify version)"""
    if hasattr(self, 'sp'):
        # Use Spotify API
        self.sp.previous_track()
        print("⏮️ Previous track")
    else:
        # Fallback to local files
        self.current_track = (self.current_track - 1) % len(self.tracks)
        self.load_track(self.current_track)
        pygame.mixer.music.play(-1)
```

#### 5. Update Volume Controls
Spotify volume control in gesture detection:

```python
if direction == "UP":
    if hasattr(music_manager, 'sp'):
        # Spotify volume control
        current = music_manager.sp.current_playback()
        if current:
            current_vol = current['device']['volume_percent']
            music_manager.sp.volume(min(current_vol + 10, 100))
    else:
        # Local file volume control
        current_volume = pygame.mixer.music.get_volume()
        pygame.mixer.music.set_volume(min(current_volume + 0.1, 1.0))
```

#### 6. Initialize Spotify in Main Code
At the top of your main script (after imports):

```python
from spotify_config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

# Initialize with Spotify
music_manager = MusicManager([])  # Empty list for Spotify mode
music_manager.connect_spotify(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
```

#### 7. Update Song Name Display
Modify `get_current_song_name()`:

```python
def get_current_song_name(self):
    """Get current song name (Spotify or local)"""
    if hasattr(self, 'sp'):
        # Fetch from Spotify
        metadata = self.get_spotify_metadata()
        if metadata:
            return f"{metadata['name']} - {metadata['artist']}"
    
    # Fallback to local file
    song_file = self.tracks[self.current_track]
    song_name = song_file.split('/')[-1].split('\\')[-1]
    song_name = song_name.replace('.mp3', '').replace('.wav', '')
    return song_name
```

### Required Spotify Scopes
```python
scope = "user-read-playback-state,user-modify-playback-state,user-read-currently-playing"
```

### Testing Spotify Integration
1. Open Spotify Desktop/Web app
2. Start playing any track
3. Run the application: `python mpsgame.py`
4. Use gestures to control Spotify playback
5. Song name and artist will appear on cube

### Troubleshooting Spotify
- **Authorization Failed**: Check Client ID and Secret in `spotify_config.py`
- **No Active Device**: Open Spotify and play a track first
- **Commands Not Working**: Verify Spotify Premium account (required for playback control)
- **Redirect URI Mismatch**: Ensure redirect URI matches exactly in code and Spotify dashboard (`http://localhost:8888/callback`)
- **Import Error**: Install spotipy with `pip install spotipy`
- **Config Not Found**: Create `spotify_config.py` file with your credentials (see Installation section)

---

## 📁 Project Structure (Updated)

See the complete structure in the beginning of this README, including:
- `.gitignore` - Configured to exclude sensitive files
- `spotify_config.py` - Your credentials (create this yourself, never commit)
- `.cache` files - Automatically generated by Spotify (also ignored by Git)

---

## 🔐 Security Best Practices

### Protecting Your Spotify Credentials

1. **Never commit credentials:**
   ```bash
   # Check before committing
   git status
   # spotify_config.py should NOT appear in the list
   ```

2. **Verify .gitignore is working:**
   ```bash
   git check-ignore spotify_config.py
   # Should output: spotify_config.py
   ```

3. **If you accidentally committed credentials:**
   ```bash
   # Remove from Git history (nuclear option)
   git filter-branch --force --index-filter \
   "git rm --cached --ignore-unmatch spotify_config.py" \
   --prune-empty --tag-name-filter cat -- --all
   
   # Regenerate new credentials at developer.spotify.com
   ```

4. **Share safely:**
   - Share `spotify_config.py.example` template instead
   - Include setup instructions in documentation
   - Use environment variables for production deployments

---

## 📁 Project Structure

```
MP Game/
├── mpsgame.py              # Main application file
├── README.md               # This file
├── .gitignore              # Git ignore file (excludes spotify_config.py)
├── spotify_config.py       # Spotify credentials (DO NOT COMMIT - add your own)
├── song1.mp3               # Your music files (optional - for local mode)
├── song2.mp3               # ...
└── mediapipe_env/          # Virtual environment (created by you)
```

### ⚠️ Important: Spotify Credentials Security

**DO NOT commit `spotify_config.py` to version control!**

The `.gitignore` file is configured to automatically exclude:
- `spotify_config.py` - Contains your Spotify API credentials
- `.cache*` - Spotify authentication cache files
- `mediapipe_env/` - Virtual environment
- `__pycache__/` - Python cache files

**To share this project:**
1. Clone/download the repository
2. Create your own `spotify_config.py` with your credentials
3. Follow setup instructions below

---

## 🛠️ Troubleshooting

### Camera Issues
- **No camera feed**: Check if another application is using webcam
- **Permission denied**: Grant camera access in system settings
- **Low FPS**: Reduce resolution or close other applications

### Hand Detection Issues
- **Hands not detected**: Improve lighting, move closer to camera
- **Wrong hand detected**: Position hands clearly in left/right zones
- **Jittery tracking**: Reduce `SMOOTHING_FACTOR` value

### Gesture Issues
- **Gestures not triggering**: Make more deliberate movements
- **Too sensitive**: Increase `GESTURE_THRESHOLD` value
- **Repeated triggers**: Increase `GESTURE_COOLDOWN` value

### Audio Issues
- **No sound**: Check system volume and audio output device
- **File not found**: Verify MP3 file paths in `tracks` list
- **Format error**: Convert files to MP3 or WAV format

---

## 🎓 Technical Details

### Hand Landmark Detection
- **MediaPipe Hands**: 21 landmark points per hand
- **Key landmarks used**:
  - Landmark 0: Wrist (base reference)
  - Landmark 5: Index finger base (rotation calculation)
  - Landmark 8: Index finger tip (gesture direction)
  - Landmark 9: Middle finger base (palm center, position tracking)

### 3D Rendering
- **Projection**: Orthographic projection (3D → 2D)
- **Depth sorting**: Painter's algorithm for face rendering order
- **Transparency**: Alpha blending with Pygame surfaces
- **Rotation**: 3-axis rotation using trigonometry (X, Y, Z)

### Smoothing Algorithm
```python
smoothed_value += (target_value - smoothed_value) * smoothing_factor
```
- **Exponential moving average**
- **Prevents jitter** from MediaPipe tracking variance
- **Maintains responsiveness** with tuned factors

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- [ ] Additional visualizations (waveform, spectrum analyzer)
- [ ] More gesture controls (pause, shuffle, repeat)
- [ ] Voice commands integration
- [ ] Multi-monitor support
- [ ] VR/AR mode
- [ ] Playlist management UI
- [ ] Theme customization

---

## 📝 License

MIT License - Feel free to use, modify, and distribute.

---

## 👨‍💻 Author

**Shaan Shoukath**
Created: October 2025

---

## 🙏 Acknowledgments

- **MediaPipe** by Google - Hand tracking technology
- **Pygame** - Graphics and audio rendering
- **OpenCV** - Computer vision library
- **Spotipy** - Spotify Web API wrapper

---

## 📞 Support

If you encounter issues or have questions:
1. Check the Troubleshooting section above
2. Review the configuration parameters
3. Ensure all dependencies are installed correctly
4. Verify camera permissions

---

## 🔮 Future Enhancements

### Planned Features
- ✅ Spotify integration (architecture ready)
- 🔄 Apple Music API support
- 🔄 YouTube Music integration
- 🔄 Machine learning for custom gestures
- 🔄 Multi-user support (different hands = different controls)
- 🔄 Audio visualization (FFT spectrum analysis)
- 🔄 Gesture recording and playback
- 🔄 Mobile app companion

### Potential Integrations
- Discord Rich Presence
- Last.fm scrobbling
- Lyrics display
- Album artwork on cube faces
- LED light sync (Philips Hue, LIFX)

---

**Enjoy controlling your music with just your hands! 🎵✋**

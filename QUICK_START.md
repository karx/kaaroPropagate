# Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Prerequisites
- Docker and Docker Compose installed
- Modern web browser (Chrome, Firefox, Safari, Edge)
- 4GB RAM minimum

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd workspaces
```

2. **Start the application**
```bash
docker-compose up -d
```

3. **Access the application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### First Steps

#### 1. View a Single Comet (30 seconds)

1. Open http://localhost:5173
2. The first comet is automatically selected
3. Click ▶️ Play to see it move
4. Use mouse to rotate the view

**That's it!** You're now viewing a comet's trajectory.

#### 2. Compare Multiple Comets (2 minutes)

1. Click the **Multi Mode** button (📊)
2. Check boxes next to 3-5 comets
3. Click **Fetch** button
4. Click ▶️ Play to see them all move together

Each comet gets a unique color!

#### 3. Adjust the View (1 minute)

**Change trajectory duration:**
- Drag the "Days" slider (30-3650 days)

**Change calculation method:**
- Select "Two-Body" (fast) or "N-Body" (accurate)

**Change animation speed:**
- Click speed buttons: 0.5x, 1x, 2x, 5x

#### 4. Explore Planets (1 minute)

- Planets move in real-time along their orbits
- Watch them as the animation plays
- Notice Saturn's rings and planet textures

---

## 🎮 Basic Controls

### Mouse
- **Left Click + Drag**: Rotate view
- **Right Click + Drag**: Pan
- **Scroll Wheel**: Zoom

### Animation
- **▶️/⏸️**: Play/Pause
- **Slider**: Jump to any time
- **Speed buttons**: Change animation speed

### Selection
- **Single Mode**: Click a comet name
- **Multi Mode**: Check boxes, then click Fetch

---

## 📊 Understanding the Display

### Colors
- **Yellow marker**: Perihelion (closest to Sun)
- **Blue marker**: Aphelion (farthest from Sun)
- **Green arrow**: Velocity vector
- **Colored trails**: Comet paths

### Panels
- **Left**: Object selector and controls
- **Center**: 3D visualization
- **Right**: Comet information
- **Bottom**: Animation timeline

---

## 🔧 Common Tasks

### View a Specific Comet
1. Scroll through the list on the left
2. Click the comet name
3. Trajectory loads automatically

### Compare Two Methods
1. Select a comet (Single Mode)
2. Check "Compare Methods"
3. See Two-Body (cyan) vs N-Body (yellow)

### Filter by Category
1. Switch to Multi Mode
2. Select category from dropdown
3. List updates automatically

### Export Data
1. Open http://localhost:8000/docs
2. Try API endpoints
3. Download JSON responses

---

## ⚡ Performance Tips

**For smooth animation:**
- Use 100-200 points
- Limit to 10-20 objects in multi-mode
- Close other browser tabs

**For detailed analysis:**
- Use 300-500 points
- Pause animation when examining
- Use single object mode

---

## 🐛 Troubleshooting

### Application won't start
```bash
# Check if ports are available
docker-compose down
docker-compose up -d
```

### Trajectory not showing
- Refresh the page
- Check browser console (F12)
- Verify object has orbital elements

### Slow performance
- Reduce number of points
- Limit objects in multi-mode
- Try different browser

### Planets not moving
- Verify animation is playing
- Check time is changing
- Reload the page

---

## 📚 Next Steps

1. **Read the full User Guide**: `USER_GUIDE.md`
2. **Explore the API**: http://localhost:8000/docs
3. **Try advanced features**: Method comparison, batch calculations
4. **Experiment with parameters**: Days, points, methods

---

## 🎯 Example Workflows

### Workflow 1: Study a Near-Earth Object
1. Switch to Multi Mode
2. Select "Near-Earth Objects" category
3. Pick an interesting NEO
4. Switch back to Single Mode
5. Enable "Compare Methods"
6. Play animation to see close approach

### Workflow 2: Compare Jupiter Family Comets
1. Multi Mode → "Jupiter Family" category
2. Select 5-10 comets
3. Click Fetch
4. Play animation
5. Watch how they cluster near Jupiter's orbit

### Workflow 3: Long-Term Evolution
1. Select a long-period comet
2. Set Days to 3650 (10 years)
3. Use N-Body method
4. Play at 5x speed
5. Watch orbital perturbations

---

## 💡 Pro Tips

1. **Use keyboard shortcuts**: Space for play/pause, arrows for stepping
2. **Zoom in on inner planets**: Better detail for close approaches
3. **Pause at perihelion**: Best time to examine comet behavior
4. **Compare methods**: See how planetary gravity affects orbits
5. **Use categories**: Quickly find similar objects

---

## 📞 Getting Help

- **User Guide**: Comprehensive documentation
- **API Docs**: http://localhost:8000/docs
- **Browser Console**: F12 for error messages
- **GitHub Issues**: Report bugs and request features

---

## 🎉 You're Ready!

You now know enough to:
- ✅ Visualize comet trajectories
- ✅ Compare multiple objects
- ✅ Understand the display
- ✅ Control the animation
- ✅ Troubleshoot issues

**Enjoy exploring the solar system!** 🌌

---

*For detailed information, see USER_GUIDE.md*

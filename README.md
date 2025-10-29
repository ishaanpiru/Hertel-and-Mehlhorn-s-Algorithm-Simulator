# 🧩 Hertel–Mehlhorn Convex Decomposition

## 📘 Overview
This project implements the **Hertel–Mehlhorn algorithm** for convex decomposition of simple polygons.  
It includes:
- **`cp2.py`** – Interactive visualizer to draw or generate polygons and step through decomposition.  
- **`gif_generator.py`** – Script to automatically generate GIFs showing the algorithm steps.

---

## 🧠 Algorithm Summary
The **Hertel–Mehlhorn algorithm** performs convex decomposition in two main phases:

1. **Triangulation (Ear Clipping Method):**  
   The polygon is divided into smaller triangles.

2. **Merging Triangles:**  
   Adjacent triangles are tested for merging:
   - **Inessential Edge** → merging keeps polygon convex → triangles are merged.  
   - **Essential Edge** → merging breaks convexity → merge skipped.  

The result is a **minimal convex decomposition** of the polygon.

---

## ⚙️ How to Run

### 1. Interactive Visualizer
Run:
```bash
python cp2.py
```
A GUI window will open to visualize the process.
Then:
- Click Draw Polygon Manually or Generate Random Polygon
- Click Start Decomposition to begin the algorithm
- Click Next Step to move through each stage of the decomposition


### 2. To automatically generate GIFs showing the decomposition steps
Run:
```bash
python gif_generator.py
```
This will:
- Generate random polygons
- Perform the decomposition
- Save GIFs such as hm_n10.gif and hm_n15.gif in the working directory
  for an n just write create_hm_gif(xxx, "hm_nxxx.gif") in the last line of the file
  
## Requirements
Install the following dependencies before running:
```bash
pip install matplotlib numpy imageio
```
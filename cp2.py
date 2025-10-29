
import random
import math
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, TextBox
import numpy as np

# ================================================
# Geometry Utility Functions
# ================================================
def orient(a, b, c):
    return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])

def is_ccw(a, b, c):
    return orient(a, b, c) > 1e-9

def point_in_triangle(p, a, b, c):
    o1 = orient(a,b,p)
    o2 = orient(b,c,p)
    o3 = orient(c,a,p)
    return (o1 >= 0 and o2 >= 0 and o3 >= 0) or (o1 <= 0 and o2 <= 0 and o3 <= 0)

def polygon_area(poly):
    area = 0
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i+1) % len(poly)]
        area += x1*y2 - x2*y1
    return area / 2

def make_simple_polygon(points):
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)
    return sorted(points, key=lambda p: math.atan2(p[1]-cy, p[0]-cx))

def generate_points(n, xrange=(0,100), yrange=(0,100)):
    pts = set()
    while len(pts) < n:
        pts.add((random.uniform(*xrange), random.uniform(*yrange)))
    return make_simple_polygon(list(pts))

# ================================================
# Triangulation
# ================================================
def ear_clipping_triangulation(poly):
    V = list(range(len(poly)))
    tris = []

    def is_convex(i):
        a, b, c = poly[V[i-1]], poly[V[i]], poly[V[(i+1) % len(V)]]
        return is_ccw(a, b, c)

    while len(V) > 3:
        for i in range(len(V)):
            if not is_convex(i):
                continue
            a, b, c = poly[V[i-1]], poly[V[i]], poly[V[(i+1) % len(V)]]
            if any(point_in_triangle(poly[V[j]], a, b, c)
                   for j in range(len(V))
                   if j not in [i-1, i, (i+1) % len(V)]):
                continue
            tris.append((V[i-1], V[i], V[(i+1) % len(V)]))
            del V[i]
            break
    tris.append((V[0], V[1], V[2]))
    return tris

# ================================================
# Hertel–Mehlhorn Convex Decomposition
# ================================================
def edge_key(a, b):
    return tuple(sorted((a, b)))

def build_piece_edges(piece):
    return {edge_key(piece[i], piece[(i+1)%len(piece)]) for i in range(len(piece))}

def is_convex_polygon(poly_pts):
    sign = 0
    for i in range(len(poly_pts)):
        a, b, c = poly_pts[i], poly_pts[(i+1)%len(poly_pts)], poly_pts[(i+2)%len(poly_pts)]
        o = orient(a, b, c)
        if abs(o) < 1e-9:
            continue
        if sign == 0:
            sign = 1 if o > 0 else -1
        elif (o > 0) != (sign > 0):
            return False
    return True

def merge_two_pieces(p1, p2, poly):
    shared = build_piece_edges(p1) & build_piece_edges(p2)
    if len(shared) != 1:
        return None, None
    edge = list(shared)[0]
    merged = list(set(p1 + p2))
    merged_coords = [poly[i] for i in merged]
    if is_convex_polygon(merged_coords):
        return merged, ("Inessential", edge)
    else:
        return None, ("Essential", edge)

# ================================================
# Visualization Helpers
# ================================================
def plot_polygon(ax, poly, pieces=None, title="", highlight_edge=None, edge_status=None):
    ax.clear()
    ax.set_title(title)
    if not pieces:
        if len(poly) > 1:
            xs, ys = zip(*poly)
            ax.plot(xs + (xs[0],), ys + (ys[0],), color='black')
        if poly:
            ax.scatter([x for x, _ in poly], [y for _, y in poly], color='red')
    else:
        for p in pieces:
            coords = [poly[i] for i in p] + [poly[p[0]]]
            xs, ys = zip(*coords)
            ax.fill(xs, ys, alpha=0.4)
            ax.plot(xs, ys, color='black')
        ax.scatter([x for x, _ in poly], [y for _, y in poly], color='red')

    # Highlight tested edge
    if highlight_edge:
        a, b = poly[highlight_edge[0]], poly[highlight_edge[1]]
        color = 'green' if edge_status == "Inessential" else 'red'
        ax.plot([a[0], b[0]], [a[1], b[1]], color=color, linewidth=3)
        mid = ((a[0]+b[0])/2, (a[1]+b[1])/2)
        ax.text(mid[0], mid[1], edge_status, color=color, fontsize=10, weight='bold')

    ax.set_aspect('equal')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    plt.draw()

# ================================================
# Interactive Visualizer Class
# ================================================
class HMVisualizer:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        plt.subplots_adjust(bottom=0.35)

        # Buttons
        self.draw_ax = plt.axes([0.05, 0.18, 0.25, 0.075])
        self.rand_ax = plt.axes([0.37, 0.18, 0.25, 0.075])
        self.start_ax = plt.axes([0.69, 0.18, 0.25, 0.075])
        self.next_ax = plt.axes([0.37, 0.08, 0.25, 0.06])

        self.draw_btn = Button(self.draw_ax, 'Draw Polygon Manually')
        self.rand_btn = Button(self.rand_ax, 'Generate Random Polygon')
        self.start_btn = Button(self.start_ax, 'Start Decomposition')
        self.next_btn = Button(self.next_ax, 'Next Step')

        self.draw_btn.on_clicked(self.enable_drawing)
        self.rand_btn.on_clicked(self.ask_vertex_count)
        self.start_btn.on_clicked(self.start_decomposition)
        self.next_btn.on_clicked(self.next_step)
        self.next_ax.set_visible(False)

        # Textbox for number of vertices
        self.text_ax = plt.axes([0.4, 0.28, 0.2, 0.05])
        self.text_box = TextBox(self.text_ax, 'Vertices:', initial="8")
        self.text_ax.set_visible(False)

        self.poly = []
        self.steps = []
        self.current_step = 0
        self.cid = None

        plot_polygon(self.ax, [], None, "Click a button to start")

    # Manual Drawing
    def enable_drawing(self, event):
        print("Drawing mode enabled: Left-click to add points, Right-click to remove nearest point.")
        self.poly = []
        plot_polygon(self.ax, self.poly, None, "Drawing Polygon (Left-click add, Right-click remove)")
        if self.cid:
            self.fig.canvas.mpl_disconnect(self.cid)
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.on_click)

    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        if event.button == 1:
            self.poly.append((event.xdata, event.ydata))
        elif event.button == 3 and self.poly:
            pts = np.array(self.poly)
            dist = np.hypot(pts[:,0] - event.xdata, pts[:,1] - event.ydata)
            idx = np.argmin(dist)
            self.poly.pop(idx)
        plot_polygon(self.ax, self.poly, None, "Drawing Polygon")

    # Random polygon generation with vertex input
    def ask_vertex_count(self, event):
        self.text_ax.set_visible(True)
        plt.draw()
        self.text_box.on_submit(self.generate_random)

    def generate_random(self, text):
        try:
            n = int(text)
            if n < 3:
                print("Need at least 3 vertices.")
                return
        except ValueError:
            print("Invalid number.")
            return
        self.poly = generate_points(n)
        if polygon_area(self.poly) < 0:
            self.poly.reverse()
        plot_polygon(self.ax, self.poly, None, f"Random Polygon with {n} vertices")
        print(f"Random polygon with {n} vertices created.")
        self.text_ax.set_visible(False)
        plt.draw()

    # Start decomposition
    def start_decomposition(self, event):
        if len(self.poly) < 3:
            print("Need at least 3 points for a polygon.")
            return
        if polygon_area(self.poly) < 0:
            self.poly.reverse()
        print("Starting Hertel-Mehlhorn decomposition...")
        tris = ear_clipping_triangulation(self.poly)
        self.steps = []
        self.build_steps(tris)
        self.current_step = 0
        title, pieces, edge_info = self.steps[0]
        plot_polygon(self.ax, self.poly, pieces, title)
        self.next_ax.set_visible(True)
        plt.draw()

    def build_steps(self, tris):
        pieces = [list(t) for t in tris]
        self.steps.append(("Triangulated Polygon", [list(t) for t in tris], None))

        tested_edges = set()  
        merged = True
        step_num = 1
        while merged:
            merged = False
            for i in range(len(pieces)):
                for j in range(i+1, len(pieces)):
                    shared = build_piece_edges(pieces[i]) & build_piece_edges(pieces[j])
                    if len(shared) != 1:
                        continue
                    edge = list(shared)[0]
                    if edge_key(*edge) in tested_edges: 
                        continue
                    tested_edges.add(edge_key(*edge)) 

                    merged_piece, edge_info = merge_two_pieces(pieces[i], pieces[j], self.poly)
                    if edge_info:
                        self.steps.append((f"Testing edge: {edge_info[1]}", [p[:] for p in pieces], edge_info))
                    if merged_piece:
                        pieces[i] = merged_piece
                        pieces.pop(j)
                        merged = True
                        self.steps.append((f"Step {step_num}: merged (Inessential edge)", [p[:] for p in pieces], edge_info))
                        step_num += 1
                        break
                if merged:
                    break

        self.steps.append(("Final Convex Decomposition", [p[:] for p in pieces], None))


    def next_step(self, event):
        if not self.steps:
            return
        self.current_step = min(self.current_step + 1, len(self.steps) - 1)
        title, pieces, edge_info = self.steps[self.current_step]
        highlight_edge = edge_info[1] if edge_info else None
        edge_status = edge_info[0] if edge_info else None
        plot_polygon(self.ax, self.poly, pieces, title, highlight_edge, edge_status)

# ================================================
# Run Application
# ================================================
if __name__ == "__main__":
    print("Launching Hertel-Mehlhorn Interactive Visualizer...")
    HMVisualizer()
    plt.show()

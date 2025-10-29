import matplotlib.pyplot as plt
import imageio
import os
from cp2 import generate_points, polygon_area, ear_clipping_triangulation, merge_two_pieces, build_piece_edges, edge_key, plot_polygon

# ===================================================
# Helper: Build decomposition steps (non-interactive)
# ===================================================
def build_steps(poly, tris):
    steps = []
    pieces = [list(t) for t in tris]
    steps.append(("Triangulated Polygon", [list(t) for t in tris], None))

    tested_edges = set()
    merged = True
    step_num = 1
    while merged:
        merged = False
        for i in range(len(pieces)):
            for j in range(i + 1, len(pieces)):
                shared = build_piece_edges(pieces[i]) & build_piece_edges(pieces[j])
                if len(shared) != 1:
                    continue
                edge = list(shared)[0]
                if edge_key(*edge) in tested_edges:
                    continue
                tested_edges.add(edge_key(*edge))

                merged_piece, edge_info = merge_two_pieces(pieces[i], pieces[j], poly)
                if edge_info:
                    steps.append((f"Testing edge: {edge_info[1]}", [p[:] for p in pieces], edge_info))
                if merged_piece:
                    pieces[i] = merged_piece
                    pieces.pop(j)
                    merged = True
                    steps.append((f"Step {step_num}: merged (Inessential edge)", [p[:] for p in pieces], edge_info))
                    step_num += 1
                    break
            if merged:
                break

    steps.append(("Final Convex Decomposition", [p[:] for p in pieces], None))
    return steps

# ===================================================
# Main Function: Generate GIF
# ===================================================
def create_hm_gif(n, filename="hm.gif"):
    print(f"Generating polygon with {n} vertices...")
    poly = generate_points(n)
    if polygon_area(poly) < 0:
        poly.reverse()

    print("Performing triangulation...")
    tris = ear_clipping_triangulation(poly)
    print("Building decomposition steps...")
    steps = build_steps(poly, tris)

    os.makedirs("frames", exist_ok=True)
    filenames = []

    fig, ax = plt.subplots(figsize=(6, 6))
    for i, (title, pieces, edge_info) in enumerate(steps):
        highlight_edge = edge_info[1] if edge_info else None
        edge_status = edge_info[0] if edge_info else None
        plot_polygon(ax, poly, pieces, title, highlight_edge, edge_status)

        frame_path = f"frames/frame_{i:03d}.png"
        plt.savefig(frame_path)
        filenames.append(frame_path)

    plt.close(fig)

    # Convert all frames into a GIF
    print("Creating GIF...")
    images = [imageio.imread(f) for f in filenames]
    imageio.mimsave(filename, images, duration=1000.0)

    # Cleanup (optional)
    for f in filenames:
        os.remove(f)

    print(f"GIF saved as {filename}")

# ===================================================
# Run for n = 10 and n = 15
# ===================================================
if __name__ == "__main__":
    create_hm_gif(10, "hm_n10.gif")
    create_hm_gif(15, "hm_n15.gif")

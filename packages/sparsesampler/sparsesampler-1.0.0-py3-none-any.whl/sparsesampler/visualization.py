import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from sklearn.datasets import make_blobs
from sklearn.decomposition import PCA
from matplotlib.animation import FuncAnimation
from .preprocessing import perform_pca_binning, adjust_feature_importances, accumulate_indices_until_threshold
import random

def generate_toy_data(n_samples=200, random_state=42):
    """Generate toy data with 3:1 variance ratio between PCs."""
    # Generate points in a circle
    np.random.seed(random_state)
    theta = np.random.uniform(0, 2*np.pi, n_samples)
    r = np.random.normal(0, 1, n_samples)
    
    # Create elliptical data with 3:1 ratio
    x = r * np.cos(theta)
    y = r * np.sin(theta) / 3
    
    # Add some noise
    x += np.random.normal(0, 0.1, n_samples)
    y += np.random.normal(0, 0.1, n_samples)
    
    # Stack coordinates
    X = np.column_stack((x, y))
    
    # Create labels (all same cluster for this example)
    y = np.zeros(n_samples)
    
    return X, y

def get_bin_edges(data, n_bins):
    # Returns the bin edges for a 1D array and number of bins
    return np.linspace(data.min(), data.max(), n_bins + 1)

def get_cell_patch_data(cells_to_highlight, color, n_bins_pc1, n_bins_pc2, pc1_edges, pc2_edges):
    patches_data = []
    for cell in cells_to_highlight:
        i, j = cell
        if 0 <= i < n_bins_pc1 and 0 <= j < n_bins_pc2:
            x0 = pc1_edges[i]
            y0 = pc2_edges[j]
            width = pc1_edges[i+1] - pc1_edges[i]
            height = pc2_edges[j+1] - pc2_edges[j]
            patches_data.append({'xy': (x0, y0), 'width': width, 'height': height, 'facecolor': color, 'alpha': 0.3})
    return patches_data

def create_animation(X, y, output_file='sampling_process.gif', target_sample_size=50, base_bins=8, random_seed=42):
    random.seed(random_seed)
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)
    df = pd.DataFrame(X_pca, columns=['PC1', 'PC2'])
    var_ratio = pca.explained_variance_ratio_
    print(f"Variance ratio between PCs: {var_ratio[0]/var_ratio[1]:.2f}:1")

    feature_importances = adjust_feature_importances(pca)
    n_bins_pc1 = max(2, feature_importances[0] // 4)
    n_bins_pc2 = feature_importances[1] if len(feature_importances) > 1 else feature_importances[0]
    if n_bins_pc2 < 2: n_bins_pc2 = 2

    pc1_edges = get_bin_edges(X_pca[:, 0], n_bins_pc1)
    pc2_edges = get_bin_edges(X_pca[:, 1], n_bins_pc2)

    pc1_bin = np.digitize(X_pca[:, 0], pc1_edges) - 1
    pc2_bin = np.digitize(X_pca[:, 1], pc2_edges) - 1
    pc1_bin = np.clip(pc1_bin, 0, n_bins_pc1 - 1)
    pc2_bin = np.clip(pc2_bin, 0, n_bins_pc2 - 1)
    df['cell'] = list(zip(pc1_bin, pc2_bin))
    cell_counts = df['cell'].value_counts()

    max_category = cell_counts.max()
    frames_data = []
    selected_indices = set()
    current_sample_count = 0

    # Frame 0: Original Data
    frames_data.append({
        'title': 'Original Data',
        'points_coords': X,
        'points_colors': y,
        'highlighted_cells': [],
        'remaining_text': '',
        'draw_grid': False,
        'xlabel': 'Feature 1',
        'ylabel': 'Feature 2'
    })

    # Frame 1: PCA Projection (all points skyblue)
    frames_data.append({
        'title': 'PCA Projection',
        'points_coords': X_pca,
        'points_colors': np.full(len(X_pca), 'skyblue', dtype=object),
        'highlighted_cells': [],
        'remaining_text': '',
        'draw_grid': True,
        'xlabel': 'PC1',
        'ylabel': 'PC2'
    })

    for k in range(1, max_category + 1):
        if current_sample_count >= target_sample_size:
            break
        category_cells = cell_counts[cell_counts == k].index
        category_indices = df[df['cell'].isin(category_cells)].index.tolist()
        n_category_points = len(category_indices)
        n_remaining = target_sample_size - current_sample_count

        # Highlighting Frame (yellow)
        temp_colors = np.full(len(X_pca), 'skyblue', dtype=object)
        temp_colors[list(selected_indices)] = 'red'  # Keep already selected points red
        # Points in currently highlighted cells: gray (unless already red)
        for idx in category_indices:
            if idx not in selected_indices:
                temp_colors[idx] = 'gray'
        current_highlight_patches = get_cell_patch_data(category_cells, 'yellow', n_bins_pc1, n_bins_pc2, pc1_edges, pc2_edges)
        frames_data.append({
            'title': f'Considering all cells with {k} point(s)',
            'points_coords': X_pca,
            'points_colors': temp_colors,
            'highlighted_cells': current_highlight_patches,
            'remaining_text': f'{n_remaining} points remaining',
            'draw_grid': True,
            'xlabel': 'PC1',
            'ylabel': 'PC2'
        })

        # Selection logic
        if n_category_points <= n_remaining:
            selected_now = set(category_indices)
        else:
            selected_now = set(random.sample(category_indices, n_remaining))
        selected_indices.update(selected_now)
        current_sample_count = len(selected_indices)

        # Retained Frame (red for picked, skyblue for others, no cell highlight)
        temp_colors2 = np.full(len(X_pca), 'skyblue', dtype=object)
        temp_colors2[list(selected_indices)] = 'red'  # All selected points remain red
        frames_data.append({
            'title': f'Retained {current_sample_count} points',
            'points_coords': X_pca,
            'points_colors': temp_colors2,
            'highlighted_cells': [],
            'remaining_text': f'{max(0, target_sample_size - current_sample_count)} points remaining',
            'draw_grid': True,
            'xlabel': 'PC1',
            'ylabel': 'PC2'
        })

    # Final frame: all selected points in red, others in skyblue
    temp_colors_final = np.full(len(X_pca), 'skyblue', dtype=object)
    temp_colors_final[list(selected_indices)] = 'red'  # All selected points remain red
    frames_data.append({
        'title': f'Final Sample: {len(selected_indices)} points selected',
        'points_coords': X_pca,
        'points_colors': temp_colors_final,
        'highlighted_cells': [],
        'remaining_text': 'Sampling complete',
        'draw_grid': True,
        'xlabel': 'PC1',
        'ylabel': 'PC2'
    })

    # Setup plot elements
    fig, ax = plt.subplots(figsize=(10, 8))
    scatter = ax.scatter([], [], s=40, alpha=0.8, zorder=2)
    ax.set_xlim(X_pca[:, 0].min() - 0.5, X_pca[:, 0].max() + 0.5)
    ax.set_ylim(X_pca[:, 1].min() - 0.5, X_pca[:, 1].max() + 0.5)
    ax.grid(False)

    grid_lines = []
    cell_patches_artists = []
    remaining_text_artist = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=12, verticalalignment='top', 
                                    bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.6), zorder=3)

    def clear_artists():
        nonlocal grid_lines, cell_patches_artists
        for line in grid_lines: line.remove()
        for patch in cell_patches_artists: patch.remove()
        grid_lines = []
        cell_patches_artists = []

    def draw_grid_lines_func():
        nonlocal grid_lines
        for x in pc1_edges:
            line = ax.axvline(x, color='gray', linestyle='--', alpha=0.4, linewidth=0.5, zorder=0)
            grid_lines.append(line)
        for y in pc2_edges:
            line = ax.axhline(y, color='gray', linestyle='--', alpha=0.4, linewidth=0.5, zorder=0)
            grid_lines.append(line)

    def init():
        scatter.set_offsets(np.empty((0, 2)))
        scatter.set_array(np.array([]))
        clear_artists()
        remaining_text_artist.set_text('')
        return scatter, remaining_text_artist
    
    def update(frame_idx):
        clear_artists()
        frame_data = frames_data[frame_idx]

        ax.set_title(frame_data['title'], fontsize=18)
        ax.set_xlabel(frame_data['xlabel'], fontsize=14)
        ax.set_ylabel(frame_data['ylabel'], fontsize=14)
        
        scatter.set_offsets(frame_data['points_coords'])

        if frame_data['points_colors'].dtype == object or isinstance(frame_data['points_colors'][0], str):
            scatter.set_array(None)
            scatter.set_color(frame_data['points_colors'])
            scatter.set_cmap(None)
        else:
            scatter.set_array(frame_data['points_colors'])
            scatter.set_cmap('viridis')
            scatter.set_color(None)

        remaining_text_artist.set_text(frame_data['remaining_text'])

        if frame_data['draw_grid']:
            draw_grid_lines_func()

        for patch_data in frame_data['highlighted_cells']:
            patch = Rectangle(patch_data['xy'], patch_data['width'], patch_data['height'], 
                              facecolor=patch_data['facecolor'], alpha=patch_data['alpha'], 
                              edgecolor=None, zorder=1)
            ax.add_patch(patch)
            cell_patches_artists.append(patch)
            
        return scatter, remaining_text_artist, *grid_lines, *cell_patches_artists

    anim = FuncAnimation(fig, update, frames=len(frames_data), init_func=init, interval=2500, blit=True)
    anim.save(output_file, writer='pillow', fps=0.5)
    plt.close()
    return output_file

def main():
    # Generate toy data
    X, y = generate_toy_data()
    
    # Create and save animation
    output_file = create_animation(X, y, target_sample_size=50, base_bins=8)
    print(f"Animation saved to: {output_file}")
    print(f"Total number of points: {len(X)}")

    # Recalculate cell counts to ensure it's based on the final binning
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)
    df = pd.DataFrame(X_pca, columns=['PC1', 'PC2'])

    # Use the same binning logic as in create_animation
    base_bins = 8  # This should match the call in create_animation
    n_bins_pc2 = base_bins
    n_bins_pc1 = 2 * base_bins
    pc1_edges = get_bin_edges(X_pca[:, 0], n_bins_pc1)
    pc2_edges = get_bin_edges(X_pca[:, 1], n_bins_pc2)

    pc1_bin = np.digitize(X_pca[:, 0], pc1_edges) - 1
    pc2_bin = np.digitize(X_pca[:, 1], pc2_edges) - 1
    pc1_bin = np.clip(pc1_bin, 0, n_bins_pc1 - 1)
    pc2_bin = np.clip(pc2_bin, 0, n_bins_pc2 - 1)
    df['cell'] = list(zip(pc1_bin, pc2_bin))
    cell_counts = df['cell'].value_counts()

    # Calculate counts for each category
    count_category_1 = len(cell_counts[cell_counts == 1])
    count_category_2 = len(cell_counts[cell_counts == 2])
    count_category_3_plus = len(cell_counts[cell_counts >= 3])

    print(f"Number of cells with 1 point: {count_category_1}")
    print(f"Number of cells with 2 points: {count_category_2}")
    print(f"Number of cells with 3+ points: {count_category_3_plus}")

if __name__ == "__main__":
    main() 
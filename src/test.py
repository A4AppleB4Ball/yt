import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

def draw_stickman(pose="neutral", expression="neutral", filename="output.png"):
    # 1. Activate "XKCD" mode for the hand-drawn look
    with plt.xkcd():
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.set_facecolor('black') # Background
        fig.patch.set_facecolor('black')
        
        # Hide axes
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')

        # PEN SETTINGS (Yellow, thick)
        pen_color = '#FFD700' # Gold/Yellow
        pen_width = 3.5

        # --- BODY PARTS COORDINATES ---
        # Head center (5, 8)
        
        # 2. Define Poses (The Puppet Logic)
        # Coordinates: [Start_X, Start_Y, End_X, End_Y]
        
        body = [5, 7.5, 5, 4]     # Torso
        legs = []
        arms = []
        
        if pose == "neutral":
            legs = [[5, 4, 4, 1], [5, 4, 6, 1]]      # Legs down
            arms = [[5, 6.5, 3.5, 4], [5, 6.5, 6.5, 4]] # Arms down
            
        elif pose == "shrug":
            legs = [[5, 4, 4, 1], [5, 4, 6, 1]]
            arms = [[5, 6.5, 3, 7], [5, 6.5, 7, 7]]  # Arms up/out
            
        elif pose == "thinking":
            legs = [[5, 4, 4, 1.5], [5, 4, 5, 1.5]] # Sittingish
            arms = [[5, 6.5, 4, 4], [5, 6.5, 6, 7.5]] # One arm up to chin

        # 3. Draw The Skeleton
        # Draw Torso
        ax.plot([body[0], body[2]], [body[1], body[3]], color=pen_color, lw=pen_width)
        
        # Draw Legs
        for leg in legs:
            ax.plot([leg[0], leg[2]], [leg[1], leg[3]], color=pen_color, lw=pen_width)
            
        # Draw Arms
        for arm in arms:
            ax.plot([arm[0], arm[2]], [arm[1], arm[3]], color=pen_color, lw=pen_width)

        # 4. Draw Head (Circle)
        # Using a slightly imperfect circle for hand-drawn look
        head = patches.Circle((5, 8), 1, edgecolor=pen_color, facecolor='none', lw=pen_width)
        ax.add_patch(head)

        # 5. Draw Face (Expression Logic)
        if expression == "neutral":
            # Eyes
            ax.plot([4.7, 4.7], [8.2, 8.4], color=pen_color, lw=pen_width) # L
            ax.plot([5.3, 5.3], [8.2, 8.4], color=pen_color, lw=pen_width) # R
            # Mouth (Flat)
            ax.plot([4.7, 5.3], [7.8, 7.8], color=pen_color, lw=pen_width)

        elif expression == "confused":
            # Eyes (One higher)
            ax.plot([4.7, 4.7], [8.1, 8.3], color=pen_color, lw=pen_width)
            ax.plot([5.3, 5.3], [8.3, 8.5], color=pen_color, lw=pen_width)
            # Mouth (Squiggly)
            ax.plot([4.8, 5.2], [7.8, 7.9], color=pen_color, lw=pen_width)

        plt.savefig(filename, dpi=100, bbox_inches='tight')
        plt.close()

# TEST IT
draw_stickman(pose="shrug", expression="confused", filename="shrug.png")
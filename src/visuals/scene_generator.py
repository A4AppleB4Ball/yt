"""
Scene Generator - Creates visual scenes for video segments.

Generates:
- Chart scenes (price charts, data overlays)
- Diagram scenes (frameworks, flow diagrams)
- Text scenes (title cards, quotes)
- Split screen scenes (comparisons)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path as MplPath
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import re


class SceneGenerator:
    """Generate visual scenes for video production."""

    def __init__(self, output_dir: str = "output/scenes", resolution: Tuple[int, int] = (1920, 1080)):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.width, self.height = resolution

        # Style settings
        self.bg_color = '#0a0a0a'  # Dark background
        self.primary_color = '#FFD700'  # Gold
        self.secondary_color = '#FF6B6B'  # Red
        self.accent_color = '#4ECDC4'  # Teal
        self.text_color = '#FFFFFF'  # White
        self.grid_color = '#2a2a2a'  # Dark gray

    def _create_base_image(self, bg_color: Optional[str] = None) -> Image.Image:
        """Create base image with background."""
        bg = bg_color or self.bg_color
        img = Image.new('RGB', (self.width, self.height), bg)
        return img

    def generate_title_card(
        self,
        title: str,
        subtitle: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate a title card scene.

        Args:
            title: Main title text
            subtitle: Optional subtitle
            output_path: Output file path

        Returns:
            Path to generated image
        """
        img = self._create_base_image()
        draw = ImageDraw.Draw(img)

        # Try to use a nice font, fall back to default
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 120)
            subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()

        # Draw title
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_w = title_bbox[2] - title_bbox[0]
        title_h = title_bbox[3] - title_bbox[1]
        title_x = (self.width - title_w) // 2
        title_y = (self.height - title_h) // 2 - 50

        draw.text((title_x, title_y), title, fill=self.primary_color, font=title_font)

        # Draw subtitle if provided
        if subtitle:
            subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
            subtitle_w = subtitle_bbox[2] - subtitle_bbox[0]
            subtitle_x = (self.width - subtitle_w) // 2
            subtitle_y = title_y + title_h + 40

            draw.text((subtitle_x, subtitle_y), subtitle, fill=self.text_color, font=subtitle_font)

        # Save
        if not output_path:
            output_path = self.output_dir / "title_card.png"
        img.save(output_path)

        return str(output_path)

    def generate_chart_scene(
        self,
        title: str,
        data: Optional[Dict] = None,
        annotations: Optional[List[str]] = None,
        output_path: Optional[str] = None,
        chart_type: str = "line"
    ) -> str:
        """
        Generate a chart scene (Bitcoin price chart, etc.).

        Args:
            title: Chart title
            data: Chart data (if None, generates placeholder)
            annotations: Text annotations to overlay
            output_path: Output file path
            chart_type: Type of chart ('line', 'candlestick', 'area')

        Returns:
            Path to generated image
        """
        with plt.style.context('dark_background'):
            fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
            fig.patch.set_facecolor(self.bg_color)
            ax.set_facecolor(self.bg_color)

            # Generate placeholder data if none provided
            if data is None:
                x = np.arange(0, 100)
                y = 90000 + np.cumsum(np.random.randn(100) * 1000)
                data = {'x': x, 'y': y, 'label': 'BTC Price'}

            # Plot based on chart type
            if chart_type == "line":
                ax.plot(data['x'], data['y'], color=self.primary_color, linewidth=3, label=data.get('label', ''))
            elif chart_type == "area":
                ax.fill_between(data['x'], data['y'], alpha=0.3, color=self.primary_color)
                ax.plot(data['x'], data['y'], color=self.primary_color, linewidth=2)

            # Styling
            ax.set_title(title, fontsize=32, color=self.text_color, pad=20, fontweight='bold')
            ax.grid(True, alpha=0.2, color=self.grid_color)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color(self.grid_color)
            ax.spines['bottom'].set_color(self.grid_color)
            ax.tick_params(colors=self.text_color, labelsize=14)

            # Add annotations if provided
            if annotations:
                for i, annotation in enumerate(annotations):
                    ax.text(
                        0.05, 0.95 - (i * 0.08),
                        annotation,
                        transform=ax.transAxes,
                        fontsize=18,
                        color=self.accent_color,
                        verticalalignment='top',
                        bbox=dict(boxstyle='round', facecolor=self.bg_color, alpha=0.8, edgecolor=self.accent_color)
                    )

            plt.tight_layout()

            if not output_path:
                output_path = self.output_dir / f"chart_{title.lower().replace(' ', '_')}.png"

            plt.savefig(output_path, facecolor=self.bg_color, dpi=100)
            plt.close()

            return str(output_path)

    def generate_diagram_scene(
        self,
        title: str,
        diagram_type: str,
        elements: List[str],
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate a diagram scene (flow chart, comparison, framework).

        Args:
            title: Diagram title
            diagram_type: Type ('flow', 'comparison', 'framework')
            elements: List of elements to display
            output_path: Output file path

        Returns:
            Path to generated image
        """
        with plt.style.context('dark_background'):
            fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
            fig.patch.set_facecolor(self.bg_color)
            ax.set_facecolor(self.bg_color)
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 10)
            ax.axis('off')

            # Title
            ax.text(5, 9.5, title, ha='center', va='top', fontsize=36,
                   color=self.primary_color, fontweight='bold')

            if diagram_type == "flow":
                self._draw_flow_diagram(ax, elements)
            elif diagram_type == "comparison":
                self._draw_comparison_diagram(ax, elements)
            elif diagram_type == "framework":
                self._draw_framework_diagram(ax, elements)

            plt.tight_layout()

            if not output_path:
                output_path = self.output_dir / f"diagram_{title.lower().replace(' ', '_')}.png"

            plt.savefig(output_path, facecolor=self.bg_color, dpi=100)
            plt.close()

            return str(output_path)

    def _draw_flow_diagram(self, ax, elements: List[str]):
        """Draw a flow diagram."""
        y_start = 7
        y_step = 2
        box_height = 0.8

        for i, element in enumerate(elements):
            y = y_start - (i * y_step)

            # Box
            rect = patches.FancyBboxPatch(
                (2, y - box_height/2), 6, box_height,
                boxstyle="round,pad=0.1",
                edgecolor=self.primary_color,
                facecolor=self.bg_color,
                linewidth=3
            )
            ax.add_patch(rect)

            # Text
            ax.text(5, y, element, ha='center', va='center',
                   fontsize=20, color=self.text_color, wrap=True)

            # Arrow to next element
            if i < len(elements) - 1:
                ax.annotate('', xy=(5, y - box_height/2 - 0.2),
                           xytext=(5, y - box_height/2 - y_step + 0.2),
                           arrowprops=dict(arrowstyle='->', lw=3, color=self.accent_color))

    def _draw_comparison_diagram(self, ax, elements: List[str]):
        """Draw a comparison diagram (split screen)."""
        if len(elements) != 2:
            elements = elements[:2] + [''] * (2 - len(elements))

        # Left side
        rect_left = patches.FancyBboxPatch(
            (0.5, 2), 4, 5,
            boxstyle="round,pad=0.2",
            edgecolor=self.secondary_color,
            facecolor=self.bg_color,
            linewidth=3
        )
        ax.add_patch(rect_left)
        ax.text(2.5, 4.5, elements[0], ha='center', va='center',
               fontsize=24, color=self.text_color, wrap=True)

        # Right side
        rect_right = patches.FancyBboxPatch(
            (5.5, 2), 4, 5,
            boxstyle="round,pad=0.2",
            edgecolor=self.accent_color,
            facecolor=self.bg_color,
            linewidth=3
        )
        ax.add_patch(rect_right)
        ax.text(7.5, 4.5, elements[1], ha='center', va='center',
               fontsize=24, color=self.text_color, wrap=True)

        # VS text
        ax.text(5, 4.5, "VS", ha='center', va='center',
               fontsize=48, color=self.primary_color, fontweight='bold')

    def _draw_framework_diagram(self, ax, elements: List[str]):
        """Draw a framework diagram (circular or hierarchical)."""
        # Simple 3-layer circular framework
        center_x, center_y = 5, 4.5

        if len(elements) >= 3:
            # Center element
            circle_center = patches.Circle(
                (center_x, center_y), 0.8,
                edgecolor=self.primary_color,
                facecolor=self.bg_color,
                linewidth=3
            )
            ax.add_patch(circle_center)
            ax.text(center_x, center_y, elements[0], ha='center', va='center',
                   fontsize=16, color=self.text_color)

            # Surrounding elements
            radius = 2.5
            angles = np.linspace(0, 2*np.pi, len(elements[1:]), endpoint=False)

            for i, (angle, element) in enumerate(zip(angles, elements[1:])):
                x = center_x + radius * np.cos(angle)
                y = center_y + radius * np.sin(angle)

                circle = patches.Circle(
                    (x, y), 0.7,
                    edgecolor=self.accent_color,
                    facecolor=self.bg_color,
                    linewidth=2
                )
                ax.add_patch(circle)

                # Wrap text
                wrapped = element[:15] + '...' if len(element) > 15 else element
                ax.text(x, y, wrapped, ha='center', va='center',
                       fontsize=14, color=self.text_color)

                # Line to center
                ax.plot([center_x, x], [center_y, y],
                       color=self.grid_color, linewidth=2, linestyle='--', alpha=0.5)

    def generate_text_overlay(
        self,
        text: str,
        position: str = "center",
        output_path: Optional[str] = None,
        background: Optional[str] = None
    ) -> str:
        """
        Generate a text overlay scene.

        Args:
            text: Text to display
            position: Position ('top', 'center', 'bottom')
            output_path: Output file path
            background: Optional background image path

        Returns:
            Path to generated image
        """
        if background:
            img = Image.open(background).resize((self.width, self.height))
            # Darken background
            img = img.point(lambda p: p * 0.4)
        else:
            img = self._create_base_image()

        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 80)
        except:
            font = ImageFont.load_default()

        # Calculate position
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_x = (self.width - text_w) // 2

        if position == "top":
            text_y = self.height // 6
        elif position == "bottom":
            text_y = self.height - self.height // 6 - text_h
        else:  # center
            text_y = (self.height - text_h) // 2

        # Draw text with shadow for better visibility
        shadow_offset = 4
        draw.text((text_x + shadow_offset, text_y + shadow_offset), text,
                 fill='#000000', font=font)
        draw.text((text_x, text_y), text, fill=self.primary_color, font=font)

        if not output_path:
            output_path = self.output_dir / "text_overlay.png"

        img.save(output_path)
        return str(output_path)


if __name__ == "__main__":
    # Test scene generation
    generator = SceneGenerator()

    print("Generating test scenes...")

    # Title card
    generator.generate_title_card(
        "Markets Don't Move on News",
        "They Already Moved"
    )
    print("✅ Title card generated")

    # Chart scene
    generator.generate_chart_scene(
        "Bitcoin Price Chart",
        annotations=["Rally to $125k", "Then -36% drop"]
    )
    print("✅ Chart scene generated")

    # Diagram scene
    generator.generate_diagram_scene(
        "Retail vs Reality",
        diagram_type="comparison",
        elements=["News → Reaction → Price", "Liquidity → Flows → Regime → News"]
    )
    print("✅ Diagram scene generated")

    print("\n✨ All test scenes generated in output/scenes/")

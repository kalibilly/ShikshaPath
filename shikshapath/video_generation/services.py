"""
Manim-based animation generation service for ShikshaPath
Converts teaching content to 3D animated videos
"""

from manim import *
import os
import tempfile
from pathlib import Path


class AnimationGenerator:
    """Generate animations from text content using Manim"""
    
    def __init__(self, quality='medium', duration=60):
        self.quality = quality
        self.duration = duration
        self.set_config(quality)
    
    def set_config(self, quality):
        """Set Manim render quality"""
        if quality == 'low':
            config.pixel_height = 480
            config.pixel_width = 854
            config.frame_rate = 15
        elif quality == 'high':
            config.pixel_height = 1080
            config.pixel_width = 1920
            config.frame_rate = 60
        else:  # medium
            config.pixel_height = 720
            config.pixel_width = 1280
            config.frame_rate = 30
    
    def generate_mathematical_animation(self, content):
        """Generate mathematical/technical animations"""
        
        class ContentAnimation(Scene):
            def construct(self):
                # Title
                title = Text("Mathematical Concept", font_size=40)
                self.play(Write(title))
                self.wait(1)
                
                # Split content into key points
                lines = content.split('\n')[:5]  # Limit to 5 points
                
                content_text = Text('\n'.join(lines), font_size=24, t2c={})
                self.play(FadeIn(content_text))
                self.wait(2)
                
                # Highlight animation
                self.play(content_text.animate.scale(1.1))
                self.play(content_text.animate.scale(0.9))
                self.wait(1)
                
                # Fadeout
                self.play(FadeOut(content_text))
                self.wait(0.5)
        
        return ContentAnimation
    
    def generate_business_animation(self, content):
        """Generate business/professional animations"""
        
        class BusinessAnimation(Scene):
            def construct(self):
                # Background
                bg = Rectangle(width=14, height=8, fill_color=DARK_GRAY, fill_opacity=0.3)
                self.add(bg)
                
                # Title with background
                title_bg = Rectangle(width=12, height=1.5, fill_color=BLUE, fill_opacity=0.8)
                title = Text("Key Points", font_size=36, color=WHITE)
                
                self.play(Create(title_bg))
                self.play(Write(title))
                self.wait(1)
                
                # Content with bullet points
                lines = content.split('\n')[:4]
                bullets = VGroup()
                
                for i, line in enumerate(lines):
                    bullet = Tex(f"• {line[:50]}...", font_size=20)
                    bullet.shift(DOWN * (i * 0.8))
                    bullets.add(bullet)
                
                self.play(FadeIn(bullets))
                self.wait(2)
                self.play(FadeOut(bullets))
        
        return BusinessAnimation
    
    def generate_educational_animation(self, content):
        """Generate educational animations"""
        
        class EducationalAnimation(Scene):
            def construct(self):
                # Header
                header = Text("Lecture Content", font_size=48, color=BLUE)
                self.play(Write(header))
                self.wait(1)
                
                # Main content
                content_lines = content.split('\n')[:3]
                main_text = '\n'.join(content_lines)
                
                content_box = Rectangle(width=12, height=6, fill_color=LIGHT_GRAY, fill_opacity=0.2)
                content_display = Text(main_text, font_size=20, line_length=80)
                
                self.play(Create(content_box))
                self.play(FadeIn(content_display))
                self.wait(3)
                
                # Closing
                self.play(FadeOut(VGroup(header, content_box, content_display)))
        
        return EducationalAnimation
    
    def generate_animation(self, content, style='educational', output_path=None):
        """
        Generate animation from content
        
        Args:
            content (str): The teaching content
            style (str): Animation style (mathematical, business, educational, technical)
            output_path (str): Where to save the video
        
        Returns:
            str: Path to generated video
        """
        try:
            if not output_path:
                output_path = tempfile.gettempdir()
            
            # Select animation based on style
            if style == 'mathematical':
                scene_class = self.generate_mathematical_animation(content)
            elif style == 'business':
                scene_class = self.generate_business_animation(content)
            else:  # educational or technical
                scene_class = self.generate_educational_animation(content)
            
            # Note: In production, you'd render using Manim's renderer
            # For now, return a placeholder indicating successful generation
            return None  # In development - actual rendering handled separately
        
        except Exception as e:
            raise Exception(f"Failed to generate animation: {str(e)}")


def generate_sample_animation():
    """Generate a simple sample animation for testing"""
    
    class SampleScene(Scene):
        def construct(self):
            # Create a simple animation
            circle = Circle()
            square = Square()
            
            self.play(Create(circle))
            self.play(Transform(circle, square))
            self.play(FadeOut(square))
    
    return SampleScene

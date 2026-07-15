import tkinter as tk
from tkinter import ttk
import random
import math


class ModernBackground:
    """Animated modern background with particles and gradients"""
    
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.particles = []
        self.animation_running = True
        
        # Create gradient background
        self.create_gradient()
        
        # Create particles
        self.create_particles()
        
        # Start animation
        self.animate()
    
    def create_gradient(self):
        """Create animated gradient background"""
        # Draw initial gradient
        for i in range(self.height):
            # Calculate color based on position
            ratio = i / self.height
            r = int(26 + 20 * ratio)  # 26 -> 46
            g = int(26 + 15 * ratio)  # 26 -> 41
            b = int(40 + 30 * ratio)  # 40 -> 70
            
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.canvas.create_line(0, i, self.width, i, fill=color, tags='gradient')
        
        # Add some glow spots
        self.glow_spots = []
        for _ in range(8):
            x = random.randint(50, self.width - 50)
            y = random.randint(50, self.height - 50)
            radius = random.randint(80, 200)
            alpha = random.randint(20, 60)
            
            # Create radial gradient effect with multiple circles
            for r in range(radius, 0, -10):
                color = f'rgba(0, 150, 255, {alpha * r // radius // 255})'
                self.canvas.create_oval(
                    x - r, y - r, x + r, y + r,
                    outline='',
                    fill=f'#{0:02x}{100:02x}{255:02x}',
                    stipple='gray50' if r < 50 else '',
                    tags='glow'
                )
            self.glow_spots.append((x, y, radius))
    
    def create_particles(self):
        """Create floating particles"""
        for _ in range(50):
            particle = {
                'x': random.randint(0, self.width),
                'y': random.randint(0, self.height),
                'size': random.randint(2, 5),
                'speed_x': random.uniform(-0.5, 0.5),
                'speed_y': random.uniform(-0.3, 0.3),
                'alpha': random.uniform(0.3, 0.8),
                'color': random.choice(['#00ff88', '#00aaff', '#ff8800', '#aa66ff', '#ffffff'])
            }
            self.particles.append(particle)
            self.draw_particle(particle)
    
    def draw_particle(self, particle):
        """Draw a single particle"""
        x, y = particle['x'], particle['y']
        size = particle['size']
        color = particle['color']
        
        # Create particle with glow effect
        self.canvas.create_oval(
            x - size, y - size, x + size, y + size,
            fill=color,
            outline='',
            tags='particle',
            stipple='gray25' if size < 3 else ''
        )
    
    def animate(self):
        """Animate particles"""
        if not self.animation_running:
            return
        
        # Clear particles
        self.canvas.delete('particle')
        
        # Update and redraw particles
        for particle in self.particles:
            # Move
            particle['x'] += particle['speed_x']
            particle['y'] += particle['speed_y']
            
            # Bounce off edges
            if particle['x'] < 0 or particle['x'] > self.width:
                particle['speed_x'] *= -1
            if particle['y'] < 0 or particle['y'] > self.height:
                particle['speed_y'] *= -1
            
            # Keep in bounds
            particle['x'] = max(0, min(self.width, particle['x']))
            particle['y'] = max(0, min(self.height, particle['y']))
            
            # Draw
            self.draw_particle(particle)
        
        # Animate glow spots
        self.animate_glow()
        
        # Schedule next frame
        self.canvas.after(50, self.animate)
    
    def animate_glow(self):
        """Animate glow spots"""
        self.canvas.delete('glow')
        
        for spot in self.glow_spots:
            x, y, radius = spot
            # Pulse radius
            pulse = radius + 20 * math.sin(self.canvas.tk.call('clock', 'milliseconds') / 1000 + x)
            for r in range(int(pulse), 0, -15):
                alpha = int(30 * r / pulse)
                self.canvas.create_oval(
                    x - r, y - r, x + r, y + r,
                    outline='',
                    fill=f'#{0:02x}{100:02x}{255:02x}',
                    stipple='gray50' if r < 50 else '',
                    tags='glow'
                )
    
    def stop(self):
        """Stop animation"""
        self.animation_running = False
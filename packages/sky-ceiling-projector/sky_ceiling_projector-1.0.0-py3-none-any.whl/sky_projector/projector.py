#!/usr/bin/env python3
"""
Sky Ceiling Projector for Raspberry Pi Zero W
Simplified version with reliable weather effects, restored detailed clouds and moon,
plus smooth color transitions between locations.
"""

from __future__ import annotations

import pygame
import requests
import json
import math
import random
import time
from datetime import datetime, timezone, timedelta
import numpy as np
from threading import Thread
import queue
from collections import deque
from typing import Tuple
import pytz  # For timezone handling

# Default configuration
DEFAULT_SCREEN_WIDTH = 1920
DEFAULT_SCREEN_HEIGHT = 1080
DEFAULT_FPS = 30
WEATHER_UPDATE_INTERVAL = 600  # Update weather every 10 minutes

# Quality presets
QUALITY_SETTINGS = {
    "performance": {
        "star_count": 150,
        "max_clouds": 8,
        "max_particles": 100,
        "enable_glow": False,
        "star_twinkle": True,
        "cloud_shadows": False,
    },
    "balanced": {
        "star_count": 250,
        "max_clouds": 15,
        "max_particles": 200,
        "enable_glow": True,
        "star_twinkle": True,
        "cloud_shadows": True,
    },
    "quality": {
        "star_count": 400,
        "max_clouds": 25,
        "max_particles": 300,
        "enable_glow": True,
        "star_twinkle": True,
        "cloud_shadows": True,
    }
}

# Debug weather conditions for testing
DEBUG_WEATHER_CONDITIONS = [
    "Clear",
    "Clouds", 
    "Rain",
    "Snow",
    "Thunderstorm",
    "Drizzle",
    "Fog"
]


def smooth_step(t):
    """Smooth interpolation function for transitions"""
    return t * t * (3.0 - 2.0 * t)


def ease_in_out_cubic(t):
    """Cubic easing for very smooth transitions"""
    return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2


def geocode_location(query: str,
                     *,
                     country_code: str | None = None,
                     user_agent: str = "sky_projector",
                     timeout: int = 5
                     ) -> Tuple[float, float, str, str]:
    """
    Resolve a human location string to (lat, lon, timezone, nice_name).
    """
    # Open-Meteo
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {"name": query, "count": 1}
        if country_code:
            params["country_code"] = country_code
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        if data.get("results"):
            rec = data["results"][0]
            lat = rec["latitude"]
            lon = rec["longitude"]
            tz  = rec.get("timezone", "UTC")
            nice_name = f"{rec['name']}, {rec.get('country_code', '')}".strip(", ")
            return lat, lon, tz, nice_name
    except Exception:
        pass  # fall through

    # geopy → Nominatim (OpenStreetMap) - Optional fallback
    try:
        from geopy.geocoders import Nominatim  # pip install geopy
        nom = Nominatim(user_agent=user_agent)
        loc = nom.geocode(query, exactly_one=True, timeout=timeout)
        if loc:
            lat, lon = loc.latitude, loc.longitude
            nice_name = loc.address.split(",")[0]
            try:
                from timezonefinder import TimezoneFinder      # pip install timezonefinder
                tf = TimezoneFinder()
                tz = tf.timezone_at(lat=lat, lng=lon) or "UTC"
            except Exception:
                tz = "UTC"
            return lat, lon, tz, nice_name
    except Exception as e:
        error = str(e)
    raise RuntimeError(f"Could not geocode '{query}'. {error if 'error' in locals() else ''}")


class DetailedCloud:
    """Restored detailed cloud class with realistic shapes and caching"""
    def __init__(self, x, y, size, speed, opacity, screen_width, screen_height):
        self.x = x
        self.y = y
        self.size = size
        self.base_speed = speed
        self.speed = speed
        self.opacity = opacity
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.blobs = []
        self.detail_level = random.randint(4, 8)
        
        # Pre-rendered cloud surfaces for performance
        self.cached_surface = None
        self.cached_shadow_surface = None
        self.cache_valid = False
        
        # Generate realistic cloud shapes with stretching and irregularity
        cloud_stretch_x = random.uniform(1.2, 2.5)  # Horizontal stretching
        cloud_stretch_y = random.uniform(0.6, 1.0)  # Vertical compression
        wind_shear = random.uniform(-0.3, 0.3)      # Wind shearing effect
        
        for i in range(self.detail_level):
            angle = random.uniform(0, 2 * math.pi)
            # Create more natural distribution with some randomness
            distance_factor = random.betavariate(1.5, 3)  # More spread out
            distance = distance_factor * size * 0.6
            
            # Apply wind shear and stretching for realistic shapes
            base_x = math.cos(angle) * distance * cloud_stretch_x
            base_y = math.sin(angle) * distance * cloud_stretch_y
            
            # Add wind shear effect (higher parts of cloud drift more)
            shear_offset = wind_shear * abs(base_y) * 0.5
            blob_x = base_x + shear_offset
            blob_y = base_y
            
            # Create elliptical blobs instead of circular
            if i < 2:  # Core blobs are larger and more stretched
                blob_width = random.uniform(size * 0.4, size * 0.7) * cloud_stretch_x
                blob_height = random.uniform(size * 0.3, size * 0.5) * cloud_stretch_y
            else:  # Outer blobs are smaller and wispier
                blob_width = random.uniform(size * 0.15, size * 0.4) * cloud_stretch_x
                blob_height = random.uniform(size * 0.1, size * 0.3) * cloud_stretch_y
            
            # Add some rotation for more natural look
            blob_rotation = random.uniform(-30, 30)  # degrees
            
            self.blobs.append((blob_x, blob_y, blob_width, blob_height, blob_rotation))
    
    def update(self, dt):
        # Add subtle vertical movement for realism
        self.y += math.sin(self.x * 0.001 + time.time() * 0.1) * 8 * dt
        self.x += self.speed * dt
        
        # Invalidate cache when cloud moves significantly
        if abs(self.speed * dt) > 5:
            self.cache_valid = False
        
        if self.x > self.screen_width + self.size:
            self.x = -self.size * 2
            self.y = random.uniform(0, self.screen_height * 0.6)
            self.cache_valid = False  # Invalidate cache for new position
    
    def get_cached_surface(self, cloud_color, light_factor, settings):
        """Get or create cached cloud surface for performance"""
        cache_key = (cloud_color, int(light_factor * 10), int(self.opacity * 10))
        
        if not self.cache_valid or self.cached_surface is None:
            # Create new cached surface
            max_size = int(self.size * 3)  # Larger to accommodate stretched shapes
            self.cached_surface = pygame.Surface((max_size, max_size), pygame.SRCALPHA)
            
            # Draw wispy, stretched cloud blobs
            for blob_x, blob_y, blob_width, blob_height, rotation in self.blobs:
                blob_center_x = max_size // 2 + blob_x
                blob_center_y = max_size // 2 + blob_y
                
                # Create elliptical blob with rotation
                blob_surf = pygame.Surface((int(blob_width * 2.5), int(blob_height * 2.5)), pygame.SRCALPHA)
                blob_rect = pygame.Rect(0, 0, int(blob_width * 2), int(blob_height * 2))
                blob_rect.center = (int(blob_width * 1.25), int(blob_height * 1.25))
                
                # Draw 3 layers for volume effect
                for layer in [3, 2, 1]:
                    layer_width = int(blob_width * (0.4 + layer * 0.25))
                    layer_height = int(blob_height * (0.4 + layer * 0.25))
                    layer_opacity = int(self.opacity * 180 * (0.3 + layer * 0.2))
                    
                    # Calculate lit color
                    brightness = light_factor * (0.75 + layer * 0.1)
                    lit_color = tuple(min(255, int(c * brightness)) for c in cloud_color)
                    
                    # Draw elliptical shape instead of circle
                    if layer_width > 0 and layer_height > 0:
                        layer_rect = pygame.Rect(0, 0, layer_width * 2, layer_height * 2)
                        layer_rect.center = blob_rect.center
                        
                        temp_surf = pygame.Surface((layer_width * 2, layer_height * 2), pygame.SRCALPHA)
                        pygame.draw.ellipse(temp_surf, lit_color, (0, 0, layer_width * 2, layer_height * 2))
                        temp_surf.set_alpha(layer_opacity)
                        
                        # Rotate the blob surface
                        if rotation != 0:
                            temp_surf = pygame.transform.rotate(temp_surf, rotation)
                        
                        # Blit to blob surface
                        blob_surf.blit(temp_surf, (layer_rect.x - blob_rect.x, layer_rect.y - blob_rect.y))
                
                # Blit blob to main surface
                blob_rect_main = blob_surf.get_rect()
                blob_rect_main.center = (int(blob_center_x), int(blob_center_y))
                self.cached_surface.blit(blob_surf, blob_rect_main.topleft)
            
            self.cache_valid = True
        
        return self.cached_surface
    
    def draw(self, screen, cloud_color, settings, sun_pos=None):
        # Calculate lighting based on sun position
        light_factor = 1.0
        shadow_offset_x = 0
        shadow_offset_y = 0
        
        if sun_pos:
            # Calculate lighting direction from sun
            sun_angle = math.atan2(sun_pos[1] - self.y, sun_pos[0] - self.x)
            light_factor = 0.7 + 0.3 * max(0, math.cos(sun_angle + math.pi * 0.25))
            shadow_offset_x = -math.cos(sun_angle) * 12
            shadow_offset_y = -math.sin(sun_angle) * 6
        
        # Draw shadow first if enabled
        if settings["cloud_shadows"] and sun_pos:
            shadow_alpha = int(self.opacity * 80)
            shadow_surf = pygame.Surface((int(self.size * 2), int(self.size * 1.2)), pygame.SRCALPHA)
            
            # Stretched elliptical shadow
            pygame.draw.ellipse(shadow_surf, (0, 0, 0), 
                              (0, 0, int(self.size * 2), int(self.size * 1.2)))
            shadow_surf.set_alpha(shadow_alpha)
            
            shadow_x = self.x + shadow_offset_x - self.size
            shadow_y = self.y + shadow_offset_y - self.size * 0.6
            screen.blit(shadow_surf, (int(shadow_x), int(shadow_y)))
        
        # Get cached cloud surface
        cloud_surf = self.get_cached_surface(cloud_color, light_factor, settings)
        
        # Draw the cached cloud
        if cloud_surf:
            cloud_x = self.x - cloud_surf.get_width() // 2
            cloud_y = self.y - cloud_surf.get_height() // 2
            screen.blit(cloud_surf, (int(cloud_x), int(cloud_y)))


class Star:
    def __init__(self, x, y, brightness, twinkle_speed, size_class="normal", color_temp=1.0, star_type="normal"):
        self.x = x
        self.y = y
        self.base_brightness = brightness
        self.brightness = brightness
        self.twinkle_speed = twinkle_speed
        self.twinkle_phase = random.uniform(0, 2 * math.pi)
        self.size_class = size_class
        self.color_temp = color_temp  # 0=red, 0.5=yellow, 1=white/blue
        self.star_type = star_type  # "normal", "variable", "giant", "supergiant"
        
        # Variable star properties
        if star_type == "variable":
            self.variable_period = random.uniform(3, 15)  # seconds
            self.variable_amplitude = random.uniform(0.3, 0.7)
            self.variable_phase = random.uniform(0, 2 * math.pi)
        
        # Giant star properties
        if star_type in ["giant", "supergiant"]:
            self.pulse_speed = random.uniform(0.5, 2.0)
            self.pulse_phase = random.uniform(0, 2 * math.pi)
        
    def update(self, dt, settings):
        base_brightness = self.base_brightness
        
        # Variable star pulsing
        if self.star_type == "variable":
            self.variable_phase += (2 * math.pi / self.variable_period) * dt
            variable_factor = 1 + self.variable_amplitude * math.sin(self.variable_phase)
            base_brightness *= variable_factor
        
        # Giant star slow pulsing
        if self.star_type in ["giant", "supergiant"]:
            self.pulse_phase += self.pulse_speed * dt
            pulse_factor = 1 + 0.2 * math.sin(self.pulse_phase)
            base_brightness *= pulse_factor
        
        # Regular twinkling
        if settings["star_twinkle"]:
            self.twinkle_phase += self.twinkle_speed * dt
            base_twinkle = math.sin(self.twinkle_phase)
            shimmer = math.sin(self.twinkle_phase * 3.7) * 0.1
            self.brightness = base_brightness * (0.8 + 0.2 * base_twinkle + shimmer)
        else:
            self.brightness = base_brightness
        
    def draw(self, screen, settings):
        if self.brightness > 0.01:
            # Enhanced size based on brightness and class
            size_mult = {
                "dim": 0.5, 
                "normal": 1, 
                "bright": 1.5, 
                "super": 2.5,
                "giant": 3.0,
                "supergiant": 4.0
            }.get(self.size_class, 1)
            
            size = max(1, int(self.brightness * 4 * size_mult))  # Increased base size for more vibrant look
            
            # Enhanced color palette for more vibrant stars
            if self.color_temp < 0.2:  # Red giants/supergiants
                r, g, b = 255, int(120 * (self.color_temp * 5)), int(80 * (self.color_temp * 5))
            elif self.color_temp < 0.35:  # Orange stars
                r, g, b = 255, int(180 + 75 * ((self.color_temp - 0.2) * 6.67)), int(100 + 80 * ((self.color_temp - 0.2) * 6.67))
            elif self.color_temp < 0.55:  # Yellow stars (like our Sun)
                r, g, b = 255, int(220 + 35 * ((self.color_temp - 0.35) * 5)), int(160 + 80 * ((self.color_temp - 0.35) * 5))
            elif self.color_temp < 0.75:  # White stars
                r, g, b = 255, 255, int(200 + 55 * ((self.color_temp - 0.55) * 5))
            else:  # Blue giants/supergiants
                r = int(255 - 100 * ((self.color_temp - 0.75) * 4))
                g = int(255 - 30 * ((self.color_temp - 0.75) * 4))
                b = 255
            
            # Boost saturation for more vibrant appearance
            saturation_boost = 1.3 if self.star_type in ["giant", "supergiant"] else 1.15
            
            # Apply brightness and saturation
            color = (
                min(255, int(r * self.brightness * saturation_boost)),
                min(255, int(g * self.brightness * saturation_boost)),
                min(255, int(b * self.brightness * saturation_boost))
            )
            
            # Enhanced glow for brighter stars
            if settings["enable_glow"] and size > 2:
                glow_layers = 3 if self.star_type in ["giant", "supergiant"] else 2
                for i in range(glow_layers):
                    glow_size = size * (3 + i * 2)
                    glow_alpha = int(40 / (i + 1))
                    
                    glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                    glow_color = tuple(min(255, int(c * 0.8)) for c in color)
                    pygame.draw.circle(glow_surf, glow_color, (glow_size, glow_size), glow_size)
                    glow_surf.set_alpha(glow_alpha)
                    screen.blit(glow_surf, (int(self.x - glow_size), int(self.y - glow_size)))
            
            # Draw main star with enhanced appearance
            if size > 3:
                # Draw star with subtle cross pattern for bright stars
                pygame.draw.circle(screen, color, (int(self.x), int(self.y)), size)
                
                # Add cross spikes for very bright stars
                if self.star_type in ["giant", "supergiant"] or self.size_class in ["super"]:
                    spike_length = size * 2
                    spike_color = tuple(int(c * 0.7) for c in color)
                    # Horizontal spike
                    pygame.draw.line(screen, spike_color, 
                                   (int(self.x - spike_length), int(self.y)), 
                                   (int(self.x + spike_length), int(self.y)), 2)
                    # Vertical spike
                    pygame.draw.line(screen, spike_color, 
                                   (int(self.x), int(self.y - spike_length)), 
                                   (int(self.x), int(self.y + spike_length)), 2)
            else:
                pygame.draw.circle(screen, color, (int(self.x), int(self.y)), size)


class EnhancedShootingStar:
    def __init__(self, screen_width, screen_height):
        # Start from random edge with more variety
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        edge = random.randint(0, 3)
        if edge == 0:  # Top
            self.x = random.uniform(0, screen_width)
            self.y = -20
        elif edge == 1:  # Right
            self.x = screen_width + 20
            self.y = random.uniform(0, screen_height)
        elif edge == 2:  # Bottom
            self.x = random.uniform(0, screen_width)
            self.y = screen_height + 20
        else:  # Left
            self.x = -20
            self.y = random.uniform(0, screen_height)
        
        # Enhanced direction towards center with more variation
        center_x = random.uniform(screen_width * 0.2, screen_width * 0.8)
        center_y = random.uniform(screen_height * 0.2, screen_height * 0.8)
        angle = math.atan2(center_y - self.y, center_x - self.x)
        
        # Different types of meteors
        meteor_type = random.choice(["fast", "slow", "bright", "long"])
        
        if meteor_type == "fast":
            speed = random.uniform(800, 1200)
            self.trail_length = 35
            self.color = (255, 255, 200)  # Yellow-white
        elif meteor_type == "slow":
            speed = random.uniform(300, 500)
            self.trail_length = 20
            self.color = (255, 200, 150)  # Orange
        elif meteor_type == "bright":
            speed = random.uniform(600, 900)
            self.trail_length = 45
            self.color = (200, 255, 255)  # Blue-white fireball
        else:  # long
            speed = random.uniform(400, 700)
            self.trail_length = 60
            self.color = (255, 150, 100)  # Red-orange
        
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
        self.trail = deque(maxlen=self.trail_length)
        self.lifetime = random.uniform(0.8, 2.0)
        self.age = 0
        self.brightness = random.uniform(0.7, 1.0)
        self.meteor_type = meteor_type
        
    def update(self, dt):
        self.age += dt
        if self.age < self.lifetime:
            self.x += self.vx * dt
            self.y += self.vy * dt
            
            # Add to trail with varying brightness
            trail_brightness = self.brightness * (1 - self.age / self.lifetime)
            self.trail.append((self.x, self.y, trail_brightness))
            
            return True
        return False
    
    def draw(self, screen):
        if len(self.trail) > 1:
            # Draw trail with enhanced effects
            for i in range(len(self.trail) - 1):
                x1, y1, bright1 = self.trail[i]
                x2, y2, bright2 = self.trail[i + 1]
                
                # Progressive trail fading
                alpha = (i / len(self.trail)) * bright2
                if alpha > 0.05:
                    width = max(1, int(6 * alpha))
                    
                    # Color varies with meteor type
                    if self.meteor_type == "bright":
                        # Bright fireball with blue core
                        core_color = tuple(int(c * alpha) for c in self.color)
                        glow_color = tuple(int(c * alpha * 0.6) for c in (100, 150, 255))
                        
                        # Draw glow first
                        if width > 2:
                            pygame.draw.line(screen, glow_color, (int(x1), int(y1)), (int(x2), int(y2)), width + 4)
                        pygame.draw.line(screen, core_color, (int(x1), int(y1)), (int(x2), int(y2)), width)
                    else:
                        # Normal meteor
                        color = tuple(int(c * alpha) for c in self.color)
                        pygame.draw.line(screen, color, (int(x1), int(y1)), (int(x2), int(y2)), width)


class Satellite:
    def __init__(self, screen_width, screen_height):
        # Satellites move in straight lines across the sky
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.start_edge = random.randint(0, 3)
        
        if self.start_edge == 0:  # Top to bottom
            self.x = random.uniform(screen_width * 0.1, screen_width * 0.9)
            self.y = -10
            self.vx = random.uniform(-50, 50)
            self.vy = random.uniform(80, 150)
        elif self.start_edge == 1:  # Right to left
            self.x = screen_width + 10
            self.y = random.uniform(screen_height * 0.1, screen_height * 0.9)
            self.vx = random.uniform(-150, -80)
            self.vy = random.uniform(-30, 30)
        elif self.start_edge == 2:  # Bottom to top
            self.x = random.uniform(screen_width * 0.1, screen_width * 0.9)
            self.y = screen_height + 10
            self.vx = random.uniform(-50, 50)
            self.vy = random.uniform(-150, -80)
        else:  # Left to right
            self.x = -10
            self.y = random.uniform(screen_height * 0.1, screen_height * 0.9)
            self.vx = random.uniform(80, 150)
            self.vy = random.uniform(-30, 30)
        
        self.brightness = random.uniform(0.3, 0.8)
        self.blink_phase = random.uniform(0, 2 * math.pi)
        self.blink_speed = random.uniform(2, 6)  # Blinking navigation lights
        self.age = 0
        self.trail = deque(maxlen=8)  # Short trail for satellite
        
    def update(self, dt):
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Update blinking
        self.blink_phase += self.blink_speed * dt
        
        # Add to trail
        self.trail.append((self.x, self.y))
        
        # Check if off screen
        return not (self.x < -50 or self.x > self.screen_width + 50 or 
                   self.y < -50 or self.y > self.screen_height + 50)
    
    def draw(self, screen):
        # Blinking satellite light
        blink_brightness = (math.sin(self.blink_phase) + 1) / 2
        current_brightness = self.brightness * blink_brightness
        
        if current_brightness > 0.1:
            # Draw satellite as small moving dot
            color = (int(255 * current_brightness), int(200 * current_brightness), int(200 * current_brightness))
            size = max(1, int(3 * current_brightness))
            
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), size)
            
            # Draw subtle trail
            if len(self.trail) > 1:
                for i in range(len(self.trail) - 1):
                    x1, y1 = self.trail[i]
                    x2, y2 = self.trail[i + 1]
                    alpha = (i / len(self.trail)) * current_brightness * 0.3
                    if alpha > 0.05:
                        trail_color = tuple(int(c * alpha) for c in (200, 180, 180))
                        pygame.draw.line(screen, trail_color, (int(x1), int(y1)), (int(x2), int(y2)), 1)


class Planet:
    def __init__(self, planet_type, x, y):
        self.type = planet_type
        self.x = x
        self.y = y
        self.age = 0
        
        # Planet properties
        planet_data = {
            "Venus": {"color": (255, 255, 220), "size": 4, "brightness": 0.9},
            "Mars": {"color": (255, 180, 120), "size": 3, "brightness": 0.7},
            "Jupiter": {"color": (255, 230, 180), "size": 5, "brightness": 0.8},
            "Saturn": {"color": (255, 240, 200), "size": 4, "brightness": 0.6},
        }
        
        self.color = planet_data[planet_type]["color"]
        self.size = planet_data[planet_type]["size"]
        self.base_brightness = planet_data[planet_type]["brightness"]
        self.brightness = self.base_brightness
        
        # Subtle variations
        self.shimmer_phase = random.uniform(0, 2 * math.pi)
        self.shimmer_speed = random.uniform(0.5, 1.5)
        
    def update(self, dt):
        self.age += dt
        # Very subtle atmospheric shimmer
        self.shimmer_phase += self.shimmer_speed * dt
        shimmer = math.sin(self.shimmer_phase) * 0.1
        self.brightness = self.base_brightness * (1 + shimmer)
    
    def draw(self, screen, settings):
        if self.brightness > 0.01:
            color = tuple(int(c * self.brightness) for c in self.color)
            
            # Draw planet with glow
            if settings["enable_glow"]:
                for i in range(3):
                    glow_size = self.size + i * 2
                    glow_alpha = int(40 / (i + 1))
                    glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, color, (glow_size, glow_size), glow_size)
                    glow_surf.set_alpha(glow_alpha)
                    screen.blit(glow_surf, (int(self.x - glow_size), int(self.y - glow_size)))
            
            # Main planet
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)


class MilkyWay:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.star_clouds = []
        self.dust_lanes = []
        self.generate_milky_way()
        
    def generate_milky_way(self):
        # Generate the galactic plane - a band across the sky
        # The Milky Way appears as a bright band with dark dust lanes
        
        # Main galactic plane (varies by season and location)
        center_y = self.screen_height * random.uniform(0.3, 0.7)  # Height across sky
        
        # Create star clouds along the galactic plane
        num_clouds = 8
        for i in range(num_clouds):
            x = (i / num_clouds) * self.screen_width
            y_variance = random.uniform(-60, 60)
            y = center_y + y_variance
            
            # Each cloud contains many faint stars
            cloud_stars = []
            for _ in range(random.randint(15, 30)):
                star_x = x + random.uniform(-100, 100)
                star_y = y + random.uniform(-40, 40)
                star_brightness = random.uniform(0.1, 0.3)
                star_color_temp = random.uniform(0.4, 0.8)
                
                # Keep within screen bounds
                if 0 <= star_x <= self.screen_width and 0 <= star_y <= self.screen_height:
                    cloud_stars.append((star_x, star_y, star_brightness, star_color_temp))
            
            self.star_clouds.append(cloud_stars)
        
        # Create dark dust lanes
        for _ in range(3):
            lane_x = random.uniform(self.screen_width * 0.2, self.screen_width * 0.8)
            lane_y = center_y + random.uniform(-30, 30)
            lane_width = random.uniform(80, 150)
            lane_height = random.uniform(20, 40)
            self.dust_lanes.append((lane_x, lane_y, lane_width, lane_height))
    
    def draw(self, screen, star_visibility, settings):
        # Only visible in dark skies
        if star_visibility < 0.7:
            return
        
        milky_way_alpha = star_visibility * 0.8
        
        # Draw background glow first
        if settings["enable_glow"]:
            glow_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            
            # Create soft galactic glow
            for cloud_stars in self.star_clouds:
                if cloud_stars:
                    # Calculate cloud center
                    center_x = sum(star[0] for star in cloud_stars) / len(cloud_stars)
                    center_y = sum(star[1] for star in cloud_stars) / len(cloud_stars)
                    
                    # Draw soft glow around star cloud
                    glow_color = (100, 120, 150)  # Bluish galactic glow
                    glow_radius = 80
                    
                    glow_circle = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_circle, glow_color, (glow_radius, glow_radius), glow_radius)
                    glow_circle.set_alpha(int(30 * milky_way_alpha))
                    
                    screen.blit(glow_circle, (int(center_x - glow_radius), int(center_y - glow_radius)))
        
        # Draw individual stars in the Milky Way
        for cloud_stars in self.star_clouds:
            for star_x, star_y, star_brightness, star_color_temp in cloud_stars:
                brightness = star_brightness * milky_way_alpha
                
                if brightness > 0.05:
                    # Color based on temperature
                    if star_color_temp < 0.5:
                        color = (255, int(180 * star_color_temp * 2), int(120 * star_color_temp * 2))
                    else:
                        color = (int(255 * (2 - star_color_temp)), int(255 * (2 - star_color_temp)), 255)
                    
                    final_color = tuple(int(c * brightness) for c in color)
                    size = max(1, int(brightness * 3))
                    
                    pygame.draw.circle(screen, final_color, (int(star_x), int(star_y)), size)
        
        # Draw dark dust lanes
        dust_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        for lane_x, lane_y, lane_width, lane_height in self.dust_lanes:
            dust_color = (0, 0, 0)  # Dark dust
            dust_alpha = int(80 * milky_way_alpha)
            
            # Draw elliptical dust lane
            dust_ellipse = pygame.Surface((int(lane_width), int(lane_height)), pygame.SRCALPHA)
            pygame.draw.ellipse(dust_ellipse, dust_color, (0, 0, int(lane_width), int(lane_height)))
            dust_ellipse.set_alpha(dust_alpha)
            
            screen.blit(dust_ellipse, (int(lane_x - lane_width/2), int(lane_y - lane_height/2)))


class BrightFlare:
    def __init__(self, screen_width, screen_height):
        self.x = random.uniform(screen_width * 0.2, screen_width * 0.8)
        self.y = random.uniform(screen_height * 0.2, screen_height * 0.8)
        self.max_brightness = random.uniform(0.8, 1.0)
        self.duration = random.uniform(0.5, 2.0)
        self.age = 0
        self.flare_type = random.choice(["iridium", "satellite", "space_debris"])
        
        # Different flare characteristics
        if self.flare_type == "iridium":
            self.color = (255, 255, 255)  # Bright white
            self.max_size = 8
        elif self.flare_type == "satellite":
            self.color = (255, 220, 180)  # Warm white
            self.max_size = 6
        else:  # space_debris
            self.color = (255, 200, 150)  # Slightly orange
            self.max_size = 5
    
    def update(self, dt):
        self.age += dt
        return self.age < self.duration
    
    def draw(self, screen):
        # Brightness peaks in the middle, fades at start and end
        progress = self.age / self.duration
        if progress < 0.5:
            brightness_factor = progress * 2  # Fade in
        else:
            brightness_factor = (1 - progress) * 2  # Fade out
        
        brightness = self.max_brightness * brightness_factor
        
        if brightness > 0.1:
            color = tuple(int(c * brightness) for c in self.color)
            size = max(1, int(self.max_size * brightness))
            
            # Draw flare with cross pattern
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), size)
            
            # Add cross spikes for bright flares
            if brightness > 0.5:
                spike_length = size * 3
                spike_color = tuple(int(c * 0.7) for c in color)
                pygame.draw.line(screen, spike_color, 
                               (int(self.x - spike_length), int(self.y)), 
                               (int(self.x + spike_length), int(self.y)), 2)
                pygame.draw.line(screen, spike_color, 
                               (int(self.x), int(self.y - spike_length)), 
                               (int(self.x), int(self.y + spike_length)), 2)


class SimpleParticle:
    """Simple rain/snow particle that always falls straight down"""
    def __init__(self, particle_type, screen_width, screen_height):
        self.type = particle_type
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.reset()
        
    def reset(self):
        self.x = random.uniform(0, self.screen_width)
        self.y = random.uniform(-50, -10)
        
        if self.type == "rain":
            self.speed = random.uniform(400, 800)
            self.length = random.uniform(10, 25)
            self.width = random.randint(1, 3)
        else:  # snow
            self.speed = random.uniform(100, 300)
            self.size = random.randint(2, 6)
            self.drift = random.uniform(-50, 50)
            
        self.opacity = random.uniform(0.5, 1.0)
    
    def update(self, dt):
        self.y += self.speed * dt
        
        if self.type == "snow":
            self.x += self.drift * dt
            
        # Reset if off screen
        if self.y > self.screen_height + 50:
            self.reset()
    
    def draw(self, screen):
        if self.type == "rain":
            color = (150, 150, 255)
            alpha = int(200 * self.opacity)
            
            # Draw rain line
            rain_surf = pygame.Surface((self.width + 2, int(self.length) + 2), pygame.SRCALPHA)
            pygame.draw.line(rain_surf, color, (1, 1), (1, int(self.length) + 1), self.width)
            rain_surf.set_alpha(alpha)
            screen.blit(rain_surf, (int(self.x), int(self.y)))
            
        else:  # snow
            color = (255, 255, 255)
            alpha = int(255 * self.opacity)
            
            # Draw snowflake
            snow_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(snow_surf, color, (self.size, self.size), self.size)
            snow_surf.set_alpha(alpha)
            screen.blit(snow_surf, (int(self.x - self.size), int(self.y - self.size)))


class SimpleLightning:
    """Simple lightning effect for thunderstorms"""
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active = False
        self.flash_alpha = 0
        self.branches = []
        self.duration = 0
        
    def trigger(self):
        if self.active:
            return
            
        self.active = True
        self.flash_alpha = 255
        self.duration = 0
        
        # Create simple lightning bolt
        self.branches = []
        start_x = random.randint(self.screen_width // 4, 3 * self.screen_width // 4)
        start_y = 0
        
        # Simple zigzag lightning
        points = [(start_x, start_y)]
        current_x = start_x
        current_y = start_y
        
        for i in range(8):
            current_x += random.randint(-60, 60)
            current_y += self.screen_height // 8
            current_x = max(0, min(self.screen_width, current_x))
            points.append((current_x, current_y))
        
        self.branches = points
    
    def update(self, dt):
        if not self.active:
            return
            
        self.duration += dt
        self.flash_alpha = max(0, self.flash_alpha - 800 * dt)
        
        if self.duration > 0.2:
            self.active = False
    
    def draw(self, screen):
        if not self.active:
            return
            
        # Screen flash
        if self.flash_alpha > 0:
            flash_surf = pygame.Surface((self.screen_width, self.screen_height))
            flash_surf.fill((255, 255, 255))
            flash_surf.set_alpha(int(self.flash_alpha))
            screen.blit(flash_surf, (0, 0))
        
        # Lightning bolt
        if len(self.branches) > 1:
            pygame.draw.lines(screen, (255, 255, 255), False, self.branches, 5)
            pygame.draw.lines(screen, (200, 200, 255), False, self.branches, 8)


class SkySimulator:
    def __init__(self, 
                 latitude=40.7128, 
                 longitude=-74.0060, 
                 timezone="America/New_York",
                 location_name="New York, NY",
                 screen_width=DEFAULT_SCREEN_WIDTH,
                 screen_height=DEFAULT_SCREEN_HEIGHT,
                 fps=DEFAULT_FPS,
                 preset="balanced",
                 cycle_cities=False,
                 cycle_interval=300,
                 show_info=True,
                 fullscreen=True,
                 world_cities=None):
        
        pygame.init()
        
        # Store configuration
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.fps = fps
        self.preset = preset
        self.settings = QUALITY_SETTINGS[preset]
        self.fullscreen = fullscreen
        
        # Set up display
        try:
            if fullscreen:
                self.screen = pygame.display.set_mode((screen_width, screen_height), 
                                                    pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
            else:
                self.screen = pygame.display.set_mode((screen_width, screen_height))
        except:
            if fullscreen:
                self.screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
            else:
                self.screen = pygame.display.set_mode((screen_width, screen_height))
                
        pygame.display.set_caption("Sky Ceiling Projector")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Location and timezone handling
        self.current_latitude = latitude
        self.current_longitude = longitude
        self.current_timezone = timezone
        self.current_location_name = location_name
        
        # City cycling for demo mode
        self.cycle_cities = cycle_cities
        self.cycle_interval = cycle_interval
        self.world_cities = world_cities or []
        self.city_index = 0
        self.last_city_change = time.time()
        self.next_city_change = self.last_city_change + self.cycle_interval
        self.location_change_queue = queue.Queue()
        
        # Location transition system for smooth color changes
        self.in_location_transition = False
        self.location_transition_progress = 0.0
        self.location_transition_duration = 5.0  # 5 second color transition
        self.old_sky_colors = None
        self.new_sky_colors = None
        
        # Debug mode
        self.debug_mode = False
        self.debug_weather_index = 0
        self.debug_weather_timer = 0
        self.debug_weather_interval = 5.0  # Change weather every 5 seconds in debug mode
        
        # Weather data
        self.weather_queue = queue.Queue()
        self.weather_data = None
        self.current_weather = "Clear"
        self.forced_weather = None  # For debug mode
        
        # Sky elements
        self.stars = []
        self.clouds = []
        self.particles = []
        self.lightning = SimpleLightning(screen_width, screen_height)
        
        # Enhanced celestial objects
        self.milky_way = MilkyWay(screen_width, screen_height)
        self.shooting_stars = []
        self.satellites = []
        self.planets = []
        self.bright_flares = []
        
        # Celestial event timers
        self.next_shooting_star = time.time() + random.uniform(15, 45)
        self.next_satellite = time.time() + random.uniform(60, 180)
        self.next_bright_flare = time.time() + random.uniform(300, 900)  # Rare events
        
        # Sky colors
        self.current_sky_color = (0, 0, 0)
        self.current_horizon_color = (0, 0, 0)
        
        # Moon and sun with restored detailed moon
        self.moon_phase = self.calculate_moon_phase()
        self.sun_position = (0, 0)
        self.moon_position = (0, 0)
        
        # Pre-generate static celestial details to avoid flickering
        self.moon_craters = self.generate_moon_craters()
        self.sun_spots = self.generate_sun_spots()
        
        # Info display
        self.show_info = show_info
        
        # Initialize elements
        self.create_stars()
        self.create_planets()
        
        # Start weather update thread
        self.weather_thread = Thread(target=self.weather_updater, daemon=True)
        self.weather_thread.start()
        
        # Start city cycling thread if enabled
        if self.cycle_cities:
            self.city_cycle_thread = Thread(target=self.city_cycler, daemon=True)
            self.city_cycle_thread.start()
    
    def create_planets(self):
        """Create visible planets based on location and season"""
        self.planets = []
        
        # Simple planet positioning (simplified for ceiling projection)
        # In reality, planets follow complex orbital mechanics
        
        local_time = self.get_local_time()
        month = local_time.month
        
        # Venus (evening or morning star)
        if random.random() < 0.7:  # 70% chance Venus is visible
            if random.random() < 0.5:  # Evening star
                venus_x = self.screen_width * random.uniform(0.1, 0.4)
                venus_y = self.screen_height * random.uniform(0.6, 0.9)
            else:  # Morning star
                venus_x = self.screen_width * random.uniform(0.6, 0.9)
                venus_y = self.screen_height * random.uniform(0.6, 0.9)
            self.planets.append(Planet("Venus", venus_x, venus_y))
        
        # Mars (varies greatly in brightness and visibility)
        if random.random() < 0.4:  # 40% chance Mars is visible
            mars_x = self.screen_width * random.uniform(0.2, 0.8)
            mars_y = self.screen_height * random.uniform(0.3, 0.8)
            self.planets.append(Planet("Mars", mars_x, mars_y))
        
        # Jupiter (bright when visible)
        if random.random() < 0.5:  # 50% chance Jupiter is visible
            jupiter_x = self.screen_width * random.uniform(0.3, 0.7)
            jupiter_y = self.screen_height * random.uniform(0.2, 0.7)
            self.planets.append(Planet("Jupiter", jupiter_x, jupiter_y))
        
        # Saturn (dimmer, less frequently visible)
        if random.random() < 0.3:  # 30% chance Saturn is visible
            saturn_x = self.screen_width * random.uniform(0.2, 0.8)
            saturn_y = self.screen_height * random.uniform(0.4, 0.8)
            self.planets.append(Planet("Saturn", saturn_x, saturn_y))
    
    def generate_moon_craters(self):
        """Pre-generate static moon craters to avoid flickering"""
        craters = []
        radius = 45
        crater_count = 12
        
        # Use a fixed seed for consistent crater pattern
        old_state = random.getstate()
        random.seed(42)  # Fixed seed for consistent craters
        
        for _ in range(crater_count):
            # Generate crater within moon circle
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, radius * 0.7)
            cx = radius + math.cos(angle) * distance
            cy = radius + math.sin(angle) * distance
            crater_radius = random.uniform(2, 8)
            depth = random.uniform(0.7, 0.9)  # How dark the crater is
            craters.append((cx, cy, crater_radius, depth))
        
        random.setstate(old_state)  # Restore random state
        return craters
    
    def generate_sun_spots(self):
        """Pre-generate static sun spots to avoid flickering"""
        spots = []
        sun_radius = 55
        spot_count = 8
        
        # Use a fixed seed for consistent spot pattern
        old_state = random.getstate()
        random.seed(123)  # Fixed seed for consistent spots
        
        for _ in range(spot_count):
            # Generate spots within sun circle
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, sun_radius * 0.8)
            sx = math.cos(angle) * distance
            sy = math.sin(angle) * distance
            spot_radius = random.uniform(3, 12)
            intensity = random.uniform(0.85, 0.95)  # How dark the spot is
            spots.append((sx, sy, spot_radius, intensity))
        
        random.setstate(old_state)  # Restore random state
        return spots
    
    def calculate_moon_phase(self):
        """Calculate current moon phase"""
        known_new_moon = datetime(2000, 1, 6, 18, 14)
        moon_cycle = 29.53059
        
        current_time = datetime.now()
        days_since = (current_time - known_new_moon).total_seconds() / 86400
        phase = (days_since % moon_cycle) / moon_cycle
        
        return phase
    
    def get_local_time(self):
        """Get current time in the location's timezone"""
        try:
            tz = pytz.timezone(self.current_timezone)
            utc_now = datetime.now(pytz.UTC)
            local_time = utc_now.astimezone(tz)
            return local_time
        except:
            return datetime.now()
    
    def create_stars(self):
        """Create enhanced starfield with variable stars, giants, and more vibrant colors"""
        self.stars = []
        star_count = self.settings["star_count"]
        
        # Red giants and supergiants (2% - rare but spectacular)
        for _ in range(int(star_count * 0.02)):
            x = random.uniform(0, self.screen_width)
            y = random.uniform(0, self.screen_height)
            brightness = random.uniform(0.8, 1.0)
            twinkle = random.uniform(1, 3)
            color_temp = random.uniform(0.05, 0.25)  # Very red
            star_type = "supergiant" if random.random() < 0.3 else "giant"
            size_class = "supergiant" if star_type == "supergiant" else "giant"
            self.stars.append(Star(x, y, brightness, twinkle, size_class, color_temp, star_type))
        
        # Blue giants (1% - hot, bright stars)
        for _ in range(int(star_count * 0.01)):
            x = random.uniform(0, self.screen_width)
            y = random.uniform(0, self.screen_height)
            brightness = random.uniform(0.9, 1.0)
            twinkle = random.uniform(2, 4)
            color_temp = random.uniform(0.8, 1.0)  # Very blue
            self.stars.append(Star(x, y, brightness, twinkle, "giant", color_temp, "giant"))
        
        # Variable stars (3% - pulsating stars)
        for _ in range(int(star_count * 0.03)):
            x = random.uniform(0, self.screen_width)
            y = random.uniform(0, self.screen_height)
            brightness = random.uniform(0.6, 0.9)
            twinkle = random.uniform(1, 3)
            color_temp = random.uniform(0.2, 0.8)  # Various colors
            size_class = "bright" if random.random() < 0.5 else "super"
            self.stars.append(Star(x, y, brightness, twinkle, size_class, color_temp, "variable"))
        
        # Bright main sequence stars (9% - the prominent stars)
        for _ in range(int(star_count * 0.09)):
            x = random.uniform(0, self.screen_width)
            y = random.uniform(0, self.screen_height)
            brightness = random.uniform(0.7, 1.0)
            twinkle = random.uniform(2, 4)
            color_temp = random.uniform(0.3, 0.9)
            size_class = "super" if random.random() < 0.3 else "bright"
            self.stars.append(Star(x, y, brightness, twinkle, size_class, color_temp))
        
        # Normal stars (60% - the majority)
        for _ in range(int(star_count * 0.6)):
            x = random.uniform(0, self.screen_width)
            y = random.uniform(0, self.screen_height)
            brightness = random.uniform(0.4, 0.8)
            twinkle = random.uniform(1, 3)
            color_temp = random.uniform(0.35, 0.85)  # Sun-like to white
            self.stars.append(Star(x, y, brightness, twinkle, "normal", color_temp))
        
        # Dim background stars (25% - fills in the sky)
        for _ in range(int(star_count * 0.25)):
            x = random.uniform(0, self.screen_width)
            y = random.uniform(0, self.screen_height)
            brightness = random.uniform(0.1, 0.5)
            twinkle = random.uniform(0.5, 2)
            color_temp = random.uniform(0.4, 0.8)
            self.stars.append(Star(x, y, brightness, twinkle, "dim", color_temp))
    
    def city_cycler(self):
        """Background thread to cycle through world cities"""
        while self.running and self.cycle_cities:
            current_time = time.time()
            if current_time >= self.next_city_change and not self.in_location_transition:
                # Move to next city
                self.city_index = (self.city_index + 1) % len(self.world_cities)
                next_city = self.world_cities[self.city_index]
                
                try:
                    lat, lon, tz, name = geocode_location(next_city)
                    self.location_change_queue.put((lat, lon, tz, name))
                except Exception as e:
                    print(f"Failed to switch to {next_city}: {e}")
                
                # Schedule next change (after transition completes)
                self.last_city_change = current_time
                self.next_city_change = current_time + self.cycle_interval + self.location_transition_duration
            
            time.sleep(5)  # Check every 5 seconds
    
    def start_location_transition(self, new_lat, new_lon, new_tz, new_name):
        """Start smooth location transition with color fading"""
        # Store old colors
        local_time = self.get_local_time()
        hour = local_time.hour + local_time.minute / 60.0
        self.old_sky_colors = self.get_sky_colors(hour, self.current_weather)
        
        # Update location immediately for calculations
        self.current_latitude = new_lat
        self.current_longitude = new_lon
        self.current_timezone = new_tz
        self.current_location_name = new_name
        
        # Calculate new colors
        new_local_time = self.get_local_time()
        new_hour = new_local_time.hour + new_local_time.minute / 60.0
        self.new_sky_colors = self.get_sky_colors(new_hour, self.current_weather)
        
        # Start transition
        self.in_location_transition = True
        self.location_transition_progress = 0.0
        
        # Regenerate celestial details for new location
        location_seed = int(abs(new_lat * 1000) + abs(new_lon * 1000)) % 10000
        old_state = random.getstate()
        random.seed(location_seed)
        self.moon_craters = self.generate_moon_craters()
        self.sun_spots = self.generate_sun_spots()
        random.setstate(old_state)
        
        # Update moon phase for new location
        self.moon_phase = self.calculate_moon_phase()
        
        print(f"🌍 Transitioning to: {new_name} with smooth color fade")
    
    def weather_updater(self):
        """Background thread to update weather data"""
        while self.running:
            try:
                url = f"https://api.open-meteo.com/v1/forecast?latitude={self.current_latitude}&longitude={self.current_longitude}&current=temperature_2m,weather_code,cloud_cover,wind_speed_10m,wind_direction_10m&timezone={self.current_timezone}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    weather_code = data['current']['weather_code']
                    
                    # Map weather codes to conditions
                    weather_map = {
                        0: "Clear", 1: "Clear", 2: "Clouds", 3: "Clouds",
                        45: "Fog", 48: "Fog",
                        51: "Drizzle", 53: "Drizzle", 55: "Drizzle",
                        61: "Rain", 63: "Rain", 65: "Rain",
                        71: "Snow", 73: "Snow", 75: "Snow",
                        80: "Rain", 81: "Rain", 82: "Rain",
                        95: "Thunderstorm", 96: "Thunderstorm", 99: "Thunderstorm"
                    }
                    
                    weather_condition = weather_map.get(weather_code, "Clear")
                    
                    formatted_data = {
                        'weather': [{'main': weather_condition}],
                        'clouds': {'all': data['current']['cloud_cover']},
                        'main': {'temp': data['current']['temperature_2m']},
                        'wind': {
                            'speed': data['current']['wind_speed_10m'],
                            'deg': data['current']['wind_direction_10m']
                        }
                    }
                    
                    self.weather_queue.put(formatted_data)
                    
            except Exception as e:
                print(f"Weather update error: {e}")
            
            time.sleep(WEATHER_UPDATE_INTERVAL)
    
    def update_weather_effects(self):
        """Update weather effects based on current conditions - SIMPLIFIED AND RELIABLE!"""
        # Determine actual weather condition
        if self.forced_weather:  # Debug mode override
            weather = self.forced_weather
        elif self.weather_data:
            weather = self.weather_data['weather'][0]['main']
        else:
            weather = "Clear"
        
        self.current_weather = weather
        
        # CLEAR ALL EXISTING EFFECTS FIRST
        self.clouds.clear()
        self.particles.clear()
        
        # NOW ADD EFFECTS BASED ON WEATHER - NO COMPLEX TRANSITIONS!
        if weather == "Clear":
            # No clouds, no particles
            pass
            
        elif weather == "Clouds":
            # LOTS of detailed clouds
            num_clouds = self.settings["max_clouds"]
            for i in range(num_clouds):
                x = random.uniform(-200, self.screen_width + 200)
                y = random.uniform(0, self.screen_height * 0.5)
                size = random.uniform(80, 200)
                speed = random.uniform(20, 60)
                opacity = random.uniform(0.6, 0.9)
                self.clouds.append(DetailedCloud(x, y, size, speed, opacity, self.screen_width, self.screen_height))
                
        elif weather == "Rain" or weather == "Drizzle":
            # LOTS of detailed clouds AND rain particles
            num_clouds = self.settings["max_clouds"]
            for i in range(num_clouds):
                x = random.uniform(-200, self.screen_width + 200)
                y = random.uniform(0, self.screen_height * 0.4)
                size = random.uniform(100, 250)
                speed = random.uniform(15, 40)
                opacity = random.uniform(0.7, 1.0)
                self.clouds.append(DetailedCloud(x, y, size, speed, opacity, self.screen_width, self.screen_height))
            
            # Rain particles
            num_particles = self.settings["max_particles"]
            for i in range(num_particles):
                self.particles.append(SimpleParticle("rain", self.screen_width, self.screen_height))
                
        elif weather == "Snow":
            # LOTS of detailed clouds AND snow particles
            num_clouds = self.settings["max_clouds"]
            for i in range(num_clouds):
                x = random.uniform(-200, self.screen_width + 200)
                y = random.uniform(0, self.screen_height * 0.4)
                size = random.uniform(120, 280)
                speed = random.uniform(10, 30)
                opacity = random.uniform(0.8, 1.0)
                self.clouds.append(DetailedCloud(x, y, size, speed, opacity, self.screen_width, self.screen_height))
            
            # Snow particles
            num_particles = self.settings["max_particles"]
            for i in range(num_particles):
                self.particles.append(SimpleParticle("snow", self.screen_width, self.screen_height))
                
        elif weather == "Thunderstorm":
            # LOTS of dark detailed clouds AND rain particles AND lightning
            num_clouds = self.settings["max_clouds"]
            for i in range(num_clouds):
                x = random.uniform(-200, self.screen_width + 200)
                y = random.uniform(0, self.screen_height * 0.5)
                size = random.uniform(150, 300)
                speed = random.uniform(10, 35)
                opacity = random.uniform(0.8, 1.0)
                self.clouds.append(DetailedCloud(x, y, size, speed, opacity, self.screen_width, self.screen_height))
            
            # Heavy rain particles
            num_particles = self.settings["max_particles"]
            for i in range(num_particles):
                self.particles.append(SimpleParticle("rain", self.screen_width, self.screen_height))
                
        elif weather == "Fog":
            # Medium detailed clouds, lower opacity
            num_clouds = self.settings["max_clouds"] // 2
            for i in range(num_clouds):
                x = random.uniform(-200, self.screen_width + 200)
                y = random.uniform(self.screen_height * 0.3, self.screen_height * 0.8)
                size = random.uniform(200, 400)
                speed = random.uniform(5, 15)
                opacity = random.uniform(0.4, 0.7)
                self.clouds.append(DetailedCloud(x, y, size, speed, opacity, self.screen_width, self.screen_height))
        
        print(f"🌤️ Weather effects updated: {weather} - {len(self.clouds)} clouds, {len(self.particles)} particles")
    
    def get_sky_colors(self, hour, weather):
        """Get sky colors based on time and weather"""
        # Base colors for different times
        if 5 < hour < 7:  # Dawn
            sky_base = (60, 40, 80)
            horizon_base = (120, 80, 100)
        elif 7 < hour < 9:  # Sunrise
            sky_base = (140, 100, 150)
            horizon_base = (255, 150, 100)
        elif 9 < hour < 17:  # Day
            sky_base = (110, 160, 255)
            horizon_base = (150, 200, 255)
        elif 17 < hour < 19:  # Sunset
            sky_base = (200, 100, 80)
            horizon_base = (255, 140, 60)
        elif 19 < hour < 21:  # Dusk
            sky_base = (80, 40, 70)
            horizon_base = (140, 60, 90)
        else:  # Night
            sky_base = (10, 10, 30)
            horizon_base = (20, 20, 50)
        
        # Modify based on weather
        if weather in ["Clouds", "Rain", "Drizzle", "Thunderstorm"]:
            # Darker for stormy weather
            sky_base = tuple(int(c * 0.6) for c in sky_base)
            horizon_base = tuple(int(c * 0.7) for c in horizon_base)
        elif weather == "Fog":
            # Gray for fog
            avg = sum(sky_base) // 3
            sky_base = (avg, avg, avg)
            horizon_base = (avg + 20, avg + 20, avg + 20)
        
        return sky_base, horizon_base
    
    def calculate_celestial_positions(self, hour):
        """Calculate sun and moon positions"""
        # Sun position (day time)
        if 5 <= hour <= 19:
            sun_progress = (hour - 5) / 14
            sun_angle = sun_progress * math.pi
            sun_x = self.screen_width * 0.1 + self.screen_width * 0.8 * sun_progress
            sun_y = self.screen_height * 0.9 - self.screen_height * 0.7 * math.sin(sun_angle)
            self.sun_position = (sun_x, sun_y)
        else:
            self.sun_position = None
        
        # Moon position (night time)
        if hour < 6 or hour > 18:
            if hour > 18:
                moon_progress = (hour - 18) / 12
            else:
                moon_progress = (hour + 6) / 12
            
            moon_angle = moon_progress * math.pi
            moon_x = self.screen_width * 0.1 + self.screen_width * 0.8 * moon_progress
            moon_y = self.screen_height * 0.9 - self.screen_height * 0.6 * math.sin(moon_angle)
            
            # Add some variation based on phase
            phase_offset_x = (self.moon_phase - 0.5) * 100
            phase_offset_y = math.sin(self.moon_phase * 2 * math.pi) * 30
            
            self.moon_position = (moon_x + phase_offset_x, moon_y + phase_offset_y)
        else:
            self.moon_position = None
    
    def update(self, dt):
        """Main update loop"""
        # Debug mode weather cycling
        if self.debug_mode:
            self.debug_weather_timer += dt
            if self.debug_weather_timer >= self.debug_weather_interval:
                self.debug_weather_timer = 0
                self.debug_weather_index = (self.debug_weather_index + 1) % len(DEBUG_WEATHER_CONDITIONS)
                self.forced_weather = DEBUG_WEATHER_CONDITIONS[self.debug_weather_index]
                self.update_weather_effects()
        
        # Check for location changes (city cycling)
        try:
            lat, lon, tz, name = self.location_change_queue.get_nowait()
            self.start_location_transition(lat, lon, tz, name)
        except queue.Empty:
            pass
        
        # Update location transition
        if self.in_location_transition:
            self.location_transition_progress += dt / self.location_transition_duration
            if self.location_transition_progress >= 1.0:
                self.in_location_transition = False
                self.location_transition_progress = 0.0
                self.old_sky_colors = None
                self.new_sky_colors = None
                print(f"✅ Arrived at: {self.current_location_name}")
        
        # Check for new weather data
        try:
            self.weather_data = self.weather_queue.get_nowait()
            if not self.debug_mode:  # Only update if not in debug mode
                self.update_weather_effects()
        except queue.Empty:
            pass
        
        # Update sky colors with smooth transition support
        local_time = self.get_local_time()
        hour = local_time.hour + local_time.minute / 60.0
        
        if self.in_location_transition and self.old_sky_colors and self.new_sky_colors:
            # Interpolate between old and new colors during location transition
            t = ease_in_out_cubic(self.location_transition_progress)
            
            old_sky, old_horizon = self.old_sky_colors
            new_sky, new_horizon = self.new_sky_colors
            
            self.current_sky_color = tuple(
                int(old_sky[i] + (new_sky[i] - old_sky[i]) * t) for i in range(3)
            )
            self.current_horizon_color = tuple(
                int(old_horizon[i] + (new_horizon[i] - old_horizon[i]) * t) for i in range(3)
            )
        else:
            # Normal color calculation
            self.current_sky_color, self.current_horizon_color = self.get_sky_colors(hour, self.current_weather)
        
        # Update celestial positions
        self.calculate_celestial_positions(hour)
        
        # Calculate star visibility
        star_visibility = 1.0 if (hour < 6 or hour > 20) else 0.0
        if 6 <= hour <= 7 or 19 <= hour <= 20:
            star_visibility = 0.5
        
        # Update stars (including variable stars and giants)
        for star in self.stars:
            star.update(dt, self.settings)
            star.brightness = min(star.brightness, star.base_brightness * star_visibility)
        
        # Update enhanced shooting stars
        self.shooting_stars = [s for s in self.shooting_stars if s.update(dt)]
        
        # Spawn new shooting star
        current_time = time.time()
        if current_time > self.next_shooting_star and star_visibility > 0.5:
            self.shooting_stars.append(EnhancedShootingStar(self.screen_width, self.screen_height))
            # More frequent during meteor showers (August, December)
            local_time = self.get_local_time()
            month = local_time.month
            if month in [8, 12]:  # Perseid and Geminid meteor showers
                self.next_shooting_star = current_time + random.uniform(8, 25)
            else:
                self.next_shooting_star = current_time + random.uniform(20, 60)
        
        # Update satellites
        self.satellites = [s for s in self.satellites if s.update(dt)]
        
        # Spawn new satellite
        if current_time > self.next_satellite and star_visibility > 0.3:
            self.satellites.append(Satellite(self.screen_width, self.screen_height))
            self.next_satellite = current_time + random.uniform(120, 300)  # Every 2-5 minutes
        
        # Update planets
        for planet in self.planets:
            planet.update(dt)
            # Planets are visible based on star visibility
            planet.brightness = min(planet.brightness, planet.base_brightness * star_visibility)
        
        # Update bright flares
        self.bright_flares = [f for f in self.bright_flares if f.update(dt)]
        
        # Spawn new bright flare (rare events)
        # Commented out to reduce frequency
        # if current_time > self.next_bright_flare and star_visibility > 0.7:
        #     self.bright_flares.append(BrightFlare(self.screen_width, self.screen_height))
        #     self.next_bright_flare = current_time + random.uniform(600, 1800)  # Every 10-30 minutes
        
        # Update clouds
        for cloud in self.clouds:
            cloud.update(dt)
        
        # Update particles
        for particle in self.particles:
            particle.update(dt)
        
        # Update lightning
        self.lightning.update(dt)
        
        # Trigger lightning for thunderstorms
        if self.current_weather == "Thunderstorm" and random.random() < 0.005:  # 0.5% chance per frame
            self.lightning.trigger()
    
    def draw_sky_gradient(self):
        """Draw sky gradient"""
        # Simple two-color gradient
        for y in range(self.screen_height):
            t = y / self.screen_height
            r = int(self.current_horizon_color[0] + (self.current_sky_color[0] - self.current_horizon_color[0]) * t)
            g = int(self.current_horizon_color[1] + (self.current_sky_color[1] - self.current_horizon_color[1]) * t)
            b = int(self.current_horizon_color[2] + (self.current_sky_color[2] - self.current_horizon_color[2]) * t)
            
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.screen_width, y))
    
    def draw_stars(self):
        """Draw enhanced starfield with Milky Way"""
        # Draw Milky Way first (background)
        local_time = self.get_local_time()
        hour = local_time.hour + local_time.minute / 60.0
        star_visibility = 1.0 if (hour < 6 or hour > 20) else 0.0
        if 6 <= hour <= 7 or 19 <= hour <= 20:
            star_visibility = 0.5
        
        self.milky_way.draw(self.screen, star_visibility, self.settings)
        
        # Draw stars by brightness layers for proper visual hierarchy
        # Dim stars first (background)
        for star in self.stars:
            if star.size_class == "dim":
                star.draw(self.screen, self.settings)
        
        # Normal stars
        for star in self.stars:
            if star.size_class == "normal":
                star.draw(self.screen, self.settings)
        
        # Bright stars
        for star in self.stars:
            if star.size_class in ["bright", "super"]:
                star.draw(self.screen, self.settings)
        
        # Giants and supergiants (most prominent)
        for star in self.stars:
            if star.size_class in ["giant", "supergiant"]:
                star.draw(self.screen, self.settings)
    
    def draw_celestial_objects(self):
        """Draw planets, satellites, and other celestial objects"""
        # Draw planets
        for planet in self.planets:
            planet.draw(self.screen, self.settings)
        
        # Draw satellites
        for satellite in self.satellites:
            satellite.draw(self.screen)
        
        # Draw enhanced shooting stars
        for shooting_star in self.shooting_stars:
            shooting_star.draw(self.screen)
        
        # Draw bright flares
        for flare in self.bright_flares:
            flare.draw(self.screen)
    
    def draw_sun(self):
        """Draw sun with spots"""
        if not self.sun_position:
            return
        
        sun_x, sun_y = self.sun_position
        sun_radius = 55
        
        # Sun colors
        base_sun_color = (255, 245, 210)
        
        # Draw corona/atmospheric glow first
        if self.settings["enable_glow"]:
            corona_layers = 8
            
            for i in range(corona_layers):
                corona_radius = sun_radius + (i + 1) * 10
                corona_alpha = int(60 * (1 - i / corona_layers) ** 2)
                
                corona_color = tuple(min(255, max(0, int(c * (0.9 + i * 0.02)))) for c in base_sun_color)
                
                corona_surf = pygame.Surface((corona_radius * 2, corona_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(corona_surf, corona_color, 
                                 (corona_radius, corona_radius), corona_radius)
                corona_surf.set_alpha(corona_alpha)
                
                self.screen.blit(corona_surf, 
                               (int(sun_x - corona_radius), int(sun_y - corona_radius)))
        
        # Create main sun surface with radial gradient
        sun_surf = pygame.Surface((sun_radius * 2, sun_radius * 2), pygame.SRCALPHA)
        
        # Draw sun with realistic gradient from center to edge
        for r in range(sun_radius, 0, -1):
            brightness_factor = 0.85 + 0.15 * (1 - r / sun_radius) ** 0.7
            gradient_color = tuple(int(c * brightness_factor) for c in base_sun_color)
            pygame.draw.circle(sun_surf, gradient_color, (sun_radius, sun_radius), r)
        
        # Add pre-generated sunspots for surface detail
        for sx, sy, spot_radius, intensity in self.sun_spots:
            spot_x = sun_radius + sx
            spot_y = sun_radius + sy
            
            # Only draw spot if it's within the sun circle
            dist_from_center = math.sqrt(sx**2 + sy**2)
            if dist_from_center + spot_radius < sun_radius:
                intensity = max(0.1, min(1.0, intensity))
                spot_color = tuple(max(0, min(255, int(c * intensity))) for c in base_sun_color)
                
                pygame.draw.circle(sun_surf, spot_color, 
                                 (int(spot_x), int(spot_y)), int(spot_radius))
        
        # Draw the main sun
        self.screen.blit(sun_surf, (int(sun_x - sun_radius), int(sun_y - sun_radius)))
    
    def draw_moon(self):
        """Draw realistic moon with pre-generated craters and smooth shading"""
        if not self.moon_position:
            return
        
        moon_x, moon_y = self.moon_position
        radius = 45
        
        # Create moon surface with realistic gradient
        moon_surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        center = radius #*2
        
        # Base moon colors for realistic appearance
        base_color = (245, 240, 225)  # Warm lunar color
        shadow_color = (180, 175, 160)
        
        # Draw moon with radial gradient for 3D effect
        for r in range(radius, 0, -1):
            # Create depth with subtle gradient
            gradient_factor = (radius - r) / radius
            brightness = 0.7 + 0.3 * (1 - gradient_factor * 0.5)
            
            color = tuple(int(c * brightness) for c in base_color)
            pygame.draw.circle(moon_surf, color, (center, center), r)
        
        # Add pre-generated craters for realistic surface detail
        for cx, cy, crater_radius, depth in self.moon_craters:
            # Only draw crater if it's within the moon circle
            dist_from_center = math.sqrt((cx - center)**2 + (cy - center)**2)
            if dist_from_center + crater_radius < radius:
                crater_color = tuple(int(c * depth) for c in base_color)
                
                # Draw crater with soft edges
                crater_surf = pygame.Surface((crater_radius * 4, crater_radius * 4), pygame.SRCALPHA)
                for cr in range(int(crater_radius), 0, -1):
                    alpha = int(255 * (1 - (crater_radius - cr) / crater_radius) * 0.6)
                    temp_surf = pygame.Surface((crater_radius * 4, crater_radius * 4), pygame.SRCALPHA)
                    pygame.draw.circle(temp_surf, crater_color, 
                                     (int(crater_radius * 2), int(crater_radius * 2)), cr)
                    temp_surf.set_alpha(alpha)
                    crater_surf.blit(temp_surf, (0, 0))
                
                moon_surf.blit(crater_surf, (int(cx - crater_radius * 2), int(cy - crater_radius * 2)))
        
        # Draw moon phase shadow with smooth gradient
        if self.moon_phase != 0.5:  # Not full moon
            shadow_surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
            
            if self.moon_phase < 0.5:
                # Waxing moon - shadow on left
                shadow_width = int(radius * 2 * (0.5 - self.moon_phase) * 2)
                for x in range(shadow_width):
                    if shadow_width > 0:
                        # Create smooth curved shadow edge
                        normalized_x = x / shadow_width
                        curve_height = math.sqrt(1 - (normalized_x - 1) ** 2) if normalized_x <= 1 else 0
                        shadow_height = int(radius * 2 * curve_height)
                        
                        # Gradient shadow for realism
                        for y in range(center - shadow_height // 2, center + shadow_height // 2):
                            if 0 <= y < radius * 4:
                                alpha = int(250 * (1 - normalized_x * 0.3))
                                shadow_surf.set_at((x, y), (20, 20, 40, alpha))
            else:
                # Waning moon - shadow on right
                shadow_width = int(radius * 2 * (self.moon_phase - 0.5) * 2)
                for x in range(shadow_width):
                    if shadow_width > 0:
                        normalized_x = x / shadow_width
                        curve_height = math.sqrt(1 - normalized_x ** 2)
                        shadow_height = int(radius * 2 * curve_height)
                        
                        start_x = radius * 4 - shadow_width + x
                        for y in range(center - shadow_height // 2, center + shadow_height // 2):
                            if 0 <= y < radius * 4 and 0 <= start_x < radius * 4:
                                alpha = int(250 * (1 - normalized_x * 0.3))
                                shadow_surf.set_at((start_x, y), (20, 20, 40, alpha))
            
            moon_surf.blit(shadow_surf, (0, 0))
        
        # Add atmospheric glow
        if self.settings["enable_glow"]:
            glow_radius = radius + 25
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            
            # Multiple glow layers for soft atmospheric effect
            for i in range(15):
                glow_alpha = int(25 * (1 - i / 15) * (0.3 + 0.7 * abs(self.moon_phase - 0.5) * 2))
                glow_size = radius + i * 2
                glow_color = (255, 255, 240)
                
                temp_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, glow_color, (glow_radius, glow_radius), glow_size)
                temp_surf.set_alpha(glow_alpha)
                glow_surf.blit(temp_surf, (0, 0))
            
            #self.screen.blit(glow_surf, 
            #               (int(moon_x - glow_radius), int(moon_y - glow_radius)))
            self.screen.blit(glow_surf, 
                           (int(moon_x - (glow_radius*1.65)), int(moon_y - (glow_radius*1.65))))
        # Draw the main moon surface
        self.screen.blit(moon_surf, (int(moon_x - radius * 2), int(moon_y - radius * 2)))
    
    def draw_clouds(self):
        """Draw all detailed clouds"""
        local_time = self.get_local_time()
        hour = local_time.hour + local_time.minute / 60.0
        
        # Cloud color based on time and weather
        if self.current_weather == "Thunderstorm":
            cloud_color = (60, 60, 80)  # Dark storm clouds
        elif 6 < hour < 18:  # Day
            cloud_color = (200, 200, 200)
        else:  # Night
            cloud_color = (80, 80, 100)
        
        for cloud in self.clouds:
            cloud.draw(self.screen, cloud_color, self.settings, self.sun_position)
    
    def draw_particles(self):
        """Draw weather particles"""
        for particle in self.particles:
            particle.draw(self.screen)
    
    def draw_lightning(self):
        """Draw lightning effects"""
        self.lightning.draw(self.screen)
    
    def draw_info_overlay(self):
        """Draw information overlay"""
        if not self.show_info:
            return
            
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)
        
        local_time = self.get_local_time()
        time_str = local_time.strftime("%H:%M %Z")
        
        # Moon phase names
        phase_names = ["New Moon", "Waxing Crescent", "First Quarter", 
                      "Waxing Gibbous", "Full Moon", "Waning Gibbous",
                      "Last Quarter", "Waning Crescent"]
        phase_idx = int(self.moon_phase * 8) % 8
        moon_name = phase_names[phase_idx]
        
        location_prefix = "✈️ " if self.in_location_transition else "🌍 "
        text_lines = [
            f"{location_prefix}{self.current_location_name}",
        ]
        
        # Add weather info if available
        if self.weather_data:
            temp = self.weather_data['main']['temp']
            weather = self.weather_data['weather'][0]['main']
            text_lines.append(f"{temp:.1f}°C - {weather}")
        else:
            text_lines.append("Loading weather...")
        
        text_lines.extend([
            f"{moon_name}",
            f"{time_str}"
        ])
        
        if self.debug_mode:
            text_lines.append(f"🔧 DEBUG MODE - Weather: {self.forced_weather}")
        
        if self.in_location_transition:
            progress = int(self.location_transition_progress * 100)
            text_lines.append(f"Traveling... {progress}%")
        
        y_offset = self.screen_height - len(text_lines) * 40 - 20
        for line in text_lines:
            # Shadow
            shadow = font.render(line, True, (0, 0, 0))
            text = font.render(line, True, (255, 255, 255))
            
            shadow_rect = shadow.get_rect(right=self.screen_width - 22, top=y_offset + 2)
            text_rect = text.get_rect(right=self.screen_width - 20, top=y_offset)
            
            self.screen.blit(shadow, shadow_rect)
            self.screen.blit(text, text_rect)
            y_offset += 40
        
        # Debug info with celestial object counts
        celestial_info = []
        if len(self.shooting_stars) > 0:
            celestial_info.append(f"Meteors: {len(self.shooting_stars)}")
        if len(self.satellites) > 0:
            celestial_info.append(f"Satellites: {len(self.satellites)}")
        if len(self.planets) > 0:
            planet_names = [p.type for p in self.planets]
            celestial_info.append(f"Planets: {', '.join(planet_names)}")
        if len(self.bright_flares) > 0:
            celestial_info.append(f"Flares: {len(self.bright_flares)}")
        
        debug_lines = [f"Clouds: {len(self.clouds)} | Particles: {len(self.particles)}"]
        if celestial_info:
            debug_lines.append(" | ".join(celestial_info))
        
        debug_y = 20
        for debug_line in debug_lines:
            debug_text = small_font.render(debug_line, True, (150, 150, 150))
            self.screen.blit(debug_text, (20, debug_y))
            debug_y += 25
        
        # City cycling countdown (if enabled and not transitioning)
        if self.cycle_cities and not self.in_location_transition:
            current_time = time.time()
            time_until_change = self.next_city_change - current_time
            if time_until_change > 0:
                countdown_text = f"Next city in: {int(time_until_change)}s"
                shadow = small_font.render(countdown_text, True, (0, 0, 0))
                text = small_font.render(countdown_text, True, (200, 200, 200))
                
                shadow_rect = shadow.get_rect(right=self.screen_width - 22, top=y_offset + 12)
                text_rect = text.get_rect(right=self.screen_width - 20, top=y_offset + 10)
                
                self.screen.blit(shadow, shadow_rect)
                self.screen.blit(text, text_rect)
    
    def draw(self):
        """Main draw function"""
        # Draw sky
        self.draw_sky_gradient()
        
        # Draw stars and Milky Way
        self.draw_stars()
        
        # Draw celestial objects (planets, satellites, shooting stars, flares)
        self.draw_celestial_objects()
        
        # Draw celestial objects (sun and moon)
        self.draw_sun()
        self.draw_moon()
        
        # Draw clouds
        self.draw_clouds()
        
        # Draw weather particles
        self.draw_particles()
        
        # Draw lightning
        self.draw_lightning()
        
        # Draw info
        self.draw_info_overlay()
    
    def run(self):
        """Main game loop"""
        print("\n🌌 Enhanced Sky Ceiling Projector Controls:")
        print("ESC - Exit")
        print("I - Toggle info display")
        print("D - Toggle debug mode (cycles through all weather)")
        print("SPACE - Manual lightning trigger (during thunderstorms)")
        print("R - Regenerate celestial objects (stars, planets, Milky Way)")
        if self.cycle_cities:
            print("N - Next city (manual)")
        print()
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_i:
                        self.show_info = not self.show_info
                        print(f"Info display: {'ON' if self.show_info else 'OFF'}")
                    elif event.key == pygame.K_d:
                        self.debug_mode = not self.debug_mode
                        if self.debug_mode:
                            print("🔧 DEBUG MODE ENABLED - Cycling through weather conditions")
                            self.forced_weather = DEBUG_WEATHER_CONDITIONS[0]
                            self.debug_weather_index = 0
                            self.debug_weather_timer = 0
                            self.update_weather_effects()
                        else:
                            print("🔧 DEBUG MODE DISABLED - Using real weather")
                            self.forced_weather = None
                            self.update_weather_effects()
                    elif event.key == pygame.K_SPACE:
                        if self.current_weather == "Thunderstorm":
                            self.lightning.trigger()
                    elif event.key == pygame.K_r:
                        print("🌟 Regenerating celestial objects...")
                        self.create_stars()
                        self.create_planets()
                        self.milky_way = MilkyWay(self.screen_width, self.screen_height)
                        # Clear existing celestial events
                        self.shooting_stars.clear()
                        self.satellites.clear()
                        self.bright_flares.clear()
                        print("✨ New starfield generated!")
                    elif event.key == pygame.K_n and self.cycle_cities:
                        # Manual city advance (only if not already transitioning)
                        if not self.in_location_transition:
                            self.city_index = (self.city_index + 1) % len(self.world_cities)
                            next_city = self.world_cities[self.city_index]
                            try:
                                lat, lon, tz, name = geocode_location(next_city)
                                self.location_change_queue.put((lat, lon, tz, name))
                                self.next_city_change = time.time() + self.cycle_interval + self.location_transition_duration
                                print(f"🌍 Manually switching to: {name}")
                            except Exception as e:
                                print(f"Failed to switch to {next_city}: {e}")
                        else:
                            print("⏳ Already transitioning, please wait...")
            
            dt = self.clock.tick(self.fps) / 1000.0
            self.update(dt)
            self.draw()
            pygame.display.flip()
        
        pygame.quit()


# Legacy support for direct execution (when used as a script)
if __name__ == "__main__":
    import argparse
    
    # Simple argument parsing for direct script execution
    parser = argparse.ArgumentParser(description="Sky Ceiling Projector")
    parser.add_argument("--location", "-l", required=True,
                        help="City[, State/ISO-country]. Example: 'Tampa, FL' or 'Berlin'")
    parser.add_argument("--preset", choices=["performance", "balanced", "quality"],
                        default="balanced", help="Graphics quality preset")
    parser.add_argument("--cycle-cities", action="store_true",
                        help="Demo mode: cycle through major world cities")
    parser.add_argument("--cycle-interval", type=int, default=300,
                        help="Seconds between city changes in demo mode")
    parser.add_argument("--no-info", action="store_true",
                        help="Disable information overlay display")
    args = parser.parse_args()
    
    # World cities for demo mode
    WORLD_CITIES = [
        "Paris, France", "Brisbane, Australia", "New York, NY, USA", "London, UK", 
        "Tokyo, Japan", "Sydney, Australia", "Cairo, Egypt", "Mumbai, India",
        "São Paulo, Brazil", "Reykjavik, Iceland", "Singapore", "Cape Town, South Africa",
        "Moscow, Russia", "Los Angeles, CA, USA", "Dubai, UAE", "Bangkok, Thailand",
        "Mexico City, Mexico", "Vancouver, Canada",
    ]
    
    # Set up initial location
    if args.cycle_cities:
        print("🌍 Demo Mode: Cycling through world cities...")
        initial_city = WORLD_CITIES[0]
    else:
        initial_city = args.location

    # Geocode initial location
    try:
        latitude, longitude, timezone, location_name = geocode_location(initial_city)
        print(f"Resolved '{initial_city}' → {latitude:.4f}, {longitude:.4f} ({timezone})")
        
        # Create and run simulator
        simulator = SkySimulator(
            latitude=latitude,
            longitude=longitude,
            timezone=timezone,
            location_name=location_name,
            preset=args.preset,
            cycle_cities=args.cycle_cities,
            cycle_interval=args.cycle_interval,
            show_info=not args.no_info,
            world_cities=WORLD_CITIES if args.cycle_cities else None
        )
        
        print(f"\n🌌 Enhanced Sky Ceiling Projector with Spectacular Starfield:")
        print(f"📍 Location: {location_name} ({latitude:.4f}, {longitude:.4f})")
        print(f"🎨 Quality preset: {args.preset}")
        print("✨ Enhanced Features:")
        print("   🌩️ Reliable weather effects that ALWAYS work!")
        print("   ☁️ Detailed realistic clouds with shadows and caching")
        print("   🌙 Realistic moon with craters and proper phases")
        print("   🌅 Smooth color transitions when changing locations")
        print("   🔧 Debug mode to test all weather conditions")
        print("   ⭐ VIBRANT STARFIELD with:")
        print("      🔴 Red giants and supergiants with cross spikes")
        print("      🔵 Blue giants and hot stars")
        print("      ✨ Variable stars that pulse and change brightness")
        print("      🌌 Milky Way galaxy with star clouds and dust lanes")
        print("      🪐 Visible planets (Venus, Mars, Jupiter, Saturn)")
        print("      🛰️ Satellites with blinking navigation lights")
        print("      ☄️ Enhanced shooting stars (meteors, fireballs)")
        print("      💫 Bright flares (Iridium flares, satellite glints)")
        print("      🎯 Press 'R' to regenerate the entire starfield!")
        if args.cycle_cities:
            print(f"   🌍 City cycling every {args.cycle_interval}s with smooth transitions")
        
        simulator.run()
        
    except Exception as e:
        print(f"❌ Failed to start projector: {e}")
        exit(1)
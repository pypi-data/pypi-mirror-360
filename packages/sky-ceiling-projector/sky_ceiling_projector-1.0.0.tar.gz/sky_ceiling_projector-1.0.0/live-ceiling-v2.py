#!/usr/bin/env python3
"""
Sky Ceiling Projector for Raspberry Pi Zero W
High-fidelity sky simulation that projects a dynamic, weather-driven sky.
Now with smooth transitions and ceiling-appropriate precipitation effects.
"""

from __future__ import annotations

import argparse
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

# ─────────────────────────────────────────────────────────────────────────────
# 1.  Geocoding helper  ───────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
def geocode_location(query: str,
                     *,
                     country_code: str | None = None,
                     user_agent: str = "sky_projector",
                     timeout: int = 5
                     ) -> Tuple[float, float, str, str]:
    """
    Resolve a human location string to (lat, lon, timezone, nice_name).

    Strategy:
    1️⃣  Open-Meteo Geocoding API   → no key, fast, returns tz directly.
    2️⃣  geopy.Nominatim fallback   → free OSM; obey 1 req/s policy.
    3️⃣  timezonefinder            → derive tz if geocoder lacks it.

    Raises RuntimeError on total failure.
    """
    # ------------------------------------------------------------------
    # 1) Open-Meteo
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

    # ------------------------------------------------------------------
    # 2) geopy → Nominatim (OpenStreetMap)
    try:
        from geopy.geocoders import Nominatim  # pip install geopy
        nom = Nominatim(user_agent=user_agent)
        loc = nom.geocode(query, exactly_one=True, timeout=timeout)
        if loc:
            lat, lon = loc.latitude, loc.longitude
            nice_name = loc.address.split(",")[0]
            # 3) timezonefinder if tz not provided
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

# ─────────────────────────────────────────────────────────────────────────────
# 2.  CLI: ask user for location  ─────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Sky Ceiling Projector")
parser.add_argument("--location", "-l", 
                    help="City[, State/ISO-country]. Example: 'Tampa, FL' or 'Berlin'")
parser.add_argument("--preset", choices=["performance", "balanced", "quality"],
                    default="balanced", help="Graphics quality preset")
parser.add_argument("--cycle-cities", action="store_true",
                    help="Demo mode: cycle through major world cities")
parser.add_argument("--cycle-interval", type=int, default=300,
                    help="Seconds between city changes in demo mode (default: 300)")
parser.add_argument("--no-info", action="store_true",
                    help="Disable information overlay display")
args = parser.parse_args()

# World cities for demo mode
WORLD_CITIES = [
    "Paris, France",
    "Brisbane, Australia",
    "New York, NY, USA",
    "London, UK", 
    "Tokyo, Japan",
    "Sydney, Australia",
    "Paris, France",
    "Cairo, Egypt",
    "Mumbai, India",
    "São Paulo, Brazil",
    "Reykjavik, Iceland",      # 64°N - Great for aurora!
    "Anchorage, AK, USA",      # 61°N - Excellent aurora location
    "Tromsø, Norway",          # 69°N - Prime aurora viewing
    "Fairbanks, AK, USA",      # 64°N - Aurora capital
    "Singapore",
    "Cape Town, South Africa",
    "Buenos Aires, Argentina",
    "Moscow, Russia",
    "Los Angeles, CA, USA",
    "Dubai, UAE",
    "Stockholm, Sweden",       # 59°N - Good aurora potential
    "Bangkok, Thailand",
    "Mexico City, Mexico",
    "Vancouver, Canada",       # 49°N - Occasional aurora
    "Yellowknife, Canada",     # 62°N - Aurora hotspot
    "Nuuk, Greenland"          # 64°N - Arctic aurora
]

# Set up initial location
if args.cycle_cities:
    print("🌍 Demo Mode: Cycling through world cities...")
    initial_city = WORLD_CITIES[0]
else:
    if not args.location:
        parser.error("--location is required unless using --cycle-cities")
    initial_city = args.location

# Geocode initial location
LATITUDE, LONGITUDE, TIMEZONE, LOCATION_NAME = geocode_location(initial_city)

print(f"Resolved '{initial_city}' → "
      f"{LATITUDE:.4f}, {LONGITUDE:.4f} ({TIMEZONE})")

# Configuration
SCREEN_WIDTH = 1920  # Adjust to your projector resolution
SCREEN_HEIGHT = 1080
FPS = 30
WEATHER_UPDATE_INTERVAL = 600  # Update weather every 10 minutes

# Performance Settings for Pi Zero W
QUALITY_PRESET = args.preset  # from CLI

# Quality presets
QUALITY_SETTINGS = {
    "performance": {
        "star_count": 150,
        "cloud_layers": 1,  # Reduced for performance
        "particle_limit": 100,
        "enable_glow": False,
        "enable_blur": False,
        "star_twinkle": True,
        "cloud_shadows": False,
        "atmospheric_scattering": False,
        "max_clouds_per_layer": 3  # New: limit clouds per layer
    },
    "balanced": {
        "star_count": 250,
        "cloud_layers": 2,  # Reduced from 3
        "particle_limit": 150,
        "enable_glow": True,
        "enable_blur": False,
        "star_twinkle": True,
        "cloud_shadows": True,
        "atmospheric_scattering": True,
        "max_clouds_per_layer": 5  # New: moderate cloud count
    },
    "quality": {
        "star_count": 400,
        "cloud_layers": 3,  # Reduced from 4
        "particle_limit": 200,
        "enable_glow": True,
        "enable_blur": True,
        "star_twinkle": True,
        "cloud_shadows": True,
        "atmospheric_scattering": True,
        "max_clouds_per_layer": 8  # New: higher cloud count for quality
    }
}

# Load quality settings
SETTINGS = QUALITY_SETTINGS[QUALITY_PRESET]

# Enhanced constellation data with more detail
CONSTELLATIONS = {
    "Orion": {
        "stars": [(0.3, 0.2), (0.35, 0.25), (0.35, 0.35), (0.3, 0.4), 
                  (0.25, 0.35), (0.25, 0.25), (0.3, 0.2), (0.45, 0.15), 
                  (0.5, 0.1), (0.15, 0.45), (0.1, 0.5)],
        "lines": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0), (1, 6), (6, 7), (4, 8), (8, 9)]
    },
    "Big Dipper": {
        "stars": [(0.6, 0.3), (0.65, 0.32), (0.7, 0.3), (0.72, 0.25),
                  (0.7, 0.2), (0.65, 0.18), (0.6, 0.2)],
        "lines": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 0)]
    },
    "Cassiopeia": {
        "stars": [(0.4, 0.6), (0.45, 0.58), (0.5, 0.62), (0.55, 0.58), (0.6, 0.6)],
        "lines": [(0, 1), (1, 2), (2, 3), (3, 4)]
    },
}

def smooth_step(t):
    """Smooth interpolation function for transitions"""
    return t * t * (3.0 - 2.0 * t)

def ease_in_out_cubic(t):
    """Cubic easing for very smooth transitions"""
    return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2

class Star:
    def __init__(self, x, y, brightness, twinkle_speed, size_class="normal", color_temp=1.0):
        self.x = x
        self.y = y
        self.base_brightness = brightness
        self.brightness = brightness
        self.twinkle_speed = twinkle_speed
        self.twinkle_phase = random.uniform(0, 2 * math.pi)
        self.size_class = size_class
        self.color_temp = color_temp  # 0=red, 0.5=yellow, 1=white/blue
        self.pulse_offset = random.uniform(0, 2 * math.pi)
        
    def update(self, dt):
        if SETTINGS["star_twinkle"]:
            # More realistic twinkling with atmospheric shimmer
            self.twinkle_phase += self.twinkle_speed * dt
            base_twinkle = math.sin(self.twinkle_phase)
            shimmer = math.sin(self.twinkle_phase * 3.7) * 0.1
            self.brightness = self.base_brightness * (0.8 + 0.2 * base_twinkle + shimmer)
        else:
            self.brightness = self.base_brightness
        
    def draw(self, screen):
        if self.brightness > 0.01:
            # Size based on brightness and class
            size_mult = {"dim": 0.5, "normal": 1, "bright": 1.5, "super": 2}[self.size_class]
            size = max(1, int(self.brightness * 3 * size_mult))
            
            # Color based on temperature
            if self.color_temp < 0.33:  # Red stars
                r = 255
                g = int(180 * (self.color_temp * 3))
                b = int(100 * (self.color_temp * 3))
            elif self.color_temp < 0.66:  # Yellow stars
                r = 255
                g = int(200 + 55 * ((self.color_temp - 0.33) * 3))
                b = int(100 + 100 * ((self.color_temp - 0.33) * 3))
            else:  # White/blue stars
                r = int(255 - 55 * ((self.color_temp - 0.66) * 3))
                g = int(255 - 15 * ((self.color_temp - 0.66) * 3))
                b = 255
            
            # Apply brightness
            color = (int(r * self.brightness), int(g * self.brightness), int(b * self.brightness))
            
            # Draw with optional glow
            if SETTINGS["enable_glow"] and size > 2:
                # Draw faint glow
                glow_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                temp_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, color, (size * 2, size * 2), size * 2)
                temp_surf.set_alpha(30)
                glow_surf.blit(temp_surf, (0, 0))
                screen.blit(glow_surf, (int(self.x - size * 2), int(self.y - size * 2)))
            
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), size)

class ShootingStar:
    def __init__(self):
        # Start from random edge
        edge = random.randint(0, 3)
        if edge == 0:  # Top
            self.x = random.uniform(0, SCREEN_WIDTH)
            self.y = 0
        elif edge == 1:  # Right
            self.x = SCREEN_WIDTH
            self.y = random.uniform(0, SCREEN_HEIGHT)
        elif edge == 2:  # Bottom
            self.x = random.uniform(0, SCREEN_WIDTH)
            self.y = SCREEN_HEIGHT
        else:  # Left
            self.x = 0
            self.y = random.uniform(0, SCREEN_HEIGHT)
        
        # Random direction towards center area
        center_x = random.uniform(SCREEN_WIDTH * 0.3, SCREEN_WIDTH * 0.7)
        center_y = random.uniform(SCREEN_HEIGHT * 0.3, SCREEN_HEIGHT * 0.7)
        angle = math.atan2(center_y - self.y, center_x - self.x)
        
        speed = random.uniform(600, 1000)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
        self.trail = deque(maxlen=25)
        self.lifetime = random.uniform(0.5, 1.2)
        self.age = 0
        self.brightness = random.uniform(0.8, 1.0)
        
    def update(self, dt):
        self.age += dt
        if self.age < self.lifetime:
            self.x += self.vx * dt
            self.y += self.vy * dt
            
            # Add to trail with interpolation for smoothness
            self.trail.append((self.x, self.y, self.age, self.brightness))
            
            return True
        return False
    
    def draw(self, screen):
        if len(self.trail) > 1:
            for i in range(len(self.trail) - 1):
                x1, y1, age1, _ = self.trail[i]
                x2, y2, age2, bright = self.trail[i + 1]
                
                # Fade based on position in trail and age
                alpha = (1 - age2 / self.lifetime) * (i / len(self.trail)) * bright
                if alpha > 0:
                    width = max(1, int(4 * alpha))
                    color = (int(255 * alpha), int(240 * alpha), int(200 * alpha))
                    pygame.draw.line(screen, color, (int(x1), int(y1)), (int(x2), int(y2)), width)

class AuroraWave:
    def __init__(self, y_base, layer):
        self.y_base = y_base
        self.phase = random.uniform(0, 2 * math.pi)
        self.amplitude = random.uniform(30, 80) * (1 + layer * 0.2)
        self.frequency = random.uniform(0.001, 0.003)
        self.speed = random.uniform(0.3, 1.0)
        self.color_shift = random.uniform(0, 1)
        self.layer = layer
        self.opacity = random.uniform(0.2, 0.4)
        
    def update(self, dt):
        self.phase += self.speed * dt
        
    def get_y(self, x, time):
        # Multiple wave frequencies for more complex movement
        primary = math.sin(x * self.frequency + self.phase)
        secondary = math.sin(x * self.frequency * 2.3 + self.phase * 1.7) * 0.3
        tertiary = math.sin(x * self.frequency * 0.7 + time) * 0.2
        return self.y_base + (primary + secondary + tertiary) * self.amplitude

class CloudLayer:
    def __init__(self, altitude_factor, opacity_range):
        self.clouds = []
        self.altitude_factor = altitude_factor  # 0-1, affects speed and size
        self.opacity_range = opacity_range
        self.wind_offset = random.uniform(0, 100)
        
    def update(self, dt, wind_speed, target_count):
        # Update existing clouds
        for cloud in self.clouds:
            cloud.update(dt)
        
        # Add/remove clouds to match target
        while len(self.clouds) < target_count:
            x = random.uniform(-300, SCREEN_WIDTH)
            y = random.uniform(0, SCREEN_HEIGHT * 0.6) * self.altitude_factor
            size = random.uniform(100, 250) * (1 + self.altitude_factor * 0.5)
            speed = wind_speed * (1 - self.altitude_factor * 0.5) + random.uniform(-10, 10)
            opacity = random.uniform(*self.opacity_range)
            self.clouds.append(Cloud(x, y, size, speed, opacity))
        
        while len(self.clouds) > target_count:
            self.clouds.pop()

class Cloud:
    def __init__(self, x, y, size, speed, opacity):
        self.x = x
        self.y = y
        self.size = size
        self.base_speed = speed
        self.speed = speed
        self.opacity = opacity
        self.blobs = []
        self.detail_level = random.randint(4, 8)  # Fewer blobs for efficiency
        
        # Pre-rendered cloud surfaces for performance
        self.cached_surface = None
        self.cached_shadow_surface = None
        self.cache_valid = False
        
        # Generate more realistic cloud shapes with stretching and irregularity
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
        
        if self.x > SCREEN_WIDTH + self.size:
            self.x = -self.size * 2
            self.y = random.uniform(0, SCREEN_HEIGHT * 0.6)
            self.cache_valid = False  # Invalidate cache for new position
    
    def get_cached_surface(self, cloud_color, light_factor):
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
                
                # Draw 3 layers for volume effect (reduced from more complex layering)
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
    
    def draw(self, screen, cloud_color, sun_pos=None):
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
        
        # Draw shadow first if enabled (simplified)
        if SETTINGS["cloud_shadows"] and sun_pos:
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
        cloud_surf = self.get_cached_surface(cloud_color, light_factor)
        
        # Draw the cached cloud
        if cloud_surf:
            cloud_x = self.x - cloud_surf.get_width() // 2
            cloud_y = self.y - cloud_surf.get_height() // 2
            screen.blit(cloud_surf, (int(cloud_x), int(cloud_y)))

class PrecipParticle:
    """Rain / Snow drawn as if falling *toward* the viewer, not radially."""
    __slots__ = ("x","y","z","vx","vy","kind","ttl","life","size","alpha")

    def __init__(self, kind: str, wind_px_s: float):
        self.kind = kind  # "rain" | "snow"
        self.reset(wind_px_s)

    def reset(self, wind_px_s: float):
        # spawn just *above* the top edge at random x
        self.x = random.uniform(-50, SCREEN_WIDTH + 50)
        self.y = random.uniform(-150, -10)
        # z‑depth 0 (far) .. 1 (near)
        self.z = random.uniform(0.2, 1.0)
        # velocity – down & slight wind drift
        speed = random.uniform(300, 600) if self.kind == "rain" else random.uniform(80, 140)
        self.vx = wind_px_s * 0.15  # gentle drift
        self.vy = speed * self.z      # perspective: nearer → faster
        self.life = 0.0
        self.ttl  = (SCREEN_HEIGHT + 200) / self.vy  # seconds until off‑screen
        # appearance cache
        self.size  = 1 + int(self.z * (4 if self.kind == "snow" else 2))
        self.alpha = 180 if self.kind == "rain" else 220

    # ---------------------------------------------------------------------
    def update(self, dt: float, wind_px_s: float):
        self.x += (self.vx + wind_px_s*0.02) * dt
        self.y += self.vy * dt
        self.life += dt
        if self.life > self.ttl or self.x < -120 or self.x > SCREEN_WIDTH+120:
            self.reset(wind_px_s)

    # ---------------------------------------------------------------------
    def draw(self, surf: pygame.Surface):
        if self.kind == "rain":
            end_y = self.y + self.vy*0.05  # short streak
            color = (200, 200, 255)
            pygame.draw.line(surf, color, (int(self.x), int(self.y)), (int(self.x), int(end_y)), max(1,self.size-1))
        else:  # snow
            color = (255, 255, 255)
            pygame.draw.circle(surf, color, (int(self.x), int(self.y)), self.size)


class PerspectiveParticle:
    """Enhanced particle for ceiling projection with perspective effects"""
    def __init__(self, particle_type, wind_strength=0):
        # Start particles at various "depths" in 3D space
        self.depth = random.uniform(0.1, 1.0)  # 0.1 = far away, 1.0 = close
        
        # Generate random angle for radial distribution
        self.angle = random.uniform(0, 2 * math.pi)
        
        # Distance from center varies with depth
        max_radius = min(SCREEN_WIDTH, SCREEN_HEIGHT) * 0.3  # Reduced initial radius
        self.radius = random.uniform(0, max_radius * (0.5 + self.depth * 0.5))  # Start closer to center
        
        # Calculate initial screen position
        center_x = SCREEN_WIDTH / 2
        center_y = SCREEN_HEIGHT / 2
        self.x = center_x + math.cos(self.angle) * self.radius
        self.y = center_y + math.sin(self.angle) * self.radius
        
        self.type = particle_type
        self.wind_strength = wind_strength
        self.age = 0
        
        # Perspective motion - particles appear to fall toward viewer
        # Radial velocity increases as particles get "closer"
        if particle_type == "snow":
            base_radial_speed = 80  # Slower for snow
        else:
            base_radial_speed = 150  # Faster for rain
            
        self.radial_velocity = base_radial_speed * (0.5 + self.depth * 1.5)
        
        # Rotational velocity for realism (wind effects)
        self.angular_velocity = random.uniform(-0.3, 0.3) + wind_strength * 0.05
        
        if particle_type == "rain":
            self.base_length = random.uniform(15, 25)
            self.opacity = random.uniform(0.4, 0.8)
        elif particle_type == "snow":
            self.base_size = random.uniform(2, 5)
            self.wobble = random.uniform(0, 2 * math.pi)
            self.wobble_speed = random.uniform(1, 3)
            self.opacity = random.uniform(0.7, 1.0)
    
    def update(self, dt):
        self.age += dt
        
        # Update radius (particles move toward viewer)
        self.radius += self.radial_velocity * dt
        
        # Update angle (wind/rotation effect)
        self.angle += self.angular_velocity * dt
        
        # Snow wobble effect
        if self.type == "snow":
            self.wobble += self.wobble_speed * dt
            # Add wobble to angle
            wobble_amount = math.sin(self.wobble) * 0.01
            effective_angle = self.angle + wobble_amount
        else:
            effective_angle = self.angle
        
        # Calculate new screen position
        center_x = SCREEN_WIDTH / 2
        center_y = SCREEN_HEIGHT / 2
        self.x = center_x + math.cos(effective_angle) * self.radius
        self.y = center_y + math.sin(effective_angle) * self.radius
        
        # Update depth based on radius (closer = higher depth)
        max_radius = min(SCREEN_WIDTH, SCREEN_HEIGHT) * 0.6
        self.depth = min(1.0, self.radius / max_radius)
        
        # Reset particle if it goes off screen or gets too close
        if (self.radius > max_radius or 
            self.x < -50 or self.x > SCREEN_WIDTH + 50 or 
            self.y < -50 or self.y > SCREEN_HEIGHT + 50):
            self.reset_particle()

    def reset_particle(self):
        """Reset particle to start position"""
        self.depth = random.uniform(0.1, 0.3)  # Start far away
        self.angle = random.uniform(0, 2 * math.pi)
        max_radius = min(SCREEN_WIDTH, SCREEN_HEIGHT) * 0.3
        self.radius = random.uniform(0, max_radius * 0.3)  # Start close to center
        self.age = 0
        
        # Recalculate position
        center_x = SCREEN_WIDTH / 2
        center_y = SCREEN_HEIGHT / 2
        self.x = center_x + math.cos(self.angle) * self.radius
        self.y = center_y + math.sin(self.angle) * self.radius

    def draw(self, screen):
        # Scale particle size based on depth (perspective)
        scale_factor = 0.3 + self.depth * 1.5  # Particles get bigger as they get closer
        
        if self.type == "rain":
            # Calculate rain drop properties with perspective
            length = self.base_length * scale_factor
            width = max(1, int(3 * scale_factor))
            
            # Rain direction follows radial motion
            angle_to_center = math.atan2(SCREEN_HEIGHT/2 - self.y, SCREEN_WIDTH/2 - self.x)
            end_x = self.x + math.cos(angle_to_center) * length
            end_y = self.y + math.sin(angle_to_center) * length
            
            # Enhanced rain colors
            blue_intensity = min(255, int(100 + 100 * self.depth))
            color = (blue_intensity, blue_intensity, 255)
            
            # Draw rain streak with better visibility
            alpha = int(150 * self.opacity * scale_factor)
            rain_surf = pygame.Surface((width + 10, int(length) + 10), pygame.SRCALPHA)
            
            # Draw thicker rain line
            pygame.draw.line(rain_surf, color, (5, 5), (5, int(length) + 5), width)
            rain_surf.set_alpha(alpha)
            screen.blit(rain_surf, (int(self.x - 5), int(self.y - 5)))
            
        elif self.type == "snow":
            # Calculate snowflake size with perspective
            size = max(1, int(self.base_size * scale_factor))
            
            # Color with depth-based brightness
            brightness = int(255 * (0.7 + 0.3 * self.depth))
            color = (brightness, brightness, brightness)
            
            # Enhanced snowflakes with better visibility
            alpha = int(200 * self.opacity * scale_factor)
            
            # Draw main snowflake
            snow_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
            pygame.draw.circle(snow_surf, color, (size * 2, size * 2), size)
            
            # Add sparkle effect for larger snowflakes
            if size > 2:
                # Draw cross pattern for snowflake detail
                pygame.draw.line(snow_surf, color, (size * 2 - size, size * 2), (size * 2 + size, size * 2), 1)
                pygame.draw.line(snow_surf, color, (size * 2, size * 2 - size), (size * 2, size * 2 + size), 1)
            
            snow_surf.set_alpha(alpha)
            screen.blit(snow_surf, (int(self.x - size * 2), int(self.y - size * 2)))

class LightningEffect:
    """Enhanced lightning effects for thunderstorms"""
    def __init__(self):
        self.active = False
        self.branches = []
        self.flash_alpha = 0
        self.flash_decay = 500  # How fast flash fades
        self.duration = 0
        self.max_duration = 0.3
        
    def trigger(self):
        """Trigger a new lightning strike"""
        if self.active:
            return  # Don't overlap lightning
            
        self.active = True
        self.duration = 0
        self.flash_alpha = 200 + random.randint(0, 55)  # Bright flash
        
        # Generate lightning branches
        self.branches = []
        
        # Main lightning bolt
        start_x = random.randint(int(SCREEN_WIDTH * 0.2), int(SCREEN_WIDTH * 0.8))
        start_y = 0
        
        # Create main branch
        main_branch = self.create_branch(start_x, start_y, random.randint(SCREEN_HEIGHT // 2, SCREEN_HEIGHT), 8)
        self.branches.extend(main_branch)
        
        # Add smaller branches
        for _ in range(random.randint(2, 5)):
            branch_start = random.choice(main_branch)
            if branch_start:
                sub_branch = self.create_branch(
                    branch_start[0], branch_start[1], 
                    random.randint(50, 200), 
                    random.randint(3, 6)
                )
                self.branches.extend(sub_branch)
    
    def create_branch(self, start_x, start_y, length, segments):
        """Create a jagged lightning branch"""
        points = [(start_x, start_y)]
        current_x = start_x
        current_y = start_y
        
        segment_length = length / segments
        
        for i in range(segments):
            # Add randomness to lightning path
            current_x += random.randint(-30, 30)
            current_y += segment_length + random.randint(-10, 10)
            
            # Keep within screen bounds
            current_x = max(0, min(SCREEN_WIDTH, current_x))
            current_y = max(0, min(SCREEN_HEIGHT, current_y))
            
            points.append((current_x, current_y))
        
        return points
    
    def update(self, dt):
        """Update lightning effect"""
        if not self.active:
            return
            
        self.duration += dt
        
        # Fade flash quickly
        self.flash_alpha = max(0, self.flash_alpha - self.flash_decay * dt)
        
        # End lightning after duration
        if self.duration >= self.max_duration:
            self.active = False
            self.branches = []
    
    def draw(self, screen):
        """Draw lightning effect"""
        if not self.active:
            return
        
        # Draw screen flash first
        if self.flash_alpha > 0:
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surf.fill((255, 255, 255))
            flash_surf.set_alpha(int(self.flash_alpha))
            screen.blit(flash_surf, (0, 0))
        
        # Draw lightning branches
        if self.branches:
            lightning_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            
            # Draw main lightning bolt
            if len(self.branches) > 1:
                # Core bolt (bright white)
                pygame.draw.lines(lightning_surf, (255, 255, 255), False, self.branches, 4)
                # Outer glow (blue-white)
                pygame.draw.lines(lightning_surf, (200, 220, 255), False, self.branches, 8)
                # Wider glow (purple-blue)
                pygame.draw.lines(lightning_surf, (150, 150, 255), False, self.branches, 12)
            
            # Set alpha based on flash intensity
            lightning_alpha = int(150 + self.flash_alpha * 0.5)
            lightning_surf.set_alpha(lightning_alpha)
            screen.blit(lightning_surf, (0, 0))

class SkyGradient:
    """Handles smooth sky color transitions with atmospheric scattering"""
    def __init__(self):
        self.cache = {}
        
    def get_gradient(self, color1, color2, height):
        """Create a gradient surface with atmospheric scattering"""
        key = (color1, color2, height)
        if key in self.cache:
            return self.cache[key]
        
        surf = pygame.Surface((1, height))
        for y in range(height):
            # Non-linear interpolation for more realistic atmosphere
            t = (y / height) ** 1.5
            r = int(color1[0] + (color2[0] - color1[0]) * t)
            g = int(color1[1] + (color2[1] - color1[1]) * t)
            b = int(color1[2] + (color2[2] - color1[2]) * t)
            surf.set_at((0, y), (r, g, b))
        
        self.cache[key] = surf
        return surf

class WeatherTransition:
    """Handles smooth transitions between weather conditions"""
    def __init__(self):
        self.current_condition = "Clear"
        self.target_condition = "Clear"
        self.transition_progress = 1.0
        self.transition_duration = 8.0  # Longer transition for smoother effect
        
        self.current_clouds = 0.0
        self.target_clouds = 0.0
        
        self.current_particles = 0
        self.target_particles = 0
        
    def start_transition(self, new_condition, new_clouds, new_particles):
        """Start a transition to new weather conditions"""
        if new_condition != self.target_condition:
            self.current_condition = self.target_condition
            self.target_condition = new_condition
            self.current_clouds = self.target_clouds
            self.target_clouds = new_clouds
            self.current_particles = self.target_particles
            self.target_particles = new_particles
            self.transition_progress = 0.0
            print(f"🌤️ Weather transitioning: {self.current_condition} → {self.target_condition}")
    
    def update(self, dt):
        """Update transition progress"""
        if self.transition_progress < 1.0:
            self.transition_progress = min(1.0, self.transition_progress + dt / self.transition_duration)
    
    def get_interpolated_values(self):
        """Get current interpolated weather values"""
        # Use cubic easing for very smooth transitions
        t = ease_in_out_cubic(self.transition_progress)
        
        clouds = self.current_clouds + (self.target_clouds - self.current_clouds) * t
        particles = int(self.current_particles + (self.target_particles - self.current_particles) * t)
        
        return clouds, particles, t

class SkySimulator:
    def __init__(self):
        pygame.init()
        
        # Try hardware acceleration
        try:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 
                                                pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
        except:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
            
        pygame.display.set_caption("Sky Ceiling Projector")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Location and timezone handling
        self.current_latitude = LATITUDE
        self.current_longitude = LONGITUDE
        self.current_timezone = TIMEZONE
        self.current_location_name = LOCATION_NAME
        
        # City cycling for demo mode
        self.cycle_cities = args.cycle_cities
        self.cycle_interval = args.cycle_interval
        self.city_index = 0
        self.last_city_change = time.time()
        self.next_city_change = self.last_city_change + self.cycle_interval
        self.location_change_queue = queue.Queue()
        
        # Enhanced transition system for smooth changes
        self.in_transition = False
        self.transition_progress = 0.0
        self.transition_duration = 8.0  # Longer transitions for smoother effect
        self.transition_direction = 0.0  # bearing in radians
        self.old_location_data = None
        self.new_location_data = None
        self.transition_offset_x = 0.0
        self.transition_offset_y = 0.0
        
        # Weather transition system
        self.weather_transition = WeatherTransition()
        
        # Weather data
        self.weather_queue = queue.Queue()
        self.weather_data = None
        self.wind_speed = 0
        self.wind_direction = 0
        
        # Sky elements
        self.stars = []
        self.constellation_stars = []
        self.constellation_lines = []
        self.cloud_layers = []
        self.particles = []  # Using new perspective particles
        self.shooting_stars = []
        
        #Particle Pools
        self.particle_pool: List[PrecipParticle] = []
        self.active_particles: List[PrecipParticle] = []

        # Lightning effect for thunderstorms
        self.lightning = LightningEffect()
        
        # Visual helpers
        self.gradient_helper = SkyGradient()
        
        # Enhanced color transition system
        self.current_sky_color = (0, 0, 0)
        self.current_horizon_color = (0, 0, 0)
        self.target_sky_color = (0, 0, 0)
        self.target_horizon_color = (0, 0, 0)
        self.color_transition_progress = 0.0
        self.color_transition_duration = 12.0  # Very slow color transitions
        
        # Moon and sun
        self.moon_phase = self.calculate_moon_phase()
        self.sun_position = (0, 0)
        self.moon_position = (0, 0)
        
        # Pre-generate static celestial details to avoid flickering
        self.moon_craters = self.generate_moon_craters()
        self.sun_spots = self.generate_sun_spots()
        
        # Timers
        self.next_shooting_star = time.time() + random.uniform(20, 90)
        self.time_acceleration = 1.0  # Can be increased for testing
        
        # Performance tracking and auto-adjustment
        self.frame_times = deque(maxlen=60)
        self.low_fps_counter = 0
        self.auto_adjust_quality = True
        
        # Info display toggle
        self.show_info = not args.no_info
        
        # Initialize sky elements
        self.create_stars()
        self.create_constellations()
        self.create_cloud_layers()
        
        # Start weather update thread
        self.weather_thread = Thread(target=self.weather_updater, daemon=True)
        self.weather_thread.start()
        
        # Start city cycling thread if enabled
        if self.cycle_cities:
            self.city_cycle_thread = Thread(target=self.city_cycler, daemon=True)
            self.city_cycle_thread.start()
    
    def generate_moon_craters(self):
        """Pre-generate static moon craters to avoid flickering"""
        craters = []
        radius = 45
        crater_count = 12
        
        # Use a fixed seed for consistent crater pattern
        import random
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
        import random
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
        """Calculate current moon phase (0 = new moon, 0.5 = full moon, 1 = new moon)"""
        # Known new moon date
        known_new_moon = datetime(2000, 1, 6, 18, 14)
        moon_cycle = 29.53059  # days
        
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
            # Fallback to system time
            return datetime.now()
    
    def create_stars(self):
        """Create a realistic starfield with varying star types"""
        star_count = SETTINGS["star_count"]
        
        # Create different star populations
        # Bright stars (10%)
        for _ in range(int(star_count * 0.1)):
            x = random.uniform(0, SCREEN_WIDTH)
            y = random.uniform(0, SCREEN_HEIGHT)
            brightness = random.uniform(0.8, 1.0)
            twinkle = random.uniform(2, 4)
            color_temp = random.uniform(0.3, 1.0)
            self.stars.append(Star(x, y, brightness, twinkle, "bright", color_temp))
        
        # Normal stars (60%)
        for _ in range(int(star_count * 0.6)):
            x = random.uniform(0, SCREEN_WIDTH)
            y = random.uniform(0, SCREEN_HEIGHT)
            brightness = random.uniform(0.4, 0.7)
            twinkle = random.uniform(1, 3)
            color_temp = random.uniform(0.4, 0.9)
            self.stars.append(Star(x, y, brightness, twinkle, "normal", color_temp))
        
        # Dim stars (30%)
        for _ in range(int(star_count * 0.3)):
            x = random.uniform(0, SCREEN_WIDTH)
            y = random.uniform(0, SCREEN_HEIGHT)
            brightness = random.uniform(0.1, 0.4)
            twinkle = random.uniform(0.5, 2)
            color_temp = random.uniform(0.5, 0.8)
            self.stars.append(Star(x, y, brightness, twinkle, "dim", color_temp))
    
    def create_constellations(self):
        """Create constellation patterns with enhanced detail"""
        for name, data in CONSTELLATIONS.items():
            # Random position and rotation for constellation
            base_x = random.uniform(200, SCREEN_WIDTH - 200)
            base_y = random.uniform(100, SCREEN_HEIGHT - 100)
            scale = random.uniform(250, 450)
            rotation = random.uniform(0, 2 * math.pi)
            
            constellation_points = []
            pattern_stars = data["stars"]
            
            for i, (px, py) in enumerate(pattern_stars):
                # Rotate and position
                x = px - 0.5
                y = py - 0.5
                rx = x * math.cos(rotation) - y * math.sin(rotation)
                ry = x * math.sin(rotation) + y * math.cos(rotation)
                
                final_x = base_x + rx * scale
                final_y = base_y + ry * scale
                
                # Vary brightness for constellation stars
                if i < 3:  # Main stars are brighter
                    brightness = random.uniform(0.9, 1.0)
                    star_class = "super"
                else:
                    brightness = random.uniform(0.7, 0.9)
                    star_class = "bright"
                
                star = Star(final_x, final_y, brightness, 
                           random.uniform(0.5, 1.5), star_class, 0.8)
                self.constellation_stars.append(star)
                constellation_points.append((final_x, final_y))
            
            # Store lines for this constellation
            lines = []
            for start, end in data["lines"]:
                if start < len(constellation_points) and end < len(constellation_points):
                    lines.append((constellation_points[start], constellation_points[end]))
            self.constellation_lines.append(lines)
    
    def create_cloud_layers(self):
        """Create multiple cloud layers for depth"""
        for i in range(SETTINGS["cloud_layers"]):
            altitude = i / SETTINGS["cloud_layers"]
            opacity = (0.2 - altitude * 0.1, 0.5 - altitude * 0.2)
            self.cloud_layers.append(CloudLayer(altitude, opacity))
    
    def calculate_bearing(self, lat1, lon1, lat2, lon2):
        """Calculate bearing from point 1 to point 2 in radians"""
        # Convert to radians
        lat1_r = math.radians(lat1)
        lat2_r = math.radians(lat2)
        lon_diff = math.radians(lon2 - lon1)
        
        # Calculate bearing
        y = math.sin(lon_diff) * math.cos(lat2_r)
        x = (math.cos(lat1_r) * math.sin(lat2_r) - 
             math.sin(lat1_r) * math.cos(lat2_r) * math.cos(lon_diff))
        
        bearing = math.atan2(y, x)
        return bearing
    
    def start_city_transition(self, new_lat, new_lon, new_tz, new_name):
        """Start smooth transition to new city"""
        # Calculate direction to new city
        self.transition_direction = self.calculate_bearing(
            self.current_latitude, self.current_longitude,
            new_lat, new_lon
        )
        
        # Store old and new location data
        self.old_location_data = {
            'lat': self.current_latitude,
            'lon': self.current_longitude,
            'tz': self.current_timezone,
            'name': self.current_location_name,
            'stars': self.stars.copy(),
            'constellation_stars': self.constellation_stars.copy(),
            'constellation_lines': [lines.copy() for lines in self.constellation_lines],
            'weather': self.weather_data
        }
        
        self.new_location_data = {
            'lat': new_lat,
            'lon': new_lon,
            'tz': new_tz,
            'name': new_name
        }
        
        # Start transition
        self.in_transition = True
        self.transition_progress = 0.0
        self.transition_offset_x = 0.0
        self.transition_offset_y = 0.0
        
        # Update location immediately for weather/time calculations
        self.current_latitude = new_lat
        self.current_longitude = new_lon
        self.current_timezone = new_tz
        self.current_location_name = new_name
        
        # Clear existing weather particles gradually
        # Don't clear immediately - let the weather transition handle it
        
        # Regenerate celestial details for new location (using coordinates as seed)
        location_seed = int(abs(new_lat * 1000) + abs(new_lon * 1000)) % 10000
        import random
        old_state = random.getstate()
        random.seed(location_seed)
        self.moon_craters = self.generate_moon_craters()
        self.sun_spots = self.generate_sun_spots()
        random.setstate(old_state)
        
        # Update moon phase immediately for new location
        self.moon_phase = self.calculate_moon_phase()
        
        # Force immediate weather update
        self.weather_data = None
        self.force_weather_update()
        
        print(f"🌍 Transitioning to: {new_name} (bearing: {math.degrees(self.transition_direction):.1f}°)")
    
    def force_weather_update(self):
        """Force an immediate weather update in a separate thread"""
        def update_weather():
            try:
                url = f"https://api.open-meteo.com/v1/forecast?latitude={self.current_latitude}&longitude={self.current_longitude}&current=temperature_2m,weather_code,cloud_cover,wind_speed_10m,wind_direction_10m&timezone={self.current_timezone}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    weather_code = data['current']['weather_code']
                    
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
                print(f"Force weather update error: {e}")
        
        Thread(target=update_weather, daemon=True).start()
    
    def update_transition(self, dt):
        """Update smooth city transition"""
        if not self.in_transition:
            return
        
        # Update transition progress
        self.transition_progress += dt / self.transition_duration
        
        if self.transition_progress >= 1.0:
            # Transition complete
            self.in_transition = False
            self.transition_progress = 0.0
            self.transition_offset_x = 0.0
            self.transition_offset_y = 0.0
            self.old_location_data = None
            
            # Regenerate sky elements for new location
            self.stars.clear()
            self.constellation_stars.clear()
            self.constellation_lines.clear()
            
            self.create_stars()
            self.create_constellations()
            
            print(f"✅ Arrived at: {self.current_location_name}")
            return
        
        # Smooth easing function (ease-in-out cubic for very smooth motion)
        t = self.transition_progress
        eased_t = ease_in_out_cubic(t)
        
        # Calculate camera offset based on direction
        max_offset = SCREEN_WIDTH * 0.8  # Maximum pan distance
        offset_distance = math.sin(eased_t * math.pi) * max_offset
        
        self.transition_offset_x = math.cos(self.transition_direction) * offset_distance
        self.transition_offset_y = -math.sin(self.transition_direction) * offset_distance
        
        # Create new sky elements gradually during transition
        if eased_t > 0.3 and not hasattr(self, '_new_stars_created'):
            self.create_stars()  # Create new stars for destination
            self.create_constellations()
            self._new_stars_created = True
        
        # Clean up the flag when transition ends
        if self.transition_progress >= 1.0 and hasattr(self, '_new_stars_created'):
            delattr(self, '_new_stars_created')
    
    def city_cycler(self):
        """Background thread to cycle through world cities"""
        while self.running and self.cycle_cities:
            current_time = time.time()
            if current_time >= self.next_city_change and not self.in_transition:
                # Move to next city
                self.city_index = (self.city_index + 1) % len(WORLD_CITIES)
                next_city = WORLD_CITIES[self.city_index]
                
                try:
                    lat, lon, tz, name = geocode_location(next_city)
                    self.location_change_queue.put((lat, lon, tz, name))
                except Exception as e:
                    print(f"Failed to switch to {next_city}: {e}")
                
                # Schedule next change (after transition completes)
                self.last_city_change = current_time
                self.next_city_change = current_time + self.cycle_interval + self.transition_duration
            
            time.sleep(5)  # Check every 5 seconds
    
    def change_location(self, lat, lon, tz, name):
        """Change the current location with smooth transition"""
        if self.in_transition:
            print(f"⏳ Already transitioning, skipping change to {name}")
            return
        
        self.start_city_transition(lat, lon, tz, name)
    
    def weather_updater(self):
        """Background thread to update weather data using Open-Meteo (FREE!)"""
        while self.running:
            try:
                # Open-Meteo API - completely free, no key needed!
                url = f"https://api.open-meteo.com/v1/forecast?latitude={self.current_latitude}&longitude={self.current_longitude}&current=temperature_2m,weather_code,cloud_cover,wind_speed_10m,wind_direction_10m&timezone={self.current_timezone}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Convert Open-Meteo format to our expected format
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
                    
                    # Format data to match our existing structure
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
    
    def get_sky_colors(self, hour, weather_condition, season):
        """Calculate sky and horizon colors with smooth transitions"""
        # Enhanced color palette for different times and seasons
        seasonal_tint = {
            "winter": (0.85, 0.9, 1.0),    # Cool blue tint
            "spring": (1.0, 1.0, 0.92),     # Slight warm tint
            "summer": (1.0, 0.92, 0.85),    # Golden warm tint
            "autumn": (1.0, 0.88, 0.8)      # Amber tint
        }
        
        # Sky and horizon colors for different times
        sky_colors = {
            0: ((10, 10, 30), (5, 5, 15)),      # Midnight
            5: ((25, 25, 50), (40, 30, 60)),    # Pre-dawn
            6: ((60, 40, 80), (120, 80, 100)),  # Dawn
            7: ((140, 100, 150), (255, 150, 100)),  # Sunrise
            8: ((135, 180, 235), (180, 210, 240)),  # Morning
            12: ((110, 160, 255), (150, 200, 255)), # Noon
            17: ((180, 150, 120), (255, 180, 100)), # Late afternoon
            18: ((200, 100, 80), (255, 140, 60)),   # Sunset
            19: ((80, 40, 70), (140, 60, 90)),     # Dusk
            20: ((30, 20, 50), (50, 30, 70)),      # Evening
            22: ((15, 15, 35), (20, 15, 40)),      # Night
        }
        
        # Find surrounding hours for interpolation
        hours = sorted(sky_colors.keys())
        prev_hour = max([h for h in hours if h <= hour], default=0)
        next_hour = min([h for h in hours if h > hour], default=24)
        
        if next_hour == 24:
            next_hour = 0
        
        # Interpolate between colors
        if prev_hour == next_hour:
            sky_color, horizon_color = sky_colors[prev_hour]
        else:
            t = (hour - prev_hour) / ((next_hour - prev_hour) if next_hour > prev_hour else (24 - prev_hour + next_hour))
            
            # Smooth interpolation using cosine
            t = (1 - math.cos(t * math.pi)) / 2
            
            prev_sky, prev_horizon = sky_colors[prev_hour]
            next_sky, next_horizon = sky_colors[next_hour]
            
            sky_color = tuple(int(prev_sky[i] + (next_sky[i] - prev_sky[i]) * t) for i in range(3))
            horizon_color = tuple(int(prev_horizon[i] + (next_horizon[i] - prev_horizon[i]) * t) for i in range(3))
        
        # Apply seasonal tint
        tint = seasonal_tint[season]
        sky_color = tuple(int(sky_color[i] * tint[i]) for i in range(3))
        horizon_color = tuple(int(horizon_color[i] * tint[i]) for i in range(3))
        
        # Weather modifications
        if "cloud" in weather_condition:
            sky_color = tuple(int(c * 0.7) for c in sky_color)
            horizon_color = tuple(int(c * 0.8) for c in horizon_color)
        elif "rain" in weather_condition or "storm" in weather_condition:
            sky_color = tuple(int(c * 0.5) for c in sky_color)
            horizon_color = tuple(int(c * 0.6) for c in horizon_color)
        elif "fog" in weather_condition:
            # Fog creates uniform gray
            avg = sum(sky_color) // 3
            sky_color = (avg, avg, avg)
            horizon_color = (avg + 20, avg + 20, avg + 20)
        
        return sky_color, horizon_color
    
    def get_season(self):
        """Get current season based on local time month and hemisphere"""
        local_time = self.get_local_time()
        month = local_time.month
        
        # Determine hemisphere based on latitude
        is_northern_hemisphere = self.current_latitude >= 0
        
        if is_northern_hemisphere:
            # Northern hemisphere seasons
            if month in [12, 1, 2]:
                return "winter"
            elif month in [3, 4, 5]:
                return "spring"
            elif month in [6, 7, 8]:
                return "summer"
            else:  # [9, 10, 11]
                return "autumn"
        else:
            # Southern hemisphere seasons (opposite of northern)
            if month in [12, 1, 2]:
                return "summer"
            elif month in [3, 4, 5]:
                return "autumn"
            elif month in [6, 7, 8]:
                return "winter"
            else:  # [9, 10, 11]
                return "spring"
    
    def update_weather_effects(self):
        if not self.weather_data:
            return
        weather_raw = self.weather_data['weather'][0]['main']
        weather = weather_raw.lower()
        clouds_fraction = self.weather_data['clouds']['all']/100

        # set sane defaults
        particle_kind = None
        target_particles = 0

        if 'snow' in weather:
            particle_kind = 'snow'
            target_particles = min(SETTINGS['particle_limit'], 220)
            clouds_fraction = max(clouds_fraction, 0.5)
        elif 'rain' in weather or 'drizzle' in weather:
            particle_kind = 'rain'
            target_particles = min(SETTINGS['particle_limit'], 280)
            clouds_fraction = max(clouds_fraction, 0.6)
        elif 'thunderstorm' in weather:
            particle_kind = 'rain'
            target_particles = min(SETTINGS['particle_limit'], 320)
            clouds_fraction = max(clouds_fraction, 0.8)
        else:
            # clear / fog etc.
            clouds_fraction = clouds_fraction * 0.9

        # Begin smooth transition
        self.weather_transition.start_transition(weather, clouds_fraction, target_particles)

        # Interpolated values
        clouds_now, particles_now, _ = self.weather_transition.get_interpolated_values()

        # ------------------------------------------------------------------
        # Cloud management
        base_total = int(clouds_now * SETTINGS['max_clouds_per_layer'])
        for idx, layer in enumerate(self.cloud_layers):
            desired = max(0, base_total - idx)
            layer.update(0, self.wind_speed*(1-idx*0.2), desired)

        # ------------------------------------------------------------------
        # Particle pool management
        if particle_kind:
            # ensure pool large enough
            while len(self.particle_pool) < particles_now:
                self.particle_pool.append(PrecipParticle(particle_kind, self.wind_speed))
            # activate required particles
            self.active_particles = self.particle_pool[:particles_now]
            for p in self.active_particles:
                p.kind = particle_kind  # switch type if weather changed
        else:
            # no precipitation
            self.active_particles = []
    
    def calculate_celestial_positions(self, hour):
        """Calculate realistic sun and moon positions"""
        # Sun position (only during day)
        if 5 <= hour <= 19:  # Sun visible from 5 AM to 7 PM
            sun_progress = (hour - 5) / 14  # 0 to 1 across day
            sun_angle = sun_progress * math.pi  # 0 to π
            sun_x = SCREEN_WIDTH * 0.1 + SCREEN_WIDTH * 0.8 * sun_progress
            sun_y = SCREEN_HEIGHT * 0.9 - SCREEN_HEIGHT * 0.7 * math.sin(sun_angle)
            self.sun_position = (sun_x, sun_y)
        else:
            self.sun_position = None
        
        # Moon position (only at night and during twilight)
        if hour < 6 or hour > 18:  # Moon visible from 6 PM to 6 AM
            # Calculate moon position opposite to sun with some variation
            if hour > 18:
                # Evening: moon rises in east
                moon_progress = (hour - 18) / 12  # 0 to 1 from 6 PM to 6 AM
            else:
                # Early morning: moon sets in west  
                moon_progress = (hour + 6) / 12  # Continue the arc
            
            moon_angle = moon_progress * math.pi
            moon_x = SCREEN_WIDTH * 0.1 + SCREEN_WIDTH * 0.8 * moon_progress
            moon_y = SCREEN_HEIGHT * 0.9 - SCREEN_HEIGHT * 0.6 * math.sin(moon_angle)
            
            # Add some randomness to moon position based on phase
            phase_offset_x = (self.moon_phase - 0.5) * 100
            phase_offset_y = math.sin(self.moon_phase * 2 * math.pi) * 30
            
            self.moon_position = (moon_x + phase_offset_x, moon_y + phase_offset_y)
        else:
            self.moon_position = None
    
    def update(self, dt):
        """Update all sky elements with time acceleration support"""
        # Apply time acceleration for testing
        dt *= self.time_acceleration
        
        # Track performance
        self.frame_times.append(dt)
        
        # Auto-adjust quality if performance is poor
        if len(self.frame_times) >= 60 and self.auto_adjust_quality:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            current_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
            
            if current_fps < 15:  # If FPS drops below 15
                self.low_fps_counter += 1
                if self.low_fps_counter > 180:  # 3 seconds of low FPS
                    # Reduce cloud quality automatically
                    for layer in self.cloud_layers:
                        if len(layer.clouds) > 2:
                            layer.clouds.pop()  # Remove a cloud
                    self.low_fps_counter = 0
                    print(f"⚠️ Performance adjustment: Reduced cloud count (FPS: {current_fps:.1f})")
            else:
                self.low_fps_counter = 0
        
        # Update city transition
        self.update_transition(dt)
        
        # Update weather transition
        self.weather_transition.update(dt)
        
        # Check for location changes (city cycling)
        try:
            lat, lon, tz, name = self.location_change_queue.get_nowait()
            self.change_location(lat, lon, tz, name)
        except queue.Empty:
            pass
        
        # Check for new weather data
        try:
            self.weather_data = self.weather_queue.get_nowait()
            self.update_weather_effects()
        except queue.Empty:
            pass
        
        # Update sky color using local time
        local_time = self.get_local_time()
        hour = local_time.hour + local_time.minute / 60.0
        season = self.get_season()
        
        weather_condition = ""
        if self.weather_data:
            weather_condition = self.weather_data['weather'][0]['main'].lower()
        
        new_sky_color, new_horizon_color = self.get_sky_colors(hour, weather_condition, season)
        
        # Start color transition if colors have changed significantly
        if (abs(new_sky_color[0] - self.target_sky_color[0]) > 10 or 
            abs(new_sky_color[1] - self.target_sky_color[1]) > 10 or 
            abs(new_sky_color[2] - self.target_sky_color[2]) > 10):
            
            self.current_sky_color = self.target_sky_color
            self.current_horizon_color = self.target_horizon_color
            self.target_sky_color = new_sky_color
            self.target_horizon_color = new_horizon_color
            self.color_transition_progress = 0.0
        
        # Update color transition with very smooth easing
        if self.color_transition_progress < 1.0:
            self.color_transition_progress = min(1.0, 
                self.color_transition_progress + dt / self.color_transition_duration)
            
            # Use cubic easing for very smooth color transitions
            t = ease_in_out_cubic(self.color_transition_progress)
            
            # Interpolate colors
            self.current_sky_color = tuple(
                int(self.current_sky_color[i] + (self.target_sky_color[i] - self.current_sky_color[i]) * t)
                for i in range(3)
            )
            self.current_horizon_color = tuple(
                int(self.current_horizon_color[i] + (self.target_horizon_color[i] - self.current_horizon_color[i]) * t)
                for i in range(3)
            )
        
        # Update celestial positions
        self.calculate_celestial_positions(hour)
        
        # Update moon phase more frequently for accuracy
        if random.random() < 0.01:  # Update 1% of frames instead of 0.01%
            self.moon_phase = self.calculate_moon_phase()
        
        # Update lightning effects
        self.lightning.update(dt)
        
        # Trigger lightning during thunderstorms
        if (self.weather_data and "thunderstorm" in self.weather_data['weather'][0]['main'].lower() 
            and random.random() < 0.001):  # 0.1% chance per frame
            self.lightning.trigger()
        
        # Calculate star visibility
        star_visibility = 0
        if hour < 6 or hour > 20:
            star_visibility = 1
        elif hour < 7 or hour > 19:
            star_visibility = 0.5 * (1 - abs(hour - 6.5 if hour < 12 else hour - 19.5))
        
        # Reduce star visibility based on moon brightness
        if self.moon_position and 0.25 < self.moon_phase < 0.75:
            moon_brightness = 1 - abs(self.moon_phase - 0.5) * 2
            star_visibility *= (1 - moon_brightness * 0.6)
        
        # Update all stars
        for star in self.stars + self.constellation_stars:
            star.update(dt)
            # Apply visibility with atmospheric extinction
            extinction = 1.0
            if hasattr(star, 'y'):
                # Stars near horizon appear dimmer
                extinction = 1 - (star.y / SCREEN_HEIGHT) * 0.3
            star.brightness = min(star.brightness, star.base_brightness * star_visibility * extinction)
        
        # Update old stars during transition
        if self.in_transition and self.old_location_data:
            for star in self.old_location_data['stars'] + self.old_location_data['constellation_stars']:
                star.update(dt)
                # Apply visibility with atmospheric extinction
                extinction = 1.0
                if hasattr(star, 'y'):
                    extinction = 1 - (star.y / SCREEN_HEIGHT) * 0.3
                star.brightness = min(star.brightness, star.base_brightness * star_visibility * extinction)
        
        # Update cloud layers
        for layer in self.cloud_layers:
            layer.update(dt, self.wind_speed, len(layer.clouds))
        
        # Update perspective particles
        #for particle in self.particles:
        #    particle.update(dt)
        for p in self.active_particles:
            p.update(dt, self.wind_speed)
        # Update shooting stars
        self.shooting_stars = [s for s in self.shooting_stars if s.update(dt)]
        
        # Spawn new shooting star
        if time.time() > self.next_shooting_star and star_visibility > 0.5:
            self.shooting_stars.append(ShootingStar())
            # More frequent during meteor showers (August, December)
            month = local_time.month
            if month in [8, 12]:
                self.next_shooting_star = time.time() + random.uniform(10, 30)
            else:
                self.next_shooting_star = time.time() + random.uniform(30, 120)
    
    def draw_sky_gradient(self):
        """Draw atmospheric sky gradient"""
        if SETTINGS["atmospheric_scattering"]:
            # Create gradient
            gradient = self.gradient_helper.get_gradient(
                self.current_horizon_color, 
                self.current_sky_color, 
                SCREEN_HEIGHT
            )
            
            # Scale and draw gradient
            scaled = pygame.transform.scale(gradient, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.screen.blit(scaled, (0, 0))
        else:
            # Simple fill
            self.screen.fill(self.current_sky_color)
    
    def draw_stars(self):
        """Draw all stars with proper layering and transition effects"""
        
        # Apply transition offset for camera movement effect
        offset_x = self.transition_offset_x if self.in_transition else 0
        offset_y = self.transition_offset_y if self.in_transition else 0
        
        # During transition, draw old stars with fade-out
        if self.in_transition and self.old_location_data:
            fade_alpha = 1.0 - self.transition_progress
            
            # Draw old background stars first
            for star in self.old_location_data['stars']:
                if star.size_class == "dim":
                    self.draw_star_with_offset(star, -offset_x, -offset_y, fade_alpha)
            
            # Draw old constellation lines if visible
            if (self.old_location_data['constellation_stars'] and 
                self.old_location_data['constellation_stars'][0].brightness > 0.3):
                for constellation in self.old_location_data['constellation_lines']:
                    for start, end in constellation:
                        alpha = int(40 * self.old_location_data['constellation_stars'][0].brightness * fade_alpha)
                        start_pos = (int(start[0] - offset_x), int(start[1] - offset_y))
                        end_pos = (int(end[0] - offset_x), int(end[1] - offset_y))
                        if alpha > 0:
                            pygame.draw.line(self.screen, (alpha, alpha, alpha), start_pos, end_pos, 1)
            
            # Draw old medium and bright stars
            for star in self.old_location_data['stars']:
                if star.size_class in ["normal", "bright", "super"]:
                    self.draw_star_with_offset(star, -offset_x, -offset_y, fade_alpha)
            
            for star in self.old_location_data['constellation_stars']:
                if star.size_class in ["bright", "super"]:
                    self.draw_star_with_offset(star, -offset_x, -offset_y, fade_alpha)
        
        # Draw current stars (with fade-in during transition)
        fade_alpha = self.transition_progress if self.in_transition else 1.0
        
        # Draw background stars first
        for star in self.stars:
            if star.size_class == "dim":
                self.draw_star_with_offset(star, offset_x, offset_y, fade_alpha)
        
        # Draw constellation lines if visible
        if self.constellation_stars and self.constellation_stars[0].brightness > 0.3:
            for constellation in self.constellation_lines:
                for start, end in constellation:
                    alpha = int(40 * self.constellation_stars[0].brightness * fade_alpha)
                    start_pos = (int(start[0] + offset_x), int(start[1] + offset_y))
                    end_pos = (int(end[0] + offset_x), int(end[1] + offset_y))
                    if alpha > 0:
                        pygame.draw.line(self.screen, (alpha, alpha, alpha), start_pos, end_pos, 1)
        
        # Draw medium stars
        for star in self.stars:
            if star.size_class == "normal":
                self.draw_star_with_offset(star, offset_x, offset_y, fade_alpha)
        
        # Draw bright stars and constellations
        for star in self.stars + self.constellation_stars:
            if star.size_class in ["bright", "super"]:
                self.draw_star_with_offset(star, offset_x, offset_y, fade_alpha)
    
    def draw_star_with_offset(self, star, offset_x, offset_y, alpha_mult=1.0):
        """Draw a star with position offset and alpha multiplier"""
        if star.brightness * alpha_mult > 0.01:
            # Calculate adjusted position
            adj_x = star.x + offset_x
            adj_y = star.y + offset_y
            
            # Skip if star is off screen (with some margin)
            if adj_x < -50 or adj_x > SCREEN_WIDTH + 50 or adj_y < -50 or adj_y > SCREEN_HEIGHT + 50:
                return
            
            # Size based on brightness and class
            size_mult = {"dim": 0.5, "normal": 1, "bright": 1.5, "super": 2}[star.size_class]
            size = max(1, int(star.brightness * alpha_mult * 3 * size_mult))
            
            # Color based on temperature
            if star.color_temp < 0.33:  # Red stars
                r = 255
                g = int(180 * (star.color_temp * 3))
                b = int(100 * (star.color_temp * 3))
            elif star.color_temp < 0.66:  # Yellow stars
                r = 255
                g = int(200 + 55 * ((star.color_temp - 0.33) * 3))
                b = int(100 + 100 * ((star.color_temp - 0.33) * 3))
            else:  # White/blue stars
                r = int(255 - 55 * ((star.color_temp - 0.66) * 3))
                g = int(255 - 15 * ((star.color_temp - 0.66) * 3))
                b = 255
            
            # Apply brightness and alpha
            color = (int(r * star.brightness * alpha_mult), 
                    int(g * star.brightness * alpha_mult), 
                    int(b * star.brightness * alpha_mult))
            
            # Draw with optional glow
            if SETTINGS["enable_glow"] and size > 2:
                # Draw faint glow
                glow_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                glow_alpha = int(30 * alpha_mult)
                temp_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, color, (size * 2, size * 2), size * 2)
                temp_surf.set_alpha(glow_alpha)
                glow_surf.blit(temp_surf, (0, 0))
                self.screen.blit(glow_surf, (int(adj_x - size * 2), int(adj_y - size * 2)))
            
            pygame.draw.circle(self.screen, color, (int(adj_x), int(adj_y)), size)
    
    def draw_moon(self):
        """Draw realistic moon with pre-generated craters and smooth shading"""
        if not self.moon_position:
            return
        
        moon_x, moon_y = self.moon_position
        radius = 45
        
        # Create moon surface with realistic gradient
        moon_surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        center = radius #* 2
        
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
        if SETTINGS["enable_glow"]:
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
            
            self.screen.blit(glow_surf, 
                           (int(moon_x - (glow_radius*1.65)), int(moon_y - (glow_radius*1.65))))
        
        # Draw the main moon surface
        self.screen.blit(moon_surf, (int(moon_x - radius * 2), int(moon_y - radius * 2)))
    
    def draw_sun(self):
        """Draw realistic sun with corona and pre-generated surface details"""
        if not self.sun_position:
            return
        
        sun_x, sun_y = self.sun_position
        sun_radius = 55
        
        # Seasonal sun color variations
        season = self.get_season()
        sun_colors = {
            "winter": (255, 220, 180),
            "spring": (255, 240, 200),
            "summer": (255, 245, 210),
            "autumn": (255, 230, 190)
        }
        base_sun_color = sun_colors[season]
        
        # Draw corona/atmospheric glow first
        if SETTINGS["enable_glow"]:
            corona_layers = 8
            
            for i in range(corona_layers):
                corona_radius = sun_radius + (i + 1) * 10
                corona_alpha = int(60 * (1 - i / corona_layers) ** 2)
                
                # Create corona color with proper bounds checking
                brightness_factor = 0.9 + i * 0.02
                corona_color = tuple(min(255, max(0, int(c * brightness_factor))) for c in base_sun_color)
                
                corona_surf = pygame.Surface((corona_radius * 2, corona_radius * 2), pygame.SRCALPHA)
                # Draw with RGB color, then set alpha on surface
                pygame.draw.circle(corona_surf, corona_color, 
                                 (corona_radius, corona_radius), corona_radius)
                corona_surf.set_alpha(corona_alpha)
                
                self.screen.blit(corona_surf, 
                               (int(sun_x - corona_radius), int(sun_y - corona_radius)))
        
        # Create main sun surface with radial gradient
        sun_surf = pygame.Surface((sun_radius * 2, sun_radius * 2), pygame.SRCALPHA)
        
        # Draw sun with realistic gradient from center to edge
        for r in range(sun_radius, 0, -1):
            # Create natural brightness falloff
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
                # Ensure intensity is valid
                intensity = max(0.1, min(1.0, intensity))
                spot_color = tuple(max(0, min(255, int(c * intensity))) for c in base_sun_color)
                
                # Draw simple sunspot without complex alpha layering
                pygame.draw.circle(sun_surf, spot_color, 
                                 (int(spot_x), int(spot_y)), int(spot_radius))
        
        # Add subtle surface texture with plasma-like effects (pre-generated)
        # Use pre-generated texture pattern to avoid flickering
        import random
        old_state = random.getstate()
        random.seed(456)  # Fixed seed for consistent texture
        
        for i in range(15):  # Reduced number for performance
            # Create subtle brightness variations
            tex_x = random.uniform(15, sun_radius * 2 - 15)
            tex_y = random.uniform(15, sun_radius * 2 - 15)
            tex_radius = random.uniform(4, 8)
            tex_brightness = random.uniform(0.98, 1.02)
            
            # Check if texture is within sun circle
            dist = math.sqrt((tex_x - sun_radius)**2 + (tex_y - sun_radius)**2)
            if dist + tex_radius < sun_radius:
                # Ensure brightness is valid
                tex_brightness = max(0.5, min(1.5, tex_brightness))
                tex_color = tuple(max(0, min(255, int(c * tex_brightness))) for c in base_sun_color)
                
                # Draw simple texture spots
                pygame.draw.circle(sun_surf, tex_color, (int(tex_x), int(tex_y)), int(tex_radius))
        
        random.setstate(old_state)  # Restore random state
        
        # Draw the main sun
        self.screen.blit(sun_surf, (int(sun_x - sun_radius), int(sun_y - sun_radius)))
    
    def draw_aurora(self):
        """Draw aurora borealis with enhanced effects based on latitude"""
        if self.aurora_intensity <= 0:
            return
        
        aurora_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        current_time = time.time()
        
        # Intensity based on latitude - stronger at higher latitudes
        abs_lat = abs(self.current_latitude)
        latitude_intensity = min(1.0, max(0.3, (abs_lat - 40) / 40))
        effective_intensity = self.aurora_intensity * latitude_intensity
        
        for i, wave in enumerate(self.aurora_waves):
            # More dramatic colors at higher latitudes
            if abs_lat >= 65:  # Arctic regions
                colors = [
                    (0, 255, 100),    # Bright Green
                    (0, 255, 200),    # Bright Cyan  
                    (150, 100, 255),  # Purple
                    (255, 100, 200),  # Pink
                    (100, 255, 255),  # Bright Teal
                    (255, 255, 100),  # Yellow
                ]
            elif abs_lat >= 55:  # Sub-arctic (Iceland, Alaska)
                colors = [
                    (0, 200, 80),     # Green
                    (0, 200, 160),    # Cyan
                    (120, 80, 200),   # Purple
                    (200, 80, 160),   # Pink
                    (80, 200, 120),   # Teal
                ]
            else:  # Lower latitudes - dimmer
                colors = [
                    (0, 150, 60),     # Dim Green
                    (0, 150, 120),    # Dim Cyan
                    (90, 60, 150),    # Dim Purple
                ]
            
            color_idx = i % len(colors)
            base_color = colors[color_idx]
            
            # Draw vertical curtains with improved visibility
            step_size = 2 if abs_lat >= 60 else 3  # Denser at high latitudes
            for x in range(0, SCREEN_WIDTH, step_size):
                y = wave.get_y(x, current_time)
                base_height = 60 if abs_lat >= 60 else 40
                height = base_height + math.sin(x * 0.005 + wave.phase) * 30
                
                # Create vertical gradient with pulsing effect
                for h in range(int(height)):
                    # Enhanced fade and wave effect
                    fade = (1 - h / height) ** 1.2
                    wave_mod = 1 + math.sin(h * 0.03 + current_time * 3) * 0.4
                    pulse = 1 + math.sin(current_time * 2) * 0.2  # Overall pulsing
                    
                    alpha = fade * effective_intensity * 0.7 * wave_mod * pulse
                    
                    if alpha > 0.02:
                        # Create temporary surface for better alpha blending
                        line_surf = pygame.Surface((step_size + 2, 2), pygame.SRCALPHA)
                        pygame.draw.line(line_surf, base_color, (0, 1), (step_size + 1, 1))
                        line_surf.set_alpha(int(alpha * 255))
                        aurora_surface.blit(line_surf, (x, int(y + h)))
        
        # Apply to screen with additive blending for glow effect
        self.screen.blit(aurora_surface, (0, 0), special_flags=pygame.BLEND_ADD)
    
    def draw_clouds(self):
        """Draw cloud layers with proper ordering and transition effects"""
        local_time = self.get_local_time()
        hour = local_time.hour + local_time.minute / 60.0
        
        # Determine cloud color based on time
        if 5 < hour < 7:  # Dawn
            cloud_color = (255, 180, 150)
        elif 17 < hour < 19:  # Dusk
            cloud_color = (220, 150, 180)
        elif 6 < hour < 18:  # Day
            cloud_color = (220, 220, 220)
        else:  # Night
            cloud_color = (80, 80, 100)
        
        # Apply transition offset
        offset_x = self.transition_offset_x if self.in_transition else 0
        offset_y = self.transition_offset_y if self.in_transition else 0
        
        # Draw cloud layers from back to front
        for i in range(len(self.cloud_layers) - 1, -1, -1):
            layer = self.cloud_layers[i]
            # Adjust color for depth
            layer_color = tuple(int(c * (0.8 + i * 0.1)) for c in cloud_color)
            
            for cloud in layer.clouds:
                self.draw_cloud_with_offset(cloud, layer_color, self.sun_position, offset_x, offset_y)
    
    def draw_cloud_with_offset(self, cloud, cloud_color, sun_pos, offset_x, offset_y):
        """Draw a cloud with position offset (optimized version)"""
        adj_x = cloud.x + offset_x
        adj_y = cloud.y + offset_y
        
        # Skip if cloud is way off screen
        if adj_x < -cloud.size * 3 or adj_x > SCREEN_WIDTH + cloud.size * 3:
            return
        
        # Adjust sun position for lighting calculations
        adj_sun_pos = None
        if sun_pos:
            adj_sun_pos = (sun_pos[0] + offset_x, sun_pos[1] + offset_y)
        
        # Calculate lighting based on sun position
        light_factor = 1.0
        shadow_offset_x = 0
        shadow_offset_y = 0
        
        if adj_sun_pos:
            sun_angle = math.atan2(adj_sun_pos[1] - adj_y, adj_sun_pos[0] - adj_x)
            light_factor = 0.7 + 0.3 * max(0, math.cos(sun_angle + math.pi * 0.25))
            shadow_offset_x = -math.cos(sun_angle) * 12
            shadow_offset_y = -math.sin(sun_angle) * 6
        
        # Draw shadow first if enabled (stretched elliptical)
        if SETTINGS["cloud_shadows"] and adj_sun_pos:
            shadow_alpha = int(cloud.opacity * 80)
            shadow_surf = pygame.Surface((int(cloud.size * 2), int(cloud.size * 1.2)), pygame.SRCALPHA)
            
            # Stretched elliptical shadow
            pygame.draw.ellipse(shadow_surf, (0, 0, 0), 
                              (0, 0, int(cloud.size * 2), int(cloud.size * 1.2)))
            shadow_surf.set_alpha(shadow_alpha)
            
            shadow_x = adj_x + shadow_offset_x - cloud.size
            shadow_y = adj_y + shadow_offset_y - cloud.size * 0.6
            self.screen.blit(shadow_surf, (int(shadow_x), int(shadow_y)))
        
        # Get cached cloud surface
        cloud_surf = cloud.get_cached_surface(cloud_color, light_factor)
        
        # Draw the cached cloud with offset
        if cloud_surf:
            cloud_x = adj_x - cloud_surf.get_width() // 2
            cloud_y = adj_y - cloud_surf.get_height() // 2
            self.screen.blit(cloud_surf, (int(cloud_x), int(cloud_y)))
    
    def draw_weather_particles(self):
        for p in self.active_particles:
            p.draw(self.screen)
        # lightning unchanged
        if self.weather_data and 'thunderstorm' in self.weather_data['weather'][0]['main'].lower():
            self.lightning.draw(self.screen)
    
    def draw_info_overlay(self):
        """Draw weather and celestial information"""
        if not self.show_info:
            return
            
        font = pygame.font.Font(None, 32)
        small_font = pygame.font.Font(None, 24)
        
        # Always show location and time info using local time
        local_time = self.get_local_time()
        season = self.get_season().title()
        
        # Moon phase names with more detail
        phase_names = ["New Moon", "Waxing Crescent", "First Quarter", 
                      "Waxing Gibbous", "Full Moon", "Waning Gibbous",
                      "Last Quarter", "Waning Crescent"]
        phase_idx = int(self.moon_phase * 8) % 8
        moon_name = phase_names[phase_idx]
        
        # Add hemisphere indicator for season
        hemisphere = "N" if self.current_latitude >= 0 else "S"
        season_with_hemisphere = f"{season} ({hemisphere})"
        
        # Local time string
        time_str = local_time.strftime("%H:%M %Z")
        
        # Create text with shadow for readability
        location_prefix = "✈️ " if self.in_transition else "🌍 "
        text_lines = [
            f"{location_prefix}{self.current_location_name}",
        ]
        
        # Add weather info if available
        if self.weather_data:
            temp = self.weather_data['main']['temp']
            weather = self.weather_data['weather'][0]['main']
            # Show transition status if weather is changing
            if self.weather_transition.transition_progress < 1.0:
                progress = int(self.weather_transition.transition_progress * 100)
                text_lines.append(f"{temp:.1f}°C - {weather} (transitioning {progress}%)")
            else:
                text_lines.append(f"{temp:.1f}°C - {weather}")
        else:
            text_lines.append("Loading weather...")
        
        # Always show season and moon phase
        text_lines.extend([
            f"{season_with_hemisphere} - {moon_name}",
            f"{time_str}"
        ])
        
        y_offset = SCREEN_HEIGHT - 140
        for line in text_lines:
            # Shadow
            shadow = font.render(line, True, (0, 0, 0))
            text = font.render(line, True, (255, 255, 255))
            
            shadow_rect = shadow.get_rect(right=SCREEN_WIDTH - 22, top=y_offset + 2)
            text_rect = text.get_rect(right=SCREEN_WIDTH - 20, top=y_offset)
            
            self.screen.blit(shadow, shadow_rect)
            self.screen.blit(text, text_rect)
            y_offset += 35
        
        # Transition progress
        if self.in_transition:
            progress_text = f"Traveling... {int(self.transition_progress * 100)}%"
            shadow = small_font.render(progress_text, True, (0, 0, 0))
            text = small_font.render(progress_text, True, (100, 255, 100))
            
            shadow_rect = shadow.get_rect(right=SCREEN_WIDTH - 22, top=y_offset + 12)
            text_rect = text.get_rect(right=SCREEN_WIDTH - 20, top=y_offset + 10)
            
            self.screen.blit(shadow, shadow_rect)
            self.screen.blit(text, text_rect)
            y_offset += 30
        
        # City cycling countdown (if enabled and not transitioning)
        if self.cycle_cities and not self.in_transition:
            current_time = time.time()
            time_until_change = self.next_city_change - current_time
            if time_until_change > 0:
                countdown_text = f"Next city in: {int(time_until_change)}s"
                shadow = small_font.render(countdown_text, True, (0, 0, 0))
                text = small_font.render(countdown_text, True, (200, 200, 200))
                
                shadow_rect = shadow.get_rect(right=SCREEN_WIDTH - 22, top=y_offset + 12)
                text_rect = text.get_rect(right=SCREEN_WIDTH - 20, top=y_offset + 10)
                
                self.screen.blit(shadow, shadow_rect)
                self.screen.blit(text, text_rect)
        
        # Performance indicator and debug info
        if len(self.frame_times) > 30:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
            fps_color = (0, 255, 0) if fps > 25 else (255, 255, 0) if fps > 20 else (255, 0, 0)
            fps_text = font.render(f"FPS: {fps:.1f}", True, fps_color)
            self.screen.blit(fps_text, (20, 20))
            
            # Debug info
            debug_y = 50
            if hasattr(self, 'moon_phase'):
                # More detailed moon phase debug info
                phase_names = ["New", "Wax Cres", "1st Qtr", "Wax Gib", "Full", "Wan Gib", "3rd Qtr", "Wan Cres"]
                phase_idx = int(self.moon_phase * 8) % 8
                phase_name = phase_names[phase_idx]
                debug_text = small_font.render(f"Moon: {self.moon_phase:.3f} ({phase_name})", True, (150, 150, 150))
                self.screen.blit(debug_text, (20, debug_y))
                debug_y += 25
            
            # Particle count debug info
            if len(self.particles) > 0:
                particle_text = small_font.render(f"Particles: {len(self.particles)}", True, (150, 150, 150))
                self.screen.blit(particle_text, (20, debug_y))
    
    def draw(self):
        """Draw the complete sky scene with all elements"""
        # Draw base sky gradient
        self.draw_sky_gradient()
        
        # Draw stars and constellations
        self.draw_stars()
        
        # Draw shooting stars
        for shooting_star in self.shooting_stars:
            shooting_star.draw(self.screen)
        
        # Draw celestial objects
        self.draw_sun()
        self.draw_moon()
        
        # Draw clouds
        self.draw_clouds()
        
        # Draw weather particles (now with ceiling perspective)
        self.draw_weather_particles()
        
        # Draw info overlay
        self.draw_info_overlay()
    
    def run(self):
        """Main loop with time acceleration support"""
        dt = 0
        print("\nControls:")
        print("ESC - Exit")
        print("+ - Speed up time")
        print("- - Slow down time")
        print("0 - Reset time speed")
        print("I - Toggle info display")
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
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        self.time_acceleration = min(60, self.time_acceleration * 2)
                        print(f"Time acceleration: {self.time_acceleration}x")
                    elif event.key == pygame.K_MINUS:
                        self.time_acceleration = max(0.1, self.time_acceleration / 2)
                        print(f"Time acceleration: {self.time_acceleration}x")
                    elif event.key == pygame.K_0:
                        self.time_acceleration = 1.0
                        print("Time acceleration reset to 1x")
                    elif event.key == pygame.K_i:
                        self.show_info = not self.show_info
                        print(f"Info display: {'ON' if self.show_info else 'OFF'}")
                    elif event.key == pygame.K_n and self.cycle_cities:
                        # Manual city advance (only if not already transitioning)
                        if not self.in_transition:
                            self.city_index = (self.city_index + 1) % len(WORLD_CITIES)
                            next_city = WORLD_CITIES[self.city_index]
                            try:
                                lat, lon, tz, name = geocode_location(next_city)
                                self.location_change_queue.put((lat, lon, tz, name))
                                self.next_city_change = time.time() + self.cycle_interval + self.transition_duration
                                print(f"🌍 Manually switching to: {name}")
                            except Exception as e:
                                print(f"Failed to switch to {next_city}: {e}")
                        else:
                            print("⏳ Already transitioning, please wait...")
            
            self.update(dt)
            self.draw()
            pygame.display.flip()
            dt = self.clock.tick(FPS) / 1000.0
        
        pygame.quit()

if __name__ == "__main__":
    print("\n🌌 Enhanced Sky Ceiling Projector starting...")
    if args.cycle_cities:
        print(f"🌍 Demo Mode: Cycling through {len(WORLD_CITIES)} world cities every {args.cycle_interval}s")
        print(f"Starting location: {LOCATION_NAME} ({LATITUDE:.4f}, {LONGITUDE:.4f})")
    else:
        print(f"📍 Location: {LOCATION_NAME} ({LATITUDE:.4f}, {LONGITUDE:.4f})")
    print(f"🕐 Local time zone: {TIMEZONE}")
    print(f"🎨 Quality preset: {QUALITY_PRESET} (auto-adjusts for performance)")
    print(f"ℹ️  Info display: {'DISABLED' if args.no_info else 'ENABLED'}")
    print("🌤️ Weather: Open-Meteo forecast API (no key needed!)")
    print("⚡ Performance: Optimized cloud rendering with caching")
    print("🌙 Moon phases: Realistic lunar cycle with proper shadows")
    print("🎭 New Features:")
    print("   ✨ Smooth weather transitions (8s duration)")
    print("   ☔ Ceiling-perspective precipitation effects")
    print("   🌈 Extended color transition timing (12s)")
    print("   🎨 Cubic easing for ultra-smooth motion")
    print("   ⚡ Enhanced lightning effects for thunderstorms")
    
    simulator = SkySimulator()
    simulator.run()
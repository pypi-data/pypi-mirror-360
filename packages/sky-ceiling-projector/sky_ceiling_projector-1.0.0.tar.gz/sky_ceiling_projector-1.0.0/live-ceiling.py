#!/usr/bin/env python3
"""
Sky Ceiling Projector for Raspberry Pi Zero W
Projects a dynamic, weather-based sky simulation onto ceiling
Enhanced with constellations, aurora, shooting stars, and more!
"""

import pygame
import requests
import json
import math
import random
import time
from datetime import datetime, timezone
import numpy as np
from threading import Thread
import queue

# Configuration
SCREEN_WIDTH = 1920  # Adjust to your projector resolution
SCREEN_HEIGHT = 1080
FPS = 30
WEATHER_UPDATE_INTERVAL = 600  # Update weather every 10 minutes

# Weather API Configuration
# Using Open-Meteo - FREE, no API key needed!
LATITUDE = 51.5074  # Update with your latitude
LONGITUDE = -0.1278  # Update with your longitude
LOCATION_NAME = "London, UK"  # For display purposes only
TIMEZONE = "Europe/London"  # Your timezone (see: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)

# Constellation data (simplified star patterns)
CONSTELLATIONS = {
    "Orion": [(0.3, 0.2), (0.35, 0.25), (0.35, 0.35), (0.3, 0.4), 
              (0.25, 0.35), (0.25, 0.25), (0.3, 0.2), (0.45, 0.15), 
              (0.5, 0.1), (0.15, 0.45), (0.1, 0.5)],
    "Big Dipper": [(0.6, 0.3), (0.65, 0.32), (0.7, 0.3), (0.72, 0.25),
                   (0.7, 0.2), (0.65, 0.18), (0.6, 0.2)],
    "Cassiopeia": [(0.4, 0.6), (0.45, 0.58), (0.5, 0.62), (0.55, 0.58), (0.6, 0.6)],
}

class Star:
    def __init__(self, x, y, brightness, twinkle_speed, is_constellation=False):
        self.x = x
        self.y = y
        self.base_brightness = brightness
        self.brightness = brightness
        self.twinkle_speed = twinkle_speed
        self.twinkle_phase = random.uniform(0, 2 * math.pi)
        self.is_constellation = is_constellation
        
    def update(self, dt):
        self.twinkle_phase += self.twinkle_speed * dt
        twinkle_factor = 0.9 if self.is_constellation else 0.7
        self.brightness = self.base_brightness * (twinkle_factor + (1 - twinkle_factor) * math.sin(self.twinkle_phase))
        
    def draw(self, screen):
        if self.brightness > 0:
            size = max(1, int(self.brightness * 3))
            if self.is_constellation:
                size = max(2, int(self.brightness * 4))
            color = (int(255 * self.brightness), int(255 * self.brightness), int(240 * self.brightness))
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
        
        speed = random.uniform(500, 800)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
        self.trail = []
        self.lifetime = random.uniform(0.5, 1.5)
        self.age = 0
        self.max_trail_length = 20
        
    def update(self, dt):
        self.age += dt
        if self.age < self.lifetime:
            self.x += self.vx * dt
            self.y += self.vy * dt
            
            # Add to trail
            self.trail.append((self.x, self.y, self.age))
            
            # Limit trail length
            if len(self.trail) > self.max_trail_length:
                self.trail.pop(0)
            
            return True
        return False
    
    def draw(self, screen):
        for i, (x, y, age) in enumerate(self.trail):
            alpha = (1 - age / self.lifetime) * (i / len(self.trail))
            if alpha > 0:
                size = max(1, int(3 * alpha))
                color = (int(255 * alpha), int(240 * alpha), int(200 * alpha))
                pygame.draw.circle(screen, color, (int(x), int(y)), size)

class AuroraWave:
    def __init__(self, y_base):
        self.y_base = y_base
        self.phase = random.uniform(0, 2 * math.pi)
        self.amplitude = random.uniform(50, 100)
        self.frequency = random.uniform(0.002, 0.004)
        self.speed = random.uniform(0.5, 1.5)
        self.color_shift = random.uniform(0, 1)
        
    def update(self, dt):
        self.phase += self.speed * dt
        
    def get_y(self, x):
        return self.y_base + math.sin(x * self.frequency + self.phase) * self.amplitude

class Cloud:
    def __init__(self, x, y, size, speed, opacity):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.opacity = opacity
        self.blobs = []
        
        # Generate cloud shape with multiple overlapping circles
        for _ in range(random.randint(5, 8)):
            blob_x = random.uniform(-size/2, size/2)
            blob_y = random.uniform(-size/4, size/4)
            blob_size = random.uniform(size/3, size/1.5)
            self.blobs.append((blob_x, blob_y, blob_size))
    
    def update(self, dt):
        self.x += self.speed * dt
        if self.x > SCREEN_WIDTH + self.size:
            self.x = -self.size
            self.y = random.uniform(0, SCREEN_HEIGHT * 0.7)
    
    def draw(self, screen, cloud_color):
        for blob_x, blob_y, blob_size in self.blobs:
            color = (*cloud_color, int(self.opacity * 255))
            s = pygame.Surface((blob_size * 2, blob_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (int(blob_size), int(blob_size)), int(blob_size))
            screen.blit(s, (int(self.x + blob_x - blob_size), int(self.y + blob_y - blob_size)))

class Particle:
    def __init__(self, x, y, particle_type):
        self.x = x
        self.y = y
        self.type = particle_type
        
        if particle_type == "rain":
            self.vy = random.uniform(300, 500)
            self.vx = random.uniform(-50, 50)
            self.length = random.uniform(10, 20)
        elif particle_type == "snow":
            self.vy = random.uniform(50, 150)
            self.vx = random.uniform(-30, 30)
            self.size = random.uniform(2, 5)
            self.wobble = random.uniform(0, 2 * math.pi)
    
    def update(self, dt):
        self.y += self.vy * dt
        self.x += self.vx * dt
        
        if self.type == "snow":
            self.wobble += dt * 3
            self.x += math.sin(self.wobble) * 20 * dt
        
        if self.y > SCREEN_HEIGHT:
            self.y = -20
            self.x = random.uniform(0, SCREEN_WIDTH)

    def draw(self, screen):
        if self.type == "rain":
            color = (100, 100, 200, 100)
            end_y = self.y + self.length
            pygame.draw.line(screen, color, (int(self.x), int(self.y)), 
                           (int(self.x - self.vx * 0.05), int(end_y)), 1)
        elif self.type == "snow":
            color = (255, 255, 255, 200)
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(self.size))

class SkySimulator:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Sky Ceiling Projector")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Weather data
        self.weather_queue = queue.Queue()
        self.weather_data = None
        self.last_weather_update = 0
        
        # Sky elements
        self.stars = []
        self.constellation_stars = []
        self.constellation_lines = []
        self.clouds = []
        self.particles = []
        self.shooting_stars = []
        self.aurora_waves = []
        
        # Time-based colors
        self.current_sky_color = (0, 0, 0)
        self.target_sky_color = (0, 0, 0)
        self.color_transition = 0
        
        # Moon phase
        self.moon_phase = self.calculate_moon_phase()
        
        # Shooting star timer
        self.next_shooting_star = time.time() + random.uniform(30, 120)
        
        # Aurora settings
        self.aurora_active = False
        self.aurora_intensity = 0
        
        # Initialize sky elements
        self.create_stars()
        self.create_constellations()
        self.create_aurora()
        
        # Start weather update thread
        self.weather_thread = Thread(target=self.weather_updater, daemon=True)
        self.weather_thread.start()
    
    def calculate_moon_phase(self):
        """Calculate current moon phase (0 = new moon, 0.5 = full moon, 1 = new moon)"""
        # Simplified moon phase calculation
        known_new_moon = datetime(2000, 1, 6)
        moon_cycle = 29.53059  # days
        
        current_time = datetime.now()
        days_since = (current_time - known_new_moon).days
        phase = (days_since % moon_cycle) / moon_cycle
        
        return phase
    
    def create_stars(self):
        """Create a realistic starfield"""
        # Bright stars
        for _ in range(50):
            x = random.uniform(0, SCREEN_WIDTH)
            y = random.uniform(0, SCREEN_HEIGHT)
            brightness = random.uniform(0.7, 1.0)
            twinkle = random.uniform(1, 3)
            self.stars.append(Star(x, y, brightness, twinkle))
        
        # Dim stars
        for _ in range(200):
            x = random.uniform(0, SCREEN_WIDTH)
            y = random.uniform(0, SCREEN_HEIGHT)
            brightness = random.uniform(0.3, 0.6)
            twinkle = random.uniform(0.5, 2)
            self.stars.append(Star(x, y, brightness, twinkle))
    
    def create_constellations(self):
        """Create constellation patterns"""
        for name, pattern in CONSTELLATIONS.items():
            # Random position and rotation for constellation
            base_x = random.uniform(200, SCREEN_WIDTH - 200)
            base_y = random.uniform(100, SCREEN_HEIGHT - 100)
            scale = random.uniform(200, 400)
            rotation = random.uniform(0, 2 * math.pi)
            
            constellation_points = []
            for px, py in pattern:
                # Rotate and position
                x = px - 0.5
                y = py - 0.5
                rx = x * math.cos(rotation) - y * math.sin(rotation)
                ry = x * math.sin(rotation) + y * math.cos(rotation)
                
                final_x = base_x + rx * scale
                final_y = base_y + ry * scale
                
                # Create constellation star
                star = Star(final_x, final_y, random.uniform(0.8, 1.0), 
                           random.uniform(0.5, 1.5), is_constellation=True)
                self.constellation_stars.append(star)
                constellation_points.append((final_x, final_y))
            
            # Store lines for this constellation
            self.constellation_lines.append(constellation_points)
    
    def create_aurora(self):
        """Create aurora borealis waves"""
        # Create multiple wave layers
        for i in range(5):
            y_base = SCREEN_HEIGHT * 0.1 + i * 30
            self.aurora_waves.append(AuroraWave(y_base))
    
    def should_show_aurora(self):
        """Determine if aurora should be visible based on location and conditions"""
        # More likely at higher latitudes
        aurora_chance = max(0, (abs(LATITUDE) - 45) / 45)
        
        # More likely in winter months
        month = datetime.now().month
        if month in [11, 12, 1, 2]:
            aurora_chance += 0.3
        
        # More likely during clear nights
        if self.weather_data and self.weather_data['clouds']['all'] < 30:
            aurora_chance += 0.2
        
        # Random factor
        return random.random() < min(aurora_chance * 0.1, 0.3)
    
    def weather_updater(self):
        """Background thread to update weather data using Open-Meteo (FREE!)"""
        while self.running:
            try:
                # Open-Meteo API - completely free, no key needed!
                url = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current=temperature_2m,weather_code,cloud_cover&timezone={TIMEZONE}"
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
                        'main': {'temp': data['current']['temperature_2m']}
                    }
                    
                    self.weather_queue.put(formatted_data)
                    
            except Exception as e:
                print(f"Weather update error: {e}")
            
            time.sleep(WEATHER_UPDATE_INTERVAL)
    
    def get_sky_color(self, hour, weather_condition, season):
        """Calculate sky color based on time of day, weather, and season"""
        # Seasonal adjustments
        seasonal_tint = {
            "winter": (0.9, 0.9, 1.0),    # Cooler, bluer
            "spring": (1.0, 1.0, 0.95),    # Slightly warm
            "summer": (1.0, 0.95, 0.9),    # Warmer
            "autumn": (1.0, 0.9, 0.85)     # Golden
        }
        
        # Base sky colors for different times
        colors = {
            0: (10, 10, 30),      # Midnight
            5: (30, 30, 60),      # Pre-dawn
            6: (100, 60, 120),    # Dawn
            7: (255, 150, 100),   # Sunrise
            8: (135, 206, 235),   # Morning
            12: (135, 206, 255),  # Noon
            17: (255, 180, 100),  # Late afternoon
            18: (255, 120, 80),   # Sunset
            19: (120, 60, 100),   # Dusk
            20: (40, 40, 80),     # Evening
            22: (20, 20, 40),     # Night
        }
        
        # Find surrounding hours
        hours = sorted(colors.keys())
        prev_hour = max([h for h in hours if h <= hour], default=0)
        next_hour = min([h for h in hours if h > hour], default=24)
        
        if next_hour == 24:
            next_hour = 0
        
        # Interpolate between colors
        if prev_hour == next_hour:
            base_color = colors[prev_hour]
        else:
            t = (hour - prev_hour) / ((next_hour - prev_hour) if next_hour > prev_hour else (24 - prev_hour + next_hour))
            prev_color = colors[prev_hour]
            next_color = colors[next_hour]
            base_color = tuple(int(prev_color[i] + (next_color[i] - prev_color[i]) * t) for i in range(3))
        
        # Apply seasonal tint
        tint = seasonal_tint[season]
        base_color = tuple(int(base_color[i] * tint[i]) for i in range(3))
        
        # Modify based on weather
        if "cloud" in weather_condition:
            base_color = tuple(int(c * 0.7) for c in base_color)
        elif "rain" in weather_condition or "storm" in weather_condition:
            base_color = tuple(int(c * 0.5) for c in base_color)
        
        return base_color
    
    def get_season(self):
        """Get current season based on month"""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "autumn"
    
    def update_weather_effects(self):
        """Update clouds and particles based on weather"""
        if not self.weather_data:
            return
        
        weather = self.weather_data['weather'][0]['main'].lower()
        clouds = self.weather_data['clouds']['all'] / 100.0  # 0-1 scale
        
        # Update clouds
        target_cloud_count = int(clouds * 15)
        
        while len(self.clouds) < target_cloud_count:
            x = random.uniform(-200, SCREEN_WIDTH)
            y = random.uniform(0, SCREEN_HEIGHT * 0.7)
            size = random.uniform(150, 300)
            speed = random.uniform(20, 50)
            opacity = random.uniform(0.3, 0.7)
            self.clouds.append(Cloud(x, y, size, speed, opacity))
        
        while len(self.clouds) > target_cloud_count:
            self.clouds.pop()
        
        # Update particles
        if "rain" in weather or "drizzle" in weather:
            target_particles = 200
            particle_type = "rain"
        elif "snow" in weather:
            target_particles = 150
            particle_type = "snow"
        else:
            target_particles = 0
            particle_type = None
        
        if particle_type:
            while len(self.particles) < target_particles:
                x = random.uniform(0, SCREEN_WIDTH)
                y = random.uniform(-20, SCREEN_HEIGHT)
                self.particles.append(Particle(x, y, particle_type))
        else:
            self.particles.clear()
    
    def update(self, dt):
        """Update all sky elements"""
        # Check for new weather data
        try:
            self.weather_data = self.weather_queue.get_nowait()
            self.update_weather_effects()
        except queue.Empty:
            pass
        
        # Update sky color
        current_time = datetime.now()
        hour = current_time.hour + current_time.minute / 60.0
        season = self.get_season()
        
        weather_condition = ""
        if self.weather_data:
            weather_condition = self.weather_data['weather'][0]['main'].lower()
        
        self.target_sky_color = self.get_sky_color(hour, weather_condition, season)
        
        # Smooth color transition
        self.color_transition = min(1, self.color_transition + dt * 0.1)
        self.current_sky_color = tuple(
            int(self.current_sky_color[i] + (self.target_sky_color[i] - self.current_sky_color[i]) * self.color_transition)
            for i in range(3)
        )
        
        # Update moon phase
        if random.random() < 0.001:  # Occasionally update
            self.moon_phase = self.calculate_moon_phase()
        
        # Update aurora
        if hour < 6 or hour > 20:  # Night time
            if not self.aurora_active and random.random() < 0.0001:
                if self.should_show_aurora():
                    self.aurora_active = True
                    self.aurora_intensity = 0
            
            if self.aurora_active:
                self.aurora_intensity = min(1, self.aurora_intensity + dt * 0.1)
                if random.random() < 0.00001:
                    self.aurora_active = False
        else:
            self.aurora_active = False
            self.aurora_intensity = max(0, self.aurora_intensity - dt * 0.2)
        
        for wave in self.aurora_waves:
            wave.update(dt)
        
        # Update stars (only visible at night)
        star_visibility = 0
        if hour < 6 or hour > 20:
            star_visibility = 1
        elif hour < 7 or hour > 19:
            star_visibility = 0.5
        
        # Reduce star visibility if moon is bright
        if self.moon_phase > 0.25 and self.moon_phase < 0.75:
            moon_brightness = 1 - abs(self.moon_phase - 0.5) * 2
            star_visibility *= (1 - moon_brightness * 0.5)
        
        for star in self.stars + self.constellation_stars:
            star.update(dt)
            star.brightness = min(star.brightness, star.base_brightness * star_visibility)
        
        # Update clouds
        for cloud in self.clouds:
            cloud.update(dt)
        
        # Update particles
        for particle in self.particles:
            particle.update(dt)
        
        # Update shooting stars
        self.shooting_stars = [s for s in self.shooting_stars if s.update(dt)]
        
        # Spawn new shooting star
        if time.time() > self.next_shooting_star and (hour < 6 or hour > 20):
            self.shooting_stars.append(ShootingStar())
            self.next_shooting_star = time.time() + random.uniform(30, 180)
    
    def draw_moon(self, hour):
        """Draw the moon with accurate phase"""
        if not (hour < 6 or hour > 18):
            return
        
        # Moon position (opposite of sun)
        moon_angle = ((hour + 12) % 24 - 18) / 12 * math.pi
        moon_x = SCREEN_WIDTH * 0.5 + SCREEN_WIDTH * 0.4 * math.cos(moon_angle)
        moon_y = SCREEN_HEIGHT * 0.2 + SCREEN_HEIGHT * 0.3 * abs(math.sin(moon_angle))
        
        radius = 40
        
        # Draw moon base
        pygame.draw.circle(self.screen, (250, 250, 230), (int(moon_x), int(moon_y)), radius)
        
        # Draw moon phase shadow
        if self.moon_phase != 0.5:  # Not full moon
            shadow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            
            if self.moon_phase < 0.5:
                # Waxing moon
                width = radius * 2 * (0.5 - self.moon_phase) * 2
                shadow_rect = pygame.Rect(0, 0, width, radius * 2)
                pygame.draw.ellipse(shadow_surface, (30, 30, 60, 255), shadow_rect)
            else:
                # Waning moon
                width = radius * 2 * (self.moon_phase - 0.5) * 2
                shadow_rect = pygame.Rect(radius * 2 - width, 0, width, radius * 2)
                pygame.draw.ellipse(shadow_surface, (30, 30, 60, 255), shadow_rect)
            
            self.screen.blit(shadow_surface, (int(moon_x - radius), int(moon_y - radius)))
        
        # Moon craters
        for _ in range(5):
            crater_x = moon_x + random.uniform(-radius * 0.6, radius * 0.6)
            crater_y = moon_y + random.uniform(-radius * 0.6, radius * 0.6)
            crater_r = random.uniform(3, 8)
            pygame.draw.circle(self.screen, (230, 230, 210), 
                             (int(crater_x), int(crater_y)), int(crater_r))
    
    def draw_aurora(self):
        """Draw aurora borealis effect"""
        if self.aurora_intensity <= 0:
            return
        
        aurora_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        for i, wave in enumerate(self.aurora_waves):
            # Create gradient colors
            colors = [
                (0, 255, 100),    # Green
                (0, 255, 200),    # Cyan
                (150, 0, 255),    # Purple
                (255, 0, 150),    # Pink
            ]
            
            color_idx = i % len(colors)
            base_color = colors[color_idx]
            
            # Draw vertical bands
            for x in range(0, SCREEN_WIDTH, 5):
                y = wave.get_y(x)
                height = 100 + math.sin(x * 0.01 + wave.phase) * 50
                
                for h in range(int(height)):
                    alpha = (1 - h / height) * self.aurora_intensity * 0.3
                    color = (*base_color, int(alpha * 255))
                    
                    pygame.draw.line(aurora_surface, color,
                                   (x, int(y + h)), (x + 5, int(y + h)))
        
        self.screen.blit(aurora_surface, (0, 0))
    
    def draw(self):
        """Draw the complete sky scene"""
        # Clear screen with sky color
        self.screen.fill(self.current_sky_color)
        
        # Draw stars
        for star in self.stars:
            star.draw(self.screen)
        
        # Draw constellations
        for star in self.constellation_stars:
            star.draw(self.screen)
        
        # Draw constellation lines (very faint)
        if self.constellation_stars[0].brightness > 0.5:
            for constellation in self.constellation_lines:
                for i in range(len(constellation) - 1):
                    alpha = int(50 * self.constellation_stars[0].brightness)
                    pygame.draw.line(self.screen, (alpha, alpha, alpha),
                                   constellation[i], constellation[i + 1], 1)
        
        # Draw shooting stars
        for shooting_star in self.shooting_stars:
            shooting_star.draw(self.screen)
        
        # Draw aurora
        self.draw_aurora()
        
        # Draw sun/moon
        current_time = datetime.now()
        hour = current_time.hour + current_time.minute / 60.0
        
        if 6 < hour < 18:  # Sun
            sun_angle = (hour - 6) / 12 * math.pi
            sun_x = SCREEN_WIDTH * 0.2 + SCREEN_WIDTH * 0.6 * (hour - 6) / 12
            sun_y = SCREEN_HEIGHT * 0.8 - SCREEN_HEIGHT * 0.6 * math.sin(sun_angle)
            
            # Sun with seasonal color
            season = self.get_season()
            if season == "winter":
                sun_color = (255, 220, 180)
            elif season == "summer":
                sun_color = (255, 240, 100)
            else:
                sun_color = (255, 230, 120)
            
            pygame.draw.circle(self.screen, sun_color, (int(sun_x), int(sun_y)), 60)
            
            # Sun glow
            for i in range(3):
                glow_alpha = 30 - i * 10
                glow_color = tuple(int(c * 0.8) for c in sun_color)
                pygame.draw.circle(self.screen, glow_color, (int(sun_x), int(sun_y)), 
                                 80 + i * 20, 2)
        else:
            # Draw moon
            self.draw_moon(hour)
        
        # Draw clouds
        cloud_color = (200, 200, 200) if hour > 6 and hour < 20 else (100, 100, 100)
        for cloud in self.clouds:
            cloud.draw(self.screen, cloud_color)
        
        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Draw info overlay (optional)
        if self.weather_data:
            font = pygame.font.Font(None, 36)
            temp = self.weather_data['main']['temp']
            weather = self.weather_data['weather'][0]['main']
            season = self.get_season().title()
            
            # Moon phase names
            phase_names = ["New Moon", "Waxing Crescent", "First Quarter", 
                          "Waxing Gibbous", "Full Moon", "Waning Gibbous",
                          "Last Quarter", "Waning Crescent"]
            phase_idx = int(self.moon_phase * 8) % 8
            moon_name = phase_names[phase_idx]
            
            text = font.render(f"{LOCATION_NAME}: {temp:.1f}°C - {weather} - {season} - {moon_name}", 
                             True, (255, 255, 255))
            text_rect = text.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
            self.screen.blit(text, text_rect)
    
    def run(self):
        """Main game loop"""
        dt = 0
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
            
            self.update(dt)
            self.draw()
            pygame.display.flip()
            dt = self.clock.tick(FPS) / 1000.0
        
        pygame.quit()

if __name__ == "__main__":
    print("Sky Ceiling Projector starting...")
    print(f"Location: {LOCATION_NAME} ({LATITUDE}, {LONGITUDE})")
    print("Using Open-Meteo FREE weather API - no key needed!")
    
    simulator = SkySimulator()
    simulator.run()
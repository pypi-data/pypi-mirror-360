#!/usr/bin/env python3
"""
Command-line interface for Sky Ceiling Projector.
"""

import argparse
import sys
import os
from .projector import SkySimulator, geocode_location


def create_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Sky Ceiling Projector - Realistic sky simulation with weather effects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sky-projector --location "Tampa, FL"
  sky-projector --location "Berlin, Germany" --preset quality
  sky-projector --cycle-cities --cycle-interval 180
  sky-projector --location "Sydney, Australia" --no-info

Features:
  • Real-time weather integration with detailed cloud formations
  • Enhanced starfield with variable stars, giants, and supergiants  
  • Accurate moon phases with surface detail and craters
  • Visible planets (Venus, Mars, Jupiter, Saturn)
  • Milky Way galaxy visualization with star clouds
  • Shooting stars, satellites, and bright flares
  • Location-aware sky simulation with timezone support
  • Debug mode for testing all weather conditions

Controls:
  ESC     - Exit
  I       - Toggle info display
  D       - Toggle debug mode (cycles through weather)
  SPACE   - Manual lightning trigger (during thunderstorms)
  R       - Regenerate celestial objects
  N       - Next city (in demo mode)
        """
    )
    
    parser.add_argument(
        "--location", "-l",
        help="City[, State/ISO-country]. Example: 'Tampa, FL' or 'Berlin, Germany'"
    )
    
    parser.add_argument(
        "--preset", 
        choices=["performance", "balanced", "quality"],
        default="balanced", 
        help="Graphics quality preset (default: balanced)"
    )
    
    parser.add_argument(
        "--cycle-cities", 
        action="store_true",
        help="Demo mode: cycle through major world cities"
    )
    
    parser.add_argument(
        "--cycle-interval", 
        type=int, 
        default=300,
        help="Seconds between city changes in demo mode (default: 300)"
    )
    
    parser.add_argument(
        "--no-info", 
        action="store_true",
        help="Disable information overlay display"
    )
    
    parser.add_argument(
        "--fullscreen", 
        action="store_true", 
        default=True,
        help="Run in fullscreen mode (default: True)"
    )
    
    parser.add_argument(
        "--windowed", 
        action="store_true",
        help="Run in windowed mode instead of fullscreen"
    )
    
    parser.add_argument(
        "--resolution", 
        default="1920x1080",
        help="Screen resolution (default: 1920x1080)"
    )
    
    parser.add_argument(
        "--fps", 
        type=int, 
        default=30,
        help="Target frame rate (default: 30)"
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"Sky Ceiling Projector {get_version()}"
    )
    
    return parser


def get_version():
    """Get the package version."""
    try:
        from . import __version__
        return __version__
    except ImportError:
        return "unknown"


def validate_location(location):
    """Validate that a location can be geocoded."""
    try:
        lat, lon, tz, name = geocode_location(location)
        print(f"✅ Location resolved: {name} ({lat:.4f}, {lon:.4f}, {tz})")
        return lat, lon, tz, name
    except Exception as e:
        print(f"❌ Failed to resolve location '{location}': {e}")
        print("\nTry formats like:")
        print("  • 'New York, NY'")
        print("  • 'London, UK'") 
        print("  • 'Sydney, Australia'")
        print("  • 'Berlin, Germany'")
        sys.exit(1)


def parse_resolution(resolution_str):
    """Parse resolution string like '1920x1080' into (width, height)."""
    try:
        width, height = map(int, resolution_str.lower().split('x'))
        return width, height
    except ValueError:
        print(f"❌ Invalid resolution format: {resolution_str}")
        print("Use format like: 1920x1080")
        sys.exit(1)


def check_dependencies():
    """Check if all required dependencies are available."""
    missing_deps = []
    
    try:
        import pygame
    except ImportError:
        missing_deps.append("pygame")
    
    try:
        import requests
    except ImportError:
        missing_deps.append("requests")
    
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
    
    try:
        import pytz
    except ImportError:
        missing_deps.append("pytz")
    
    if missing_deps:
        print("❌ Missing required dependencies:")
        for dep in missing_deps:
            print(f"  • {dep}")
        print("\nInstall with: pip install", " ".join(missing_deps))
        sys.exit(1)


def main():
    """Main entry point for the command-line interface."""
    
    # Check dependencies first
    check_dependencies()
    
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle windowed vs fullscreen
    if args.windowed:
        args.fullscreen = False
    
    # Parse resolution
    screen_width, screen_height = parse_resolution(args.resolution)
    
    # Validate location requirements
    if not args.cycle_cities and not args.location:
        parser.error("Either --location is required or use --cycle-cities for demo mode")
    
    # World cities for demo mode
    WORLD_CITIES = [
        "Paris, France",
        "Brisbane, Australia", 
        "New York, NY, USA",
        "London, UK",
        "Tokyo, Japan",
        "Sydney, Australia",
        "Cairo, Egypt",
        "Mumbai, India",
        "São Paulo, Brazil",
        "Reykjavik, Iceland",
        "Singapore",
        "Cape Town, South Africa",
        "Moscow, Russia",
        "Los Angeles, CA, USA",
        "Dubai, UAE",
        "Bangkok, Thailand",
        "Mexico City, Mexico",
        "Vancouver, Canada",
    ]
    
    # Set up initial location
    if args.cycle_cities:
        print("🌍 Demo Mode: Cycling through world cities...")
        initial_city = WORLD_CITIES[0]
        latitude, longitude, timezone, location_name = validate_location(initial_city)
    else:
        latitude, longitude, timezone, location_name = validate_location(args.location)
    
    print(f"\n🌌 Sky Ceiling Projector v{get_version()}")
    print(f"📍 Location: {location_name}")
    print(f"🎨 Quality preset: {args.preset}")
    print(f"🖥️  Resolution: {screen_width}x{screen_height}")
    print(f"🎯 Frame rate: {args.fps} FPS")
    print(f"🖼️  Display mode: {'Fullscreen' if args.fullscreen else 'Windowed'}")
    
    if args.cycle_cities:
        print(f"🌍 City cycling every {args.cycle_interval}s")
    
    print("\n✨ Enhanced Features:")
    print("   🌩️ Reliable weather effects")
    print("   ☁️ Detailed realistic clouds with shadows")
    print("   🌙 Realistic moon with craters and phases")
    print("   ⭐ Vibrant starfield with giants and variables")
    print("   🌌 Milky Way galaxy visualization")
    print("   🪐 Visible planets and celestial objects")
    print("   ☄️ Shooting stars and satellite tracking")
    
    try:
        # Import here to avoid early pygame initialization
        from .projector import SkySimulator
        
        # Create and run the simulator with parsed arguments
        simulator = SkySimulator(
            latitude=latitude,
            longitude=longitude, 
            timezone=timezone,
            location_name=location_name,
            screen_width=screen_width,
            screen_height=screen_height,
            fps=args.fps,
            preset=args.preset,
            cycle_cities=args.cycle_cities,
            cycle_interval=args.cycle_interval,
            show_info=not args.no_info,
            fullscreen=args.fullscreen,
            world_cities=WORLD_CITIES,
        )
        
        simulator.run()
        
    except KeyboardInterrupt:
        print("\n👋 Sky projector stopped by user")
    except Exception as e:
        print(f"\n❌ Error running sky projector: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
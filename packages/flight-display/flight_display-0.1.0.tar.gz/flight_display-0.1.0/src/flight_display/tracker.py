#!/usr/bin/env python3
"""
Aircraft Tracker - Airport Departure Board Style Display
Fetches nearby aircraft data and displays it like an airport departure board
"""

import requests
import json
import time
import math
import sys
from datetime import datetime
from typing import List, Dict, Optional
from tabulate import tabulate
from colorama import Fore, Back, Style, init
import re

# Initialize colorama for cross-platform colored output
init(autoreset=True)


class AircraftTracker:
    def __init__(
        self,
        lat: float,
        lon: float,
        radius_km: float = 50,
        fetch_online_codes: bool = True,
    ):
        """
        Initialize the aircraft tracker

        Args:
            lat: Your latitude
            lon: Your longitude
            radius_km: Search radius in kilometers
            fetch_online_codes: Whether to fetch airline codes from online sources
        """
        self.lat = lat
        self.lon = lon
        self.radius_km = radius_km
        self.base_url = "https://adsbexchange.com/api/aircraft/json"
        self.location_name = "Unknown Location"  # Will be set later

        # Cache for aircraft operator data to avoid repeated API calls
        self.operator_cache = {}

        # Initialize empty airline codes dictionary - will be populated from online sources
        self.airline_codes = {}

        # Fetch airline codes from online sources (only if requested)
        if fetch_online_codes:
            self.update_airline_database_online()

    def haversine_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth's radius in kilometers

        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        return R * c

    def fetch_aircraft_data(self) -> List[Dict]:
        """Fetch aircraft data from OpenSky Network with enhanced error handling"""
        max_retries = 3
        base_delay = (
            10  # Base delay in seconds - increased for better rate limit handling
        )

        for attempt in range(max_retries):
            try:
                # Use OpenSky Network API (free, no key required)
                opensky_url = f"https://opensky-network.org/api/states/all"

                print(
                    f"🌐 Fetching aircraft data (attempt {attempt + 1}/{max_retries})..."
                )
                response = requests.get(opensky_url, timeout=15)

                # Handle rate limiting (429 error)
                if response.status_code == 429:
                    retry_after = response.headers.get(
                        "Retry-After", base_delay * (2**attempt)
                    )
                    try:
                        wait_time = int(retry_after)
                    except (ValueError, TypeError):
                        wait_time = base_delay * (2**attempt)  # Exponential backoff

                    if attempt < max_retries - 1:
                        print(
                            f"⏳ API rate limit hit (HTTP 429). Waiting {wait_time} seconds before retry..."
                        )
                        print(
                            "   📊 OpenSky API has usage limits - this is normal during peak times"
                        )
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"❌ Rate limit exceeded after {max_retries} attempts.")
                        print(
                            f"💡 Please wait {wait_time} seconds before trying again."
                        )
                        print(
                            "   🌐 The OpenSky API is free but has rate limits to ensure fair usage"
                        )
                        return []

                response.raise_for_status()
                data = response.json()

                if not data or "states" not in data:
                    print("⚠️ No aircraft data received from API")
                    return []

                aircraft_list = []
                current_time = int(time.time())

                for state in data["states"]:
                    if not state or len(state) < 17:
                        continue

                    # OpenSky API format: [icao24, callsign, origin_country, time_position,
                    # last_contact, longitude, latitude, baro_altitude, on_ground, velocity,
                    # true_track, vertical_rate, sensors, geo_altitude, squawk, spi, position_source]

                    icao24 = state[0]
                    callsign = state[1]
                    latitude = state[6]
                    longitude = state[5]
                    altitude = state[7]  # barometric altitude in meters
                    velocity = state[9]  # velocity in m/s
                    track = state[10]  # true track in degrees
                    vertical_rate = state[11]  # vertical rate in m/s

                    # Skip if missing position data
                    if not latitude or not longitude:
                        continue

                    # Calculate distance from your location
                    distance = self.haversine_distance(
                        self.lat, self.lon, latitude, longitude
                    )

                    # Filter by radius
                    if distance <= self.radius_km:
                        callsign_clean = (
                            callsign.strip() if callsign else f"ICAO{icao24.upper()}"
                        )

                        # Get operator information
                        operator_info = "Unknown"
                        aircraft_type_short = "UNK"
                        registration = "Unknown"

                        # First try to get operator from callsign (faster)
                        if callsign:
                            operator_info = self.get_operator_from_callsign(
                                callsign_clean
                            )

                        # For unknown operators, try to fetch detailed info (slower)
                        if operator_info == "Unknown":
                            try:
                                details = self.fetch_aircraft_details(icao24)
                                operator_info = details.get("operator", "Unknown")
                                aircraft_type_short = self.get_aircraft_type_short(
                                    details.get("aircraft_type", "Unknown")
                                )
                                registration = details.get("registration", "Unknown")
                            except:
                                pass

                        aircraft = {
                            "icao24": icao24,
                            "callsign": callsign_clean,
                            "operator": operator_info,
                            "registration": registration,
                            "aircraft_type": aircraft_type_short,
                            "latitude": latitude,
                            "longitude": longitude,
                            "altitude": int(altitude) if altitude else 0,
                            "velocity": (
                                int(velocity * 1.94384) if velocity else 0
                            ),  # Convert m/s to knots
                            "track": int(track) if track else 0,
                            "vertical_rate": (
                                int(vertical_rate * 196.85) if vertical_rate else 0
                            ),  # Convert m/s to ft/min
                            "distance": distance,
                        }
                        aircraft_list.append(aircraft)

                # Sort by distance (closest first)
                aircraft_list.sort(key=lambda x: x["distance"])
                print(
                    f"✅ Successfully fetched data for {len(aircraft_list)} nearby aircraft"
                )
                return aircraft_list

            except requests.exceptions.RequestException as e:
                if "429" in str(e):
                    wait_time = base_delay * (2**attempt)
                    if attempt < max_retries - 1:
                        print(
                            f"⏳ Rate limit detected. Waiting {wait_time} seconds before retry..."
                        )
                        print(
                            "   📊 OpenSky API has usage limits - this is normal during peak times"
                        )
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"❌ Rate limit exceeded after all retries.")
                        print(f"💡 Please wait a few minutes before trying again.")
                        return []
                else:
                    print(f"⚠️ Network error (attempt {attempt + 1}/{max_retries}): {e}")
                    if attempt == max_retries - 1:
                        print("❌ All retry attempts failed due to network errors")
                        return []
                    time.sleep(base_delay)
                    continue

            except Exception as e:
                print(f"⚠️ Unexpected error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    print("❌ All retry attempts failed due to unexpected errors")
                    return []
                time.sleep(base_delay)
                continue

        # If we get here, all retries failed
        print("❌ Failed to fetch aircraft data after all retry attempts")
        print(
            "💡 The OpenSky API may be experiencing high load. Try again in a few minutes."
        )
        return []

    def format_departure_board(self, aircraft_list: List[Dict]) -> str:
        """Format aircraft data as departure board display with tabulate"""
        if not aircraft_list:
            return f"{Fore.RED}NO AIRCRAFT IN RANGE{Style.RESET_ALL}"

        # Prepare data for tabulate
        table_data = []
        current_time = datetime.now().strftime("%H:%M:%S")

        for aircraft in aircraft_list[
            :12
        ]:  # Show top 12 aircraft (reduced to fit operator info)
            callsign = aircraft["callsign"][:10]  # Limit callsign length
            icao24 = aircraft["icao24"].upper()

            # Format operator name (truncate if too long)
            operator = aircraft.get("operator", "Unknown")
            if len(operator) > 18:
                operator = operator[:15] + "..."

            # Format aircraft type
            aircraft_type = aircraft.get("aircraft_type", "UNK")

            # Format altitude with color coding
            if aircraft["altitude"] > 0:
                if aircraft["altitude"] > 30000:
                    altitude = (
                        f"{Fore.CYAN}{aircraft['altitude']:,} ft{Style.RESET_ALL}"
                    )
                elif aircraft["altitude"] > 10000:
                    altitude = (
                        f"{Fore.YELLOW}{aircraft['altitude']:,} ft{Style.RESET_ALL}"
                    )
                else:
                    altitude = (
                        f"{Fore.GREEN}{aircraft['altitude']:,} ft{Style.RESET_ALL}"
                    )
            else:
                altitude = f"{Fore.RED}GROUND{Style.RESET_ALL}"

            # Format speed
            speed = f"{aircraft['velocity']} kt" if aircraft["velocity"] > 0 else "--"

            # Format track/heading
            track = f"{aircraft['track']:03d}°" if aircraft["track"] > 0 else "---"

            # Vertical speed with arrows and colors
            vs = aircraft["vertical_rate"]
            if vs > 500:
                vs_str = f"{Fore.GREEN}↑{abs(vs):4d}{Style.RESET_ALL}"
            elif vs < -500:
                vs_str = f"{Fore.RED}↓{abs(vs):4d}{Style.RESET_ALL}"
            elif vs > 100:
                vs_str = f"{Fore.LIGHTGREEN_EX}↗{abs(vs):4d}{Style.RESET_ALL}"
            elif vs < -100:
                vs_str = f"{Fore.LIGHTRED_EX}↘{abs(vs):4d}{Style.RESET_ALL}"
            else:
                vs_str = f"{Fore.WHITE}═══{Style.RESET_ALL}"

            # Format distance with color coding
            dist = aircraft["distance"]
            if dist < 10:
                distance = f"{Fore.RED}{dist:.1f} km{Style.RESET_ALL}"
            elif dist < 25:
                distance = f"{Fore.YELLOW}{dist:.1f} km{Style.RESET_ALL}"
            else:
                distance = f"{Fore.GREEN}{dist:.1f} km{Style.RESET_ALL}"

            table_data.append(
                [
                    callsign,
                    operator,
                    aircraft_type,
                    altitude,
                    speed,
                    track,
                    vs_str,
                    distance,
                ]
            )

        # Create header
        headers = [
            f"{Fore.WHITE}{Style.BRIGHT}CALLSIGN{Style.RESET_ALL}",
            f"{Fore.WHITE}{Style.BRIGHT}OPERATOR{Style.RESET_ALL}",
            f"{Fore.WHITE}{Style.BRIGHT}TYPE{Style.RESET_ALL}",
            f"{Fore.WHITE}{Style.BRIGHT}ALTITUDE{Style.RESET_ALL}",
            f"{Fore.WHITE}{Style.BRIGHT}SPEED{Style.RESET_ALL}",
            f"{Fore.WHITE}{Style.BRIGHT}TRACK{Style.RESET_ALL}",
            f"{Fore.WHITE}{Style.BRIGHT}V/SPEED{Style.RESET_ALL}",
            f"{Fore.WHITE}{Style.BRIGHT}DISTANCE{Style.RESET_ALL}",
        ]

        # Create the table
        table = tabulate(
            table_data,
            headers=headers,
            tablefmt="fancy_grid",
            stralign="center",
            numalign="center",
        )

        # Add title and footer
        title = f"{Back.BLUE}{Fore.WHITE}{Style.BRIGHT}{'AIRCRAFT DEPARTURE BOARD':^100}{Style.RESET_ALL}\n"
        footer = f"\n{Fore.CYAN}Last Update: {current_time} | Aircraft Count: {len(aircraft_list)} | Radius: {self.radius_km}km{Style.RESET_ALL}"
        footer += f"\n{Fore.MAGENTA}Monitoring: {self.location_name} ({self.lat:.4f}°, {self.lon:.4f}°){Style.RESET_ALL}"
        footer += f"\n{Fore.LIGHTBLUE_EX}Note: Operator info cached for performance. Some private aircraft may show 'Unknown'.{Style.RESET_ALL}"

        return title + table + footer

    def run_display(self, update_interval: int = 10):
        """Run the continuous display"""
        print("Starting Aircraft Tracker...")
        print(
            f"Monitoring aircraft within {self.radius_km}km of {self.lat:.4f}, {self.lon:.4f}"
        )
        print("Press Ctrl+C to stop\n")

        try:
            while True:
                # Clear screen (works on most terminals)
                print("\033[2J\033[H")

                aircraft_data = self.fetch_aircraft_data()
                display = self.format_departure_board(aircraft_data)
                print(display)

                time.sleep(update_interval)

        except KeyboardInterrupt:
            print("\nStopping Aircraft Tracker...")

    def get_operator_from_callsign(self, callsign: str) -> str:
        """Extract operator from callsign using ICAO airline codes"""
        if not callsign or len(callsign) < 3:
            return "Unknown"

        # Extract the airline code (first 3 characters for most airlines)
        airline_code = callsign[:3].upper()

        # Check if it's in our airline codes database
        if airline_code in self.airline_codes:
            return self.airline_codes[airline_code]

        # If not found, try 2-character codes (some airlines use 2-char codes)
        if len(callsign) >= 2:
            airline_code_2 = callsign[:2].upper()
            if airline_code_2 in self.airline_codes:
                return self.airline_codes[airline_code_2]

        # Check for common patterns
        if callsign.startswith("N") and len(callsign) >= 4:
            return "Private/Corporate"
        elif callsign.startswith(("G-", "D-", "F-", "I-", "OE-")):
            return "Private/Corporate"
        elif any(callsign.startswith(prefix) for prefix in ["JA", "HL", "VH", "ZK"]):
            return "Private/Corporate"

        return "Unknown"

    def fetch_aircraft_details(self, icao24: str) -> Dict[str, str]:
        """
        Fetch additional aircraft details using the ICAO24 code
        This uses a combination of methods to get operator info
        """
        # Check cache first
        if icao24 in self.operator_cache:
            return self.operator_cache[icao24]

        details = {
            "registration": "Unknown",
            "operator": "Unknown",
            "aircraft_type": "Unknown",
            "country": "Unknown",
        }

        # Try multiple sources for aircraft data
        sources_tried = []

        try:
            # Source 1: OpenSky aircraft database
            opensky_db_url = (
                f"https://opensky-network.org/api/metadata/aircraft/icao/{icao24}"
            )
            response = requests.get(opensky_db_url, timeout=5)
            sources_tried.append("OpenSky")

            if response.status_code == 200:
                data = response.json()
                if data:
                    details["registration"] = data.get("registration", "Unknown")
                    details["operator"] = data.get("operator", "Unknown")
                    details["aircraft_type"] = data.get("model", "Unknown")
                    details["country"] = data.get("country", "Unknown")

                    # If we got good data, we can stop here
                    if details["operator"] != "Unknown":
                        self.operator_cache[icao24] = details
                        return details

        except Exception:
            pass

        try:
            # Source 2: Use our enhanced callsign database
            # Since we don't have callsign in this method, we'll skip this for now
            pass

        except Exception:
            pass

        try:
            # Source 3: PlaneSpotters API (free tier available)
            # Note: This is a placeholder - you'd need to register for an API key
            # planespotters_url = f"https://api.planespotters.net/pub/photos/hex/{icao24}"
            # This would require API key registration
            pass

        except Exception:
            pass

        # If still no operator found, try pattern matching on registration
        if details["operator"] == "Unknown" and details["registration"] != "Unknown":
            reg = details["registration"]
            if reg.startswith(("N", "n")):
                details["operator"] = "US Registered"
                details["country"] = "United States"
            elif reg.startswith(("G-", "g-")):
                details["operator"] = "UK Registered"
                details["country"] = "United Kingdom"
            elif reg.startswith(("D-", "d-")):
                details["operator"] = "German Registered"
                details["country"] = "Germany"
            elif reg.startswith(("F-", "f-")):
                details["operator"] = "French Registered"
                details["country"] = "France"
            elif reg.startswith(("VT-", "vt-")):
                details["operator"] = "Indian Registered"
                details["country"] = "India"

        # Cache the result
        self.operator_cache[icao24] = details
        return details

    def get_aircraft_type_short(self, aircraft_type: str) -> str:
        """Convert long aircraft type names to shorter versions for display"""
        if not aircraft_type or aircraft_type == "Unknown":
            return "UNK"

        # Common aircraft type mappings
        type_mappings = {
            "Boeing 737": "B737",
            "Boeing 747": "B747",
            "Boeing 757": "B757",
            "Boeing 767": "B767",
            "Boeing 777": "B777",
            "Boeing 787": "B787",
            "Airbus A320": "A320",
            "Airbus A321": "A321",
            "Airbus A330": "A330",
            "Airbus A340": "A340",
            "Airbus A350": "A350",
            "Airbus A380": "A380",
            "Embraer": "EMB",
            "Bombardier": "CRJ",
            "McDonnell Douglas": "MD",
        }

        for full_name, short_name in type_mappings.items():
            if full_name.lower() in aircraft_type.lower():
                return short_name

        # If no mapping found, try to extract model number
        import re

        match = re.search(r"[A-Z]\d{3}", aircraft_type.upper())
        if match:
            return match.group()

        # Return first 4 characters if nothing else works
        return aircraft_type[:4].upper()

    def get_current_location(self) -> tuple[float, float, str]:
        """
        Get current location using IP-based geolocation
        Returns (latitude, longitude, location_string) tuple
        """
        try:
            # Try ipapi.co first (reliable and free)
            response = requests.get("http://ipapi.co/json/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                lat = data.get("latitude")
                lon = data.get("longitude")
                if lat and lon:
                    city = data.get("city", "Unknown")
                    region = data.get("region", "Unknown")
                    country = data.get("country_name", "Unknown")
                    location_str = f"{city}, {region}, {country}"
                    print(f"📍 Location detected: {location_str}")
                    print(f"🌐 Coordinates: {lat:.4f}°, {lon:.4f}°")
                    return float(lat), float(lon), location_str
        except:
            pass

        try:
            # Fallback to httpbin.org/ip + ipinfo.io
            ip_response = requests.get("https://httpbin.org/ip", timeout=5)
            if ip_response.status_code == 200:
                ip = ip_response.json().get("origin", "").split(",")[0]

                location_response = requests.get(
                    f"https://ipinfo.io/{ip}/json", timeout=5
                )
                if location_response.status_code == 200:
                    data = location_response.json()
                    loc = data.get("loc", "")
                    if loc and "," in loc:
                        lat, lon = map(float, loc.split(","))
                        city = data.get("city", "Unknown")
                        region = data.get("region", "Unknown")
                        country = data.get("country", "Unknown")
                        location_str = f"{city}, {region}, {country}"
                        print(f"📍 Location detected: {location_str}")
                        print(f"🌐 Coordinates: {lat:.4f}°, {lon:.4f}°")
                        return lat, lon, location_str
        except:
            pass

        # If all fails, use default NYC coordinates
        print("⚠️  Could not detect location automatically.")
        print("🏙️  Using default coordinates (New York City): 40.7128°, -74.0060°")
        print("💡 You can manually set coordinates in the main() function if needed.")
        return 40.7128, -74.0060, "New York City, NY, USA"

    def fetch_airline_codes_online(self) -> Dict[str, str]:
        """
        Fetch airline ICAO codes from online sources
        Returns a dictionary of ICAO codes to airline names
        """
        online_codes = {}

        print("🌐 Fetching airline codes from online sources...")

        # Source 1: Try OpenFlights airline database
        try:
            openflights_url = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat"
            response = requests.get(openflights_url, timeout=10)
            if response.status_code == 200:
                lines = response.text.strip().split("\n")
                for line in lines:
                    try:
                        parts = line.split(",")
                        if len(parts) >= 4:
                            # OpenFlights format: ID,Name,Alias,IATA,ICAO,Callsign,Country,Active
                            icao_code = parts[4].strip('"').strip()
                            airline_name = parts[1].strip('"').strip()
                            if icao_code and len(icao_code) == 3 and icao_code != "\\N":
                                online_codes[icao_code.upper()] = airline_name
                    except:
                        # Skip malformed lines
                        continue

                if online_codes:
                    print(
                        f"✅ Fetched {len(online_codes)} airline codes from OpenFlights database"
                    )
                    return online_codes

        except Exception as e:
            print(f"⚠️ OpenFlights source failed: {e}")

        # Source 2: Try a different aviation database
        try:
            # Alternative source - could try other aviation APIs here
            # For now, we skip to avoid hardcoding more sources
            pass

        except Exception as e:
            print(f"⚠️ Alternative source failed: {e}")

        # Source 3: Try Wikipedia's airline codes (if available as structured data)
        try:
            # This would require parsing Wikipedia or finding a structured data source
            # For now, we'll skip this to avoid hardcoding
            pass

        except Exception as e:
            print(f"⚠️ Wikipedia source failed: {e}")

        # If no online sources work, return empty dict
        if not online_codes:
            print(
                "⚠️ All online sources failed. Aircraft operator identification will be limited."
            )
            print(
                "💡 The system will rely on OpenSky metadata and registration patterns for operator detection."
            )

        return online_codes

    def update_airline_database_online(self):
        """Update the airline database with codes fetched from online sources"""
        try:
            online_codes = self.fetch_airline_codes_online()
            if online_codes:
                # Merge with existing codes (online codes take precedence for conflicts)
                original_count = len(self.airline_codes)
                self.airline_codes.update(online_codes)
                new_count = len(self.airline_codes)
                added_count = new_count - original_count
                print(
                    f"📊 Airline database updated: {original_count} → {new_count} codes (+{added_count} new)"
                )
            else:
                print("📊 No airline codes fetched from online sources.")
                print("🔍 Operator identification will rely on:")
                print("   • OpenSky aircraft metadata API")
                print("   • Aircraft registration pattern matching")
                print("   • Country-based operator classification")
        except Exception as e:
            print(f"⚠️ Error updating airline database: {e}")
            print("🔍 Falling back to metadata-based operator detection.")

# Parkkaro - Upgrade Guide

## What's New? 🚀

Your parking application has been upgraded with the following features:

### 1. **Google Maps Integration** 🗺️
- Parking lots are now displayed on an interactive Google Map (just like restaurants on Google Maps)
- Users can view all parking locations with markers on the map
- Click on markers to see parking lot details and book spots directly
- User's current location is shown on the map (if location permission is granted)

### 2. **Rebranded to "Parkkaro"** 🎨
- Application name changed from "Smart Parking" to "Parkkaro"
- All references updated across templates, navigation, and branding

### 3. **GPS Coordinates Support** 📍
- Database model updated to store latitude and longitude for each parking lot
- Admin interface includes fields to add/edit GPS coordinates
- Optional feature - parking lots work with or without coordinates

## Setup Instructions

### Step 1: Database Migration
Since we added new fields (latitude, longitude) to the database, you need to reset the database:

```powershell
# Remove the old database
Remove-Item instance\parking_app.db -ErrorAction SilentlyContinue

# The database will be recreated automatically when you run the app
```

### Step 2: Get Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Maps JavaScript API**
4. Create credentials (API Key)
5. Copy your API key

### Step 3: Add API Key to the Application

Open `templates\user\map_view.html` and find this line (near the bottom):

```html
src="https://maps.googleapis.com/maps/api/js?key=YOUR_GOOGLE_MAPS_API_KEY&callback=initMap">
```

Replace `YOUR_GOOGLE_MAPS_API_KEY` with your actual Google Maps API key.

### Step 4: Run the Application

```powershell
# Activate virtual environment
.\venv\Scripts\activate.ps1

# Run the application
python app.py
```

## How to Use

### For Admins:

1. **Login** with admin credentials (username: `admin`, password: `admin123`)
2. **Add/Edit Parking Lots:**
   - When adding or editing a parking lot, you'll see new fields for Latitude and Longitude
   - These are optional but recommended for map display
   - To find coordinates:
     - Open Google Maps
     - Right-click on the location
     - Click on the coordinates to copy them
     - Paste latitude and longitude in the respective fields

### For Users:

1. **View Map:**
   - After login, click on the **Map** link in the navigation
   - See all parking lots displayed on Google Maps
   - Red markers show parking locations
   - Blue marker shows your current location (if permitted)

2. **Book Parking:**
   - Click on any marker to see parking lot details
   - Click "Book Now" to reserve a spot
   - Or use the parking lot cards below the map

## Example GPS Coordinates for Testing

Here are some example coordinates you can use when adding parking lots:

| City | Location | Latitude | Longitude |
|------|----------|----------|-----------|
| Delhi | Connaught Place | 28.6289 | 77.2065 |
| Mumbai | Gateway of India | 18.9220 | 72.8347 |
| Bangalore | MG Road | 12.9716 | 77.5946 |
| Kolkata | Park Street | 22.5549 | 88.3519 |
| Chennai | Marina Beach | 13.0499 | 80.2824 |

## Features Overview

### Map View Features:
- ✅ Interactive Google Maps display
- ✅ Parking lot markers with info windows
- ✅ Current location detection
- ✅ Click markers to view details
- ✅ Direct booking from map
- ✅ Auto-centering on user location
- ✅ Parking lot cards with "Show on Map" button

### Updated Admin Interface:
- ✅ Add GPS coordinates when creating parking lots
- ✅ Edit GPS coordinates for existing lots
- ✅ Optional fields - works without coordinates too
- ✅ Helper text with example coordinates

### Application Rebranding:
- ✅ "Parkkaro" branding throughout
- ✅ Updated navigation and titles
- ✅ Updated footer and hero section

## Troubleshooting

**Map not displaying:**
- Make sure you've added a valid Google Maps API key
- Check if Maps JavaScript API is enabled in Google Cloud Console
- Check browser console for any JavaScript errors

**Coordinates not showing on map:**
- Verify latitude and longitude are entered correctly
- Latitude should be between -90 and 90
- Longitude should be between -180 and 180

**Database errors:**
- Delete the old database file and restart the application
- The new database will be created with the updated schema

## Next Steps

1. Delete old database and restart the app
2. Get your Google Maps API key
3. Update the map_view.html with your API key
4. Login as admin and add GPS coordinates to parking lots
5. Test the map view as a user

Enjoy your upgraded Parkkaro application! 🎉

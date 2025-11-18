# Google Maps API Setup Guide

## Quick Setup (3 Steps)

### Step 1: Get Your Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing one)
3. Go to **APIs & Services** → **Library**
4. Search for and enable **"Maps JavaScript API"**
5. Go to **APIs & Services** → **Credentials**
6. Click **"Create Credentials"** → **"API Key"**
7. Copy your API key (looks like: `AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)

### Step 2: Add API Key to Your App

Open `app.py` and find this line:

```python
app.config['GOOGLE_MAPS_API_KEY'] = 'YOUR_GOOGLE_MAPS_API_KEY'
```

Replace `YOUR_GOOGLE_MAPS_API_KEY` with your actual API key:

```python
app.config['GOOGLE_MAPS_API_KEY'] = 'AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
```

### Step 3: Reset Database and Run

```powershell
# Delete old database
Remove-Item instance\parking_app.db -ErrorAction SilentlyContinue

# Run the app
python app.py
```

## Testing

1. Login as admin (username: `admin`, password: `admin123`)
2. Go to "Add Parking Lot"
3. You should see the location picker working!
4. Allow location access when prompted

## Troubleshooting

**Still seeing "Oops! Something went wrong"?**
- Make sure your API key is correct (no spaces or quotes issues)
- Verify "Maps JavaScript API" is enabled in Google Cloud Console
- Check browser console (F12) for detailed error messages

**Location not detected?**
- Allow location access when browser asks
- Make sure you're using HTTPS (or localhost is allowed)
- Some browsers block location on HTTP connections

**API Key restrictions (Optional but recommended):**
1. In Google Cloud Console, go to your API key
2. Under "Application restrictions", select "HTTP referrers"
3. Add: `http://localhost:5000/*` and `http://127.0.0.1:5000/*`
4. Under "API restrictions", select "Restrict key"
5. Choose "Maps JavaScript API"

This makes your key more secure!

## Free Tier Limits

Google Maps API includes:
- $200 free credit per month
- ~28,000 map loads per month for free
- Perfect for development and small apps!

Your Parkkaro app is ready! 🎉

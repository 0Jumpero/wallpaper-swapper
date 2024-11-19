# Script to change windows 11 wallpaper to a random image from a database (JSON file with an array of urls) 

import ctypes
import os
import random
from PIL import Image
import requests
import winreg
import json

# Unsplash API key
key = 'your-api-key'

# Paths
pictures_folder = os.path.join('C:\\', 'Users', 'Public', 'Pictures', 'Wallpapers')
main_wallpaper_path = os.path.join(pictures_folder, "main_wallpaper.jpg")
lock_screen_wallpaper_path = os.path.join(pictures_folder, "lock_screen_wallpaper.jpg")
json_file_path = os.path.join(pictures_folder, 'wallpapers.json')

# Load JSON and get random URLs
def pick_random_wallpapers(json_file_path):
  print('Opening wallpapers database...')
  try:
    with open(json_file_path, 'r', encoding='utf-8') as f:
      urls = json.load(f)
  except FileNotFoundError:
    print(f"Error: {json_file_path} not found.")
    return []
  except json.JSONDecodeError:
    print(f"Error: Malformed JSON in {json_file_path}.")
    return []

  if urls == []: return []
  print('Selecting random wallpapers...')
  try:
    selection = random.sample(urls, 2)
    selection[0] = selection[0]['urls']['raw']
    selection[1] = selection[1]['urls']['raw']
  except (IndexError, KeyError):
    print("Error: Invalid data structure in the JSON file.")
    return []
  except Exception as e:
    print("Error picking random wallpapers.")
    return []

  print(f"Random wallpapers selected: \n {selection[0]} \n {selection[1]}")
  return selection

# Download and save wallpaper images
def download_wallpapers(urls, folder):
  if urls == []: return [0, 0]
  print('Downloading wallpapers...')
  wallpapers = []
  for i, url in enumerate(urls):

    # Get wallpaper data
    try:
      response = requests.get(url, stream=True)
      response.raise_for_status()
    except requests.exceptions.RequestException as e:
      print(f"Error downloading {url}: {e}")
      continue

    # Set name of file and path
    file_name = "home.jpg" if i == 0 else "lock.jpg"
    file_path = os.path.join(folder, file_name)

    # Add URL metadata
    try:
      print(f"Adding URL metadata to {file_name}...")
      response.raw.decode_content = True
      with Image.open(response.raw) as img:
        exif = img.getexif()  
        exif[0x010E] = url 
        img.save(file_path, "JPEG", exif=exif)
    except Exception as e:
      print(f"Error saving {file_name}: {e}")
      continue

    # Add file path to list
    wallpapers.append(file_path)
    print(f"Wallpaper {file_name} saved to {file_path}")
  return wallpapers


# Set the main wallpaper
def set_desktop_wallpaper(image_path):
  if(image_path == 0): return 1
  print('Setting desktop wallpaper...')
  try:
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, "Wallpaper", 0, winreg.REG_SZ, str(image_path))
    winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, "10")
    winreg.SetValueEx(key, "TileWallpaper", 0, winreg.REG_SZ, "0")
    winreg.CloseKey(key)
    ctypes.windll.user32.SystemParametersInfoW(20, 0, str(image_path), 3)
    print('Desktop wallpaper set.')
    return 0
  except Exception as e:
    print(f"Error setting desktop wallpaper: {e}")
    return 1

# Set the lock screen wallpaper
def set_lock_screen_wallpaper(image_path):
  if(image_path == 0): return 1
  print('Setting lockscreen wallpaper...')
  try:
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\Personalization", 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, "LockScreenImage", 0, winreg.REG_SZ, str(image_path))
    winreg.CloseKey(key)
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\PersonalizationCSP", 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, "LockScreenImageUrl", 0, winreg.REG_SZ, str(image_path))
    winreg.SetValueEx(key, "LockScreenImagePath", 0, winreg.REG_SZ, str(image_path))
    winreg.SetValueEx(key, "LockScreenImageStatus", 0, winreg.REG_DWORD, 1)
    winreg.CloseKey(key)
    print('Lockscreen wallpaper set.')
    return 0
  except Exception as e:
    print(f"Error setting lockscreen wallpaper: {e}")
    return 1

# Get wallpapers from Unsplash
def fetch_wallpapers_db(json_file_path):
  query = 'nature' # Change the query to selected wallpaper topic
  wallpapers = []
  page = 0

  # Check if api key is set
  if key == 'your-api-key':
    print("Error: API key not set.")
    return 1

	# Download wallpapers infos from Unsplash
  print("Fetching wallpapers database from Unsplash...")
  while page < 50:
    page += 1
    url = f"https://api.unsplash.com/search/photos?query={query}&orientation=landscape&per_page=30&page={page}&client_id={key}"
    try:
      response = requests.get(url)
      response.raise_for_status()  # Raise an error for bad status codes
      data = response.json()
      if 'results' in data:
        wallpapers.extend(data['results'])
      else:
        print(f"Unexpected API response structure on page {page}.")
        continue
      print(f"Fetched page {page}, total wallpapers: {len(wallpapers)}")

      # Check if we need to fetch more pages
      if len(data['results']) == 0:
        break

    except requests.exceptions.RequestException as error:
      print(f"Error fetching page {page}: {error}")
      continue
    except KeyError as e:
      print(f"Error parsing API response: Missing key {e}")
      continue

  # Check for errors
  if len(wallpapers) == 0:
    print("Error fetching wallpapers from Unsplash.")
    return 1

  # Check if wallpapers folder exists
  if not os.path.exists(json_file_path):
    print(f"Creating wallpapers folder at {os.path.dirname(json_file_path)}...")
    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
  
  # Save wallpapers infos to JSON file
  try:
    with open(json_file_path, 'w') as file:
      json.dump(wallpapers, file, indent=2)
    print(f"Saved {len(wallpapers)} wallpapers to {json_file_path}")
  except Exception as e:
    print(f"Error saving wallpapers to {json_file_path}: {e}")
    return 1

  return 0

# Check JSON
def check_wallpapers_JSON(json_file_path):
  print("Checking wallpapers database JSON...")
  if os.path.exists(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
      data = json.load(f)
      if len(data) < 300:
        return fetch_wallpapers_db(json_file_path)
  else:
    return fetch_wallpapers_db(json_file_path)
  return 0

# Main function
def change_wallpaper():

  # Check database
  status = check_wallpapers_JSON(json_file_path)

  # Get random wallpapers from JSON file
  if status == 0: urls = pick_random_wallpapers(json_file_path)
  else: urls = []

  # Download wallpapers
  if urls != []: wallpaper_files = download_wallpapers(urls, pictures_folder)
  else: wallpaper_files = [0,0]

  # Set the first wallpaper as desktop background
  status = set_desktop_wallpaper(wallpaper_files[0])

  #Set the second wallpaper as lock screen background
  status = status + set_lock_screen_wallpaper(wallpaper_files[1])

  if status == 0: print("Wallpapers changed successfully!")
  else: print("Error changing wallpapers.")

# Run the main function
change_wallpaper()

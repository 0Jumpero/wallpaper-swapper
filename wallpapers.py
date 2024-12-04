# Script to change windows 11 wallpaper to a random image from a database (JSON file with an array of urls) 

import ctypes
import os
from io import BytesIO
import random
from PIL import Image
import requests
import winreg
import json
import schedule
import tkinter as tk
import time
import pystray
from threading import Thread

# Load settings
try:
  print("Loading settings...")
  with open('settings.json', 'r', encoding='utf-8') as f:
    settings = json.load(f)
    key = settings['key']
    interval = settings['interval']
    lock_toggle = settings['lock_toggle']
    query = settings['query']
    pictures_folder = settings['pictures_folder']
except FileNotFoundError:
  print("Failed to load settings. Using default values...")
  key = 'your-api-key'
  interval = 30
  lock_toggle = False
  query = 'nature'
  pictures_folder = os.path.join('C:\\', 'Users', 'Public', 'Pictures', 'Wallpapers')

# Paths
main_wallpaper_path = os.path.join(pictures_folder, "main_wallpaper.jpg")
lock_screen_wallpaper_path = os.path.join(pictures_folder, "lock_screen_wallpaper.jpg")
json_file_path = os.path.join(pictures_folder, 'wallpapers.json')

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

# Get wallpapers from Unsplash
def fetch_wallpapers_db(json_file_path):
  global query
  wallpapers = []
  page = 0

  # Check if api key is set
  if key == 'your-api-key':
    print("Error: API key not set. Set it in settings.json.")
    root = tk.Tk()
    root.title("API Error")
    root.geometry("200x100")
    root.resizable(False, False)
    root.attributes('-toolwindow', True, '-topmost', True)
    tk.Label(root, text = "Error: API key not set.\nSet it in settings.json").place(relx=0.5, rely=0.25, anchor="center")
    tk.Button(root, text = "OK", width=10, command = root.destroy).place(relx=0.5, rely=0.7, anchor="center")
    root.eval('tk::PlaceWindow . center')
    root.mainloop()
    return "API key not set."

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
      if page == 1: break
      else: continue
    except KeyError as e:
      print(f"Error parsing API response: Missing key {e}")
      break

  # Check for errors
  if len(wallpapers) == 0:
    print("Error fetching wallpapers from Unsplash.")
    return "Error fetching wallpapers from Unsplash."

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
    return "Error saving wallpapers to JSON file."

  return 0

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
  if(not image_path): return "Error: Invalid desktop image path."
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
    return "Error setting desktop wallpaper."

# Set the lock screen wallpaper
def set_lock_screen_wallpaper(image_path):
  if(image_path == 0): return "Error: Invalid lock image path."
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
    return "Error setting lockscreen wallpaper."

# Main function to change wallpapers
def change_wallpaper():

  # Check database
  status = check_wallpapers_JSON(json_file_path)

  # Get random wallpapers from JSON file
  if status == 0: urls = pick_random_wallpapers(json_file_path)

  # Download wallpapers
  if status == 0: wallpaper_files = download_wallpapers(urls, pictures_folder)

  # Set the first wallpaper as desktop background
  if status == 0: status = set_desktop_wallpaper(wallpaper_files[0])

  #Set the second wallpaper as lock screen background
  if lock_toggle and status == 0: status = set_lock_screen_wallpaper(wallpaper_files[1])

  if status == 0: print("Wallpapers changed successfully!")
  else: print(f'Error changing wallpapers. Error message: "{status}"')

  return status

# Save settings
def save_settings():
  try:
    with open('settings.json', 'w', encoding='utf-8') as f:
      global key, pictures_folder, interval, lock_toggle, query
      json.dump({
        'key': key, 
        'interval': interval, 
        'lock_toggle': lock_toggle,
        'query': query,
        'pictures_folder': pictures_folder 
      }, f, indent=2)
    print("Settings saved.")
  except Exception as e:
    print(f"Error saving settings: {e}")

# Set interval function
def set_interval(new_interval):
  global interval, run, scheduler
  interval = new_interval
  print("Quitting current schedule...")
  run = False
  scheduler.join()
  print("Schedule quit.\nStarting new schedule...")
  run = True
  scheduler = Thread(target=run_schedule, daemon=True)
  scheduler.start()
  print(f"Schedule with {new_interval}min interval started.")
  save_settings()

# Elevate to admin 
def elevate():
  print("Relaunching as admin...")
  ctypes.windll.shell32.ShellExecuteW(None, "runas", "pythonw", __file__, None, 1)
  os._exit(0)

# Toggle lockscreen function
def toggle_lockscreen(setting):
  global lock_toggle
  if setting == True:
    print("Checking admin privileges...")
    try:
      isAdmin = ctypes.windll.shell32.IsUserAnAdmin()
    except:
      isAdmin = False

    if isAdmin:
      lock_toggle = True
      print(f"Lockscreen toggle set to {lock_toggle}.")
      save_settings()
    else:
      print("Lacking admin privileges.")
      root = tk.Tk()
      root.geometry("300x120")
      root.resizable(False, False)
      root.title("Admin mode required")
      root.attributes('-toolwindow', True, '-topmost', True)
      tk.Label(root, text="To change the lockscreen wallpaper you need to \nrelaunch the program in admin mode. Continue?", padx=10, pady=10).place(relx=0.5, rely=0.3, anchor="center")
      tk.Button(root, text="Yes", width=10, command=elevate).place(relx=0.3, rely=0.7, anchor="center")
      tk.Button(root, text="No", width=10, command=lambda: root.destroy()).place(relx=0.7, rely=0.7, anchor="center")
      root.eval('tk::PlaceWindow . center')
      root.mainloop()
  else:
    lock_toggle = False
    print(f"Lockscreen toggle set to {lock_toggle}.")
    save_settings()

# Tray menu setup
def tray_setup():
  print("Setting up tray menu...\nDownloading icon...")
  img_url = "https://cdn-icons-png.flaticon.com/512/1046/1046493.png"
  try:
    response = requests.get(img_url, stream=True)
    response.raise_for_status()
  except requests.exceptions.RequestException as e:
    print(f"Error downloading icon: {e}")
    return
  
  print("Converting menu items...")
  img = Image.open(BytesIO(response.content))
  tray = pystray.Icon("wallpaper-changer", img, "Wallpaper Changer", menu=(
    pystray.MenuItem("Change wallpaper", lambda: change_wallpaper()),
    pystray.MenuItem("Toggle Lockscreen", lambda: toggle_lockscreen(not lock_toggle), checked=lambda item: lock_toggle),
    pystray.MenuItem("Set Interval", pystray.Menu(
      pystray.MenuItem("15 minutes", lambda: set_interval(15), checked=lambda item: interval == 15),
      pystray.MenuItem("30 minutes", lambda: set_interval(30), checked=lambda item: interval == 30),
      pystray.MenuItem("1 hour", lambda: set_interval(60), checked=lambda item: interval == 60),
      pystray.MenuItem("2 hours", lambda: set_interval(120), checked=lambda item: interval == 120),
    )),
    pystray.MenuItem("Quit", lambda: tray.stop()),
  ))
  print("Starting tray icon...")
  tray.run()

# Schedule thread
def run_schedule():
  global run, interval

  print("Starting schedule thread...")
  # Schedule the wallpaper change
  schedule.every(interval).minutes.do(change_wallpaper)

  # Run the schedule
  while run:
    schedule.run_pending() 
    time.sleep(1)

  # Stop the schedule
  schedule.clear()
  print("Terminating schedule thread...")

# Main thread globals
run = True
scheduler = None

# Main thread
if __name__ == "__main__": 
  # Check lockscreen toggle requirement
  if lock_toggle: toggle_lockscreen(lock_toggle)

  # Initial wallpaper change
  status = change_wallpaper()

  if status == 0: 
    # Start the schedule in a separate thread
    scheduler = Thread(target=run_schedule, daemon=True)
    scheduler.start()

    # Show the tray icon
    tray_setup()

    # Stop the schedule when the tray icon is closed
    print("Quitting...")
    run = False
    scheduler.join()

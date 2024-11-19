# wallpaper-swapper

**wallpaper-swapper** is a Python script that dynamically changes your Windows 11 desktop and lock screen wallpapers using wallpapers from Unsplash. You can either use an included local database (`wallpapers.json`) or fetch new wallpapers via the Unsplash API.

## Features
- Gets database with 1500 wallpapers from Unsplash.
- Sets a random desktop and lock screen wallpaper.
- Automatically updates the local wallpapers database when necessary.
- Compatible with Windows 11.

## Prerequisites
1. Python 3.6 or higher installed on your system.
2. Install the required Python packages:
    ```bash
    pip install pillow requests
    ```
3. Administrator rights are required to change lockscreen wallpaper.

## Setup

### Place API Key
To fetch wallpapers from Unsplash, you'll need an API key:
1. Create a free Unsplash developer account at [Unsplash Developer](https://unsplash.com/developers).
2. Generate an API key.
3. Replace the placeholder `key` in the script with your API key:
   
```python
# Unsplash API key
key = 'your-api-key'
```

### Or use the Included Database
If you don't want to fetch new wallpapers:
1. Copy the provided `wallpapers.json` file to:
   
```
C:\Users\Public\Pictures\Wallpapers\
```

### (Optional) Change the wallpaper topic (default: nature)
```python
def fetch_wallpapers_db(json_file_path):
  query = 'nature' # Change the query to selected wallpaper topic
```

## Folder Structure

The script uses the following folder structure:
```
C:\
└── Users
    └── Public
        └── Pictures
            └── Wallpapers
                ├── main_wallpaper.jpg
                ├── lock_screen_wallpaper.jpg
                └── wallpapers.json
```
- main_wallpaper.jpg: The current desktop wallpaper.
- lock_screen_wallpaper.jpg: The current lock screen wallpaper.
- wallpapers.json: The local database of wallpapers (created/updated by the script).

The script will automatically create these folders and files if they do not exist.

## Usage

### Fetch New Wallpapers from Unsplash:
  Ensure the key variable contains a valid API key.
  Change wallpaper topic if needed.
  Run the script as an administrator.

### Use the Included Database:
  Place the wallpapers.json file in the correct folder.
  Run the script as an administrator.

## Notes

  The script requires administrator privileges to change wallpapers and edit Windows Registry settings.
  If the wallpaper database contains fewer than 300 wallpapers, the script will fetch more from Unsplash automatically.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
Contributing

Contributions are welcome! Feel free to fork this repository, create a branch, and submit a pull request.
Enjoy a refreshing look for your desktop and lock screen!

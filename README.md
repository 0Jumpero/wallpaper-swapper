# wallpaper-swapper

**wallpaper-swapper** is a Python script that dynamically changes your Windows 11 desktop and lock screen wallpapers using wallpapers from Unsplash. You can either use an included local database ([`wallpapers.json`](https://github.com/0Jumpero/wallpaper-swapper/blob/main/wallpapers.json)) or fetch new wallpapers via the Unsplash API.

## Download
- You can download the [`wallpapers.py`](https://github.com/0Jumpero/wallpaper-swapper/blob/main/wallpapers.py) script and run it with python
- You can also download standalone executable from the [Releases](https://github.com/0Jumpero/wallpaper-swapper/releases/)

## Features
- Gets database with 1500 wallpapers from Unsplash.
- Sets a random desktop and lock screen wallpaper.
- Automatically updates the local wallpapers database when necessary.

## Prerequisites for running script version
> 1. Python 3.6 or higher installed on your system.
> 2. Install the required Python packages: `pip install pillow requests`
> 3. Administrator rights are required to change lockscreen wallpaper.

## Prerequisites for running executable version
> None

## Setup for running script version

### Place API Key
To fetch wallpapers from Unsplash, you'll need an API key:
1. Create a free Unsplash developer account at [Unsplash Developer](https://unsplash.com/developers).
2. Generate an API key.
3. Replace the placeholder `key` in the settings.json (generated upon running script once) with your API key:
   
```json
{
    "key": "your-api-key",
}
```

### Or use the Included Database
If you don't want to fetch new wallpapers:
1. Copy the provided `wallpapers.json` file to:
   
```
C:\Users\Public\Pictures\Wallpapers\
```

### (Optional) Change the wallpaper topic (default: nature)
```json
{
  "query": "nature"
}
```

## Folder Structure

The script uses the following folder structure:
```
C:\
└── Users
    └── Public
        └── Pictures
            └── Wallpapers
                ├── home.png
                ├── lock.png
                ├── settings.json
                └── wallpapers.json

```
- home.png: The current desktop wallpaper.
- lock.png: The current lock screen wallpaper.
- settings.json: Settings for the wallpaper-swapper.
- wallpapers.json: The local database of wallpapers (created/updated by the script).

The script will automatically create these folders and files if they do not exist.

## Usage

### Fetch New Wallpapers from Unsplash:
  Ensure API key is set and valid in the settings.json.
  Change wallpaper topic if needed.
  Delete old wallpapers.json if present.
  Run the script.

### Use the Included Database:
  Place the wallpapers.json file in the correct folder.
  Run the script.

## Notes

  The script requires administrator privileges to change wallpapers and edit Windows Registry settings.
  If the wallpaper database contains fewer than 300 wallpapers, the script will fetch more from Unsplash automatically.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

Contributing

Contributions are welcome! Feel free to fork this repository, create a branch, and submit a pull request.
Enjoy a refreshing look for your desktop and lock screen!

Attributions

This script uses an image from www.flaticon.com as an icon.

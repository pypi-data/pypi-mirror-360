# Auto-DLP
A simple command-line utility for automating the process of downloading songs using yt-dlp and sorting them into folders. Can also push files to android devices.

The philosophy of this tool is to download songs and lay them out beautifully in the filesystem, this means that there are a lot of features to get the names of files, folders, etc. correct.

## Getting Started
Use ```pipx install auto-dlp``` to install the command directly or use
```pip install auto-dlp``` to install the module and run it using ```<Your python installation> -m auto_dlp```.
```Your python installation``` is usually one of ```python```, ```python3``` or ```py```.

In the command line try ```auto-dlp -h```. If this runs without an error, you have successfully installed the tool.

Now choose a directory in which you would like your music to be stored, there run the command ```auto-dlp --create-example .```. This will create an example ```auto-dlp.json``` file which will download some songs and playlists. For the more advanced features of this tool, read the following section.

## Advanced Features

### Pushing the files to folders (Syncing)
```jsonc
{
    "sync dirs": ["the/directory/you/would like to sync to"]
    
    // alternatively, if you have a lot of directories you might
    // want to sync to:
    // "sync": [
    //    "path1",
    //    "path2",
    //    ...
    // ]
    // The syncing is not invoked if the destination does not exist
    
    // Optional entries
    
    // Additional folders that should be copied to your device
    // By default Auto-DLP only copies the artist's folders
    // "extra sync folders": [...]
 }
```


### Pushing the files to Android devices
Use the normal method described in the previous header if possible.


------


First you must configure the feature in your `auto-dlp.json` file:
```jsonc
{
  // Where various files are cached
  "config dir": "~/.local/state/youtube-downloader/",
  // This is where your artists go
  "artists": {
    ...
  },
  // This is the important line
  // adb stands for Android-Debug-Bridge and
  // is an offial tool for debugging (and copying files)
  "adb push": true

  // The following options are optional
  
  // This option can be used to restart the adb service every
  // time the program is executed, use this if it is making problems
  // "restart adb": true
  
  // Where the files should be copied to 
  // "adb push dir": "/sdcard/Music"
  
  // Additional folders that should be copied to your device
  // By default Auto-DLP only copies the artist's folders
  // "extra sync folders": [...]
}
```

Then you must plug your phone into your Laptop with the phone's debug mode enabled. Now just start `auto-dlp` normally and it should copy the files over automatically.

### Heeelp!! I get errors on certain playlists/songs

For this there is two configuration options:
```jsonc
{
  // Where various files are cached
  "config dir": "~/.local/state/youtube-downloader/",
  // This is where your artists go
  "artists": {
    ...
  },
  // With this entry you can forcefully rename songs that
  // are automatically downloaded as part of a playlist.
  // This is for example a fix for the problem of empty names.
  "rename": {
    "<some name>": "<a valid name>",
    ...
  },
  // This key is for playlists that just don't want to be downloaded
  // and make the program throw the following error:
  // "The Youtube Api returned the same result twice"
  // Ironically this is (so far) only on official Youtube Playlists
  "fragile playlists": [
    "RDCLAK5uy_lp8LtelM9GiSwRFGGQjctKaGoHcrgQVEU",
    ...
  ]
}
```

### The names don't look like I want them to

The names for songs in playlists are simply those entered
on Youtube. These are, however, sometimes shit.

For this there is the following configuration options:
```jsonc
{
  // Where various files are cached
  "config dir": "~/.local/state/youtube-downloader/",
  // This is where your artists go
  "artists": {
    ...
  },
  // This entry specifies this that are searched for in names
  // and removed. Case is ignored and the values are treated as
  // python regexes
  "name rules": [
    // This value will remove all text from titles that contain a
    // '(official' followed by anything and then another ')'
    // i.e '(Official Music Video)'
    "\\(official.*\\)",
    ...
  ],
  // This entry is somewhat meta. It is intented to make writing
  // regexes for "name rules" easier. It is a simple find and replace
  // system.
  // In the following example the string "<" is replaced by something
  // that matches '[' or '('
  // The strings are replaced in the "name rules"
  // For example we could write the above rule as
  // "<official.*>"
  // Now it would also match (and remove) '[Official Video]'
  "rule macros": {
    "<": "[\\[\\(]",
    ">": "[\\]\\)]",
    ...
  }
}
```

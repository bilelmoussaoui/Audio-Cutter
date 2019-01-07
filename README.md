# Audio Cutter

[![CircleCI](https://circleci.com/gh/bilelmoussaoui/Audio-Cutter/tree/master.svg?style=shield)](https://circleci.com/gh/bilelmoussaoui/Audio-Cutter/tree/master)

The project is a WIP.

## Screenshots
<div align="center">
    <img src="https://pbs.twimg.com/media/DwRNuLwWsAAw3bR.jpg:large" alt="Screenshot of the current UI of Audio Cutter" />
</div>

## How to install?
As the application is a WIP, there are no stable packages of the application yet. Once the first stable release is out, you should be able to get it from Flathub.

### Dependencies
- `python3`
- `gtk3`
- `gstreamer`
- `gstreamer-plugins-good`
- `gst-editing-services`
- `gst-transcoder`
- `gst-python`
- `cairo`
- `py3cairo`
- `python-numpy`
- `meson`

### Install the Flatpak nightly
In order to build and run the Flatpak package you need to install
- `xdg-desktop-portal`
- `xdg-desktop-portal-gtk`

The GNOME 3.30 runtime/sdk is required to build the Flatpak package
```
flatpak install flathub org.gnome.Sdk//3.30
```
Then you can build & install it
```
git clone https://github.com/bilelmoussaoui/Audio-Cutter.git
cd Audio-Cutter/build-aux/flatpak
flatpak-builder --install app com.github.bilelmoussaoui.AudioCutter.json --user
```
You can run it using 
```
flatpak run com.github.bilelmoussaoui.AudioCutter
```
### Manual installation
```
meson _build --prefix=/usr
sudo ninja -C _build install
```

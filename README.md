# simple-icons-blender

[Simple Icons] Blender addon. Add 2D SVG brand icons to Blender easily.

## Download

Download the addon using [the next link](https://github.com/mondeja/simple-icons-blender/releases/download/5.20.0/simple_icons_blender.py):

```
https://github.com/mondeja/simple-icons-blender/releases/download/5.20.0/simple_icons_blender.py
```

If you want to install another version of [Simple Icons], change the version
number in the link.

## Install

Under `Edit` -> `Preferences` -> `Add-ons`, press on `Install` and select the
downloaded file:

<p align="center">
  <img src="images/install-button.png" "Simple Icons in drawio">
</p>

Search for `Simple Icons` in the search bar and enable the addon marking the
top-left checkbox:

<p align="center">
  <img src="images/enable-addon.png" "Simple Icons in drawio">
</p>


## Usage

You can load icons from the `3D Viewport` in object mode clicking on `Add` ->
`Curve` -> `Simple Icons`:

<p align="center">
  <img src="images/selector-usage.png" "Simple Icons in drawio">
</p>

All icons are operators, so you can directly load one through the `Menu Search`
(`Edit` -> `Menu Search`):

<p align="center">
  <img src="images/menu-search-usage.png" "Simple Icons in drawio">
</p>

Keep in mind that icons are small, so you'll probably need to zoom in after
loading to see them.

## Status

[![Verify Workflow][tests-badge]][tests-link]

[Simple Icons]: https://simpleicons.org
[tests-link]: https://github.com/mondeja/simple-icons-blender/actions/workflows/verify.yml
[tests-badge]: https://img.shields.io/github/workflow/status/mondeja/simple-icons-blender/Verify/develop?label=tests

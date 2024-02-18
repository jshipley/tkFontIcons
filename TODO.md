# To-Do

## Potential icon libraries to support
* Box Icons
* Feather Icons
* Font Awesome
* Google Material Icons
* Phosphor Icons
* Streamline Icons
* Any SVG icons

## Inputs
* Accept input from toml (including pyproject.toml) or cli
* Icon source (url or path) for icon resources
* Icon names to include

## FontAwesome
"fa-family fa-icon" - default to solid, make fa optional
find icon in icons
if it's not there, then search aliases
if it's not there then error out
if family is not specified, default to solid/brand
if family is specified but not there, error out
possibly warn about free/not free if family is not brand/solid
load alias+new, or just alias?

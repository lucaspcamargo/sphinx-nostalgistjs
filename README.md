# sphinx-nostalgistjs

Sphinx extension for embedding RetroArch in HTML documents, using [NostalgistJS](https://nostalgist.js.org/).
Styling and layout depend on Bootstrap v5, not included.

This package is released on [pypi](https://pypi.org/project/sphinx-nostalgistjs/).

<!--ENGBR_SECTION
## Demo

Click to start. Use the Z key to jump, and the Enter key to start.
This is emulating "flappybird.nes" on the "FCEUmm" core in RetroArch.

```{nostalgistjs}
    :rom_url: "flappybird.nes"
    :core_id: fceumm
    {
        "omit_attribution": true
    }
```
ENGBR_SECTION-->



## Basic Usage

Add this extension to your Sphinx `conf.py`, like so:

``` python
extensions = [
    "sphinx_nostalgistjs",
]
```

You have to at least configure where to find the JS file to be used whenever a document
uses this extension, also in `conf.py`:

``` python
nostalgistjs_script_url = "https://unpkg.com/nostalgist"
```

In this case, we are using UNPKG as a CDN. You can always download a release of NostalgisJS and place it
in your `_static` folder, loading it like so:

``` python
nostalgistjs_script_url = "/_static/nostalgist.js"
```

If the extension was successfully installed, you can include an emulator in a document, using the following directive:

    For reStructuredText:
    :::{nostalgistjs}
        :rom_url: "30yearsofnintendont.bin"
        :core_id: genesis_plus_gx
    :::    
    
    For Myst: (used throughout this document)
    ```{nostalgistjs}
        :rom_url: "30yearsofnintendont.bin"
        :core_id: genesis_plus_gx
    ```

This will embed an emulator that loads the given ROM with the respective emulation core.
If `rom_url` is not an URL, and instead, just a plain filename, NostalgistJS will try to load the ROM from [retrobrews](https://retrobrews.github.io/), as of the latest version. This uses the file extension in an attempt to determine the target system automatically. The core is not important in this case.

To use a local ROM file instead, use `:rom_file:` with a path relative to the current document:

    ```{nostalgistjs}
        :rom_file: roms/mygame.bin
        :core_id: genesis_plus_gx
    ```

Sphinx will copy the file to the output directory automatically and the correct URL will be resolved at build time.

Please consult the [launch(...) API](https://nostalgist.js.org/apis/launch/) of NostalgistJS to understand these arguments, and the available cores. As for the core to use, as a general rule:

| System     | Core |
|------------|------|
| Mega Drive | genesis_plus_gx |
| NES        | fceumm |
| SNES       | snes9x |
| GB, GBC, GBA | mgba |


```{warning}
Some configuration options allow a document's author to inject arbitrary JavaScript into the page.
This plugin is not appropriate for environments where this may be a security issue.
``````

## Advanced Usage

It is possible to change most parameters of NostalgistJS using the directive.

Inside the directive, if there is any content, there must be a JSON object that can configure the
emulator in various ways. Most notably, the `'nostalgist_options'` is an object that
can be used to add options to be passed to the [launch(...) API](https://nostalgist.js.org/apis/launch/) of
NostalgistJS.

Here is an example of advanced usage.
This injects preamble JS code to setup input device types and mappings, specific to the ROM being used.
It can get a bit ugly, though:

    ```{nostalgistjs}
        :rom_url: "https://example.site/rom.bin"
        :core_id: genesis_plus_gx
        {
            "nostalgist_options": {
                "retroarchConfig": {
                    "video_smooth": true,
                    "input_auto_mouse_grab": true
                }
            },
            "before_launch_epilogue": "let efs = nostalgist.getEmscriptenFS(); efs.mkdirTree('/home/web_user/retroarch/userdata/config/remaps/Genesis Plus GX'); efs.writeFile('/home/web_user/retroarch/userdata/config/remaps/Genesis Plus GX/rom.rmp',  'input_libretro_device_p1 = \"1\"\\ninput_libretro_device_p2 = \"2\"');"
        }
    ```

## Directive options

### `rom_url`

A URL or plain filename for the ROM to load. If a plain filename is given (no protocol), NostalgistJS will attempt to load it from [retrobrews](https://retrobrews.github.io/). Mutually exclusive with `rom_file`.

### `rom_file`

A path to a local ROM file, relative to the current document. Sphinx will copy the file into the build output using its download file mechanism (`_downloads/<hash>/<filename>`), and the correct absolute URL is resolved automatically at build time. Mutually exclusive with `rom_url`.

### `core_id`

The RetroArch core to use for emulation. See the table above for common values.

### `nostalgist_options`

These are the options passed straight to NostalgistJS for configuring the emulator. 
Consult the [NostalgistJS documentation](https://nostalgist.js.org/apis/launch/) for more info. 

The options `rom` and `core` are filled in from the directive's `rom_url`/`rom_file` and `core_id` parameters, and don't need to be specified again. 
Also, `respondToGlobalEvents` is set to false by default, but this can be overridden.

Note that there's no need to specify the `element` option, this is handled automatically by the plugin.
Doing so will break the UI controls.

### `omit_attribution`

A boolean. If set to true, this will hide the credits that are rendered at the bottom. Defaults to false.

### `extra_nostalgist_options`

A string. This will be output directly in the JavaScript source, inside an object literal. The resulting 
object is merged into the options object used for launching NostalgistJS.

This can be used to add options that cannot be expressed in JSON, such as callback functions. 
Defaults to an empty string.

### Custom code injection

#### `before_launch_preamble`

JS code executed before `Nostalgist.launch()` is called. The `nostalgist` instance is **not** available here.
Use this for setting up options or state that doesn't require the emulator instance.

#### `before_launch_epilogue`

JS code executed inside the `beforeLaunch` callback, after the `nostalgist` instance is assigned.
The `nostalgist` instance **is** available here. Use this for Emscripten FS setup, input remaps, and similar pre-launch configuration that requires the instance (e.g. `nostalgist.getEmscriptenFS()`).

#### `on_launch_preamble`

JS code executed after the emulator starts (inside `.then()`), before UI state is updated.

#### `on_launch_epilogue`

JS code executed after the emulator starts (inside `.then()`), after UI state is updated.

## Troubleshooting

In case the ROM doesn't load, it may be related to CORS configuration issues.
Please refer to the browser's "Developer Tools" console and network tabs for clues of
what may be happening.

## License

This project is licensed under the GPLv3 license.

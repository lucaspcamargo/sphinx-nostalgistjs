# sphinx-nostalgistjs

Sphinx extension for embedding RetroArch in HTML documents, using [NostalgistJS](https://nostalgist.js.org/).

## Quick Usage

Add this extension to your Sphinx `conf.py`, like so:

``` python
extensions = [
    "sphinx_nostalgistjs",
    ⋯
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


    ```{nostalgistjs}
        :rom_url: "30yearsofnintendont.bin"
        :core_id: genesis_plus_gx
    ```

This will lanuch the given ROM with the given emulation core.
If `rom_url` is not an URL, and instead, just a plain filename, NostalgistJS will try to load the ROM from [retrobrews](), as of the latest version.

Please consult the [launch(...) API](https://nostalgist.js.org/apis/launch/) of NostalgistJS to understand these arguments, and the available cores.

**TODO continue**

## TODO Extension configuration

## TODO Directive configuration
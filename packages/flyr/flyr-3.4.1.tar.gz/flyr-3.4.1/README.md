# Flyr
![A picture of a FLIR thermogram, the embedded optical data and a Flyr render concatenated into one](https://bitbucket.org/nimmerwoner/flyr/downloads/readme_intro.jpg)

Flyr is a library for extracting thermal data from FLIR images written fully in Python.

Other solutions are wrappers around ExifTool to actually do the hard part of extracting the thermal data. Flyr is a reimplementation of the ExifTool's FLIR parser. Practically, this offers the following benefits:

* Faster decoding because no new process needs to be started and in-memory data does not need to be communicated to this other process
* More accurate, because Flyr uses all of the camera metadata to translate the raw values into Kelvin, while other projects have a certain set hardcoded. The differences are often about 0.1°C, but can be as high as 0.6°C.
* Easier and robust installation and deployment, because Flyr is completely installable from PyPI.
* Arguably simpler use: no need to create a superfluous extraction object; simply call `thermogram = flyr.unpack(flir_file_path)` and done
* Extra features (see feature section) such as different units, built-in rendering and adjustable thermal data.

## Installation

Flyr is installable from [PyPi](https://pypi.org/project/flyr/):

```bash
pip install flyr
```

## Latest additional features

These features appeared in 3.4.0. Also see the CHANGELOG.md for feature history.

- Exposed embedded measurements, such as spot, ellipsis and area, via `FlyrThermogram.measurements`; other are expected to work too, but untested

## Upcoming features

These are features already implemented and merged into the master branch, but not released yet. Also see the CHANGELOG.md for feature history.

## Usage and features
### Different units
Thermal data is available in kelvin, celsius and fahrenheit.

```python
import flyr

flir_path = "thermograms/flir_c5_1.jpg"
thermogram = flyr.unpack(flir_path)

thermal = thermogram.kelvin  # As kelvin
thermal = thermogram.celsius  # As celsius
thermal = thermogram.fahrenheit  # As fahrenheit
```

### Optical data can be read
![The optical photo embedded in the FLIR thermogram](https://bitbucket.org/nimmerwoner/flyr/downloads/readme_optical.jpg)

To read the embedded photo, access either `optical` or `optical_pil` to respectively get a 3D numpy or Pillow Image object with the photo.

```python

import flyr

flir_path = "thermograms/flir_e5_2.jpg"
thermogram = flyr.unpack(flir_path)
optical_arr = thermogram.optical  # Also works
thermogram.optical_pil.save("optical.jpg")
```

### Built-in support for rendering
![Examples of different RGB renders of the same thermogram](https://bitbucket.org/nimmerwoner/flyr/downloads/readme_render_example.png)

Flyr has built-in support to render thermal data to RGB images. It is possible to use the embedded palette or one of the provides [palettes](flyr/palettes). Normalization can be done by percentiles or absolute values.

```python
import flyr

flir_path = "thermograms/flir_e5_2.jpg"
thermogram = flyr.unpack(flir_path)
# render = thermogram.render()  # Use to get raw RGB array
render = thermogram.render_pil()  # Returns Pillow Image object
render.save(f"render-embedded.png")
```

```python
palettes = ["turbo", "cividis", "inferno", "grayscale", "hot"]
for p in palettes:
    # The below call returns a Pillow Image object.
    # A sibling method called `render` returns a numpy array.
    render = thermogram.render_pil(
        min_v=27.1,
        max_v=35.6,
        unit="celsius",
        palette=p,
    )
    render.save(f"render-{p}.png")
```

To render by percentiles, call as below. This approach is useful when it isn't known what temperature range to render.

```python
thermogram.render_pil(
    min_v=0.0,
    max_v=1.0,
    unit="percentiles",
    palette="copper",
).save(f"render-percentiles.png")
```

It's also possible to apply a palette only to a specific part of rendered image, highlighting it and leaving the rest grayscale. Just pass a boolean mask to the `mask` parameter.

```python
mask = thermogram.kelvin > thermogram.kelvin.mean()
thermogram.render_pil(mask=mask).save("render-masked.png")
```

### Edge emphasis for better delineation
![Example of five renders with and without edges emphasized](https://bitbucket.org/nimmerwoner/flyr/downloads/readme_edge_emphasis.png)

If optical imagery is present, it can be used to detect edges and more sharply delinate them. Used the `edge_emphasis` parameter with a value between 0 and 1 to enable it. When a mask is applied, edges are only emphasized in the masked region.

```python
import flyr

thermogram = flyr.unpack("flir_e6_1.jpg")
thermogram.render_pil(edge_emphasis=0.0).save("render-no-edge-emphasis.png")
thermogram.render_pil(edge_emphasis=0.275).save("render-edge-emphasis.png")

mask = thermogram.kelvin > thermogram.kelvin.mean()
thermogram.render_pil(edge_emphasis=0.275, mask=mask).save("render-edge-emphasis-masked.png")
```

### Putting the Picture in the Picture
![Example of a render pictured in a photograph (Picture-in-Picture)](https://bitbucket.org/nimmerwoner/flyr/downloads/readme_picture_in_picture_example.png)

Renders and optical imagery can also be combined according to the Picture-in-Picture mode.

```python
import flyr

thermogram = flyr.unpack("flir_e40_4.jpg")
thermogram.picture_in_picture_pil(render_opacity=0.8).save("pip.png")
```

![Example of a masked render pictured in a photograph (Picture-in-Picture)](https://bitbucket.org/nimmerwoner/flyr/downloads/readme_picture_in_picture_mask_example.png)

Like the `render_pil` method, a `mask` parameter can be used to highlight a certain region of the image. There are two modes in which this mask can work: `"classical"` and `"alternative"`. In classical mode, the photograph is highlighted using a thermal mask of the region of interest. In the alternative mode, a thermal mask is applied to a grayscale render of the thermogram layered on top of the optical image.

```python
import flyr

thermogram = flyr.unpack('flir_one_pro_1.jpg')
mask = thermogram.kelvin > thermogram.kelvin.mean()
thermogram.picture_in_picture_pil(mask=mask, mask_mode="classical").save("pip_classical.png")
thermogram.picture_in_picture_pil(mask=mask, mask_mode="alternative").save("pip_alternative.png")
```

### Access embedded measurements

Measurements embedded in the thermogram can be accessed via the `measurements` member.

```python
import flyr

thermogram = flyr.unpack("flir_e50_3.jpg")
for m in thermogram.measurements:
    print(f"{m.tool} at {m.params} called {m.label}")

# Tool.SPOT at [115, 83] called Sp1
# Tool.SPOT at [104, 42] called Sp2
# Tool.SPOT at [113, 11] called Sp3
# Tool.SPOT at [102, 99] called Sp4
# Tool.SPOT at [88, 121] called Sp5
# Tool.SPOT at [116, 125] called Sp6
# Tool.SPOT at [137, 105] called Sp7
# Tool.SPOT at [154, 93] called Sp8
```

### Adjustable camera settings
![Examples of different RGB renders of the same thermogram](https://bitbucket.org/nimmerwoner/flyr/downloads/readme_render_emissivities.png)

It is possible to update the camera settings / parameters with which the thermal data is calculated. A typical value to adjust would be `emissivity`, but `object_distance`, `relative_humidity` and others are also configurable. See the parameters of [`FlyrThermogam.__raw_to_kelvin()`](https://bitbucket.org/nimmerwoner/flyr/src/90635d825bba132a99a240c511df892fab1f05bb/flyr/thermogram.py#lines-217) for which.

```python
import flyr

flir_path = "thermograms/flir_e5_2.jpg"
thermogram = flyr.unpack(flir_path)

emissivities = [0.6, 0.7, 0.8, 0.9, 1.0]
for e in emissivities:
    thermogram = thermogram.adjust_metadata(emissivity=e)
    # thermal = thermogram.celsius  # Access updated data as normal
    render = thermogram.render_pil(
        min_v=27.1,
        max_v=35.6,
        unit="celsius",
        palette="viridis",
    )
    render.save(f"render-{e}.png")
```

### Read from file, from file handle or binary stream
Call `flyr.unpack` on a filepath to receive a numpy array with the thermal data. Alternatively, first open the file in binary mode for reading and and pass the the file handle to `flyr.unpack`.

```python
import flyr

# From file path
flir_path = "thermograms/flir_e5_2.jpg"
thermogram = flyr.unpack(flir_path)  # From file path
```

```python
# From file handle / binary stream
with open(flir_path, "rb") as flir_handle:  # In binary mode!
    thermogram = flyr.unpack(flir_handle)
```

## Access EXIF data
Some common EXIF metadata has been made easily accessible via `thermogram.camera_metadata`:

```python
import flyr

# From file path
flir_path = "thermograms/flir_e75_1.jpg"
thermogram = flyr.unpack(flir_path)
cm = thermogram.camera_metadata
print(cm.data)  # Raw EXIF data (dict)
print(cm.gps_data)  # Raw GPS data (dict)
print(cm.date_time)  # Parsed datetime object of when picture was taken (datetime)
print(cm.gps_altitude)  # (float)
print(cm.gps_image_direction)  # (float)
print(cm.gps_latitude)  # (float)
print(cm.gps_longitude)  # (float)
print(cm.gps_map_datum)  # (str)
print(cm.make)  # (str)
print(cm.model)  # (str)
print(cm.software)  # (str)
print(cm.x_resolution)  # (float)
print(cm.y_resolution)  # (float)
```

The `data` and `gps_data` properties may also contain values not accessible via the handy properties mentioned above. The return values are always either the value itself or `None`, in case this EXIF data is not embedded in the file.


## Supported cameras
Currently this library has been tested to work with:

* FLIR C5
* FLIR E4, E5, E6, E8, E8XT, E30, E30BX, E40, E50, E50BX, E53, E60BX, E75
* FLIR I5
* FLIR ONE, ONE Pro, ONE Pro Next Gen
* FLIR P60 (PAL)
* FLIR SC660
* FLIR T630SC, T660
* FLIR ThermaCAM B400

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. Most help is currently needed supporting more models and testing against more pictures. Testing and developing for your own camera's images or FLIR Tools' samples is recommended.

## Acknowledgements
This code would not be possible without [ExifTool](https://exiftool.org/)'s efforts to [document](https://exiftool.org/TagNames/FLIR.html) the FLIR format. [tomas123](https://www.eevblog.com/forum/thermal-imaging/flir-e4-thermal-imaging-camera-teardown/msg342072/#msg342072)'s work is similarly important to mention. [Previous work](https://github.com/Nervengift/read_thermal.py) in Python must also be acknowledged for creating a workable solution.

## License
Flyr is licensed under The European Union Public License 1.2. The English version is included in the license file. Translations for all EU languages, each fully legally valid, can be found at the [EUPL](https://eupl.eu/) website.

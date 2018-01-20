# blender-addon-cocos2dx

This Blender add-on allows to export one or more objects to Cocos2d-x. It
uses Cocos2d-x's JSON format (c3t). The advantages of this format are:
* It uses a standardized data format and can be loaded without much effort in
  most programming languages.
* It is human readable and easy to understand.
* It can be modified in any text editor to quickly

The obvious disadvantages of the c3t format are:
* It is much larger than a binary format.
* Loading in Cocos2d-x is slower.

Note that in this early stage the add-on does not export animations. It can
only be used for exporting meshes.

## Installation

This addon is installed just like any other Blender addon. In case you have never done
it before, follow the instructions below:

* Safe this add-on's ZIP-file on the hard disk.
* Go to ``File > User Preferences...``
* Select the ``Add-ons`` tab.
* Press the button ``Install Add-on from File...`` at the bottom of the tab.
* Select the ZIP-file and press ``Install Add-on from File...`` at the upper right.

At this point, the add-on is installed but not activated and won't show up in the
export menu. Follow the next steps to activate the add-on:
* Enter ``cocos2d`` in the search field of the ``Add-ons`` tab. The only match should be this add-on.
* Alternatively you can can select the category ``Import-Export`` from the list on the left and search for this add-on.
* Click the small check-box to the left of the add-on to activate it for the current Blender session.
* If the add-on should be activated automatically the next time when Blender starts, click on the
  ``Save User Settings`` button at the bottom of the dialog.

## Updates

The add-on can be updated in the ``Add-ons`` tab in the ``User Preferences``
dialog (``File > User Preferences...``).
Simply click on the small triangle to the left of the add-on to show the updater
options. Here it is also possible to activate auto-updating and the frequency
for checking for updater. Note that auto-updates are disabled by default.

## Usage

Exporting with the Cocos2d-x add-on follows the same procedure as most other
exporters. The steps are:

* Go into object mode and select the relevant objects for exporting.
* Next choose ``File > Export > Cocos2d-x (.c3t)`` to bring up the export dialog.
* Select a directory and output filename.
* Adjust the export options (see below).
* Press ``Export Cocos2d-x`` in the upper right corner to create the c3t file.

### Export options

The Cocos2d-x add-on makes the options listed below available for the export.
Note that the add-on always operates on copies of the objects, e.g. when
applying the mesh modifiers, so no harm is done to the original data.

* ``Forward:`` Selects the axis in the exported coordinate frame pointing forward.

* ``Up:`` Selects the axis in the exported coordinate frame pointing up.

* ``Selection Only:`` If checked, only selected objects will be exported. Otherwise, all objects in the scene
  are exported.

* ``Export Normals:`` When checked, the normal vectors are written into the c3t files. Normals are witten per
  vertex per face. This makes the exported file larger but leads to much better lightning especially when the
  model has sharp edges.

* ``Export UVs:`` If checked, the UV coordinates and textures are exported.

* ``Apply Modifiers:`` When checked, the mesh modifiers are applied before the mesh is
  exported.

* ``Use Modifiers Render Settings:`` When selected, the modifier's render settings are
  used. If unchecked, the preview settings are applied instead.

* ``Scale:`` The factor by which all objects are scaled during exporting.

* ``Path Mode:`` Selects how the exporter deals with file names of textures, which
  are referenced by the exported objects.

### Known issues

If in Cocos2d-x a texture does not show up and the model is painted with a solid red color instead, most likely
Cocos2d-x is not able to find the texture. In this case, it is recommended to set ``Path Mode`` to ``Copy``. This will copy the
textures into the same directory as the c3t output file. In the JSON file, the texture is then referenced only
by its filen ame.

## Future work

* Exporting animations is work in progress.
* Only the text-based c3t format is supported. There is no support for writing a binary c3b file, yet.

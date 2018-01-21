# blender-addon-cocos2dx

This is a Blender exporter to write objects in the Cocos2d-x ``c3t`` format, which
is a JSON text file. Directly exporting to Cocos2d-x's native text format obsoletes
the usual workflow of exporting to FBX and converting to Cocos2d-x with ``fbx-conv``.

The advantages of the ``c3t`` format are:
* It is plain JSON, which is standardized and easy to load in most programming languages.
* It is human readable and easy to understand.
* It can be modified in a text editor to quickly experiment with changes in
  transformation matrices, for example.

Note that the current version of this add-on does not export animations, yet. Also, it
cannot serialize to ``c3b``, which is a binary format used by Cocos2d-x.

# Installation

This add-on is installed just like any other Blender add-on. In case you have never done
it before, follow the instructions below:

* Download this add-on in its ZIP-form.
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

# Updates

The add-on can be updated from the ``Add-ons`` tab in the ``User Preferences``
dialog (``File > User Preferences...``).
Simply click on the small triangle to the left of the add-on to show the updater
options. Here it is also possible to activate auto-updating and the frequency
for checking for updates. Note that auto-updates are disabled by default.

# Usage

Exporting with the Cocos2d-x add-on follows the same procedure as most other
exporters. The steps are:

* Go into object mode and select the relevant objects for exporting.
* Next choose ``File > Export > Cocos2d-x (.c3t)`` to bring up the export dialog.
* Select a directory and output filename.
* Adjust the export options (see below).
* Press ``Export Cocos2d-x`` in the upper right corner to create the ``c3t`` file.

## Export options

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

# Known issues

If a texture does not show up in Cocos2d-x and the model is painted with a solid red color instead, most likely
Cocos2d-x is not able to find the texture file. In this case, it is recommended to set ``Path Mode`` to ``Copy``. This will copy the
textures into the same directory as the c3t output file. In the JSON file, the texture is then referenced only
by its file name.

# Work in progress

* Export animations.
* Add support for the binary ``c3b`` format.

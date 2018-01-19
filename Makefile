#!/bin/bash
#
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

# ====---------------------------------------------------------------------====
#     This is a Blender addon for exporting a scene to Cocos2d-x in
#     its JSON file format (c3t).
#     Created by Manuel Freiberger.
# ====---------------------------------------------------------------------====

PROJECT  = Cocos2d-x-Exporter
VERSION  = 0.1.0
BUILDDIR = build
FILELIST = *.py LICENSE README.md

.DEFAULT_GOAL := release


release:
	mkdir -p $(BUILDDIR)/$(PROJECT)
	cp $(FILELIST) $(BUILDDIR)/$(PROJECT)
	cd $(BUILDDIR); zip -r $(PROJECT)_$(VERSION).zip $(PROJECT)

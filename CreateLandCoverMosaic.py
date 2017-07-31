# ----------------------------------------------------------------------------------------
# CreateLandCoverMosaic.py
# Version:  ArcGIS 10.3.1 / Python 2.7.8
# Creation Date: 2017-07-17
# Last Edit: 2017-07-31
# Creators:  Roy Gilb, DJ Helkowski, and Kirsten Hazler
# 
# Summary:
# This model creates a mosaic dataset and places it into an output geodatabase. It then adds raster tiles to the mosaic dataset. Next, the model imports mosaic dataset geometry from an imported footprint. 
# Then, the model sets dataset properties and afterwards, the raster dataset becomes projected. Finally, a colormap is imported from one of the original raster files. 
#
# Usage Tips:
#
# Dependencies:
#
# Syntax: CreateLandCoverMosaic <outputGDB> <mosaicName> <inDir> <snapRaster> <inFootprint> <outTIFF> <inputColormap> <outputDataset> 
# Description: 
# 
# Parameters:
# Mosaic Dataset Name - select a name for your mosaic dataset.
# Output Geodatabase - select a geodatabase for your mosaic dataset to be stored in.
# Input Raster Folder - Select the folder containing the raster files you want to be added to the mosaic dataset. 
#                       These input rasters are in the NAD 1983 HARN State Plane Virginia North OR South FIPS 4502 Feet coordinate system.
# Input Footprint Geometry - Select a feature class whose footprint will match the mosaic dataset.
# Snap Raster - Select a snap raster that is in the Virginia Lambert coordinate system. 
# Output Projected Raster - Select the name and storage of your projected raster.
# Input Raster Colormap - select the raster file from which you want to import a colormap to the output raster dataset. 

# ---------------------------------------------------------------------------
#import modules
import arcpy # to get ArcGIS functionality
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
import os # provides access to operating system funtionality such as file and directory paths
import sys # provides access to Python system functions
import traceback # used for error handling

# Script arguments
inDir = arcpy.GetParameterAsText(0) # Folder with raster files you want to be added to the mosaic dataset.  
filterString = arcpy.GetParameterAsText(1) # Prefix string used to restrict rasters selected for processing
### To Do: In toolbox, make the above a drop-down with only two options ("N" or "S")
snapRaster = arcpy.GetParameterAsText(2) # This will be used to set output coordinate system and pixel alignment
inFootprint = arcpy.GetParameterAsText(3)
delivArea = arcpy.GetParameterAsText(4) # The delivery area to process.
### To Do: In toolbox, make the above a string type filtered by a value list for user to choose from, based on all possible values from the "Delivery A" field in both tile reference shapefiles
outTIFF = arcpy.GetParameterAsText(5) # Need to enforce a TIF output somehow

### To do: Edit toolbox to reflect changes in user-specified parameters
### To do: clean up the obsolete junk and comments above when done

# Local variables:
cellSizeIn = 3.28084  #You need the input cell size first, which is in feet. 
cellSizeOut = 1  #Set output cell size to 1 (meter), rather than 3.28084 (feet)
resamp = "NEAREST"
outDir = os.path.dirname(outTIFF)
outName = os.path(outTIFF)
baseName = outName[:-4]

# Create geodatabase in output directory, for storing mosaic dataset 
gdbName = 'Mosaics.gdb'
arcpy.CreateFileGDB_management(outDir, gdbName)

# Specify paths to mosaic dataset and raster copy
mosaicDataset = outDir + os.sep + gdbName + os.sep + "md_%s" %baseName
mosaicCopy = outDir + os.sep + "rd_%s.tif" %baseName    #Place copied mosaic in same folder as output TIF

# Specify output coordinate system and snap raster
outCoordSys = arcpy.Describe(snapRaster).spatialReference
arcpy.env.snapRaster = snapRaster

# Create a list containing only the paths to rasters with the specified criteria 
arcpy.env.workspace = inDir
rasterList = arcpy.ListRasters("%s*" %filterString, "TIF")

# Get the input coordinate system from the first raster in the list
inCoordSys = arcpy.Describe(rasterList[0]).spatialReference

# Check coordinate systems of all remaining rasters in list
# If not all the same as inCoordSys from first raster, throw error and abort.
for rast in rasterList[1:]:
   cs = arcpy.Describe(rast).spatialReference.Name
   if cs != inCoordSys.Name:
      arcpy.AddError('Coordinate systems do not match for all rasters in directory. Aborting operation.')
      sys.exit()

# Process: Create Mosaic Dataset
arcpy.CreateMosaicDataset_management(outputGDB, mosaicName, inCoordSys, "1", "8_BIT_UNSIGNED", "NONE", "")

arcpy.AddMessage('Mosaic dataset created...')
arcpy.AddMessage('Adding Rasters to the dataset...')

# Process: Add Rasters To Mosaic Dataset
# Replaced inDir with rasterList
arcpy.AddRastersToMosaicDataset_management(mosaicDataset, "Raster Dataset", rasterList, "", "UPDATE_BOUNDARY", "NO_OVERVIEWS", "", "", "", inCoordSys)

arcpy.AddMessage('Importing geometry and setting mosaic dataset properties...')
### To do: Create a layer representing only the footprints corresponding to the selected delivery area. Call it lyrFootprint.

# Process: Import Mosaic Dataset Geometry
arcpy.ImportMosaicDatasetGeometry_management(mosaicDataset, "FOOTPRINT", "Name", lyrFootprint, "Tile")

# Process: Set Mosaic Dataset Properties
arcpy.SetMosaicDatasetProperties_management(mosaicDataset, "", "", "", "None", "", "", resamp, "NOT_CLIP", "FOOTPRINTS_MAY_CONTAIN_NODATA", "CLIP", "NOT_APPLY", "", "", "Center", "Center", "", "", "", "MAX", "", "", "", "", "", cellSizeIn, "Basic", "", "", "", "", "", "", "", "", "THEMATIC", "1", "", "None")

# Process: Copy Raster
arcpy.AddMessage('Copying mosaic dataset...')
arcpy.CopyRaster_management(mosaicDataset, mosaicCopy)

# Check if coordinate system for mosaicCopy is the same as for snapRaster. 
# If it is, no need to re-project, and mosaicCopy is final product. 
if inCoordSys.Name = outCoordSys.Name:
   arcpy.AddMessage('No reprojection necessary.')
   ### To do: rename copyMosaic to be the name of the user-selected output name
else:
   arcpy.AddMessage('Projecting mosaic...')
   # First check if a geographic transformation is needed
   inGCS_name = inCoordSys.GCS.Name
   outGCS_name = outCoordSys.GCS.Name
   if inGCS_name == outGCS_name:
      arcpy.AddMessage('Datums are the same; no geographic transformation needed.')
      geoTrans = ""
   else:
      arcpy.AddMessage('Datums do not match; re-projecting with geographic transformation')
      # Get the list of applicable geographic transformations
      transList = arcpy.ListTransformations(inCoordSys,outCoordSys)
      # Extract the first item in the list which I hope is the right transformation to use
      geoTrans = transList[0]
   # Process: Project Raster
   arcpy.ProjectRaster_management(mosaicCopy, outTIFF, outCoordSys, resamp, cellSizeOut, geoTrans, "", inCoordSys) 

# Process: Add Colormap
arcpy.AddColormap_management(outTIFF, inputColormap, "")
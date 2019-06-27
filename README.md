The python scripts provided here downloads OMNI data from the NASA ftp website (ftp://cdaweb.gsfc.nasa.gov/pub/data/omni/), compiles the data for all the years, and provides a single netCDF file as output.

From the OMNI documentation:

" 	The /data/omni/low_res_omni/ directory contains the hourly mean values of
	the interplanetary magnetic  field (IMF) and solar wind plasma parameters
	measured by various spacecraft near  the  Earth's  orbit,  as  well  as  
	geomagnetic and solar activity indices, and energetic proton fluxes
	known as OMNI2 data. "


 "  This directory (ftp://spdf.gsfc.nasa.gov/pub/data/omni/high_res_omni/) provides access to high resolution OMNI (HRO)
	data at 1-min and 5-min resolution and to related 1-min
	resolution spacecraft-specific data sets.  The latter consist of
	ACE, Wind and IMP 8 field and plasma data sets shifted to
	the bow shock nose, initially for 1995-2006, by a specific
	combination of Minimum Variance and Cross Product techniques.  
	The latter also consists of 1998-2000 ACE data shifted to Wind
	by each of four techniques.  "

### Dependencies:

This code depends on the `wget` and `netCDF4` python libraries to work properly. Pip install them from the terminal if missing:

```
> pip install wget
> pip install netCDF4
```

### Function call:
```
> import gof
> gof.generateOmniFile(startYear = 1995, endYear = 2005, resolution = "high", outputFile= "myOutputFile.nc")
```
The above call will generate a netCDF file named ```myOutputFile.nc``` containing high resolution OMNI data between years 1995 and 2005.

### Default parameters:
The function definition provides default values used when the function is called with no parameters passed:
```
generateOmniFile(startYear=1963, endYear=datetime.datetime.now().year, resolution='low', outputFile='defaultOutput')
```
Therefore, the call
```
gof.generateOmniFile()
```
will produce a file named containing low resolution OMNI data from 1963 to the current year. The file will be named ```'OMNI_1963_<currentYear>_low_resolution.nc'```.

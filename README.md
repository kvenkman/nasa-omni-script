The python scripts provided here downloads OMNI data from the NASA ftp website (ftp://cdaweb.gsfc.nasa.gov/pub/data/omni/), compiles the data for all the years, and provides a single netCDF file as output.

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
The above call will generate a netCDF file named ```myOutputFile.nc``` containing high resolution (5 minute) OMNI data between years 1995 and 2005.

### Default parameters:
The function definition provides default values that are used when the function is called with one or more parameters missing:
```
generateOmniFile(startYear=1963, endYear=datetime.datetime.now().year, resolution='low', hroRes = '5',
modFlag=False, outputFile='defaultOutput', writeOutput=True, cleanUp=True)
```
Therefore, the call
```
gof.generateOmniFile()
```
will produce a file named ```'OMNI_1963_<currentYear>_low_resolution.nc'``` containing unmodified low resolution OMNI data from 1963 to the current year. The ```modFlag``` keyword allows the user to switch between the original and derived low resolution OMNI data products. This keyword is ignored when the ```resolution``` keyword is set to ```high```. Similarly, the ```hroRes``` allows users to switch between 1 and 5 minute high resolution OMNI data, and the keyword is ignored when the ```resolution``` is set to ```low```. More information regarding the low and high resolution OMNI data and their sub-flavours can be found in the appropriate READMEs available in this repository.

The ```cleanUp``` keyword may be set to ```False``` if the user wishes to retain the raw data files downloaded by the script. These will be stored in the ```./~tmp``` folder, created by the script in the same folder where it is located. *If the folder previously exists, its contents are first wiped*.

The ```writeOutput``` keyword was added for users who may want to download the OMNI data using this script but not want a netCDF file to be generated. Setting both ```writeOutput``` and ```cleanUp``` to ```False``` will allow users to do this.


### OMNI documentation:

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

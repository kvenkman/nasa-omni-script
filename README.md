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
	
### Function call: 

download_omni_data(year_start = "", year_end = "", resolution = "high", output_filename="")

Editing to test a pull

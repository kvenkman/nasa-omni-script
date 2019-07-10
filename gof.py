import wget
from netCDF4 import Dataset
import datetime
import os
import numpy as np
import glob

# Main function
def generateOmniFile(startYear=1963, endYear=datetime.datetime.now().year, resolution='low', hroRes = '5', modFlag=False, outputFile='defaultOutput', writeOutput=True, cleanUp=True):
    # Sanitizing the inputs a bit
    if(startYear>endYear):
        startYear, endYear = endYear, startYear
        print("Setting startYear, endYear to {}, {}".format(startYear, endYear))
    if(startYear<1963):
        print("Start year cannot be less than 1963. Setting startYear to 1963")
        startYear = 1963
    if(endYear>datetime.datetime.now().year):
        print("End year cannot be greater than current year. Setting endYear to currentYear")
        startYear = datetime.datetime.now().year
    if((resolution != 'low' ) and (resolution != 'high')):
        print("resolution keyword has to be set to low/high. setting to low.")
        resolution = "low"
    if((resolution == 'high') and ((hroRes != '5') and (hroRes != '1'))):
        print("For high resolution OMNI data, hroRes keyword has to be either 1 or 5 minutes. Setting to 5 minutes.")
        hroRes = 5
    if((resolution == 'low') and ((modFlag != True) and (modFlag != False))):
        print("For low resolution OMNI data, modFlag keyword has to be either True or False. Setting to False.")
        modFlag = False
    if((writeOutput != True) and (writeOutput != False)):
        print("writeOutput must be either True/False. Setting to True")
        writeOutput = True

    # Done squaring away the inputs. Lets get started.
    serverAddress='ftp://cdaweb.gsfc.nasa.gov/'

    if(resolution == 'low'):
        omniDataPath = 'pub/data/omni/low_res_omni/'
        filePrefix = 'omni2_' if(modFlag == 'False') else 'omni_m'
        fileSuffix = '.dat'
        hroRes = ''

    if(resolution == 'high'):
        omniDataPath = 'pub/data/omni/high_res_omni/'
        filePrefix = 'omni_5min' if(hroRes == '5') else 'omni_min'
        fileSuffix = '.asc'
        hroRes = '_5min' if(hroRes == '5') else '_1min'

    # Because when the code breaks, it does not return to the root directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Create temporary directory and chdir into it, to download files
    if(not os.path.isdir('~tmp')):
        os.system('mkdir ~tmp')

    os.chdir('~tmp')
    oldFiles = glob.glob('*.dat')
    if(len(oldFiles) != 0):
        os.system('rm *.dat') # Wipe clean in case there are previously existing files there

    # Setting output filename
    if(outputFile == 'defaultOutput'):
        outputFile = 'OMNI_'+str(startYear)+"_"+str(endYear)+"_"+resolution+hroRes+'_resolution.nc'

    # Download all the needed files
    print("Downloading requested data .. \n")
    for i in range(startYear, endYear+1):
        tmpFilename = filePrefix+str(i)+fileSuffix
        print("\nGetting file {}\n".format(tmpFilename))
        file = wget.download(serverAddress+omniDataPath+tmpFilename, out=tmpFilename)
    print("\nDownload complete")

    if(writeOutput):
        # Process the files
        print("Beginning processing of data")

        if(resolution == 'low'):
            if(modFlag == True):
                file_description = ""
                lowResModOMNI(outputFile)
            else:
                lowResOMNI(outputFile)
        else:
            highResOMNI(outputFile)


        print("Processing complete")

        os.chdir('..')
        os.system('mv ~tmp/'+outputFile+' .')

    # Clean up
    if(cleanUp):
        print("Cleaning up")
        os.system('rm -rf ~tmp')

    if(writeOutput):
        print("Success! Output filename: "+outputFile+"\n")
    else:
        print("Success!")

##
## End of main function
##

# Functions to help process the downloaded OMNI dataset

# Function to process low resolution OMNI data
def lowResOMNI(outputFile):
    print("Processing low resolution OMNI files .. \n ")

    # Open a new netCDF file
    fileid = Dataset(outputFile, 'w', format='NETCDF4')

    # Create variable dimensions
    # The only dimension here will be time, and it will be unlimited in length
    time = fileid.createDimension('time', None)

    # fileid.createVariable('name', format, (dimensions))
    #altitudes = fileid.createVariable('altitude', np.float32, ('index',))
    year = fileid.createVariable('year', "u4", ('time', ))
    day = fileid.createVariable('day', 'u4', ('time', ))
    hour = fileid.createVariable('hour', 'u4', ('time', ))
    brn = fileid.createVariable('brn', 'u8', ('time', ))
    imf_sc_id = fileid.createVariable('imf_sc_id', 'u4', ('time', ))

    swplasma_sc_id = fileid.createVariable('swplasma_sc_id', 'u4', ('time', ))
    npts_imf_avg = fileid.createVariable('npts_imf_avg', 'u8', ('time', ))
    npts_plasma_avg = fileid.createVariable('npts_plasma_avg', 'u8', ('time', ))
    avg_B = fileid.createVariable('avg_B', 'f8', ('time', ))
    avg_B_vec = fileid.createVariable('avg_B_vec', 'f8', ('time', ))

    lat_avg_B_vec = fileid.createVariable('lat_avg_B_vec', 'f8', ('time', ))
    lon_avg_B_vec = fileid.createVariable('lon_avg_B_vec', 'f8', ('time', ))
    bx = fileid.createVariable('bx', 'f8', ('time', ))
    by_gse = fileid.createVariable('by_gse', 'f8', ('time', ))
    bz_gse = fileid.createVariable('bz_gse', 'f8', ('time', ))

    by_gsm = fileid.createVariable('by_gsm', 'f8',('time', ))
    bz_gsm = fileid.createVariable('bz_gsm', 'f8',('time', ))
    sigma_mag_b = fileid.createVariable('sigma_mag_b', 'f8',('time', ))
    sigma_b = fileid.createVariable('sigma_b', 'f8',('time', ))
    sigma_bx = fileid.createVariable('sigma_bx', 'f8',('time', ))

    sigma_by = fileid.createVariable('sigma_by', 'f8',('time', ))
    sigma_bz = fileid.createVariable('sigma_bz', 'f8',('time', ))
    proton_temp = fileid.createVariable('proton_temp', 'f8',('time', ))
    proton_den = fileid.createVariable('proton_den', 'f8',('time', ))
    plasma_speed = fileid.createVariable('plasma_speed', 'f8',('time', ))

    flow_lon_angle = fileid.createVariable('flow_lon_angle', 'f8',('time', ))
    flow_lat_angle = fileid.createVariable('flow_lat_angle', 'f8',('time', ))
    ap_ratio = fileid.createVariable('ap_ratio', 'f8',('time', ))
    flow_prsr = fileid.createVariable('flow_prsr', 'f8',('time', ))
    sigma_t = fileid.createVariable('sigma_t', 'f8',('time', ))

    sigma_n = fileid.createVariable('sigma_n', 'f8',('time', ))
    sigma_v = fileid.createVariable('sigma_v', 'f8',('time', ))
    sigma_phi_v = fileid.createVariable('sigma_phi_v', 'f8',('time', ))
    sigma_theta_v = fileid.createVariable('sigma_theta_v', 'f8',('time', ))
    sigma_ap = fileid.createVariable('sigma_ap', 'f8',('time', ))

    efield = fileid.createVariable('efield', 'f8',('time', ))
    plasma_beta = fileid.createVariable('plasma_beta', 'f8',('time', ))
    alfven_mach = fileid.createVariable('alfven_mach', 'f8',('time', ))
    kp = fileid.createVariable('kp', 'u4', ('time', ))
    ssn = fileid.createVariable('ssn', 'u4', ('time', ))

    dst = fileid.createVariable('dst', 'u8', ('time', ))
    ae = fileid.createVariable('ae', 'u8', ('time', ))
    pflux1 = fileid.createVariable('pflux1', 'f8', ('time', ))
    pflux2 = fileid.createVariable('pflux2', 'f8',('time', ))
    pflux3 = fileid.createVariable('pflux3', 'f8',('time', ))

    pflux4 = fileid.createVariable('pflux4', 'f8',('time', ))
    pflux5 = fileid.createVariable('pflux5', 'f8',('time', ))
    pflux6 = fileid.createVariable('pflux6', 'f8',('time', ))
    flag = fileid.createVariable('flag', 'u4', ('time', ))
    ap = fileid.createVariable('ap', 'u4', ('time', ))

    f107 = fileid.createVariable('f107', 'f4',('time', ))
    pcn_index = fileid.createVariable('pcn_index', 'f8', ('time', ))
    al_index = fileid.createVariable('al_index', 'u8', ('time', ))
    au_index = fileid.createVariable('au_index', 'u8', ('time', ))
    ms_mach = fileid.createVariable('ms_mach', 'f8', ('time', ))

    files = glob.glob('*')
    print(files)

    fileid.close()


# Function to process low resolution OMNI data
def lowResModOMNI(outputFile):
    print("Processing low resolution modified OMNI files .. \n")
    fileid = Dataset(outputFile, 'w', format='NETCDF3_CLASSIC')

def highResOMNI(outputFile):
    print("Processing high resolution OMNI files .. \n")
    fileid = Dataset(outputFile, 'w', format='NETCDF3_CLASSIC')

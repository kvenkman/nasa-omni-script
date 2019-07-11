import wget
from netCDF4 import Dataset
import datetime
import os
import numpy as np
import glob
import time

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
        filePrefix = 'omni2_' if(modFlag == False) else 'omni_m'
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

    start_time = time.time()
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

    print("Time elapsed: {}".format(time.time()-start_time))
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
    year.description = "Year"
    year.units = "1963, 1964, etc."

    day = fileid.createVariable('day', 'u4', ('time', ))
    day.description = "Decimal Day"
    day.units = "0, 1,...,23"

    hour = fileid.createVariable('hour', 'u4', ('time', ))
    hour.description = "Hour"
    hour.units = "0, 1, 2, .. 23"

    brn = fileid.createVariable('brn', 'u8', ('time', ))
    brn.description = "Bartels rotation number"
    brn.units = ""

    imf_sc_id = fileid.createVariable('imf_sc_id', 'u4', ('time', ))
    imf_sc_id.description = "ID for IMF spacecraft"
    imf_sc_id.units = ""

    swplasma_sc_id = fileid.createVariable('swplasma_sc_id', 'u4', ('time', ))
    swplasma_sc_id.description = "ID for SW plasma spacecraft"
    swplasma_sc_id.units = ""

    npts_imf_avg = fileid.createVariable('npts_imf_avg', 'u8', ('time', ))
    npts_imf_avg.description = "# of points in the IMF averages"
    npts_imf_avg.units = ""

    npts_plasma_avg = fileid.createVariable('npts_plasma_avg', 'u8', ('time', ))
    npts_plasma_avg.description = "# of points in the plasma averages"
    npts_plasma_avg.units = ""

    avg_B = fileid.createVariable('avg_B', 'f8', ('time', ))
    avg_B.description = "Field Magnitude Average |B|  1/N SUM |B|"
    avg_B.units = "nT"

    avg_B_vec = fileid.createVariable('avg_B_vec', 'f8', ('time', ))
    avg_B_vec.description = "Magnitude of Average Field Vector sqrt(Bx^2+By^2+Bz^2) "
    avg_B_vec.units = "nT"

    lat_avg_B_vec = fileid.createVariable('lat_avg_B_vec', 'f8', ('time', ))
    lat_avg_B_vec.description = "Lat.Angle of Aver. Field Vector"
    lat_avg_B_vec.units = "Degrees (GSE coords) "

    lon_avg_B_vec = fileid.createVariable('lon_avg_B_vec', 'f8', ('time', ))
    lon_avg_B_vec.description = "Long.Angle of Aver.Field Vector"
    lon_avg_B_vec.units = "Degrees (GSE coords) "

    bx = fileid.createVariable('bx', 'f8', ('time', ))
    bx.description = "Bx GSE, GSM"
    bx.units = "nT"

    by_gse = fileid.createVariable('by_gse', 'f8', ('time', ))
    by_gse.description = "By GSE"
    by_gse.units = "nT"

    bz_gse = fileid.createVariable('bz_gse', 'f8', ('time', ))
    bz_gse.description = "Bz GSE"
    bz_gse.units = "nT"

    by_gsm = fileid.createVariable('by_gsm', 'f8',('time', ))
    by_gsm.description = "By GSM"
    by_gsm.units = "nT"

    bz_gsm = fileid.createVariable('bz_gsm', 'f8',('time', ))
    bz_gsm.description = "Bz GSM"
    bz_gsm.units = "nT"

    sigma_mag_b = fileid.createVariable('sigma_mag_b', 'f8',('time', ))
    sigma_mag_b.description = "sigma|B|  RMS Standard Deviation in average magnitude"
    sigma_mag_b.units = "nT"

    sigma_b = fileid.createVariable('sigma_b', 'f8',('time', ))
    sigma_b.description = "sigma B RMS Standard Deviation in field vector"
    sigma_b.units = "nT"

    sigma_bx = fileid.createVariable('sigma_bx', 'f8',('time', ))
    sigma_bx.description = "sigma Bx"
    sigma_bx.units = "nT"

    sigma_by = fileid.createVariable('sigma_by', 'f8',('time', ))
    sigma_by.description = "sigma By"
    sigma_by.units = "nT"

    sigma_bz = fileid.createVariable('sigma_bz', 'f8',('time', ))
    sigma_bz.description = "sigma Bz"
    sigma_bz.units = "nT"

    proton_temp = fileid.createVariable('proton_temp', 'f8',('time', ))
    proton_temp.description = "Proton temperature"
    proton_temp.units = "Degrees, K"

    proton_den = fileid.createVariable('proton_den', 'f8',('time', ))
    proton_den.description = "Proton density"
    proton_den.units = "N/cm^3"

    plasma_speed = fileid.createVariable('plasma_speed', 'f8',('time', ))
    plasma_speed.description = "Plasma (Flow) speed"
    plasma_speed.units = "km/s"

    flow_lon_angle = fileid.createVariable('flow_lon_angle', 'f8',('time', ))
    flow_lon_angle.description = "Plasma Flow Long. Angle"
    flow_lon_angle.units = "Degrees, quasi-GSE (ref original OMNI notes)"

    flow_lat_angle = fileid.createVariable('flow_lat_angle', 'f8',('time', ))
    flow_lat_angle.description = "Plasma Flow Lat. Angle"
    flow_lat_angle.units = "Degrees, quasi-GSE (ref original OMNI notes)"

    ap_ratio = fileid.createVariable('ap_ratio', 'f8',('time', ))
    ap_ratio.description = "Na/Np Alpha/Proton ratio"
    ap_ratio.units = ""

    flow_prsr = fileid.createVariable('flow_prsr', 'f8',('time', ))
    flow_prsr.description = "Flow Pressure P (nPa) = (1.67/10**6) * Np*V**2 * (1+ 4*Na/Np) \n for hours with non-fill Na/Np ratios and \n P (nPa) = (2.0/10**6) * Np*V**2 \n for hours with fill values for Na/Np"
    flow_prsr.units = "nPa"

    sigma_t = fileid.createVariable('sigma_t', 'f8',('time', ))
    sigma_t.description =  "sigma T"
    sigma_t.units = "Degrees, K"

    sigma_n = fileid.createVariable('sigma_n', 'f8',('time', ))
    sigma_n.description = "sigma N"
    sigma_n.units = "N/cm^3"

    sigma_v = fileid.createVariable('sigma_v', 'f8',('time', ))
    sigma_v.description = "sigma V"
    sigma_v.units = "km/s"

    sigma_phi_v = fileid.createVariable('sigma_phi_v', 'f8',('time', ))
    sigma_phi_v.description = "sigma phi V"
    sigma_phi_v.units = "Degrees"

    sigma_theta_v = fileid.createVariable('sigma_theta_v', 'f8',('time', ))
    sigma_theta_v.description = "sigma theta V"
    sigma_theta_v.units = "Degrees"

    sigma_ap = fileid.createVariable('sigma_ap', 'f8',('time', ))
    sigma_ap.description = "sigma-Na/Np"
    sigma_ap.units = ""

    efield = fileid.createVariable('efield', 'f8',('time', ))
    efield.description = "Electric field -[V(km/s) * Bz (nT; GSM)] * 10**-3"
    efield.units = "(mV/m)"

    plasma_beta = fileid.createVariable('plasma_beta', 'f8',('time', ))
    plasma_beta.description = "Plasma beta            Beta = [(T*4.16/10**5) + 5.34] * Np / B**2"
    plasma_beta.units = ""

    alfven_mach = fileid.createVariable('alfven_mach', 'f8',('time', ))
    alfven_mach.description = "Alfven mach number      Ma = (V * Np**0.5) / 20 * B"
    alfven_mach.units = ""

    kp = fileid.createVariable('kp', 'u4', ('time', ))
    kp.description = "Kp Planetary Geomagnetic Activity Index"
    kp.units = "(e.g. 3+ = 33, 6- = 57, 4 = 40, etc.)"

    ssn = fileid.createVariable('ssn', 'u4', ('time', ))
    ssn.description = "Sunspot number (new version 2)"
    ssn.units = ""

    dst = fileid.createVariable('dst', 'u8', ('time', ))
    dst.description = "DST Index  from Kyoto "
    dst.units = " nT "

    ae = fileid.createVariable('ae', 'u8', ('time', ))
    ae.description = "AE-index from Kyoto"
    ae.units = " nT "

    pflux1 = fileid.createVariable('pflux1', 'f8', ('time', ))
    pflux1.description = "Proton flux"
    pflux1.units = "number/cmsq sec sr >1 Mev "

    pflux2 = fileid.createVariable('pflux2', 'f8',('time', ))
    pflux2.description = "Proton flux"
    pflux2.units = "number/cmsq sec sr >2 Mev "

    pflux3 = fileid.createVariable('pflux3', 'f8',('time', ))
    pflux3.description = "Proton flux"
    pflux3.units = "number/cmsq sec sr >4 Mev "

    pflux4 = fileid.createVariable('pflux4', 'f8',('time', ))
    pflux4.description = "Proton flux"
    pflux4.units = "number/cmsq sec sr >10 Mev "

    pflux5 = fileid.createVariable('pflux5', 'f8',('time', ))
    pflux5.description = "Proton flux"
    pflux5.units = "number/cmsq sec sr >30 Mev "

    pflux6 = fileid.createVariable('pflux6', 'f8',('time', ))
    pflux6.description = "Proton flux"
    pflux6.units = "number/cmsq sec sr >60 Mev "

    flag = fileid.createVariable('flag', 'intc', ('time', ))
    flag.description = "Flag(***)   (-1,0,1,2,3,4,5,6)"
    flag.units = ""

    ap = fileid.createVariable('ap', 'u4', ('time', ))
    ap.description = "ap-index"
    ap.units = "nT"

    f107 = fileid.createVariable('f107', 'f4',('time', ))
    f107.description = "f10.7_index"
    f107.units = "sfu = 10-22W.m-2.Hz-1"

    pcn_index = fileid.createVariable('pcn_index', 'f8', ('time', ))
    pcn_index.description = "PC(N) index"
    pcn_index.units = ""

    al_index = fileid.createVariable('al_index', 'u8', ('time', ))
    al_index.description = "AL-index, from Kyoto"
    al_index.units = "nT"

    au_index = fileid.createVariable('au_index', 'u8', ('time', ))
    au_index.description = "AL-index, from Kyoto"
    au_index.units = "nT"

    ms_mach = fileid.createVariable('ms_mach', 'f8', ('time', ))
    ms_mach.description = "Magnetosonic mach number= = V/Magnetosonic_speed Magnetosonic speed = [(sound speed)**2 + (Alfv speed)**2]**0.5 The Alfven speed = 20. * B / N**0.5 The sound speed = 0.12 * [T + 1.28*10**5]**0.5"
    ms_mach.units = ""

    # To parse all .dat files available in ~tmp
    files = glob.glob('*.dat')

    # Initialize a dummy variable to append rows to
    all_lines = np.zeros((1, 55))

    for file in files:
        with open(file, 'r') as fhandle:
            lines = fhandle.readlines()

        for line in lines:
            lineFields = line.split()
            all_lines = np.vstack([all_lines, lineFields])

    year[:] = all_lines[1:, 0].astype(np.uintc)
    day[:] = all_lines[1:, 1].astype(np.uintc)
    hour[:] = all_lines[1:, 2].astype(np.uintc)
    brn[:] = all_lines[1:, 3].astype(np.uint)
    imf_sc_id[:] = all_lines[1:, 4].astype(np.uintc)

    swplasma_sc_id[:] = all_lines[1:, 5].astype(np.uintc)
    npts_imf_avg[:] = all_lines[1:, 6].astype(np.uint)
    npts_plasma_avg[:] = all_lines[1:, 7].astype(np.uintc)
    avg_B[:] = all_lines[1:, 8].astype(np.double)
    avg_B_vec[:] = all_lines[1:, 9].astype(np.double)

    lat_avg_B_vec[:] = all_lines[1:, 10].astype(np.double)
    lon_avg_B_vec[:] = all_lines[1:, 11].astype(np.double)
    bx[:] = all_lines[1:, 12].astype(np.double)
    by_gse[:] = all_lines[1:, 13].astype(np.double)
    bz_gse[:] = all_lines[1:, 14].astype(np.double)

    by_gsm[:] = all_lines[1:, 15].astype(np.double)
    bz_gsm[:] = all_lines[1:, 16].astype(np.double)
    sigma_mag_b[:] = all_lines[1:, 17].astype(np.double)
    sigma_b[:] = all_lines[1:, 18].astype(np.double)
    sigma_bx[:] = all_lines[1:, 19].astype(np.double)

    sigma_by[:] = all_lines[1:, 20].astype(np.double)
    sigma_bz[:] = all_lines[1:, 21].astype(np.double)
    proton_temp[:] = all_lines[1:, 22].astype(np.double)
    proton_den[:] = all_lines[1:, 23].astype(np.double)
    plasma_speed[:] = all_lines[1:, 24].astype(np.double)

    flow_lon_angle[:] = all_lines[1:, 25].astype(np.double)
    flow_lat_angle[:] = all_lines[1:, 26].astype(np.double)
    ap_ratio[:] = all_lines[1:, 27].astype(np.double)
    flow_prsr[:] = all_lines[1:, 28].astype(np.double)
    sigma_t[:] = all_lines[1:, 29].astype(np.double)

    sigma_n[:] = all_lines[1:, 30].astype(np.double)
    sigma_v[:] = all_lines[1:, 31].astype(np.double)
    sigma_phi_v[:] = all_lines[1:, 32].astype(np.double)
    sigma_theta_v[:] = all_lines[1:, 33].astype(np.double)
    sigma_ap[:] = all_lines[1:, 34].astype(np.double)

    efield[:] = all_lines[1:, 35].astype(np.double)
    plasma_beta[:] = all_lines[1:, 36].astype(np.double)
    alfven_mach[:] = all_lines[1:, 37].astype(np.double)
    kp[:] = all_lines[1:, 38].astype(np.uintc)
    ssn[:] = all_lines[1:, 39].astype(np.uintc)

    dst[:] = all_lines[1:, 40].astype(np.uint)
    ae[:] = all_lines[1:, 41].astype(np.uint)
    pflux1[:] = all_lines[1:, 42].astype(np.double)
    pflux2[:] = all_lines[1:, 43].astype(np.double)
    pflux3[:] = all_lines[1:, 44].astype(np.double)

    pflux4[:] = all_lines[1:, 45].astype(np.double)
    pflux5[:] = all_lines[1:, 46].astype(np.double)
    pflux6[:] = all_lines[1:, 47].astype(np.double)
    flag[:] = all_lines[1:, 48].astype(np.uintc)
    ap[:] = all_lines[1:, 49].astype(np.uintc)

    f107[:] = all_lines[1:, 50].astype(np.float32)
    pcn_index[:] = all_lines[1:, 51].astype(np.double)
    al_index[:] = all_lines[1:, 52].astype(np.uint)
    au_index[:] = all_lines[1:, 53].astype(np.uint)
    ms_mach[:] = all_lines[1:, 54].astype(np.double)

    fileid.close()


# Function to process low resolution OMNI data
def lowResModOMNI(outputFile):
    print("Processing low resolution modified OMNI files .. \n")
    fileid = Dataset(outputFile, 'w', format='NETCDF3_CLASSIC')

def highResOMNI(outputFile):
    print("Processing high resolution OMNI files .. \n")
    fileid = Dataset(outputFile, 'w', format='NETCDF3_CLASSIC')

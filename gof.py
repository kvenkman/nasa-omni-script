import wget
from netCDF4 import Dataset
import datetime
import os
import numpy as np
import glob
import time

# Main function
def generateOmniFile(startYear=1963, endYear=datetime.datetime.now().year, resolution='low', hroRes = 5, modFlag=False, outputFile='defaultOutput', writeOutput=True, cleanUp=True):
    # Sanitizing the inputs a bit
    resolution = resolution.lower()
    hroRes = str(hroRes)

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
        hroResSuffix = ''

    if(resolution == 'high'):
        omniDataPath = 'pub/data/omni/high_res_omni/'
        filePrefix = 'omni_5min' if(hroRes == '5') else 'omni_min'
        fileSuffix = '.asc'
        hroResSuffix = '_5min' if(hroRes == '5') else '_1min'

    # Because when the code breaks, it does not return to the root directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Create temporary directory and chdir into it, to download files
    if(not os.path.isdir('~tmp')):
        os.system('mkdir ~tmp')

    # Setting output filename
    if(outputFile == 'defaultOutput'):
        modified = "m" if (modFlag == True) else ""
        outputFile = 'OMNI_'+str(startYear)+"_"+str(endYear)+modified+"_"+resolution+hroResSuffix+'_resolution.nc'

    os.chdir('~tmp')

    oldFiles = glob.glob('*.dat') + glob.glob('*.asc')
    if(len(oldFiles) != 0):
        os.system('rm *.dat *.asc') # Wipe clean in case there are previously existing files there

    # Download all the needed files
    print("Downloading requested data .. \n")
    for i in range(startYear, endYear+1):
        tmpFilename = filePrefix+str(i)+fileSuffix
        print("\nGetting file {}\n".format(tmpFilename))
        if(resolution=='low'):
            file = wget.download(serverAddress+omniDataPath+tmpFilename, out=str(i)+'.dat')
        else:
            file = wget.download(serverAddress+omniDataPath+tmpFilename, out=str(i)+'.asc')

    print("\nDownload complete")

    start_time = time.time()
    if(writeOutput):
        # Process the files
        print("Beginning processing of data")

        if(resolution == 'low'):
            if(modFlag == True):
                lowResModOMNI(outputFile)
            else:
                lowResOMNI(outputFile)
        else:
            highResOMNI(outputFile, hroRes)


        print("Processing complete")

        os.chdir('..')
        os.system('mv ~tmp/'+outputFile+' .')

    print("Time elapsed: {} seconds".format(time.time()-start_time))
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

    # Creating the needed variables
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
    files = sorted(glob.glob('*.dat'))

    # Initialize counter
    count = 0

    for file in files:
        with open(file, 'r') as fhandle:
            lines = fhandle.readlines()

        if(count == 0):
            all_lines = np.zeros((len(lines), 55))
        else:
            all_lines = np.vstack([all_lines, np.zeros((len(lines), 55))])

        for line in lines:
            all_lines[count, :] = line.split()
            count += 1

    year[:] = all_lines[:, 0].astype(np.uintc)
    day[:] = all_lines[:, 1].astype(np.uintc)
    hour[:] = all_lines[:, 2].astype(np.uintc)
    brn[:] = all_lines[:, 3].astype(np.uint)
    imf_sc_id[:] = all_lines[:, 4].astype(np.uintc)

    swplasma_sc_id[:] = all_lines[:, 5].astype(np.uintc)
    npts_imf_avg[:] = all_lines[:, 6].astype(np.uint)
    npts_plasma_avg[:] = all_lines[:, 7].astype(np.uintc)
    avg_B[:] = all_lines[:, 8].astype(np.double)
    avg_B_vec[:] = all_lines[:, 9].astype(np.double)

    lat_avg_B_vec[:] = all_lines[:, 10].astype(np.double)
    lon_avg_B_vec[:] = all_lines[:, 11].astype(np.double)
    bx[:] = all_lines[:, 12].astype(np.double)
    by_gse[:] = all_lines[:, 13].astype(np.double)
    bz_gse[:] = all_lines[:, 14].astype(np.double)

    by_gsm[:] = all_lines[:, 15].astype(np.double)
    bz_gsm[:] = all_lines[:, 16].astype(np.double)
    sigma_mag_b[:] = all_lines[:, 17].astype(np.double)
    sigma_b[:] = all_lines[:, 18].astype(np.double)
    sigma_bx[:] = all_lines[:, 19].astype(np.double)

    sigma_by[:] = all_lines[:, 20].astype(np.double)
    sigma_bz[:] = all_lines[:, 21].astype(np.double)
    proton_temp[:] = all_lines[:, 22].astype(np.double)
    proton_den[:] = all_lines[:, 23].astype(np.double)
    plasma_speed[:] = all_lines[:, 24].astype(np.double)

    flow_lon_angle[:] = all_lines[:, 25].astype(np.double)
    flow_lat_angle[:] = all_lines[:, 26].astype(np.double)
    ap_ratio[:] = all_lines[:, 27].astype(np.double)
    flow_prsr[:] = all_lines[:, 28].astype(np.double)
    sigma_t[:] = all_lines[:, 29].astype(np.double)

    sigma_n[:] = all_lines[:, 30].astype(np.double)
    sigma_v[:] = all_lines[:, 31].astype(np.double)
    sigma_phi_v[:] = all_lines[:, 32].astype(np.double)
    sigma_theta_v[:] = all_lines[:, 33].astype(np.double)
    sigma_ap[:] = all_lines[:, 34].astype(np.double)

    efield[:] = all_lines[:, 35].astype(np.double)
    plasma_beta[:] = all_lines[:, 36].astype(np.double)
    alfven_mach[:] = all_lines[:, 37].astype(np.double)
    kp[:] = all_lines[:, 38].astype(np.uintc)
    ssn[:] = all_lines[:, 39].astype(np.uintc)

    dst[:] = all_lines[:, 40].astype(np.uint)
    ae[:] = all_lines[:, 41].astype(np.uint)
    pflux1[:] = all_lines[:, 42].astype(np.double)
    pflux2[:] = all_lines[:, 43].astype(np.double)
    pflux3[:] = all_lines[:, 44].astype(np.double)

    pflux4[:] = all_lines[:, 45].astype(np.double)
    pflux5[:] = all_lines[:, 46].astype(np.double)
    pflux6[:] = all_lines[:, 47].astype(np.double)
    flag[:] = all_lines[:, 48].astype(np.uintc)
    ap[:] = all_lines[:, 49].astype(np.uintc)

    f107[:] = all_lines[:, 50].astype(np.float32)
    pcn_index[:] = all_lines[:, 51].astype(np.double)
    al_index[:] = all_lines[:, 52].astype(np.uint)
    au_index[:] = all_lines[:, 53].astype(np.uint)
    ms_mach[:] = all_lines[:, 54].astype(np.double)

    fileid.close()


# Function to process low resolution OMNI data
def lowResModOMNI(outputFile):
    print("Processing low resolution modified OMNI files .. \n")

    # Open a new netCDF file
    fileid = Dataset(outputFile, 'w', format='NETCDF4')

    # Create variable dimensions
    # The only dimension here will be time, and it will be unlimited in length
    time = fileid.createDimension('time', None)

    # Creating the needed variables
    year = fileid.createVariable('year', "u4", ('time', ))
    year.description = "Year"
    year.units = "1963, 1964, etc."

    day = fileid.createVariable('day', 'u4', ('time', ))
    day.description = "Decimal Day"
    day.units = "0, 1,...,23"

    hour = fileid.createVariable('hour', 'u4', ('time', ))
    hour.description = "Hour"
    hour.units = "0, 1, 2, .. 23"

    helio_ilat = fileid.createVariable('helio_ilat', 'f8',('time', ))
    helio_ilat.description = "Heliographic Inertial Latitude of the Earth"
    helio_ilat.units = "Degrees"

    helio_ilon = fileid.createVariable('helio_ilon', 'f8',('time', ))
    helio_ilon.description = "Heliographic Inertial Longitude of the Earth"
    helio_ilon.units = "Degrees"

    br_rtn = fileid.createVariable('br_rtn', 'f8',('time', ))
    br_rtn.description = "BR RTN"
    br_rtn.units = "nT"

    bt_rtn = fileid.createVariable('bt_rtn', 'f8',('time', ))
    bt_rtn.description = "BT RTN"
    bt_rtn.units = "nT"

    bn_rtn = fileid.createVariable('bn_rtn', 'f8',('time', ))
    bn_rtn.description = "BN RTN"
    bn_rtn.units = "nT"

    b_avg =  fileid.createVariable('b_avg', 'f8',('time', ))
    b_avg.description = "Field Magnitude Average |B|"
    b_avg.units = "nT"

    flow_speed = fileid.createVariable('flow_speed', 'f8',('time', ))
    flow_speed.description = "Bulk Flow speed"
    flow_speed.units = "km/s"

    theta = fileid.createVariable('theta', 'f8',('time', ))
    theta.description = "THETA - elevation angle  of the velocity vector (RTN)"
    theta.units = "Degrees"

    phi = fileid.createVariable('phi', 'f8',('time', ))
    phi.description = "PHI- azimuth angle of the velocity vector (RTN)"
    phi.units = "Degrees"

    ion_den = fileid.createVariable('ion_den', 'f8',('time', ))
    ion_den.description = " ION Density "
    ion_den.units = "N/cm^3"

    temperature = fileid.createVariable('temperature', 'f8',('time', ))
    temperature.description = "Temperature"
    temperature.units = "Degrees K"

    # To parse all .dat files available in ~tmp
    files = sorted(glob.glob('*.dat'))

    # Initialize counter
    count = 0

    for file in files:
        with open(file, 'r') as fhandle:
            lines = fhandle.readlines()

        if(count == 0):
            all_lines = np.zeros((len(lines), 14))
        else:
            all_lines = np.vstack([all_lines, np.zeros((len(lines), 14))])

        for line in lines:
            all_lines[count, :] = line.split()
            count += 1

    year[:] = all_lines[:, 0].astype(np.uintc)
    day[:] = all_lines[:, 1].astype(np.uintc)
    hour[:] = all_lines[:, 2].astype(np.uintc)
    helio_ilat[:] = all_lines[:, 3].astype(np.double)
    helio_ilon[:] = all_lines[:, 4].astype(np.double)

    br_rtn[:] = all_lines[:, 5].astype(np.double)
    bt_rtn[:] = all_lines[:, 6].astype(np.double)
    bn_rtn[:] = all_lines[:, 7].astype(np.double)
    b_avg[:] = all_lines[:, 8].astype(np.double)
    flow_speed[:] = all_lines[:, 9].astype(np.double)

    theta[:] = all_lines[:, 10].astype(np.double)
    phi[:] = all_lines[:, 11].astype(np.double)
    ion_den[:] = all_lines[:, 12].astype(np.double)
    temperature[:] = all_lines[:, 13].astype(np.double)

    fileid.close()


def highResOMNI(outputFile, hroRes):
    print("Processing high resolution OMNI files .. \n")

    # Open a new netCDF file
    fileid = Dataset(outputFile, 'w', format='NETCDF4')

    # Create variable dimensions
    # The only dimension here will be time, and it will be unlimited in length
    time = fileid.createDimension('time', None)

    # Creating the needed variables
    year = fileid.createVariable('year', "u4", ('time', ))
    year.description = "Year"
    year.units = "1963, 1964, etc."

    day = fileid.createVariable('day', 'u4', ('time', ))
    day.description = "Decimal Day"
    day.units = "0, 1,...,23"

    hour = fileid.createVariable('hour', 'u4', ('time', ))
    hour.description = "Hour"
    hour.units = "0, 1, 2, .. 23"

    minute = fileid.createVariable('minute', 'u4', ('time', ))
    minute.description = "Minute"
    minute.units = "0, 1 ... 59"

    imf_sc_id = fileid.createVariable('imf_sc_id', 'u4', ('time', ))
    imf_sc_id.description = "ID for IMF spacecraft"
    imf_sc_id.units = "ID for IMF spacecraft"

    swplasma_sc_id = fileid.createVariable('swplasma_sc_id', 'u4', ('time', ))
    swplasma_sc_id.description = "ID for SW plasma spacecraft"
    swplasma_sc_id.units = "ID for SW Plasma spacecraft"

    imf_avg_npts = fileid.createVariable('imf_avg_npts', 'u8', ('time', ))
    imf_avg_npts.description = ""
    imf_avg_npts.units = "\# of points in IMF averages	I4"

    plasma_avg_npts = fileid.createVariable('plasma_avg_npts', 'u8', ('time', ))
    plasma_avg_npts.description = "\# of points in Plasma averages"
    plasma_avg_npts.units = ""

    percent_interp = fileid.createVariable('percent_interp', 'u4', ('time', ))
    percent_interp.description = "The percent (0-100) of the points contributing to\
    the 1-min magnetic field averages whose phase front normal (PFN)\
    was interpolated because neither the MVAB-0 nor Cross Product\
    shift techniques yielded a PFN that satisfied its respective tests\
    (see detailed documentation for these)."
    percent_interp.units = ""

    tshift = fileid.createVariable('tshift', 'f8', ('time', ))
    tshift.description = "Timeshift"
    tshift.units = "sec"

    rms_tshift = fileid.createVariable('rms_tshift', 'f8', ('time', ))
    rms_tshift.description = "RMS, Timeshift"
    rms_tshift.units = ""

    rms_pfront = fileid.createVariable('rms_pfront', 'f8', ('time', ))
    rms_pfront.description = "RMS, Phase front normal"
    rms_pfront.units = ""

    delta_t = fileid.createVariable('delta_t', 'f8', ('time', ))
    delta_t.description = ""
    delta_t.units = ""

    avg_B = fileid.createVariable('avg_B', 'f8', ('time', ))
    avg_B.description = "Field Magnitude Average |B|  1/N SUM |B|"
    avg_B.units = "nT"

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

    rms_sd_b = fileid.createVariable('rms_sd_b', 'f8', ('time', ))
    rms_sd_b.description = "RMS SD B scalar"
    rms_sd_b.units = "nT"

    rms_sd_bvector = fileid.createVariable('rms_sd_bvector', 'f8', ('time', ))
    rms_sd_bvector.description = "RMS SD field vector"
    rms_sd_bvector.units = "nT"

    flow_speed = fileid.createVariable('flow_speed', 'f8',('time', ))
    flow_speed.description = "Bulk Flow speed"
    flow_speed.units = "km/s"

    vx = fileid.createVariable('vx', 'f8', ('time', ))
    vx.description = "Vx GSE"
    vx.units = "km/s"

    vy = fileid.createVariable('vy', 'f8', ('time', ))
    vy.description = "Vy GSE"
    vy.units = "km/s"

    vz = fileid.createVariable('vz', 'f8', ('time', ))
    vz.description = "Vz GSE"
    vz.units = "km/s"

    proton_den = fileid.createVariable('proton_den', 'f8',('time', ))
    proton_den.description = "Proton density"
    proton_den.units = "N/cm^3"

    temperature = fileid.createVariable('temperature', 'f8',('time', ))
    temperature.description = "Temperature"
    temperature.units = "Degrees K"

    flow_prsr = fileid.createVariable('flow_prsr', 'f8',('time', ))
    flow_prsr.description = "Flow Pressure P (nPa) = (1.67/10**6) * Np*V**2 * (1+ 4*Na/Np) \n for hours with non-fill Na/Np ratios and \n P (nPa) = (2.0/10**6) * Np*V**2 \n for hours with fill values for Na/Np"
    flow_prsr.units = "nPa"

    efield = fileid.createVariable('efield', 'f8',('time', ))
    efield.description = "Electric field -[V(km/s) * Bz (nT; GSM)] * 10**-3"
    efield.units = "(mV/m)"

    plasma_beta = fileid.createVariable('plasma_beta', 'f8',('time', ))
    plasma_beta.description = "Plasma beta Beta = [(T*4.16/10**5) + 5.34] * Np / B**2"
    plasma_beta.units = ""

    alfven_mach = fileid.createVariable('alfven_mach', 'f8',('time', ))
    alfven_mach.description = "Alfven mach number      Ma = (V * Np**0.5) / 20 * B"
    alfven_mach.units = ""

    scx = fileid.createVariable('scx', 'f8', ('time', ))
    scx.description = "X(s/c) GSE"
    scx.units = "Re"

    scy = fileid.createVariable('scy', 'f8', ('time', ))
    scy.description = "Y(s/c) GSE"
    scy.units = "Re"

    scz = fileid.createVariable('scz', 'f8', ('time', ))
    scz.description = "Z(s/c) GSE"
    scz.units = "Re"

    bsn_loc_xgse = fileid.createVariable('bsn_loc_xgse','f8' , ('time', ))
    bsn_loc_xgse .description = "Bow shock nose (BSN) location X GSE"
    bsn_loc_xgse .units = "Re"

    bsn_loc_ygse = fileid.createVariable('bsn_loc_ygse', 'f8', ('time', ))
    bsn_loc_ygse.description = "Bow shock nose (BSN) location Y GSE"
    bsn_loc_ygse.units = "Re"

    bsn_loc_zgse = fileid.createVariable('bsn_loc_zgse','f8' , ('time', ))
    bsn_loc_zgse.description = "Bow shock nose (BSN) location Z GSE"
    bsn_loc_zgse.units = "Re"

    ae = fileid.createVariable('ae', 'u8', ('time', ))
    ae.description = "AE-index from Kyoto"
    ae.units = " nT "

    al_index = fileid.createVariable('al_index', 'u8', ('time', ))
    al_index.description = "AL-index, from Kyoto"
    al_index.units = "nT"

    au_index = fileid.createVariable('au_index', 'u8', ('time', ))
    au_index.description = "AL-index, from Kyoto"
    au_index.units = "nT"

    sym_d = fileid.createVariable('sym_d', 'u8', ('time', ))
    sym_d.description = "longitudinally  symmetric  (ASY) disturbance  index"
    sym_d.units = ""

    sym_h = fileid.createVariable('sym_h', 'u8', ('time', ))
    sym_h.description = ""
    sym_h.units = "longitudinally  symmetric  (ASY)  disturbance  index horizontal direction"

    asy_d = fileid.createVariable('asy_d', 'u8', ('time', ))
    asy_d.description = "longitudinally  asymmetric  (ASY)  disturbance  index "
    asy_d.units = ""

    asy_h = fileid.createVariable('asy_h','u8' , ('time', ))
    asy_h.description = "longitudinally  asymmetric  (ASY)  disturbance  index horizontal direction"
    asy_h.units = ""

    pcn_index = fileid.createVariable('pcn_index', 'f8', ('time', ))
    pcn_index.description = "PC(N) index"
    pcn_index.units = ""

    ms_mach = fileid.createVariable('ms_mach', 'f8', ('time', ))
    ms_mach.description = "Magnetosonic mach number= = V/Magnetosonic_speed Magnetosonic speed = [(sound speed)**2 + (Alfv speed)**2]**0.5 The Alfven speed = 20. * B / N**0.5 The sound speed = 0.12 * [T + 1.28*10**5]**0.5"
    ms_mach.units = ""


    if(hroRes == '1'):
        all_lines = np.zeros((1, 46))
    else:
        all_lines = np.zeros((1, 49))
        pflux1 = fileid.createVariable('pflux1', 'f8',('time', ))
        pflux1.description = "Proton flux"
        pflux1.units = "number/cmsq sec sr >10 Mev "

        pflux2 = fileid.createVariable('pflux2', 'f8',('time', ))
        pflux2.description = "Proton flux"
        pflux2.units = "number/cmsq sec sr >30 Mev "

        pflux3 = fileid.createVariable('pflux3', 'f8',('time', ))
        pflux3.description = "Proton flux"
        pflux3.units = "number/cmsq sec sr >60 Mev "

    # To parse all .dat files available in ~tmp
    files = sorted(glob.glob('*.asc'))

    # Initialize counter
    count = 0

    for file in files:
        with open(file, 'r') as fhandle:
            lines = fhandle.readlines()

        if(count == 0):
            if(hroRes == '1'):
                all_lines = np.zeros((len(lines), 46))
            else:
                all_lines = np.zeros((len(lines), 49))
        else:
            if(hroRes == '1'):
                all_lines = np.vstack([all_lines, np.zeros((len(lines), 46))])
            else:
                all_lines = np.vstack([all_lines, np.zeros((len(lines), 49))])

        for line in lines:
            all_lines[count, :] = line.split()
            count += 1

    year[:] = all_lines[:, 0].astype(np.uintc)
    day[:] = all_lines[:, 1].astype(np.uintc)
    hour[:] = all_lines[:, 2].astype(np.uintc)
    minute[:] = all_lines[:, 3].astype(np.uintc)
    imf_sc_id[:] = all_lines[:, 4].astype(np.uintc)

    swplasma_sc_id[:] = all_lines[:, 5].astype(np.uintc)
    imf_avg_npts[:] = all_lines[:, 6].astype(np.uintc)
    plasma_avg_npts[:] = all_lines[:, 7].astype(np.uintc)
    percent_interp[:] = all_lines[:, 8].astype(np.uintc)
    tshift[:] = all_lines[:, 9].astype(np.uintc)

    rms_tshift[:] = all_lines[:, 10].astype(np.double)
    rms_pfront[:] = all_lines[:, 11].astype(np.double)
    delta_t[:] = all_lines[:, 12].astype(np.double)
    avg_B[:] = all_lines[:, 13].astype(np.double)
    bx[:] = all_lines[:, 14].astype(np.double)

    by_gse[:] = all_lines[:, 15].astype(np.double)
    bz_gse[:] = all_lines[:, 16].astype(np.double)
    by_gsm[:] = all_lines[:, 17].astype(np.double)
    bz_gsm[:] = all_lines[:, 18].astype(np.double)
    rms_sd_b[:] = all_lines[:, 19].astype(np.double)

    rms_sd_bvector[:] = all_lines[:, 20].astype(np.double)
    flow_speed[:] = all_lines[:, 21].astype(np.double)
    vx[:] = all_lines[:, 22].astype(np.double)
    vy[:] = all_lines[:, 23].astype(np.double)
    vz[:] = all_lines[:, 24].astype(np.double)

    proton_den[:] = all_lines[:, 25].astype(np.double)
    temperature[:] = all_lines[:, 26].astype(np.double)
    flow_prsr[:] = all_lines[:, 27].astype(np.double)
    efield[:] = all_lines[:, 28].astype(np.double)
    plasma_beta[:] = all_lines[:, 29].astype(np.double)

    alfven_mach[:] = all_lines[:, 30].astype(np.double)
    scx[:] = all_lines[:, 31].astype(np.double)
    scy[:] = all_lines[:, 32].astype(np.double)
    scz[:] = all_lines[:, 33].astype(np.double)
    bsn_loc_xgse[:] = all_lines[:, 34].astype(np.double)

    bsn_loc_ygse[:] = all_lines[:, 35].astype(np.double)
    bsn_loc_zgse[:] = all_lines[:, 36].astype(np.double)
    ae[:] = all_lines[:, 37].astype(np.uint)
    al_index[:] = all_lines[:, 38].astype(np.uint)
    au_index[:] = all_lines[:, 39].astype(np.uint)

    sym_d[:] = all_lines[:, 40].astype(np.uint)
    sym_h[:] = all_lines[:, 41].astype(np.uint)
    asy_d[:] = all_lines[:, 42].astype(np.uint)
    asy_h[:] = all_lines[:, 43].astype(np.uint)
    pcn_index[:] = all_lines[:, 44].astype(np.double)

    ms_mach[:] = all_lines[:, 45].astype(np.double)

    if(hroRes == '5'):
        pflux1[:] = all_lines[:, 46].astype(np.double)
        pflux2[:] = all_lines[:, 47].astype(np.double)
        pflux3[:] = all_lines[:, 48].astype(np.double)

    fileid.close()

import wget
import netCDF4
import datetime
import os

def generateOmniFile(startYear=1963, endYear=datetime.datetime.now().year, resolution='low', hroRes = '5', outputFile='defaultOutput'):
    serverAddress='ftp://cdaweb.gsfc.nasa.gov/'

    if(resolution == 'low'):
        omniDataPath = 'pub/data/omni/low_res_omni/' if (resolution == 'low') else 'pub/data/omni/high_res_omni/'
        filePrefix = 'omni2_'
        fileSuffix = '.dat'
        hroRes = ''

    #if(resolution == 'high'):

    # Create temporary directory
    os.system('mkdir ~tmp')
    os.chdir('~tmp')

    if(outputFile == 'defaultOutput'):
        outputFile = 'OMNI_'+str(startYear)+"_"+str(endYear)+"_"+resolution+hroRes+'_resolution.nc'

    # Download all the needed files
    print("Downloading requested data .. ")
    for i in range(startYear, endYear+1):
        tmpFilename = filePrefix+str(i)+fileSuffix
        file = wget.download(serverAddress+omniDataPath+tmpFilename, out=tmpFilename)

    print("\nDownload complete")


    # Process the files
    print("Beginning processing of data")
    # Dummy file write at the moment
    f = open(outputFile, 'w')
    f.close()
    print("Processing complete")

    # Clean up
    print("Cleaning up")
    os.system('mv '+outputFile+' ..')
    os.system('rm *')
    os.chdir('..')
    os.system('rmdir ~tmp')

    print("Complete. Output filename: "+outputFile+"\n")

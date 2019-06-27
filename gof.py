import wget
import netCDF4
import datetime

def generateOmniFile(startYear=1963, endYear=datetime.datetime.now().year, resolution='low', outputFile='defaultOutput'):
    serverAddress='ftp://cdaweb.gsfc.nasa.gov/'

    omniDataPath = 'pub/data/omni/low_res_omni/'
    filename = 'omni2_1963.dat'

    print(startYear, endYear, resolution, filename)

    if(outputFile == 'defaultOutput'):
        outputFile = 'OMNI_'+str(startYear)+"_"+str(endYear)+"_"+resolution+'_resolution.nc'

    print("Before: "+outputFile)
    outputFile = outputFile + '.nc' if (outputFile[-3:] != ".nc") else outputFile
    print(outputFile)

    #file = wget.download(serverAddress+omniDataPath+filename, out=filename)

def helloworld():
    print("Hello World")

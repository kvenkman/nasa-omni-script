import wget
import netCDF4
import datetime
import os

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

    # Create temporary directory and chdir into it, to download files
    if(not os.path.isdir('~tmp')):
        os.system('mkdir ~tmp')

    os.chdir('~tmp')

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
                lowResModOMNI(filename=outputFile)
            else:
                lowResOMNI(filename=outputFile)
        else:
            highResOMNI(filename=outputFile)

        #ncfile = netCDF4.Dataset(outputFile, mode='w', format='NETCDF4_CLASSIC')
        f = open(outputFile, 'w')
        f.close()

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

def lowResModOMNI(filename=outputFile):

def lowResOMNI(filename=outputFile):

def highResOMNI(filename=outputFile):

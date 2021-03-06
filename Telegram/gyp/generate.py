'''
This file is part of Bettergram.

For license and copyright information please follow this link:
https://github.com/bettergram/bettergram/blob/master/LEGAL
'''
import sys, os, re, subprocess

def finish(code):
    global executePath
    os.chdir(executePath)
    sys.exit(code)

if sys.platform == 'win32' and not 'COMSPEC' in os.environ:
    print('[ERROR] COMSPEC environment variable is not set.')
    finish(1)

executePath = os.getcwd()
scriptPath = os.path.dirname(os.path.realpath(__file__))

apiId = ''
apiHash = ''
nextApiId = False
nextApiHash = False
for arg in sys.argv:
    if nextApiId:
        apiId = re.sub(r'[^\d]', '', arg)
        nextApiId = False
    elif nextApiHash:
        apiHash = re.sub(r'[^a-fA-F\d]', '', arg)
        nextApiHash = False
    else:
        nextApiId = (arg == '--api-id')
        nextApiHash = (arg == '--api-hash')

officialTarget = ''
officialTargetFile = scriptPath + '/../build/target'
if os.path.isfile(officialTargetFile):
    with open(officialTargetFile, 'r') as f:
        for line in f:
            officialTarget = line.strip()

if officialTarget != '':
    officialApiIdFile = scriptPath + '/../../../TelegramPrivate/custom_api_id.h'
    if not os.path.isfile(officialApiIdFile):
        print("[ERROR] TelegramPrivate/custom_api_id.h not found.")
        finish(1)
    with open(officialApiIdFile, 'r') as f:
        for line in f:
            apiIdMatch = re.search(r'ApiId\s+=\s+(\d+)', line)
            apiHashMatch = re.search(r'ApiHash\s+=\s+"([a-fA-F\d]+)"', line)
            if apiIdMatch:
                apiId = apiIdMatch.group(1)
            elif apiHashMatch:
                apiHash = apiHashMatch.group(1)

if apiId == '' or apiHash == '':
    print("""[USAGE]: refresh --api-id YOUR_API_ID --api-hash YOUR_API_HASH

> To build your version of Telegram Desktop you're required to provide
> your own 'api_id' and 'api_hash' for the Telegram API access.
> 
> How to obtain your 'api_id' and 'api_hash' is described here:
> https://core.telegram.org/api/obtaining_api_id
> 
> If you're building the application not for deployment,
> but only for test purposes you can use TEST ONLY credentials,
> which are very limited by the Telegram API server:
> 
> api_id: 17349
> api_hash: 344583e45741c457fe1862106095a5eb
> 
> Your users will start getting internal server errors on login
> if you deploy an app using those 'api_id' and 'api_hash'.""")
    finish(0)


BuildTargetGeneralDescription="You can change the build target at the Telegram/build/target file."

MacStoreDescription="""It will make .app directory ready for Apple App Store.
You also need the following files:
* TelegramPrivate/mac_development_team"""

MacDmgDescription="""It will make and sign .app directory and .dmg file.
You also need the following files:
* TelegramPrivate/mac_certificate_identity
* TelegramPrivate/mac_development_team
* TelegramPrivate/BettergramDmg.json
* TelegramPrivate/Bettergram.icns"""

ChangeToMacStoreDescription="""
If you want to deliver the application through the Apple App Store
then just write the following content to the Telegram/build/target file: macstore
""" + MacStoreDescription

ChangeToMacDmgDescription="""
If you want to deliver the application outside the Apple App Store
then just write the following content to the Telegram/build/target file: macdmg
""" + MacDmgDescription

ChangeToEmptyDescription="""
Or If you want just to build the application
then clear the content of the Telegram/build/target file.
To get more information please check the docs/building-xcode.md file."""

if sys.platform == 'darwin':
    if officialTarget != "":
        print('Build target: ' + officialTarget)

    if officialTarget == "macstore":
        print('\n')
        print(MacStoreDescription)
        print('\n')
        print(BuildTargetGeneralDescription)
        print(ChangeToMacDmgDescription)
        print(ChangeToEmptyDescription)
    elif officialTarget == "macdmg":
        print('\n')
        print(MacDmgDescription)
        print('\n')
        print(BuildTargetGeneralDescription)
        print(ChangeToMacStoreDescription)
        print(ChangeToEmptyDescription)
    else:
        print('\n')
        print('At macOS you can build the application for Apple App Store or deliver it though your site.')
        print('\n')
        print(BuildTargetGeneralDescription)
        print(ChangeToMacStoreDescription)
        print(ChangeToMacDmgDescription)
        print(ChangeToEmptyDescription)

gypScript = 'gyp'
gypFormats = []
gypArguments = []
cmakeConfigurations = []
gypArguments.append('--depth=.')
gypArguments.append('--generator-output=..')
gypArguments.append('-Goutput_dir=../out')
gypArguments.append('-Dapi_id=' + apiId)
gypArguments.append('-Dapi_hash=' + apiHash)
gypArguments.append('-Dofficial_build_target=' + officialTarget)
if 'TDESKTOP_BUILD_DEFINES' in os.environ:
    buildDefines = os.environ['TDESKTOP_BUILD_DEFINES']
    gypArguments.append('-Dbuild_defines=' + buildDefines)
    print('[INFO] Set build defines to ' + buildDefines)

if sys.platform == 'win32':
    os.environ['GYP_MSVS_VERSION'] = '2017'
    gypFormats.append('ninja')
    gypFormats.append('msvs-ninja')
elif sys.platform == 'darwin':
    # use patched gyp with Xcode project generator
    gypScript = '../../../Libraries/gyp/gyp'
    gypArguments.append('-Gxcode_upgrade_check_project_version=1010')
    gypFormats.append('xcode')
else:
    gypScript = '../../../Libraries/gyp/gyp'
    gypFormats.append('cmake')
    cmakeConfigurations.append('Debug')
    cmakeConfigurations.append('Release')

os.chdir(scriptPath)
for format in gypFormats:
    command = gypArguments[:]
    command.insert(0, gypScript)
    command.append('--format=' + format)
    command.append('Telegram.gyp')
    result = subprocess.call(' '.join(command), shell=True)
    if result != 0:
        print('[ERROR] Failed generating for format: ' + format)
        finish(result)

os.chdir(scriptPath + '/../../out')
for configuration in cmakeConfigurations:
    os.chdir(configuration)
    result = subprocess.call('cmake "-GCodeBlocks - Unix Makefiles" .', shell=True)
    if result != 0:
        print('[ERROR] Failed calling cmake for ' + configuration)
        finish(result)
    os.chdir('..')

finish(0)

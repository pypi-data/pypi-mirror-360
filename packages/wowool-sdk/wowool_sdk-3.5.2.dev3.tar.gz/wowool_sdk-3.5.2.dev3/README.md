# Release

## linux arm/amd

You need to build on a arm64 or amd64 machine !
Note: that if you don't build on the correct architecture it will be *SLOW* , I mean really *SLOOOW*.

to build for amd64 follow the 3 steps but change the platform to **linux/amd64**

### Step 1

Prepare the base docker container.

cd ~/dev/wowoool/docker-wowool-basic-build
./build.sh --platform linux/arm64

### Step 2

Build the tir-thirdparty library, 

at this stage you need your AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY to upload to aws.

cd ~/dev/wowoool/tir-thirdparty
./build.sh --platform linux/arm64


### Step 3

Build the tir library, 

cd ~/dev/wowoool/tir

./build.sh --platform linux/arm64


### Stem4


cd ~/dev/wowoool/comp-wowool-sdk-native-py-cpp


set the target:
export CIBW_BUILD=cp312-macosx_arm64
CIBW_BUILD_VERBOSITY=3 CIBW_BUILD_FRONTEND="pip; args: -v" python -m cibuildwheel --output-dir wheelhouse



## Darwin

You need to set a couple of env variables

export CIBW_SKIP="cp311-macosx_* pp-macosx_*"
python -m cibuildwheel --output-dir /Users/phforest/dev/wowool/comp-wowool-sdk-native-py-cpp/dist  --debug

## Linux arm

CIBW_PLATFORM=linux \
CIBW_ARCHS=aarch64 \
CIBW_BUILD="cp312-* cp313-*" \
CIBW_SKIP="*musllinux*" \
CIBW_MANYLINUX_AARCH64_IMAGE=manylinux2014 \
cibuildwheel --output-dir dist
#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <version>"
    exit 1;
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
DEFAULT='\033[0;39m'
CYAN='\033[0;36m'

VERSION=$(echo $1 | sed 's/v//g')
BASEDIR="storeops-custom-application"
DIST=$(awk -F "=" '/VERSION_CODENAME/ {print $2}' /etc/os-release)
ARCH=$(dpkg --print-architecture)
INSTALLDIR="/root/${BASEDIR}"

echo -e "${CYAN}Distribution detected: ${DIST}${DEFAULT}"
echo -e "${CYAN}Version detected: ${VERSION}${DEFAULT}"
echo -e "${CYAN}Architecture detected: ${ARCH}${DEFAULT}"

echo "Updating the control file..."
sed -i "s/Architecture:.*/Architecture: ${ARCH}/g" ./${BASEDIR}/DEBIAN/control
sed -i "s/Version:.*/Version: ${VERSION}/g" ./${BASEDIR}/DEBIAN/control

echo -e "${GREEN}Installing required packages...${DEFAULT}"
apt-get install -y python3-dev python3-venv

echo -e "${GREEN}Copying files to install directory...${DEFAULT}"
rm -rf ${BASEDIR}${INSTALLDIR}
mkdir -p ${BASEDIR}${INSTALLDIR}
cp -R ../src/* ${BASEDIR}${INSTALLDIR}

echo -e "${GREEN}Installing dependencies...${DEFAULT}"
mkdir -p ${INSTALLDIR}
cp ../src/requirements.txt ${INSTALLDIR}
cd ${INSTALLDIR}
python3 -m venv venv
source venv/bin/activate
pip3 install --upgrade pip
pip3 install -r requirements.txt
deactivate
cd -
rm -rf ${BASEDIR}${INSTALLDIR}/venv
cp -r ${INSTALLDIR}/venv ${BASEDIR}${INSTALLDIR}
rm -rf ${INSTALLDIR}

echo -e "${GREEN}Building debian package...${DEFAULT}"
chmod 755 ${BASEDIR}/DEBIAN
chmod 755 ${BASEDIR}/DEBIAN/*
dpkg-deb --build ${BASEDIR} ./${BASEDIR}_${DIST}_${VERSION}_${ARCH}.deb

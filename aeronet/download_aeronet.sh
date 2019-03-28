#!/usr/bin/env bash

year=02

day2=31
month2=12
year2=18 #117 for 2017
for level in 15 20 
do
# for site in  OHP_OBSERVATOIRE Aubiere_LAMP 
 for site in COVE_SEAPRISM Galata_Platform Gloria GOT_Seaprism Gustav_Dalen_Tower Helsinki_Lighthouse Ieodo_Station Lake_Erie LISCO Lucinda MVCO Palgrunden Socheongcho Thornton_C-power USC_SEAPRISM Venise WaveCIS_Site_CSI_6 Zeebrugge-MOW1 
do
echo $site
# for AOD data
if [ 1 == 1 ];then
wget "http://aeronet.gsfc.nasa.gov/cgi-bin/print_warning_v3?site="$site"&year=1$year&month=1&day=1&year2=1"$year2"&month2="$month2"&day2="$day2"&AOD"$level"=1&SDA"$level"=1&AVG=10" --no-check-certificate
zipfile=20"$year"0101_20"$year2$month2$day2"_"$site"
wget http://aeronet.gsfc.nasa.gov/zip_files/V3/"$zipfile".zip -O zip.tmp
 
unzip -o zip.tmp && \
mv $zipfile.lev$level ../V3/"$site"_aod_V3.lev$level && \
mv $zipfile.ONEILL_lev$level ../V3/"$site"_sda_V3.lev$level && sed -i 's/Exact_Wavelengths_of_AOD(um)/Exact_Wavelengths_of_AOD(um),,,,,,,,,/' ../V3/"$site"_sda_V3.lev$level
fi

# for Aerosol Inversion data
wget "http://aeronet.gsfc.nasa.gov/cgi-bin/print_warning_inv_v3?site="$site"&year=1$year&month=1&day=1&year2=1"$year2"&month2="$month2"&day2="$day2"&SSA=1&RIN=1&VOL=1&TAB=1&ASY=1&AVG=10&DATA_TYPE="$level --no-check-certificate
zipfile=20"$year"0101_20"$year2$month2$day2"_"$site"
wget http://aeronet.gsfc.nasa.gov/zip_files/V3/inv/"$zipfile".zip -O zip.tmp
unzip -o zip.tmp && \
	mv $zipfile.ssa ../V3/"$site"_ssa_V3.lev$level && \
	mv $zipfile.rin ../V3/"$site"_rin_V3.lev$level && \
        mv $zipfile.vol ../V3/"$site"_vol_V3.lev$level && \
        mv $zipfile.tab ../V3/"$site"_tab_V3.lev$level && \
        mv $zipfile.asy ../V3/"$site"_asy_V3.lev$level

done
done


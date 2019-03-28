#!/usr/bin/env bash
odir='../OCv3/'

year=2015 #02

day2=31
month2=12
year2=2018

for level in 20 #10 15 20 
do
 for site in 'Abu_Al_Bukhoosh' 'ARIAKE_TOWER' 'Bari_Waterfront' 'Blyth_NOAH' 'COVE_SEAPRISM' 'Gageocho_Station' 'Galata_Platform' 'Gloria' 'GOT_Seaprism' 'Gustav_Dalen_Tower' 'Helsinki_Lighthouse' 'Ieodo_Station' 'Irbe_Lighthouse' 'KAUST_Campus' 'Lake_Erie' 'Lake_Okeechobee' 'LISCO' 'Lucinda' 'MVCO' 'Palgrunden' 'Socheongcho' 'South_Greenbay' 'Thornton_C-power' 'USC_SEAPRISM' 'USC_SEAPRISM_2' 'Venise' 'WaveCIS_Site_CSI_6' 'Zeebrugge-MOW1'
do
echo $site
wget  -qO- --no-check-certificate "https://aeronet.gsfc.nasa.gov/cgi-bin/print_web_data_v3?site="$site"&year="$year"&month=1&day=1&year2="$year2"&month2="$month2"&day2="$day2"&LWN"$level"=1&AVG=10" | sed -e 's/<[^>]*>//g' > $odir$site"_OCv3".lev$level

done
done


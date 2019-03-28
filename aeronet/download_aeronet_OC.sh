#!/usr/bin/env bash


year=02

day2=31
month2=12
year2=18

for level in 10 15 20 
do
 for site in COVE_SEAPRISM Galata_Platform Gloria GOT_Seaprism Gustav_Dalen_Tower Helsinki_Lighthouse Ieodo_Station Lake_Erie LISCO Lucinda MVCO Palgrunden Socheongcho Thornton_C-power USC_SEAPRISM Venise WaveCIS_Site_CSI_6 Zeebrugge-MOW1
do
echo $site
wget  -qO- --no-check-certificate "http://aeronet.gsfc.nasa.gov/cgi-bin/print_web_new_seaprism_new?site="$site"&year=1"$year"&month=1&day=1&year2=1"$year2"&month2="$month2"&day2="$day2"&LEV"$level"=1&AVG=10" | sed -e 's/<[^>]*>//g' > ../OC/$site"_OC".lev$level

done
done


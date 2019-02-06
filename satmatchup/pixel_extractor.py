
command_xml='
<parameters>
    <sourceProductPaths>/DATA/Satellite/SENTINEL2/venice/L2h/**/*dim,/DATA/Satellite/SENTINEL2/venice/L2aero/*dim</sourceProductPaths>
    <exportBands>true</exportBands>
    <exportTiePoints>true</exportTiePoints>
    <exportMasks>true</exportMasks>
    <coordinates>
        <coordinate>
            <name>Venise</name>
            <latitude>45.3139</latitude>
            <longitude>12.5083</longitude>
            <originalValues/>
            <id>0</id>
        </coordinate>
    </coordinates>
    <timeDifference/>
    <windowSize>7</windowSize>
    <outputFilePrefix>pixEx</outputFilePrefix>
    <exportExpressionResult>true</exportExpressionResult>
    <aggregatorStrategyType>no aggregation</aggregatorStrategyType>
    <exportSubScenes>true</exportSubScenes>
    <subSceneBorderSize>0</subSceneBorderSize>
    <exportKmz>false</exportKmz>
    <extractTimeFromFilename>true</extractTimeFromFilename>
    <dateInterpretationPattern>yyyyMMdd</dateInterpretationPattern>
    <filenameInterpretationPattern>*${startDate}*${endDate}*</filenameInterpretationPattern>
    <includeOriginalInput>false</includeOriginalInput>
</parameters>'

Product:	S2B_MSIL2grs_20180927T103019_N0206_R108_T31TGK_20180927T143835

Image-X:	198	pixel
Image-Y:	327	pixel
Longitude:	6°19'13" E	degree
Latitude:	44°30'14" N	degree

BandName	Wavelength	Unit	Bandwidth	Unit	Value	Unit	Solar Flux	Unit
flags:					0
Lwn_g_B1:	442.311	nm	58.0	nm	1.15130
Lwn_g_B2:	492.1326	nm	130.0	nm	1.67281
Lwn_g_B3:	558.9499	nm	100.0	nm	1.38088
Lwn_g_B4:	664.938	nm	90.0	nm	0.02857
Lwn_g_B5:	703.8308	nm	97.0	nm	0.02403
Lwn_g_B6:	739.129	nm	40.0	nm	0.03669
Lwn_g_B7:	779.7236	nm	71.0	nm	0.05549
Lwn_g_B8:	832.9462	nm	175.0	nm	0.04742
Lwn_g_B8A:	863.9796	nm	79.0	nm	0.04516
Lwn_g_B11:	1610.4191	nm	172.0	nm	0.01878
Lwn_g_B12:	2185.6987	nm	276.0	nm	0.00970
Lwn_B1:	442.311	nm	58.0	nm	1.11465
Lwn_B2:	492.1326	nm	130.0	nm	1.63038
Lwn_B3:	558.9499	nm	100.0	nm	1.33794
Lwn_B4:	664.938	nm	90.0	nm	-0.00947
Lwn_B5:	703.8308	nm	97.0	nm	-0.01235
Lwn_B6:	739.129	nm	40.0	nm	0.00340
Lwn_B7:	779.7236	nm	71.0	nm	0.02488
Lwn_B8:	832.9462	nm	175.0	nm	0.02006
Lwn_B8A:	863.9796	nm	79.0	nm	0.01998
Lwn_B11:	1610.4191	nm	172.0	nm	-0.00261
Lwn_B12:	2185.6987	nm	276.0	nm	0.00106
BRDFg:					0.67172
SZA:					47.41843
VZA:					0.50358
AZI:					283.47034


flags.nodata:	false
flags.negative:	false
flags.ndwi:	false
flags.ndwi_corr:	false
flags.high_nir:	false
flags.empty:	false
flags.empty:	false

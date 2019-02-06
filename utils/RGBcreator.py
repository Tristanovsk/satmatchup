import sys
import esasnappy
from esasnappy import ProductIO, ProductUtils, ProgressMonitor

#if len(sys.argv) != 2:
#    print("usage: %s <file>" % sys.argv[0])
#    sys.exit(1)

file,suff = sys.argv[1],sys.argv[2]
#dir = '/DATA/Satellite/SENTINEL2/venice/L2h/'
#file=dir+'S2A_OPER_PRD_MSIL2h_PDMC_20160718T175711_R022_V20160718T101028_20160718T101028.dim'


jpy = esasnappy.jpy

# More Java type definitions required for image generation
Color = jpy.get_type('java.awt.Color')
ColorPoint = jpy.get_type('org.esa.snap.core.datamodel.ColorPaletteDef$Point')
ColorPaletteDef = jpy.get_type('org.esa.snap.core.datamodel.ColorPaletteDef')
ImageInfo = jpy.get_type('org.esa.snap.core.datamodel.ImageInfo')
ImageManager = jpy.get_type('org.esa.snap.core.image.ImageManager')
JAI = jpy.get_type('javax.media.jai.JAI')

# Disable JAI native MediaLib extensions
System = jpy.get_type('java.lang.System')
System.setProperty('com.sun.media.jai.disableMediaLib', 'true')

def write_image(band, points, filename, format):
    cpd = ColorPaletteDef(points)
    ii = ImageInfo(cpd)
    band.setImageInfo(ii)
    im = ImageManager.getInstance().createColoredBandImage([band], band.getImageInfo(), 0)
    JAI.create("filestore", im, filename, format)

def write_rgb_image(bands, filename, format):
    image_info = ProductUtils.createImageInfo(bands, True, ProgressMonitor.NULL)
    im = ImageManager.getInstance().createColoredBandImage(bands, image_info, 0)
    JAI.create("filestore", im, filename, format)


image_format='PNG'
product = ProductIO.readProduct(file)
# band = product.getBand('B2')
# band_ = product.getBand('Rlut_B2')
# # The colour palette assigned to pixel values 0, 50, 100 in the band's geophysical units
# points = [ColorPoint(0.0, Color.BLACK),
#           ColorPoint(0.75, Color.BLUE),
#           ColorPoint(1.5, Color.GREEN),
#           ColorPoint(2.25, Color.YELLOW),
#           ColorPoint(4, Color.RED),
#           ColorPoint(6, Color.WHITE)]
#
# write_image(band, points, file.replace('.dim',"_B2.png"), image_format)
# write_image(band_, points, file.replace('.dim',"_RLut_B2.png"), image_format)

#suff='' #'_g'
red = product.getBand('Lwn'+suff+'_B4')
green = product.getBand('Lwn'+suff+'_B3')
blue = product.getBand('Lwn'+suff+'_B2')
write_rgb_image([red, green, blue], file.replace('.nc',suff+'_RGB.png'), image_format)
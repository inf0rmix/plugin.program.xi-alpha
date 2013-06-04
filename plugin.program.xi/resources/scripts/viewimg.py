import xbmcgui
import sys
import urlparse
 
class PopupWindow(xbmcgui.WindowDialog):
    def __init__(self, image):
        self.addControl(xbmcgui.ControlImage(x=100, y=90, width=1050, height=550, filename=image, aspectRatio=2))
        #self.addControl(xbmcgui.ControlImage(x=0, y=0, width=1300, height=800, filename=image, aspectRatio=2))
 
if __name__ == '__main__':
    if len(sys.argv) >= 2:
      mycimg = sys.argv[1]
    else:
      mycimg = '/usr/share/xbmc/addons/skin.confluence/media/MediaBladeSub.png'
    #mycimg = 'http://www.nasa.gov/images/content/744056main_DSC6398_SaundersIsland-orig_full.jpg'
    #mycimg = 'http://www.dradio.de/pictures/rss/dradio-logo.gif'
    window = PopupWindow(mycimg)
    window.show()
    xbmc.sleep(5000)
    window.close()
    del window

##Function to verify the image
import PIL.Image as Image
import os

__all__ = ['verify_image']

def verify_image(image_path, image_type=None, image_size=None,logger=None):
    """
    Function to verify the image
    Input:
        image_path: path to the image
        image_name: name of the image
        image_type: type of the image
        image_size: size of the image
    Output:
        status: True if the image is verified, False otherwise
    """
    status = False
    if os.path.isfile(image_path):
        if image_size:
            if os.path.getsize(image_path) == image_size:
                status=True
            else:
                status=False
                if logger:
                    logger.warning("Image size mismatch : {}".format(image_path))
                return status         
        try:
            im = Image.open(image_path)
            if im.format == 'JPEG':
                status = True
                return status
            if im.format == 'PNG':
                status = True
                return status
            if im.format == 'GIF':
                status = True
                return status
            if im.format == 'BMP':
                status = True
                return status
            if im.format == 'TIFF':
                status = True
                return status    
            if im.format == "JPG":
                status = True
                return status
            else:
                if logger:
                    logger.warning("Unknown image type : {}".format(image_path))
        except IOError:
            if logger:
                logger.warning("Image path not verified : {}".format(image_path))
            pass
    else:
        if logger:
            logger.warning("Image path not found : {}".format(image_path))
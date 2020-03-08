import os
import secrets
from PIL import Image

from webapp import app



# Method for randomise image's name and save in the static/pic file 
def store_image(form_image):
    # Get a random hex 
    random_hex = secrets.token_hex(8)
    # Get the extention of the pic file and concatenate it the hex
    _, f_ext = os.path.splitext(form_image.filename)
    image_fn = random_hex + f_ext
    # Make a path to the static/pics directory
    image_path = os.path.join(app.root_path, 'static/pics', image_fn)

    # Resize the image before saving it
    output_size = (125, 125)
    image = Image.open(form_image)
    image.thumbnail(output_size)
    image.save(image_path)

    return image_fn
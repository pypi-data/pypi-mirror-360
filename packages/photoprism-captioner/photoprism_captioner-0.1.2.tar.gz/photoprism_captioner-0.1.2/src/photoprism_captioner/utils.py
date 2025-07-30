from io import BytesIO


def resize_photo_to_max_width(photo:bytes, max_width:int) -> bytes:
    from PIL import Image
    img = Image.open(BytesIO(photo))
    width, height = img.size
    if width > max_width:
        aspect_ratio = height / width
        new_width = max_width
        new_height = int(new_width * aspect_ratio)
        img = img.resize((new_width, new_height))
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='jpeg')
    return img_byte_arr.getvalue()

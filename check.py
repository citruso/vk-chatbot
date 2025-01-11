from PIL import Image
import pytesseract

def check(name):
    img = Image.open(name)
    obj = img.load()
    width, height = img.size

    if obj[0,height-1] == (252,196,51):
        scan = img.crop((width-110,height-14,width-25,height))
        text = pytesseract.image_to_string(scan, lang='eng')

        if 'reactor' in text:
            new_img = img.crop((0,0,width,height-14))
            new_img.save(name)

    elif obj[0,height-1] == (255,255,255):
        scan = img.crop((175,height-20,width-175,height))
        text = pytesseract.image_to_string(scan, lang='eng')

        if 'shutterstock' in text:
            new_img = img.crop((0,0,width,height-20))
            new_img.save(name)

    img.close()

































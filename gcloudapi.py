from google.cloud import vision
import io
import os
import pandas as pd

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "client.json"
client = vision.ImageAnnotatorClient()

import fitz
pdffile = "C:\\Users\\hp\\AppData\\Desktop\\makeathon\\data.png"
doc = fitz.open(pdffile)
page = doc.loadPage(0) #number of page
pix = page.getPixmap()
output = "outfile.png"
pix.writePNG(output)

with io.open('outfile.png', 'rb') as im_file:
    content = im_file.read()

image = vision.types.Image(content=content)

response = client.document_text_detection(image=image)
texts = response.text_annotations
textf = dict()
itr = 0
init = []
print(texts)
for text in texts:
        #print('\n"{}"'.format(text.description))
        if itr==0:
            lines = text.description.split('\n')
            itr += 1
        else:
            vertices = list(text.description)
            for vertex in text.bounding_poly.vertices:
                vertices.append(vertex.x)
                vertices.append(vertex.y)
            init.append(vertices)
x = pd.DataFrame(init, columns = ['key','x1','y1','x2','y2','x3','y3','x4','y4'])
print(x)

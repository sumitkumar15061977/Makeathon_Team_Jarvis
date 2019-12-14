from google.cloud import vision
import io
import os
import shutil
from collections import OrderedDict

def pdftojpg(path):
    #import sys
    #print(path)
    pdf = open(path, "rb").read()

    startmark = b"\xff\xd8"
    startfix = 0
    endmark = b"\xff\xd9"
    endfix = 2
    i = 0

    njpg = 0
    while True:
        istream = pdf.find(b"stream", i)
        if istream < 0:
            break
        istart = pdf.find(startmark, istream, istream + 20)
        if istart < 0:
            i = istream + 20
            continue
        iend = pdf.find(b"endstream", istart)
        if iend < 0:
            raise Exception("Didn't find end of stream!")
        iend = pdf.find(endmark, iend - 20)
        if iend < 0:
            raise Exception("Didn't find end of JPG!")

        istart += startfix
        iend += endfix
        print
        "JPG %d from %d to %d" % (njpg, istart, iend)
        jpg = pdf[istart:iend]
        jpgfile = open("jpg%d.jpg" % njpg, "wb")
        jpgfile.write(jpg)
        jpgfile.close()

        njpg += 1
        i = iend
        return os.path.basename(jpgfile.name)


def get_invoice_number(textf, pos):
    items = list(textf.items())
    invoice_number = None
    min = 99999
    for item in items:
        if item[1][0] > items[pos][1][0] and item[1][1] == items[pos][1][1] and str(item[0]).isnumeric() and len(
                str(item[0])) >= 5:
            invoice_number = str(item[0])
            return invoice_number

        elif item[1][0] == items[pos][1][0] and item[1][1] > items[pos][1][1] and str(item[0]).isnumeric() and len(
                str(item[0])) >= 5:
            invoice_number = str(item[0])
            return invoice_number

        if item[1][0] > items[pos][1][0] and (
                item[1][1] < items[pos][1][1] + 20 or item[1][1] > items[pos][1][1] - 20) and str(
                item[0]).isnumeric() and len(str(item[0])) >= 5:
            temp = abs(item[1][1] - items[pos][1][1])
            if temp < min:
                min = temp
                # print(item)
                invoice_number = str(item[0])

        if (item[1][0] < items[pos][1][0] + 20 or item[1][0] > items[pos][1][0] - 20) and item[1][1] > items[pos][1][
            1] and str(item[0]).isnumeric() and len(str(item[0])) >= 5:
            temp = abs(item[1][0] - items[pos][1][0])
            if temp < min:
                min = temp
                invoice_number = str(item[0])
    return invoice_number


def get_purchase_number(textf, pos):
    items = list(textf.items())
    purchase_number = None
    min = 99999
    for item in items:
        if item[1][0] > items[pos][1][0] and item[1][1] == items[pos][1][1] and str(item[0]).isnumeric() and len(
                str(item[0])) >= 5:
            purchase_number = str(item[0])
            return purchase_number

        elif item[1][0] == items[pos][1][0] and item[1][1] > items[pos][1][1] and str(item[0]).isnumeric() and len(
                str(item[0])) >= 5:
            purchase_number = str(item[0])
            return purchase_number

        if item[1][0] > items[pos][1][0] and (
                item[1][1] < items[pos][1][1] + 20 or item[1][1] > items[pos][1][1] - 20) and str(
                item[0]).isnumeric() and len(str(item[0])) >= 5:
            temp = abs(item[1][1] - items[pos][1][1])
            if temp < min:
                min = temp
                # print(item)
                purchase_number = str(item[0])

        if (item[1][0] < items[pos][1][0] + 20 or item[1][0] > items[pos][1][0] - 20) and item[1][1] > items[pos][1][
            1] and str(item[0]).isnumeric() and len(str(item[0])) >= 5:
            temp = abs(item[1][0] - items[pos][1][0])
            if temp < min:
                min = temp
                purchase_number = str(item[0])
    return purchase_number


def main_code(path):
    with io.open(pdftojpg(path), 'rb') as im_file:
        content = im_file.read()

    image = vision.types.Image(content=content)

    response = client.document_text_detection(image=image)
    texts = response.text_annotations
    textf = OrderedDict()
    vertices = []
    itr = 0
    invoice_flag = 0
    purchase_flag = 0
    for text in texts:
        # print('\n"{}"'.format(text.description))
        if itr == 0:
            lines = text.description.split('\n')
            itr += 1
        else:
            vertices = []
            if invoice_flag == 1:
                if str(text.description).lower() == "number" or str(text.description).lower() == "#":
                    textf["invoice number"] = temp_vertices_invoice
                    invoice_flag = 2
                    continue
                invoice_flag = 0
            if purchase_flag == 1:
                if str(text.description).lower() == "order":
                    purchase_flag = 2
                    continue
                purchase_flag = 0
            if purchase_flag == 2:
                if str(text.description).lower() == "number" or str(text.description).lower() == "#":
                    textf["purchase order number"] = temp_vertices_purchase
                    purchase_flag = 3
                    continue
                elif str(text.description).isnumeric():
                    textf["purchase order number"] = temp_vertices_purchase
                    purchase_flag = 3
                purchase_flag = 0
            for vertex in text.bounding_poly.vertices:
                vertices.append(vertex.x)
                vertices.append(vertex.y)
            textf[str(text.description).lower()] = list(vertices)
            if str(text.description).lower() == "invoice" and invoice_flag != 2:
                temp_vertices_invoice = list(vertices)
                invoice_flag = 1
                purchase_flag = 3
            if str(text.description).lower() == "purchase" and purchase_flag != 3:
                temp_vertices_purchase = list(vertices)
                purchase_flag = 1
            if str(text.description).lower() in ["po", "order"] and purchase_flag != 3:
                temp_vertices_purchase = list(vertices)
                purchase_flag = 2

        # print('bounds: {}'.format(','.join(vertices)))
    # print(textf)
    # print(lines)
    print("*****************************************************")
    print(path.split('\\')[-1])
    # print("\n")

    if "invoice number" in textf.keys():
        print("DOCUMENT CLASSIFIED:     This is an INVOICE!")
        pos = list(textf.keys()).index("invoice number")
        invoice_no = get_invoice_number(textf, pos)
        if invoice_no != None:
            print(f"Invoice_no: {invoice_no}")
            shutil.move(path, )
        else:
            print("Couldn't get invoice no")

    elif "purchase order number" in textf.keys():
        print("DOCUMENT CLASSIFIED:     This is a PURCHASE ORDER!")
        pos = list(textf.keys()).index("purchase order number")
        purchase_order_no = get_purchase_number(textf, pos)
        if purchase_order_no != None:
            print(f"Purchase_order_no: {purchase_order_no}")
        else:
            print("Couldn't get purchase order no")

    else:
        print("Could not classify document")

    print("\n")


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "TextReader-e3632e286783.json"
client = vision.ImageAnnotatorClient()

path = 'C:\\Users\\hp\\AppData\\Desktop\\makeathon'

files = []
# r=root, d=directories, f = files
for r, d, f in os.walk(path):
    for file in f:
        if '.pdf' in file:
            files.append(os.path.join(r, file))

for f in files:
    main_code(f);

print("All files Classified successfully")


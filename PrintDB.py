import mysql.connector
from mysql.connector import Error

#####connect to MYSQL
print('Connecting to database system.')

database_name = input('Please name your database: ')

connection = mysql.connector.connect(
  host="localhost",
  port = 8889,
  user="root",
  password="root"
)
print('Creating database:', database_name)
cursor = connection.cursor()
#createDB
drop_db = "DROP DATABASE IF EXISTS {}"
create_db = "CREATE DATABASE {}"
cursor.execute(drop_db.format(database_name))
cursor.execute(create_db.format(database_name))

connection.commit()
connection.close()


connection = mysql.connector.connect(
  host="localhost",
  port = 8889,
  user="root",
  password="root",
  database = database_name
)
print('Creating necessary tables in', database_name)
cursor = connection.cursor()
###clean table and recreate
### sql for TABLE_SCHEMA
mySql_insert_querys = '''
Drop Table if exists `product` ;
Drop Table if exists `prices`;
Drop Table if exists `size`  ;
Drop Table if exists `finish`;
Drop Table if exists `photo`;

CREATE TABLE size (
    size_id INT AUTO_INCREMENT,
    pretty_size text,
    short_size INT,
    long_size INT,
    size_sku text,
    index(size_id),
    PRIMARY KEY(size_id)
)ENGINE=InnoDB CHARACTER SET=utf8;

CREATE TABLE finish (
    finish_id INT AUTO_INCREMENT,
    finish_type TEXT,
    finish_description TEXT,
    finish_sku TEXT,
    index(finish_id),
    PRIMARY KEY(finish_id)
)ENGINE=InnoDB CHARACTER SET=utf8;

CREATE TABLE prices (
    price_id INT AUTO_INCREMENT,
    price INT,
    sku_combo TEXT,
    finish_id INT,
    size_id INT,
    index(finish_id),
    index(size_id),
    index(price_id),
    Constraint foreign key (finish_id) REFERENCES finish (finish_id) ON DELETE CASCADE ON UPDATE CASCADE,
    Constraint foreign key (size_id) REFERENCES size (size_id) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY(price_id)
)ENGINE=InnoDB CHARACTER SET=utf8;


CREATE TABLE photo (
    photo_id INT AUTO_INCREMENT,
    img_title TEXT,
    img_http TEXT,
    img_description TEXT,
    img_aspect TEXT,
    img_crop TEXT,
    PRIMARY KEY(photo_id)
)ENGINE=InnoDB CHARACTER SET=utf8;

CREATE TABLE product (
    product_id INT AUTO_INCREMENT,
    photo_id INT,
    price_id INT,
    finish_id INT,
    size_id INT,
    PRIMARY KEY(product_id),
    index(finish_id),
    index(size_id),
    index(photo_id),
    index(price_id),
    Constraint foreign key (finish_id) REFERENCES finish (finish_id) ON DELETE CASCADE ON UPDATE CASCADE,
    Constraint foreign key (size_id) REFERENCES size (size_id) ON DELETE CASCADE ON UPDATE CASCADE,
    Constraint foreign key (photo_id) REFERENCES photo (photo_id) ON DELETE CASCADE ON UPDATE CASCADE,
    Constraint foreign key (price_id) REFERENCES prices (price_id) ON DELETE CASCADE ON UPDATE CASCADE
)ENGINE=InnoDB CHARACTER SET=utf8;'''
##### MYSQL.connector doesn't like multiple querys so split on ; and execute singly
querys = mySql_insert_querys.split(';')
#print(querys)
for query in querys:
    cursor.execute(query)


connection.commit()

######Populate with photographs
filename = input('Where is the photo info? ')
if len(filename) < 1:
    filename = 'lightroomexport.ods'

import pandas as pd
import numpy as np

##connect to database
connection = mysql.connector.connect(user='root', password='root', host='localhost', port=8889, database= database_name)
cursor = connection.cursor()

print('Reading photo metadata.')

path = filename
# load a sheet based on its index (1 based) (shlould be list view from lightroomexport)
from pandas_ods_reader import read_ods



df = read_ods(path, 'List View')
#print(df)
index = df.index
#print(type(index))

df.insert(loc=0, column='index', value=np.arange(len(df)))
#print(df)

#print(index)
#print(list(df))
#print(list(df)[0:10])

imagenumber = list(df)[0]
#print(imagenumber)
imagehttp = list(df)[1]
title = list(df)[2]
caption = list(df)[3]
cropped = list(df)[6]
#horizont= list(df)[7]
#vert = list(df)[8]

#print(vert)

#print(list(dict(df).get(list(df)[1])))
imagedata = zip(list(dict(df).get(list(df)[0])),list(dict(df).get(list(df)[1])),list(dict(df).get(list(df)[2])),list(dict(df).get(list(df)[3])),list(dict(df).get(list(df)[6])))


print('Extracting image details and inserting into database:', database_name)
#######check how many uploads of images have been made with WP/LR This is written only for the first one.
websiteurl = input('I need some of the details of your website to publish in the description of the products. What is the main address your website? ')
#for each photograph extract img details and calculate img_aspect
for image in list(imagedata):

    print(image)
    photo_id =int(image[0])+1
    img_title = image[2]
    try:
        strip_img_title = img_title.strip().replace("'", '')
    except:
        strip_img_title = img_title.strip()
    img_http = websiteurl + '/wp-content/uploads/' +strip_img_title.replace(' ', '-')+'.jpg'
    img_description = image[3]
    img_crop = image[4]
    img_size1 = img_crop.split()[0]
    img_size2 = img_crop.split()[2]
    if int(img_size1)<= int(img_size2):
        img_short = img_size1
        img_long = img_size2
    else:
        img_short = img_size2
        img_long = img_size1
    img_aspect = int(img_short)/int(img_long)
    #print(photo_id, img_title, img_long, img_short, img_description, img_aspect)

    cursor.execute('''INSERT INTO photo (photo_id, img_title, img_http, img_description, img_crop, img_aspect)
    VALUES (%s, %s, %s, %s, %s, %s)''', (photo_id, img_title, img_http, img_description, img_crop, img_aspect,))
    connection.commit()
    #print('photo number ', photo_id, 'inserted')


######## add the sizes to the size table
#cm come first because it works automatically for woocommerce sizes in numerical order
sizes = ['20 x 30 cm, 8 x 12 inches' ,'30 x 46 cm, 12 x 18 inches','41 x 61 cm, 16 x 24 inches','51 x 76 cm, 20 x 30 inches','61 x 91 cm, 24 x 36 inches','20 x 20 cm, 8 x 8 inches','30 x 30 cm, 12 x 12 inches','41 x 41 cm, 16 x 16 inches','51 x 51 cm, 20 x 20 inches','61 x 61 cm, 24 x 24 inches','20 x 25 cm, 8 x 10 inches','30 x 38 cm, 12 x 15 inches','41 x 51 cm, 16 x 20 inches','51 x 64 cm, 20 x 25 inches','61 x 76 cm, 24 x 30 inches', '20 x 40 cm, 8 x 16 inches','30 x 60 cm, 12 x 24 inches','41 x 82 cm, 16 x 32 inches','51 x 102 cm, 20 x 40 inches','61 x 122 cm, 24 x 48 inches']

print('Calculating sizes.')
#calculating on the inch sizes
for size in sizes:
    short_size = size.split()[4]
    long_size = size.split()[6]
    size_sku = str(size.split()[4]) + size.split()[5].upper() + str(size.split()[6])
    #print(short_size, long_size, size_sku)
    cursor.execute('''INSERT INTO size (pretty_size, short_size, long_size, size_sku)
    VALUES (%s, %s, %s, %s)''', (size, short_size, long_size, size_sku,))
    connection.commit()
    #print('size ', size, 'inserted')


########## add the finishes to the finish TABLE
print('Checking for available finishes for these sizes.')

finish_types = ['Stretched Canvas', 'Lustre Photographic Paper ', 'Fine Art Print on Premium Photo Rag']
finish_descriptions = ['All stretched canvas prints have a non-coated finish on a 19 mm stretched frame of European knotless pine. Canvases are printed with a mirror wrap, and stretched by a professional framing team, ensuring perfect corner folds and an excellent finish. Canvases are 400 gsm.' , 'A premium photographic paper with a satin lustre finish. The lustre finish provides a subtle pearl-like texture. Supporting deeper colour-saturation than matte papers, this paper produces impressive colour depth and strikingly intense blacks. Lustre prints are on 240 gsm premium paper. Photo prints are surrounded by a white border. Bordersize varies and is approximately 10% of the edge length.', 'A heavy-duty matte paper made of 100% cotton rag with a natural white tone and excellent black saturation. This paper produces very high-quality print reproductions. The Hahnemühle Photo Rag paper is 308 gsm. Fine art prints are surrounded by a white border. Bordersize varies and is approximately 10% of the edge length.']
finish_skus = ['CAN19SC', 'PP240LPP', 'FA308HPR']

finishes = (list(zip(finish_types, finish_descriptions, finish_skus)))

for finish in finishes:
    cursor.execute('''INSERT INTO finish (finish_type, finish_description, finish_sku)
    VALUES (%s, %s, %s)''', (finish[0],finish[1],finish[2],))
    connection.commit()
    #print('size ', finish[0], 'inserted')


#### get the prices from ods file
print("Pricing the printable images.")
from pyexcel_ods import get_data
#####This needs fixing to figure out where the prices come from. Only works for my original file
print('We need your photo metadata. It should be an ODS filetype and in the same directory as the python module.')
price_filename = input('Where is the pricing info? ')
data = get_data(price_filename)

#print('this is my list', list(data))
pricedata =(data.get(list(data)[2]))
#print('the price data', pricedata)
#print(pricedata[0])
pricedict = {}
for sizeprices in pricedata[1:-2]:
    #print(sizeprices)
    size = sizeprices[0]
    #print('This is the big',size)
    #print(size.split('*')[1])
    skusize = str(size.split('*')[0])+'X'+str(size.split('*')[1])

    canvasprice = sizeprices[6]
    photoprint240price = sizeprices[12]
    fineart308price = sizeprices[18]
    #print('sku size and prices', skusize, canvasprice, photoprint240price, fineart308price)

    cursor.execute('''SELECT size_id From size where `size_sku` = %s''', (skusize,))
    size_id = cursor.fetchone()

    if canvasprice != 0:
        cursor.execute('''SELECT finish_id From finish where `finish_sku` = "CAN19SC" ''')
        finish_id = cursor.fetchone()
        sku_combo = skusize+'CAN19SC'
        pricedict[sku_combo] = (size_id[0], finish_id[0], canvasprice)
        #print('sku and price', sku_combo, canvasprice)
    if photoprint240price != 0:
        cursor.execute('''SELECT finish_id From finish where `finish_sku` = "PP240LPP" ''')
        finish_id = cursor.fetchone()
        sku_combo = skusize+'PP240LPP'
        pricedict[sku_combo] = (size_id[0], finish_id[0], photoprint240price)
        #print('sku and price', sku_combo, photoprint240price)
    if fineart308price != 0:
        cursor.execute('''SELECT finish_id From finish where `finish_sku` = "FA308HPR" ''')
        finish_id = cursor.fetchone()
        sku_combo = skusize+'FA308HPR'
        pricedict[sku_combo] = (size_id[0], finish_id[0], fineart308price)
        #print('sku and price', sku_combo, fineart308price)
    else:
        continue

#print('dictionary of prices to be added',pricedict)

for sku1, prices in pricedict.items():
    #print('SKU is ', sku1 , 'size id is', prices[0], 'finish id is ', prices[1], 'prices is ', prices[2] )

    cursor.execute('''INSERT INTO prices (price, sku_combo, finish_id, size_id)
    VALUES (%s, %s, %s, %s)''', (prices[2], sku1, prices[1], prices[0],))
    connection.commit()
    #print('price ', sku1, 'inserted')

######### filling the product table with products

cursor.execute('''SELECT img_crop, photo_id From photo ''')
photos = cursor.fetchall()
#print(photos)
cursor.execute('''SELECT short_size , long_size , size_id From size ''')
sizes = cursor.fetchall()
#print(sizes)
cursor.execute('''SELECT finish_sku, finish_id From finish ''')
finishes = cursor.fetchall()
# print(finishes)
possibleprints = [(x,y,z) for x in photos for y in sizes for z in finishes]


######possible photos has form ((crop, id), (short side, size id), (finish, finish, id)
print('Collecting printable photos and adding to database:', database_name)
products=[]
#print(products)
for possibleprint in possibleprints:
    if possibleprint[0][0].split()[0] <= possibleprint[0][0].split()[2]:
        shortedge = int(possibleprint[0][0].split()[0])
        longedge = int(possibleprint[0][0].split()[2])
    else:
        shortedge = int(possibleprint[0][0].split()[2])
        longedge = int(possibleprint[0][0].split()[0])
    photo_id = possibleprint[0][1]
    size_id = possibleprint[1][2]
    shortinches = possibleprint[1][0]
    longinches = possibleprint[1][1]
    finish_id = possibleprint[2][1]
    finish_sku = possibleprint[2][0]
    aspectratio = shortedge/longedge
    printcombos = ((longedge, shortedge, aspectratio,  photo_id, size_id, shortinches, longinches, finish_sku, finish_id))
    if finish_sku == 'CAN19SC' and shortinches == 8 and shortedge/shortinches >= 250 and longinches == round(shortinches/aspectratio):
        products.append(printcombos)
    if finish_sku  == 'FA308HPR' and shortinches == 8 and shortedge/shortinches >= 280 and longinches == round(shortinches/aspectratio):
        products.append(printcombos)
    if finish_sku  == 'PP240LPP' and shortinches == 8 and shortedge/shortinches >= 280 and longinches == round(shortinches/aspectratio):
        products.append(printcombos)
    if finish_sku == 'CAN19SC' and shortinches == 12 and shortedge/shortinches >= 150 and longinches == round(shortinches/aspectratio):
        products.append(printcombos)
    if finish_sku  == 'FA308HPR' and shortinches == 12 and shortedge/shortinches >= 180 and longinches == round(shortinches/aspectratio):
        products.append(printcombos)
    if finish_sku  == 'PP240LPP' and shortinches == 12 and shortedge/shortinches >= 180 and longinches == round(shortinches/aspectratio):
        products.append(printcombos)
    if finish_sku == 'CAN19SC' and shortinches == 16 and shortedge/shortinches >= 120 and longinches == round(shortinches/aspectratio):
        products.append(printcombos)
    if finish_sku  == 'FA308HPR' and shortinches == 16 and shortedge/shortinches >= 150 and longinches == round(shortinches/aspectratio):
        products.append(printcombos)
    if finish_sku  == 'PP240LPP' and shortinches == 16 and shortedge/shortinches >= 150 and longinches == round(shortinches/aspectratio):
        products.append(printcombos)
    if finish_sku == 'CAN19SC' and shortinches == 20 and shortedge/shortinches >= 100 and longinches == round(shortinches/aspectratio):
        products.append(printcombos)
    if finish_sku  == 'FA308HPR' and shortinches == 20 and shortedge/shortinches >= 125 and longinches == round(shortinches/aspectratio):
        products.append(printcombos)
    if finish_sku  == 'PP240LPP' and shortinches == 20 and shortedge/shortinches >= 125 and longinches == round(shortinches/aspectratio):
        products.append(printcombos)
    if finish_sku == 'CAN19SC' and shortinches == 24 and shortedge/shortinches >= 90 and longinches == round(shortinches/aspectratio):
        products.append(printcombos)
    if finish_sku  == 'FA308HPR' and shortinches == 24 and shortedge/shortinches >= 110 and longinches == round(shortinches/aspectratio):
        products.append(printcombos)
    if finish_sku  == 'PP240LPP' and shortinches == 24 and shortedge/shortinches >= 110 and longinches == round(shortinches/aspectratio):
        products.append(printcombos)
    #print(printcombos)
#ppilist=[250,150,120,100,90,280,180,150,125,110]

cursor.execute('''SELECT price_id, finish_id, size_id from prices ''')
prices = cursor.fetchall()
#print(prices)
pricedict = {}
for price in prices:
    pricedict[(price[1], price[2])] = price[0]
    #print(pricedict)


for product in products:
    size_id = list(product)[4]
    finish_id = list(product)[8]
    photo_id = list(product)[3]
    price_id = pricedict.get((finish_id, size_id))
    #print('product is: ', photo_id, price_id, finish_id, size_id)
#print(len(products))

####create products by adding to db when all things work.

    if price_id != None:

        cursor.execute('''INSERT INTO product (price_id, size_id, finish_id, photo_id)
        VALUES (%s, %s, %s, %s)''', (price_id, size_id, finish_id, photo_id,))
        connection.commit()
        #print('product ', photo_id, 'inserted at another size')
    #else:
        #print("no price for this size")



#######collecting the products and creating csvs

import csv
print('We need to export your products as a CSV for import into WooCommerce.')
print('There will be two files, one for parent products and one for all the variations of every parent product.')
#####ask for two file names and open them, prepare to write as CSV
woocomparentfilename = input('What would you like to call the name of the file with your parent products? ')
woocomvariationfilename = input('And the file for the variations. What should we call it?')
woocomcsvpar = open(woocomparentfilename+'.csv', mode='w')
woocomcsvpar = csv.writer(woocomcsvpar, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
woocomcsvvar = open(woocomvariationfilename+'.csv', mode='w')
woocomcsvvar = csv.writer(woocomcsvvar, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)


#CSV headers are defined by woocommerce
csv_headers = ("ID","Type","SKU", "Name","Published","Is featured?","Visibility in catalog","Short description","Description","Date sale price starts","Date sale price ends","Tax status","Tax class","In stock?","Stock","Low stock amount","Backorders allowed?","Sold individually?","Weight (kg)","Length (cm)","Width (cm)","Height (cm)","Allow customer" "reviews?","Purchase note","Sale price","Regular price","Categories","Tags","Shipping class","Images","Download limit","Download expiry days","Parent","Grouped products","Upsells","Cross-sells","External URL","Button text","Position","Attribute 1 name","Attribute 1 value(s)","Attribute 1 visible","Attribute 1 global","Attribute 2 name","Attribute 2 value(s)","Attribute 2 visible","Attribute 2 global")
woocomcsvpar.writerow(list(csv_headers))
woocomcsvvar.writerow(list(csv_headers))

#### select product details from database
cursor.execute('''SELECT * FROM product JOIN (finish, photo, size, prices) ON (product.size_id = size.size_id AND product.finish_id = finish.finish_id AND product.price_id = prices.price_id AND product.photo_id = photo.photo_id) ORDER BY photo.photo_id''')
photos = cursor.fetchall()
###determine which photos ids are used (ie the product parents)
photosused = []
for photo in photos:
    if photo[1] not in photosused:
        photosused.append(photo[1])
#print(photosused)
#extra description on images says contact us if you want other sizes. Find the website address



genericdescription = f'''<p>Prints are made to order and generally take 2- 3 days for production before shipping. As prints are made to order <a href="{websiteurl}/store/refunds">refunds</a> are unfortunately not possible. <a href="{websiteurl}/store/refunds">More info is available here</a>.</p>
<p>Express delivery is included in the price for EU and US customers. This is usually 2-3
days from when the print is ready. As my printer has locations worldwide nearly all other destinations are included as well. Times may vary. Check the <a href="{websiteurl}/store/deliveries">delivery page</a> for details.</p>
<p>Prodigi is my printing partner. I have chosen them for their print quality and ability to print and ship locally. Find out more <a href ="{websiteurl}about/printing">here.</a></p>
<p>Discrepancies in computer and phone screens can lead to colours looking different when printed. Even if your screen has been calibrated colours can display subtle variations on print media.</p>
<p>Print sizes are measured and produced in inches. Centimeter sizes are given for indicative purposes and are not precise.</p>
<p>If think the image would look good on your wall with a different finish or a print size not mentioned above please just send a message with the <a href="#contact">contact form</a>.</p>'''


#for each parent product figure out the finishes, sizes and description etc.
for i in photosused:
    cursor.execute('''SELECT * FROM product JOIN (finish, photo, size, prices) ON (product.size_id = size.size_id AND product.finish_id = finish.finish_id AND product.price_id = prices.price_id AND product.photo_id = photo.photo_id) where photo.photo_id = %s''', (i,))
####ACHTUNG!!!! why is variation used here as a variable? it isn't very descriptive. It is all variations of printable photo, not just the variation of one. ie it is the master photo. Product is used for the variations.
    variations = cursor.fetchall()

    finishes = []
    sizes = []
    for variation in variations:

        if variation[6] not in finishes:
            finishes.append(variation[6])
        if variation[16] not in sizes:
            sizes.append(variation[16])
    csvline_parent = ('', 'variable', str(variation[1])+'IMG', variation[10], 1, 0, 'visible', variation[12], genericdescription ,'','', 'taxable','',1,'','',0,0,'','','','',0,'','', '','Photo Prints','','', variation[11],'','','','','','','','','', 'Finish', ','.join(finishes), 1, 1, 'Size', (('|'.join(sizes)).replace(',',' ')).replace('|', ','),1, 1)
    woocomcsvpar.writerow(list(csvline_parent))

##### sizes needs to be rewritten for woocommerce to change the , in the database for a ;  Then Woo separtes the sizes on a variable product properly
    #print(sizes)
    #print((('|'.join(sizes)).replace(',',';')).replace('|', ','))


#### select product details
cursor.execute('''SELECT * FROM product JOIN (finish, photo, size, prices) ON (product.size_id = size.size_id AND product.finish_id = finish.finish_id AND product.price_id = prices.price_id AND product.photo_id = photo.photo_id) ORDER BY photo.photo_id''')
products = cursor.fetchall()


for product in products:
    #####create sku
    sku=str(product[1])+'IMG'+product[-3]
    #csvline_variation=( 1, 1, str(product[1])+'IMG', 'variation',sku, product[10], product[12], product[12]+'\n'+product[7], product[21], 'Photo Prints', product[11], 'Finish', product[6],'', '', 'Size', product[16].replace(',',';'),'','')
    csvline_variation = ('', 'variation', sku, product[10]+'-'+product[6]+ ', '+product[16], 1, 0, 'visible', product[12], product[7],'','', 'taxable','parent',1,'','',0,0,'','','','',0,'','', product[21],'Photo Prints','','', product[11],'','',str(product[1])+'IMG','','','','','','', 'Finish', product[6], '', 1, 'Size', product[16].replace(',',';'),'', 1)
    woocomcsvvar.writerow(list(csvline_variation))

print('Your CSV for parent products is: ', woocomparentfilename)
print('Your CSV for variations is: ', woocomvariationfilename)
print('Import the parent products into your website first.')

connection.close()

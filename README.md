# Lightroom Product Export for WooCommerce
 Python code to take Lightroom data, store in MySQL and produce csv for WooCommerce products


 This is basically my first code.

 It takes lightroom data from ListView plugin in ods form (check column names) and converts it into a CSV to upload products (photo prints) to a WooCommerce store.


 Input is in the form of .ods spreadsheets for image data and for prices.

 Output is an importable .csv for WooCommerce.

 the program decides what size the images are in pixels and computes what size prints are possible on certain print materiels.

 Descriptions are taken from lightroom for the product parent description and the specific descriptions for the variations are written into the program.

 It runs through a MySQL database to store the data. Why???? because my skills probably weren't anywhere near enough when I wrote the program but I could do it this way.

 If it is useful use it. If you think you can make it more efficient, more reusable by others let me know.

# ocr

Use this to ocr an image with table(s) in it:
+ table2cells.py: use this to split a table into cells
+ img2xls.py: use this to ocr cells then compile them to Excel format.
+ ocr_(engin_name).py: called in img2xls.py (ocr engine)

Usage:
```
python table2cells (image file) (temp dir)
python ../../gadgets/files/list_files.py (temp dir) > (file list).txt
cat (file list).txt | python img2xls.py (excel file)
```

## Example (table2cells.py):
* Original image:

![keishin_1](https://user-images.githubusercontent.com/87534698/227750513-778bfb03-75be-42d0-ba1e-6de9eb8bbde1.png)

* Image with cells overlaid:

![keishin_2](https://user-images.githubusercontent.com/87534698/227750521-a9f27df7-ee22-4a18-b2d0-010a74f589b4.png)

* Extracted cells:
![keishin_3](https://user-images.githubusercontent.com/87534698/227750524-43d0da39-b33c-42f5-81e0-e74459173639.png)

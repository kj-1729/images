# -*- encoding: utf-8 -*-

import openpyxl
import sys
import re

#from ocr_tesseract import ocr
from ocr_google_cloud_vision import ocr

class img2xls:
	def __init__(self, xls_path):
		self.create_xls(xls_path)
		self.ocr = ocr()
	
	# self.wb: Excel workbook
	# self.sheet: active sheet in Excel
	def create_xls(self, xls_path):
		self.xls_path = xls_path

		self.wb = openpyxl.Workbook()
		self.sheet = self.wb.active
		self.sheet.title = 'data'
		self.wb.save(self.xls_path)
	
	def close_xls(self):
		self.wb.save(self.xls_path)
		self.wb.close()
	
	def set_offset(self, offset_row, offset_col):
		self.offset_row = offset_row
		self.offset_col = offset_col
	
	def img2xls(self, img_fname, img_path):
		m = re.search('(\d+)_(\d+)\.jpg', img_fname)
		if m is not None:
			idx_row = int(m.group(1)) + self.offset_row
			idx_col = int(m.group(2)) + self.offset_col
			
			txt = self.img2txt(img_path)
			print(f'{idx_row}, {idx_col}: {txt}')
			self.sheet.cell(row=idx_row, column=idx_col).value = txt

	def img2txt(self, img_path):
		self.txt = self.ocr.img2txt(img_path)
		return self.txt
		

def main():
	if len(sys.argv) < 2:
		sys.stderr.write('usage: cat filelist | python img2xls.py (xls_fname)\n')
		sys.exit(1)
		
	hd = img2xls(sys.argv[1])
	
	for loop in range(4):
		header = sys.stdin.readline()
		
	idx = 0
	for line in sys.stdin:
		data = line[:-1].split('\t')
		if data[4] == 'jpg':
			img_fname = data[5]
			img_path = data[7]
			hd.set_offset(1, 1)
			hd.img2xls(img_fname, img_path)
		idx += 1
	hd.close_xls()

if __name__ == '__main__':
	main()


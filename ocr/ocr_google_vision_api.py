# -*- coding:utf8 -*-

import sys
import io
import os
from google.cloud import vision
from google.oauth2 import service_account

class CFG:
	num_headers = 4

	idx_seqno = 0
	idx_fullpath = 7
	idx_dir = 6

	root_dir = r'C:\Users\Koji\Documents\programs\python\devel\ocr'
	credentials_fname = '(credential_file_name).json'

	
class ocr:
	def __init__(self):
		credentials_fullpath = os.path.join(CFG.root_dir, CFG.credentials_fname)
		credentials = service_account.Credentials.from_service_account_file(credentials_fullpath)
		self.client = vision.ImageAnnotatorClient(credentials=credentials)

	def img2txt(self, image_fullpath):
		print(f'image: {image_fullpath}')
		with open(image_fullpath, 'rb') as fp:
		    content = fp.read()

		image = vision.Image(content=content)
		response = self.client.document_text_detection(image=image)
		
		self.txt = response.full_text_annotation.text

		return self.txt

	def save_txt(text_fullpath):
		with open(text_fullpath, 'w', encoding='utf-8') as fp:
			fp.write(self.txt)

def main():
	ocr_hd = ocr()
	for loop in range(CFG.num_headers):
		header = sys.stdin.readline()

	for line in sys.stdin:
		data = line[:-1].split('\t')
		img_fullpath = data[CFG.idx_fullpath]
		txt_fullpath = os.path.join(data[CFG.idx_dir], data[CFG.idx_seqno] + '.txt')
		ocr_hd.img2txt(img_fullpath)
		ocr_hd.save_text(txt_fullpath)

if __name__ == '__main__':
	main()


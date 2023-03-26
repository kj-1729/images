# -*- coding:utf8 -*-

import sys
import os
from PIL import Image
import pyocr
  
class CFG:
	num_headers = 4

	idx_seqno = 0
	idx_fullpath = 7
	idx_dir = 6
	
class ocr:
	def __init__(self):
		path='C:\\Program Files\\Tesseract-OCR\\'
		os.environ['PATH'] = os.environ['PATH'] + path

		pyocr.tesseract.TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
		self.tools = pyocr.get_available_tools()
		self.tool = self.tools[0]
		
		#  0　テキストの傾斜角度や言語の種類を検知（OSD）して出力
		#  1　OSDありでOCR（回転した画像にも対応してOCR可）
		#  2　OSDなしでテキストの傾斜角度情報を標準出力（OCRなし）
		#  3　OSDなしでOCR（デフォルトの設定はこれ）
		#  4　単一列にさまざまなテキストサイズが入り混じったものと想定してOCR
		#  5　縦書きのまとまった文章と想定してOCR
		#  6　横書きのまとまった文章と想定してOCR
		#  7　一行の文章と想定してOCR
		#  8　一単語と想定してOCR
		#  9　円の中に一単語がある想定でOCR（①、➁など）
		# 10　一文字と想定してOCR
		# 11　順序を気にせずできるだけ画像内に含まれる文章をOCRで取得
		# 12　OSDありでできるだけ画像内に含まれる文章をOCRで取得
		# 13　Tesseract固有の処理を飛ばして一行の文章としてOCR処理
		self.tesseract_layout = 6

	def img2txt(self, image_fullpath):
		img = Image.open(image_fullpath)
		builder = pyocr.builders.TextBuilder(tesseract_layout=self.tesseract_layout)
		self.text = self.tool.image_to_string(img, lang="jpn", builder=builder)
		
		return self.text
		
	def save_txt(self, text_fullpath):
		with open(text_fullpath, 'w') as fp:
			print(self.text, file=fp)

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


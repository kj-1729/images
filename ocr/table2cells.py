# -*- encoding: utf-8 -*-
import sys
import cv2
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import os

class params:
	threshold_color = 200
	threshold_min_line_share = [0.015, 0.03] # v, h
	threshold_dup_rate = 0.6

class image_handler:
	def __init__(self, params):
		self.params = params
	
	#########################################################
	#                                                       #
	#                 Function: read_img                    #
	#                                                       #
	#########################################################
	# - input: img_path
	# - output:
	#  - self.img_BGR
	#  - self.img (RGB)
	#  - self.img_gray
	#  - self.img_bin
	def read_img(self, img_path):
		self.img_path = img_path
		self.img_BGR = cv2.imread(self.img_path)
		self.img = cv2.cvtColor(self.img_BGR, cv2.COLOR_BGR2RGB)

		self.get_stat()
		self.img_RGB2GRAY()
		self.img_thresholding()

		return self.img

	#########################################################
	#                                                       #
	#                 Function: line_detector               #
	#                                                       #
	#########################################################
	# - input: self.img_bin
	# - output:
	#  - self.hlines, self.vlines ([[xmin, ymin, xmax, ymax], [xmin, ymin, xmax, ymax], [xmin, ymin, xmax, ymax], ...])
	#  - self.cells ([[xmin, ymin, xmax, ymax], [xmin, ymin, xmax, ymax], [xmin, ymin, xmax, ymax], ...])
	#  - self.vpoints, hpoints ([y0, y1, y2, y3, ...], [x0, x1, x2, x3, ...])
	def line_detector(self):
		self.search_lines('h')
		self.dedup_lines('h')
		print(f'##### {len(self.hlines)} hlines detected')
		print(self.hlines)

		self.search_lines('v')
		self.dedup_lines('v') 
		print(f'##### {len(self.vlines)} vlines detected')
		print(self.vlines)

		self.extract_cells()
		print(f'##### {len(self.cells)} cells detected')
		print(self.cells)
	
	#########################################################
	#                                                       #
	#                 Function: search_lines                #
	#                                                       #
	#########################################################
	# search_lines
	# - input: self.img_bin
	# - output: self.hlines, self.vlines ([[xmin, ymin, xmax, ymax], [xmin, ymin, xmax, ymax], [xmin, ymin, xmax, ymax], ...])
	def search_lines(self, direction='h'):
		lines = []
		if direction == 'h':
			for idx_y in range(self.stat[0]):
				prev_color = 1
				prev_idx_x = 0
				for idx_x in range(self.stat[1]):
					if self.img_bin[idx_y, idx_x] != prev_color:
						if prev_color == 0 and (idx_x - prev_idx_x) / self.stat[1] >= self.params.threshold_min_line_share[1]:
							lines.append([prev_idx_x, idx_y, idx_x-1, idx_y])
						prev_idx_x = idx_x
						prev_color = (prev_color+1) % 2
				if prev_color == 0 and (self.stat[1]-1 - prev_idx_x) / self.stat[1] >= self.params.threshold_min_line_share[1]:
							lines.append([prev_idx_x, idx_y, self.stat[1]-1, idx_y])

			self.hlines = lines
		else:
			for idx_x in range(self.stat[1]):
				prev_color = 1
				prev_idx_y = 0
				for idx_y in range(self.stat[0]):
					if self.img_bin[idx_y, idx_x] != prev_color:
						if prev_color == 0 and (idx_y - prev_idx_y) / self.stat[0] >= self.params.threshold_min_line_share[0]:
							lines.append([idx_x, prev_idx_y, idx_x, idx_y-1])
						prev_idx_y = idx_y
						prev_color = (prev_color+1) % 2
				if prev_color == 0 and (self.stat[0]-1 - prev_idx_y) / self.stat[0] >= self.params.threshold_min_line_share[0]:
							lines.append([idx_x, prev_idx_y, idx_x, self.stat[0]-1])

			self.vlines = lines

	#########################################################
	#                                                       #
	#                 Function: dedup_lines                 #
	#                                                       #
	#########################################################
	# dedup_lines
	# - input: self.hlines, vlines
	# - output: self.hlines, self.vlines (deduplicated)
	def dedup_lines(self, direction='h'):
		new_lines = []
		if direction == 'h':
			idx = 0
			while idx < len(self.hlines):
				this_line = self.hlines[idx]
				offset = 1
				idx2 = idx+1
				while idx2 < len(self.hlines):
					test_line = self.hlines[idx2]
					if this_line[1] <= test_line[1] and test_line[1] <= this_line[1]+offset:
						xmin_left, xmin_right = sorted([this_line[0], test_line[0]])
						xmax_left, xmax_right = sorted([this_line[2], test_line[2]])
						if (xmax_left - xmin_right)/(xmax_right-xmin_left) >= self.params.threshold_dup_rate:
							self.hlines.pop(idx2)
							this_line =[xmin_left, this_line[1], xmax_right, test_line[3]]
							offset = test_line[1] - this_line[1] + 1
						else:
							idx2 += 1
					else:
						idx2 += 1
				new_lines.append(this_line)
				idx += 1
			self.hlines = new_lines
		else:
			idx = 0
			while idx < len(self.vlines):
				this_line = self.vlines[idx]
				offset = 1
				idx2 = idx+1
				while idx2 < len(self.vlines):
					test_line = self.vlines[idx2]
					if this_line[0] <= test_line[0] and test_line[0] <= this_line[0]+offset:
						ymin_upper, ymin_lower = sorted([this_line[1], test_line[1]])
						ymax_upper, ymax_lower = sorted([this_line[3], test_line[3]])
						if (ymax_upper - ymin_lower)/(ymax_lower-ymin_upper) >= self.params.threshold_dup_rate:
							self.vlines.pop(idx2)
							this_line =[this_line[0], ymin_upper, test_line[2], ymax_lower]
							offset = test_line[0] - this_line[0] + 1
						else:
							idx2 += 1
					else:
						idx2 += 1
				new_lines.append(this_line)
				idx += 1
			self.vlines = new_lines

	#########################################################
	#                                                       #
	#                 Function: extract_cells               #
	#                                                       #
	#########################################################
	# extract_cells
	# - input: self.hlines, vlines
	# - output: self.cells, self.vpoints, self.hpoints
	def extract_cells(self):
		self.cells = []
		self.cells_topleft = []
		v_points = {}
		h_points = {}

		this_margin = 5
		for idx_hlines in range(len(self.hlines)):
			xmin, ymin, xmax, ymax = self.hlines[idx_hlines]

			# set div points on self.hlines[idx_hlines]
			# points = [[xmin0, xmax0], [xmin1, xmax1], [xmin2, xmax2], ...]
			points = []
			points.append([xmin, xmin])
			for idx_vlines in range(len(self.vlines)):
				this_vline = self.vlines[idx_vlines]
				if xmin <= this_vline[0] and this_vline[2] <= xmax and this_vline[1] <= ymax and ymax < this_vline[3]:
					if xmin == this_vline[0]:
						points.pop(0)
					points.append([this_vline[0], this_vline[2]])
			if xmax > points[len(points)-1][1]:
				points.append([xmax, xmax])
			
			for idx in range(len(points)-1):
				pt_left = points[idx]
				pt_right = points[idx+1]

				# find a cell (rectangle) with edge 'pt_left - pt_right'
				min_y = self.stat[0]
				for this_vline in self.vlines:
					if this_vline[0] + this_margin < pt_right[0] and this_vline[2] - this_margin > pt_left[1] and this_vline[3] > ymax and this_vline[1] < min_y:
						min_y = this_vline[1]

				for idx_hlines_2 in range(idx_hlines+1, len(self.hlines)):
					this_hline = self.hlines[idx_hlines_2]
					if this_hline[0] < pt_right[0] and this_hline[2] > pt_left[1] and this_hline[3] > ymax and this_hline[1] < min_y:
						min_y = this_hline[1]

				if min_y > ymax and min_y < self.stat[0]:
					self.cells.append([pt_left[1]+1, ymax+1, pt_right[0], min_y])
					v_points[ymax+1] = 1
					h_points[pt_left[1]+1] = 1

				self.cells_topleft.append([pt_left[1], ymax, pt_left[1], ymax])

		# def vpoints = {y0: 0, y1: 1, y2: 2, ...}, hpoints = {x0: 0, x1: 1, x2: 2, ...}
		self.vpoints = {}
		self.hpoints = {}
		idx = 0
		for y in sorted(v_points.keys()):
			self.vpoints[y] = idx
			idx += 1

		idx = 0
		for x in sorted(h_points.keys()):
			self.hpoints[x] = idx
			idx += 1

	#########################################################
	#                                                       #
	#              Function: img_RGB2GRAY                   #
	#                                                       #
	#########################################################
	# img_RGB2GRAY
	# - input: self.img
	# - output: self.img_gray
	def img_RGB2GRAY(self):
		self.img_gray = cv2.cvtColor(self.img, cv2.COLOR_RGB2GRAY)
		return self.img_gray

	#########################################################
	#                                                       #
	#             Function: img_thresholding                #
	#                                                       #
	#########################################################
	# img_thresholding
	# - input: self.img_gray
	# - output: self.img_bin
	def img_thresholding(self):
		th, self.img_bin = cv2.threshold(self.img_gray, self.params.threshold_color, 1, cv2.THRESH_BINARY)
		return self.img_bin

	#########################################################
	#                                                       #
	#                 Function: get_img                     #
	#                                                       #
	#########################################################
	# get_img
	# - output: self.img
	def get_img(self):
		return self.img

	#########################################################
	#                                                       #
	#                 Function: get_stat                    #
	#                                                       #
	#########################################################
	# get_stat
	# - input: self.img
	# - output: self.stat ([height, width, channels])
	def get_stat(self):
		self.stat = list(self.img.shape)
		return self.stat

	#########################################################
	#                                                       #
	#              Function: get_img_cell                   #
	#                                                       #
	#########################################################
	# get_img_cell
	# - input: idx (=> idx-th cell)
	# - output: self.cell[idx], self.idx_y, self.idx_x
	def get_img_cell(self, idx):
		this_cell = self.cells[idx]
		self.idx_y = self.vpoints[this_cell[1]]
		self.idx_x = self.hpoints[this_cell[0]]
		print(f'[{idx}] cell[{self.idx_y}, {self.idx_x}] = {this_cell}')
		self.img_cell = self.img[this_cell[1]:this_cell[3], this_cell[0]:this_cell[2], :]
		self.img_cell_BGR = self.img_BGR[this_cell[1]:this_cell[3], this_cell[0]:this_cell[2], :]

		return self.img_cell

	#########################################################
	#                                                       #
	#                 Function: display_img                 #
	#                                                       #
	#########################################################
	# display_img
	# - intput: self.img
	# - output: image
	def display_img(self):
		fig = plt.figure(figsize=(10,10))
		ax = fig.add_subplot(1,1,1)
		ax.imshow(self.img)

	#########################################################
	#                                                       #
	#                 Function: display_a_cell              #
	#                                                       #
	#########################################################
	# - input: idx, self.img_cell
	# - output: image
	def display_a_cell(self, idx):
		self.get_img_cell(idx)
		fig = plt.figure(figsize=(10,10))
		ax = fig.add_subplot(1,1,1)
		ax.imshow(self.img_cell)

	#########################################################
	#                                                       #
	#      Function: display_img_with_cells_overlayed       #
	#                                                       #
	#########################################################
	# - input: self.img, self.vlines, self.hlines, self.cells
	# - output: image
	def display_img_with_cells_overlayed(self):
		fig = plt.figure(figsize=(20,20))
		ax = fig.add_subplot(1,1,1)
		ax.imshow(self.img)
		
		for this_cell in self.cells:
			#print(f'vline: [{this_cell[0]}. {this_cell[1]}] - [{this_cell[2]}, {this_cell[3]}]')
			this_patch = patches.Rectangle((this_cell[0], this_cell[1]), width=(this_cell[2] - this_cell[0]+1), height=(this_cell[3] - this_cell[1]+1), fill=False, color='red')
			ax.add_patch(this_patch)
		
	#########################################################
	#                                                       #
	#              Function: save_cells                     #
	#                                                       #
	#########################################################
	# - input: img_dir, self.img_BGR, self.cells
	# - output: image files
	def save_cells(self, img_dir):
		for idx in range(len(self.cells)):
			self.get_img_cell(idx)
			img_fname = str(self.idx_y).zfill(3) + '_' + str(self.idx_x).zfill(3) + '.jpg'
			img_path = os.path.join(img_dir, img_fname)
			try:
				cv2.imwrite(img_path, self.img_cell_BGR)
			except:
				print(f'Failed to save [{idx}] cells[{self.idx_y}, {self.idx_x}]')

def main():
	if len(sys.argv) < 3:
		sys.stderr.write('Usage; pythom table2cells.py img_filename output_dir\n')
		
	img_path = sys.argv[1]
	output_dir = sys.argv[2]
	
	hd = image_handler(params)
	hd.read_img(img_path)
	hd.line_detector()
	hd.save_cells(output_dir)
	
if __name__ == '__main__':
	main()


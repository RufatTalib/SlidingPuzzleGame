#!/usr/bin/python3

# Author:kochrufet
# Copyright reserved 2022
# Version 3.5

import pygame
import random
import os
import time
from enum import Enum
 
class GameState(Enum):
    Running = 1
    Lose = 2
    Won = 3

class Hole:
	def __init__(self, i = 0):
		self.index = i

class Tile(Hole):
	def __init__(self, i, img):
		Hole.__init__(self, i)

		self.img = img

class GameText():
	def __init__(self, text, font, antialias = False, color = "black", backgroundcolor = 'white'):
		self.text = text
		self.antialias = antialias
		self.color = color
		self.font = font

		self.sw = self.font.render(self.text, self.antialias, self.color)
		self.background = self.sw.copy()
		self.backgroundcolor = backgroundcolor
		self.background.fill(self.backgroundcolor)

		self.rect = self.sw.get_rect()

	def set_pos(self, pos):
		self.rect.center = pos

	def Draw(self, sw):
		sw.blit(self.background,(self.rect.x,self.rect.y))
		sw.blit(self.sw,(self.rect.x,self.rect.y))
		pygame.display.update(self.rect)

	def DrawCenter(self, sw):
		W,H = sw.get_size()
		self.rect.center = (W/2,H/2)
		self.Draw(sw)
	
	def UpdateText(self, text):
		self.text = text
		self.sw = self.font.render(self.text, self.antialias, self.color)
		center = self.rect.center
		self.rect = self.sw.get_rect()
		self.rect.center = center
		self.background = self.sw.copy()
		self.background.fill(self.backgroundcolor)


class Game:
	
	def __init__(self, n):
		pygame.init()
		info = pygame.display.Info()
		w,h = info.current_w/2, info.current_h/2
		self.sw = pygame.display.set_mode((w,h))
		self.sw_w, self.sw_h = w,h
		pygame.display.set_caption('Sliding Puzzle')

		self.clk = pygame.time.Clock()
		self.fps = 30
		self.timer_event = 	pygame.USEREVENT + 1
		pygame.time.set_timer(self.timer_event, 1000)


		# default image
		image_files = tuple(
			map(lambda x: 'images/' + x, os.listdir('images'))
		)


		self.picture = pygame.image.load(image_files[0])
		self.tiles = []


		self.final_piece = None


		self.run = True


		self.pad = 0
		self.rat = 1
		self.num = n
		self.appr = 0.01
		self.softness = 0.01
		self.highlight_width = 5
		self.posx = 0
		self.posy = 0
		self.c = self.num * self.num
		self.hole = Hole(self.c-1)


		pygame.font.init()
		self.font = pygame.font.SysFont('calibri', int( (1/self.num)*100 ))
		self.big_font = pygame.font.SysFont('calibri', int( (1/self.num)*100*3 ))


		


		self.calc_vec_dt = {
			'left' : -1,
			'right' : +1,
			'top' : -self.num,
			'bottom' : self.num
		}


		self.modes = {
			'easy' : 100*self.num**2,
			'normal' : 100*self.num**3,
			'hard' : 100*self.num**4
		}


		self.timers = {
			'easy' : 3600,
			'normal' : 1800,
			'hard' : 600
		}


		self.unit_vect = {
			True : 1,
			False : -1
		}


		self.piece_states = [0] * self.num * self.num

		
		self.bg_color = "#F4F5FA"
		self.mode = 'easy'

		self.sw.fill(self.bg_color)
		pygame.display.update()

		
		self.game_state = GameState.Running


		self.percentage = 0
		self.time_count = self.timers[self.mode]


		self.lose_text = GameText("You Lose !", self.big_font, True, "red", self.bg_color)

		self.percentage_text = GameText("Win percentage: 0 %", self.font, True, "black", self.bg_color)
		self.percentage_text.set_pos((self.sw_w-self.percentage_text.sw.get_width()/2-10, self.percentage_text.sw.get_height()/2+10))

		self.time_text = GameText(self.get_remaining_time(), self.font, True, "black", self.bg_color)
		self.time_text.set_pos((self.time_text.sw.get_width()/2+10, self.time_text.sw.get_height()/2+10))

		self.generate_parts(self.picture)

		self.shuffle()


		self.draw()
		for i_rect in range(self.c):
			pygame.display.update(self.getRect(i_rect))



		self.sw.fill(self.bg_color)
	


	def text(self, x, antialias = True, color = "white"):
		return self.font.render(x, antialias, color)
	
	def calculate_percentage(self):
		number_of_same = 0
		for i in range(0, self.c):
			if i == self.piece_states[i]:
				number_of_same += 1

		self.percentage = round((number_of_same / (self.c-1))*100,2)
		
	def checkForWin(self):
		for i in range(1,self.c):
			if self.piece_states[i-1] > self.piece_states[i]:
				return False

		return True

	def generate_parts(self, picture):
		self.tiles.clear()

		pic = self.resize(picture)
		self.picture = pic.copy()

		W,H = self.sw.get_size()
		w,h = pic.get_size()

		self.posx = W/2 - w/2
		self.posy = H/2 - h/2

		self.highlight = self.picture.get_rect()
		self.highlight.x = self.posx - self.highlight_width/2
		self.highlight.y = self.posy - self.highlight_width/2
		self.highlight.w += self.highlight_width
		self.highlight.h += self.highlight_width
		
		

		self.size_w = pic.get_width() // self.num
		self.size_h = pic.get_height() // self.num
		
		white_block = pygame.Surface((self.size_w, self.size_h))
		white_block.fill("white")

		c = 0
		for y in range(self.num):
			for x in range(self.num):
				img = pic.subsurface( pygame.Rect( x*self.size_w, y*self.size_h, self.size_w, self.size_h) )

				img.blit(self.text(str(c+1)), (5,5))
				
				self.tiles.append( Tile(c,img) )
				c+=1

				self.tile_size = c
				self.c = c

				self.soft_show()

		# remove this piece for movement other parts
		self.final_piece = self.tiles.pop()

		# decorate as white box
		decorbox = pygame.Surface((int(self.size_w),int(self.size_h)))
		decorbox.fill("white")

		self.tiles.append( Tile(c, decorbox) )

		self.hole = Hole(c-1)

		self.tile_size = len(self.tiles)

		

	def soft_show(self):
		self.draw()

	def swap(self, i,j):
		self.tiles[i],self.tiles[j] = self.tiles[j],self.tiles[i]

	def getRandomNeighbour(self, x):
		generator_matrix = [-1,1,-self.num,self.num]
		size = 4
		

		if x%self.num == 0:
			generator_matrix.remove( self.calc_vec_dt['left'] )
			size -= 1

		if (x+1)%self.num == 0:
			generator_matrix.remove( self.calc_vec_dt['right'] )
			size -= 1


		if x < self.num:
			generator_matrix.remove( self.calc_vec_dt['top'] )
			size -= 1
			

		if x >= self.num*self.num - self.num:
			generator_matrix.remove( self.calc_vec_dt['bottom'] )
			size -= 1
		
		random_index = random.randint( 0, size-1 )

		return x + generator_matrix[random_index]

	def shuffle(self):
		past = self.c - 1
		new = self.getRandomNeighbour(past)
		self.swap(past, new)
		
		for repeat in range(self.modes[self.mode]):
			past = new
			new = self.getRandomNeighbour(past)
			self.swap(past, new)

		for i in range(self.c):
			if self.tiles[i].index == self.c:
				self.hole.index = i	

	def resize(self, img):
		W,H = self.sw.get_size()
		w,h = img.get_size()
		cw = (self.num+1)*self.pad + w
		ch = (self.num+1)*self.pad + h

		while cw / self.rat > W: self.rat += self.appr
		while ch / self.rat > H: self.rat += self.appr
		
		w,h = cw/self.rat, ch/self.rat

		self.posx = W/2 - w/2
		self.posy = H/2 - h/2

		return pygame.transform.scale(img, (w,h))

	

	def control(self):
		ev = pygame.event.wait()

		if ev.type == pygame.QUIT:
			self.run = False
			return
		if ev.type == pygame.KEYDOWN and ev.key == pygame.K_q:
			self.run = False
			return
		

		if ev.type == pygame.MOUSEBUTTONDOWN:
			mx,my = pygame.mouse.get_pos()
			
			if self.game_state == GameState.Running:
				self.check_blocks(mx,my)

		if ev.type == self.timer_event and self.game_state == GameState.Running:
			self.time_count -= 1
			self.time_text.UpdateText(self.get_remaining_time())

			if self.time_count <= 0:
				self.game_state = GameState.Lose
				self.draw()
	
	def check_blocks(self,mx,my):
		for i in range(self.c):
				if self.getRect(i).collidepoint((mx,my)):

					hx,hy = self.getCoordinate(self.hole.index)
					cx,cy = self.getCoordinate(i)
					if hx == cx and hy == cy:
						break

					factor = self.unit_vect[ i > self.hole.index ]

					if cx == hx:
						
						for k in range(self.hole.index + self.num*factor, i+self.num*factor, self.num*factor):
							r1 = self.getRect(self.hole.index)
							r2 = self.getRect(k)

							self.swap(self.hole.index, k)
							self.hole.index = k
							self.draw()
							pygame.display.update((r1,r2))

					if cy == hy:

						for k in range(self.hole.index + factor, i+factor, factor):
							r1 = self.getRect(self.hole.index)
							r2 = self.getRect(k)



							self.swap(self.hole.index, k)

							self.hole.index = k
							self.draw()
							pygame.display.update((r1,r2))
							

					for i in range(self.c):
						if self.piece_states[i] != self.tiles[i].index:
							self.piece_states[i] = self.tiles[i].index


					self.calculate_percentage()
					self.percentage_text.UpdateText("Win percentage: " + str(self.percentage) + " %")
					self.draw()
					self.clk.tick(self.fps)



					if self.checkForWin():
						self.game_state = GameState.Won
						self.draw()
						return



					break

	def getCoordinate(self, i):
		return (i%self.num)*(self.size_w+self.pad), (i//self.num)*(self.size_h+self.pad)

	def getRect(self, i):
		x,y = self.getCoordinate(i)
		w,h = self.size_w,self.size_h

		return pygame.Rect(x+self.posx, y+self.posy, w,h)

	def drawTiles(self):
		for i in range(self.c):
			x,y = self.getCoordinate(i)
			self.sw.blit(self.tiles[i].img, (x + self.posx, y + self.posy) )

	def draw(self):
		self.sw.fill(self.bg_color)

		if self.game_state == GameState.Running:
			self.drawTiles()

		elif self.game_state == GameState.Won:
			self.sw.blit(self.picture, (self.posx, self.posy))
			pygame.draw.rect(self.sw, "green", self.highlight, self.highlight_width)
			pygame.display.set_caption("You Won !")
			pygame.display.update()

		elif self.game_state == GameState.Lose:
			self.drawTiles()
			self.lose_text.DrawCenter(self.sw)
			pygame.display.update()
		
		
		time.sleep(self.softness)
	
	def get_remaining_time(self):
		response = ""
		time_count = self.time_count
		if time_count >= 3600:
			response += str(time_count//3600).zfill(2) + ":"
			time_count = time_count % 3600
		if time_count >= 60:
			response += str(time_count//60).zfill(2) + ":"
			time_count = time_count % 60
		response += str(time_count).zfill(2)

		return "Remaining time: " + response
	

	def mainloop(self):
		while self.run:
			self.control()
			self.time_text.Draw(self.sw)
			self.percentage_text.Draw(self.sw)


	def __del__(self):
		pygame.quit()		

game = Game(5)
game.mainloop()



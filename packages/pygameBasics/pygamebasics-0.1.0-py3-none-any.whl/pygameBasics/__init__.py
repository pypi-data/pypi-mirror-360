import time
import math
import os
import random
import sys
import threading
import inspect
import functools
import string
from safeImport import safe_import
import atexit
safe_import('pygame')
safe_import('mouse')
safe_import('keyboard')
safe_import('pyautogui')

if  __name__ != '__main__':
	RUNNING = False
	caller_globals = inspect.stack()[1].frame.f_globals
else:
	caller_globals = globals()

class GUI:
	k = keyboard
	m = mouse
	g = pyautogui

G = GUI

def getGlobal(v):
	global caller_globals
	
	def _print(*args, **kwargs):
		""" Debug Print: Add '#' before print below to hide debug messages """
		#print(*args, **kwargs)
		pass

	temp = []
	val = ''

	def get(r):
		nonlocal temp, val
		_print('get(r) done at:    ', r)

		if '[' in r and ']' == r[len(r)-1]:
			idx = r.index('[')
			_idx = len(r) - [t for t in [_ for _ in r].__reversed__()].index(']')
			temp.append(r[:idx])
			_print('indexed new lists:    ', r[idx:_idx], '\t', r[idx+1:_idx-1])
			_print('temp current:    ', temp)
			_print('r:    ', r)
			if '[' == r[idx:_idx][0] and ']' in r[idx+1:_idx-1]:
				ti = r.index(']')
				_print('got ] location index:    ', ti)
				r = r[:ti] + r[ti+1:]
				_print('list after removing]:    ', r)
				get(r[idx+1:_idx])
			else:
				get(r[idx+1:_idx-1])
		else:
			temp.append(r)
			temp = list(map(lambda x: x.strip("""'"""), temp))
			_print('list generated:    ', temp)
			val = caller_globals[temp[0]]
			for ab in temp[1:]:
				_print('val beg:    ', val)
				val = val[eval(ab.strip("""'"""))]
				_print('val end:    ', val, end='\n\n')
			_print('val prepared:    ', val)
			return

	get(v)
	_print('value got:   ', val)
	return val
getG = getGlobal

def exportDecorator(func):
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		global caller_globals
		result = func(*args, **kwargs)
		
		for item in globals().keys():
			if not item in ['__name__', '__all__', func.__name__]:
				caller_globals[item] = globals()[item]
				
		return result
	return wrapper

class paths:
	if __name__ == '__main__':
		base_path = r"C:\Users\Siddharth\Pictures\pictures"
		image1 = os.path.join(base_path, 'DP.jpg')
		image2 = os.path.join(base_path, 'DP_circle.png')

class WINDOW:
	WIDTH = 1200
	HEIGHT = 600
	w = WIDTH
	h = HEIGHT
	size = (w,h)
	
class config:
	WINDOWTITLE = 'Pygame'
	debug = False
	def atExit():
		pass
	#atExit = lambda: print('', end='')
	size = 40
	speed = 4
	centerX, centerY = 0, 0
	stampSpamMode = False
	showMask = False
	backgroundColor = (255, 255, 255)
	LOG = ''
	FPS = 60
	smoothWait = 0.1
	class strings:
		a2z = 'abcdefghijklmnopqrstuvwxyz'
		A2Z = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
		num = '0123456789'
		allChar = a2z + A2Z + num
		alph = a2z + A2Z	
	key_map = {
		"Player1": (pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_e, pygame.K_z, pygame.K_x, pygame.K_LSHIFT),
		"Player2": (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_0, pygame.K_5, pygame.K_2, pygame.K_RSHIFT),
	}
	class mouse:
		x = 0
		y = 0
		down = False
		clicked = False
	noCollide = ['Text', 'Box', 'Stamp', 'Line', 'Polygon']
	class screen:
		WIDTH = G.g.size()[0]
		HEIGHT = G.g.size()[1]
		w = WIDTH
		h = HEIGHT
		size = (w,h)
		

class temp:
	for x in string.ascii_lowercase:
		globals()[x] = None
	
t = temp

def SMOOTH(wait=None):
	if not wait: wait = config.smoothWait
	time.sleep(wait)

class colors:
	RED = (255, 0, 0)
	WHITE = (255, 255, 255)
	GREEN = (0, 255, 0)
	BLUE = (0, 0, 255)
	CYAN = (0, 255, 255)
	YELLOW = (255, 255, 0)
	PURPLE = (255, 0, 255)
	BLACK = (0, 0, 0)

def startConfigSync(data_dict):
	data_dict = getG(data_dict)
	def main():
		while True:
			for key in data_dict.keys():
				try:
					data_dict[key] = getG(key)
				except Exception as e:
					print(f'SYNC ERROR:    {e}')
			
			SMOOTH()
	
	Script(main)

#@exportDecorator
def INITIALIZE():
	global SCREEN, CLOCK, RUNNING, win, ENTITIES, SCRIPTS, BROADCASTS, caller_globals, STAMPS
	
	caller_globals = inspect.stack()[1].frame.f_globals
	atexit.register(lambda: config.atExit())
	
	win = WINDOW()
	config.centerX, config.centerY = win.w // 2, win.h // 2
	pygame.init()
	pygame.font.init()
	pygame.mixer.init()
	RUNNING = True

	ENTITIES = []
	SCRIPTS = []
	STAMPS = []

	SCREEN = pygame.display.set_mode(win.size)
	CLOCK = pygame.time.Clock()
	BROADCASTS = {'clonesCreated' : False}
	
	for _ in ['SCREEN', 'win', 'ENTITIES', 'SCRIPTS', 'BROADCASTS', 'RUNNING', 'CLOCK']:
		caller_globals[_] = globals()[_]

def limit(value, _min, _max):
	return max(_min, min(_max, value))

class Script:
	def __init__(self, function, starter='RUNNING'):
		global SCRIPTS
		self.function = function
		self.starter = starter

		def main():
			global caller_globals
			with threading.Lock():
				while True:
					if getG(self.starter):
						#try:
						self.function()
						#except NameError:
						#except Exception as e:
						#	if RUNNING: print(f"SCRIPT ERROR:    {e}\nIn {self.function.__name__}\n")
						#	break
						
						if self.starter == 'RUNNING': break

		self.id = len(SCRIPTS)
		SCRIPTS.append(main)

		threading.Thread(target=SCRIPTS[self.id], daemon=True).start()

class Entity:
	def __init__(self, size=None, sizeX=None, sizeY=None, color=colors.BLACK, shape='rect', x=None, y=None, type='Entity', name=None, image=None, hidden=False, variables=None, attributes=[], collider=None, sounds={}):
		self.name = name
		self.transparency = 0
		self.brightness = 0
		self.x =  config.centerX if x is None else x
		self.y = config.centerY if y is None else y
		self.direction = 0
		self.shape, self.color, self.type = shape, color, type
		self.sizeX, self.sizeY = size if size else sizeX, size if size else sizeY
		self.sizeX, self.sizeY = 0 if not sizeX else sizeX, 0 if not sizeY else sizeY
		self.image = remove_transparent_pixels(pygame.image.load(image).convert_alpha()) if image else None
		self.image_path = image
		self.hidden = hidden
		self.config = attributes
		self.old_sizeX, self.old_sizeY, self.old_x, self.old_y, self.old_direction = None, None, None, None, None
		self.clones, self.variables = [], {} if not variables else variables
		self._vars = self.variables
		self._vars['isRect'] = True if not self.image else False
		self._vars['collider'] = collider
		self.deleted = False
		self.stamps = []
		self.boxCord = self.x + 130, self.y + 5, 150, 40

		if self.image:
			self.sizeX = self.image.get_width()
			self.sizeY = self.image.get_height()
			self.mask = pygame.mask.from_surface(self.image)
		else:
			self.image = pygame.Surface((self.sizeX, self.sizeY)).convert()
			self.image.fill(self.color)
			self.mask = None

		self.rect = self.image.get_rect(topleft=(self.x, self.y))
		self.original_image = self.image.copy()
		self._vars['originalSize'] = (self.sizeX, self.sizeY)

		if self.type != "Stamp":
			if 'start at random position' in self.config:
				tmp = 0
				while self.check_collisions() and tmp < 10:
					self.x = random.randint(0, win.w - self.sizeX)
					self.y = random.randint(0, win.h - self.sizeY)
					tmp += 1
				del tmp

		if self.type != "Stamp":
			ENTITIES.append(self)
		else:
			STAMPS.append(self)

	def touching(self, other):
		if other == '__mouse__':
			'''
			if config.mouse.x > self.x and config.mouse.y > self.y:
				if config.mouse.x < ((config.screen.w - win.w)/2 + self.x + self.sizeX):
					if config.mouse.y < ((config.screen.h - win.h)/2 + self.y + self.sizeY):
						return True
			return False
			'''
			
			if not self.rect.collidepoint(config.mouse.x, config.mouse.y):
				return False
			elif not self.mask:
				return True
			
			relative_x = config.mouse.x - self.rect.x
			relative_y = config.mouse.y - self.rect.y

			return self.mask.get_at((relative_x, relative_y))
	
		if self.mask and other.mask:
			offset = (other.rect.x - self.rect.x, other.rect.y - self.rect.y)
			return self.mask.overlap(other.mask, offset) is not None

		return self.rect.colliderect(other.rect)

	def check_collisions(self, _old_x=None, _old_y=None, _old_sizeX=None, _old_sizeY=None, _old_direction=None):
		if self._vars['collider'] == None:
			return False

		for entity in ENTITIES:
			if entity != self and entity.type not in config.noCollide and self.touching(entity):
				if _old_x is not None and _old_y is not None:
					self.x, self.y = _old_x, _old_y
				if _old_sizeX is not None and _old_sizeY is not None:
					self.sizeX, self.sizeY = _old_sizeX, _old_sizeY
				if _old_direction is not None:
					self.direction = _old_direction
				return True
		return False

	def changeXby(self, steps):
		self.x += steps
	chx = changeXby
	
	def changeYby(self, steps):
		self.y -= steps
	chy = changeYby

	def move(self, steps):
		dir = math.radians(self.direction)
		self.old_x, self.old_y = self.x, self.y

		self.changeXby(math.sin(dir) * steps)
		self.check_collisions(_old_x=self.old_x, _old_y=self.y)
		self.changeYby(math.cos(dir) * steps)
		self.check_collisions(_old_x=self.x, _old_y=self.old_y)

	def turn(self, deg):

		self.old_direction = self.direction
		self.direction += deg
		self.check_collisions(_old_direction=self.old_direction)

	def changeSize(self, value):
		self.old_sizeX, self.old_sizeY = self.sizeX, self.sizeY
		new_sizeX, new_sizeY = max(1, self.sizeX * (100 + value)/100), max(1, self.sizeY * (100 + value)/100)
		
		if self.image:
			self.image = pygame.transform.smoothscale(self.original_image, (new_sizeX, new_sizeY))

		self.sizeX, self.sizeY = new_sizeX, new_sizeY
		self.check_collisions(self.old_sizeX, self.old_sizeY)
	chs = changeSize
	
	def setSize(self, value):
		self.old_sizeX, self.old_sizeY = self.sizeX, self.sizeY
		new_sizeX, new_sizeY = max(1, self._vars['originalSize'][0] * (100 + value)/100), max(1, self._vars['originalSize'][1] * (100 + value)/100)
		
		if self.image:
			self.image = pygame.transform.smoothscale(self.original_image, (new_sizeX, new_sizeY))

		self.sizeX, self.sizeY = new_sizeX, new_sizeY
		self.x -= (new_sizeX - self.old_sizeX) / 2
		self.y -= (new_sizeY - self.old_sizeY) / 2
		self.check_collisions(self.old_sizeX, self.old_sizeY)

	def isClicked(self):
		if config.mouse.down:
			return self.rect.collidepoint(config.mouse.x, config.mouse.y)
		return False

	def update(self, keys):
		if not self.type.startswith("Player"):
			return

		self.old_x, self.old_y, self.old_sizeX, self.old_sizeY = self.x, self.y, self.sizeX, self.sizeY
	
		UP, DOWN, LEFT, RIGHT, STAMP, GROW, SHRINK = config.key_map[self.name]

		if keys[UP]: self.move(1)
		if keys[DOWN]: self.move(-1)
		if keys[LEFT]: self.turn(-5)
		if keys[RIGHT]: self.turn(5)
		if keys[STAMP] and config.stampSpamMode: self.stamp()
		if keys[GROW]: self.changeSize(2)
		if keys[SHRINK]: self.changeSize(-2)

		self.x = min(win.w, max(0, self.x))
		self.y = min(win.h, max(0, self.y))

	def get_surface(self):
		if self.image:
			rotated_surf = pygame.transform.rotate(self.image, -self.direction)
			return rotated_surf
		
		rect_surf = pygame.Surface((self.sizeX, self.sizeY), pygame.SRCALPHA)
		pygame.draw.rect(rect_surf, self.color, (0, 0, self.sizeX, self.sizeY))
		rotated_surf = pygame.transform.rotate(rect_surf, -self.direction)
		return rotated_surf

	def draw(self, SCREEN):
		self.boxCord = self.x + 130, self.y + 5, 150, 40
		self.rect = self.image.get_rect(topleft=(self.x, self.y))
		if self.image is None:
			self.color = (*self.color[:3], 255-self.transparency)
			rotated_surf = pygame.Surface((self.sizeX, self.sizeY), pygame.SRCALPHA)
			rotated_surf.fill(self.color)
		else:
			self.image.set_alpha(255-self.transparency)
			if self._vars['isRect']: self.image.fill(self.color)
			rotated_surf = self.get_surface()

		rotated_rect = rotated_surf.get_rect(center=(self.x + self.sizeX // 2, self.y + self.sizeY // 2))

		brightness_surface = pygame.Surface(rotated_surf.get_size(), pygame.SRCALPHA)
		if self.brightness > 0:
			brightness_surface.fill((self.brightness, self.brightness, self.brightness, 0))
			rotated_surf.blit(brightness_surface, (0,0), special_flags=pygame.BLEND_RGBA_ADD)
			config.LOG = 'brightness done'
		elif self.brightness < 0:
			brightness_surface.fill((abs(self.brightness), abs(self.brightness), abs(self.brightness), 0))
			rotated_surf.blit(brightness_surface, (0,0), special_flags=pygame.BLEND_RGBA_SUB)
			config.LOG = 'darkness done'

		SCREEN.blit(rotated_surf, rotated_rect.topleft)

		if config.showMask:
			mask_surf = pygame.mask.from_surface(rotated_surf).to_surface(setcolor=(255, 0, 0, 160), unsetcolor=(0,0,0, 60))
			SCREEN.blit(mask_surf, rotated_rect.topleft)

	def stamp(self, _vars=None, ret=False):
		stamp_entity = Entity(sizeX=self.sizeX, sizeY=self.sizeY, color=self.color, shape=self.shape, x=self.x, y=self.y, type='Stamp', name=self.name, variables=_vars, image=self.image_path)
		stamp_entity.direction = self.direction
		stamp_entity.brightness = self.brightness
		stamp_entity.transparency = self.transparency
		self.stamps.append(stamp_entity)
		if ret:
			return stamp_entity
		
	def createClone(self, ret=False, config=None):
		if not config: config = self.config
		clone = Entity(sizeX=self.sizeX, sizeY=self.sizeY, color=self.color, shape=self.shape, x=self.x, y=self.y, type='Clone', name=self.name, image=self.image_path, variables=self.variables.copy(), attributes=config)
		clone.direction = self.direction
		clone.brightness = self.brightness
		clone.transparency = self.transparency
		self.clones.append(clone)
		if ret:
			return clone

	def askAndWait(self, question):
		box = Box('input', *self.boxCord, prompt=question + ' ')
		response = box.response
		del box
		return response
		
	def sayFor(self, text, timeout=1):
		Box('sayFor', *self.boxCord, prompt=text, _vars={'timeout':timeout})
		
	def say(self, text):
		Box('say', *self.boxCord, prompt=text, _vars={'target':self})

class Box(Entity):
	def __init__(self, boxType, x, y, w, h, font=None, prompt='', _vars={}):
		super().__init__(x=x, y=y, sizeX=w, sizeY=h)
		self.size = [x, y, w, h]
		self.rect = pygame.Rect(*self.size)
		self.color_inactive = colors.BLACK
		self.color_active = colors.BLUE
		self.input = ''
		self.prompt = prompt
		self.hidden = False
		self.font = font if font else pygame.font.Font(None, 28)
		self.active = True
		self.variables = _vars
		self._vars = self.variables
		self.type = "Box"
		self.box = boxType
		self.clones = []
		self.entered_text = ''
		self.deleted = False
		self.last_char = ''
		self.last_time = 0
		
		
		if self.box == 'sayFor':
			self.timeout, self.startTime = self._vars['timeout'], time.time()
		elif self.box == 'say':
			self.target = self._vars['target']
			self.target._vars['msg'] = self.prompt
			
		while G.k.is_pressed('enter'):
			pass
		
		while True:
			self.update()
			if self.box == 'input':
				if self.entered_text:
					self.response = self.entered_text
					self.deleted = True
					break
					
			elif self.box == 'sayFor':
				if time.time() - self.startTime > self.timeout:
					self.deleted = True
					break
					
			elif self.box == 'say':
				def boxThread(target):
					while True:
						if target.target._vars['msg'] == '':
							target.deleted = True
							break
						else:
							target.prompt = target.target._vars['msg']
						
				Script(lambda: boxThread(self), 'RUNNING')

			SMOOTH(config.smoothWait/5)

	def wrap_text(self, text, font, max_width):
		words = text.split()
		lines = []
		current_line = ''

		for word in words:
			test_line = current_line + ' ' + word if current_line else word
			text_width, _ = font.size(test_line)

			if text_width <= max_width and word != '\n':
				current_line = test_line
			else:
				if current_line: lines.append(current_line)

				while font.size(word)[0] > max_width:
					split_point = len(word) * max_width // font.size(word)[0]
					lines.append(word[:split_point])
					word = word[split_point:]

				current_line = word

		if current_line: lines.append(current_line)
		return lines

	def update(self):
		if G.m.is_pressed('left'):
			self.active = self.rect.collidepoint(config.mouse.x, config.mouse.y)
			self.color = self.color_active if self.active else self.color_inactive

		if self.active:		
			for char in [*[_ for _ in config.strings.a2z], *[_ for _ in config.strings.num], ' ', 'backspace']:
				if G.k.is_pressed(char):
					if self.last_char == char:
						if time.time() - self.last_time < 0.2:
							continue
					if char != 'backspace': self.input += char
					if char == 'backspace': self.input = self.input[:-1]
					self.last_char = char
					self.last_time = time.time()
					break

			#if G.k.is_pressed('backspace'):
			#	self.input = self.input[:-1]

			if G.k.is_pressed('enter'):
				self.entered_text = self.input
				self.input = ''
				self.active = False

	def draw(self, SCREEN):
		self.color = self.color_active if self.active else self.color_inactive
		self.text = self.prompt + ':' + '\n' + self.input if self.box == 'input' else self.prompt
		max_width = self.size[2] - 10

		lines = self.wrap_text(self.text, self.font, max_width)
		line_height = self.font.get_height()
		self.size[3] =  10 + len(lines) * line_height
		self.rect.size = (self.size[2], self.size[3])

		pygame.draw.rect(SCREEN, colors.WHITE, self.rect)
		pygame.draw.rect(SCREEN, self.color, self.rect, 2)

		for i, line in enumerate(lines):
			text = self.font.render(line, True, self.color)
			SCREEN.blit(text, (self.rect.x + 5, self.rect.y + 5 + i * line_height))

class Text(Entity):
	def __init__(self, text, x, y, font=None, size=40, align='left', color=colors.BLACK, _vars={}):
		super().__init__(x=x, y=y, size=size)
		self.font = font
		self.size = size
		self.color = color
		self.text = text
		self.x, self.y = x, y
		self.align = align
		self.hidden = False
		self._vars = _vars if _vars else {}
		self.type = "Text"
		self.deleted = False
		self.original_x = self.x
		self.renderText()
		
		#ENTITIES.append(self)   # Already Added in super().__init__()

	def renderText(self):
		try:
			self.FONT = pygame.font.Font(self.font, self.size)
			self.text_surface = self.FONT.render(self.text, True, self.color)
			
			if self.align in ['center', 'centre']: self.x = self.original_x - self.text_surface.get_width() // 2
		except Exception as e:
			print(f'RENDER TEXT ERROR in TEXT {self.text}:    {e}')
		
	def draw(self, SCREEN):
		self.renderText()
		SCREEN.blit(self.text_surface, (self.x, self.y))

	def change(self, name, value):
		if hasattr(self, name):
			setattr(self, name, value)
			#self.renderText()
			if name == 'x': self.original_x = self.x

class Variable(Text):
	def __init__(self, variable, x, y, font=None, size=40, color=colors.BLACK, _vars={}):
		self.variable = variable
		self.x = x
		self.y = y
		self.font = font
		self.size = size
		self.color = color
		self._vars = _vars
		super().__init__(str(getG(self.variable)), self.x, self.y, self.font, self.size, 'center', self.color, self._vars)
		
		def scriptMain(target):
			while not target.deleted:
				new_text = str(getG(self.variable))
				if target.text != new_text: target.change('text', new_text)

				SMOOTH()
				
		Script(lambda: scriptMain(self), 'RUNNING')
	
	def delete(self):
		self.deleted = True

	def change(self, name, value):
		super().change(name, value)

class Line:
	def __init__(self, cord1, cord2, color=colors.BLACK, width=5):
		self.cords = (tuple(map(int, cord1)), tuple(map(int, cord2)))
		self.color = color
		self.width = width
		self.type = 'Line'
		self.hidden = False
		verifyAttributes(self)
		ENTITIES.append(self)
	
	def draw(self, SCREEN):
		if not self.hidden: pygame.draw.line(SCREEN, self.color, self.cords[0], self.cords[1], self.width)

class Polygon:
	def __init__(self, cords, color=colors.BLACK):
		self.cords = cords
		self.color = color
		self.type = 'Polygon'
		self.hidden = False
		self.surface = pygame.Surface(SCREEN.get_size(), pygame.SRCALPHA)
		verifyAttributes(self)
		if self.type not in config.noCollide: config.noCollide.append(self.type)
		ENTITIES.append(self)
	
	def draw(self, SCREEN):
		if not self.hidden: pygame.draw.polygon(self.surface, self.color, self.cords)
		if not self.hidden: SCREEN.blit(self.surface, (0,0))

class Circle:
	def __init__(self, center, radius, width=5, color=colors.BLACK):
		self.radius = radius
		self.center = center
		self.color = color
		self.hidden = False
		self.width = width
		self.type = 'Circle'
		self.surface = pygame.Surface(SCREEN.get_size(), pygame.SRCALPHA)
		verifyAttributes(self)
		if self.type not in config.noCollide: config.noCollide.append(self.type)
		ENTITIES.append(self)
	
	def draw(self, SCREEN):
		if not self.hidden: pygame.draw.circle(self.surface, self.color, self.center, self.radius, self.width)
		if not self.hidden: SCREEN.blit(self.surface, (0,0))

def toggle_mask():
	config.showMask = not config.showMask

def updateTerminal():
	while True:
		with threading.Lock():
			print(len(ENTITIES), end='')
			print('\r', end='')

def verifyAttributes(object):
	#if object in config.verified: return
	if not hasattr(object, 'hidden'): setattr(object, 'hidden', False)
	if not hasattr(object, 'deleted'): setattr(object, 'deleted', False)
	if not hasattr(object, 'clones'): setattr(object, 'clones', [])
	#config.verified.append(object)

#@exportDecorator
def UPDATE():
	global ENTITIES, SCREEN, SCRIPTS, CLOCK, RUNNING, win, STAMPS
	try:
		pygame.display.set_caption(config.WINDOWTITLE)
		SCREEN.fill(config.backgroundColor)

		config.mouse.x, config.mouse.y = pygame.mouse.get_pos()
		keys = pygame.key.get_pressed()
		
		'''
		if not hasattr(config, 'verified'): setattr(config, 'verified', [])
		
		for entity in ENTITIES:
			#if entity in config.verified:
			#	continue
			
			verifyAttributes(entity)
			if not entity.type in ['Entity', 'Clone'] and not entity.type.startswith('Player'): continue
			for clone in entity.clones:
				verifyAttributes(clone)
				for cloneOfClone in clone.clones:
					verifyAttributes(cloneOfClone)
		'''
		
		STAMPS = [e for e in STAMPS if not (e.type == "Stamp" and e._vars.get('erasePerFrame', False))]
		ENTITIES = [e for e in ENTITIES if not e.deleted]
		STAMPS = [e for e in STAMPS if not e.deleted]
		#config.verified = [e for e in config.verified if not e.deleted]
	
		for stamp in STAMPS:
			stamp.draw(SCREEN)

		for entity in ENTITIES:	
			if not entity.hidden:
				entity.draw(SCREEN)
				'''
				if entity.type in ['Entity', 'Clone'] or entity.type.startswith('Player'):
					for clone in entity.clones:
						clone.draw(SCREEN)
						for cloneOfClone in clone.clones:
							cloneOfClone.draw(SCREEN)
				'''
				
		pygame.display.update()

		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT:
				with threading.Lock():
					RUNNING = False
				pygame.quit()
				sys.exit()

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_q:
					ENTITIES = [e for e in ENTITIES if e.type != "Stamp"]
				elif event.key == pygame.K_m:
					toggle_mask()
			
			if event.type == pygame.MOUSEBUTTONDOWN:
				config.mouse.down = True
				config.mouse.clicked = True
			
			if not event.type == pygame.MOUSEBUTTONDOWN:
				config.mouse.clicked = False

			if event.type == pygame.MOUSEBUTTONUP:
				config.mouse.down = False

		CLOCK.tick(config.FPS)
	
	except ValueError:
	#except Exception as e:
		print(f'RUNTIME ERROR:	{e}')
		RUNNING = False
		pygame.quit()
		sys.exit()

def GAMEPLAY():
	global ENTITIES, SCREEN, CLOCK, RUNNING

	if not RUNNING: INITIALIZE()

	with threading.Lock():
		RUNNING = True
		SCREEN = pygame.display.set_mode(win.size)
		pygame.display.set_caption("PYGAME")
		CLOCK = pygame.time.Clock()

	while RUNNING:
		SCREEN.fill(config.backgroundColor)
		with threading.Lock():
			keys = pygame.key.get_pressed()
		if PLAYER1: PLAYER1.update(keys)
		if PLAYER2: PLAYER2.update(keys)

		for entity in ENTITIES:	
			if entity.type == "Stamp":
				entity.draw(SCREEN)

		for entity in ENTITIES:	
			if entity.type != "Stamp" and not entity.hidden:
				entity.draw(SCREEN)
				for clone in entity.clones:
					clone.draw(SCREEN)

		pygame.display.flip()
		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT:
				with threading.Lock():
					RUNNING = False

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_q:
					ENTITIES = [e for e in ENTITIES if e.type != "Stamp"]
				elif not config.stampSpamMode and event.key == config.key_map['Player1'][4]:
					PLAYER1.stamp()
				elif not config.stampSpamMode and event.key == config.key_map['Player2'][4]:
					PLAYER2.stamp()
				elif event.key == pygame.K_m:
					toggle_mask()

		CLOCK.tick(60)

	pygame.quit()

def mainloopGAME():
	threading.Thread(target=GAME, daemon=True).start()

if __name__ == '__main__':
	pygameInitialize()

	PLAYER1 = Entity(name='Player1', x=config.centerX-50, image=paths.image1, attributes=['start at random position'])
	PLAYER2 = Entity(name='Player2', x=config.centerX+50, image=paths.image2, attributes=['start at random position'])

	GAMEPLAY()

else:
	PLAYER1 = PLAYER2 = None

# DEBUG CONSOLE THREAD
# threading.Thread(target=updateTerminal, daemon=True).start()

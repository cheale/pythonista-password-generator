import ui
import string
import random
import math
import clipboard
from console import hud_alert
from objc_util import *


UIDevice = ObjCClass('UIDevice')
SPECIALS = '*&$#@%!'
stops = [15, 20]
password_with_hyphens = ''
password_without_hyphens = ''
hyphen_replacement_chars = ''


def vibrate():
	UIDevice.new()._tapticEngine().actuateFeedback_(1001)


def character_slider_changed(sender):
	v = sender.superview
	char_count = round(sender.value * 28 + 4)
	prev_char_count_string = v['char_count_value'].text
	prev_char_count = int(prev_char_count_string) if prev_char_count_string else 0
	if char_count != prev_char_count:
		if char_count in stops:
			vibrate()
		v['char_count_value'].text = str(char_count)
		font_decrease_factor = (char_count - 12) / 20
		font_size = int(34 - 18 * font_decrease_factor)
		v['password'].font = ('<System-Bold>', font_size)
		set_new_password()


def switch_changed(sender):
	set_new_password()


def hyphen_switch_changed(sender):
	v = sender.superview
	has_hyphens = v['hyphens_switch'].value
	v['password'].text = password_with_hyphens if has_hyphens else password_without_hyphens


def generate_button_pressed(sender):
	set_new_password()


def copy_button_pressed(sender):
	clipboard.set(v['password'].text)
	hud_alert('Copied')

def set_new_password():
	v['password'].text = get_new_password()


def get_new_password():
	global password_with_hyphens
	global hyphen_replacement_chars
	global password_without_hyphens
	char_count = int(v['char_count_value'].text)
	has_specials = v['specials_switch'].value
	has_hyphens = v['hyphens_switch'].value
	has_numbers = v['numbers_switch'].value
	has_lowercase = v['lowercase_switch'].value
	has_uppercase = v['uppercase_switch'].value

	if not any((has_lowercase, has_numbers, has_specials, has_uppercase)):
		password_with_hyphens = '-' * char_count
		password_without_hyphens = ' ' * char_count
		return password_with_hyphens if has_hyphens else password_without_hyphens

	char_bank = SPECIALS if has_specials else ''
	char_bank += string.digits if has_numbers else ''
	char_bank += string.ascii_lowercase if has_lowercase else ''
	char_bank += string.ascii_uppercase if has_uppercase else ''

	while len(char_bank) < char_count:
		char_bank += char_bank

	# setup for hyphen algorithm
	def get_hyphen_count(even, v):
		# the hyphen count is the closest number of the same parity as the char count
		ceil = math.ceil(v)
		ceil_even = ceil % 2 == 0
		next_n_of_parity = ceil if ceil_even and even or not ceil_even and not even else ceil + 1
		prev_n_of_parity = next_n_of_parity - 2
		if abs(v - next_n_of_parity) < abs(v - prev_n_of_parity):
			return next_n_of_parity
		else:
			return prev_n_of_parity
	even = char_count % 2 == 0
	tmp = char_count / 7
	# hyphen algorithm
	hyphen_count = int(tmp if round(tmp) == tmp else get_hyphen_count(even, tmp))
	section_count = hyphen_count + 1
	non_hyphen_char_count = char_count - hyphen_count
	base_section_char_count = math.floor(non_hyphen_char_count / section_count)
	overflow_section_count = non_hyphen_char_count % section_count
	#
	def get_random_char(s):
		return s[random.randint(0, len(s) - 1)]
	non_hyphen_chars = ''
	# add one from each included section first to ensure that all sections are represented
	non_hyphen_chars += get_random_char(SPECIALS) if has_specials else ''
	non_hyphen_chars += get_random_char(string.digits) if has_numbers else ''
	non_hyphen_chars += get_random_char(string.ascii_lowercase) if has_lowercase else ''
	non_hyphen_chars += get_random_char(string.ascii_uppercase) if has_uppercase else ''
	while len(non_hyphen_chars) < non_hyphen_char_count:
		char = get_random_char(char_bank)
		non_hyphen_chars += char
		char_bank = char_bank.replace(char, '', 1)

	non_hyphen_chars = ''.join(random.sample(non_hyphen_chars,len(non_hyphen_chars)))

	hyphen_replacement_chars = ''
	while len(hyphen_replacement_chars) < hyphen_count:
		char = get_random_char(char_bank)
		hyphen_replacement_chars += char
		char_bank = char_bank.replace(char, '', 1)

	password_with_hyphens = ''
	for i in range(section_count):
		this_section_char_count = base_section_char_count
		if overflow_section_count != 0:
			max_overflow_distance = (overflow_section_count - 1) / 2
			if overflow_section_count % 2 != 0:
				#check distance from center
				center_index = (section_count - 1) / 2
				if abs(i - center_index) <= max_overflow_distance:
					this_section_char_count += 1
			else:
				#check distance from edge
				if min(i, section_count - 1 - i) <= max_overflow_distance:
					this_section_char_count += 1
		password_with_hyphens += non_hyphen_chars[0:this_section_char_count]
		non_hyphen_chars = non_hyphen_chars[this_section_char_count:]
		password_with_hyphens += '-' if len(non_hyphen_chars) > 0 else ''

	password_without_hyphens = password_with_hyphens
	for i in range(hyphen_count):
		char = hyphen_replacement_chars[i]
		password_without_hyphens = password_without_hyphens.replace('-', char, 1)

	return password_with_hyphens if has_hyphens else password_without_hyphens


v = ui.load_view()
v.name = 'Generate Strong Password'
character_slider_changed(v['char_count_slider'])
v.background_color = '#f0f0f0'
v.present('sheet')

# secretrandom 2.2.2 STABLE

import random
import secrets
import string
from decimal import Decimal


shuffled_digits_for_unprdictibility = string.digits + string.digits + string.digits


def randchar(length):   
    characters = list(string.ascii_letters + string.digits + string.punctuation)
    random.shuffle(characters)
    password = ''
    for _ in range(length-1):
        password += secrets.choice(characters)
    password += random.choice(characters)
    return password
        
def randcode(length):
    code = ''
    code += random.choice(shuffled_digits_for_unprdictibility)
    for _ in range(length):
        code += secrets.choice(shuffled_digits_for_unprdictibility)
    return code

def randint(from_this, to_this, step=1):
    the_repeating_number_to_loop = random.choice(shuffled_digits_for_unprdictibility)
    for _ in range(random.randint(1, 22)):
        num = random.randrange(from_this, to_this+1, step)
    return num

def randflt(from_this, to_this):
    for _ in range(randint(2, 23)):
        float = random.uniform(from_this, to_this)
    return float

def choice(i):
    for _ in range(randint(1, 5)):
        x = secrets.choice(i)
    return x

def shuffle(i):
    for _ in range(randint(4, 25)):
        random.shuffle(i)
    return i

def ver():
    return 'secretrandom v2.2.2 Stable\nOfficial Stable Release by Annoying-mous.\nMore information at https://github.com/dUhEnC-39/secretrandom'



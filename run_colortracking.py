# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division

from collections import deque

import cv2
import numpy
import pygame
from pygame.locals import DOUBLEBUF, HWSURFACE, QUIT


SCREEN_SIZE = (960, 540)
pts = deque(maxlen=10)


def capture_image(cam):
    image = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2BGR)
    return cv2.resize(image, SCREEN_SIZE)


def get_surface(image):
    return pygame.surfarray.make_surface(numpy.rot90(image))


if __name__ == '__main__':
    pygame.init()
    clock = pygame.time.Clock()
    cam = cv2.VideoCapture(0)
    screen = pygame.display.set_mode(SCREEN_SIZE, DOUBLEBUF | HWSURFACE, 32)
    exosphere_surface = pygame.image.load('assets/blood1.png')
    x, y = None, None
    while True:
        snapshot = capture_image(cam)
        msecs_since_lastupdate = clock.tick(15)
        pygame.display.set_caption('augmented [FPS: {:.1f}]'.format(clock.get_fps()))
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
        screen.blit(get_surface(snapshot), (0, 0))

        # Orange golf ball
        mask = cv2.inRange(snapshot, (180, 60, 40), (250, 115, 77))
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        if cnts:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            screen.blit(exosphere_surface, (SCREEN_SIZE[0]-x, y))

        pygame.display.flip()

    print "Goodbye"

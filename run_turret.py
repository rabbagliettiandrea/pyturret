# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division

import random
from collections import deque

import cv2
import numpy
import pygame
from pygame.locals import DOUBLEBUF, HWSURFACE, QUIT


def capture_image(cam):
    image = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2BGR)
    return cv2.resize(image, (640, 360))


def get_diff_image(t0, t1, t2):
    t0_gray = cv2.cvtColor(t0, cv2.COLOR_RGB2GRAY)
    t1_gray = cv2.cvtColor(t1, cv2.COLOR_RGB2GRAY)
    t2_gray = cv2.cvtColor(t2, cv2.COLOR_RGB2GRAY)
    d1 = cv2.absdiff(t2_gray, t1_gray)
    d2 = cv2.absdiff(t1_gray, t0_gray)
    return cv2.bitwise_and(d1, d2)


def get_surface(image):
    return pygame.surfarray.make_surface(numpy.rot90(image))


if __name__ == '__main__':
    pygame.init()

    threshold = 0
    msecs_since_start = 0
    msecs_since_lastsnap = 0
    msecs_since_lastupdate = 0
    msecs_since_lastping = 0
    clock = pygame.time.Clock()
    cam = cv2.VideoCapture(0)
    ping_sound = pygame.mixer.Sound('assets/ping.wav')
    boot_sound = pygame.mixer.Sound('assets/boot.wav')
    deploy_sounds = [pygame.mixer.Sound('assets/deploy{}.wav'.format(i)) for i in xrange(1, 5)]
    shoot_surfaces = [pygame.image.load('assets/blood{}.png'.format(i)) for i in xrange(1, 4)]
    shoot_sounds = [pygame.mixer.Sound('assets/shoot{}.wav'.format(i)) for i in xrange(1, 3)]

    t_0 = capture_image(cam)
    t_1 = capture_image(cam)
    t_2 = capture_image(cam)

    height, width, channel = t_0.shape
    total = width * height

    turret_on = False

    turret_surface = pygame.image.load('assets/turret.jpg')
    turret_firing_surface = pygame.image.load('assets/turret_firing.jpg')
    turret_halted_surface = pygame.image.load('assets/turret_halted.jpg')
    hud_surface = pygame.image.load('assets/hud.png')
    hud_kill_surface = pygame.image.load('assets/hud_kill.png')
    blood_holes_history = deque(maxlen=2)

    screen = pygame.display.set_mode((width * 2, height * 2), DOUBLEBUF | HWSURFACE, 32)

    while True:
        pygame.display.set_caption('pyTurret [FPS: {:.1f}]'.format(clock.get_fps()))
        msecs_since_lastupdate = clock.tick(40)

        for event in pygame.event.get():
            if event.type == QUIT:
                exit()

        image_diff = get_diff_image(t_0, t_1, t_2)
        diff_surface = get_surface(image_diff)
        t_2_surface = get_surface(t_2)
        screen.blit(diff_surface, (0, 0))
        screen.blit(hud_surface, (0, 0))
        screen.blit(t_2_surface, (0, height))
        for blood_hole in blood_holes_history:
            screen.blit(*blood_hole)
        screen.blit(turret_surface, (width, 0))

        non_zeros = cv2.countNonZero(image_diff)
        ratio = non_zeros / total * 100


        msecs_since_start = pygame.time.get_ticks()
        if msecs_since_start < 5000:
            threshold = ratio * 1.1
            screen.blit(turret_halted_surface, (width, 0))
        else:
            if not turret_on:
                turret_on = True
                boot_sound.play()
                random.choice(deploy_sounds).play()
            if ratio > threshold:
                random.choice(shoot_sounds).play()
                blood_hole_surfaces = shoot_surfaces * 2
                random.shuffle(blood_hole_surfaces)
                for blood_hole_surface in blood_hole_surfaces:
                    x, y = random.randint(0, width // 3), random.randint(height, height * 2)
                    blood_holes_history.append((blood_hole_surface, (x, y)))
                screen.blit(turret_firing_surface, (width, 0))
                screen.blit(hud_kill_surface, (0, 0))
            else:
                msecs_since_lastping += msecs_since_lastupdate
                if msecs_since_lastping > 1500:
                    ping_sound.play()
                    msecs_since_lastping = 0

        print 'threshold: {} | ratio: {} | total: {} | non_zeros: {}'.format(threshold, ratio, total, non_zeros)

        msecs_since_lastsnap += msecs_since_lastupdate
        if msecs_since_lastsnap > 100:
            t_0 = t_1
            t_1 = t_2
            t_2 = capture_image(cam)
            msecs_since_lastsnap = 0

        pygame.display.flip()

    print "Goodbye"

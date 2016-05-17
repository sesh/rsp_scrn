#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import time
from datetime import date
from io import BytesIO

import click
import imageio
import numpy
import pytweening
from PIL import Image
from selenium import webdriver


def valid_filename(value):
    value = value.strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', value)


def take_screenshot(url, width, height, max_size, sleep=0, resize=False):
    print('[{}x{}] URL: {}'.format(width, height, url))

    browser = webdriver.PhantomJS()
    browser.set_window_size(width, height)
    browser.get(url)

    if sleep:
        print('Taking a nap, see you in {} seconds'.format(sleep))
        time.sleep(sleep)

    screenshot = BytesIO(browser.get_screenshot_as_png())
    browser.quit()

    white_bg_placeholder = Image.new('RGB', max_size, (222, 222, 222))
    screenshot = Image.open(screenshot)

    # retina display + chrome ends up with screenshots that are too large, resize those
    if screenshot.width > width:
        screenshot = screenshot.resize((width, int(screenshot.height * (width / screenshot.width))))

    white_bg_placeholder.paste(screenshot, (0, 0))

    if resize:
        white_bg_placeholder = white_bg_placeholder.resize((960, 600))

    return numpy.asarray(white_bg_placeholder)


@click.command()
@click.argument('url')
@click.option('--sleep', default=0)
@click.option('--resize', is_flag=True)
def responsive_screenshot(url, sleep, resize):
    filename = valid_filename(url.split('://')[-1])
    # note: PhantomJS always returns a screenshot that's the full height of the page
    # note: Chromium doesn't resize smaller than ~500x500
    largest_size = (1920, 1200)
    smallest_size = (320, 1200) # iPhone 4

    frames = []
    for x in range(0, 101, 5):  # +1 to ensure that we include the largest size in our set
        width, height = pytweening.getPointOnLine(*smallest_size, *largest_size, x / 100.0)
        frame = take_screenshot(url, int(width), int(height), largest_size, int(sleep), resize)
        frames.append(frame)
    imageio.mimwrite('{}-{}.gif'.format(str(date.today()), filename), frames, duration=0.2)


if __name__ == '__main__':
    responsive_screenshot()

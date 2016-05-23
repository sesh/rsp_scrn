#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import time
from datetime import date
from io import BytesIO

import click
import imageio
import numpy
import pytweening
from PIL import Image
from selenium import webdriver



def get_iphone_browser():
    dcap = dict(webdriver.DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_1 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D201 Safari/9537.53'  # noqa
    browser = webdriver.PhantomJS(desired_capabilities=dcap)
    return browser


def valid_filename(value):
    value = value.strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', value)


def take_screenshot(url, width, height, max_size, sleep=0, resize=False):
    print('[{}x{}] URL: {}'.format(width, height, url))

    if width < 450:
        browser = get_iphone_browser()
    else:
        browser = webdriver.PhantomJS()

    browser.set_window_size(width, height)
    browser.get(url)

    if sleep:
        print('Taking a nap, see you in {} seconds'.format(sleep))
        time.sleep(sleep)

    screenshot_from_selenium = BytesIO(browser.get_screenshot_as_png())
    browser.quit()

    screenshot_canvas = Image.new('RGB', max_size, (222, 222, 222))
    screenshot_no_bg = Image.open(screenshot_from_selenium)

    screenshot = Image.new("RGB", screenshot_no_bg.size, (255, 255, 255))
    screenshot.paste(screenshot_no_bg, mask=screenshot_no_bg.split()[3])

    # retina display + chrome ends up with screenshots that are too large, resize those
    if screenshot.width > width:
        screenshot = screenshot.resize((width, int(screenshot.height * (width / screenshot.width))))

    screenshot_canvas.paste(screenshot, (0, 0))

    if resize:
        screenshot_canvas = screenshot_canvas.resize((960, 600))

    return numpy.asarray(screenshot_canvas)


@click.command()
@click.argument('url')
@click.option('--sleep', default=0)
@click.option('--resize', is_flag=True)
def responsive_screenshot(url, sleep, resize):
    if not url.startswith('http://') and not url.startswith('https://'):
        sys.exit('URL must start with http:// or https://')

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

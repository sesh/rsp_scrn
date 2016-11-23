## Screenshot Responsive Sites

A simple Python script that uses Selenium, PhantomJS and Pillow to create animated GIFs of how websites respond to
different browser widths. Useful for testing your site's responsive breakpoints and comparing it to others.


### Usage

```
python rsp_scrn.py <domain> [--resize] [--sleep=<int>]

   --resize       Shrink the final GIF to save on filesize
   --sleep        Wait x seconds before taking the screenshot
```

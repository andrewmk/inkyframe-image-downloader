# Inkyframe image downloader
Robust script to regularly download a JPEG image from a webserver onto a [Pimoroni InkyFrame 7.3"](https://shop.pimoroni.com/products/inky-frame-7-3). Can be used for digital picture frames, home automation dashboard, calendar, weather forecast etc.

This is a mashup of the Pimoroni [xkcd](https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/examples/inky_frame/inky_frame_xkcd_daily.py), [random joke](https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/examples/inky_frame/inky_frame_random_joke.py), [placekitten](https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/examples/inky_frame/inky_frame_placekitten.py) etc. examples plus other code from all over the place that I'm afraid I didn't keep track of.

Uses a tweaked version of [urllib.urequest](https://github.com/pfalcon/pycopy-lib/tree/master/urllib.urequest) so that we can provide a timeout for the socket right from its point of creation.

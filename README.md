# Inkyframe image downloader
Robust script to regularly download a JPEG image from a webserver onto a [Pimoroni InkyFrame 7.3"](https://shop.pimoroni.com/products/inky-frame-7-3). Can be used for digital picture frames, home automation dashboard, calendar, weather forecast etc.

Uses a tweaked version of [urllib.urequest](https://github.com/pfalcon/pycopy-lib/tree/master/urllib.urequest) so that we can provide a timeout for the socket right from its point of creation.

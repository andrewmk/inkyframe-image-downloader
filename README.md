# inkyframe-image-downloader
Robust script to regularly download a JPEG image from a webserver. Can be used for a digital picture frame, home automation dashboard etc.

Uses a tweaked version of [urllib.urequest](https://github.com/pfalcon/pycopy-lib/tree/master/urllib.urequest) so that we can provide a timeout for the socket right from its point of creation.

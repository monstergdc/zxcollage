#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# python3 for my env! ^^^

# big collage from ZX images from ZXArt.ee [CGI]
# (c)2025 MoNsTeR/GDC, Noniewicz.com, Jakub Noniewicz
# cre: 20250227
# upd: ?


from zxcollage import get_cgi_par, all_collages, all_sizes

if __name__ == '__main__':

    folder = "./allgfx"
    par = get_cgi_par()
    z = par['size']
    all_sizes_list = all_sizes()
    one_size = all_sizes_list[z]
    sizes = {z: one_size}
    all_collages('cgi', folder, sizes, pfx="zxcollage-", shuffle=par['shuffle'], logo=par['logo'], txt=True, zxbar=par['zxbar'])

# EOF

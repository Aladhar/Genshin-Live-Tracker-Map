#!/usr/bin/env python3
"""Capture screenshots periodically for dataset collection.

Usage examples:
  python capture_screenshots.py --output dataset/raw --interval 0.5 --count 100
  python capture_screenshots.py --output dataset/raw --region 100,100,800,600
"""
import argparse
import time
import os
from mss import mss
from PIL import Image


def parse_region(s):
    parts = s.split(',')
    if len(parts) != 4:
        raise argparse.ArgumentTypeError('region must be left,top,width,height')
    return dict(left=int(parts[0]), top=int(parts[1]), width=int(parts[2]), height=int(parts[3]))


def main():
    p = argparse.ArgumentParser(description='Capture screenshots for chest detector dataset')
    p.add_argument('--output', '-o', default='dataset/raw', help='output directory')
    p.add_argument('--interval', '-i', type=float, default=0.5, help='seconds between captures')
    p.add_argument('--count', '-c', type=int, default=0, help='number of screenshots to capture, 0=until interrupted')
    p.add_argument('--region', '-r', type=parse_region, help='capture region: left,top,width,height')
    p.add_argument('--monitor', type=int, default=1, help='monitor index to capture (1-based, default 1)')
    p.add_argument('--prefix', default='shot', help='filename prefix')
    args = p.parse_args()

    os.makedirs(args.output, exist_ok=True)
    sct = mss()
    count = 0
    try:
        while True:
            if args.region:
                img = sct.grab(args.region)
            else:
                monitor = sct.monitors[args.monitor] if args.monitor < len(sct.monitors) else sct.monitors[1]
                img = sct.grab(monitor)

            im = Image.frombytes('RGB', (img.width, img.height), img.rgb)
            fname = f"{args.prefix}_{int(time.time()*1000)}_{count:04d}.png"
            path = os.path.join(args.output, fname)
            im.save(path)
            print('Saved', path)
            count += 1
            if args.count and count >= args.count:
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print('\nCapture stopped by user')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Simple OpenCV-based labeler to move images into pos/neg folders.

Controls while image shown:
  p - mark positive (moves file to pos folder)
  n - mark negative (moves file to neg folder)
  q - quit
"""
import argparse
import os
import cv2
import shutil


def main():
    p = argparse.ArgumentParser(description='Label images as positive/negative')
    p.add_argument('--input', '-i', default='dataset/raw', help='input directory')
    p.add_argument('--pos', default='dataset/pos', help='positive dir')
    p.add_argument('--neg', default='dataset/neg', help='negative dir')
    args = p.parse_args()

    os.makedirs(args.pos, exist_ok=True)
    os.makedirs(args.neg, exist_ok=True)

    files = sorted([f for f in os.listdir(args.input) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    for fn in files:
        path = os.path.join(args.input, fn)
        img = cv2.imread(path)
        if img is None:
            continue
        cv2.imshow('labeler', img)
        k = cv2.waitKey(0) & 0xFF
        if k == ord('p'):
            shutil.move(path, os.path.join(args.pos, fn))
            print('Moved to pos:', fn)
        elif k == ord('n'):
            shutil.move(path, os.path.join(args.neg, fn))
            print('Moved to neg:', fn)
        elif k == ord('q'):
            print('Quitting')
            break
        else:
            print('Skipped', fn)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()

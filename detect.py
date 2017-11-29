from pytube import YouTube
import argparse
import os
import shutil
import subprocess as sp
from datetime import timedelta
import client
from constants import paths
from constants import defaults

ARGS = None
SPLIT_IMAGES = paths.TEMP_DIR + '/input/'

def create_dirs_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

def delete_dir_if_exists(path):
    if os.path.exists(path):
        shutil.rmtree(path)

def is_downloaded(vidoe_id):
    """Check if we have already downloaded the video"""
    return vidoe_id + '.mp4' in os.listdir(paths.DATA_DIR)

def detect(url):
    """Detect slides present in the given youtube url"""

    # assumes that url is copied from browser, assumes particular type of yt url only
    vid_id = url.split('v=')[-1]
    create_dirs_if_not_exists(paths.DATA_DIR)
    downladed = is_downloaded(vid_id)
    if not downladed:
        yt = YouTube(url)
        yt.set_filename(vid_id)
        vid = yt.get('mp4', '360p')
        create_dirs_if_not_exists(paths.DATA_DIR)
        create_dirs_if_not_exists(paths.SLIDES_DIR)
        print 'Starting video download....\n'
        vid.download(paths.DATA_DIR)
        print 'Video download finished\n'
    else:
        print 'Video already downloaded\n'
    try:
        shutil.rmtree(SPLIT_IMAGES)
    except OSError:
        pass
    create_dirs_if_not_exists(SPLIT_IMAGES)
    print 'Splitting video into images\n'
    command = ['ffmpeg', '-n', '-i', paths.DATA_DIR + vid_id + '.mp4',
               '-vf', 'fps=1',
               SPLIT_IMAGES + '%d.jpeg']
    sp.call(command)
    print 'Images extracted from the video\n'
    input_images = sorted(
        os.listdir(SPLIT_IMAGES),
        key=lambda x: int(os.path.splitext(x)[0])
    )

    delete_dir_if_exists(paths.SLIDES_DIR + vid_id)
    delete_dir_if_exists(paths.NON_SLIDES_DIR + vid_id)
    create_dirs_if_not_exists(paths.SLIDES_DIR + vid_id)
    if ARGS.save_non_slides:
        create_dirs_if_not_exists(paths.NON_SLIDES_DIR + vid_id)

    for image in input_images:
        print 'processing frame at ' + str(timedelta(seconds=int(image.split('.')[0])))
        val = client.main(SPLIT_IMAGES + image)
        if val > 0.5:
            shutil.copy2(SPLIT_IMAGES + image, paths.SLIDES_DIR + vid_id)
        elif ARGS.save_non_slides:
            shutil.copy2(SPLIT_IMAGES + image, paths.NON_SLIDES_DIR + vid_id)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--url',
        type=str,
        default='',
        help='Url of the youtube video you want to extract slides from'
    )
    parser.add_argument(
        '--save_non_slides',
        help='Save frames not detected as slides'
    )
    ARGS, unparsed = parser.parse_known_args()
    if not ARGS.url:
        raise ValueError('Pass in the url of the youtube video you want to parse slides from in the --url arg')
    detect(ARGS.url)

from pytube import YouTube
import os.path
import subprocess as sp
import itertools
import shutil
from constants import defaults
from constants import paths

IMAGE_SIZE = defaults.IMAGE_SIZE


def create_dirs_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

class Sequence:

    def __init__(self, id, label, url, res, fmt, slices):
        self.id = id
        self.label = label
        self.url = url
        self.res = res
        self.fmt = fmt

        self.dir_name = paths.DATA_DIR + self.id
        self.file_path = self.dir_name + "/" + self.id + "." + self.fmt

        yt = YouTube(url)
        yt.set_filename(id)
        self.downloader = yt.get(fmt, res)

        # flatten
        self.positives = list(itertools.chain(
            *[range(x[0], x[1]) for x in slices]))

    def download(self):
        create_dirs_if_not_exists(self.dir_name)

        if os.path.isfile(self.file_path):
            print "file: %s already exists, skipping" % self.file_path
        else:
            print "downloading %s to %s" % (self.url, self.file_path)
            self.downloader.download(self.dir_name)

    def read(self, validation_data=False):
        print "reading %s" % self.file_path
        parent_folder = './images/' if not validation_data else './validation_images/'
        slide_image_path = parent_folder + 'slide/'
        noslide_image_path = parent_folder + 'noslide/'
        TEMP = paths.TEMP_DIR + '/images/'
        try:
            shutil.rmtree(TEMP)
        except OSError as e:
            pass
        create_dirs_if_not_exists(TEMP)
        create_dirs_if_not_exists(parent_folder)
        create_dirs_if_not_exists(slide_image_path)
        create_dirs_if_not_exists(noslide_image_path)

        # TODO: use piplines instead of savings files to disk
        command = ['ffmpeg', '-n', '-i', self.file_path,
                   '-vf', 'fps=1, scale=' +
                   str(IMAGE_SIZE) + ':' + str(IMAGE_SIZE),
                   TEMP + '%d.jpeg']
        sp.call(command)
        video_name = os.path.splitext(os.path.basename(self.file_path))[0]

        image_files = os.listdir(TEMP)

        for file in image_files:
            seq = int(file.split(".")[0])
            src = TEMP + file
            try:
                if seq in self.positives:
                    shutil.copyfile(src, slide_image_path + video_name + file)
                    print "copying file" + file
                else:
                    shutil.copyfile(src, noslide_image_path + video_name + file)
                    print "copying no slide file" + file
            except IOError as e:
                print "Could not read", src, e

## Slide Extraction

Extract slides out of videos

### Setup

You need to have ffmpeg installed & in path.
I've noticed some inconsistencies between ffmpeg versions. Please use v3.0

Set up a docker container for tensorflow server following the instructions at https://www.tensorflow.org/serving/serving_inception 
 
Install the required python dependencies
```sh
# Create a new env using virtualenv
virtualenv venv
source venv/bin/activate
# install required python packages
pip install -r requirements.txt
```

### Extract slides from video

Start the container for tensorflow you have created
```sh
# attach the project dir as a volume to the container
docker run -p 9000:9000 -v PROJECT_DIR:/app $USER/inception_serving tensorflow_model_server --port=9000 --model_name=inception --model_base_path=/app/checkpoints &> inception_log
```
```sh
# just run this script and pass it the video url
# the detected slides are stored in the detected_slides folder
python detect.py --url URL_TO_YOUTUBE_VIDEO
````

### Training the network

Import some data to train the network.
```sh
# The script downloads a bunch of youtube videos & serialzes them into bin
# vidoes stored in /data and training data in /images
# modify this script if you want to change data used to train the network
python import_data.py
```

Train the network
```sh
python image_retraining/retrain.py --image_dir images
```

### Visualize
TODO

### Architecture & memory constraints

TODO


### Workflow to add more data

TODO

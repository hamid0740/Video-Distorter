import os, sys, subprocess
import cv2
import ffmpeg

def distorter(vn, format, DISTORT_PERCENTAGE=60, SOUND_FILTER_FREQUENCY=10, SOUND_FILTER_MODULATION_DEPTH=1):
  # define paths
  path = f"./temp/{vn}"
  videoName = f"original_{vn}.{format}"
  videoPath = f"./temp/{vn}/original_{vn}.{format}"
  processDirPath = f"./temp/{vn}/process"
  framesPath = f"./temp/{vn}/process/frames"
  distortedFramesPath = f"./temp/{vn}/process/distorted_frames"
  distortedVideoPath = f"./temp/{vn}/process/distorted_{vn}.mp4"
  resultVideoPath = f"./temp/{vn}/result_{vn}.mp4"
  
  # define video variables
  capture = cv2.VideoCapture(videoPath)
  fps = capture.get(cv2.CAP_PROP_FPS)
  nbFrames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
  videoSize = (
    int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
    int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
  )

  # create output directories
  os.makedirs(processDirPath, exist_ok=True)
  os.makedirs(framesPath, exist_ok=True)
  os.makedirs(distortedFramesPath, exist_ok=True)
  for i in os.listdir(framesPath):
    os.remove(os.path.join(framesPath, i))
  for i in os.listdir(distortedFramesPath):
    os.remove(os.path.join(distortedFramesPath, i))

  # convert video to frames
  #print('Converting video into frames...')
  frameNr = 0
  while True:
    #print(f'{frameNr}/{nbFrames}', end='\r')
    success, frame = capture.read()
    if not success:
      break
    # naming the file with an appropriate number of leading zeros
    filename = f"frame_{str(frameNr).zfill(len(str(nbFrames)))}.jpg"
    cv2.imwrite(os.path.join(framesPath, filename), frame)
    frameNr += 1
  capture.release()

  # distortion of frames
  #print('Distorting frames...')
  for i, elem in enumerate(os.listdir(framesPath), start=1):
    #print(f'{i}/{nbFrames}', end="\r")
    curFramePath = os.path.join(framesPath, elem)
    resFramePath = os.path.join(distortedFramesPath, elem)
    cmd = f"/usr/local/bin/magick {curFramePath}\
      -liquid-rescale {100-DISTORT_PERCENTAGE}x{100-DISTORT_PERCENTAGE}%!\
      -resize {videoSize[0]}x{videoSize[1]}\! {resFramePath}"
    exitCode, cmdOutput = subprocess.getstatusoutput(cmd)
    if exitCode != 0:
      raise os.error(f"Error while distorting frame {i}/{nbFrames}: " + cmdOutput + subprocess.run(["type", "magick"], shell=True, stdout=subprocess.PIPE).stdout.decode("utf-8'"))
  
  # Assembling frames back into a video
  #print('Creating video...')
  out = cv2.VideoWriter(distortedVideoPath, cv2.VideoWriter_fourcc(*"MP4V"), fps, videoSize)

  img_array = [cv2.imread(os.path.join(distortedFramesPath, elem)) for elem in sorted(os.listdir(distortedFramesPath))]
  print(str(img_array))
  for i in range(len(img_array)):
    #print(f'{i}/{nbFrames}', end="\r")
    out.write(img_array[i])
  out.release()
  cv2.destroyAllWindows()
  
  
  # add distorted sound
  #print("Adding distorted sound...")
  video = ffmpeg.input(distortedVideoPath).video
  audio = ffmpeg.input(videoPath).audio.filter(
    "vibrato",
    f=SOUND_FILTER_FREQUENCY,
    d=SOUND_FILTER_MODULATION_DEPTH
    # Documentation : https://ffmpeg.org/ffmpeg-filters.html#vibrato
  )
  (
    ffmpeg
    .concat(video, audio, v=1, a=1) # v = video stream, a = audio stream
    .output(resultVideoPath)
    .run(overwrite_output=True)
    # Documentation : https://kkroening.github.io/ffmpeg-python/
  )
  
  # delete the distorted video with no sound
  os.remove(processDirPath)

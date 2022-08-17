import streamlit as st
import os, sys, subprocess
import cv2
import ffmpeg
from distorter import distorter

uploaded_file = st.file_uploader("Upload a video")
#total_points = st.slider("Number of points in spiral", 1, 5000, 2000)
if uploaded_file is not None:
  format = uploaded_file.name.split(".")[-1].lower()
  if format in ["mp4", "avi", "mov", "wmv", "flv"]:
    bytes_data = uploaded_file.getvalue()
    os.makedirs("./temp", exist_ok=True)
    vn = 1
    while True:
      if not os.path.isfile(f"./temp/{vn}/original_{vn}.mp4"):
        filename = f"./temp/{vn}/original_{vn}.mp4"
        os.makedirs(f"./temp/{vn}", exist_ok=True)
        with open(filename, "wb") as file:
          file.write(uploaded_file.getvalue())
        break
      else:
        vn += 1
    distorter(vn, format)
    st.write("✅️ Converted succesfully!")
    st.video(open(f"./temp/{vn}/result_{vn}.mp4", "rb").read())
    os.remove(filename)
  else:
    st.write("⚠️ Please upload a video only!")

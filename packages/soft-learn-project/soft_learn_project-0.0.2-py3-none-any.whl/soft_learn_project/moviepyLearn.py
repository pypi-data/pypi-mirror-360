# %% [markdown]
# # 安装
# * 更多的例子参考网址
# * [中文学习手册](http://doc.moviepy.com.cn/index.html#document-2_MoviePy%E5%85%A5%E9%97%A8/contents/%E5%BF%AB%E9%80%9F%E5%87%86%E5%A4%87)

# %% [markdown]
# MoviePy依赖FFMPEG软件对视频进行读写。不用对此担心，在你第一次使用MoviePy的时候，FFMPEG将会自动由ImageIO下载和安装（不过需要花一些时间）。如果你想使用FFMPEG的特定版本，你可以设置FFMPEG_BINARY环境变量。详见moviepy/config_defaults.py

# %% [markdown]
# 可选但有用的依赖包
#
# ImageMagick 只有在你想要添加文字时需要用到。它可作为一个后端用在GIF上，但如果不安装ImageMagick，你也可以用MoviePy处理GIF。m

# %% [markdown]
# * pip install moviepy
# * 还需要 安装ffmpeg
#     * 最好先更新以下brew: brew update
#     * brew install ffmpeg
#     * brew install imagemagick
#     * 测试ffmpeg 是否安装成功
#     * 终端输入ffmpeg 会显示版本号

# %% [markdown]
# ## 例子1

# %%
# Import everything needed to edit video clips
from moviepy.video.io.bindings import mplfig_to_npimage
from moviepy.editor import VideoClip
import numpy as np
import matplotlib.pyplot as plt
from email.mime import audio
from numpy import VisibleDeprecationWarning
from matplotlib import interactive
from moviepy.editor import *

# Load myHolidays.mp4 and select the subclip 00:00:50 - 00:00:60
# 剪辑视频50-60s
clip = VideoFileClip("test.mp4").subclip((1, 0), (1, 20))

# Reduce the audio volume (volume x 0.8)
# 调整音量为原0.8
clip = clip.volumex(0.8)

# Generate a text clip. You can customize the font, color, etc.
# 视频添加文字 如果用中文需要添加字体
txt_clip = TextClip("My Holidays 2013", fontsize=70, color='black')

# Say that you want it to appear 10s at the center of the screen
# 设置添加文字的位置和持续时间
txt_clip = txt_clip.set_pos('center').set_duration(10)

# Overlay the text clip on the first video clip
# 将视频和文字合成在一起
video = CompositeVideoClip([clip, txt_clip])

# Write the result to a file (many options available !)
# 写入到新的视频文件里
video.write_videofile("my合成视频.mp4")

# %% [markdown]
# ## 例子2 从视频中获取音频文件

# %%
# 从视频中获取音频文件
video = VideoFileClip("./my合成视频.mp4")
video.audio.write_audiofile("test.mp3")
# videos = video.show(1)  # 预览一帧
# video.save_frame("test.png",t=1) # 保存视频里的一帧

# %%
# ipython_display(video)
# video.ipython_display(width=280)


# %% [markdown]
# ## 例子3 把音乐合成到视频中

# %%
video = VideoFileClip("./movie.mp4").subclip("1:00", "2:00")
audio = AudioFileClip("test.mp3")
# 设置音频文件循环
loop_audio = afx.audio_loop(audio, duration=video.duration)  # 时长为视频文件的时长
# 把音频添加到视频
final = video.set_audio(loop_audio)
# 写入新文件
final.write_videofile("movie_test.mp4", audio_codec="aac")

# %% [markdown]
# ## 使用concatenate_videoclips函数进行连接操作。

# %% [markdown]
# ```
# from moviepy.editor import VideoFileClip, concatenate_videoclips
# clip1 = VideoFileClip("myvideo.mp4")
# clip2 = VideoFileClip("myvideo2.mp4").subclip(50,60)
# clip3 = VideoFileClip("myvideo3.mp4")
# final_clip = concatenate_videoclips([clip1,clip2,clip3])
# final_clip.write_videofile("my_concatenation.mp4")
# ```

# %% [markdown]
# ### 使用clip_array函数对剪辑进行堆叠操作。
# ```
# from moviepy.editor import VideoFileClip, clips_array, vfx
# clip1 = VideoFileClip("myvideo.mp4").margin(10) # add 10px contour
# clip2 = clip1.fx( vfx.mirror_x)
# clip3 = clip1.fx( vfx.mirror_y)
# clip4 = clip1.resize(0.60) # downsize 60%
# final_clip = clips_array([[clip1, clip2],
#                           [clip3, clip4]])
# final_clip.resize(width=480).write_videofile("my_stack.mp4")
# ```

# %%

x = np.linspace(-2, 2, 200)

duration = 2

fig, ax = plt.subplots()


def make_frame(t):
  ax.clear()
  ax.plot(x, np.sinc(x**2) + np.sin(x + 2*np.pi/duration * t), lw=3)
  ax.set_ylim(-1.5, 2.5)
  return mplfig_to_npimage(fig)


animation = VideoClip(make_frame, duration=duration)
animation.write_gif('matplotlib.gif', fps=20)

# %%

x = np.linspace(-2, 2, 200)

duration = 2

fig, ax = plt.subplots()


def make_frame(t):
  ax.clear()
  ax.plot(x, np.sinc(x**2) + np.sin(x + 2*np.pi/duration * t), lw=3)
  ax.set_ylim(-1.5, 2.5)
  return mplfig_to_npimage(fig)


animation = VideoClip(make_frame, duration=duration)
animation.ipython_display(fps=20, loop=True, autoplay=True)

# %%

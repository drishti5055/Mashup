#!/usr/bin/env python
# coding: utf-8

# In[75]:



from pytube import YouTube, Search, exceptions
from youtube_search import YoutubeSearch
from moviepy.editor import VideoFileClip, concatenate_audioclips
import os
import sys
import re
import streamlit as st
import zipfile as zp
from send_mail import send_mail
os.environ["IMAGEIO_FFMPEG_EXE"] = "ffmpeg"
import time


# In[76]:


def videos_download(singer,n):
    query=singer+'music video'
    results=YoutubeSearch(query,max_results=n+15).to_dict()
    # attribute will only ever request the first set of search results
    for i in results:
        try:
            y = YouTube('https://youtube.com/' + i['url_suffix'])
            #if y.length <300:
            video=y.streams.filter(file_extension='mp4').first()
            destination='Video Files'
            out_file=video.download(output_path=destination)
        except exceptions.VideoUnavailable:
            pass
        else:
            basePath, extension = os.path.splitext(out_file)
    st.info('Downloaded Videos')
    


# In[77]:


def video_to_audio(output_ext='mp3'):
    folder='Video Files/'
    clips=[]
    for filename in os.listdir(folder):
        if filename.endswith(".mp4"):
            final_path=os.path.join(folder,filename)
            clip=VideoFileClip(final_path) #converting video to frames
            audioclip=clip.audio #converting to audio
            basePath, extension = os.path.splitext(filename)
            clips.append(audioclip)
    st.info('Converted Videos to Audios')
    return clips
            


# In[78]:


def triming(clips,y):
    subclips=[]
    for clip in clips:
        subclip=clip.subclip(10,10+y)
        subclips.append(subclip)
    st.info('Trimmed Audios')
    return subclips


# In[79]:


def combined(clips,output='mashup'):
    concat=concatenate_audioclips(clips)
    concat.write_audiofile(f'{output}.mp3')
    st.success('Created Mashup')


# In[80]:


def createzip(file):
    destination='mashup.zip'
    zip_file=zp.ZipFile(destination,'w')
    zip_file.write(file,compress_type=zp.ZIP_DEFLATED)
    zip_file.close()
    return destination


# In[81]:


def writeup(singer,count,duration,mail,output='mashup'):
    videos_download(singer,count)
    clips=video_to_audio()
    subclips=triming(clips,duration)
    combined(subclips,output)
    send_mail(mail,createzip('mashup.mp3'))
    st.info('Mail sent!')
    


# In[82]:


st.title('Make your own Mashup!!')
st.subheader('Of your fav singer')


# In[83]:


with st.form('my_page'):
    singer=st.text_input('Singer Name')
    count=st.slider('Number of videos',10,60)
    duration=st.slider('Duration of each video to be trimmed(in seconds)',20,60)
    mail=st.text_input('Email Id')
    submitted=st.form_submit_button('Submit')
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if submitted:
        if not singer.strip():
            st.error('Pease enter the name of the singer')
        elif not re.match(pattern,mail):
            st.error('Invalid email! Please try again.')
        else:
            progress_text='In progress.Kindly wait.'
            my_bar=st.progress(0,text=progress_text)
            
            for percent_complete in range(100):
                time.sleep(0.01)
                my_bar.progress(percent_complete+1,text=progress_text)
            st.success('Yipee! Your mashup will arrive shortly in your mailbox')
            directory='Video Files'
            if os.path.exists(directory):
                for filename in os.listdir(directory):
                    file_path=os.path.join(directory,filename)
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
            
            if os.path.exists('mashup.mp3'):
                os.unlink('mashup.mp3')
            
            if os.path.exists('mashup.zip'):
                os.unlink('mashup.zip')
                
            writeup(singer,count,duration,mail)
                    
    


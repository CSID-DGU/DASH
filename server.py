import os, sys
import shutil
import time

username="your-username"

def encode_video(video_name,num):
    EXPORT_mp4 ="MP4Box -add {}{}.h264 video{}.mp4".format(video_name,num,num)
    os.system(EXPORT_mp4)
    os.remove('{}{}.h264'.format(video_name,num))

    EXPORT_encoding="ffmpeg -i video{}.mp4 -an -c:v libx264 -x264opts 'keyint=25:min-keyint=25:no-scenecut' -b:v 600k -maxrate 600k -bufsize 300k -vf 'scale=640:360' video{}-360.mp4".format(num,num)
    os.system(EXPORT_encoding)

    EXPORT_encoding2="ffmpeg -i video{}.mp4 -an -c:v libx264 -x264opts 'keyint=25:min-keyint=25:no-scenecut' -b:v 1060k -maxrate 1060k -bufsize 530k -vf 'scale=854:480' video{}-480.mp4".format(num,num)
    os.system(EXPORT_encoding2)

    EXPORT_encoding3="ffmpeg -i video{}.mp4 -an -c:v libx264 -x264opts 'keyint=25:min-keyint=25:no-scenecut' -b:v 2400k -maxrate 2400k -bufsize 1200k -vf 'scale=1280:720' video{}-720.mp4".format(num,num)
    os.system(EXPORT_encoding3)

def dash_video(segment_len,num):
    EXPORT_dash = "MP4Box -dash {} -rap -frag-rap -profile live -segment-name %s_dash -out video.mpd -mpd-refresh 5 video{}-360.mp4 video{}-480.mp4 video{}-720.mp4".format(segment_len*1000,num,num,num)
    os.system(EXPORT_dash)

def del_files(apache_dir_name,num,segment_num):

    temp = num-10

    os.remove('video{}-720.mp4'.format(temp))
    os.remove('video{}-360.mp4'.format(temp))
    os.remove('video{}-480.mp4'.format(temp))
    os.remove('video{}.mp4'.format(temp))

    for j in range(1,segment_num+1):
        os.remove('video{}-360_dash{}.m4s'.format(temp,j))
        os.remove('video{}-480_dash{}.m4s'.format(temp,j))
        os.remove('video{}-720_dash{}.m4s'.format(temp,j))

    #Apache drive
    for j in range(1,segment_num+1):
        os.remove('{}video{}-360_dash{}.m4s'.format(apache_dir_name,temp,j))
        os.remove('{}video{}-480_dash{}.m4s'.format(apache_dir_name,temp,j))
        os.remove('{}video{}-720_dash{}.m4s'.format(apache_dir_name,temp,j))

def upload_apache(apache_dir_name, num,segment_num):
    #copy mpd and init files to Apache
    os.system("cp video_init.mp4 video.mpd {}".format(apache_dir_name))

    #copy m4s files to Apache
    for j in range(1,segment_num+1):
        os.system("cp video{}-360_dash{}.m4s video{}-480_dash{}.m4s video{}-720_dash{}.m4s {}".format(num,j,num,j,num,j,apache_dir_name))

def main():
    print("* Welcome to the Server")
    i=0

    latest_dir = -1

    video_len = 6 #sec
    segment_len = 2 #sec
    segment_num = video_len//segment_len

    #local drive for video
    dir_name ='/home/{}/dash/videos'.format(username)
    if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    os.mkdir(dir_name)

    #drive for apache
    apache_dir_name = '/var/www/html/video/'
    if os.path.exists(apache_dir_name):
            shutil.rmtree(apache_dir_name)
    os.mkdir(apache_dir_name)

    os.system("cp /var/www/html/.htaccess "+apache_dir_name)

    while True:
        encoding_time=4.8

        #check directory for new video
        dir_name ='/home/{}/dash/videos'.format(username)
        dirs = os.listdir(dir_name)

        if len(dirs)>0:
            for dir in dirs:
                if not os.path.isdir(os.path.join(dir_name,dir)):
                    dirs.remove(dir)

            for i in range(len(dirs)):
                dirs[i]=int(dirs[i])

            if not latest_dir == max(dirs):
                latest_dir = max(dirs)
                i=0

            dir_name = os.path.join(dir_name,str(latest_dir))
            video_name = dir_name+"/"+str(latest_dir)+"_"

            while True:
                n = str(i)
                if os.path.isfile("{}{}.h264".format(video_name,n)):
                    start = time.time()

                    os.chdir(dir_name)
                    encode_video(video_name,i)

                    dash_video(segment_len,i)

                    #delete old files in local drive and Apache
                    if i>10 :
                        del_files(apache_dir_name,i,segment_num)

                    end = time.time()
                    work_time = round(end-start,2)

                    print('\n* No.'+n+' Upload Done. {}.s'.format(work_time))

                    upload_apache(apache_dir_name,i,segment_num)

                    if(work_time<encoding_time):
                        print('* Waiting for proper timing...')
                        time.sleep(encoding_time-work_time)
                    i += 1
                else:
                    continue

if __name__ == "__main__":
    main()

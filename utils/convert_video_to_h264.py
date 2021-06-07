import os,subprocess
import json
import argparse

def convert_video_to_h264(DATASET_DIR,DST_DIR,classname_path):

    mini_classes = []
    with open(classname_path, "r") as f:
        for classname in f.readlines():
            mini_classes.append(classname.strip("\n"))

    error_txt=open("convert_h264_err.txt", "a")
    for class_name in sorted(mini_classes):

        for video in os.listdir(os.path.join(DATASET_DIR,class_name)):
            raw_video_path=os.path.join(DATASET_DIR,class_name,video)

            compressed_video_path=os.path.join(DST_DIR,class_name,video.split(".")[0]+".h264")
            if not os.path.exists(os.path.join(DST_DIR,class_name)):
                os.makedirs(os.path.join(DST_DIR,class_name))
            try:
                result = subprocess.Popen(
                    ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", raw_video_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT)

                data = json.load(result.stdout)
                print(data)
                print("****Codec",data['streams']['codec_name'])
                return_code=subprocess.call(["ffmpeg","-y","-i",raw_video_path,compressed_video_path])
                if return_code != 0:
                    print(raw_video_path)
            except:
                error_txt.write(raw_video_path)
                error_txt.write("\n")
                pass

    error_txt.close()

if __name__=='__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('dir_path',
                        default=None,
                        type=str,
                        help='Directory path of videos')
    parser.add_argument('dst_path',
                        default=None,
                        type=str,
                        help='Directory path of h.264')
    parser.add_argument('classname_path',
                        default='../../../data/mini-ssv2-87-classes.txt',
                        type=str,
                        help='path of dataset classname list')

    args = parser.parse_args()
    convert_video_to_h264(args.dir_path,args.dst_path,args.classname_path)



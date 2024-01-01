import json
from googleapiclient.discovery import build
from pytube import YouTube
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import VideoFileClip
from PIL import Image
from googleapiclient.errors import HttpError


def load_config():
    with open('config.json', 'r') as file:
        config = json.load(file)
    return config.get('api_key'), config.get('channel_id')


def get_latest_video_id(api_key, channel_id):
    youtube = build('youtube', 'v3', developerKey=api_key)
    try:
        request = youtube.search().list(part='id', channelId=channel_id, order='date', type='video', maxResults=1)
        response = request.execute()
        return response['items'][0]['id']['videoId']
    except HttpError as e:
        print(f"Error getting latest video ID: {e}")
        return None


def download_video(video_id, output_path='./', filename='latest_video'):
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    yt = YouTube(video_url)
    video_path = yt.streams.first().download(output_path=output_path, filename=filename)
    return video_path


def convert_to_gif(input_video_path, output_gif_path, target_width=700, target_height=240, target_duration=10):
    clip = VideoFileClip(input_video_path)

    frames = [Image.fromarray(frame) for frame in clip.iter_frames(fps=clip.fps)]
    resized_frames = [frame.resize((target_width, target_height)) for frame in frames]

    num_frames = int(target_duration * clip.fps)

    num_frames = min(num_frames, len(resized_frames))

    resized_frames[0].save(
        output_gif_path,
        save_all=True,
        append_images=resized_frames[1:num_frames],
        duration=target_duration,
        loop=0
    )


def main():
    api_key, channel_id = load_config()
    latest_video_id = get_latest_video_id(api_key, channel_id)

    if latest_video_id:
        video_path = download_video(latest_video_id)
        input_video_path = video_path
        output_gif_path = 'banner.gif'
        convert_to_gif(input_video_path, output_gif_path, target_width=700, target_height=240)


if __name__ == "__main__":
    main()

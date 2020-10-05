#TODO 지현이 코드 넣기
#vid2.mp4가 코드와 같은 폴더에 저장되어있는 영상 이름, audio.wav가 음악 파일 이름이고 코드 실행하면 결과로 output.mp4가 같은 파일에 저장됨
#이 부분도 수정 필요할듯.
def cross_edit():
  os.system("ffmpeg -i vid2.mp4 -i audio.wav -c:v copy -c:a aac output.mp4")

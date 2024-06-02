ffmpeg: ffmpeg-7.0.1
	cd ffmpeg-7.0.1 && ./configure --prefix=../ffmpeg && make && make install && cd .. && rm -rf ffmpeg-7.0.1.tar.xz && rm -rf ffmpeg-7.0.1

ffmpeg-7.0.1:
	wget https://ffmpeg.org/releases/ffmpeg-7.0.1.tar.xz
	tar -xf ffmpeg-7.0.1.tar.xz
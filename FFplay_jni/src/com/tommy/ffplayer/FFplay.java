package com.tommy.ffplayer;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.util.Log;

import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioTrack;

public class FFplay extends Activity
{
	/** Called when the activity is first created. */

	/*
	 * A native method that is implemented by the 'hello-jni' native library,
	 * which is packaged with this application.
	 */
	public native int FFplayInit();

	public native int FFplayExit();

	public native int FFplayOpenFile(String name);

	public native int FFplayCloseFile();

	public native byte[] FFplayDecodeFrame();

	public native String FFplayGetStreamInfo();

	private final static String TAG = "ffplay-java";
	private AudioTrack at = null;
	private int min_buf_size;
	private boolean bRunning = false;
	private Thread thPlay;

	private Button mButton1, mButton2, mButton3;
	private TextView tv1;

	@Override
	public void onCreate(Bundle savedInstanceState)
	{

		super.onCreate(savedInstanceState);
		setContentView(R.layout.main);

		mButton1 = (Button) findViewById(R.id.button1);
		mButton1.setOnClickListener(handler_button1);

		mButton2 = (Button) findViewById(R.id.button2);
		mButton2.setOnClickListener(handler_button2);

		tv1 = (TextView) findViewById(R.id.textview1);
		Log.i(TAG, "ffplay oncreate !");

		AudioTrack_init();
		FFplayInit();

	}

	/*
	 * this is used to load the 'hello-jni' library on application startup. The
	 * library has already been unpacked into
	 * /data/data/com.example.HelloJni/lib/libhello-jni.so at installation time
	 * by the package manager.
	 */
	static
	{
		System.loadLibrary("ffplay_jni");
	}
	/*
	 * playing wave
	 */
	Button.OnClickListener handler_button1 = new Button.OnClickListener()
	{
		@Override
		public void onClick(View arg0)
		{
			if (bRunning)
				return;

			at.play();
			FFplayOpenFile(new String("/mnt/sdcard/srv/stream/vs.mp4"));
			tv1.setText(FFplayGetStreamInfo());
			bRunning = true;
			thPlay = new Thread()
			{
				@Override
				public void run()
				{
					try
					{
						while (bRunning)
						{
							byte[] outpcm;
							outpcm = FFplayDecodeFrame();
							if (outpcm == null)
							{
								bRunning = false;
								Log.i(TAG, "outpcm got null.");
							}
							else
							{
								at.write(outpcm, 0, outpcm.length);
							}
							Thread.sleep(1);
						}
						at.stop();
						FFplayCloseFile();
						bRunning = false;

					} catch (Exception e)
					{
						// TODO Auto-generated catch block
						e.printStackTrace();
					}
				}
			};
			thPlay.start();
		}

	};

	/*
	 * Stop
	 */
	Button.OnClickListener handler_button2 = new Button.OnClickListener()
	{
		@Override
		public void onClick(View arg0)
		{
			bRunning = false;
		}
	};

	/*
	 * Init Audio Track.
	 */
	private void AudioTrack_init()
	{
		// Get Min Buffer Size
		min_buf_size = AudioTrack.getMinBufferSize(44100, AudioFormat.CHANNEL_OUT_STEREO, AudioFormat.ENCODING_PCM_16BIT);

		// New
		at = new AudioTrack(AudioManager.STREAM_MUSIC, 44100, AudioFormat.CHANNEL_OUT_STEREO, AudioFormat.ENCODING_PCM_16BIT, min_buf_size * 2, AudioTrack.MODE_STREAM);
		Log.d(TAG, "volume " + at.getMinVolume() + " -- " + at.getMaxVolume());
		Log.d(TAG, "audio track's min. buffer is " + min_buf_size);
	}

}
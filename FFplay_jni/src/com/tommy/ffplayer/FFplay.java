package com.tommy.ffplayer;

import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.view.View;
import android.widget.Button;
import android.widget.ProgressBar;
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
	// AUDIO TRACK
	private AudioTrack at = null;
	private int min_buf_size;
	private boolean bRunning = false;
	private Thread thPlay;
	private int at_srate = 44100;
	private int at_channel = AudioFormat.CHANNEL_OUT_STEREO;
	private int frame;
	// VIEW
	private Button mButton1, mButton2, mButton3;
	private TextView tv1, tv2, tv3, tv4;
	private ProgressBar progbar;
	// HANDLE
	private Handler handler = null;
	protected static final int GUI_UPDATE_PROGRESS = 0x100;
	protected static final int GUI_PLAYEND = 0x101;

	@Override
	public void onCreate(Bundle savedInstanceState)
	{

		super.onCreate(savedInstanceState);
		setContentView(R.layout.main);

		mButton1 = (Button) findViewById(R.id.button1);
		mButton1.setOnClickListener(handler_button1);
		mButton2 = (Button) findViewById(R.id.button2);
		mButton2.setOnClickListener(handler_button2);
		tv1 = (TextView) findViewById(R.id.TextView1);
		tv2 = (TextView) findViewById(R.id.TextView2);
		tv3 = (TextView) findViewById(R.id.TextView3);
		tv4 = (TextView) findViewById(R.id.TextView4);
		progbar = (ProgressBar) findViewById(R.id.progressBar1);
		Log.i(TAG, "ffplay oncreate !");

		initHandles();
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
	 * Can only update UI in handle.
	 */
	private void initHandles()
	{
		// Create Main MSG handler
		handler = new Handler()
		{
			@Override
			public void handleMessage(Message msg)
			{
				switch (msg.what)
				{
					case GUI_UPDATE_PROGRESS:
						tv3.setText("playing frame " + frame);
						if (progbar.getProgress() >= progbar.getMax())
							progbar.setProgress(0);
						progbar.incrementProgressBy(1);
						break;

					case GUI_PLAYEND:
						progbar.setProgress(0);
						tv3.setText("play end!");
						break;
				}
				super.handleMessage(msg);
			}
		};
	}

	/*
	 * playing wave
	 */
	Button.OnClickListener handler_button1 = new Button.OnClickListener()
	{
		@Override
		public void onClick(View arg0)
		{
			String filename = new String("/mnt/sdcard/srv/stream/vs.mp4"); 
//			String filename = new String("/mnt/sdcard/srv/stream/VIDEO0001.3gp");

			if (bRunning)
				return;

			at.play();
			FFplayOpenFile(filename);
			tv1.setText(filename);
			// FFplayOpenFile(new String

			tv4.setText(FFplayGetStreamInfo());
			bRunning = true;
			thPlay = new Thread()
			{
				@Override
				public void run()
				{
					try
					{
						frame = 0;
						while (bRunning)
						{
							byte[] outpcm;
							outpcm = FFplayDecodeFrame();

							if (outpcm == null)
							{
								bRunning = false;
								Log.i(TAG, "outpcm got null.");
							} else
							{
								if (outpcm[0] == 1)
								{ // If audio data.
									at.write(outpcm, 40, outpcm.length - 40);
								} else
								{	// If video data.
									handler.sendEmptyMessage(GUI_UPDATE_PROGRESS);
									frame++;									
									Log.d(TAG, "SKIP VIDEO DATA " + outpcm.length + " BYTES.");
								}
							}
							Thread.sleep(1);
						}
						at.stop();
						FFplayCloseFile();
						bRunning = false;
						handler.sendEmptyMessage(GUI_PLAYEND);

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
		min_buf_size = AudioTrack.getMinBufferSize(at_srate, at_channel, AudioFormat.ENCODING_PCM_16BIT);

		// New
		at = new AudioTrack(AudioManager.STREAM_MUSIC, at_srate, at_channel, AudioFormat.ENCODING_PCM_16BIT, min_buf_size * 2, AudioTrack.MODE_STREAM);
		Log.d(TAG, "volume " + at.getMinVolume() + " -- " + at.getMaxVolume());
		Log.d(TAG, "audio track's min. buffer is " + min_buf_size);
	}

}
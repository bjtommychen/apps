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

import android.view.Surface;
import android.view.SurfaceHolder;
import android.view.SurfaceView;

import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.PixelFormat;
import android.graphics.RectF;
import android.graphics.Bitmap.Config;

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
	private boolean bRunning = false, bOpenfile = false;
	private Thread thPlay;
	private int at_srate = 44100;
	private int at_channel = AudioFormat.CHANNEL_OUT_STEREO;
	private int frame;
	// VIEW
	private Button btn_open, btn_play, btn_stop;
	private TextView tv1, tv2, tv3, tv4;
	private ProgressBar progbar;
	// HANDLE
	private Handler handler = null;
	protected static final int GUI_UPDATE_PROGRESS = 0x100;
	protected static final int GUI_PLAYEND = 0x101;
	// SURFACE
	private SurfaceView mSurfaceView1;
	private SurfaceHolder mSurfaceHolder1;

	@Override
	public void onCreate(Bundle savedInstanceState)
	{

		super.onCreate(savedInstanceState);
		setContentView(R.layout.main);

		btn_open = (Button) findViewById(R.id.button_open);
		btn_open.setOnClickListener(handler_button3);
		btn_play = (Button) findViewById(R.id.button_play);
		btn_play.setOnClickListener(handler_button1);
		btn_stop = (Button) findViewById(R.id.button_stop);
		btn_stop.setOnClickListener(handler_button2);
		tv1 = (TextView) findViewById(R.id.TextView1);
		tv2 = (TextView) findViewById(R.id.TextView2);
		tv3 = (TextView) findViewById(R.id.TextView3);
		tv4 = (TextView) findViewById(R.id.TextView4);
		progbar = (ProgressBar) findViewById(R.id.progressBar1);
		Log.i(TAG, "ffplay oncreate !");

		mSurfaceView1 = (SurfaceView) findViewById(R.id.surfaceView1);
		mSurfaceHolder1 = mSurfaceView1.getHolder();
		// mSurfaceHolder1.setFormat(PixelFormat.L_8);
		// mSurfaceHolder1.setType(SurfaceHolder.SURFACE_TYPE_PUSH_BUFFERS);

		mSurfaceHolder1.addCallback(new SurfaceHolder.Callback()
		{

			public void surfaceChanged(SurfaceHolder holder, int format, int width, int height)
			{
				Log.v(TAG, "surfaceChanged format=" + format + ", width=" + width + ", height=" + height);
			}

			public void surfaceCreated(SurfaceHolder holder)
			{
				Log.v(TAG, "surfaceCreated");
				// setSurface(holder.getSurface());
			}

			public void surfaceDestroyed(SurfaceHolder holder)
			{
				Log.v(TAG, "surfaceDestroyed");
			}
		});

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

						// if (false)
						// {
						// Canvas canvas = mSurfaceHolder1.lockCanvas();// 获取画布
						// Bitmap bitmap = Bitmap.createBitmap(canvas.getWidth()
						// / 2, canvas.getHeight() / 2, Config.ALPHA_8);
						// if (canvas == null)
						// break;
						// Paint mPaint = new Paint();
						// mPaint.setColor(Color.BLUE);
						// canvas.drawRect(new RectF(0, 0, canvas.getWidth() /
						// 2, canvas.getHeight() / 2), mPaint);
						// mPaint.setColor(Color.RED);
						// canvas.drawCircle(50, 50, 50, mPaint);
						// mSurfaceHolder1.unlockCanvasAndPost(canvas);//
						// 解锁画布，提交画好的图像
						// }

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

	Button.OnClickListener handler_button3 = new Button.OnClickListener()
	{
		@Override
		public void onClick(View arg0)
		{
			String filename = new String("/mnt/sdcard/srv/stream/vs.mp4");
			// String("/mnt/sdcard/srv/stream/VIDEO0001.3gp");
			if (bRunning)
				return;

			FFplayOpenFile(filename);
			tv1.setText(filename);
			tv4.setText(FFplayGetStreamInfo());
			bOpenfile = true;
		}
	};

	/*
	 * playing wave
	 */
	Button.OnClickListener handler_button1 = new Button.OnClickListener()
	{
		@Override
		public void onClick(View arg0)
		{
			if (bOpenfile == false)
				return;
			at.play();
			tv4.setText("");
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
							int[] outyuv;

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
								} else if (outpcm[0] == 2)
								{ // If video data.
									// Log.d(TAG, "SKIP VIDEO DATA " +
									// outpcm.length + " BYTES.");
									if (true)
									{
										int i, j, vw, vh, cw, ch, w, h;
										int linesize;
										byte c;
										Canvas canvas = mSurfaceHolder1.lockCanvas();// 获取画布
										cw = canvas.getWidth();
										ch = canvas.getHeight();
										vw = 640; // linesize 672, 336
										vh = 360;
										linesize = 672;
										if (canvas == null)
											break;
										outyuv = new int[vh * linesize];// [outpcm.length-40];
										for (j = 0; j < vh; j++)
											for (i = 0; i < vw; i++)
											{
												c = outpcm[40 + vw * j + i];
												outyuv[vw * j + i] = Color.argb(0xff, c, c, c);
											}
										canvas.drawBitmap(outyuv, 0, linesize, 0, 0, cw, vh, false, null);
										Paint mPaint = new Paint();
										mPaint.setColor(Color.RED);
										canvas.drawText("Demo", 10, 10, mPaint);
										mSurfaceHolder1.unlockCanvasAndPost(canvas);// 解锁画布，提交画好的图像
									}
									if (frame % 5 == 0)
										handler.sendEmptyMessage(GUI_UPDATE_PROGRESS);
									frame++;
								}
							}
							// Thread.sleep(1);
						}
						at.stop();
						FFplayCloseFile();
						bOpenfile = false;
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
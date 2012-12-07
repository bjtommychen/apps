package com.tommy.ffplayer;

import org.apache.http.util.ByteArrayBuffer;

import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.ProgressBar;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.ToggleButton;
import android.util.Log;

import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioTrack;

import android.view.Surface;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import android.view.Window;

import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.PixelFormat;
import android.graphics.RectF;
import android.graphics.Bitmap.Config;

import java.util.ArrayList;
import java.io.File;

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

	public native int[] FFplayConvertRGB();

	public native int FFplayConvertGray(int[] buf);

	public native byte[] FFplayGetPCM();

	private final static String TAG = "ffplay-java";
	
	// AUDIO TRACK
	private AudioTrack at = null;
	private int min_buf_size;
	private boolean bRunning = false, bOpenfile = false;
	private Boolean bAVoutput = true;
	private Thread thPlay;
	private int at_srate = 44100;
	private int at_channel = AudioFormat.CHANNEL_OUT_STEREO;
	private int frame, frame_fps;
	
	// VIEW
	private Button btn_open, btn_play, btn_stop;
	private ToggleButton tbtn_output;
	private TextView tv1, tv2, tv3, tv4;
	private ProgressBar progbar;
	private final static String StartDir = "/mnt/sdcard/stream/";
	private final static String StartDir2 = "/mnt/ext_sdcard/stream/";
	
	// HANDLE
	private Handler handler_UI = null;
	protected static final int GUI_UPDATE_PROGRESS = 0x100;
	protected static final int GUI_PLAYEND = 0x101;
	
	// SURFACE
	private SurfaceView mSurfaceView1;
	private SurfaceHolder mSurfaceHolder1;

	private String mSourceString;
	private DecInfo decinfo;

	// Time
	private long tstart, telapsed, tend;

	// Add this class to emulate structure in C.
	private class DecInfo
	{
		short magic; // must be MAGIC_ID
		short header_len; // sizeof this structure.
		short type; // 1: audio, 2:video
		// Audio
		short samplerate, channel, bitspersample;
		// Video
		short yuv_format;
		short width, height;
		short linesizeY, linesizeU, linesizeV;

		public void parse(byte[] buf)
		{
			int i;
			short v;
			short[] hdr = new short[20];
			for (i = 0; i < 12; i++)
			{
				hdr[i] = (short) (((short) buf[2 * i + 1] & 0xff) << 8 | (short) buf[2 * i] & 0xff);
				// Log.v(TAG, "decinfo parse." + i + " value " +
				// String.format("0x%x", hdr[i]));
			}
			magic = hdr[0];
			header_len = hdr[1];
			type = hdr[2];
			samplerate = hdr[3];
			channel = hdr[4];
			bitspersample = hdr[5];
			yuv_format = hdr[6];
			width = hdr[7];
			height = hdr[8];
			linesizeY = hdr[9];
			linesizeU = hdr[10];
			linesizeV = hdr[11];
			// Log.v(TAG, "decinfo parse." + header_len + " width " + width);
		}
	}

	@Override
	public void onCreate(Bundle savedInstanceState)
	{

		super.onCreate(savedInstanceState);
		requestWindowFeature(Window.FEATURE_NO_TITLE);
		setContentView(R.layout.main);

		btn_open = (Button) findViewById(R.id.button_open);
		btn_open.setOnClickListener(handler_btnopen);
		btn_play = (Button) findViewById(R.id.button_play);
		btn_play.setOnClickListener(handler_btnplay);
		btn_stop = (Button) findViewById(R.id.button_stop);
		btn_stop.setOnClickListener(handler_btnstop);
		tbtn_output = (ToggleButton) findViewById(R.id.toggleButton1);
		tv1 = (TextView) findViewById(R.id.TextView1);
		tv2 = (TextView) findViewById(R.id.TextView2);
		tv3 = (TextView) findViewById(R.id.TextView3);
		tv4 = (TextView) findViewById(R.id.TextView4);
		progbar = (ProgressBar) findViewById(R.id.progressBar1);
		Log.i(TAG, "ffplay onCreate !");

		mSurfaceView1 = (SurfaceView) findViewById(R.id.surfaceView1);
		mSurfaceHolder1 = mSurfaceView1.getHolder();
		// mSurfaceHolder1.setFormat(PixelFormat.RGBA_8888);
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

		// initialize content source spinner
		Spinner sourceSpinner = (Spinner) findViewById(R.id.spinner1);
//		ArrayAdapter<CharSequence> sourceAdapter = ArrayAdapter.createFromResource(this, R.array.source_array, android.R.layout.simple_spinner_item);
		ArrayList<CharSequence> source_array = new ArrayList<CharSequence>();
		ArrayAdapter<CharSequence> sourceAdapter = new ArrayAdapter<CharSequence>(this, android.R.layout.simple_spinner_item, source_array);
//		
		sourceAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
		sourceSpinner.setAdapter(sourceAdapter);
		
		{
			File file;
			File[] files;
			String PathName;
			
			PathName = StartDir;
			file = new File(PathName);
			files = file.listFiles();
			if (file == null || files == null)
			{
				PathName = StartDir2;
				file = new File(PathName);
				files = file.listFiles();
			}
			
			if (files != null)
			{
				for (File fileitem : files) {
					String name;
					name  = PathName + fileitem.getName();
					if (!fileitem.isDirectory())
						sourceAdapter.add(name);
					else
						sourceAdapter.add("< " + name + " >"); // like
				}
			}
			else
			{
				sourceAdapter.add("Empty, no file found! ");
			}
		}
		
		sourceSpinner.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener()
		{

			public void onItemSelected(AdapterView<?> parent, View view, int pos, long id)
			{
				mSourceString = parent.getItemAtPosition(pos).toString();
				Log.v(TAG, "onItemSelected " + mSourceString);
			}

			public void onNothingSelected(AdapterView<?> parent)
			{
				Log.v(TAG, "onNothingSelected");
				mSourceString = null;
			}

		});

		tbtn_output.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener()
		{
			@Override
			public void onCheckedChanged(CompoundButton buttonView, boolean isChecked)
			{
				if (buttonView.getId() == R.id.toggleButton1)
					bAVoutput = isChecked;
			}
		});

		decinfo = new DecInfo();
		initHandles();
		AudioTrack_init();
		FFplayInit();
	}

	@Override
	protected void onDestroy()
	{
		bRunning = false;
		if (at != null)
		{
			at.stop();
			at.flush();
		}
		FFplayCloseFile();
		bOpenfile = false;
		FFplayExit();
		super.onDestroy();
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

		// Create Main MSG handler_UI
		handler_UI = new Handler()
		{
			float fps = 0;

			@Override
			public void handleMessage(Message msg)
			{
				switch (msg.what)
				{
					case GUI_UPDATE_PROGRESS:
						if ((frame - frame_fps) >= 30)
						{
							tend = System.currentTimeMillis();
							telapsed = tend - tstart;
							fps = (float) ((float) (frame - frame_fps) * 1000. / telapsed);
							tstart = tend;
							frame_fps = frame;
						}
						String fps_str = String.format("%.2f", fps);
						tv3.setText("Frame " + frame + ", -------  FPS: " + fps_str);
//						tv3.setText("Frame " + frame);
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
						tv3.setText("frame " + frame + ", play end!");
						break;
				}
				super.handleMessage(msg);
			}
		};
	}

	Button.OnClickListener handler_btnopen = new Button.OnClickListener()
	{
		@Override
		public void onClick(View arg0)
		{

			String filename = mSourceString;

			if (bRunning)
				return;

			if (FFplayOpenFile(filename) == 0)
			{
				tv1.setText(filename);
				tv4.setText(FFplayGetStreamInfo());
				bOpenfile = true;
			}
		}
	};

	/*
	 * playing wave
	 */
	Button.OnClickListener handler_btnplay = new Button.OnClickListener()
	{
		@Override
		public void onClick(View arg0)
		{
			if (bOpenfile == false)
				return;
			if (at != null)
				at.play();
			tv4.setText("");
			bRunning = true;

			thPlay = new Thread()
			{
				byte[] out_hdr = null;
				byte[] outpcm = null;
				int[] outyuv = null;

				@Override
				public void run()
				{
					try
					{
						frame = 0;
						frame_fps = 0;
						tstart = System.currentTimeMillis();
						while (bRunning)
						{
							out_hdr = FFplayDecodeFrame();

							if (out_hdr == null)
							{
								bRunning = false;
								Log.i(TAG, "out_hdr got null.");
							} else
							{
								// parse the info header from ffmpeg
								decinfo.parse(out_hdr);
								if (decinfo.type == 1)
								{ // If audio data.
									if (decinfo.bitspersample == 16)
									{
										outpcm = FFplayGetPCM();
										if (bAVoutput && outpcm != null)
										{
											if (at != null)
												at.write(outpcm, 0, outpcm.length);
										}
									}
								} else if (decinfo.type == 2)
								{ // If video data.
									if (bAVoutput)
									{
										int i, j, vw, vh, cw, ch, w, h;
										int linesize;
										// outyuv = FFplayConvertRGB();
										Canvas canvas = mSurfaceHolder1.lockCanvas();// 获取画布
										cw = canvas.getWidth();
										ch = canvas.getHeight();
										vw = decinfo.width; // linesize 672, 336
										vh = decinfo.height;
										linesize = decinfo.linesizeY;
										if (outyuv == null)
											outyuv = new int[linesize * vh];
										FFplayConvertGray(outyuv);
										if (canvas != null)
										{
											int x = 0, y = 0;
											// make video centered in canvas.
											if (vw > cw)
											{
												x = (vw - cw) / 2;
											}
											// if (vh > ch)
											// {
											// y = (vh - ch) / 2;
											// }
											canvas.drawBitmap(outyuv, 0, linesize, -x, 0, Math.min(cw, vw) + x, Math.min(ch, vh), false, null);
											Paint mPaint = new Paint();
											mPaint.setColor(Color.RED);
											canvas.drawText("FFplay Demo", 0, 10, mPaint);
											mSurfaceHolder1.unlockCanvasAndPost(canvas);// 解锁画布，提交画好的图像
										}
									}
									frame++;
									if (frame % 5 == 0)
									{
										handler_UI.sendEmptyMessage(GUI_UPDATE_PROGRESS);
									}
								}
							}
							// Thread.sleep(1);
						}
						if (at != null)
						{
							at.stop();
							at.flush();
						}
						FFplayCloseFile();
						bOpenfile = false;
						bRunning = false;
						handler_UI.sendEmptyMessage(GUI_PLAYEND);

					} catch (Exception e)
					{
						at.stop();
						at.flush();
						FFplayCloseFile();
						bOpenfile = false;
						bRunning = false;
						handler_UI.sendEmptyMessage(GUI_PLAYEND);
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
	Button.OnClickListener handler_btnstop = new Button.OnClickListener()
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

        final int TEST_SR = 22050;
        final int TEST_CONF = AudioFormat.CHANNEL_OUT_STEREO;
        final int TEST_FORMAT = AudioFormat.ENCODING_PCM_16BIT;
        final int TEST_MODE = AudioTrack.MODE_STREAM;
        final int TEST_STREAM_TYPE = AudioManager.STREAM_MUSIC;
        
		
		
		// Get Min Buffer Size
        //-------- initialization --------------
//      int minBuffSize = AudioTrack.getMinBufferSize(TEST_SR, TEST_CONF, TEST_FORMAT);
		min_buf_size = AudioTrack.getMinBufferSize(at_srate, at_channel, AudioFormat.ENCODING_PCM_16BIT);

		// New
		at = new AudioTrack(AudioManager.STREAM_MUSIC, at_srate, at_channel, AudioFormat.ENCODING_PCM_16BIT, min_buf_size * 2, AudioTrack.MODE_STREAM);
//        at = new AudioTrack(TEST_STREAM_TYPE, TEST_SR, TEST_CONF, TEST_FORMAT, 
//        		min_buf_size, TEST_MODE);		
		
		if (at != null)
		{
			Log.d(TAG, "AudioTrack init done!");
		}
		Log.d(TAG, "volume " + at.getMinVolume() + " -- " + at.getMaxVolume());
		Log.d(TAG, "audio track's min. buffer is " + min_buf_size);
		Log.d(TAG, "audio track native sample rate is " + at.getNativeOutputSampleRate(AudioManager.STREAM_MUSIC));
	}

}












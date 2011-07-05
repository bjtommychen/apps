package com.tommy.test.audiotest;

import android.app.Activity;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import android.view.View;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;

import android.os.Environment;
import android.util.Log;

import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioTrack;

public class AudioTest extends Activity
{
	private final static String TAG = "audiotest";
	private AudioTrack at = null;
	private int min_buf_size;
	private boolean bRunning = false;
	private Thread thPlay;

	// wav info
	private byte[] wavheader = new byte[44];
	private long myChunkSize;
	private long mySubChunk1Size;
	private int myFormat;
	private short myChannels;
	private int mySampleRate;
	private long myByteRate;
	private int myBlockAlign;
	private short myBitsPerSample;
	private long myDataSize;

	//
	private Button mButton1, mButton2, mButton3;
	private TextView tv1;
	private FileInputStream fins;

	/** Called when the activity is first created. */
	@Override
	public void onCreate(Bundle savedInstanceState)
	{
		super.onCreate(savedInstanceState);
		setContentView(R.layout.main);

		mButton1 = (Button) findViewById(R.id.button1);
		mButton1.setOnClickListener(handler_button1);

		mButton2 = (Button) findViewById(R.id.button2);
		mButton2.setOnClickListener(handler_button2);

		mButton3 = (Button) findViewById(R.id.button3);
		mButton3.setOnClickListener(handler_button3);

		Log.i(TAG, "audio test start !");

		tv1 = (TextView) findViewById(R.id.textview1);
		tv1.setText(stringFromJNI());

		audiotrack_init();

	}

	/*
	 * A native method that is implemented by the 'hello-jni' native library,
	 * which is packaged with this application.
	 */
	public native String stringFromJNI();

	public native int mp3decInit();

	public native int mp3decExit();

	public native int mp3decRun();

	public native int mp3decGetInputDataLen();

	public native int mp3decFillData(byte[] buf, int len);

	public native int mp3decGetOutputPcmLen();

	public native byte[] mp3decGetOutputPcmBuff(byte[] buf);

	/*
	 * this is used to load the 'hello-jni' library on application startup. The
	 * library has already been unpacked into
	 * /data/data/com.example.HelloJni/lib/libhello-jni.so at installation time
	 * by the package manager.
	 */
	static
	{
		System.loadLibrary("mp3dec");
	}

	/*
	 * playing wave
	 */
	Button.OnClickListener handler_button1 = new Button.OnClickListener()
	{
		public void onClick(View arg0)
		{
			try
			{
				readFileWav("media/hero.wav", true);
				parseWavHeader(wavheader);
				playwav();

			} catch (Exception e)
			{
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
	};

	/*
	 * Stop
	 */
	Button.OnClickListener handler_button2 = new Button.OnClickListener()
	{
		public void onClick(View arg0)
		{
			bRunning = false;
		}
	};

	/*
	 * Playing mp3
	 */
	Button.OnClickListener handler_button3 = new Button.OnClickListener()
	{
		// play mp3
		public void onClick(View arg0)
		{
			bRunning = false;
			try
			{
				playMp3("media/spring_mud.mp3");
			} catch (Exception e)
			{
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
	};

	private void readFileWav(String fileName, boolean isSdcard) throws Exception
	{
		// byte[] buf = new byte[1024];
		int len = 0;

		fins = null;

		if (isSdcard)
		{
			File file = new File(Environment.getExternalStorageDirectory(), fileName);
			fins = new FileInputStream(file);
		} else
		{
			// fins = context.openFileInput(fileName);
			fins = new FileInputStream(fileName);
		}

		// Read wav header.
		len = fins.read(wavheader, 0, 44);

		// while ((len = fins.read(buf)) != -1)
		{
			// Log.d(TAG, "read bytes " + len);
			// bouts.write(buf, 0, len);
		}
		// byte[] data = bouts.toByteArray();
		// fins.close();
		// bouts.close();
	}

	/*
	 * Playing mp3.
	 */
	private void playMp3(String fileName) throws Exception
	{
		int len = 0;

		fins = null;
		File file = new File(Environment.getExternalStorageDirectory(), fileName);
		fins = new FileInputStream(file);

		mp3decInit();

		bRunning = true;
		at.play();

		thPlay = new Thread()
		{
			@Override
			public void run()
			{
				int readlen, outlen, writelen;
				int count = 0;
				int total = 0;
				byte[] inData;
				byte[] outPcm;
				// byte[] audioout;

				try
				{
					// inData = new byte[977 * 2];
					outPcm = new byte[1152 * 2 * 2];
					while (bRunning == true)
					{
						// Read data
						readlen = mp3decGetInputDataLen();
						Log.i(TAG, "Frame " + count++);
						Log.d(TAG, "mp3decGetInputDataLen return short. " + readlen);

						if (readlen > 0)
						{
							Log.d(TAG, "new indata");
							inData = new byte[readlen * 2];
							Log.d(TAG, "before read");

							readlen = fins.read(inData);
							if (readlen == -1)
							{
								bRunning = false; // Exit
								continue;
							}
							total += readlen;
							Log.d(TAG, "total bytes " + total);
							Log.d(TAG, "fins.read read byte. " + readlen);
							mp3decFillData(inData, readlen);
							inData = null;
						}
						// Run
						if (mp3decRun() != 0)
							continue;

						/*
						 * stop at frame 515, size 323kbytes.
						 */
						
						
						// Output
						outlen = mp3decGetOutputPcmLen();
						Log.d(TAG, "output pcm byte. " + outlen);
						if (outlen > 0)
						{
							// outPcm = new byte[outlen];
							mp3decGetOutputPcmBuff(outPcm);
							Log.d(TAG, "get pcm done.");
							// Audio out

							writelen = at.write(outPcm, 0, outlen);
							Log.d(TAG, "write2audio bytes " + writelen);
							// outPcm = null;
						}
						Thread.sleep(1);
					}
					fins.close();
					mp3decExit();

				} catch (IOException e)
				{
					// TODO Auto-generated catch block
					e.printStackTrace();
				} catch (InterruptedException e)
				{
					// TODO Auto-generated catch block
					e.printStackTrace();
				}

				at.stop();
			}
		};
		thPlay.start();

	}

	/*
	 * Read wav header.
	 */
	private void parseWavHeader(byte[] header)
	{
		/*
		 * WAV File Specification FROM
		 * http://ccrma.stanford.edu/courses/422/projects/WaveFormat/ The
		 * canonical WAVE format starts with the RIFF header: 0 4 ChunkID
		 * Contains the letters "RIFF" in ASCII form (0x52494646 big-endian
		 * form). 4 4 ChunkSize 36 + SubChunk2Size, or more precisely: 4 + (8 +
		 * SubChunk1Size) + (8 + SubChunk2Size) This is the size of the rest of
		 * the chunk following this number. This is the size of the entire file
		 * in bytes minus 8 bytes for the two fields not included in this count:
		 * ChunkID and ChunkSize. 8 4 Format Contains the letters "WAVE"
		 * (0x57415645 big-endian form).
		 * 
		 * The "WAVE" format consists of two subchunks: "fmt " and "data": The
		 * "fmt " subchunk describes the sound data's format: 12 4 Subchunk1ID
		 * Contains the letters "fmt " (0x666d7420 big-endian form). 16 4
		 * Subchunk1Size 16 for PCM. This is the size of the rest of the
		 * Subchunk which follows this number. 20 2 AudioFormat PCM = 1 (i.e.
		 * Linear quantization) Values other than 1 indicate some form of
		 * compression. 22 2 NumChannels Mono = 1, Stereo = 2, etc. 24 4
		 * SampleRate 8000, 44100, etc. 28 4 ByteRate == SampleRate *
		 * NumChannels * BitsPerSample/8 32 2 BlockAlign == NumChannels *
		 * BitsPerSample/8 The number of bytes for one sample including all
		 * channels. I wonder what happens when this number isn't an integer? 34
		 * 2 BitsPerSample 8 bits = 8, 16 bits = 16, etc.
		 * 
		 * The "data" subchunk contains the size of the data and the actual
		 * sound: 36 4 Subchunk2ID Contains the letters "data" (0x64617461
		 * big-endian form). 40 4 Subchunk2Size == NumSamples * NumChannels *
		 * BitsPerSample/8 This is the number of bytes in the data. You can also
		 * think of this as the size of the read of the subchunk following this
		 * number. 44 * Data The actual sound data.
		 * 
		 * 
		 * NOTE TO READERS:
		 * 
		 * The thing that makes reading wav files tricky is that java has no
		 * unsigned types. This means that the binary data can't just be read
		 * and cast appropriately. Also, we have to use larger types than are
		 * normally necessary.
		 * 
		 * In many languages including java, an integer is represented by 4
		 * bytes. The issue here is that in most languages, integers can be
		 * signed or unsigned, and in wav files the integers are unsigned. So,
		 * to make sure that we can store the proper values, we have to use
		 * longs to hold integers, and integers to hold shorts.
		 * 
		 * Then, we have to convert back when we want to save our wav data.
		 * 
		 * It's complicated, but ultimately, it just results in a few extra
		 * functions at the bottom of this file. Once you understand the issue,
		 * there is no reason to pay any more attention to it.
		 * 
		 * 
		 * ALSO:
		 * 
		 * This code won't read ALL wav files. This does not use to full
		 * specification. It just uses a trimmed down version that most wav
		 * files adhere to.
		 */
		myChannels = (short) (header[23] << 8 | header[22]);
		myBitsPerSample = (short) (header[35] << 8 | header[34]);
		mySampleRate = (int) (header[27] << 24 | header[26] << 16 | (header[25] << 8 | header[24]) & 0xffff);
		// mySampleRate &= 0xffff;
		Log.d(TAG, String.format("%#x", mySampleRate));
		String info;
		info = "wave info:  " + myChannels + "channel, " + myBitsPerSample + "bits, " + mySampleRate + "hz !";
		Log.d(TAG, info);

		tv1.setText(info);
	}

	/*
	 * Init Audio Track.
	 */
	private void audiotrack_init()
	{
		// Get Min Buffer Size
		min_buf_size = AudioTrack.getMinBufferSize(44100, AudioFormat.CHANNEL_CONFIGURATION_STEREO, AudioFormat.ENCODING_PCM_16BIT);

		// New
		at = new AudioTrack(AudioManager.STREAM_MUSIC, 44100, AudioFormat.CHANNEL_CONFIGURATION_STEREO, AudioFormat.ENCODING_PCM_16BIT, min_buf_size*2, AudioTrack.MODE_STREAM);
		Log.d(TAG, "volume " + at.getMinVolume() + " -- " + at.getMaxVolume());
		Log.d(TAG, "min buffer is " + min_buf_size);
	}

	/*
	 * Play wav.
	 */
	private void playwav() throws IOException
	{
		bRunning = true;
		at.play();

		thPlay = new Thread()
		{
			@Override
			public void run()
			{
				int len;
				byte[] audioData;

				audioData = new byte[min_buf_size * 2];
				try
				{
					while ((len = fins.read(audioData)) != -1 && bRunning == true)
					{
						Log.d(TAG, "write bytes " + len);
						at.write(audioData, 0, audioData.length);
//						Thread.sleep(1);
					}
				} catch (IOException e)
				{
					// TODO Auto-generated catch block
					e.printStackTrace();
				}

				at.stop();
			}
		};
		thPlay.start();

	}

	/*
	 * Int to Byte.
	 */
	public static byte[] int2byte(int n)
	{
		byte[] b = new byte[4];
		b[0] = (byte) (n >> 24);
		b[1] = (byte) (n >> 16);
		b[2] = (byte) (n >> 8);
		b[3] = (byte) (n);

		return b;
	}

}

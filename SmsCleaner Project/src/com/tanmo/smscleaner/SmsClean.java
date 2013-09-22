package com.tanmo.smscleaner;

// TODO version notes
// TODO select all
// 

import android.app.Activity;
import android.app.ProgressDialog;
import android.os.Bundle;
import android.os.SystemClock;

import android.text.util.Linkify;
import android.util.Log;
import android.net.Uri;
import android.database.Cursor;
import android.graphics.Color;
import android.graphics.Typeface;
import java.util.*;
import android.widget.*;
import android.view.*;
import android.content.Context;
import android.content.DialogInterface;
import android.os.Handler;
import android.os.Message;
import android.provider.ContactsContract;
import android.app.AlertDialog;
import android.content.ContentResolver;
import android.content.pm.PackageManager.NameNotFoundException;

public class SmsClean extends Activity
{
	static final String TAG = "smsclean";
	static final boolean debugmode = true; // 0 for release mode.
	static final int MAX_SMS_BROWSE = 10000; // Tommy: max sms displayed. too
	// large will slower.
	private String info, dbginfo, info_show;
	private Cursor cur, cur_contacts;
	private Uri uri;
	private List<String> arraylist_sms = new ArrayList<String>();
	private ArrayList<Boolean> checkedItem = new ArrayList<Boolean>();
	private ArrayAdapter<String> arrayadapter_sms;
	private ListView list;
	private TextView footview;
	private ArrayList<Map<String, Object>> sms_array1 = new ArrayList<Map<String, Object>>();
	private int iTotal, iSelected, iCount;
	static final int MENU_DELETE_SELECTED = Menu.FIRST;
	static final int MENU_ABOUT = Menu.FIRST + 1;
	static final int MENU_QUIT = Menu.FIRST + 2;
	private int m_count = 0;
	private ProgressDialog progressDialog;
	private Handler handler = null;
	private Thread thread_sms, thread_getsmsinfo;
	private Toast toast, toast2;
	private MyAdapter smslistadapter;
	private boolean delete_running = false, showwaiting_running = false;

	protected static final int GUI_UPDATE_SMS_LIST = 0x108;
	protected static final int GUI_SHOW_WAITING = 0x109;
	protected static final int GUI_GET_SMSINFO = 0x10A;

	// private ListView list;

	/** Called when the activity is first created. */
	@Override
	public void onCreate(Bundle savedInstanceState)
	{
		super.onCreate(savedInstanceState);
		setContentView(R.layout.main);

		initResourceRefs();

		initHandles();

		// select
		Log.i(TAG, "start !");

		// ////////////
		handler.sendEmptyMessage(GUI_SHOW_WAITING);
		Log.i(TAG, "show waiting !");
	}

	/*
	 * Whenever the UI is re-created (due f.ex. to orientation change) we have
	 * to reinitialize references to the views.
	 */
	private void initResourceRefs()
	{
		smslistadapter = new MyAdapter(this);

		list = (ListView) findViewById(R.id.listView1);
		list.setBackgroundColor(Color.WHITE);// (0xff02003f);
		// Tommy: add to make color won't be changed when scroll.
		list.setCacheColorHint(Color.TRANSPARENT);

		// head/foot view, display 222/333 selected.
		footview = new TextView(this);
		footview.setTextColor(Color.RED);
		footview.setTypeface(null, Typeface.BOLD);
		footview.setGravity(Gravity.CENTER_HORIZONTAL);
		list.addHeaderView(footview);
		
		toast = Toast.makeText(getApplicationContext(), ".", Toast.LENGTH_LONG);
		toast.setGravity(Gravity.CENTER, 0, 0);
		toast2 = Toast.makeText(getApplicationContext(), ".", Toast.LENGTH_SHORT);
		toast2.setGravity(Gravity.BOTTOM, 0, 0);
		
	}

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
					case GUI_SHOW_WAITING:
						show_wait();
						break;

					case GUI_GET_SMSINFO:
						thread_getsmsinfo = new Thread()
						{
							@Override
							public void run()
							{
								get_smsinfo(MAX_SMS_BROWSE);
								handler.sendEmptyMessage(GUI_UPDATE_SMS_LIST);
								showwaiting_running = false;
								Log.i(TAG, "thread_getsmsinfo done !");
							}
						};
						thread_getsmsinfo.start();
						Log.i(TAG, "thread_getsmsinfo start !");
						break;

					case GUI_UPDATE_SMS_LIST:
						update_showlist();
						break;

				}
				super.handleMessage(msg);
			}
		};
	}

	private void list_update_headview()
	{
		// footview.setText("Total " + iTotal + ", " + "Selected " + iSelected);
		footview.setText(" " + getString(R.string.sms) + " " + iSelected + "/" + iTotal + " " + getString(R.string.selected) + ". ");
	}

	/*
	 * private void thread_show_sms() { new Thread() {
	 * 
	 * @Override public void run() { try { get_smsinfo(MAX_SMS_BROWSE);
	 * Thread.sleep(1); } catch (InterruptedException e) { e.printStackTrace();
	 * } finally { } }
	 * 
	 * }.start(); }
	 */

	// 显示 '请等待...'
	private void show_wait()
	{
		final ProgressDialog pd;

		pd = new ProgressDialog(this);
		pd.setProgressStyle(ProgressDialog.STYLE_HORIZONTAL);
		pd.setTitle(getString(R.string.app_name));
		pd.setMessage(getString(R.string.load));
		pd.setMax(0);
		pd.setCancelable(false);
//		pd.setCancelable(true);

		pd.show();
		
		if (debugmode)
		{
			toast.setText("Debug mode !");
			toast.show();
		}
		/*
		 * m_count = 0; while (m_count <= iSelected) { m_count++; //
		 * progressDialog.setProgress(m_count);
		 * progressDialog.incrementProgressBy(1); SystemClock.sleep(100); }
		 * SystemClock.sleep(1000);
		 */
		{
			new Thread()
			{
				@Override
				public void run()
				{
					int bGetCount = 0;
					try
					{
						iTotal = 0;
						iCount = 0;
						
						showwaiting_running = true;
						handler.sendEmptyMessage(GUI_GET_SMSINFO);

						// for (int j = 0; j < 150; j++)
						while (showwaiting_running)
						{
							// pd.incrementProgressBy(1);
							if (bGetCount == 0 && iCount != 0 )
							{
								pd.setMax(iCount);
								bGetCount = 1;
							}
							if (bGetCount == 1)
								pd.setProgress(iTotal);
							Thread.sleep(500);
							// if (j == 50)
							// handler.sendEmptyMessage(GUI_UPDATE_SMS_LIST);
						}
						pd.setProgress(pd.getMax());
						Thread.sleep(100);
						pd.cancel();
						Thread.sleep(1);
					} catch (InterruptedException e)
					{
						e.printStackTrace();
					} finally
					{
					}
				}

			}.start();
		}

	}

	private boolean isInteger( String input )  
	{  
	   try  
	   {  
	      Integer.parseInt( input );  
	      return true;  
	   }  
	   catch( Exception e)  
	   {  
	      return false;  
	   }  
	} 
	
	// Browser all the SMS
	private void get_smsinfo(int num)
	{
		int i;
		int index;
		int contactIdIndex = 0;
		boolean bStranger;

		if (num == 0)
			num = 99999;

		i = 1;
		// arrayadapter_sms.clear();
		arraylist_sms.clear();
		checkedItem.clear();
		sms_array1.clear();

		uri = Uri.parse("content://sms/inbox");
		cur = getContentResolver().query(uri, new String[] { "_id", "thread_id", "address", /*"person",*/ "body" }, null, null, null);
//		cur = getContentResolver().query(uri, null, null, null, null);
		contactIdIndex = cur.getColumnIndex("address");

		iSelected = 0;
		iTotal = 0;
		iCount = 0;
		if (cur.getCount() == 0)
		{
			Log.i(TAG, "No sms found !");
		} else
		{
			Log.i(TAG, "Total " + cur.getCount() + " sms !!!");
			// arraylist_sms.add("Total " + cur.getCount() + " sms !!!");
			iCount = cur.getCount();
			
			if (cur.moveToFirst())
			{
				do
				{
					Map<String, Object> map = new HashMap<String, Object>();
					bStranger = false;

//					info = "Sms " + String.valueOf(i) + ": ";

					{
						String addr = cur.getString(contactIdIndex);
						Uri myPerson = Uri.withAppendedPath(ContactsContract.CommonDataKinds.Phone.CONTENT_FILTER_URI,
			                        Uri.encode(addr));
			            String[] projection = new String[] { ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME };
			            Cursor cursor = getContentResolver().query(myPerson,
			                        projection, null, null, null);								
			            if (cursor.moveToFirst())
			            {	
			            	bStranger = false;
			            	continue;
			            }
			            else
			            {
			            	bStranger = true;
			            }
					}
					
					if (bStranger == false)
						continue;
					
					for (int j = 0; j < cur.getColumnCount(); j++)
					{
//						Log.i(TAG, "    Column:"+j+ "name:" + cur.getColumnName(j) + ", string:" + cur.getString(j));
						if (cur.getColumnName(j).equals("body"))
						{
//							Log.i(TAG, "Msg is " + cur.getString(j));
//							info_show += cur.getString(j);
							map.put("BODY", cur.getString(j));
						} else if (cur.getColumnName(j).equals("address"))
						{
//							Log.i(TAG, "NO." + i + " From: " + cur.getString(j));
//							info_show += "From:" + cur.getString(j) + "\n";
							map.put("ADDR", cur.getString(j));
							
							{
								String addr = cur.getString(j);
								Uri myPerson = Uri.withAppendedPath(ContactsContract.CommonDataKinds.Phone.CONTENT_FILTER_URI,
					                        Uri.encode(addr));
					            String[] projection = new String[] { ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME };
					            Cursor cursor = getContentResolver().query(myPerson,
					                        projection, null, null, null);								
					            if (cursor.moveToFirst())
					            {	// Person in contacts list !
					            	String name=cursor.getString(cursor.getColumnIndex(ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME));
					            	Log.i(TAG, name);
									checkedItem.add(false);
//									map.put("CHECKED", false);
//									map.put("NAME", name);
					            }
					            else
					            {	// Stranger !!!
									map.put("CHECKED", true);
									if (true) // when test, set to false
									{
										checkedItem.add(true);
										iSelected++;
									} else
									{
										checkedItem.add(false);
									}
					            }
					            cursor.close();
							}
							
						}else if (cur.getColumnName(j).equals("_id"))
						{
							map.put("ID", cur.getString(j));
						} else if (cur.getColumnName(j).equals("thread_id"))
						{
							map.put("THREAD_ID", cur.getString(j));
						} 
					}
					// Log.i(TAG, info);
					// arraylist_sms.add(info_show);
					sms_array1.add(map);
					iTotal++;

					if (debugmode)
						SystemClock.sleep(10);

					// String id =
					// cur.getString(cur.getColumnIndex(People._ID));
					// String name =
					// cur.getString(cur.getColumnIndex(People.DISPLAY_NAME));
					// String number =
					// cur.getString(cur.getColumnIndex(People.NUMBER));
					// Log.i(TAG, id + "  " + name + " " + number);

				} while (cur.moveToNext() && (i++ < num));
			}
		}
		cur.close();
		
		Log.i(TAG, "done1");

	}

	private void update_showlist()
	{
		list_update_headview();

		{ // if extends ListActivity, Tommy: this mode, can't change textsize.
			// arrayadapter_sms = new ArrayAdapter<String>(this,
			// android.R.layout.simple_list_item_multiple_choice,
			// arraylist_sms);
			// setListAdapter(arrayadapter_sms);
			// final ListView listView = getListView();
			// listView.setChoiceMode(ListView.CHOICE_MODE_MULTIPLE);
		}

		{ // Use customer listview
			// arrayadapter_sms = new ArrayAdapter<String>(this,
			// R.layout.smslist_layout, arraylist_sms);
			// list.setAdapter(arrayadapter_sms);
		}

		// Use SimpleAdapter
		{
			// SimpleAdapter smslistadapter = new SimpleAdapter(this,
			// sms_array1,
			// R.layout.smslist_map, new String[] { "ADDR", "BODY" },
			// new int[] { R.id.sms_address, R.id.sms_body });
			//
			// list.setAdapter(smslistadapter);
		}

		// Use My Adapter
		{
			list.setAdapter(smslistadapter);
		}

		// Display SMS list statistics.
		toast.setText(getString(R.string.stranger) + " " + getString(R.string.sms) + " " + iSelected + " ."
				+ "\n" 
				+ getString(R.string.total) + " " + getString(R.string.sms) + " " + iTotal + " ."
				);
		toast.show();

		// listView.setItemsCanFocus(false);

		// listView.setItemChecked(1, true);

	} // get_smsinfo

	// Delete SMS
	private void delete_sms_selected()
	{
		progressDialog = new ProgressDialog(this);
		progressDialog.setProgressStyle(ProgressDialog.STYLE_HORIZONTAL);
		progressDialog.setTitle(getString(R.string.processbar_deleting_title));
		// progressDialog.setMessage(getString(R.string.processbar_deleting_msg));
		progressDialog.setMax(iSelected);
		progressDialog.setProgress(0);
		progressDialog.setIndeterminate(false);
		progressDialog.setCancelable(true);
		progressDialog.setButton(DialogInterface.BUTTON_NEGATIVE, getString(android.R.string.cancel), new DialogInterface.OnClickListener()
		{
			@Override
			public void onClick(DialogInterface dialog, int which)
			{
				// dialog.cancel();
				// If running, stop it.
				if (delete_running)
					delete_running = false;
			}
		});

		// SystemClock.sleep(100);

		/*
		 * m_count = 0; while (m_count <= iSelected) { m_count++; //
		 * progressDialog.setProgress(m_count);
		 * progressDialog.incrementProgressBy(1); SystemClock.sleep(100); }
		 * SystemClock.sleep(1000);
		 */
		if (iTotal > 0 && iSelected > 0)
		{
			progressDialog.show();

			thread_sms = new Thread()
			{
				Boolean bDel;

				@Override
				public void run()

				{
					try
					{
						m_count = 0;
						ContentResolver resolver = SmsClean.this.getContentResolver();
						delete_running = true;
						for (int i = 0; i < iTotal && delete_running; i++)
						{
							bDel = (Boolean) checkedItem.get(i);
							if (bDel)
							{
								m_count++;
								if (!debugmode)
								{ // Deleting SMS
									resolver.delete(Uri.parse("content://sms/conversations/" + sms_array1.get(i).get("THREAD_ID")), "_id = " + sms_array1.get(i).get("ID"), null);
									// Log.i(TAG, "deleting " + "_id = " +
									// sms_array1.get(i).get("ID"));
								} else
								{ // Simulate
									Thread.sleep(100);
									Log.i(TAG, "deleting " + i);
								}
								progressDialog.incrementProgressBy(1);
							}
						}

						delete_running = false;
						progressDialog.cancel();
						handler.sendEmptyMessage(GUI_SHOW_WAITING);
						Thread.sleep(1);

					} catch (InterruptedException e)
					{
						e.printStackTrace();
					} finally
					{
						// get_smsinfo(MAX_SMS_BROWSE);
					}
				}

			};
			thread_sms.start();
		}

		progressDialog.setOnCancelListener(new ProgressDialog.OnCancelListener()
		{

			@Override
			public void onCancel(DialogInterface dialog)
			{
				thread_sms.interrupt();
			}
		});

	}

	// Delete SMS
	private void show_about()
	{
		AlertDialog.Builder aboutBox;
		String pkName = this.getPackageName();

		// this.getPackageManager().getPackageInfo返回包的一些overall信息
		String versionName = null;
		try
		{
			versionName = this.getPackageManager().getPackageInfo(pkName, 0).versionName;
		} catch (NameNotFoundException e)
		{
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		LinearLayout aboutLayout = new LinearLayout(this);
		aboutLayout.setOrientation(LinearLayout.VERTICAL);
		// TextView aboutText = new TextView(this);
		TextView emailLink = new TextView(this);
		ImageView iv = new ImageView(this);

		// aboutText.setText(getString(R.string.app_name) );
		emailLink.setAutoLinkMask(Linkify.ALL);
		emailLink.setText(getString(R.string.feedback));
		emailLink.setGravity(Gravity.CENTER_HORIZONTAL);
		iv.setImageResource(R.drawable.tanmo);
		aboutBox = new AlertDialog.Builder(SmsClean.this);

		// aboutLayout.addView(aboutText);
		aboutLayout.addView(iv);
		aboutLayout.addView(emailLink);

		aboutBox.setView(aboutLayout);

		aboutBox.setTitle(getString(R.string.app_name) + " " + versionName);
		// aboutBox.setMessage(getString(R.string.delete_sms_confirm));
		if (debugmode)
			aboutBox.setMessage("DEBUG");

		aboutBox.setPositiveButton(getString(android.R.string.ok), new DialogInterface.OnClickListener()
		{
			public void onClick(DialogInterface dialog, int which)
			{
			}
		});

		aboutBox.show();
	}

	// START of MyAdapter
	public final class ViewHolder
	{
		public TextView addr;
		public TextView body;
		public CheckBox checked;
	}

	// ///////////////////////////////
	public class MyAdapter extends BaseAdapter
	{
		private LayoutInflater mInflater;

		public MyAdapter(Context context)
		{
			this.mInflater = LayoutInflater.from(context);
		}

		@Override
		public int getCount()
		{
			return sms_array1.size();
		}

		@Override
		public Object getItem(int arg0)
		{
			return null;
		}

		@Override
		public long getItemId(int position)
		{
			return position;
		}

		@Override
		public View getView(int position, View convertView, ViewGroup parent)
		{
			final int p = position; // Must be final.
			ViewHolder holder = null;

			// Log.i(TAG, "MyAdapter getView " + position);
			// Tommy: always create holder. scroll slower, but correct. I think,
			// the faster way is optimized with speed, and not good for
			// CheckBox.
			if (true)// (convertView == null)
			{
				holder = new ViewHolder();
				convertView = mInflater.inflate(R.layout.smslist_map, null);
				holder.addr = (TextView) convertView.findViewById(R.id.sms_address);
				holder.body = (TextView) convertView.findViewById(R.id.sms_body);
				holder.checked = (CheckBox) convertView.findViewById(R.id.checkBox_delete);
				convertView.setTag(holder);
			} else
			{ // 得到缓存的
				holder = (ViewHolder) convertView.getTag();
			}

			if ((String) sms_array1.get(position).get("NAME") == null)
			{
				holder.addr.setText(/* getString(R.string.from) + ": " + */(String) sms_array1.get(position).get("ADDR"));
			} else
			{
				holder.addr.setText(/* getString(R.string.from) + ": " + */(String) sms_array1.get(position).get("NAME") + " (" + (String) sms_array1.get(position).get("ADDR")
						+ ")");
			}
			holder.addr.setTextColor(Color.BLACK);
			holder.body.setText((String) sms_array1.get(position).get("BODY"));
			// holder.checked.setChecked((Boolean) sms_array1.get(position).get(
			// "CHECKED"));
			// holder.checked.setChecked(false);
			holder.checked.setChecked(checkedItem.get(position));
			holder.checked.setOnCheckedChangeListener(new CheckBox.OnCheckedChangeListener()
			{
				@Override
				public void onCheckedChanged(CompoundButton buttonView, boolean isChecked)
				{
					// sms_array1.get(p);
					// Toast.makeText(getApplicationContext(),
					// "Pos " + p + " will be deleted !!!",
					// Toast.LENGTH_LONG)
					// .show();
					if (isChecked)
					{
						checkedItem.set(p, true);
						iSelected++;
					} else
					{
						checkedItem.set(p, false);
						iSelected--;
					}
					list_update_headview();
					// Display SMS list statistics.
					toast2.setText(
							getString(R.string.stranger) + " " + getString(R.string.sms) + " " + iSelected + " ."
							+ "\n" 
							+ getString(R.string.total) + " " + getString(R.string.sms) + " " + iTotal + " ." 
							);
					
					toast2.setGravity(Gravity.BOTTOM, 0, 0);
					toast2.show();					
				}
			});

			return convertView;
		}
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu)
	{
		int idGroup1 = 0;

		/* The order position of the item */
		// int orderItem1 = Menu.NONE;
		// int orderItem3 = Menu.NONE + 2;

		menu.add(Menu.NONE, MENU_DELETE_SELECTED, Menu.NONE, getString(R.string.delete_seleted)).setIcon(android.R.drawable.ic_delete);
		int MENU_DRAW;
		menu.add(Menu.NONE, MENU_ABOUT, Menu.NONE, getString(R.string.about)).setIcon(android.R.drawable.ic_menu_info_details);
		menu.add(Menu.NONE, MENU_QUIT, Menu.NONE, getString(R.string.quit)).setIcon(android.R.drawable.ic_menu_close_clear_cancel);
		return super.onCreateOptionsMenu(menu);
	}

	@Override
	public boolean onMenuItemSelected(int featureId, MenuItem item)
	{
		switch (item.getItemId())
		{
			case (MENU_DELETE_SELECTED):
				if (iTotal > 0 && iSelected > 0)
				{
				} else
				{ // if no sms, exit
					break;
				}

				new AlertDialog.Builder(SmsClean.this).setTitle(android.R.string.dialog_alert_title).setMessage(getString(R.string.delete_sms_confirm)).setPositiveButton(
						getString(android.R.string.ok), new DialogInterface.OnClickListener()
						{
							public void onClick(DialogInterface dialog, int which)
							{
								delete_sms_selected();
							}
						}).setNegativeButton(getString(android.R.string.cancel), new DialogInterface.OnClickListener()
				{
					public void onClick(DialogInterface dialog, int which)
					{
					}
				}).show();

				break;

			case (MENU_ABOUT):
				show_about();
				break;

			case (MENU_QUIT):
				finish();
				break;
		}
		return super.onMenuItemSelected(featureId, item);
	}

}

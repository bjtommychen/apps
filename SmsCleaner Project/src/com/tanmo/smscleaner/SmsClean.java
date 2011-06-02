package com.tanmo.smscleaner;

import android.app.Activity;
import android.os.Bundle;

import android.util.DisplayMetrics;
import android.util.Log;
import android.net.Uri;
import android.database.Cursor;
import android.graphics.Color;
import android.graphics.Typeface;

import java.util.*;

import android.os.Bundle;
import android.widget.*;
import android.view.*;
import android.content.Context;

public class SmsClean extends Activity
{
	private String TAG = "smsclean";
	private String info, dbginfo, info_show;
	private Cursor cur;
	private Uri uri;
	private List<String> arraylist_sms = new ArrayList<String>();
	private ArrayAdapter<String> arrayadapter_sms;
	private ListView list;
	private TextView footview;
	private ArrayList<Map<String, Object>> sms_array1 = new ArrayList<Map<String, Object>>();
	private int iTotal, iSelected;

	// private ListView list;

	/** Called when the activity is first created. */
	@Override
	public void onCreate(Bundle savedInstanceState)
	{
		super.onCreate(savedInstanceState);
		setContentView(R.layout.main);

		list = (ListView) findViewById(R.id.listView1);
		list.setBackgroundColor(Color.BLUE);
		list.setCacheColorHint(Color.BLUE);// Tommy: won't change color when
		// select
		Log.i(TAG, "start !");

		// Show list
		browse_sms(25);

		Log.i(TAG, "stop !");
	}

	// Browser all the SMS
	private void browse_sms(int num)
	{
		int i;

		if (num == 0)
			num = 99999;

		// String[] sw = new String[100];
		// for (i = 0; i < 100; i++)
		// {
		// sw[i] = "listtest_" + i;
		// }

		// for (i = 0; i < 10; i++)
		// {
		// HashMap<String, Object> map = new HashMap<String, Object>();
		// map.put("ADDR", "Test Title");
		// map.put("BODY", "listtest_" + i);
		// sms_array1.add(map);
		// }

		i = 1;
		arraylist_sms.clear();

		uri = Uri.parse("content://sms/inbox");
		// cur = this.managedQuery(uri, null, null, null, null);
		cur = getContentResolver().query(uri, null, null, null, null);
		
		iSelected = 0;
		if (cur.getCount() == 0)
		{
			Log.i(TAG, "No sms found !");
		} else
		{
			Log.i(TAG, "Total " + cur.getCount() + " sms !!!");
			// arraylist_sms.add("Total " + cur.getCount() + " sms !!!");
			
			footview = new TextView(this);
//			footview.setText("Total " + cur.getCount() + " !");
			footview.setTextColor(Color.RED);
			footview.setTypeface(null, Typeface.BOLD);
//			list.addFooterView(footview);
			list.addHeaderView(footview);

			iSelected = 0;
			iTotal = 0;
			if (cur.moveToFirst())
			{
				do
				{
					Map<String, Object> map = new HashMap<String, Object>();

					info = "Sms " + String.valueOf(i) + ": ";
					info_show = "";
					for (int j = 0; j < cur.getColumnCount(); j++)
					{
						if (cur.getColumnName(j).equals("body"))
						{
							Log.i(TAG, "Msg is " + cur.getString(j));
							info_show += cur.getString(j);
							map.put("BODY", cur.getString(j));
						} else if (cur.getColumnName(j).equals("address"))
						{
							Log.i(TAG, "From " + cur.getString(j));
							info_show += "From:" + cur.getString(j) + "\n";
							map.put("ADDR", cur.getString(j));
						} else if (cur.getColumnName(j).equals("person"))
						{
							if (cur.getString(j) == null)
							{
								map.put("CHECKED", true);
								iSelected++;
							}
							else
								map.put("CHECKED", false);
						} else
						{
							info += cur.getColumnName(j) + "="
									+ cur.getString(j) + ";";
						}

					}
					Log.i(TAG, info);
					arraylist_sms.add(info_show);
					sms_array1.add(map);
					iTotal++;
					
				} while (cur.moveToNext() && (i++ < num));
			}
		}

		footview.setText("Total " + iTotal + ", " + "Selected " + iSelected);
		
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
			MyAdapter smslistadapter = new MyAdapter(this);

			list.setAdapter(smslistadapter);
		}

		Toast.makeText(getApplicationContext(),
				"Total " + cur.getCount() + " sms !!!", Toast.LENGTH_LONG)
				.show();

		// listView.setItemsCanFocus(false);

		// listView.setItemChecked(1, true);

	} // browse_sms

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
			// TODO Auto-generated method stub
			return sms_array1.size();
		}

		@Override
		public Object getItem(int arg0)
		{
			// TODO Auto-generated method stub
			return null;
		}

		@Override
		public long getItemId(int position)
		{
			// TODO Auto-generated method stub
			return position;
		}

		@Override
		public View getView(int position, View convertView, ViewGroup parent)
		{
			final int p = position;	// Must be final.
			ViewHolder holder = null;

			// Log.i(TAG, "MyAdapter getView " + position);
			if (convertView == null)
			{
				holder = new ViewHolder();
				convertView = mInflater.inflate(R.layout.smslist_map, null);
				holder.addr = (TextView) convertView
						.findViewById(R.id.sms_address);
				holder.body = (TextView) convertView
						.findViewById(R.id.sms_body);
				holder.checked = (CheckBox) convertView
						.findViewById(R.id.checkBox_delete);
				convertView.setTag(holder);
			} else
			{
				holder = (ViewHolder) convertView.getTag();
			}

			holder.addr.setText("From:"
					+ (String) sms_array1.get(position).get("ADDR"));
			holder.body.setText((String) sms_array1.get(position).get("BODY"));
			holder.checked.setChecked((Boolean) sms_array1.get(position).get(
					"CHECKED"));
			holder.checked
					.setOnCheckedChangeListener(new CheckBox.OnCheckedChangeListener()
					{
						@Override
						public void onCheckedChanged(CompoundButton buttonView,
								boolean isChecked)
						{
							// sms_array1.get(p);
							// Toast.makeText(getApplicationContext(),
							// "Pos " + p + " will be deleted !!!",
							// Toast.LENGTH_LONG)
							// .show();
							if (isChecked)
							{
								iSelected++;
							}
							else
							{
								iSelected--;
							}
							footview.setText("Total " + iTotal + ", " + "Selected " + iSelected);
						
						}
					});

			return convertView;
		}
	}
}

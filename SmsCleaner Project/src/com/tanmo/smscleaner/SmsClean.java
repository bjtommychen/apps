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
	ArrayList<HashMap<String, Object>> sms_array1 = new ArrayList<HashMap<String, Object>>();

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
		browse_sms(20);

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
		if (cur.getCount() == 0)
		{
			Log.i(TAG, "No sms found !");
		} else
		{
			Log.i(TAG, "Total " + cur.getCount() + " sms !!!");
			// arraylist_sms.add("Total " + cur.getCount() + " sms !!!");

			footview = new TextView(this);
			footview.setText("Total " + cur.getCount() + " sms !!!");
			footview.setTextColor(Color.RED);
			footview.setTypeface(null, Typeface.BOLD);
			list.addFooterView(footview);
			list.addHeaderView(footview);

			if (cur.moveToFirst())
			{
				do
				{
					HashMap<String, Object> map = new HashMap<String, Object>();
					
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
							map.put("ADDR","From:" + cur.getString(j));
						} else
						{
							info += cur.getColumnName(j) + "="
									+ cur.getString(j) + ";";
						}
					}
					Log.i(TAG, info);
					arraylist_sms.add(info_show);
					sms_array1.add(map);
				} while (cur.moveToNext() && (i++ < num));
			}
		}

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
			SimpleAdapter smslistadapter = new SimpleAdapter(this, sms_array1,
					R.layout.smslist_map, new String[] { "ADDR", "BODY" },
					new int[] { R.id.sms_address, R.id.sms_body });

			list.setAdapter(smslistadapter);
		}

		Toast.makeText(getApplicationContext(),
				"Total " + cur.getCount() + " sms !!!", Toast.LENGTH_LONG)
				.show();

		// listView.setItemsCanFocus(false);

		// listView.setItemChecked(1, true);

	} // browse_sms

}

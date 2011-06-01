package com.tanmo.smscleaner;

import android.app.Activity;
import android.os.Bundle;

import android.util.DisplayMetrics;
import android.util.Log;
import android.net.Uri;
import android.database.Cursor;
import java.util.Arrays;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import android.app.ListActivity;
import android.os.Bundle;
import android.widget.ArrayAdapter;
import android.widget.ListView;

public class SmsClean extends ListActivity
{
	private String TAG = "smsclean";
	private String info, dbginfo, info_show;
	private Cursor cur;
	private Uri uri;
	private List<String> arraylist_sms = new ArrayList<String>();
	private ArrayAdapter<String> arrayadapter_sms;

	// private ListView list;

	/** Called when the activity is first created. */
	@Override
	public void onCreate(Bundle savedInstanceState)
	{
		super.onCreate(savedInstanceState);
		setContentView(R.layout.main);

		// list=(ListView)findViewById(R.id.listView1);
		Log.i(TAG, "start !");

		browse_sms(20);

		Log.i(TAG, "stop !");
	}

	// Browser all the SMS
	private void browse_sms(int num)
	{
		int i;

		if (num == 0)
			num = 99999;

//		String[] sw = new String[100];
//		for (i = 0; i < 100; i++)
//		{
//			sw[i] = "listtest_" + i;
//		}
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
			arraylist_sms.add("Total " + cur.getCount() + " sms !!!");

			if (cur.moveToFirst())
			{
				do
				{
					info = "Sms " + String.valueOf(i) + ": ";
					info_show = "";
					for (int j = 0; j < cur.getColumnCount(); j++)
					{

						if (cur.getColumnName(j).equals("body"))
						{
							Log.i(TAG, "Msg is " + cur.getString(j));
							info_show += cur.getString(j);
						} else if (cur.getColumnName(j).equals("address"))
						{
							Log.i(TAG, "From " + cur.getString(j));
							info_show += "From:" + cur.getString(j) + "\n";
						} else
						{
							info += cur.getColumnName(j) + "="
									+ cur.getString(j) + ";";
						}
					}
					Log.i(TAG, info);
					arraylist_sms.add(info_show);
				} while (cur.moveToNext() && (i++ < num));
			}
		}

		// if extends ListActivity, Tommy: this mode, can't change textsize.
		if (true)
		{
			arrayadapter_sms = new ArrayAdapter<String>(this,
					android.R.layout.simple_list_item_multiple_choice,
					arraylist_sms);
			setListAdapter(arrayadapter_sms);
			final ListView listView = getListView();
			listView.setChoiceMode(ListView.CHOICE_MODE_MULTIPLE);
		}
		
		
		// arrayadapter_sms = new ArrayAdapter<String>(this,
		// R.layout.smslist_layout, sw);

		// listView.setItemsCanFocus(false);

		// listView.setItemChecked(1, true);

	} // browse_sms

}

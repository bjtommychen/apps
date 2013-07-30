try:
    import win32api,win32gui,win32con
    from ctypes import * 
except:
    win32gui=None   

import time

def winEnumHandler( hwnd, ctx ):
    if win32gui.IsWindow( hwnd ) and win32gui.IsWindowVisible( hwnd ) and win32gui.IsWindowEnabled( hwnd ):
        print 'HEX', hex(hwnd), 'Text:', win32gui.GetWindowText( hwnd )
        if 'Administrator' in win32gui.GetWindowText( hwnd ):
            print 'try to setfore'
#            win32gui.SetActiveWindow(hwnd)
#            win32gui.BringWindowToTop(hwnd)
#            win32gui.SetFocus(hwnd)
#            win32gui.SetForegroundWindow(hwnd)
#            win32gui.ShowWindow(hwnd,win32con.SW_SHOWDEFAULT)

            
#            win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_F1, 0)
#            win32api.PostMess2age(hwnd, win32con.WM_KEYUP, win32con.VK_F1, 0)
#            win32api.PostMessage(hwnd, win32con.WM_SETTEXT, None, 'win32con.VK_F1')
#            win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_TAB, 0)
#            win32api.keybd_event(86,0,0,0)221
#            win32api.keybd_event(86,0,win32con.KEYEVENTF_KEYUP,0)
#            SendMessage(hwnd, 258, ord('a'), 0)
#            win32api.keybd_event(112,0,0,0)2
#            win32api.keybd_event(112,0,win32con.KEYEVENTF_KEYUP,0)
#            win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
#            time.sleep(1)
#            win32api.SendMessage(hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
#            win32api.keybd_event(127,0,0,0)
#            win32api.keybd_event(86,0,0,0)  
#            win32api.keybd_event(86,0,win32con.KEYEVENTF_KEYUP,0) 
#            win32api.keybd_event(17,0,win32con.KEYEVE2NTF_KEYUP,0)
            win32api.keybd_event(50,0,0,0)  
#            win32api.keybd_event(50,0,win32con.KEYEVENTF_KEYUP,0)
#            win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_TAB, 0)
#        time.sleep(1)

if True:
    win32gui.EnumWindows( winEnumHandler, None )
    time.sleep(2)
    print 'Final'
    print win32gui.GetWindowText(win32gui.GetForegroundWindow())
#    hwnd = win32gui.GetForegroundWindow()
    win32api.keybd_event(50,0,0,0)  
    win32api.keybd_event(50,0,win32con.KEYEVENTF_KEYUP,0)
    win32api.keybd_event(ord('a'), 0, 0, 0) 
    win32api.keybd_event(ord('a'), 0, 0, 0) 
    win32api.keybd_event(ord('a'), 0, 0, 0) 
    win32api.keybd_event(ord('a'), 0, 0, 0) 
    win32api.keybd_event(ord('a'), 0, 0, 0) 
    win32api.keybd_event(ord('a'), 0, 0, 0) 
    win32api.keybd_event(ord('a'), 0, 0, 0) 

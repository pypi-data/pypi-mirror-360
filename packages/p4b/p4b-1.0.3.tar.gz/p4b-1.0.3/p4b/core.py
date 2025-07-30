import os #line:1
import json #line:2
import time #line:3
import base64 #line:4
import random #line:5
import logging #line:6
import keyboard #line:7
import argparse #line:8
import pyperclip #line:9
import pyautogui as pg #line:10
import subprocess as sb #line:11
import google .generativeai as genai #line:12
from PIL import Image #line:14
from io import BytesIO #line:15
from openai import OpenAI #line:16
from rich .text import Text #line:17
from rich .panel import Panel #line:18
from rich .align import Align #line:19
from rich .console import Console #line:20
from setproctitle import setproctitle #line:21
BANNER ="""
██████╗ ██╗  ██╗██████╗ 
██╔══██╗██║  ██║██╔══██╗
██████╔╝███████║██████╔╝
██╔═══╝ ╚════██║██╔══██╗
██║          ██║██████╔╝
╚═╝          ╚═╝╚═════╝ 
"""#line:32
SCREEN_HEIGHT ,SCREEN_WIDTH =pg .size ()#line:33
POSITION_MAP ={"s":(SCREEN_HEIGHT /4 ,SCREEN_WIDTH /4 ),"x":(3 *SCREEN_HEIGHT /4 ,SCREEN_WIDTH /4 ),"a":(0 *SCREEN_HEIGHT /4 ,3 *SCREEN_WIDTH /4 ),"b":(1 *SCREEN_HEIGHT /4 ,3 *SCREEN_WIDTH /4 ),"c":(2 *SCREEN_HEIGHT /4 ,3 *SCREEN_WIDTH /4 ),"d":(3 *SCREEN_HEIGHT /4 ,3 *SCREEN_WIDTH /4 ),"e":(4 *SCREEN_HEIGHT /4 ,3 *SCREEN_WIDTH /4 )}#line:43
LLM_INSTRUCTION =base64.b64decode("IkdpdmVuIGFuIGltYWdlLCBkZXRlcm1pbmUgdGhlIHR5cGUgb2YgcXVlc3Rpb24gaXQgY29udGFpbnMuIElmIGl0J3MgYSBjb2RpbmcgcHJvYmxlbSwgc29sdmUgaXQgaW4gdGhlIGxhbmd1YWdlIHNob3duIGluIHRoZSBpbWFnZS4gSWYgaXQncyBhbiBNQ1EsIHJldHVybiBvbmx5IHRoZSBjb3JyZWN0IG9wdGlvbiBhcyBhIHNpbmdsZSBhbHBoYWJldCBjaGFyYWN0ZXIgKGUuZy4sIGEsIGIsIGMsIGQsIGUpLiBJZiBpdCdzIGEgZ2VuZXJhbCBxdWVzdGlvbiwgcmV0dXJuIG9ubHkgdGhlIGRpcmVjdCBhbnN3ZXIuIFN0cmljdGx5IGRvIG5vdCBpbmNsdWRlIGFueSBleHBsYW5hdGlvbnMsIGNvbW1lbnRzLCBvciBleHRyYSB0ZXh0LiI=".encode("ascii")).decode("ascii")#line:44
RAINBOW_COLORS =["dark_cyan","light_sea_green","deep_sky_blue2","deep_sky_blue1","green3","spring_green3","cyan3","dark_turquoise","turquoise2"]#line:55
GEMINI_API_KEY =""#line:57
GITHUB_TOKEN =""#line:58
logging .basicConfig (level =logging .INFO ,format ='%(asctime)s - %(name)s - %(levelname)s - %(message)s',handlers =[logging .FileHandler ("p4b.log"),logging .StreamHandler ()])#line:67
logger =logging .getLogger ("p4b")#line:68
console =Console ()#line:69
exit_requested =False #line:70
config_path =os .path .join (os .path .dirname (__file__ ),'config.json')#line:71
setproctitle ("p4b - A vertical within Bruhmastra")#line:73
def show_welcome ():#line:76
    os .system ('cls'if os .name =='nt'else 'clear')#line:77
    O0OOOOOOOO0O00OO0 =Text ()#line:79
    for O0OOO0OOO0OO0O000 in BANNER .strip ("\n").splitlines ():#line:80
        for OOO0OO000O000OO00 in O0OOO0OOO0OO0O000 :#line:81
            O00OO00OO0O0OO0O0 =random .choice (RAINBOW_COLORS )#line:82
            O0OOOOOOOO0O00OO0 .append (OOO0OO000O000OO00 ,style =f"bold {O00OO00OO0O0OO0O0}")#line:83
        O0OOOOOOOO0O00OO0 .append ("\n")#line:84
    O00OO000000O0O0OO =Text ()#line:86
    O00OO000000O0O0OO .append ("Welcome to the P4B Assistant CLI\n",style ="bold magenta")#line:87
    O00OO000000O0O0OO .append ("══════════════════════════════════════════════════\n\n",style ="cyan")#line:88
    O00OO000000O0O0OO .append ("Available Hotkeys:\n",style ="bold yellow")#line:90
    O00OO000000O0O0OO .append ("  ⮞ alt+shift+1",style ="cyan")#line:91
    O00OO000000O0O0OO .append (" → Gemini 2.5 Flash Lite Preview 06-17\n",style ="white")#line:92
    O00OO000000O0O0OO .append ("  ⮞ alt+shift+2",style ="cyan")#line:93
    O00OO000000O0O0OO .append (" → Gemini 2.5 Flash\n",style ="white")#line:94
    O00OO000000O0O0OO .append ("  ⮞ alt+shift+3",style ="cyan")#line:95
    O00OO000000O0O0OO .append (" → Gemini 2.5 Pro\n",style ="white")#line:96
    O00OO000000O0O0OO .append ("  ⮞ alt+shift+4",style ="cyan")#line:97
    O00OO000000O0O0OO .append (" → OpenAI GPT-4.1\n",style ="white")#line:98
    O00OO000000O0O0OO .append ("  ⮞ alt+shift+q",style ="cyan")#line:99
    O00OO000000O0O0OO .append (" → Quit the application\n\n",style ="white")#line:100
    O00OO000000O0O0OO .append ("💡 Make sure to wait for cursor feedback after each hotkey.",style ="italic green")#line:102
    O0OOO000O0O0OO0OO =Text ()#line:104
    O0OOO000O0O0OO0OO .append (O0OOOOOOOO0O00OO0 )#line:105
    O0OOO000O0O0OO0OO .append ("\n")#line:106
    O0OOO000O0O0OO0OO .append (O00OO000000O0O0OO )#line:107
    O0OO000O0OOOOOO0O =Panel (Align .left (O0OOO000O0O0OO0OO ),padding =(1 ,2 ),border_style ="bright_blue",title ="P4B | A vertical within Bruhmastra")#line:109
    console .print (O0OO000O0OOOOOO0O )#line:111
def capture_screenshot ():#line:113
    OOOO0O0O000OO00O0 =pg .screenshot ()#line:114
    O00OOOO0OOO0O0OOO =BytesIO ()#line:115
    OOOO0O0O000OO00O0 .save (O00OOOO0OOO0O0OOO ,format ='PNG')#line:116
    O00OOOO0OOO0O0OOO .seek (0 )#line:117
    return O00OOOO0OOO0O0OOO #line:118
def move_mouse_to_response_position (O00OOOOOOO000OO0O ,launch =False ):#line:120
    if len (O00OOOOOOO000OO0O )==1 and O00OOOOOOO000OO0O in ['a','b','c','d','e','s']:#line:121
        OOOO0OO0O0000O000 =O00OOOOOOO000OO0O .lower ().strip ()#line:122
        pg .moveTo (POSITION_MAP [OOOO0OO0O0000O000 ])#line:123
        if not launch :#line:124
            logger .info (f"Cursor notified with state: '{OOOO0OO0O0000O000}'")#line:125
    else :#line:126
        pg .moveTo (POSITION_MAP ["x"])#line:127
        logger .info ("Cursor notified with state: 'x' (default/fallback).")#line:128
def process_code (model ="gemini",name ="gemini-2.5-flash"):#line:130
    try :#line:131
        logger .info (f"Starting code processing with model: {name}")#line:132
        move_mouse_to_response_position ("s")#line:133
        logger .debug ("Cursor notification set to 's' (start).")#line:134
        O0OO0000OO000O00O =capture_screenshot ()#line:136
        logger .info ("Screenshot captured successfully.")#line:137
        OOOO0O0000O0OO00O =time .time ()#line:139
        O00O00O0O0OO0O0OO =send_to_llm (model =model ,name =name ,img_buffer =O0OO0000OO000O00O ,prompt =LLM_INSTRUCTION ,clean_text =True )#line:140
        if O00O00O0O0OO0O0OO is None :#line:141
            logger .error ("Failed to get a response from the model.")#line:142
            return #line:143
        logger .info ("Response received from {} in {:.2f} seconds.".format (name ,time .time ()-OOOO0O0000O0OO00O ))#line:144
        pyperclip .copy (O00O00O0O0OO0O0OO )#line:146
        logger .debug ("Response copied to clipboard.")#line:147
        move_mouse_to_response_position (O00O00O0O0OO0O0OO )#line:149
    except Exception as OO0O0O0O0O00OOO0O :#line:151
        logger .exception (f"Error processing code screenshot: {str(OO0O0O0O0O00OOO0O)}")#line:152
def silent_start ():#line:154
    try :#line:155
        sb .Popen (["p4b","--no-welcome"],stdout =sb .DEVNULL ,stderr =sb .DEVNULL ,stdin =sb .DEVNULL ,creationflags =sb .CREATE_NEW_PROCESS_GROUP )#line:159
    except Exception as O000O00O0OOOOOOOO :#line:160
        logger .error (f"Failed to start silent process: {O000O00O0OOOOOOOO}")#line:161
def setup_config ():#line:163
    OO00O00OOOOOO00OO =console .input ("[bold cyan][link=https://ai.google.dev/gemini-api/docs/api-key]Gemini API Key[/link]:[/] ")#line:164
    O00OO0OOO0O000O00 =console .input ("[bold cyan][link=https://github.com/settings/tokens]GitHub Token[/link]:[/] ")#line:165
    O0O0OO0O0OOOOOO0O ={"GITHUB_TOKEN":O00OO0OOO0O000O00 .strip (),"GEMINI_API_KEY":OO00O00OOOOOO00OO .strip ()}#line:170
    with open (config_path ,'w')as OOOOO0O00O0OO0OOO :#line:172
        json .dump (O0O0OO0O0OOOOOO0O ,OOOOO0O00O0OO0OOO ,indent =4 )#line:173
    console .print ("[bold green]Configuration file created successfully![/bold green]")#line:175
    return O0O0OO0O0OOOOOO0O ['GEMINI_API_KEY'],O0O0OO0O0OOOOOO0O ['GITHUB_TOKEN']#line:176
def check_config ():#line:178
    if os .path .exists (config_path ):#line:179
        with open (config_path )as O0OOOO0O00O0O00O0 :#line:180
            O00O0OO0O0OO0O0OO =json .load (O0OOOO0O00O0O00O0 )#line:181
            if "GITHUB_TOKEN"in O00O0OO0O0OO0O0OO and "GEMINI_API_KEY"in O00O0OO0O0OO0O0OO :#line:182
                console .print ("[bold green]Configuration file already exists![/bold green]")#line:183
                console .print ("[bold yellow]Current configuration:[/bold yellow]")#line:184
                console .print (f"GITHUB_TOKEN: {O00O0OO0O0OO0O0OO['GITHUB_TOKEN']}")#line:185
                console .print (f"GEMINI_API_KEY: {O00O0OO0O0OO0O0OO['GEMINI_API_KEY']}")#line:186
                return O00O0OO0O0OO0O0OO ['GEMINI_API_KEY'],O00O0OO0O0OO0O0OO ['GITHUB_TOKEN']#line:187
    return setup_config ()#line:189
class Gemini :#line:192
    def __init__ (O0O0O00O00000000O ,model_name ="gemini-2.5-flash"):#line:193
        O0O0O00O00000000O .model_name =model_name #line:194
        genai .configure (api_key =GEMINI_API_KEY )#line:195
        O0O0O00O00000000O .model =genai .GenerativeModel (model_name )#line:196
    def janitor_bhaiyo (O0O000O0OO0OOO0O0 ,OO0O000O00O0O0OOO ):#line:198
        O0OO0000000O00O00 =OO0O000O00O0O0OOO .splitlines ()#line:199
        if O0OO0000000O00O00 and O0OO0000000O00O00 [0 ].startswith ("```"):#line:200
            O0OO0000000O00O00 =O0OO0000000O00O00 [1 :]#line:201
        if O0OO0000000O00O00 and O0OO0000000O00O00 [-1 ].strip ()=="```":#line:202
            O0OO0000000O00O00 =O0OO0000000O00O00 [:-1 ]#line:203
        return "\n".join (O0OO0000000O00O00 ).strip ()#line:205
    def send (OOO00O0O000O0O0O0 ,img_buffer =None ,prompt =None ,clean_text =True ):#line:207
        try :#line:208
            O0OO000O00OO00000 =genai .GenerativeModel (OOO00O0O000O0O0O0 .model_name )#line:209
            if img_buffer is not None :#line:211
                O0OOO0OO0O0OOO0O0 =Image .open (img_buffer )#line:212
                OOOOOOO0O0000OO00 =O0OO000O00OO00000 .generate_content ([prompt ,O0OOO0OO0O0OOO0O0 ])#line:213
            else :#line:214
                OOOOOOO0O0000OO00 =O0OO000O00OO00000 .generate_content (prompt )#line:215
            OOOOOOO0O0000OO00 =OOOOOOO0O0000OO00 .text .strip ()#line:217
            return OOO00O0O000O0O0O0 .janitor_bhaiyo (OOOOOOO0O0000OO00 )if clean_text else OOOOOOO0O0000OO00 #line:218
        except Exception as OO0OO0OOOOO0O00O0 :#line:220
            print (f"Error sending image to Gemini: {str(OO0OO0OOOOO0O00O0)}")#line:221
            return None #line:222
class GPT :#line:224
    ENDPOINT ="https://models.github.ai/inference"#line:225
    def __init__ (O0OOOO0OO0O00OOO0 ,model_name ="openai/gpt-4.1"):#line:227
        O0OOOO0OO0O00OOO0 .model_name =model_name #line:228
        O0OOOO0OO0O00OOO0 .client =OpenAI (base_url =O0OOOO0OO0O00OOO0 .ENDPOINT ,api_key =GITHUB_TOKEN ,)#line:232
    def janitor_bhaiyo (OOO0OO00O0000OO00 ,OOOO0OOOOOO0OOO00 ):#line:234
        O0OOO0OOO00O0O00O =OOOO0OOOOOO0OOO00 .splitlines ()#line:235
        if O0OOO0OOO00O0O00O and O0OOO0OOO00O0O00O [0 ].startswith ("```"):#line:236
            O0OOO0OOO00O0O00O =O0OOO0OOO00O0O00O [1 :]#line:237
        if O0OOO0OOO00O0O00O and O0OOO0OOO00O0O00O [-1 ].strip ()=="```":#line:238
            O0OOO0OOO00O0O00O =O0OOO0OOO00O0O00O [:-1 ]#line:239
        return "\n".join (O0OOO0OOO00O0O00O ).strip ()#line:241
    def send (O0O0OO0000OO000OO ,img_buffer =None ,prompt =None ,clean_text =True ):#line:243
        if img_buffer :#line:244
            OOO0OOOO0O000O0O0 =base64 .b64encode (img_buffer ).decode ('utf-8')#line:245
            O00OO0OO0OOOOOOOO ={"type":"image_url","image_url":{"url":f"data:image/png;base64,{OOO0OOOO0O000O0O0}"}}#line:251
        else :#line:252
            O00OO0OO0OOOOOOOO =None #line:253
        O00O0O0OOOOOOO0OO =OpenAI (base_url =O0O0OO0000OO000OO .ENDPOINT ,api_key =O0O0OO0000OO000OO .TOKEN ,)#line:258
        O0OO0OO0O0OO0000O =[{"role":"system","content":prompt }]if prompt else []#line:260
        O00000O00OO000000 ={"role":"user","content":[]}#line:265
        if O00OO0OO0OOOOOOOO :#line:267
            O00000O00OO000000 ["content"].append (O00OO0OO0OOOOOOOO )#line:268
        O00000O00OO000000 ["content"].append ({"type":"text","text":prompt })#line:269
        O0OO0OO0O0OO0000O .append (O00000O00OO000000 )#line:271
        OOO0OO0O0O00OO0OO =O00O0O0OOOOOOO0OO .chat .completions .create (messages =O0OO0OO0O0OO0000O ,temperature =1.0 ,top_p =1.0 ,model =O0O0OO0000OO000OO .model_name )#line:278
        OO0OOO000000OO0OO =OOO0OO0O0O00OO0OO .choices [0 ].message .content .strip ()#line:280
        return O0O0OO0000OO000OO .janitor_bhaiyo (OO0OOO000000OO0OO )if clean_text else OO0OOO000000OO0OO #line:281
def send_to_llm (model ="gemini",name ="gemini-2.5-pro",img_buffer =None ,prompt =None ,clean_text =True ):#line:283
    if model =="gemini":#line:284
        O0O000000O0OOO00O =Gemini (model_name =name )#line:285
        return O0O000000O0OOO00O .send (img_buffer =img_buffer ,prompt =prompt ,clean_text =clean_text )#line:286
    elif model =="github":#line:288
        OOOOOOOO00OO00O0O =GPT (model_name =name )#line:289
        return OOOOOOOO00OO00O0O .send (img_buffer =img_buffer .getvalue (),prompt =prompt ,clean_text =clean_text )#line:290
def kill ():#line:292
    global exit_requested #line:293
    logger .info ("Exiting p4b gracefully.")#line:294
    os .system ('cls'if os .name =='nt'else 'clear')#line:295
    move_mouse_to_response_position ("c")#line:296
    exit_requested =True #line:297
    exit (0 )#line:298
def parse_arguments ():#line:300
    O0O0O0O00O000OO00 =argparse .ArgumentParser (description ="p4b - A vertical within Bruhmastra")#line:301
    O0O0O0O00O000OO00 .add_argument ("--silent","-s",action ="store_true",help ="Launch application as a background process")#line:302
    O0O0O0O00O000OO00 .add_argument ("--disable-hotkeys",action ="store_true",help ="Disable keyboard hotkeys")#line:303
    O0O0O0O00O000OO00 .add_argument ("--no-welcome",action ="store_true",help ="No welcome message on startup")#line:304
    O0O0O0O00O000OO00 .add_argument ("--reset-config",action ="store_true",help ="Reset configuration file")#line:305
    return O0O0O0O00O000OO00 .parse_args ()#line:306
def main ():#line:309
    O0000O0OOOO00000O =parse_arguments ()#line:310
    global GEMINI_API_KEY ,GITHUB_TOKEN #line:311
    try :#line:312
        if O0000O0OOOO00000O .reset_config :#line:313
            setup_config ()#line:314
            return #line:315
        if O0000O0OOOO00000O .silent :#line:317
            silent_start ()#line:318
            return #line:319
        if not O0000O0OOOO00000O .disable_hotkeys :#line:321
            GEMINI_API_KEY ,GITHUB_TOKEN =check_config ()#line:322
            time .sleep (1 )#line:324
            move_mouse_to_response_position ("c",launch =True )#line:325
            if not O0000O0OOOO00000O .no_welcome :#line:327
                show_welcome ()#line:328
            keyboard .add_hotkey ("alt+shift+1",lambda :process_code (model ="gemini",name ="gemini-2.5-flash-lite-preview-06-17"))#line:330
            keyboard .add_hotkey ("alt+shift+2",lambda :process_code (model ="gemini",name ="gemini-2.5-flash"))#line:331
            keyboard .add_hotkey ("alt+shift+3",lambda :process_code (model ="gemini",name ="gemini-2.5-pro"))#line:332
            keyboard .add_hotkey ("alt+shift+4",lambda :process_code (model ="github",name ="openai/gpt-4.1"))#line:334
            keyboard .add_hotkey ("alt+shift+q",kill )#line:335
        while not exit_requested :#line:337
            time .sleep (0.1 )#line:338
    except KeyboardInterrupt :#line:340
        os .system ('cls'if os .name =='nt'else 'clear')#line:341
    except Exception as O0OO00O000O00OOOO :#line:342
        logger .exception (f"An error occurred: {str(O0OO00O000O00OOOO)}")#line:343
    finally :#line:344
        keyboard .unhook_all ()#line:345
if __name__ =="__main__":#line:347
    main ()
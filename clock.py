from operator import mod
import streamlit as st 
import datetime
import time
from colorama import Fore, Back, Style
import pandas as pd 
import json
import os 

df = pd.read_csv(os.path.join("data", "time_data.csv"))
def modify_datetime(time):
    hrs, mins, secs = [int(x) for x in time.split(':')]
    return hrs * 3600 + mins * 60 + secs
df['Total seconds'] = df["Time"].apply(lambda x: modify_datetime(x))
part1, part2 = st.columns([2, 3])
part1.dataframe(data = df.style.highlight_max(axis=0), height = 250)
part2.bar_chart(data = df, x = "Day", y = "Total seconds", x_label = "Time Spent Studying", y_label = "Frequency",use_container_width = True)
st.line_chart(data = df, x = "Day", y = "Total seconds", x_label = "Days", y_label = "Time (in seconds)", use_container_width = True)

t = st.time_input("Set Timer:", value = None)
try: hv, mv, sv = t.hour, t.minute, 0
except: hv, mv, sv = 0, 0, 0
total_time = hv * 3600 + mv * 60 + sv
hours, minutes, seconds = st.columns(3) 
hour_p = hours.empty()
minute_p = minutes.empty()
second_p = seconds.empty()

##########################################################################
btn1, btn2 = st.columns([1, 6]) 
if btn1.button("Start", icon=":material/rocket:", type = "primary"):
    st.session_state["total_time"] = total_time
    st.session_state["timer_running"] = False 
    with open(os.path.join("data", "save_state"), "r") as files:
        try: temp_dict = json.load(files)
        except: temp_dict = {}
        for k, v in temp_dict.items():
            # Some keys might be missing in temp_dict.
            st.session_state[k] = v 
    st.session_state["timer_running"] = True
    while st.session_state["total_time"] >= 0:
        chv, cmv, csv = st.session_state["total_time"] // 3600, \
                        (st.session_state["total_time"] % 3600) // 60, \
                        st.session_state["total_time"] % 60 
        hour_p.metric("Hours", f"{chv}", label_visibility = "visible", border = True)
        minute_p.metric("Minutes", f"{cmv}", label_visibility = "visible", border = True)
        second_p.metric("Seconds", f"{csv}", label_visibility = "visible", border = True)
        st.session_state["total_time"] -= 1
        time.sleep(1)

if btn2.button("Pause", icon="⏸️") and "total_time" in st.session_state: 
    with open(os.path.join("data", "save_state"), "w") as files:
        json.dump(dict(st.session_state), files, indent = 5)
    chv, cmv, csv = st.session_state["total_time"] // 3600, \
                    (st.session_state["total_time"] % 3600) // 60, \
                    st.session_state["total_time"] % 60
    while True:
        hour_p.metric("Hours", f"{chv}", label_visibility = "visible", border = True)
        minute_p.metric("Minutes", f"{cmv}", label_visibility = "visible", border = True)
        second_p.metric("Seconds", f"{csv}", label_visibility = "visible", border = True)
        time.sleep(0.1)

st.divider()

##########################################################################
btn2, btn3 = st.columns([1, 4]) 
def get_time():
    hv, mv, sv = str(st.session_state["elapsed_time"] // 3600), \
                 str((st.session_state["elapsed_time"] % 3600) // 60), \
                 str(st.session_state["elapsed_time"] % 60)
    if len(hv) == 1: hv = "0" + hv
    if len(mv) == 1: mv = "0" + mv
    if len(sv) == 1: sv = "0" + sv
    return ":".join([hv, mv, sv])
def log_data():
    if "total_time" not in st.session_state:
        st.write(f'**Elapsed Time:** 00:00:00')
        return
    dt = max(0, total_time - max(0, st.session_state["total_time"]))
    if "elapsed_time" not in st.session_state: st.session_state["elapsed_time"] = 0
    st.session_state["elapsed_time"] += dt 
    del st.session_state["total_time"]
    with open(os.path.join("data", "save_state"), "w") as files:
        json.dump(dict(st.session_state), files, indent = 5)
    st.write(f'**Elapsed Time:** {get_time()}')
    if st.session_state["elapsed_time"] <= 0: st.balloons()

if btn2.button("Accumulate", icon="🔥", type = "primary"): log_data()

def save_data():
    global df 
    if "total_time" not in st.session_state: return
    current_day = df["Day"].max() + 1
    df = pd.concat([pd.DataFrame({"Day": [current_day], "Time": [get_time()]}), df], ignore_index = True)[["Day", "Time"]]
    df.to_csv(os.path.join("data", "time_data.csv"), index = False)
    with open(os.path.join("data", "save_state"), "r") as files:
        try: temp_dict = json.load(files)
        except: temp_dict = {}
        for k, v in temp_dict.items():
            if isinstance(v, int): temp_dict[k] = 0
            if isinstance(v, bool): temp_dict[k] = False 
    with open(os.path.join("data", "save_state"), "w") as files:
        json.dump(temp_dict, files, indent = 5)
        
if btn3.button("Save", icon="💾"): save_data()

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import RangeSlider, Button, Slider
import numpy as np
import pandas as pd

# we force a dark theme because raw white charts at 2 AM are a war crime against retinas.
plt.style.use('dark_background')

# ingesting data
df = pd.read_csv('depth_data.csv')
df.rename(columns={'Point': 'pt', 'Depth (m)': 'depth'}, inplace=True)

df['depth_raw'] = pd.to_numeric(df['depth'], errors='coerce')
df['temp_filled'] = df['depth_raw'].bfill().ffill()

# spike and noise cleaning
# We use rolling median and MAD instead of standard deviation because real-world telemetry is full of garbage outliers, and I can't put that into EWMA directly without polluting the stream, so I use the median to filter the really big spikes and then put that into ewma.
def clean_spikes(series, window=5, n_sigmas=3):
  rolling_med=series.rolling(window=window, min_periods=1, center=True).median()
  rolling_mad=(series-rolling_med).abs().rolling(window=window, min_periods=1,center=True).median()
  threshold=n_sigmas*1.4826*rolling_mad
  is_spike=(series-rolling_med).abs()>threshold
  cleaned=series.copy()
  cleaned[is_spike]=rolling_med[is_spike]
  return cleaned, is_spike
df['clean_stream'], df['is_spike'] = clean_spikes(df['temp_filled'])
# EWMA Floor Tracking: Smooths the stream so it doesn't look like an erratic cardiogram,
# introducing a tiny lag because physics hates instant gratification.
df['depth_ewma'] = df['clean_stream'].ewm(span=5, adjust=False).mean()
# proximity alerts: Looking at the first derivative to see if the floor is rushing upward to crack your hull
df['depth_diff']=df['depth_ewma'].diff()
df['is_proximity_alert']=df['depth_diff'] > 2.0
# canvas setup: carving out extra margins because cramming a legend inside the actual chart area is amateur hour
fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor('#121212')
ax.set_facecolor('#121212')
plt.subplots_adjust(bottom=0.35, right=0.8)

ax.set_title('Depth Feed', fontsize=12, fontweight='bold', color='white')
ax.set_xlabel('Time (Seconds)', color='white')
ax.set_ylabel('Metres (Inverted)', color='white')
ax.grid(True, linestyle='--', alpha=0.3, color='#333333')

valid_depths = pd.to_numeric(df['depth'], errors='coerce').dropna()
y_min = valid_depths.min()-50
y_max = 0
ax.set_ylim(y_min, y_max)

min_pt,max_pt = df['pt'].min(),df['pt'].max()
ax.set_xlim(min_pt,min_pt+30)

# Plot Layers: Separating the raw garbage stream from the processed fantasy line.
raw_line, = ax.plot([],[],color='#616161',alpha=0.6,linewidth=1.5,linestyle='-',label='Raw Reading')
ewma_line, = ax.plot([],[],color='#00B0FF',linewidth=2.5,label='Computed Floor (EWMA)',picker=5)
spike_scatter = ax.scatter([],[],color='#FF9100',edgecolor='black',s=40,zorder=4,label='Filtered Spike')
alert_scatter = ax.scatter([],[],color='#FF5252',s=60,zorder=5,label='Proximity Alert')

legend = ax.legend(bbox_to_anchor=(1.02, 1),loc='upper left',frameon=False)
for text in legend.get_texts():
  text.set_color('white')
# RangeSlider: For when you want to manually override the timeline instead of letting the script do it.
ax_slider = fig.add_axes([0.15, 0.20, 0.60, 0.03],facecolor='#1e1e1e')
slider = RangeSlider(ax_slider,'Timeline Window',min_pt,max_pt,valinit=(min_pt, min_pt + 30))
slider.label.set_color('white')
slider.valtext.set_color('white')

# Speed Slider: Allowing speed adjustment from 1x (1000ms interval) up to 10x (100ms interval).
ax_speed = fig.add_axes([0.15, 0.12, 0.45, 0.03],facecolor='#1e1e1e')
speed_slider = Slider(ax_speed,'Speed Multiplier',1.0,10.0,valinit=1.0,valstep=0.1)
speed_slider.label.set_color('white')
speed_slider.valtext.set_color('white')

def update_speed(val):
  # Directly modifying both interval properties and restarting the underlying timer source so backend queues pick it up immediately
  new_interval=1000.0/val
  anim.interval=new_interval
  if anim.event_source:
    anim.event_source.interval=new_interval
    anim.event_source.stop()
    anim.event_source.start()

speed_slider.on_changed(update_speed)

# auto scroll toggle button: because wrestling Matplotlib's event loop just to toggle a boolean is peak software engineering pain.
ax_button = fig.add_axes([0.63, 0.12, 0.12, 0.04])
btn_auto = Button(ax_button, 'Auto: ON',color='#1e1e1e',hovercolor='#333333')
btn_auto.label.set_color('white')

auto_scroll = True
slider_active = False
def toggle_auto(event):
  global auto_scroll
  auto_scroll = not auto_scroll
  btn_auto.label.set_text(f"Auto: {'ON' if auto_scroll else 'OFF'}")
  fig.canvas.draw_idle()

btn_auto.on_clicked(toggle_auto)

def update_slider(val):
  global slider_active
  if slider_active:
    ax.set_xlim(val[0],val[1])
    fig.canvas.draw_idle()

slider.on_changed(update_slider)

def on_press(event):
  global slider_active
  if event.inaxes==ax_slider:
    slider_active=True

def on_release(event):
  global slider_active
  if slider_active:
    slider_active=False

fig.canvas.mpl_connect('button_press_event', on_press)
fig.canvas.mpl_connect('button_release_event', on_release)

# Hover Annotation: Hand-crafting tooltips because Matplotlib's native interactivity is aggressively primitive.
annot = ax.annotate("", xy=(0,0), xytext=(-20,20), textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="#1e1e1e", ec="white", lw=1),
                    arrowprops=dict(arrowstyle="->", color="white"))
annot.set_visible(False)

def update_annot(ind):
  x,y=ewma_line.get_data()
  pos=ind["ind"][0]
  annot.xy=(x[pos], y[pos])
  annot.set_text(f"Time: {x[pos]:.1f}s\nDepth: {y[pos]:.2f}m")
  annot.get_bbox_patch().set_alpha(0.9)

def hover(event):
  vis = annot.get_visible()
  if event.inaxes==ax:
    cont,ind=ewma_line.contains(event)
    if cont:
      update_annot(ind)
      annot.set_visible(True)
      fig.canvas.draw_idle()
    else:
      if vis:
        annot.set_visible(False)
        fig.canvas.draw_idle()

fig.canvas.mpl_connect("motion_notify_event", hover)

def init():
  return raw_line, ewma_line, spike_scatter, alert_scatter

# Animation Frame Update: Feeding data slice by slice while fighting the rigid viewport state machine.
def update(frame):
  sub_df = df.iloc[:frame+1]
  raw_line.set_data(sub_df['pt'],sub_df['depth_raw'])
  ewma_line.set_data(sub_df['pt'],sub_df['depth_ewma'])

  spikes = sub_df[sub_df['is_spike']]
  spike_scatter.set_offsets(np.c_[spikes['pt'],spikes['depth_raw']] if not spikes.empty else np.empty((0, 2)))

  alerts = sub_df[sub_df['is_proximity_alert']]
  alert_scatter.set_offsets(np.c_[alerts['pt'],alerts['depth_ewma']] if not alerts.empty else np.empty((0, 2)))

  # Directly scroll the window viewport limits instead of breaking slider value triggers
  if auto_scroll and not slider_active and frame > 30:
    window_width=slider.val[1]-slider.val[0]
    new_left=frame-30
    new_right=new_left+window_width
    ax.set_xlim(new_left,new_right)
    slider.set_val((new_left,new_right))

  return raw_line, ewma_line, spike_scatter, alert_scatter

anim = FuncAnimation(fig, update, frames=len(df), init_func=init, interval=1000, repeat=False)
plt.show()
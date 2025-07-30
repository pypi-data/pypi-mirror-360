import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from bokeh.plotting import show, figure, save
from bokeh.io import export_png
from bokeh.layouts import column, row
from IPython.display import display
from bokeh.models import Button, ColumnDataSource, BoxEditTool, Slider, Div, InlineStyleSheet, RangeSlider
from bokeh.models.mappers import LinearColorMapper
from jupyter_bokeh.widgets import BokehModel
from bokeh.events import SelectionGeometry
from bokeh import palettes
from bokeh.colors import RGB
from matplotlib import cm
from scipy.ndimage import gaussian_filter

__all__ = ["plot_heatmap", 
           "plot_av_trace", 
           "colorbar", 
           "calcium_analysis_widget"
           ]


def plot_heatmap(axes:plt.Axes, 
                 data:pd.DataFrame, 
                 colfrom=None, 
                 colto=None, 
                 title="Heatmap",
                 cbar_title = "deltaF/F", 
                 vmin=-0.3, 
                 vmax=0.3, 
                 skipticks=None,
                 cmap="coolwarm",
                 trigger_onset=15,
                 cbar=True,
                 cbar_size = "5%",
                 **kwargs):
    ax=sns.heatmap(data.loc[:,colfrom:colto], ax=axes, vmin=vmin, vmax=vmax, cmap=cmap, cbar=False, cbar_kws={'label':cbar_title, 'aspect':40, 'pad':0.01},**kwargs)
    if cbar:
        colorbar(ax.get_children()[0], cbar_title, cbar_size)
        
    ax.set_title(title)
    ax.axvline(x=trigger_onset, linestyle='dashed', linewidth=1, color='k')

    if skipticks:    
        ax.set_xticks(ax.get_xticks()[::skipticks])
        ax.set_yticks(ax.get_yticks()[::skipticks])
        ax.set_yticklabels(["{}".format(round(i)) for i in range(0,len(ax.get_yticks()),skipticks)],fontsize=8)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("" )
    return ax


def plot_av_trace(
        axes:plt.Axes, 
        data:pd.DataFrame, 
        x:str,
        y:str, 
        title="Average dF/F", 
        xlim=None, 
        ylim=None, 
        ytitle="dF/F", 
        xtitle="Time (s)", 
        plot_individual=False,
        color='k',
        **kwargs):
    if plot_individual:
        ax = sns.lineplot(data=data,x=x,y=y, units=plot_individual, estimator=None, alpha=0.1, color=color)
    ax = sns.lineplot(data=data,x=x,y=y, ax=axes,errorbar=('se',1), color=color, **kwargs)
    if xlim:
        ax.set_xlim(xlim[0],xlim[1])
    if ylim:
        ax.set_ylim(ylim[0],ylim[1])
    else:
        ax.set_ylim(0)

    ax.set_xlabel(xtitle)
    ax.set_ylabel(ytitle)

#    ax.set_xticks([i for i in range(-3,9,3)])
#    ax.axvline(x=0, linestyle='dashed', linewidth=2, color='k')
    ax.spines['bottom'].set_position('zero')
#    ax2.fill_between(x=all_roi_av["Time"], y1 = all_roi_av["dF/F"] - all_roi_av["sem"], y2 = all_roi_av["dF/F"] + all_roi_av["sem"], alpha=0.2, color='k')
    ax.set_title(title)
    return ax


def colorbar(mappable, cbar_label="",cbar_size="5%"):
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    import matplotlib.pyplot as plt
    last_axes = plt.gca()
    ax = mappable.axes
    fig = ax.figure
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size=cbar_size, pad=0.02)
    cbar = fig.colorbar(mappable, cax=cax, label=cbar_label)
    cbar.set_label(cbar_label, labelpad=-0.5)
    plt.sca(last_axes)
    return cbar


def display_stack_bar(df:pd.DataFrame, ax:plt.Axes, title, palette=None, hatch=None, palette_orient="vertical", legend=True, stacked=True, normalize=True, pct=True):
    """
    Create a stacked or grouped bar chart with customizable colors, hatching patterns, and percentage labels.
    
    This function plots categorical data as bars with optional normalization, custom coloring schemes,
    and automatic chi-square contingency test calculation.
    
    Parameters
    ----------
    df : pd.DataFrame
        Data to plot where rows represent categories and columns represent groups.
    ax : plt.Axes
        Matplotlib axes object where the plot will be drawn.
    title : str
        Title for the plot. Will be displayed with chi-square p-value.
    palette : list, optional
        List of colors to use for the bars.
    hatch : list, optional
        List of hatch patterns to apply to bars.
    palette_orient : str, default="vertical"
        Controls color assignment direction:
        - "vertical": Same colors for bars in same row category across groups
        - "horizontal": Same colors for bars in same column group across categories
    legend : bool, default=True
        Whether to display the legend.
    stacked : bool, default=True
        If True, creates stacked bars; if False, creates grouped bars.
    normalize : bool, default=True
        If True, normalizes data to percentages within each group (columns).
    pct : bool, default=True
        If True, displays percentage values on bars.
        
    Returns
    -------
    None
        The function modifies the provided axes object directly.
        
    Notes
    -----
    - Automatically calculates and displays chi-square test p-value in the plot title
    - Percentages are shown inside bars when pct=True
    - Bar edges are always set to black with linewidth=0.5
    """
    
    from matplotlib.patches import Patch
    from scipy.stats import chi2_contingency

    pval=chi2_contingency(df.values.T)[1]
    if normalize:
        df = df.div(df.sum(axis=0),axis=1)
        ax.set_ylim(0,1)
    df.T.plot(kind="bar", legend=legend, stacked=stacked, width=0.4, ax=ax,)
    ax.set_title(f"{title}\n p={pval:.2f}")
    
    bar:Patch
    for i, bar in enumerate(ax.patches):
        #if i%len(df.columns):
        bar.set_edgecolor("k")
        bar.set_linewidth(0.5)
        if palette is not None:
            if palette_orient == "vertical":
                bar.set_facecolor(palette[i//len(df.columns)])
            else:
                bar.set_facecolor(palette[i%len(df.columns)])
        if hatch is not None:
            if palette_orient == "vertical":
                bar.set_hatch(hatch[i%len(df.columns)] if hatch is not None else None)
            else:
                bar.set_hatch(hatch[i//len(df.columns)] if hatch is not None else None)
        width = bar.get_width()
        height = bar.get_height()
        x = bar.get_x()
        y = bar.get_y() + height/2
        if pct:
            ax.text(x + width/2, y, f'{height*100:.1f}%', 
                            ha='center', va='center', fontsize=8)
    #add/modify legend
    if legend:
        handles, labels = ax.get_legend_handles_labels()
        if palette is not None:
            if palette_orient == "vertical":
                handles = [Patch(facecolor=palette[i]) for i in range(len(df.index))]
            else:
                handles = [Patch(facecolor='white',hatch=hatch[i] if hatch is not None else None) for i in range(len(df.columns))]
        ax.legend(handles, labels, fontsize=8)
    sns.despine()



def calcium_analysis_widget(z_file:np.ndarray, proc_file:np.ndarray, alignment_events:np.ndarray, baseline:float, posttime:float,FPS:float=5)->BokehModel:
    '''
    Disaply an interactive plot for the analysis of Ca-imaging data.

    # Parameters:

    z_file: array-like. A sequence of z-scored images, 3D numpy array, with time in the first dimension.

    proc_file: array-like. A sequence of z-scored images, aligned to the trigger onset.

    alignment_events: a list of events to align signals to, in seconds.

    baseline: length of the baseline before the alignment onset, in seconds. 

    posttime: duration of signal after the alignment onset, in seconds.

    FPS: sampling frequency, in Hz  
    
    # Returns:

    BokehModel of the widget, it can be displayed via IPython.display.display(*function output*) or via Panel, with panel.pane.Bokeh(*function output*) command.
    
    '''



    triggers = alignment_events
    m_coolwarm_rgb = (255 * cm.coolwarm(range(256))).astype('int')
    trial_length = (baseline+posttime)*FPS
    coolwarm_palette = [RGB(*tuple(rgb)).to_hex() for rgb in m_coolwarm_rgb]

    def tranform_bokeh_coords(bokeh_coords:list, invert_y=1):
        x = bokeh_coords[0]
        y = bokeh_coords[1]
        width = bokeh_coords[2]
        height = bokeh_coords[3]
        return [round(y-invert_y*height/2), round(y+invert_y*height/2), round(x-width/2), round(x+width/2)]

    def update_linegraph(second=0):
        nonlocal lines
        nonlocal lineplot
        nonlocal line_src
        nonlocal heatmap_df_al
        nonlocal ROI_colors

        if len(ROI_colors)!=len(ROIs):
            ROI_colors = [col_pal[roi%10] for roi in ROIs]

        if len(ROIs)==len(lines):
            roilist = []
            for roi in ROIs:
                new_coord = tranform_bokeh_coords(ROIs[roi], invert_y=-1)
                new_y = gaussian_filter(trace_to_show[:,new_coord[0]:new_coord[1],new_coord[2]:new_coord[3]],smooth_factor).mean(axis=1).mean(axis=1)
                new_x = [i/5 for i in range(0,trace_to_show.shape[0])]
                lines[roi].data_source.data = {'x':new_x, 'y{}'.format(roi):new_y}
                lines[roi].glyph.line_color = ROI_colors[roi]
                roilist.append(new_y)
            if len(ROIs):
                heatmap_df_al = np.array(roilist)
                im_heatmap_al_render.glyph.dh = len(ROIs)
                im_heatmap_al_render.data_source.data = {"image": [heatmap_df_al]}
            
        elif not second:
            if len(ROIs)<len(lines):
                lines = {roi:lines[roi] for roi in lines if roi<len(ROIs)}
                lineplot.renderers = lineplot.renderers[:len(ROIs)]
            while len(ROIs)>len(lines):
                roi = len(lines)
                line_src[roi] = ColumnDataSource({'x':[], 'y{}'.format(roi):[]})
                lines[roi] = lineplot.line('x','y{}'.format(roi), line_color=ROI_colors[roi],source=line_src[roi])

            update_linegraph(second=1)

    #DEFAULTS
    fig_dim = 400
    ROIs={}
    top_z = 4
    roi=0
    gridsize = 2
    frame = proc_file[0]
    smooth_factor = 0
    trace_to_show = proc_file.copy()
    heatmap_df = np.zeros((1,z_file.shape[0]))
    heatmap_df_al = np.zeros((1,posttime+baseline))
    latency_heatmap_df = np.zeros((gridsize, gridsize))
    latency_heatmap_df.fill(np.nan)
    ROI_colors = np.array([])
    diff_file = []
    latency_z_thresh = 1
    cor_df = []

    #COLORS
    col_pal = palettes.Category20[20]
    color_mapper = LinearColorMapper(palette=coolwarm_palette, low=-top_z, high=top_z)
    heatmap_color_mapper = LinearColorMapper(palette=coolwarm_palette, low=-top_z/2, high=top_z/2)
    latency_color_mapper = LinearColorMapper(palette="Viridis256", low=0, high=4)
    category_mapper = LinearColorMapper(palette=palettes.Category20_20, low=-1, high=19)

    #STYLES
    slider_st = InlineStyleSheet(css=".bk-slider-title { color: black; }")
    label_st = InlineStyleSheet(css=".bk-div { color: black; }")

    #LINEGRAPH
    lineplot = figure(width=fig_dim,height=fig_dim//2,tools=["ywheel_zoom"])
    line_src = {roi:ColumnDataSource({'x':[], 'y':[], 'line_color':'blue'}) for roi in ROIs}
    lineplot.vspan(x=[baseline])
    lines={roi:lineplot.line('x','y{}'.format(roi),source=line_src[roi], line_color='line_color') for roi in ROIs}
    update_linegraph()

    cluster_lineplot = figure(width=fig_dim,height=fig_dim//2,tools=["ywheel_zoom"])
    cluster_lineplot.vspan(x=[baseline])


    # IMAGE AND TOOLS
    im_frame = figure(width=fig_dim, tools=["reset"], height=fig_dim, toolbar_location=None)
    src = ColumnDataSource({
        'x': [ROIs[roi][0] for roi in ROIs], 'y': [ROIs[roi][1] for roi in ROIs], 'width': [ROIs[roi][2] for roi in ROIs],
        'height': [ROIs[roi][3] for roi in ROIs], 'alpha': [1 for roi in ROIs], 'line_color':[col_pal[roi%10] for roi in ROIs], 'line_width': [1 for roi in ROIs]
    })

    r = im_frame.rect('x', 'y', 'width', 'height', line_color="line_color", line_width="line_width", source=src, alpha='alpha', fill_alpha=0)
    draw_tool = BoxEditTool(renderers=[r],  num_objects=32)
    im_frame.add_tools(draw_tool)
    im_frame.toolbar.active_drag = draw_tool

    im_render = im_frame.image(image=[frame], color_mapper=color_mapper, x=0, y=0, dw=frame.shape[1], dh=frame.shape[0], level="image")
    im_frame.grid.grid_line_width = 0
    im_frame.y_range.flipped = True

    cor_heatmap = figure(width=int(fig_dim/2), tools=["reset",], height=int(fig_dim/2), title="Correlated rois", toolbar_location=None)
    cor_renderer = cor_heatmap.image([], color_mapper=category_mapper, x=0, y=0, dw=gridsize, dh=gridsize, level="image")
    cor_heatmap.grid.grid_line_width = 0
    cor_heatmap.y_range.flipped = True

    #Heatmaps
    im_heatmap_aligned = figure(width=fig_dim, tools=["reset"], height=fig_dim//2, title="Aligned heatmap", x_range = lineplot.x_range, toolbar_location=None)
    im_heatmap_aligned.vspan(x=[baseline])
    im_heatmap_al_render = im_heatmap_aligned.image(image=[heatmap_df_al], color_mapper=heatmap_color_mapper, x=0, y=0, dw=posttime+baseline, dh=len(ROIs), level="image")
    im_heatmap_aligned.grid.grid_line_width = 0

    im_heatmap = figure(width=fig_dim, tools=["reset","xwheel_zoom"], height=fig_dim//2, title="Recording-wide heatmap")
    im_heatmap.vspan(x=triggers)
    heatmap_line = im_heatmap.line(x=[0,len(z_file)/FPS], y=[len(ROIs)+1, len(ROIs)+1], line_color='red', line_width=2)
    im_heatmap_render = im_heatmap.image(image=[heatmap_df], color_mapper=heatmap_color_mapper, x=0, y=0, dw=int(len(z_file)/FPS), dh=len(ROIs), level="image")
    im_heatmap.grid.grid_line_width = 0


    #Latency heatmap
    latency_heatmap = figure(width=int(fig_dim/1.5), tools=["reset"], height=int(fig_dim/1.5), title="Response latency heatmap", toolbar_location=None)
    latency_renderer = latency_heatmap.image([latency_heatmap_df], color_mapper=latency_color_mapper, x=0, y=0, dw=gridsize, dh=gridsize, level="image")
    latency_heatmap.grid.grid_line_width = 0
    latency_heatmap.y_range.flipped = True
    #Latency streamplot
    latency_streamplot = figure(width=int(fig_dim/1.5), tools=["reset"], height=int(fig_dim/1.5), title="Response latency streamplot", toolbar_location=None)
    latency_streampot_renderer = latency_streamplot.image([latency_heatmap_df],  x=0, y=0, dw=gridsize, dh=gridsize, level="image")
    latency_streamplot.grid.grid_line_width = 0
    latency_streamplot.y_range.flipped = True

    #Differential image
    dif_heatmap = figure(width=int(fig_dim/1.5), tools=["reset"], height=int(fig_dim/1.5), title="Differential image", toolbar_location=None)
    dif_renderer = dif_heatmap.image([], color_mapper=color_mapper, x=0, y=0, dw=gridsize, dh=gridsize, level="image")
    dif_heatmap.grid.grid_line_width = 0
    dif_heatmap.y_range.flipped = True

    #Differential image streamplot
    dif_streamplot = figure(width=int(fig_dim/1.5), tools=["reset"], height=int(fig_dim/1.5), title="Differential image streamplot", toolbar_location=None)
    dif_streampot_renderer = dif_streamplot.image([],  x=0, y=0, dw=gridsize, dh=gridsize, level="image")
    dif_streamplot.grid.grid_line_width = 0
    dif_streamplot.y_range.flipped = True


    # BUTTONS
    update_heatmap_button = Button(label="Update heatmap", button_type="primary", sizing_mode="fixed")
    split_into_roigrid_button = Button(label="Split FOV into ROI grid", button_type="primary", sizing_mode="fixed")
    latency_heatmap_button = Button(label="Calculate latency heatmap", button_type="primary", sizing_mode="fixed")
    av_latency_heatmap_button = Button(label="Calculate AV. latency heatmap", button_type="primary", sizing_mode="fixed")
    dif_image_button = Button(label="Make differential image", button_type="primary", sizing_mode="fixed")
    find_similarities_button = Button(label="Find correlated regions", button_type="primary", sizing_mode="fixed")
    sort_heatmaps_button = Button(label="Resort heatmaps", button_type="primary", sizing_mode="fixed")

    # SLIDERS
    trace_slider = Slider(start=0, end=len(triggers), value=0, step=1, title="Select trace (0 for average of all)", sizing_mode='stretch_width', stylesheets=[slider_st])
    frame_slider = Slider(start=0, end=proc_file.shape[0]-1, value=0, step=1, title="Select frame", sizing_mode='stretch_width', stylesheets=[slider_st])
    z_slider = Slider(start=0.1, end=10, value = top_z, step = 0.1, title="Z-threshold", sizing_mode='stretch_width', stylesheets=[slider_st])
    smooth_slider = Slider(start=0, end=10, value = 0, step = 1, title="Smoothing", sizing_mode='stretch_width', stylesheets=[slider_st])
    grid_slider = Slider(start=2, end=20, value = 2, step = 1, width=fig_dim//3, title="Grid Size", stylesheets=[slider_st])
    latency_z_thresh_slider = Slider(start=0, end=3, value = 1, step = 0.1, title="Response Z thresh", stylesheets=[slider_st],width=fig_dim//3)
    latency_range_slider = RangeSlider(start=0, end = int(trial_length/FPS), value=(0,int(trial_length/FPS)), step=0.1, title="Colormap range", width=fig_dim//2, stylesheets=[slider_st])


    # CALLBACKS
    def box_callback(data, old,new):
        nonlocal ROI_colors
        if old!=new:
            nonlocal ROIs
            if len(r.data_source.data["x"]):
                ROIs={}
                for roi,val in enumerate(r.data_source.data["x"]):
                    width = r.data_source.data["width"][roi]
                    height = r.data_source.data["height"][roi]
                    x=r.data_source.data["x"][roi]
                    y=r.data_source.data["y"][roi]
                    ROIs[roi] = [x,y,width,height]

                if len(ROI_colors)!=len(ROIs):
                    ROI_colors = [col_pal[roi%10] for roi in ROIs]

                r.data_source.data = {
                    'x': [ROIs[roi][0] for roi in ROIs], 'y': [ROIs[roi][1] for roi in ROIs], 'width': [ROIs[roi][2] for roi in ROIs],
                    'height': [ROIs[roi][3] for roi in ROIs], 'alpha': [1 for roi in ROIs], 'line_color':ROI_colors, 'line_width': [1 for roi in ROIs]
                }
            update_linegraph()

    def selection_change(data,old,new):
        if len(new):
            for line in lines:
                lines[line].visible = (line in new)
        else:
            for line in lines:
                lines[line].visible = True

    def change_trace_callback(attr, old, new):
        nonlocal trace_to_show
        if new:
            timestamp = triggers[new-1]
            trace_to_show = z_file[int((timestamp-baseline)*FPS):int((timestamp+posttime)*FPS)]
            heatmap_line.data_source.data = {'x':[timestamp-baseline,timestamp+posttime], 'y':[len(ROIs)+1, len(ROIs)+1]}
        else:
            trace_to_show = proc_file.copy()
            heatmap_line.data_source.data = {'x':[0,len(z_file)//FPS], 'y':[len(ROIs)+1, len(ROIs)+1]}
        
        change_frame_callback("",0,frame_slider.value)
        update_linegraph()

    def change_frame_callback(attr, old, new):
        nonlocal diff_file
        frame = trace_to_show[new]
        if smooth_factor:
            frame = gaussian_filter(frame,smooth_factor)
        im_render.data_source.data = {"image": [frame]}
        if len(diff_file):
            dif_renderer.data_source.data= {"image":[diff_file[new]]}
        #im_frame.image(image=[frame], x=0, y=0, dw=frame.shape[1], dh=frame.shape[0], level="image",  color_mapper=color_mapper)

    def change_z_callback(attr, old, new):
        nonlocal top_z
        nonlocal color_mapper
        top_z=new
        color_mapper.low = -top_z
        color_mapper.high = top_z
        heatmap_color_mapper.low = -top_z/2
        heatmap_color_mapper.high = top_z/2

    def change_smooth_callback(attr, old, new):
        nonlocal smooth_factor
        smooth_factor=new
        frame = trace_to_show[frame_slider.value].copy()
        if smooth_factor:
            frame = gaussian_filter(frame,smooth_factor)
        im_render.data_source.data = {"image": [frame]}
        update_linegraph()

    def update_heatmap_callback(event):
        nonlocal heatmap_df
        roilist = []
        if len(r.data_source.selected.indices):
            rois_to_plot = r.data_source.selected.indices
        else:
            rois_to_plot = ROIs
        for roi in rois_to_plot:
            new_coord = tranform_bokeh_coords(ROIs[roi], invert_y=-1)
            roilist.append(gaussian_filter(z_file[:,new_coord[0]:new_coord[1],new_coord[2]:new_coord[3]],smooth_factor).mean(axis=1).mean(axis=1))
        heatmap_df = np.array(roilist)
        heatmap_line_x = heatmap_line.data_source.data["x"]
        heatmap_line_y = [len(ROIs)+1, len(ROIs)+1]
        heatmap_line.data_source.data = {"x":heatmap_line_x, "y":heatmap_line_y}
        im_heatmap_render.glyph.dh = len(ROIs)
        im_heatmap_render.data_source.data = {"image":[heatmap_df]}
        
    def ROIgrid_callback(event):
        nonlocal ROIs
        nonlocal gridsize
        gridsize = grid_slider.value
        w = im_render.data_source.data["image"][0].shape[1]/gridsize
        h = im_render.data_source.data["image"][0].shape[0]/gridsize
        X = [1+w//2 + i*w for i in range(gridsize)]
        Y = [1+h//2 + i*h for i in range(gridsize)]
        X,Y = np.meshgrid(X,Y)

        r.data_source.data = {
                    'x': X.ravel().tolist(), 'y': Y.ravel().tolist(), 'width': [w for i in range(gridsize**2)],
                    'height': [-h for i in range(gridsize**2)], 'alpha': [1 for i in range(gridsize**2)],
                    'line_color':[col_pal[i%10] for i in range(gridsize**2)], 'line_width': [2 for i in range(gridsize**2)]
                }
        
    def recalc_latencies_callback(event):
        nonlocal latency_heatmap_df
        nonlocal gridsize
        if len(lines):
            line_df = pd.DataFrame([lines[line].data_source.data["y{}".format(line)] for line in lines]).T
            #latencies = np.array([-1 if (line_df[col].max()<latency_z_thresh or line_df[col][:10].mean()>latency_z_thresh) else line_df[col].where(line_df[col]/line_df[col].max()>0.4).dropna().index[0] for col in line_df])
            latencies = np.array([-1 if (line_df[col].max()<latency_z_thresh or line_df[col][:10].mean()>latency_z_thresh) else line_df[col].where(line_df[col]>latency_z_thresh).dropna().index[0] for col in line_df])
            latency_heatmap_df = pd.Series(latencies).where(latencies>0).values.reshape(gridsize,gridsize)/FPS
            latency_renderer.glyph.dw = gridsize
            latency_renderer.glyph.dh = gridsize
            latency_renderer.data_source.data={"image":[latency_heatmap_df]}

            fig = plt.figure(figsize=(5,5))
            ax=plt.gca()
            X,Y=np.meshgrid(range(gridsize),range(gridsize))
            Ex=np.gradient(latency_heatmap_df,axis=0)
            Ey=np.gradient(latency_heatmap_df,axis=1)
            ax.streamplot(X,Y,Ex,Ey, density=2)
            #ax.streamplot(X,Y,Ex,-Ey, density=3)
            ax.set_xlim(0,gridsize)
            ax.set_ylim(gridsize,0)
            ax.axis("off")
            canvas = fig.canvas
            canvas.draw()
            buf = np.asarray(canvas.buffer_rgba())
            plt.close()
            latency_streampot_renderer.glyph.dw = gridsize
            latency_streampot_renderer.glyph.dh = gridsize
            buf = cv2.cvtColor(buf[100:-100,100:-100], cv2.COLOR_BGR2GRAY)
            latency_streampot_renderer.data_source.data = {"image":[buf]}

    def recalc_av_latencies_callback(event):
        nonlocal latency_heatmap_df
        nonlocal gridsize
        if len(lines):
            lat_list = []
            for i in range(trial_num):
                roilist = []
                for roi in ROIs:
                    new_coord = tranform_bokeh_coords(ROIs[roi], invert_y=-1)
                    trace_to_show = z_file[i*trial_length:(i+1)*trial_length]
                    new_y = gaussian_filter(trace_to_show[10:,new_coord[0]:new_coord[1],new_coord[2]:new_coord[3]],smooth_factor).mean(axis=1).mean(axis=1)
                    roilist.append(new_y)
                line_df = pd.DataFrame(roilist).T
                latencies = np.array([-1 if (line_df[col].max()<latency_z_thresh or line_df[col][:10].mean()>latency_z_thresh) else line_df[col].where(line_df[col]/line_df[col].max()>0.4).dropna().index[0] for col in line_df])
                latencies = pd.Series(latencies).where(latencies>0).values.reshape(gridsize,gridsize)/FPS
                lat_list.append(latencies)
            latency_heatmap_df = np.nanmean(np.array(lat_list),axis=0)
            latency_renderer.glyph.dw = gridsize
            latency_renderer.glyph.dh = gridsize
            latency_renderer.data_source.data={"image":[latency_heatmap_df]}

    def update_latency_colormap_range(attr, old, new):
        nonlocal latency_color_mapper
        latency_color_mapper.low = new[0]
        latency_color_mapper.high = new[1]

    def update_latency_z_thresh(attr, old, new):
        nonlocal latency_z_thresh
        latency_z_thresh=new

    def make_dif_image(event):
        fig = plt.figure(figsize=(5,5))
        nonlocal trace_to_show
        nonlocal diff_file
        temp_bin = gaussian_filter(pnan.space_bin(trace_to_show,2),5)
        mask = np.where(temp_bin.max(axis=0)<0.2)
        temp_bin = temp_bin/ temp_bin.max(axis=0)
        temp_bin[:,mask[0],mask[1]] = np.nan
        
        diff_file =  (np.roll(temp_bin,-4,axis=0)-np.roll(temp_bin,4,axis=0))

        frame = diff_file[frame_slider.value]
        dif_renderer.data_source.data = {"image":[frame]}

        X,Y=np.meshgrid(range(frame.shape[1]),range(frame.shape[0]))
        Ex=np.gradient(frame,axis=0)
        Ey=np.gradient(frame,axis=1)
        ax = plt.gca()
        ax.streamplot(X,Y,Ey,Ex, density=2)
        ax.invert_yaxis()
        ax.set_xlim(0,frame.shape[0])
        ax.set_ylim(frame.shape[1],0)
        canvas = fig.canvas
        canvas.draw()
        buf = np.asarray(canvas.buffer_rgba())
        plt.close()
        buf = cv2.cvtColor(buf[100:-100,100:-100], cv2.COLOR_BGR2GRAY)
        dif_streampot_renderer.data_source.data = {"image":[buf]}

    def find_similarities(event):
        nonlocal cor_df
        nonlocal gridsize
        nonlocal ROI_colors
        if heatmap_df.shape[0]>1:
            n_neighbours = 10#gridsize//2
            reducer = umap.UMAP(metric = "correlation", n_neighbors=n_neighbours, min_dist=0)
            embedding = reducer.fit_transform(heatmap_df)
            cluster = HDBSCAN().fit_predict(embedding)
            cor_df = cluster.reshape(gridsize,gridsize)
            cor_renderer.data_source.data = {"image": [cor_df]}

            ROI_colors = [col_pal[clus+1] for clus in cluster]
            x = r.data_source.data["x"]
            y = r.data_source.data["y"]
            w = r.data_source.data["width"]
            h = r.data_source.data["height"]
            r.data_source.data = {"x":x, "y":y, "width": w, "height":h, 'line_color':ROI_colors,'alpha': [1 for roi in ROIs], 'line_width': [1 for roi in ROIs]}

            cluster_lineplot.renderers=[]
            cluster_lineplot.vspan(x=[baseline])
            temp_df = pd.DataFrame(heatmap_df_al).T
            newx = [i/FPS for i in range(temp_df.shape[0])]
            for clus in np.unique(cluster):
                newy = temp_df.loc[:, np.where(cluster==clus)[0]].mean(axis=1).values
                cluster_lineplot.line(x=newx, y=newy, line_color = palettes.Category20_20[clus+1])

    def resort_heatmaps(event):
        nonlocal cor_df
        nonlocal gridsize
        nonlocal heatmap_df
        nonlocal heatmap_df_al
        if len(cor_df) == gridsize:
            heatmap_df = pd.DataFrame(heatmap_df)
            heatmap_df["clus"] = cor_df.ravel()
            heatmap_df = heatmap_df.sort_values(by="clus").drop(columns="clus").values
            im_heatmap_render.data_source.data = {"image": [heatmap_df]}

            heatmap_df_al = pd.DataFrame(heatmap_df_al)
            heatmap_df_al["clus"] = cor_df.ravel()
            heatmap_df_al = heatmap_df_al.sort_values(by="clus").drop(columns="clus").values
            im_heatmap_al_render.data_source.data = {"image": [heatmap_df_al]}


    # SIGNAL CONNECTIONS
    trace_slider.on_change('value_throttled', change_trace_callback)
    frame_slider.on_change('value', change_frame_callback)
    z_slider.on_change('value', change_z_callback)
    smooth_slider.on_change('value', change_smooth_callback)
    src.on_change('data',box_callback)
    r.data_source.selected.on_change("indices", selection_change)
    update_heatmap_button.on_click(update_heatmap_callback)
    split_into_roigrid_button.on_click(ROIgrid_callback)
    latency_heatmap_button.on_click(recalc_latencies_callback)
    av_latency_heatmap_button.on_click(recalc_av_latencies_callback)
    latency_range_slider.on_change("value", update_latency_colormap_range)
    latency_z_thresh_slider.on_change("value", update_latency_z_thresh)
    dif_image_button.on_click(make_dif_image)
    find_similarities_button.on_click(find_similarities)
    sort_heatmaps_button.on_click(resort_heatmaps)

    bokeh_m = BokehModel(column(
        row(column(trace_slider,frame_slider,z_slider, smooth_slider,im_frame,row(grid_slider,split_into_roigrid_button,update_heatmap_button), cluster_lineplot),
            column( lineplot,im_heatmap_aligned,im_heatmap,row(column(find_similarities_button, sort_heatmaps_button), cor_heatmap)),
            column(row(latency_heatmap_button, latency_z_thresh_slider, av_latency_heatmap_button),
                latency_range_slider, 
                row(latency_heatmap, latency_streamplot),
                dif_image_button,
                row(dif_heatmap, dif_streamplot)
                ))))

    return bokeh_m
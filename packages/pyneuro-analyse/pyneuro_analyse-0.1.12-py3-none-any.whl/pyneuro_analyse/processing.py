'''
Set of helper functions to use 
'''



__all__=["extract_timestamp_cutouts", 
         "extract_timestamp_cutouts_2p", 
         "locate_onsets_offsets", 
         "create_timestamp_aligned_video", 
         "z_score_trace", 
         "bin_trace", 
         "space_bin", 
         "extract_response_parameters", 
         "calculate_response_statistics",
         "load_preprocess_TST_datasets",
         "calc_velocities_standardize_DLC"]



import numpy as np
import pandas as pd
import math
from scipy.ndimage import gaussian_filter, gaussian_filter1d
from matplotlib.axes import Axes
from scipy.optimize import curve_fit
from scipy.stats import wilcoxon
import matplotlib.pyplot as plt
import seaborn as sns

def extract_timestamp_cutouts(trace_to_extr:np.ndarray, 
                              uncor_timestamps:np.ndarray, 
                              baseline:float, 
                              posttime=None,
                              sampling=1,
                              offset=0.0, 
                              z_scored=False, 
                              dff=False,
                              z_scoring_interval:tuple = None)->pd.DataFrame:
    """
        # Parameters:
        **trace_to_extract**: an array containing values of interest (e.g. dF/F trace), ASSUMES CONSTANT SAMPLING FREQUENCY!!

        **timestamps**: array containing timepoints of the events, points from trace_to_extract will be taken around each timestamp

        **baseline**: time before the timepoint (in seconds) to be extracted

        **posttime**: time after the timepoint (in seconds) to be extracted, by default equals baseline

        **sampling**: acquisition rate of the trace_to-extract, in Hz (by default 1)

        **offset**: shift in time in seconds between timestamps and trace_to_extract (if, for example photometry acqusition starts 5 seconds before behavior video 
            from which timepoints were annotated offset = 5)

        **z-scored**: returns cutouts as z-score values computed on baseline

        **dff**: returns cutouts as deltaF/F values computed on baseline

        # Returns:
        DataFrame with signal cutouts around each trigger, organized in columns
    """
    #Copy the input trace
    trace_to_extract = trace_to_extr.copy()
    #if time after the trigger is not specified, make it equal to baseline
    if not posttime:
        posttime=baseline
    #if time interval for z-score baseline is not specified, use the whole duration of the baseline
    if z_scoring_interval is None:
        z_scoring_interval = (-baseline,0)
    #Make "result" dataframe
    result=pd.DataFrame()
    #Apply offset to trigger timestamps
    timestamps = uncor_timestamps+offset
    #Define length of the cutout (in points)
    cutout_length =  round((posttime+baseline)*sampling)
    #Define time points of the cutouts relative to the trigger

    cutouts = []
    #Extract cutouts around each trigger in a loop
    for i,timestamp in enumerate(timestamps):
        indfrom = round((timestamp-baseline)*sampling)
        if indfrom<0 or indfrom+cutout_length>len(trace_to_extract):
            continue
        cutouts.append(pd.Series(trace_to_extract[indfrom:indfrom+cutout_length]))
    if len(cutouts)==0:
        print("No cutouts extracted, check timestamps and baseline/posttime parameters.")
        return pd.DataFrame()
    result = pd.concat(cutouts, axis=1)
    result.index=np.round([-baseline + i/sampling for i in range(len(result.index))],round(math.log10(sampling)+2))
    
    #Apply deltaF/F0 transformation to all cutouts (columns of results
    if dff:
        result = result.div(result.loc[:0,:].mean(axis=0), axis=1)-1
    #Apply z-score transformation to the cutout (columns of results)
    if z_scored:
        z_score_from = result.index[result.index>=z_scoring_interval[0]][0]
        z_score_to = result.index[result.index<z_scoring_interval[1]][-1]
        for col in result:
            std = result.loc[z_score_from:z_score_to,col].std()
            result[col]-=result.loc[z_score_from:z_score_to,col].mean()
            result[col]/=std
            
    return result

def extract_timestamp_cutouts_2p(roi_table:pd.DataFrame, 
                                 uncor_timestamps :np.ndarray, 
                                 baseline:float, 
                                 posttime=None,
                                 sampling=1,
                                 offset=0.0, 
                                 z_scored=False, 
                                 dff=False, 
                                 z_scoring_interval:tuple = None)->pd.DataFrame:
    """
        Parameters:
        roi_table: 2d table containing ROI data, 1 ROI per column, ASSUMES CONSTANT SAMPLING FREQUENCY!!

        timestamps: array containing timepoints of the events, points from trace_to_extract will be taken around each timestamp

        baseline: time before the timepoint (in seconds) to be extracted

        posttime: time after the timepoint (in seconds) to be extracted, by default equals baseline

        sampling: acquisition rate of the trace_to-extract, in Hz (by default 1)

        offset: shift in time in seconds between timestamps and trace_to_extract (if, for example photometry acqusition starts 5 seconds before behavior video 
            from which timepoints were annotated offset = 5)

        z-scored: returns cutouts as z-score values computed on baseline

        dff: returns cutouts as deltaF/F values computed on baseline

        Returns:
        DataFrame with signal cutouts around each trigger, for each ROI, organized in columns
    """
    #Declare list of results to store cutouts of every ROI
    per_ROI_df_list = []
    #Go over all ROIs in a loop
    for i,roi in enumerate(roi_table):
        #Extract cutout for current ROI
        temp_results = extract_timestamp_cutouts(roi_table[roi].values, uncor_timestamps, baseline, posttime, sampling, offset, z_scored, dff, z_scoring_interval)
        #Rename columns to start with ROI
        temp_results.columns = [f"ROI{i:02}_{col:02}" for col in temp_results.columns]
        #append one ROI results to the list
        per_ROI_df_list.append(temp_results.T)
    #Concatenate results into one big table and return the product
    return pd.concat(per_ROI_df_list, axis=0)

    
def locate_onsets_offsets(annotated_trace:np.ndarray, time_trace:np.ndarray = None, thresh=0.5, on_dur_thresh=0, off_dur_thresh=0, return_dur = False, pad_edges=False)->pd.DataFrame:
    '''
    Locate all time point in the annotated trace where annotated trace crosses the threshold in the up (onsets) or down (offsets) direction.

    # Parameters:

    annotated_trace: array with behavioral annotations

    time_trace: array of equal length with annotated_trace, providing timing information on every point. If not provided, assumes 1 second for each point in annotated_trace

    thresh: Threshold to separate ON and OFF states of the trace, Default = 0.5 (separates above and below)

    on_dur_threh: removes all ON bouts with shorter duration than this parameter (in s), merges OFF bouts

    off_dur_thresh: removes all OFF bouts shorter that this parameter (in s), merges ON bouts

    return_dur: append column with durations of ON bouts

    # Returns:

    Table with onsets (column 1), offsets (column 2) timings, and if return_dur=True durations of active state (column 3)
    '''

    #If time trace is not given, make one with integers of the same length as the annotated trace
    if time_trace is None:
        time_trace = np.arange(len(annotated_trace))
    
    #Detect all timepoints where annotated trace crosses the treshold in either direction (all point above threshold where previous point is below the threshold, and vice-versa)
    onsets = time_trace[1:][(annotated_trace[1:]>thresh) & (annotated_trace[:-1]<=thresh)].astype("float")
    offsets = time_trace[1:][(annotated_trace[1:]<thresh) & (annotated_trace[:-1]>=thresh)].astype("float")

    if len(onsets)==0 and len(offsets)==0:
        print("Nothing detected")
        return pd.DataFrame({"on":[], "off":[]})

    #Pad the list of onset timepoints with empty values (nan) in case there are less of them compared to list of offsets
    if len(onsets)< len(offsets) or offsets[0]<onsets[0]:
        to_insert = time_trace[0] if pad_edges else float("nan")
        onsets=np.insert(onsets,0,to_insert)
    #Same but for offsets compared to onsets
    if len(onsets)> len(offsets):
        to_insert = time_trace[-1] if pad_edges else float("nan")
        offsets=np.append(offsets,to_insert)

    #calculate duration of every off-state
    off_durations=onsets-np.roll(offsets,1)
    off_durations[0] = onsets[0] - time_trace[0] 
    #if off_dur_threshold given, exclude all onsets starting within off_dur_thresh seconds after the previous offset (and the corresponding offset)
    if off_dur_thresh>0:
        #keep only onsets/offsets where duration is above given value
        onsets = onsets[off_durations>=off_dur_thresh]
        offsets = np.append(offsets[:-1][off_durations[1:]>=off_dur_thresh], offsets[-1])

        #Pad the list of onset timepoints with empty values (nan) in case there are less of them compared to list of offsets
        if len(onsets)< len(offsets) or offsets[0]<onsets[0]:
            to_insert = time_trace[0] if pad_edges else float("nan")
            onsets=np.insert(onsets,0,to_insert)
        #Same but for offsets compared to onsets
        if len(onsets)> len(offsets):
            to_insert = time_trace[-1] if pad_edges else float("nan")
            offsets=np.append(offsets,to_insert)
        #recalculate new durations

        off_durations=onsets-np.roll(offsets,1)
        off_durations[0] = onsets[0] - time_trace[0] 


    
    #calculate duration of every on-state
    on_durations=offsets-onsets
    #if on_dur_threshold given, exclude all offsets starting within on_dur_thresh seconds after the previous onset (and the corresponding onset)
    if on_dur_thresh>0:
        #keep only onsets/offsets where duration is above given value
        indices_to_keep = on_durations>=on_dur_thresh
        onsets = onsets[indices_to_keep]
        offsets = offsets[indices_to_keep]
        #off_durations = off_durations[indices_to_keep]
        #recalculate new durations
        on_durations=offsets-onsets
        if len(onsets)>0:
            off_durations=onsets-np.roll(offsets,1)
            off_durations[0] = onsets[0] - time_trace[0]


    #concatenate results in the table
    results = pd.concat([pd.Series(onsets), pd.Series(offsets)],axis=1)
    #rename columns to "on", "off"
    results.columns = ["on","off"]
    #if also returning durations, calculate final durations of on- and off-state and append to the table
    if return_dur:
        results["on_duration"] = on_durations
        results["off_duration"] = off_durations
    #return result table
    return results



def create_timestamp_aligned_video(video:np.ndarray, 
                                   timestamps:np.ndarray, 
                                   FPS:int, 
                                   baseline:float, 
                                   posttime:float, 
                                   bin_factor=1, 
                                   gaussian_smoothing=None, 
                                   z_scored=False,
                                   z_scoring_interval:tuple = None):
    """
    Produce a sequence of images by extracting cutouts around event timestamps and averaging them

    # Parameters:

    video: 3d array (time being the first dimension) from which to make an aligned movie

    timestamps: a list of timestamps (in seconds) to which to align the video

    FPS: sampling frequency in Hz

    baseline: duration of cutout before alignment point, in seconds

    posttime: duration of cutout afte the alignment point, in seconds

    bin_factor: optional, perform spatial n x n binning on the resulting video. Default: 1 - no binning 

    gaussian_smoothing: optional, kernel for the gaussian filter (smoothes both in space !!AND TIME!!). Default: None - no smoothing

    z_scored: if True, z-scores the movie, mean and std for z-scoring are calculated on the "z-scoring interval". Default: False

    z-scoring_interval: if not None, a pair of values denoting the interval in which to calculate the mean and std for z-scoring, in seconds, relative to the alignment point 0,
    e.g. (-3,0) will use all points 3 seconds before the alignemtn point (including -3). if None, uses the whole duration of the baseline. Default: None

    # Returns:

    A video (3d array) aligned to the event. 1st dimention is time.
    """
    #empty list of cutouts
    excerpts = []
    #counter for ommitted timestamps
    omitted_count = 0

    #if z_scoring_interval is not given, take the whole baseline to calculate z-score
    if z_scoring_interval is None:
        z_scoring_interval = (-baseline,0)

    
    for timestamp in timestamps:
        #take timestamps not too close to the start/end of the trace (defined by the length of baseline and posttime)
        if timestamp>=baseline and timestamp<=len(video)/FPS-posttime:
            from_frame = int((timestamp-baseline)*FPS)
            to_frame = int((timestamp+posttime)*FPS)
            #append new cutout to the list of cutouts
            excerpts.append(video[from_frame:to_frame,:,:])
            #z-score the resulting excerpt if needed, based on the z_scoring_interval
            if z_scored:
                z_from = int((baseline+z_scoring_interval[0])*FPS)
                z_to = int((baseline+z_scoring_interval[1])*FPS)
                excerpts[-1] = (excerpts[-1]-excerpts[-1][z_from:z_to].mean(axis=0))\
                    /excerpts[-1][z_from:z_to].std(axis=0)

        #exclude timestamps too close to the start/end of the trace (defined by the length of baseline and posttime)
        else:
            omitted_count+=1
    if omitted_count>0:
        print("{} timestamps omitted due to being too close to the start/end of the video, shorten baseline/posttime parameters to reinclude them.".format(omitted_count))

    #if not all timestamps are excluded
    if len(excerpts):
        #make cutout-average per frame
        aligned_video = np.array(excerpts).mean(axis=0)
        #bin the resulting video if needed (in space, not time)
        if bin_factor>1:
            aligned_video = space_bin(aligned_video,bin_factor)
        #apply gaussian smoothing if needed (both space AND time)
        if gaussian_smoothing is not None:
            aligned_video = gaussian_filter(aligned_video, gaussian_smoothing)


        return aligned_video



def z_score_trace(trace: np.ndarray, z_scoring_interval:tuple=None, gaussian_smoothing = None):
    '''
    Perform z-scoring of 1D array

    # Parameters:

    trace: array-like to z-score

    z_scoring_interval: time interval (in points) from which to calculate mean and standard deviation used for z-scoring of the whole trace. Default: the whole trace.

    gaussian_smoothing: kernel of gaussian filter to perform on the resulted z-score. Default: None, no filtering.

    # Returns:

    z-scored array
    '''

    #if interval is not given, take the whole trace
    if z_scoring_interval is None:
        z_scoring_interval = (0, len(trace))

    #calculate standard deviation
    std = trace[z_scoring_interval[0]:z_scoring_interval[1]].std(axis=0)
    #get z-scored trace
    z_trace = (trace - trace[z_scoring_interval[0]:z_scoring_interval[1]].mean(axis=0))/std
    #perform gaussian filtering if needed
    if gaussian_smoothing is not None:
        z_trace = gaussian_filter(z_trace, gaussian_smoothing)

    return z_trace
 


def bin_trace(trace:np.ndarray, binwidth=1, just_smooth=False):
    '''
    Perform binning of the 1D trace or time-bin the video (Reduces number of points by binwidth)

    #Parameters:

    trace: array-like to perform binning on

    binwidth: width (in points) of individual bin. With binwidth=n, average of every n points from original trace produces 1 point in the results. Default: 1 (no binning)

    just_smooth: set to True to perform smoothing instead of binning (performs rolling average, number of points in the resulting trace equals to the original). Default: False.

    # Returns:

    Binned array
    '''

    if binwidth>1:
        numpnts = (len(trace)//binwidth) *binwidth
        trace = np.insert(trace, 0 , [trace[0] for _ in range(binwidth)])
        trace = np.append(trace, [trace[-1] for _ in range(binwidth)])
        new_trace = trace.copy()
        
        for i in range(1,binwidth):
            new_trace+=np.roll(trace,-i)
        if just_smooth:
            return np.roll(new_trace/binwidth,binwidth//2)[binwidth:-binwidth]
        else:
            return new_trace[binwidth:-binwidth][0:numpnts:binwidth]/binwidth
    else:
        return trace
    
def space_bin(video, bin:int=2):
    '''
    Perform spatial binning of the video or individual frame. (Reduces number of points by binwidth)

    # Parameters:

    video: array-like, either a frame (2D array) or a sequence of frames (3D array, with the first dimention being time) to bin

    bin: binwidth, with bin=n, perfroms averaging in n x n bins. 

    # Returns:

    Space-binned image/video
    '''
    if bin<2:
        return video
    binrate = bin
    binned_video = video.copy()
    if len(video.shape)>2:
        for i in range(1,bin):
            binned_video+=np.roll(binned_video,-i,axis=1)
            binned_video+= np.roll(binned_video,-i,axis=2)  
        return binned_video[:,::binrate,::binrate]/(bin**2)
    else:
        for i in range(1,bin):
            binned_video+=np.roll(binned_video,-i,axis=0)
            binned_video+= np.roll(binned_video,-i,axis=1)  
        return binned_video[::binrate,::binrate]/(bin**2)   



def extract_response_parameters(trace:pd.DataFrame, 
                                response_type="mean",
                                no_resp_thresh:float=0, 
                                subtract_baseline=False,
                                baseline_time_interval:tuple=None,
                                response_time_interval:tuple=None,
                                gaussian_smoothing:float=0,
                                plateau_thresh:float=0.9,
                                tau_range:float = None,
                                save_figure:str=None,
                                show_figure=False)-> pd.DataFrame:
    '''
    Extract various parameters of the time-aligned response of continuous variable (e.g. dF/F, z-score, frequency etc.), such as mean value, peak, latency, tau of decay and plateau duration. 
    
    # Parameters:

    trace: 

    response_type: type of response to evaluate, either "mean" or "peak"
    
    no_resp_thresh: threshold of response below which it is considered a non-response. Default: 0

    subtract_baseline: if average of baseline needs to be subtracted from the response, True or False. Defalut: False.

    baseline_time_interval: time interval according to trace index in which to calculate the average value during baseline (e.g. (-1,0) to take 1 second before the event).
    Default - None, takes all time points before the event onset (before index 0).

    response_time_interval: time interval according to trace index in which to characterize the response (e.g. (0,2) to take 2 second after the event). Default - None, takes all time points
    after the event onset (after index 0).

    gaussian_smoothing: kernel of the gaussian filter to perform on the original trace before calculating tau of decay and latency of the response.

    plateau_thresh: fraction of the peak above which the response is still considered part of the plateau. For example with plateau_thresh=0.5, function will output duration that response 
    was above half of response peak, in other words, a half-width.

    tau_range: time interval according to trace index, to take into consideration when calculating tau of decay. Default: None, automatically takes interval from peak to the point when 
    value falls below 50% of peak for the first time.

    save_figure: full path (including filename) where to save the resulting figure (e.g. "C:\\User\\Documents\\results.pdf"). Default: None - don't save the figure.

    show_figure: display extracted results, with peak and fitted decay for each response, True or False, Default: False.
    '''
    from matplotlib.axes import Axes
    from scipy.optimize import curve_fit
    
    def extract_response_parameters_1d(trace:pd.Series,
                                       response_type="mean",
                                       no_resp_thresh:float=0,
                                       subtract_baseline=False,
                                       baseline_time_interval:tuple=None,
                                       response_time_interval:tuple=None,
                                       gaussian_smoothing:float=0,
                                       plateau_thresh:float=0.9,
                                       tau_range:float = None,
                                       ax:Axes=None):

        sampling = 1/(trace.index[1]-trace.index[0])
        resp={}
        baseline = trace[trace.index[np.where((trace.index>=baseline_time_interval[0]) & (trace.index<=baseline_time_interval[1]))]].mean()
        #print(baseline)

        if subtract_baseline:
            trace-=baseline

        #extract mean
        if response_type=="mean":
            resp["mean"] = trace[trace.index[np.where((trace.index>=response_time_interval[0]) & (trace.index<=response_time_interval[1]))]].mean()

        #extract peak
        elif response_type=="peak":
            resp["peak"] = trace[trace.index[np.where((trace.index>=response_time_interval[0]) & (trace.index<=response_time_interval[1]))]].max()

        resp[f"{response_type}_above_thresh"] = np.nan if resp[f"{response_type}"]-baseline< no_resp_thresh else resp[f"{response_type}"]

        if ax is not None:
            ax.plot(trace)
            ax.plot([baseline_time_interval[0],baseline_time_interval[1]],[baseline,baseline],color='k', linewidth=1.5)
            ax.plot([response_time_interval[0],response_time_interval[1]],[resp[response_type],resp[response_type]],color='r', linewidth=2)
            ax.axvline(x=0, color='k', linestyle='dashed', linewidth=0.5)

        if resp[f"{response_type}_above_thresh"] is np.nan:
            resp["latency"]=np.nan
            resp["time_to_peak"]=np.nan
            resp["tau_decay"]=np.nan
            resp["plateau_dur"]=np.nan
            resp["0.5 decay"]=np.nan
        else:
            #get peak position
            peak = trace[(trace.index>=response_time_interval[0]) & (trace.index<=response_time_interval[1])].max() - baseline
            peak_loc = trace[(trace.index>=response_time_interval[0]) & (trace.index<=response_time_interval[1])].idxmax()

            #smooth trace
            if gaussian_smoothing:
                trace.loc[:] = gaussian_filter1d(trace, gaussian_smoothing)

            #extract latency
            resp["latency"] = get_response_latency(trace, response_time_interval, baseline_time_interval=None)
            if ax is not None:
                ax.plot([resp["latency"],resp["latency"]],[0,resp["mean"]],color='g', linestyle='dashed', linewidth=1)

            
            if ax is not None:
                ax.plot(trace, linestyle='dashed')
            #extract latency
            peak_loc = trace[(trace.index>=response_time_interval[0]) & (trace.index<=response_time_interval[1])].idxmax()
            resp["time_to_peak"] = peak_loc
            if ax is not None:
                ax.plot([peak_loc],[peak+baseline],color='b', marker="o", linewidth=0.5)
            peak = trace[(trace.index>=response_time_interval[0]) & (trace.index<=response_time_interval[1])].max()
            trace-=baseline
            trace/=(peak-baseline)

            # resp["latency"] = trace.index[np.where((trace.values<0.2) & (trace.index<=peak_loc))[0][-1]+1]
            # if ax is not None:
            #     ax.plot([resp["latency"],resp["latency"]],[0,resp["mean"]],color='g', linestyle='dashed', linewidth=0.5)
            #extract plateau duration
            try:
                plateau_from = trace.index[np.where((trace.values<plateau_thresh) & (trace.index<=peak_loc))][-1]
                plateau_to = trace.index[np.where((trace.values<plateau_thresh) & (trace.index>=peak_loc))][0]
                resp["plateau_dur"] = plateau_to - plateau_from
            except:
                resp["plateau_dur"] = np.nan

            #extract tau decay

            # Curve fitting function
            def fit_func(x, a,b,c):
                nonlocal baseline
                return np.clip(b*np.exp(-(x-c)/a),0,1)
            
            if tau_range is None:
                fit_to = peak_loc+6/sampling

                
                diff_trace = trace.diff()

                while trace[trace.index<fit_to].iloc[-1]>-0.1 and diff_trace[trace.index<fit_to].iloc[-1]<0 and fit_to<trace.index[-1]:
                    fit_to+=1/sampling

                #fit_to = trace.index[np.where((trace.values>=0) & (trace.index>=peak_loc))][-1]
                #print(peak_loc, fit_to)
            else:
                fit_to = trace.index[np.where((trace.index<=tau_range) & (trace.index>=peak_loc))][-1]
            if len(trace[(trace.index>=peak_loc) & (trace.index<=fit_to)])>10:
                fit_trace = trace[peak_loc:fit_to]
            else:
                fit_trace = trace[peak_loc:].iloc[:10]
            
            try:
                params = curve_fit(fit_func, fit_trace.index.values, fit_trace.values, [1,2,0])
                if params[1][0,0]<5:
                    #print(params[0])
                    resp["tau_decay"]=params[0][0]
                    if ax is not None:
                        ax.plot(fit_trace.index,[fit_func(i,params[0][0],params[0][1],params[0][2])*peak for i in fit_trace.index], linewidth=2, color='k', linestyle='dashed')
                else:
                    resp["tau_decay"]=np.nan
                
            except:
                resp["tau_decay"]=np.nan

        return pd.DataFrame(resp, index=[0])


    if response_time_interval is None:
        response_time_interval = (0,trace.index[-1])
    else:
        trace.index = trace.index.astype(float)
        response_time_interval = np.clip(response_time_interval,trace.index[0],trace.index[-1])
    
    if baseline_time_interval is None:
        baseline_time_interval = (trace.index[0],0)
    else:
        baseline_time_interval = np.clip(baseline_time_interval,trace.index[0],trace.index[-1])

    if len(trace.shape)==1:
        fig = plt.figure(figsize=(3,3))
        ax = fig.add_subplot(111)
        res = extract_response_parameters_1d(trace.copy(), 
                                             response_type, 
                                             no_resp_thresh, 
                                             subtract_baseline, 
                                             baseline_time_interval, 
                                             response_time_interval, 
                                             gaussian_smoothing, 
                                             plateau_thresh,
                                             tau_range,
                                             ax=ax)
        sns.despine()
        fig.show
        if save_figure is not None:
            fig.savefig(save_figure)
        if not show_figure:
            plt.close(fig)
        return res
    
    else:

        res_list = []
        nrows = max(2,math.ceil(np.sqrt(trace.shape[1])))
        ncols = max(2,math.ceil(trace.shape[1]/nrows))
        fig,axes = plt.subplots(nrows,ncols,figsize=(2*nrows,2*ncols))
        ax_counter = 0
        for roi in trace:
            res = extract_response_parameters_1d(trace[roi].copy(), 
                                                 response_type, 
                                                 no_resp_thresh, 
                                                 subtract_baseline, 
                                                 baseline_time_interval, 
                                                 response_time_interval, 
                                                 gaussian_smoothing, 
                                                 plateau_thresh,
                                                 tau_range,
                                                 ax=axes[ax_counter//ncols, ax_counter%ncols])
            res_list.append(res)
            ax_counter+=1

        result = pd.concat(res_list)
        result.index=trace.columns
        

        ax_counter = 0
        for roi in trace:
            axes[ax_counter//ncols, ax_counter%ncols].yaxis.set_major_locator(plt.MaxNLocator(4))
            axes[ax_counter//ncols, ax_counter%ncols].set_title(f"{roi}: {result.loc[roi,response_type]:.2f} resp.", fontsize=6)
            #axes[ax_counter//ncols, ax_counter%ncols].set_ylim((-2*result[f"{response_type}_above_thresh"].median(skipna=True),4*result[f"{response_type}_above_thresh"].median(skipna=True)))
            axes[ax_counter//ncols, ax_counter%ncols].tick_params(axis="y", labelsize=5)
            axes[ax_counter//ncols, ax_counter%ncols].spines['bottom'].set_position('zero')
            ax_counter+=1

        sns.despine()
        #fig.show
        if save_figure is not None:
            from scipy.stats import ttest_1samp
            res_to_save = result.T.copy()
            av= res_to_save.mean(axis=1)
            sd= res_to_save.std(axis=1)
            sem= res_to_save.sem(axis=1)
            reliability= 1-res_to_save.isna().sum(axis=1)/len(res_to_save.columns)
            significance = res_to_save.apply(lambda x: ttest_1samp(x.dropna(),0)[1] if x.count() > 1 else np.nan, axis=1)
            res_to_save["average"]=av
            res_to_save["std"]=sd
            res_to_save["sem"]=sem
            res_to_save["reliability"]=reliability
            res_to_save["significance"]=significance
            res_to_save.to_csv(save_figure.replace(".pdf",".csv"))
            fig.savefig(save_figure)
        if not show_figure:
            plt.close(fig)
        return result



def get_response_latency(trace:pd.Series, response_time_interval:tuple, baseline_time_interval:tuple=None, threshold = 0.2)->float:
    if type(trace) is np.ndarray:
        trace = pd.Series(trace)
    else:
        try:
            trace.index = trace.index.astype(float)
        except:
            raise ValueError("Trace index must be convertible to float.")
    
    if baseline_time_interval is None:
        baseline_time_interval = (trace.index[0],response_time_interval[0])

    baseline = trace[trace.index[np.where((trace.index>=baseline_time_interval[0]) & (trace.index<=baseline_time_interval[1]))]].mean()
    trace = trace-baseline
    response = trace[trace.index[np.where((trace.index>=response_time_interval[0]) & (trace.index<=response_time_interval[1]))]].mean()
    if response<0:
        trace*=-1
    trace=trace/trace[trace.index[np.where((trace.index>=response_time_interval[0]) & (trace.index<=response_time_interval[1]))]].max()

    #find the first time point where response is above threshold
    if trace[trace.index>=response_time_interval[0]].values[0]<=threshold:
        latency = trace.index[np.where((trace.values>threshold) & (trace.index>=response_time_interval[0]))]

        if len(latency)>0:
            latency = latency[0]
        else:
            latency = np.nan
    #or find the last time point where response is below threshold
    else:
        latency = trace.index[np.where((trace.values<threshold) & (trace.index<response_time_interval[0]))]
        if len(latency)>0:
            latency = latency[-1]
        else:
            latency = np.nan

    return latency


def calculate_response_statistics(response_data_table:pd.DataFrame,
                                  response_type:str="mean",
                                  groups:pd.Series=None,
                                  save_figure:str=None,
                                  show_figure=False)->pd.DataFrame:
    '''
    Extract statistical parameters from the results of 

    # Parameters:

    response_data_table: DataFrame, result of running the *extract_response_parameters* function

    response_type: type of extracted response, "mean" or "peak", Default: "mean"

    groups: a column of labels same length as the input table. If provided, response statistics are calculated 

    save_figure: a full path to save the graphical representation of results. Default: None - does not save the figure

    show_figure: display a figure with results of statistical analysis.

    # Returns: 

    A table with computed means, standard deviations, SEMs, reliabilities and statistical significances of response (split by group if group is given).
    '''

    response_data_table = response_data_table.copy()
    cols = response_data_table.columns
    stats = {}
    if groups is not None:
        response_data_table["gr"] = groups.values
        response_data_table = response_data_table.groupby("gr")

    stats[response_type+"_average"] = response_data_table[response_type].mean()
    stats[response_type+"_std"] = response_data_table[response_type].std()
    stats[response_type+"_sem"] = response_data_table[response_type].sem()

    stats[response_type+"_above_thresh_average"] = response_data_table[response_type+"_above_thresh"].mean()
    stats[response_type+"_above_thresh_std"] = response_data_table[response_type+"_above_thresh"].std()
    stats[response_type+"_above_thresh_sem"] = response_data_table[response_type+"_above_thresh"].sem()

    if "latency" in cols:
        stats["latency_average"] = response_data_table["latency"].mean()
        stats["latency_std"] = response_data_table["latency"].std()
    if "tau_decay" in cols:
        stats["tau_decay_average"] = response_data_table["tau_decay"].mean()
        stats["tau_decay_std"] = response_data_table["tau_decay"].std()
    if "plateau_dur" in cols:
        stats["plateau_dur_average"] = response_data_table["plateau_dur"].mean()
        stats["plateau_dur_std"] = response_data_table["plateau_dur"].std()

    stats["reliability"] = response_data_table[response_type+"_above_thresh"].count() / response_data_table[response_type].count()

    if groups is None:
        stats["wilc_p_value"] = wilcoxon(response_data_table[response_type].values, np.zeros_like(response_data_table[response_type].values)).pvalue

        fig,axes=plt.subplots(1,5, figsize=(5,2))
        for i,metric in enumerate(response_data_table):
            sns.boxplot(response_data_table[metric].dropna(),ax=axes[i])
            sns.swarmplot(y=response_data_table[metric].dropna(),ax=axes[i],s=2)
        sns.despine()
        plt.tight_layout()
        if not show_figure:
            plt.close(fig)

        return pd.DataFrame(stats, index=["population"])
    else:
        stats["wilc_p_value"] = response_data_table[response_type].apply(lambda x: wilcoxon(x,np.zeros_like(x)).pvalue)
        if show_figure:
            fig,axes=plt.subplots(5,1, figsize=(len(groups.unique())//2,10))
            for i,metric in enumerate(response_data_table.obj.drop(columns="gr")):
                sns.boxplot(response_data_table.obj,y=metric, x="gr", hue='gr',ax=axes[i])
                sns.swarmplot(response_data_table.obj,y=metric,ax=axes[i],x="gr",color='k',s=2, edgecolor='w', linewidth=0.2);
            sns.despine()
            plt.tight_layout()

        return pd.DataFrame(stats)
    


#########################TST analysis functions ##############################################

def load_preprocess_TST_datasets(datasets:list[str], protocol_dur:float, num_keypoints:int, filter_optimal_freq = True, plot_psd = False)->pd.DataFrame:
    """
    Load and preprocess DeepLabCut tracking data from multiple TST (Tail Suspension Test) videos.

    This function loads CSV files containing DLC tracking data, standardizes the coordinate system and filters motion artifacts.

    Parameters
    ----------
    datasets : list[str]
        List of paths to CSV files containing DeepLabCut tracking data
    FPS : list[float] 
        List of frame rates (frames per second) for each video
    time_starts : list[float]
        List of start times (in seconds) for analysis of each video
    num_keypoints : int
        Number of tracked keypoints in the DeepLabCut output
    filter_optimal_freq : bool, optional
        Whether to automatically determine optimal frequency for motion artifact filtering.
        Default is True
    plot_psd : bool, optional
        Whether to plot power spectral density during frequency filtering.
        Default is False

    Returns
    -------
    pd.DataFrame
        Preprocessed tracking data with columns:
        - Time: timestamps
        - x/y coordinates for each keypoint
        - Velocity features for each keypoint
        Index is animal ID from video filename

    Notes
    -----
    The preprocessing steps include:
    1. Loading and standardizing coordinate data
    2. Centering coordinates relative to tail base position
    3. Filtering motion artifacts using notch filters
    4. Computing velocity features
    """
    from tqdm import tqdm
    from scipy.fft import fft, fftfreq
    from scipy.signal import find_peaks, iirnotch,filtfilt
    from scipy.signal import ShortTimeFFT
    from scipy.signal.windows import gaussian

    def filter_feature(feature_array:np.ndarray, fps = 20, filter_freq=0, Q=4, find_optimal=False, freq_from_to=(0.5,2), plot_psd=False, peak_width=(0.1,0.2)):
        if not filter_freq:
            filter_freq=0.9
        
        if find_optimal:
            g_std = 200 # standard deviation for Gaussian window in samples
            w = gaussian(1000, std=g_std, sym=True)  # symmetric Gaussian window
            #T_x, N = 1 / fps, feature_array.shape[0]
            SFT = ShortTimeFFT(w, hop=50, fs=fps, mfft=4000, scale_to='magnitude')
            Sx = SFT.stft(feature_array)
            sampling = fps/2/Sx.shape[0]
            new_fft = (abs(Sx)/abs(Sx[round(freq_from_to[0]/sampling):round(freq_from_to[1]/sampling),:]).std(axis=0)).mean(axis=1)[round(freq_from_to[0]/sampling):round(freq_from_to[1]/sampling)]
            peaks = find_peaks(new_fft, prominence=0.2, width=(peak_width[0]/sampling, peak_width[1]/sampling))
            if len(peaks[0])>0:
                filter_freq = peaks[0][np.argmax(peaks[1]["prominences"])]*sampling+freq_from_to[0]
            if plot_psd:
                fig = plt.figure(figsize=(2,2))
                plt.plot([freq_from_to[0] + i*sampling for i in range(len(new_fft))],new_fft)
                plt.gca().axvline(x=filter_freq,linestyle='dashed',linewidth=0.5, color='k')
                sns.despine()
                
        #print(filter_freq)

        b, a = iirnotch(filter_freq,Q=Q,fs=fps)
        filtered = filtfilt(b,a,feature_array)

        return filtered
    FPS=[]
    df_all = [pd.read_csv(dataset) for dataset in datasets]
    for i,df in enumerate(tqdm(df_all)):
        filename = datasets[i].split("\\")[-1]
        df_all[i].columns = ["{}_{}".format(df.iloc[0,i], df.iloc[1,i]) for i in range(len(df.columns))]
        df_all[i].rename(columns={"bodyparts_coords":"Time"},inplace=True)
        df_all[i]=df_all[i].iloc[2:,:].astype(float)
        FPS.append(df_all[i].Time.values.max()/protocol_dur)
        df_all[i].Time=(df_all[i].Time.astype(float)/FPS[i]).round(3)
        df_all[i] = df_all[i][[df.columns[0]]+df.columns[1:-1:3].tolist() + df.columns[2:-1:3].tolist()+df.columns[3::3].tolist()]
        df_all[i]["animal"] = filename.split("cropped")[0]
        df_all[i]=df_all[i].set_index("animal")
        df_all[i].loc[:,df_all[i].columns[1:1+num_keypoints]]-=df_all[i]["tail_base_x"].mean()
        df_all[i].loc[:,df_all[i].columns[1+num_keypoints:1+2*num_keypoints]]-=df_all[i]["tail_base_y"].mean()
    
    print("Done Loading")

    df_all = pd.concat(df_all)
    df_all.loc[:,df_all.columns[1+num_keypoints:1+2*num_keypoints]]*=-1


    for col in tqdm(df_all.columns[1:2*num_keypoints+1]):
        for i,animal in enumerate(df_all.index.unique()):
            df_all.loc[animal,col] = filter_feature(df_all.loc[animal,col].values,fps=FPS[i], find_optimal=filter_optimal_freq, freq_from_to=(0.6,2), peak_width=(0.01,0.3),Q=5, plot_psd=plot_psd)

    for col in tqdm(df_all.columns[1:2*num_keypoints+1]):
        for i,animal in enumerate(df_all.index.unique()):
            df_all.loc[animal,col] = filter_feature(df_all.loc[animal,col].values,fps=FPS[i], find_optimal=filter_optimal_freq, freq_from_to=(0.6,2), peak_width=(0.01,0.3),Q=5, plot_psd=plot_psd)

    print("Done Filtering")
    
    return df_all




def calc_velocities_standardize_DLC(df_all: pd.DataFrame, model_dir:str, num_keypoints=8, confidence_thresh=0)->pd.DataFrame:
    """
    Calculate velocities and standardize DeepLabCut tracking data using pre-trained scalers.

    This function computes velocities for tracked keypoints, standardizes coordinates and 
    velocity features using pre-trained standard scalers, and filters data based on tracking
    confidence.

    Parameters
    ----------
    df_all : pd.DataFrame
        DataFrame containing DeepLabCut tracking data (output of the load_preprocess_TST_datasets function) with columns:
        - Time: timestamps
        - x/y coordinates for each keypoint 
        - likelihood scores for each keypoint
    model_dir : str
        Directory path containing the pre-trained scaler models
    num_keypoints : int, optional
        Number of tracked keypoints in the DeepLabCut output.
        Default is 8
    confidence_thresh : float, optional
        Threshold for likelihood scores to filter low-confidence tracking data.
        Points below threshold are set to 0.
        Default is 0 (no filtering)

    Returns
    -------
    pd.DataFrame
        Processed tracking data with columns:
        - Time: timestamps 
        - Standardized x/y coordinates
        - Velocity features for each keypoint
        - Average velocities for front/hindpaws

    Notes
    -----
    Processing steps:
    1. Standardizes coordinates using scaler1
    2. Computes velocities using gradient method
    3. Filters velocities based on tracking confidence
    4. Standardizes all features using scaler2
    5. Computes average paw velocities
    """

    from tqdm import tqdm
    import pickle
    with open(model_dir+"Standard_scaler1_20240908.pkl",'rb') as f:
        scaler1 = pickle.load(f)
    with open(model_dir+"Standard_scaler2_20240908.pkl",'rb') as f:
        scaler2 = pickle.load(f)

    df_scaled=df_all[[f for f in df_all.columns if f.find("likelihood")==-1]].copy()
    #standardize individually
    for animal in df_all.index.unique():
        min_tail = np.percentile(df_all.loc[animal,"tail_base_y"].values, 2)
        
        for col in df_all.columns[1+num_keypoints:1+2*num_keypoints]:
            if col!="tail_base_y":
                min_snout = np.percentile(df_all.loc[animal,col].values, 2)
            else:
                min_snout = np.percentile(df_all.loc[animal,"snout_y"].values, 2)
            df_scaled.loc[animal,col] = (df_all.loc[animal,col] - np.percentile(df_all.loc[animal,col].values, 2))/(min_tail - min_snout)

    print("Calculating Velocities")
    df_scaled.loc[:,df_all.columns[1:1+2*num_keypoints]]=scaler1.transform(df_scaled.loc[:,df_all.columns[1:1+2*num_keypoints]])
    for i,col in enumerate(tqdm(df_scaled.columns[1:num_keypoints+1])):
        dx = np.gradient(df_scaled[col].rolling(1,min_periods=1,center=True).mean(),
                        df_scaled.loc[:,"Time"])
        dy = np.gradient(df_scaled.iloc[:,i+num_keypoints+1].rolling(1,min_periods=1,center=True).mean(),
                        df_scaled.loc[:,"Time"])
        dx=pd.Series(dx).rolling(3,min_periods=1,center=True).mean().values
        dy=pd.Series(dy).rolling(3,min_periods=1,center=True).mean().values

        col_name = col.split("_")[-2] if len(col.split("_"))==2 else col.split("_")[-3] + "_" + col.split("_")[-2]
        likelihood = df_all.loc[:,col_name+"_likelihood"].apply(lambda x: 0 if x<confidence_thresh else 1).values


        df_scaled.loc[:,col.split("_")[-2]+"_vel"] = np.sqrt(dy**2+dx**2) * likelihood
        df_scaled.loc[:,col.split("_")[-2]+"_yvel"] = np.abs(dy) * likelihood


    df_scaled.loc[:,df_scaled.columns[1:]]=scaler2.transform(df_scaled.loc[:,df_scaled.columns[1:]])

        
    df_scaled["hindpaw_av_vel"] = (df_scaled["lefthindpaw_vel"] + df_scaled["righthindpaw_vel"])/2
    df_scaled["hindpaw_av_yvel"] = (df_scaled["lefthindpaw_yvel"] + df_scaled["righthindpaw_yvel"])/2
    df_scaled["frontpaw_av_vel"] = (df_scaled["leftfrontpaw_vel"] + df_scaled["rightfrontpaw_vel"])/2
    df_scaled["frontpaw_av_yvel"] = (df_scaled["leftfrontpaw_yvel"] + df_scaled["rightfrontpaw_yvel"])/2

    for col in df_all[[f for f in df_all.columns if f.find("likelihood")!=-1]]:
        df_scaled[col] = df_all[col].values

    return df_scaled
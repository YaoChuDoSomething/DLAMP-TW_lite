import importlib
from datetime import datetime, timedelta
import numpy as np

import hydra
import matplotlib.pyplot as plt
from omegaconf import DictConfig, OmegaConf
from tqdm import tqdm

from src.utils import DataCompose
from visual import *


@hydra.main(version_base=None, config_path="config", config_name="predict")
def main(cfg: DictConfig) -> None:
    OmegaConf.set_struct(cfg, True)
    eval_cases = [datetime(2022, 9, 12)] # datetime(2021, 8, 7)

    # Inference
    if cfg.inference.infer_type == "ckpt":
        infer_machine = getattr(
            importlib.import_module("inference"), "BatchInferenceCkpt"
        )
    elif cfg.inference.infer_type == "onnx":
        infer_machine = getattr(
            importlib.import_module("inference"), "BatchInferenceOnnx"
        )
    infer_machine = infer_machine(cfg, eval_cases)
    infer_machine.infer()
    
    # Do the inference and save the output
    # count_loop = 0
    for eval_case in tqdm( eval_cases , desc = 'Do Inferencing' ):
        output_upper    = infer_machine.output_upper
        output_surface  = infer_machine.output_surface
        output_calender = eval_case + timedelta( hours = 1 )
        np.save( output_calender.strftime('DLAMPout_%Y-%m-%d_%H_%M_upper.npy')   , output_upper   , allow_pickle=True , fix_imports=True )
        np.save( output_calender.strftime('DLAMPout_%Y-%m-%d_%H_%M_surface.npy') , output_surface , allow_pickle=True , fix_imports=True )
        #new_output_upper   = infer_machine.output_upper
        #new_output_surface = infer_machine.output_surface
        #count_loop = count_loop + 1
        #new_datetime = eval_case + timedelta( hours = 1 )
        #print( str(count_loop) + '_' + new_datetime.strftime('%Y%m%d_%H%M') )
        # output
        #DLAMP
        # replace
        #output_upper = new_output_upper
        #output_surface = new_output_surface
    
    #new_output_upper   = infer_machine.output_upper
    #new_output_surface = infer_machine.output_surface

    # Prepare lat/lon
    data_gnrt = infer_machine.data_manager.data_gnrt
    lat, lon = data_gnrt.yield_data(
        datetime(2022, 10, 1, 0), {"Lat": ["NoRule"], "Lon": ["NoRule"]}
    )

    workflow = 'archive'
    if workflow == 'radar':
        # Plot radar
        (data_compose,) = DataCompose.from_config({"Radar": ["Surface"]})
        radar_painter = VizRadar()
        for eval_case in tqdm(eval_cases, desc="Plot radar figures"):
            all_init_times = infer_machine.showcase_init_time_list(eval_case)
            gt, pred = infer_machine.get_figure_materials(eval_case, data_compose)
            fig, ax = radar_painter.plot_mxn(lon, lat, gt, pred, grid_on=True)
            fig.savefig(
                f"./gallery/{data_compose}_{eval_case.strftime('%Y%m%d_%H%M')}_{cfg.inference.output_itv.hours}.png",
                transparent=False,
            )
            plt.close()

    if workflow == 'uv850':
        # plot wind 850
        u_compose, v_compose = DataCompose.from_config({"U": ["Hpa850"], "V": ["Hpa850"]})
        wind_painter = VizWind(u_compose.level.name)
        for eval_case in tqdm(eval_cases, desc="Plot wind figures"):
            all_init_times = infer_machine.showcase_init_time_list(eval_case)
            gt_u, pred_u = infer_machine.get_figure_materials(eval_case, u_compose)
            gt_v, pred_v = infer_machine.get_figure_materials(eval_case, v_compose)
            fig, ax = wind_painter.plot_mxn(lon, lat, gt_u, gt_v, pred_u, pred_v)
            fig.savefig(
                f"./gallery/{u_compose}_{eval_case.strftime('%Y%m%d_%H%M')}_{cfg.inference.output_itv.hours}.png",
                transparent=False,
            )
            plt.close()


if __name__ == "__main__":
    main()

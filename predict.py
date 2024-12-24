import importlib
from datetime import datetime, timedelta
import numpy as np

import hydra
import matplotlib.pyplot as plt
from omegaconf import DictConfig, OmegaConf
from tqdm import tqdm

from src.utils import DataCompose
#from visual import *

print('predict.py')
    
@hydra.main(version_base=None, config_path="config", config_name="predict")
def main(cfg: DictConfig) -> None:
    OmegaConf.set_struct(cfg, True)
    eval_cases = [datetime(2020, 5, 20)]
    #print( cfg )
    #print( eval_cases )

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

    print( cfg )
    print( eval_cases )
    #print( infer_machine )

    # Prepare lat/lon
    data_gnrt = infer_machine.data_manager.data_gnrt
    lat, lon = data_gnrt.yield_data(
        datetime(2020,  5, 20,  0,  0,  0), {"Lat": ["NoRule"], "Lon": ["NoRule"]}
        )

    #workflow = 'archive'
    #if workflow == 'radar':
        # Plot radar
    #(data_compose,) = DataCompose.from_config({"Radar": ["Surface"]})
        #radar_painter = VizRadar()
    print('---------------------')
    for eval_case in tqdm(eval_cases, desc="Extract VAR"):
        all_init_times = infer_machine.showcase_init_time_list(eval_case)
        #print( all_init_times )
        output_upp   = infer_machine.output_upper
        print( output_upp )
        print( '---' )
        output_sfc = infer_machine.output_surface

        np.save( './output_upper.npy' , output_upp )
        np.save( './output_surface.npy' , output_sfc )
        print( 'infer_machine.preslv' )
        print( infer_machine.pressure_lv )
        
        print( 'dir infer_machine' )
        print( dir( infer_machine ) )
        
        return infer_machine
        
        
        


        #print( output_upper )

        #gt, pred = infer_machine.get_infer_outputs_from_dt(eval_case, data_compose)
        #print( all_init_times )
        #infer_machine.output_upper
        #infer_machine.output_surface
        #fig, ax = radar_painter.plot_mxn(lon, lat, gt, pred, grid_on=True)
        #fig.savefig(
        #    f"./gallery/{data_compose}_{eval_case.strftime('%Y%m%d_%H%M')}_{cfg.inference.output_itv.hours}.png",
        #    transparent=False,
        #)
        #plt.close()

    #if workflow == 'uv850':
    #   # plot wind 850
    #    u_compose, v_compose = DataCompose.from_config({"U": ["Hpa850"], "V": ["Hpa850"]})
    #    wind_painter = VizWind(u_compose.level.name)
    #    for eval_case in tqdm(eval_cases, desc="Plot wind figures"):
    #        all_init_times = infer_machine.showcase_init_time_list(eval_case)
    #        gt_u, pred_u = infer_machine.get_figure_materials(eval_case, u_compose)
    #        gt_v, pred_v = infer_machine.get_figure_materials(eval_case, v_compose)
    #        fig, ax = wind_painter.plot_mxn(lon, lat, gt_u, gt_v, pred_u, pred_v)
    #        fig.savefig(
    #            f"./gallery/{u_compose}_{eval_case.strftime('%Y%m%d_%H%M')}_{cfg.inference.output_itv.hours}.png",
    #            transparent=False,
    #        )
    #        plt.close()


if __name__ == "__main__":
    main()

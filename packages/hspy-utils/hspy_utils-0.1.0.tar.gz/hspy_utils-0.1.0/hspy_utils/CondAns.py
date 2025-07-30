from IPython.lib.display import FileLink
from lmfit import Parameters

# from hspy_utils import HspyPrep
import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import IntProgress
from skimage import io, color
from skimage.metrics import structural_similarity as ssim
import matplotlib.patches as patches
import pickle
from lmfit.models import GaussianModel, ConstantModel, LorentzianModel, VoigtModel
from matplotlib.gridspec import GridSpec
import traceback
import seaborn as sns
from scipy.signal import find_peaks, peak_widths
import os
import pandas as pd
from skimage.exposure import match_histograms
from ipywidgets import FloatSlider, IntSlider, Dropdown, Button, HBox, VBox, Output, Layout, BoundedIntText, FloatText, \
    BoundedFloatText, Checkbox, interact
from IPython.display import display
import re


class CondAns:
    def __init__(self, data_dict: dict, ref, addr_file, load_mapping=False):
        self.best_r2 = None
        self.best_result = None
        self.best_model = None
        self.params_fit = None
        self.best_fit = None
        self.data_dict = data_dict
        self.ref = ref
        self.list_of_exp = list(self.data_dict.keys())

        if load_mapping:
            with open(f"{addr_mapping}/data_coordinates.pkl", "rb") as file:
                self.data_coordinates = pickle.load(file)

    def map_all_pixels(self, window_size, max_disp, ref):
        image_ref = self.data_dict[ref].get_live_scan()
        mapping_save = dict()
        mapping = ''
        for key, value in self.data_dict.items():
            value.live_scan = match_histograms(value.live_scan, image_ref)
        for key in self.data_dict.keys():
            if key == ref:
                mapping_save['ref'] = key
                continue
            mapping = CondAns.map_pixels(image_ref, self.data_dict[key].get_live_scan(), window_size=window_size,
                                         search_radius=max_disp)
            mapping_save[key] = mapping
        print(mapping_save)
        mapping_save['ref'] = list(mapping.keys())
        with open("data_coordinates.pkl", "wb") as file:
            pickle.dump(mapping_save, file)
            self.data_coordinates = mapping_save

    def plot_all_pixels(self, figsize=(20, 10), save=False, filename=None, x_pixel=0, y_pixel=0, show_plots=False):
        '''

        :param show_plots: 
        :param figsize:
        :param save:
        :param filename:
        :param x_pixel:
        :param y_pixel:
        '''

        shape_image = self.data_dict[self.ref].get_live_scan().shape
        for key_coord in self.data_coordinates['ref']:
            key_coord = (key_coord[0] + y_pixel, key_coord[1] + x_pixel)
            if key_coord[1] > shape_image[1] or key_coord[0] > shape_image[0]:
                continue
            print(key_coord[0], key_coord[1])

            ax_main, image_axes, colors = self.__setup_plotting(figsize,
                                                                self.data_dict[self.ref].get_wavelengths()[::-1])
            coord_x, coord_y = self.__setup_coordinations(key_coord, image_axes)

            for idx, (temp, color, x, y) in enumerate(zip(list(self.data_dict.keys()), colors, coord_x, coord_y)):
                if x == 0 and y == 0:
                    continue
                wavelengths = self.data_dict[temp].get_wavelengths()[::-1]
                intensity = self.data_dict[temp].get_numpy_spectra()[y][x][::-1]
                ax_main.plot(wavelengths, intensity, color=color, linewidth=2, label=f'{temp} nA')

            if save:
                folder = f'./{filename}'
                os.makedirs(folder, exist_ok=True)
                plt.savefig(f'{folder}/{key_coord[0]}_{key_coord[1]}.png', dpi=300)

            if show_plots:
                plt.show()
                plt.close()

    def plot_all_pixels_with_fitting(self, figsize=(20, 10), save=False, filename=None, fit_func=VoigtModel,
                                     peaks='Automatic', max_peaks=3, x_pixel=0, y_pixel=0, height=100, prominence=1,
                                     distance=5, show_plots=False):
        '''

        :param show_plots:
        :param x_pixel:
        :param y_pixel:
        :param prominence:
        :param height:
        :param distance:
        :param max_peaks:
        :param figsize:
        :param save:
        :param filename:
        :param fit_func: define a fit function which the data can be fitted with thats
        :param peaks: The number of peaks will be defined automatically; however, you can define estimations about the number of peaks that you may have.
        :return:
        '''

        shape_image = self.data_dict[self.ref].get_live_scan().shape
        for key_coord in self.data_coordinates['ref']:
            key_coord = (key_coord[0] + y_pixel, key_coord[1] + x_pixel)
            if key_coord[1] > shape_image[1] or key_coord[0] > shape_image[0]:
                continue

            print(key_coord[0], key_coord[1])

            ax_main, image_axes, colors = self.__setup_plotting(figsize,
                                                                self.data_dict[self.ref].get_wavelengths()[::-1])
            coord_x, coord_y = self.__setup_coordinations(key_coord, image_axes)

            for idx, (temp, color, x, y) in enumerate(zip(list(self.data_dict.keys()), colors, coord_x, coord_y)):
                if x == 0 and y == 0:
                    continue
                wavelengths = self.data_dict[temp].get_wavelengths()[::-1]
                intensity = self.data_dict[temp].get_numpy_spectra()[y][x][::-1]
                ax_main.plot(wavelengths, intensity, color=color, linewidth=2, label=f'{temp} nA')
                if peaks == 'Automatic':
                    self.__peak_fitting_auto(intensity, wavelengths, height, prominence, distance, max_peaks, fit_func)
                    ax_main.plot(wavelengths, self.best_result.best_fit, '--', color=color, linewidth=2,
                                 label=f'R²={self.best_r2:.4f}')
                if peaks == 'Manual':
                    pass

            if save:
                folder = f'./{filename}'
                os.makedirs(folder, exist_ok=True)
                plt.savefig(f'{folder}/{key_coord[0]}_{key_coord[1]}_fitted.png', dpi=300)

            if show_plots:
                plt.show()
                plt.close()

    def single_exp_run_plot(self, exp_key, figsize=(20, 10), save=False, show_plots=False, filename=None, x_pixel=0,
                            y_pixel=0):

        shape_image = self.data_dict[self.ref].get_live_scan().shape

        for key_coord in self.data_coordinates[exp_key]:
            key_coord = (key_coord[0] + y_pixel, key_coord[1] + x_pixel)
            if key_coord[1] > shape_image[1] or key_coord[0] > shape_image[0]:
                continue
            print(key_coord[0], key_coord[1])

            x = key_coord[1]
            y = key_coord[0]

            wavelengths = self.data_dict[exp_key].get_wavelengths()[::-1]
            intensity = self.data_dict[exp_key].get_numpy_spectra()[y][x][::-1]

            ax_main, ax_image = self.__setup_plotting_single_image(figsize, wavelengths)
            ax_main.plot(wavelengths, intensity, color='red', linewidth=2)
            CondAns.__plot_image_with_rect(ax_image, self.data_dict[exp_key].get_live_scan(),
                                           (x, y), exp_key)

            if save:
                folder = f'./{filename}'
                os.makedirs(folder, exist_ok=True)
                plt.savefig(f'{folder}/{key_coord[0]}_{key_coord[1]}_fitted.png', dpi=300)

            if show_plots:
                plt.show()
                plt.close()

    def single_exp_plot(self, exp_key, x_pixel, y_pixel, figsize=(20, 10), save=False, show_plots=False, filename=None):

        shape_image = self.data_dict[self.ref].get_live_scan().shape

        # for key_coord in self.data_coordinates[exp_key]:
        #     key_coord = (key_coord[0] + y_pixel, key_coord[1] + x_pixel)
        #     if key_coord[1] > shape_image[1] or key_coord[0] > shape_image[0]:
        #         continue
        #     print(key_coord[0], key_coord[1])

        x = x_pixel
        y = y_pixel

        wavelengths = self.data_dict[exp_key].get_wavelengths()[::-1]
        intensity = self.data_dict[exp_key].get_numpy_spectra()[y][x][::-1]

        ax_main, ax_image = self.__setup_plotting_single_image(figsize, wavelengths)
        ax_main.plot(wavelengths, intensity, color='red', linewidth=2)
        CondAns.__plot_image_with_rect(ax_image, self.data_dict[exp_key].get_live_scan(),
                                       (x, y), exp_key)

        # if save:
        #     folder = f'./{filename}'
        #     os.makedirs(folder, exist_ok=True)
        #     plt.savefig(f'{folder}/{key_coord[0]}_{key_coord[1]}_fitted.png', dpi=300)

        # if show_plots:
        plt.show()
        # plt.close()

    def single_exp_run_fitting(self, exp_key, figsize=(20, 10), save_excel=False, filename=None, fit_func=VoigtModel,
                               peaks='Automatic', max_peaks=3, x_pixel=0, y_pixel=0, height=100, prominence=1,
                               distance=5, save_plots=False):

        shape_image = self.data_dict[self.ref].get_live_scan().shape
        params_data = []

        for key_coord in self.data_coordinates[exp_key]:
            key_coord = (key_coord[0] + y_pixel, key_coord[1] + x_pixel)
            if key_coord[1] > shape_image[1] or key_coord[0] > shape_image[0]:
                continue
            print(key_coord[0], key_coord[1])

            x = key_coord[1]
            y = key_coord[0]

            wavelengths = self.data_dict[exp_key].get_wavelengths()[::-1]
            intensity = self.data_dict[exp_key].get_numpy_spectra()[y][x][::-1]

            ax_main, ax_image = self.__setup_plotting_single_image(figsize, wavelengths)
            ax_main.plot(wavelengths, intensity, color='red', linewidth=2)
            CondAns.__plot_image_with_rect(ax_image, self.data_dict[exp_key].get_live_scan(),
                                           (x, y), exp_key)

            if peaks == 'Automatic':
                self.__peak_fitting_auto(intensity, wavelengths, height, prominence, distance, max_peaks, fit_func)
                ax_main.plot(wavelengths, self.best_result.best_fit, '--', color=color, linewidth=2,
                             label=f'R²={self.best_r2:.4f}')
                try:
                    params_data.append({
                        "Key": (x, y),
                        "R^2": self.best_r2
                    })
                    for param_name, param in self.best_result.params.items():
                        params_data[-1][param_name] = param.value
                except Exception as e:
                    print("An error occurred during fitting:")
                    traceback.print_exc()

            if save_plots:
                folder = f'./{filename}'
                os.makedirs(folder, exist_ok=True)
                plt.savefig(f'{folder}/{key_coord[0]}_{key_coord[1]}_fitted.png', dpi=300)
                plt.show()
                plt.close()

            if save_excel:
                params_df = pd.DataFrame(params_data)
                params_df.to_excel(f"lmfit_parameters_{exp_key}.xlsx", index=False)

    def get_data_coordinate(self):
        return self.data_coordinates

    def __setup_plotting(self, figsize, wavelengths):
        colors = sns.color_palette('inferno', len(self.list_of_exp))
        n_images = len(self.list_of_exp)
        fig = plt.figure(figsize=figsize)
        gs = GridSpec(6, 7, figure=fig, wspace=0.1, hspace=0.2)
        ax_main = fig.add_subplot(gs[:, 0:4])
        image_axes = dict()
        n_cols = 3

        for i, (key, value) in enumerate(self.data_dict.items(), start=0):
            row = (i // n_cols) * 2
            col = 4 + (i % n_cols)
            ax_im = fig.add_subplot(gs[row:row + 2, col])
            image_axes[key] = ax_im

        ax_main.set_xlabel('Wavelength (nm)', fontsize=18, labelpad=15)
        ax_main.set_ylabel('Intensity (a.u.)', fontsize=18, labelpad=15)

        ax_main.tick_params(axis='both', which='major', labelsize=14, length=6, width=1.5)
        ax_main.tick_params(axis='both', which='minor', length=4, width=1)

        secax = ax_main.secondary_xaxis('top')
        secax.set_xlabel('Energy (eV)', fontsize=18, labelpad=15)
        secax.tick_params(axis='x', labelsize=14, length=6, width=1.5)

        wavelength_ticks = np.linspace(min(wavelengths), max(wavelengths), num=6)
        energy_ticks = np.linspace(wavelengths[0], wavelengths[-1], num=5)
        secax.set_xticks(energy_ticks)
        secax.set_xticklabels([f'{1239.84193 / wl:.2f}' for wl in energy_ticks])

        ax_main.grid(True)
        ax_main.grid(True, which='both', color='black', linestyle='--', linewidth=0.3)
        for spine in ax_main.spines.values():
            spine.set_edgecolor('black')
            spine.set_linewidth(1.5)
        ax_main.axvspan(950, 1000, color='green', alpha=0.15, label="950-1000 nm")
        ax_main.axvspan(870, 940, color='blue', alpha=0.15, label="870-940 nm")

        ax_main.legend()

        return ax_main, image_axes, colors

    def __setup_plotting_single_image(self, figsize, wavelengths):
        fig = plt.figure(figsize=figsize)
        gs = GridSpec(6, 7, figure=fig, wspace=0.1, hspace=0.2)
        ax_main = fig.add_subplot(gs[:, 0:4])
        ax_im = fig.add_subplot(gs[:, 4:])

        ax_main.set_xlabel('Wavelength (nm)', fontsize=18, labelpad=15)
        ax_main.set_ylabel('Intensity (a.u.)', fontsize=18, labelpad=15)

        ax_main.tick_params(axis='both', which='major', labelsize=14, length=6, width=1.5)
        ax_main.tick_params(axis='both', which='minor', length=4, width=1)

        secax = ax_main.secondary_xaxis('top')
        secax.set_xlabel('Energy (eV)', fontsize=18, labelpad=15)
        secax.tick_params(axis='x', labelsize=14, length=6, width=1.5)

        wavelength_ticks = np.linspace(min(wavelengths), max(wavelengths), num=6)
        energy_ticks = np.linspace(wavelengths[0], wavelengths[-1], num=5)
        secax.set_xticks(energy_ticks)
        secax.set_xticklabels([f'{1239.84193 / wl:.2f}' for wl in energy_ticks])

        ax_main.grid(True)
        ax_main.grid(True, which='both', color='black', linestyle='--', linewidth=0.3)
        for spine in ax_main.spines.values():
            spine.set_edgecolor('black')
            spine.set_linewidth(1.5)
        ax_main.axvspan(950, 1000, color='green', alpha=0.15, label="950-1000 nm")
        ax_main.axvspan(870, 940, color='blue', alpha=0.15, label="870-940 nm")

        ax_main.legend()

        return ax_main, ax_im

    def __setup_coordinations(self, key_coord, image_axes):
        coord_x = []
        coord_y = []
        for i in self.data_coordinates.keys():
            if i == 'ref':
                coord_x.append(key_coord[1])
                coord_y.append(key_coord[0])
                CondAns.__plot_image_with_rect(image_axes[self.ref], self.data_dict[self.ref].get_live_scan(),
                                               key_coord, self.ref)
            else:
                temp_coord = self.data_coordinates[i].get(key_coord)
                if temp_coord is None:
                    temp_coord = (0, 0)
                coord_x.append(temp_coord[1])
                coord_y.append(temp_coord[0])
                CondAns.__plot_image_with_rect(image_axes[i], self.data_dict[i].get_live_scan(),
                                               temp_coord, i)

        return coord_x, coord_y

    def __peak_fitting_auto(self, intensity, wavelengths, height, prominence, distance, max_peaks, fit_func):

        self.best_r2 = None
        self.best_result = None
        self.best_model = None
        self.params_fit = None
        self.best_fit = None

        peaks_indices, properties = find_peaks(intensity, height=height, prominence=prominence, distance=distance)
        peak_positions = wavelengths[peaks_indices]
        peak_heights = intensity[peaks_indices]

        sorted_idx = np.argsort(peak_heights)[::-1]
        sorted_idx = sorted_idx[:max_peaks]
        peak_positions = peak_positions[sorted_idx]
        peak_heights = peak_heights[sorted_idx]

        r2_list = []
        params_list = []
        models = []
        results = []

        model = ConstantModel(prefix='bkg_')
        params = model.make_params(bkg_c=0)
        flag = False
        for m, (pos, height) in enumerate(zip(peak_positions, peak_heights)):
            prefix = f'g{m}_'
            gauss = fit_func(prefix=prefix)
            model += gauss
            params.update(gauss.make_params())
            params[f'{prefix}amplitude'].set(value=height, min=0)
            params[f'{prefix}center'].set(value=pos)
            params[f'{prefix}sigma'].set(value=1, min=0.1)

            result = model.fit(intensity, params, x=wavelengths)

            ss_total = np.sum((intensity - np.mean(intensity)) ** 2)
            ss_residual = np.sum(result.residual ** 2)
            r_squared = 1 - (ss_residual / ss_total)
            r2_list.append(r_squared)
            params_list.append(result.params)
            models.append(model)
            results.append(result)

            print(f"Using {m + 1} peak(s): R² = {r_squared:.4f}")

            if len(peak_positions) == 1:
                self.best_fit = m
                self.params_fit = params_list[-1]
                self.best_model = models[-1]
                self.best_result = results[-1]
                self.best_r2 = r2_list[-1]
                flag = True
                break

            # if len(r2_list) == len(peak_positions):
            r2_temp = sorted(r2_list, reverse=True)
            for i in range(len(r2_temp) - 1):
                if r2_temp[i] - r2_temp[i + 1] > 0.005:
                    index = r2_list.index(r2_temp[i])
                    self.best_fit = index
                    self.params_fit = params_list[index]
                    self.best_model = models[index]
                    self.best_result = results[index]
                    self.best_r2 = r2_list[index]
                    flag = True
                    if len(r2_list) == len(peak_positions):
                        break

        if flag == False:
            self.best_fit = 1
            self.params_fit = params_list[0]
            self.best_model = models[0]
            self.best_result = results[0]
            self.best_r2 = r2_list[0]

            # if r2_list[-1] - r2_list[-2] < 0.007:
            #     self.best_fit = m
            #     self.params_fit = params_list[-2]
            #     self.best_model = models[-2]
            #     self.best_result = results[-2]
            #     self.best_r2 = r2_list[-2]
            # else:
            #     self.best_fit = m + 1
            #     self.params_fit = params_list[-1]
            #     self.best_model = models[-1]
            #     self.best_result = results[-1]
            #     self.best_r2 = r2_list[-1]

            # if len(r2_list) > 1 and r2_list[-1] - r2_list[-2] < 0.007 and r2_list[-2] > 0.99:
            #     self.best_fit = m
            #     self.params_fit = params_list[-2]
            #     self.best_model = models[-2]
            #     self.best_result = results[-2]
            #     self.best_r2 = r2_list[-2]
            #     # break

    def interactive_peak_fit(self, exp_key, start_row=0, start_col=0):
        """
        Interactive peak fitting with Prev/Next + direct-entry for row & col,
        plus a button to fit all spectra, store and list those below an R² threshold,
        with a progress bar for the Fit All operation, and export fit data to Excel.
        Optionally exclude low-R² spectra from the exported file.
        """
        from ipywidgets import IntProgress
        import pandas as pd
        from IPython.display import display, FileLink

        exp_dropdown = Dropdown(
            options=list(self.data_dict.keys()),
            value=exp_key,
            description='Dataset:',
            layout=Layout(align_items='center', margin='0 10px')
        )
        # pull out data
        data = self.data_dict[exp_key].get_numpy_spectra()
        wavelengths = self.data_dict[exp_key].get_wavelengths()
        n_rows, n_cols = data.shape[0], data.shape[1]
        image_scan = self.data_dict[exp_key].get_live_scan()

        # init storage
        self.last_low_r2 = []
        self.last_fit_results = []

        # state
        row, col = start_row, start_col
        max_row, max_col = data.shape[0] - 1, data.shape[1] - 1

        desc_w = '80px'

        field_layout = Layout(width='200px', height='40px')

        row_entry = BoundedIntText(
            value=row,
            min=0,
            max=max_row,
            description='Row:',
            style={'description_width': desc_w},
            layout=field_layout
        )

        col_entry = BoundedIntText(
            value=col,
            min=0,
            max=max_col,
            description='Col:',
            style={'description_width': desc_w},
            layout=field_layout
        )

        # nav buttons
        btn_prev_row = Button(description='←', tooltip='Previous row', layout=Layout(width='50px'))
        btn_next_row = Button(description='→', tooltip='Next row', layout=Layout(width='50px'))
        btn_prev_col = Button(description='←', tooltip='Previous col', layout=Layout(width='50px'))
        btn_next_col = Button(description='→', tooltip='Next col', layout=Layout(width='50px'))

        out = Output(layout=Layout(border='1px solid gray'))

        w_height = FloatSlider(value=0.1, min=0.0, max=np.max(data), step=0.01, description='height',
                               continuous_update=False)
        w_prominence = FloatSlider(value=0.1, min=0.0, max=20, step=0.01, description='prominence',
                                   continuous_update=False)
        w_distance = FloatSlider(value=1.0, min=0.0, max=40, step=1.0, description='distance', continuous_update=False)
        w_max_peaks = IntSlider(value=3, min=1, max=10, step=1, description='max_peaks', continuous_update=False)
        w_fit_func = Dropdown(
            options=[('Gaussian', GaussianModel), ('Lorentzian', LorentzianModel), ('Voigt', VoigtModel)],
            description='fit_func')
        btn_fit = Button(description='Fit Peaks', button_style='primary')

        # Fit All controls
        threshold_entry = BoundedFloatText(value=0.9, min=0.0, max=1.0, step=0.01, description='R² thresh:')
        include_low_chk = Checkbox(value=True, description='Include low R² in Excel')
        btn_fit_all = Button(description='Fit All', button_style='warning')

        def update_display(change=None):
            nonlocal row, col
            row, col = row_entry.value, col_entry.value
            intensity = data[row, col]
            with out:
                out.clear_output(wait=True)
                self.__peak_fitting_auto(intensity=intensity, wavelengths=wavelengths,
                                         height=w_height.value, prominence=w_prominence.value,
                                         distance=w_distance.value, max_peaks=w_max_peaks.value,
                                         fit_func=w_fit_func.value)
                # 2) create side‐by‐side plots
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

                # — left: spectrum + fit
                ax1.plot(wavelengths, intensity, label='data', markersize=3)
                best = self.best_model.eval(x=wavelengths, params=self.params_fit)
                ax1.plot(wavelengths, best, '-', label=f'best fit (R²={self.best_r2:.3f})')
                names = []
                for name, comp in self.best_model.eval_components(x=wavelengths, params=self.params_fit).items():
                    names.append(name)
                    if name != 'bkg_':
                        ax1.plot(wavelengths, comp, '--', label=name)
                ax1.set(xlabel='Wavelength', ylabel='Intensity',
                        title=f'{exp_key} @ (row={row},col={col})')
                ax1.legend()

                if image_scan is not None:
                    ax2.imshow(image_scan, cmap='gray')
                    ax2.axis('off')
                    ax2.set_title('Sample map')
                    img_h, img_w = image_scan.shape[:2]
                    cell_w = img_w / n_cols
                    cell_h = img_h / n_rows
                    x0 = (col * cell_w) - (cell_w / 2)
                    y0 = (row * cell_h) - (cell_h / 2)
                    from matplotlib.patches import Rectangle
                    rect = Rectangle((x0, y0), cell_w, cell_h,
                                     linewidth=2, edgecolor='red', facecolor='none')
                    ax2.add_patch(rect)
                else:
                    ax2.text(0.5, 0.5, 'No map image\nprovided',
                             ha='center', va='center', fontsize=12)
                    ax2.axis('off')

                plt.tight_layout()
                plt.show()

                params = self.params_fit

                # decide the order you want suffixes printed in
                suffix_order = ['amplitude', 'center', 'sigma', 'fwhm']

                # 1) collect all the prefixes (e.g. 'g0', 'g1', 'bkg')
                prefixes = sorted({name.split('_', 1)[0] for name in params.keys()})

                print(f"Fit parameters for {exp_key} @ (row={row},col={col}):")
                print(f"  overall R² = {self.best_r2:.4f}")
                print("  detailed parameters:")

                for pfx in prefixes:
                    print(f"  {pfx}_:")
                    for suf in suffix_order:
                        full = f"{pfx}_{suf}"
                        if full in params:
                            par = params[full]
                            print(f"    {suf:<9} = {par.value:10.3f}  ± {par.stderr:.3f}" if par.stderr else
                                  f"    {suf:<9} = {par.value:10.3f}")
                    extras = sorted(
                        name.split('_', 1)[1]
                        for name in params.keys()
                        if name.startswith(pfx + '_') and name.split('_', 1)[1] not in suffix_order
                    )
                    for suf in extras:
                        par = params[f"{pfx}_{suf}"]
                        print(f"    {suf:<9} = {par.value:10.3f}")

        btn_fit.on_click(lambda _: update_display())

        def fit_all_callback(_):
            self.last_low_r2.clear()
            self.last_fit_results.clear()
            thresh = threshold_entry.value
            total = data.shape[0] * data.shape[1]
            progress = IntProgress(min=0, max=total, description='Fitting:')
            count = 0
            low_list = []
            with out:
                out.clear_output()
                display(progress)

                for r in range(data.shape[0]):
                    for c in range(data.shape[1]):
                        try:
                            self.__peak_fitting_auto(intensity=data[r, c], wavelengths=wavelengths,
                                                     height=w_height.value, prominence=w_prominence.value,
                                                     distance=w_distance.value, max_peaks=w_max_peaks.value,
                                                     fit_func=w_fit_func.value)
                            params = self.params_fit.valuesdict()
                            rec = {'row': r, 'col': c, 'r2': self.best_r2, 'fit_func': w_fit_func.value}
                            rec.update(params)
                            self.last_fit_results.append(rec)
                            if self.best_r2 < thresh: low_list.append((r, c, self.best_r2))
                        except Exception as e:
                            print(f"Error fitting (row={r}, col={c}): {e}")
                        count += 1
                        progress.value = count
                self.last_low_r2 = low_list
                # prepare DataFrame
                df = pd.DataFrame(self.last_fit_results)
                # filter if excluding low
                if not include_low_chk.value:
                    df = df[df['r2'] >= thresh]
                path = f'fitting_results_{exp_key}.xlsx'
                df.to_excel(path, index=False)
                # print summary
                if low_list:
                    print(f"Spectra with R² below {thresh}:")
                    for r, c, r2 in low_list: print(f"  row={r},col={c},R²={r2:.3f}")
                else:
                    print(f"All spectra have R² ≥ {thresh}.")
                print(f"\nExcel file saved to '{path}'.")
                display(FileLink(path))

        btn_fit_all.on_click(fit_all_callback)

        # navigation
        def shift_row(d):
            row_entry.value = np.clip(row_entry.value + d, 0, max_row)

        def shift_col(d):
            col_entry.value = np.clip(col_entry.value + d, 0, max_col)

        def refresh_for_new_key(new_key):
            """Re-load all of the per-key variables and reset controls."""
            nonlocal data, wavelengths, image_scan, n_rows, n_cols, max_row, max_col
            data = self.data_dict[new_key].get_numpy_spectra()
            wavelengths = self.data_dict[new_key].get_wavelengths()
            image_scan = self.data_dict[new_key].get_live_scan()
            n_rows, n_cols = data.shape[:2]
            max_row, max_col = n_rows - 1, n_cols - 1

            # update widget limits and reset position
            row_entry.max = max_row
            col_entry.max = max_col
            row_entry.value = 0
            col_entry.value = 0

            update_display()  # redraw immediately on key change

            # observer on the dropdown

        def on_key_change(change):
            if change['name'] == 'value' and change['new'] != change['old']:
                refresh_for_new_key(change['new'])

        exp_dropdown.observe(on_key_change, names='value')

        btn_prev_row.on_click(lambda _: shift_row(-1));
        btn_next_row.on_click(lambda _: shift_row(1))
        btn_prev_col.on_click(lambda _: shift_col(-1));
        btn_next_col.on_click(lambda _: shift_col(1))
        row_entry.observe(update_display, names='value');
        col_entry.observe(update_display, names='value')

        # # layout
        # row_ctrl = HBox([row_entry, btn_prev_row, btn_next_row], layout=Layout(align_items='center', margin='0 10px'))
        # col_ctrl = HBox([col_entry, btn_prev_col, btn_next_col], layout=Layout(align_items='center'))
        # ctrl = VBox([
        #     HBox([row_ctrl, col_ctrl]),
        #     HBox([w_height, w_prominence], layout=Layout(margin='10px 0')),
        #     HBox([w_distance, w_max_peaks, w_fit_func], layout=Layout(margin='10px 0')),
        #     HBox([btn_fit, threshold_entry, include_low_chk, btn_fit_all], layout=Layout(margin='10px 0'))
        # ])
        # display(VBox([ctrl, out]))
        # update_display()
        # now build the UI
        # controls = HBox([
        #     exp_dropdown,
        #     HBox([btn_prev_row, row_entry, btn_next_row]),
        #     HBox([btn_prev_col, col_entry, btn_next_col])
        # ])
        # fit_controls = HBox([w_height, w_prominence, w_distance, w_max_peaks, w_fit_func, btn_fit])
        # all_controls = HBox([threshold_entry, include_low_chk, btn_fit_all])
        #
        # display(VBox([controls, fit_controls, all_controls, out]))
        #

        row1 = exp_dropdown

        # Row 2: row/col navigator
        row_controls = HBox(
            [btn_prev_row, row_entry, btn_next_row],
            layout=Layout(
                display='flex',
                flex_flow='row nowrap',
                align_items='center',
                gap='5px'  # small CSS gap between all children
            )
        )

        col_controls = HBox(
            [btn_prev_col, col_entry, btn_next_col],
            layout=Layout(
                display='flex',
                flex_flow='row nowrap',
                align_items='center',
                gap='5px'  # small CSS gap between all children
            )
        )

        # Row 3: fit‐parameter sliders
        row5 = HBox([
            w_height, w_prominence, w_distance
        ], layout=Layout(margin='10px 10px', flex_flow='row wrap'))

        row3 = HBox([
            w_max_peaks, w_fit_func, btn_fit
        ], layout=Layout(margin='10px 10px', flex_flow='row wrap'))

        # Row 4: action buttons
        row4 = HBox([
            threshold_entry, include_low_chk, btn_fit_all
        ], layout=Layout(margin='10px 10px'))

        # === display all four rows + output below ===
        display(VBox([
            row1,
            row_controls,
            col_controls,
            row5,
            row3,
            row4,
            out
        ], layout=Layout(spacing='15px')))
        update_display()

    def interactive_peak_fit_manual(self, exp_key, start_row=0, start_col=0):
        """
        Interactive manual peak fitting with Prev/Next + direct-entry for row & col,
        plus controls to add/remove individual peak guesses (amplitude, center, sigma, function),
        collect them into a dict, and call __peak_fitting_manual.
        """
        from ipywidgets import HBox, VBox, Button, Dropdown, FloatText, BoundedIntText, Output, Layout
        import numpy as np
        import matplotlib.pyplot as plt

        field_layout = Layout(width='180px')
        label_style = {'description_width': '60px'}
        btn_layout = Layout(width='150px')
        hbox_gap = {'gap': '10px', 'margin': '5px 0'}

        self.last_low_r2 = []
        self.last_fit_results = []

        # grab your data
        data = self.data_dict[exp_key].get_numpy_spectra()
        wavelengths = self.data_dict[exp_key].get_wavelengths()
        image_scan = self.data_dict[exp_key].get_live_scan()
        n_rows, n_cols = data.shape[:2]
        max_row, max_col = n_rows - 1, n_cols - 1

        row, col = start_row, start_col
        peak_widgets = []  # list of tuples (amp_w, cen_w, sig_w, func_w)

        # —— dataset selector ——
        exp_dropdown = Dropdown(
            options=list(self.data_dict.keys()),
            value=exp_key,
            description='Dataset:',
            layout=Layout(margin='0 10px'),
            style=label_style
        )

        # —— navigation entries ——
        row_entry = BoundedIntText(
            value=row, min=0, max=max_row,
            description='Row:',
            layout=field_layout,
            style=label_style
        )
        col_entry = BoundedIntText(
            value=col, min=0, max=max_col,
            description='Col:',
            layout=field_layout,
            style=label_style
        )
        btn_prev_row = Button(description='←', layout=btn_layout)
        btn_next_row = Button(description='→', layout=btn_layout)
        btn_prev_col = Button(description='←', layout=btn_layout)
        btn_next_col = Button(description='→', layout=btn_layout)

        # —— peak controls ——
        peaks_container = VBox(layout=Layout(border='1px solid lightgray', padding='5px'))
        btn_add_peak = Button(description='Add Peak', layout=btn_layout)
        btn_remove_peak = Button(description='Remove Peak', layout=btn_layout)
        btn_fit_manual = Button(description='Fit Manual', button_style='primary', layout=btn_layout)

        out = Output(layout=Layout(border='1px solid gray'))

        def make_peak_row():
            amp = FloatText(
                value=1.0,
                description='Amp',
                layout=field_layout,
                style=label_style
            )
            amp_limit = FloatText(
                value=None,
                description='±',
                layout=field_layout,
                style=label_style
            )
            cen = FloatText(
                value=0.0,
                description='Center',
                layout=field_layout,
                style=label_style
            )
            cen_limit = FloatText(
                value=None,
                description='±',
                layout=field_layout,
                style=label_style
            )
            sig = FloatText(
                value=1.0,
                description='Sigma',
                layout=field_layout,
                style=label_style
            )
            sig_limit = FloatText(
                value=1.0,
                description='±',
                layout=field_layout,
                style=label_style
            )
            func = Dropdown(
                options=[('Gaussian', GaussianModel),
                         ('Lorentzian', LorentzianModel),
                         ('Voigt', VoigtModel)],
                description='Func',
                layout=field_layout,
                style=label_style
            )

            peak_widgets.append((amp, amp_limit, cen, cen_limit, sig, sig_limit, func))
            return HBox([amp, amp_limit, cen, cen_limit, sig, sig_limit, func], layout=Layout(**hbox_gap))

        def on_add_peak(_):
            widget_row = make_peak_row()
            peaks_container.children += (widget_row,)

        def on_remove_peak(_):
            if peak_widgets:
                peak_widgets.pop()
                peaks_container.children = peaks_container.children[:-1]

        # redraw & fit
        def update_display():
            nonlocal row, col, data, wavelengths
            row, col = row_entry.value, col_entry.value
            intensity = data[row, col]
            with out:
                out.clear_output(wait=True)
                peak_list = []
                for amp_w, amp_limit_w, cen_w, cen_limit_w, sig_w, sig_limit_w, func_w in peak_widgets:
                    peak_list.append({
                        'amplitude': amp_w.value,
                        'amplitude_limit': None if amp_limit_w.value == 0 else amp_limit_w.value,
                        'center': cen_w.value,
                        'center_limit': None if cen_limit_w.value == 0 else cen_limit_w.value,
                        'sigma': sig_w.value,
                        'sigma_limit': None if sig_limit_w.value == 0 else sig_limit_w.value,
                        'func': func_w.value
                    })
                # print(f"Manual peak params for {exp_key} @ (row={row},col={col}):")
                # for i, p in enumerate(peak_list):
                #     print(f"  Peak {i}: {p}")

                self.__peak_fitting_manual(
                    intensity=intensity,
                    wavelengths=wavelengths,
                    peak_params=peak_list
                )
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
                # print(self.params_fit)
                # print(self.best_r2)
                ax1.plot(wavelengths, intensity, label='data', markersize=3)
                best = self.best_model.eval(x=wavelengths, params=self.params_fit)
                ax1.plot(wavelengths, best, '-', label=f'best fit (R²={self.best_r2:.3f})')
                names = []
                for name, comp in self.best_model.eval_components(x=wavelengths, params=self.params_fit).items():
                    names.append(name)
                    if name != 'bkg_':
                        ax1.plot(wavelengths, comp, '--', label=name)

                ax1.set(xlabel='Wavelength', ylabel='Intensity',
                        title=f'{exp_key} @ (row={row},col={col})')
                ax1.legend()
                if image_scan is not None:
                    ax2.imshow(image_scan, cmap='gray')
                    ax2.axis('off')
                    ax2.set_title('Sample map')
                    # compute cell size in pixels
                    img_h, img_w = image_scan.shape[:2]
                    cell_w = img_w / n_cols
                    cell_h = img_h / n_rows
                    # rectangle lower‐left corner in pixels
                    x0 = (col * cell_w) - (cell_w / 2)
                    y0 = (row * cell_h) - (cell_h / 2)
                    from matplotlib.patches import Rectangle
                    rect = Rectangle((x0, y0), cell_w, cell_h,
                                     linewidth=2, edgecolor='red', facecolor='none')
                    ax2.add_patch(rect)
                else:
                    ax2.text(0.5, 0.5, 'No map image\nprovided',
                             ha='center', va='center', fontsize=12)
                    ax2.axis('off')

                plt.tight_layout()
                plt.show()

                params = self.params_fit

                # decide the order you want suffixes printed in
                suffix_order = ['amplitude', 'center', 'sigma', 'fwhm']

                # 1) collect all the prefixes (e.g. 'g0', 'g1', 'bkg')
                prefixes = sorted({name.split('_', 1)[0] for name in params.keys()})

                print(f"Fit parameters for {exp_key} @ (row={row},col={col}):")
                print(f"  overall R² = {self.best_r2:.4f}")
                print("  detailed parameters:")

                for pfx in prefixes:
                    print(f"  {pfx}_:")
                    for suf in suffix_order:
                        full = f"{pfx}_{suf}"
                        if full in params:
                            par = params[full]
                            print(f"    {suf:<9} = {par.value:10.3f}  ± {par.stderr:.3f}" if par.stderr else
                                  f"    {suf:<9} = {par.value:10.3f}")
                    extras = sorted(
                        name.split('_', 1)[1]
                        for name in params.keys()
                        if name.startswith(pfx + '_') and name.split('_', 1)[1] not in suffix_order
                    )
                    for suf in extras:
                        par = params[f"{pfx}_{suf}"]
                        print(f"    {suf:<9} = {par.value:10.3f}")

        # wire buttons
        btn_add_peak.on_click(on_add_peak)
        btn_remove_peak.on_click(on_remove_peak)
        btn_fit_manual.on_click(lambda _: update_display())

        threshold_entry = BoundedFloatText(value=0.9, min=0.0, max=1.0, step=0.01, description='R² thresh:')
        include_low_chk = Checkbox(value=True, description='Include low R² in Excel')
        btn_fit_all = Button(description='Fit All', button_style='warning')

        def fit_all_callback(_):
            self.last_low_r2.clear()
            self.last_fit_results.clear()
            thresh = threshold_entry.value
            total = data.shape[0] * data.shape[1]
            progress = IntProgress(min=0, max=total, description='Fitting:')
            count = 0
            low_list = []
            with out:
                out.clear_output()
                display(progress)
                peak_list = []
                for amp_w, amp_limit_w, cen_w, cen_limit_w, sig_w, sig_limit_w, func_w in peak_widgets:
                    peak_list.append({
                        'amplitude': amp_w.value,
                        'amplitude_limit': None if amp_limit_w.value == 0 else amp_limit_w.value,
                        'center': cen_w.value,
                        'center_limit': None if cen_limit_w.value == 0 else cen_limit_w.value,
                        'sigma': sig_w.value,
                        'sigma_limit': None if sig_limit_w.value == 0 else sig_limit_w.value,
                        'func': func_w.value
                    })
                for r in range(data.shape[0]):
                    for c in range(data.shape[1]):
                        try:
                            self.__peak_fitting_manual(
                                intensity=data[r, c],
                                wavelengths=wavelengths,
                                peak_params=peak_list
                            )
                            params = self.params_fit.valuesdict()
                            rec = {'row': r, 'col': c, 'r2': self.best_r2,
                                   'func_list': [peak['func'] for peak in peak_list]}
                            rec.update(params)
                            self.last_fit_results.append(rec)
                            if self.best_r2 < thresh: low_list.append((r, c, self.best_r2))
                        except Exception as e:
                            print(f"Error fitting (row={r}, col={c}): {e}")
                        count += 1
                        progress.value = count

                self.last_low_r2 = low_list
                df = pd.DataFrame(self.last_fit_results)
                if not include_low_chk.value:
                    df = df[df['r2'] >= thresh]
                path = f'fitting_results_{exp_key}.xlsx'
                df.to_excel(path, index=False)
                if low_list:
                    print(f"Spectra with R² below {thresh}:")
                    for r, c, r2 in low_list: print(f"  row={r},col={c},R²={r2:.3f}")
                else:
                    print(f"All spectra have R² ≥ {thresh}.")
                print(f"\nExcel file saved to '{path}'.")
                display(FileLink(path))

        btn_fit_all.on_click(fit_all_callback)

        # navigation logic
        def shift_row(d):
            row_entry.value = np.clip(row_entry.value + d, 0, max_row)

        def shift_col(d):
            col_entry.value = np.clip(col_entry.value + d, 0, max_col)

        btn_prev_row.on_click(lambda _: shift_row(-1))
        btn_next_row.on_click(lambda _: shift_row(1))
        btn_prev_col.on_click(lambda _: shift_col(-1))
        btn_next_col.on_click(lambda _: shift_col(1))

        row_entry.observe(lambda _: update_display(), names='value')
        col_entry.observe(lambda _: update_display(), names='value')

        def on_key_change(change):
            if change['name'] == 'value' and change['new'] != change['old']:
                # reload all of your spectra
                nonlocal data, wavelengths, image_scan, n_rows, n_cols, max_row, max_col
                data = self.data_dict[change['new']].get_numpy_spectra()
                wavelengths = self.data_dict[change['new']].get_wavelengths()
                image_scan = self.data_dict[change['new']].get_live_scan()
                n_rows, n_cols = data.shape[:2]
                max_row, max_col = n_rows - 1, n_cols - 1
                row_entry.max, col_entry.max = max_row, max_col
                row_entry.value, col_entry.value = 0, 0
                update_display()

        exp_dropdown.observe(on_key_change, names='value')

        # assemble the top-level layout
        nav_row = HBox([btn_prev_row, row_entry, btn_next_row], layout=Layout(gap='5px'))
        nav_col = HBox([btn_prev_col, col_entry, btn_next_col], layout=Layout(gap='5px'))
        peak_ctrl = HBox([btn_add_peak, btn_remove_peak, btn_fit_manual, threshold_entry, include_low_chk, btn_fit_all],
                         layout=Layout(margin='10px 0', gap='10px'))

        from IPython.display import display
        display(VBox([
            exp_dropdown,
            nav_row,
            nav_col,
            peak_ctrl,
            peaks_container,
            out
        ], layout=Layout(spacing='10px')))

        # trigger your initial plot
        # update_display()

    def interactive_plot_fitted_data_all(self, addr, start_row=0, start_col=0):

        data = self.data_dict[self.ref].get_numpy_spectra()
        wavelengths = self.data_dict[self.ref].get_wavelengths()
        n_rows, n_cols = data.shape[0], data.shape[1]
        image_scan = self.data_dict[self.ref].get_live_scan()

        row, col = start_row, start_col
        max_row, max_col = data.shape[0] - 1, data.shape[1] - 1

        desc_w = '80px'

        field_layout = Layout(width='200px', height='40px')

        row_entry = BoundedIntText(
            value=row,
            min=0,
            max=max_row,
            description='Row:',
            style={'description_width': desc_w},
            layout=field_layout
        )

        col_entry = BoundedIntText(
            value=col,
            min=0,
            max=max_col,
            description='Col:',
            style={'description_width': desc_w},
            layout=field_layout
        )

        # nav buttons
        btn_prev_row = Button(description='←', tooltip='Previous row', layout=Layout(width='50px'))
        btn_next_row = Button(description='→', tooltip='Next row', layout=Layout(width='50px'))
        btn_prev_col = Button(description='←', tooltip='Previous col', layout=Layout(width='50px'))
        btn_next_col = Button(description='→', tooltip='Next col', layout=Layout(width='50px'))

        out = Output(layout=Layout(border='1px solid gray'))

        def shift_row(d):
            row_entry.value = np.clip(row_entry.value + d, 0, max_row)

        def shift_col(d):
            col_entry.value = np.clip(col_entry.value + d, 0, max_col)

        def update_display(change=None):
            nonlocal row, col
            peaks_data = dict()
            row, col = row_entry.value, col_entry.value
            intensity = data[row, col]
            row_a, col_a = row, col
            with out:
                out.clear_output(wait=True)
                cmap = plt.get_cmap('gnuplot')
                colors = cmap(np.linspace(0, 1, len(self.data_dict.keys())))
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
                for idx, key in enumerate(self.data_coordinates):
                    if key == 'ref':
                        i = self.ref
                        peaks_data[i] = []
                        row_a, col_a = row, col
                    else:
                        i = key
                        peaks_data[key] = []
                        print(f"Processing {i} @ (row={row}, col={col})")
                        row_a, col_a = self.data_coordinates[i][(row, col)]

                    x = self.data_dict[i].get_wavelengths()[::-1]
                    y = self.data_dict[i].get_numpy_spectra()[row_a, col_a][::-1]

                    res = self.__remodel_fitted_data(f'./{addr}/fitting_results_{i}.xlsx', int(row), int(col), x, y,
                                                     peak_type='lorentzian')
                    ax1.plot(x, res.best_fit,
                             color=colors[idx],
                             label=i)
                    j = 0
                    while True:
                        # amp_name = f"p{i}_height"
                        cen_name = f"g{j}_center"
                        if cen_name not in res.params:
                            break
                        # amp = res.params[amp_name].value
                        cen = res.params[cen_name].value
                        if cen < x[0] or cen > x[-1]:
                            j += 1
                            continue
                        
                        idx_cen = np.abs(x - cen).argmin()
                        peaks_data[i].append((cen, res.best_fit[idx_cen]))
                        j += 1

                    # for idx, (pos, height) in enumerate(peaks, 1):
                    #     print(f"Peak {idx}: x = {pos:.3f}, height = {height:.3f}")
                    # print(f'{i} : {max(res.best_fit)}')
                    # print(f'{i} : {x[np.argmax(res.best_fit)]}')
                    # y = res.best_fit
                    # peaks, props = find_peaks(y, height=0)
                    # peak_heights   = props["peak_heights"]
                    # peak_positions = x[peaks]
                    # for idx, (pos, height) in enumerate(zip(peak_positions, peak_heights), start=1):
                    #     # print(f"{i} – Peak {idx}: x = {pos:.3f}, height = {height:.3f}")
                    #     peaks_data[i].append((pos, height))
                   


                if image_scan is not None:
                    ax2.imshow(image_scan, cmap='gray')
                    ax2.axis('off')
                    ax2.set_title('Sample map')
                    img_h, img_w = image_scan.shape[:2]
                    cell_w = img_w / n_cols
                    cell_h = img_h / n_rows
                    x0 = (col * cell_w) - (cell_w / 2)
                    y0 = (row * cell_h) - (cell_h / 2)
                    from matplotlib.patches import Rectangle
                    rect = Rectangle((x0, y0), cell_w, cell_h,
                                     linewidth=2, edgecolor='red', facecolor='none')
                    ax2.add_patch(rect)
                else:
                    ax2.text(0.5, 0.5, 'No map image\nprovided',
                             ha='center', va='center', fontsize=12)
                    ax2.axis('off')

                plt.tight_layout()
                ax1.legend(title='Curve index')
                plt.show()
                def key_value_in_thousands(key):
                    num_str = key.split("_")[-1]
                    if num_str.endswith("NA"):
                        return int(num_str.rstrip("NA"))
                    elif num_str.endswith("PA"):
                        return int(num_str.rstrip("PA")) / 1000

                sorted_items = sorted(peaks_data.items(), key=lambda kv: key_value_in_thousands(kv[0]))
                peaks_data = {k: v for k, v in sorted_items}
                for k,v in peaks_data.items():
                    if v:
                        print(f"Peaks for {k} @ (row={row}, col={col}):")
                        for idx, (pos, height) in enumerate(v, start=1):
                            print(f"  Peak {idx}: x = {pos:.3f}, height = {height:.3f}")
                    else:
                        print(f"No peaks found for {k} @ (row={row}, col={col})")         

        btn_prev_row.on_click(lambda _: shift_row(-1))
        btn_next_row.on_click(lambda _: shift_row(1))
        btn_prev_col.on_click(lambda _: shift_col(-1))
        btn_next_col.on_click(lambda _: shift_col(1))
        row_entry.observe(update_display, names='value')
        col_entry.observe(update_display, names='value')

        row_controls = HBox(
            [btn_prev_row, row_entry, btn_next_row],
            layout=Layout(
                display='flex',
                flex_flow='row nowrap',
                align_items='center',
                gap='5px'
            )
        )

        col_controls = HBox(
            [btn_prev_col, col_entry, btn_next_col],
            layout=Layout(
                display='flex',
                flex_flow='row nowrap',
                align_items='center',
                gap='5px'
            )
        )
        display(VBox([
            row_controls,
            col_controls,
            out
        ], layout=Layout(spacing='15px')))
        update_display()

    def __peak_fitting_manual(self, intensity, wavelengths, peak_params):
        peak_params.sort(key=lambda p: p['amplitude'], reverse=True)
        composite_model = ConstantModel(prefix='bkg_')
        params = composite_model.make_params(bkg_c=0)

        self.best_r2 = None
        self.best_result = None
        self.best_model = None
        self.params_fit = None
        self.best_fit = None

        r2_list = []
        params_list = []
        models = []
        results = []

        def set_with_limit(param, base, limit, always_min=None):
            """
            Sets param.value=base;
            if limit is not None, also sets min=base-limit, max=base+limit;
            if always_min is given (not None), always sets min=always_min.
            """
            kw = {'value': base}
            if limit is not None:
                kw['min'] = base - limit
                kw['max'] = base + limit
            elif always_min is not None:
                kw['min'] = always_min
            param.set(**kw)

        for i in range(len(peak_params)):
            model = peak_params[i]['func'](prefix=f'p{i}_')
            composite_model = model if composite_model is None else composite_model + model

            model_params = model.make_params()
            params = model_params if params is None else params.update(model_params) or params

            set_with_limit(
                params[f'p{i}_amplitude'],
                peak_params[i]['amplitude'],
                peak_params[i].get('amplitude_limit', None)
            )

            set_with_limit(
                params[f'p{i}_center'],
                peak_params[i]['center'],
                peak_params[i].get('center_limit', None),
            )

            set_with_limit(
                params[f'p{i}_sigma'],
                peak_params[i]['sigma'],
                peak_params[i].get('sigma_limit', None),
            )

            # fit & collect results
            result = composite_model.fit(intensity, params, x=wavelengths)
            ss_total    = np.sum((intensity - intensity.mean())**2)
            ss_residual = np.sum(result.residual**2)
            r_squared   = 1 - ss_residual/ss_total

            r2_list.append(r_squared)
            params_list.append(result.params)
            models.append(composite_model)
            results.append(result)

            print(f"Using {i+1} peak(s): R² = {r_squared:.4f}")

            # track the “latest” best fit so far
            self.best_fit    = i
            self.params_fit  = params_list[-1]
            self.best_model  = models[-1]
            self.best_result = results[-1]
            self.best_r2     = r2_list[-1]

        # after looping, pick the first bump in R² drop >0.005
        r2_sorted = sorted(r2_list, reverse=True)
        for j in range(len(r2_sorted)-1):
            if r2_sorted[j] - r2_sorted[j+1] > 0.005:
                idx = r2_list.index(r2_sorted[j])
                self.best_fit    = idx
                self.params_fit  = params_list[idx]
                self.best_model  = models[idx]
                self.best_result = results[idx]
                self.best_r2     = r2_list[idx]
                # stop if we've considered all peaks
                if len(r2_list) == len(peak_params):
                    break


    def interactive_peak_refine(self, exp_key, start_row=0, start_col=0):
        """
        Manual‐only peak fitting panel where each peak can be
        Gaussian or Lorentzian independently.
        """
        # 1) data
        data = self.data_dict[exp_key].get_numpy_spectra()
        x = self.data_dict[exp_key].get_wavelengths()
        max_row, max_col = data.shape[0] - 1, data.shape[1] - 1

        # 2) row/col controls
        row_entry = BoundedIntText(value=start_row, min=0, max=max_row, description='Row:')
        col_entry = BoundedIntText(value=start_col, min=0, max=max_col, description='Col:')
        btn_pr = Button(description='←', layout=Layout(width='50px'))
        btn_nr = Button(description='→', layout=Layout(width='50px'))
        btn_pc = Button(description='←', layout=Layout(width='50px'))
        btn_nc = Button(description='→', layout=Layout(width='50px'))
        btn_pr.on_click(lambda _: setattr(row_entry, 'value', max(0, row_entry.value - 1)))
        btn_nr.on_click(lambda _: setattr(row_entry, 'value', min(max_row, row_entry.value + 1)))
        btn_pc.on_click(lambda _: setattr(col_entry, 'value', max(0, col_entry.value - 1)))
        btn_nc.on_click(lambda _: setattr(col_entry, 'value', min(max_col, col_entry.value + 1)))
        row_ctrl = HBox([row_entry, btn_pr, btn_nr],
                        layout=Layout(align_items='center', margin='0 50px 0 0'))
        col_ctrl = HBox([col_entry, btn_pc, btn_nc],
                        layout=Layout(align_items='center'))

        # 3) manual‐peak container + add button
        peaks_box = VBox()
        btn_add = Button(description='Add Peak', button_style='info')

        def add_peak(_):
            c = FloatText(value=0.0, description='Center', layout=Layout(width='200px'))
            s = FloatText(value=1.0, description='Sigma', layout=Layout(width='200px'))
            h = FloatText(value=1.0, description='Height', layout=Layout(width='200px'))
            dd = Dropdown(options=['Gaussian', 'Lorentzian'],
                          value='Gaussian',
                          description='Func',
                          layout=Layout(width='500px'))
            rm = Button(description='✖', layout=Layout(width='30px'))
            row = HBox([c, s, h, dd, rm], layout=Layout(align_items='center', spacing='10px'))
            # remove callback
            rm.on_click(lambda __: setattr(
                peaks_box, 'children',
                tuple(w for w in peaks_box.children if w is not row)
            ))
            # append
            peaks_box.children = peaks_box.children + (row,)

        btn_add.on_click(add_peak)
        add_peak(None)  # start with one

        # 4) fit button + output
        btn_fit = Button(description='Fit with Manual Guesses', button_style='primary', layout=Layout(width='400px'))
        out = Output(layout=Layout(border='1px solid gray'))

        def on_fit(_):
            out.clear_output()
            with out:
                if not peaks_box.children:
                    print("⚠️ Add at least one peak before fitting.")
                    return
                r, c = row_entry.value, col_entry.value
                y = data[r, c]

                # build composite model from each row's Func
                composite = None
                for i, row_w in enumerate(peaks_box.children):
                    prefix = f'p{i}_'
                    func = row_w.children[3].value  # the Dropdown
                    ModelClass = GaussianModel if func == 'Gaussian' else LorentzianModel
                    m = ModelClass(prefix=prefix)
                    composite = m if composite is None else composite + m

                # make & seed parameters
                params = composite.make_params()
                for i, row_w in enumerate(peaks_box.children):
                    prefix = f'p{i}_'
                    params[f'{prefix}center'].value = row_w.children[0].value
                    params[f'{prefix}sigma'].value = row_w.children[1].value
                    params[f'{prefix}height'].value = row_w.children[2].value

                # fit & plot
                result = composite.fit(y, params, x=x)
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.plot(x, y, 'o', ms=3, label='data')
                comps = result.eval_components(x=x)
                for name, comp in comps.items():
                    ax.plot(x, comp, '--', label=name)
                ax.plot(x, result.best_fit, '-', lw=2,
                        label=f'fit (R²={result.rsquared:.3f})')
                ax.set_xlabel('Wavelength')
                ax.set_ylabel('Intensity')
                ax.set_title(f'{exp_key} @ (row={r}, col={c})')
                ax.legend()
                plt.show()

        btn_fit.on_click(on_fit)

        # 5) display
        controls = VBox([
            HBox([row_ctrl, col_ctrl]),
            btn_add,
            peaks_box,
            HBox([btn_fit], layout=Layout(margin='10px 0')),
        ])
        display(VBox([controls, out]))

    def __remodel_fitted_data(self,
                              excel_path: str,
                              row: int,
                              col: int,
                              x: np.ndarray,
                              y: np.ndarray,
                              peak_type: str
                              ):

        df = pd.read_excel(excel_path)
        pix = df[(df['row'] == row) & (df['col'] == col)]
        if pix.empty:
            raise ValueError(f"No fit parameters for row={row}, col={col}")
        pix = pix.iloc[0]

        # 2) pick model class
        # model_cls = {
        #     'gaussian': GaussianModel,
        #     'lorentzian': LorentzianModel,
        #     'voigt': VoigtModel
        # }.get(peak_type.lower())
        # if model_cls is None:
        #     raise ValueError("peak_type must be 'Gaussian', 'Lorentzian' or 'Voigt'")

        composite = None
        params = None
        i = 0
        while True:
            prefix = f"g{i}_"
            amp_key, cen_key, sig_key = prefix + 'amplitude', prefix + 'center', prefix + 'sigma'
            
            if amp_key not in pix or np.isnan(pix[amp_key]):
                break
            
            if float(pix[cen_key]) < 800:
                model_cls = GaussianModel
            else:
                model_cls = LorentzianModel
                
            

            mod = model_cls(prefix=prefix)
            if composite is None:
                composite = mod
            else:
                composite += mod

            par = mod.make_params(
                amplitude=pix[amp_key],
                center=pix[cen_key],
                sigma=pix[sig_key]
            )
            if params is None:
                params = par
            else:
                params.update(par)

            i += 1

        # print(i)
        bkg_mod = ConstantModel(prefix='bkg_c')
        composite += bkg_mod
        bkg_par = bkg_mod.make_params(c=pix['bkg_c'])
        params.update(bkg_par)

        result = composite.fit(y, params, x=x)

        return result

    @staticmethod
    def visualize_pixel_similarity(image1, image2, coord1, coord2, patch1, patch2, ssim_value, window_size=11,
                                   title='Image 2'):
        """
        Visualizes the pixel comparison process, showing the images, patches, and SSIM value.
        """
        fig, axes = plt.subplots(1, 2, figsize=(12, 6))

        # First image
        axes[0].imshow(image1, cmap='gray', extent=[0, 64, 64, 0])
        axes[0].set_title('Image 1')
        axes[0].axis('off')
        axes[0].plot(coord1[1], coord1[0], 'ro')  # Note that matplotlib uses x, y coordinates

        # Draw rectangle around patch
        rect1 = patches.Rectangle((coord1[1] - window_size // 2, coord1[0] - window_size // 2),
                                  window_size, window_size, linewidth=1, edgecolor='r', facecolor='none')
        axes[0].add_patch(rect1)

        # Second image
        axes[1].imshow(image2, cmap='gray', extent=[0, 64, 64, 0])
        axes[1].set_title(title)
        axes[1].axis('off')
        axes[1].plot(coord2[1], coord2[0], 'ro')

        rect2 = patches.Rectangle((coord2[1] - window_size // 2, coord2[0] - window_size // 2),
                                  window_size, window_size, linewidth=1, edgecolor='r', facecolor='none')
        axes[1].add_patch(rect2)

        plt.show()

        # Display the patches and SSIM value
        fig2, axes2 = plt.subplots(1, 2, figsize=(8, 4))
        axes2[0].imshow(patch1, cmap='gray', extent=[0, 64, 64, 0])
        axes2[0].set_title('Patch from Image 1')
        axes2[0].axis('off')
        axes2[1].imshow(patch2, cmap='gray', extent=[0, 64, 64, 0])
        axes2[1].set_title('Patch from Image 2')
        axes2[1].axis('off')
        plt.suptitle(f'SSIM between patches: {ssim_value:.4f}', fontsize=16)
        plt.show()

    @staticmethod
    def are_pixels_similar(image1, image2, coord1, coord2, window_size=7, threshold=0.5):
        """
        Determines if two pixels in different images are similar based on the SSIM of patches around them.

        Parameters:
        - mes1, mes2: Two set of measurements that has been done.
        - coord1, coord2: Tuples (y, x) representing the coordinates of the pixels in image1 and image2.
        - window_size: Size of the square window around the pixel to compute SSIM.
        - threshold: SSIM threshold above which pixels are considered similar.

        Returns:
        - ssim_value: The computed SSIM value.
        - is_similar: True if SSIM between patches is above the threshold, False otherwise.
        - patch1, patch2: The patches extracted from image1 and image2.
        """
        y1, x1 = coord1
        y2, x2 = coord2
        half_window = window_size // 2

        # image1 = self.data_dict[mes1].get_live_scan()
        # image2 = self.data_dict[mes2].get_live_scan()

        patch1 = image1[max(0, y1 - half_window): y1 + half_window + 1,
                 max(0, x1 - half_window): x1 + half_window + 1]
        patch2 = image2[max(0, y2 - half_window): y2 + half_window + 1,
                 max(0, x2 - half_window): x2 + half_window + 1]

        min_rows = min(patch1.shape[0], patch2.shape[0])
        min_cols = min(patch1.shape[1], patch2.shape[1])
        patch1 = patch1[:min_rows, :min_cols]
        patch2 = patch2[:min_rows, :min_cols]

        ssim_value = ssim(patch1, patch2,
                          data_range=patch1.max() - patch1.min(),
                          channel_axis=-1 if patch1.ndim == 3 else None)

        is_similar = ssim_value >= threshold
        # CondAns.visualize_pixel_similarity(image1, image2, coord1, coord2, patch1, patch2, ssim_value,
        # window_size=window_size)
        return ssim_value, is_similar, patch1, patch2

    @staticmethod
    def map_pixels(img1, img2, window_size=11, search_radius=15):
        """
        Find pixel correspondences between two images using local SSIM comparison

        Args:
            img1 (numpy.ndarray): First image (2D array)
            img2 (numpy.ndarray): Second image (2D array)
            window_size (int): Odd number size of the comparison window
            search_radius (int): Search radius in pixels around original position

        Returns:
            correspondence_map (numpy.ndarray): Array of shape (H, W, 2) containing
            corresponding [x,y] coordinates in img2 for each pixel in img1
        """

        assert img1.ndim == 2 and img2.ndim == 2, "Images must be 2D arrays"
        assert img1.shape == img2.shape, "Images must have the same dimensions"
        assert window_size % 2 == 1, "Window size must be odd"

        global_min = min(img1.min(), img2.min())
        global_max = max(img1.max(), img2.max())
        data_range = global_max - global_min
        result_dict = dict()

        pad = window_size // 2
        height, width = img1.shape

        img1_padded = np.pad(img1, pad, mode='reflect')
        img2_padded = np.pad(img2, pad, mode='reflect')

        correspondence_map = np.zeros((height, width, 2), dtype=np.int32)

        offsets = [(di, dj) for di in range(-search_radius, search_radius + 1)
                   for dj in range(-search_radius, search_radius + 1)]

        for i in range(height):
            for j in range(width):
                pi, pj = i + pad, j + pad

                window1 = img1_padded[pi - pad:pi + pad + 1, pj - pad:pj + pad + 1]

                best_score = -np.inf
                best_pos = (i, j)

                min_i = max(pad, pi - search_radius)
                max_i = min(img2_padded.shape[0] - pad, pi + search_radius + 1)
                min_j = max(pad, pj - search_radius)
                max_j = min(img2_padded.shape[1] - pad, pj + search_radius + 1)

                for x in range(min_i, max_i):
                    for y in range(min_j, max_j):
                        window2 = img2_padded[x - pad:x + pad + 1, y - pad:y + pad + 1]

                        score = ssim(window1, window2,
                                     data_range=data_range,
                                     gaussian_weights=True,
                                     win_size=window_size,
                                     use_sample_covariance=False)

                        if score > best_score:
                            best_score = score
                            best_pos = (x - pad, y - pad)

                correspondence_map[i, j] = best_pos

        for i in range(height):
            for j in range(width):
                result_dict[(i, j)] = tuple(correspondence_map[i][j])

        return result_dict

    @staticmethod
    def fit_lorentzian_spectrum(x, y, num_peaks=1, model_func=VoigtModel):
        """
        Fits the given spectrum using a sum of Lorentzian functions.

        Parameters:
            x (numpy.ndarray): The x-axis data (e.g., wavelength, energy, etc.).
            y (numpy.ndarray): The y-axis data (intensity).
            num_peaks (int): Number of Lorentzian peaks to fit.
            model_func (class): The model class to use for each peak (e.g., VoigtModel, GaussianModel).

        Returns:
            lmfit.model.ModelResult: The fitting result.
        """
        composite_model = None
        params = None

        for i in range(num_peaks):
            model = model_func(prefix=f'p{i}_')

            if composite_model is None:
                composite_model = model
            else:
                composite_model += model

            if i == 0:
                amp_guess = 2000
                center_guess = 800
                sigma_guess = 10
            elif i == 1:
                amp_guess = 2000
                center_guess = 900
                sigma_guess = 1
            elif i == 2:
                amp_guess = 2000
                center_guess = 970
                sigma_guess = 1

            model_params = model.make_params()
            if params is None:
                params = model_params
            else:
                params.update(model_params)

            params[f'p{i}_amplitude'].set(value=amp_guess, min=0)
            params[f'p{i}_center'].set(value=center_guess, min=x.min(), max=x.max())
            params[f'p{i}_sigma'].set(value=sigma_guess, min=0)

        result = composite_model.fit(y, params, x=x)
        return result

    @staticmethod
    def __plot_image_with_rect(ax, image_data, coord, title):
        """
        Plot a grayscale image on the given axis with a red rectangle
        marking the coordinate.

        Parameters:
            ax (matplotlib.axes.Axes): Axis to plot the image.
            image_data (numpy.ndarray): 2D image array.
            coord (tuple): (row, col) coordinate. If None, uses (0, 0).
            title (str): Axis title.
        """
        if coord == (0, 0):
            ax.imshow(image_data, extent=(0, image_data.shape[1], image_data.shape[0], 0),
                      cmap='gray')
            ax.set_title(title)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.grid(False)
        else:
            ax.imshow(image_data, extent=(0, image_data.shape[1], image_data.shape[0], 0),
                      cmap='gray')
            rect = patches.Rectangle((coord[1], coord[0]), 1, 1,
                                     linewidth=1, edgecolor='r', facecolor='none')
            ax.add_patch(rect)
            ax.set_title(title)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.grid(False)

        return coord, ax

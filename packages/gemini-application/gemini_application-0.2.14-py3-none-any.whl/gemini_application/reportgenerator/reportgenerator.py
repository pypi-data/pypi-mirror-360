from gemini_application.application_abstract import ApplicationAbstract
from gemini_application.injectionwell.injectionwell_monitoring import InjectionWellMonitoring
from gemini_model.well.pressure_drop import DPDT
from gemini_model.fluid.pvt_water_stp import PVTConstantSTP
from gemini_model.reservoir.reservoir_pressuredrop import bottomhole_skin_dp

import io
from math import ceil, sqrt
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import matplotlib.image as mpimg

from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib import rcParams
matplotlib.use('Agg')


class ReportGenerator(ApplicationAbstract):
    """Class for generating reports
            The class retrieves data from the database and generates a report in pdf format

            """
    def __init__(self):
        super().__init__()
        self.plant_name = None
        self.project_path = None
        self.start_time = None
        self.end_time = None
        self.start_datestamp_title = None
        self.end_datestamp_title = None
        self.timestep = 3600    # Default value is 1 hour since usually values are given /h
        self.database_internal = None
        self.database_external = None
        self.pdf_buffer = None
        self.pdf_object = None
        self.author_name = None
        self.project_name = None
        self.number_days = None

        # Well pressure drop model
        self.well_DP = DPDT()
        self.well_DP.PVT = PVTConstantSTP()
        self.bottomhole_skin_dp = bottomhole_skin_dp()

    def init_parameters(self, **kwargs):
        """Function to initialize parameters"""
        for key, value in kwargs.items():
            setattr(self, key, value)

        start_dt = datetime.strptime(self.start_time, "%Y-%m-%d %H:%M:%S")
        self.start_datestamp_title = (
            f"{start_dt.month}/"
            f"{start_dt.day}/"
            f"{start_dt.year} "
            f"{start_dt.strftime('%H')}:{start_dt.strftime('%M')}"
        )

        end_dt = datetime.strptime(self.end_time, "%Y-%m-%d %H:%M:%S")
        self.end_datestamp_title = (
            f"{end_dt.month}/"
            f"{end_dt.day}/"
            f"{end_dt.year} "
            f"{end_dt.strftime('%H')}:{end_dt.strftime('%M')}"
        )

    def calculate(self):
        # Class ReportGenerator does not require calculations
        pass

    def get_units(self, tagname):
        tag = tagname.lower()
        if "pressure" in tag:
            units = "[bar]"
        elif "temperature" in tag:
            units = "[°C]"
        elif "flow" in tag:
            units = "[m^3/h]"
        elif "frequency" in tag:
            units = "[Hz]"
        elif "current" in tag:
            units = "[A]"
        elif "power" in tag:
            units = "[kW]"
        else:
            units = "[-]"
        return units

    def get_data(self, tagname):
        result, time = self.plant.database.read_internal_database(
            self.unit.plant.name,
            self.unit.name,
            tagname,
            self.start_time,
            self.end_time,
            self.timestep
        )
        return result, time

    def initialize_pdf_object(self):
        self.pdf_buffer = io.BytesIO()
        self.pdf_object = PdfPages(self.pdf_buffer)
        return

    def add_title_page(self):
        title = f'{self.project_name} Report'
        date_str = datetime.now().strftime("%A, %B %dth %Y, %I:%M %p")
        author = self.author_name

        if not hasattr(self, 'pdf_object') or self.pdf_object is None:
            raise ValueError("PDF object is not initialized. "
                             "Ensure self.pdf_object is properly set.")

        fig, ax = plt.subplots()
        ax.axis("off")  # Remove axes

        # Title: centered in the page
        ax.text(0.5, 0.5, title, fontsize=32, fontweight="bold", ha="center", va="center")

        # Author and Date: below the title, left aligned
        ax.text(0.1, 0.42, f"Date: {date_str}", fontsize=14, ha="left", va="top")
        ax.text(0.1, 0.38, f"Author: {author}", fontsize=14, ha="left", va="top")

        # Logo at top-right
        try:
            logo_img = mpimg.imread(".\\static\\images\\gemini_DDT_V1_300dpi.jpg")
            imagebox = OffsetImage(logo_img, zoom=0.2)
            ab = AnnotationBbox(imagebox, (0.95, 0.92), frameon=False, box_alignment=(1, 1))
            ax.add_artist(ab)
        except FileNotFoundError:
            # Placeholder if no logo image
            ax.text(0.95, 0.92, "[Logo Here]", fontsize=12, ha="right", va="top", style='italic')

        # Save to PDF
        width, height = 11.69, 8.27
        fig.set_size_inches(width, height)
        self.pdf_object.savefig(fig, bbox_inches="tight", pad_inches=0.5)
        plt.close(fig)

    def get_injection_wells(self):
        output = list()
        for unit in self.plant.units:
            unit_name = unit.name
            if "injection_well" in unit_name:
                output.append(unit_name)
        return output

    def get_production_wells(self):
        output = list()
        for unit in self.plant.units:
            unit_name = unit.name
            if "production_well" in unit_name:
                output.append(unit_name)
        return output

    def get_esps(self):
        output = list()
        for unit in self.plant.units:
            unit_name = unit.name
            if "esp" in unit_name:
                output.append(unit_name)
        return output

    def add_timeseries_plot_to_pdf(self, data, timestamps, xlabel, ylabel, title):
        plt.figure(figsize=(10, 5))
        dates = [datetime.fromisoformat(ts.replace("Z", "")) for ts in timestamps]
        plt.plot(timestamps, dates, linestyle="-", color="b", label="Time Series")

        plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(nbins='auto'))
        plt.gca().yaxis.set_major_locator(ticker.MaxNLocator(nbins='auto'))

        plt.xlabel("Timestamp")
        plt.ylabel(ylabel)
        plt.title(title)
        plt.legend()
        plt.grid()

        self.pdf_object.savefig()
        plt.close()

    def add_X_Y_plot_to_pdf(self, x_data, y_data):
        plt.figure(figsize=(11.69, 8.27))
        plt.plot(x_data, y_data, marker="o", linestyle="-", color="r", label="X-Y Plot")
        plt.xlabel("X Data")
        plt.ylabel("Y Data")
        plt.title("X-Y Plot")
        plt.legend()
        plt.grid()
        self.pdf_object.savefig()
        plt.close()

    def get_clean_list(self, value_list):
        clean_list = []
        for value in value_list:
            try:
                # Try converting to float
                converted = float(value)
                clean_list.append(converted)
            except (ValueError, TypeError):
                # Discard if not convertible
                continue
        return clean_list

    def add_stats_plot(self, inj_wells, prod_wells):
        inj_well_tagnames = [
            'injectionwell_flow.measured',
            'injectionwell_wellhead_pressure.measured',
            'injectionwell_annulus_a_pressure.measured'
        ]
        prod_well_tagnames = [
            'productionwell_annulus_a_pressure.measured',
            'productionwell_annulus_b_pressure.measured'
        ]

        all_wells = inj_wells + prod_wells
        unit_tag_pairs = []

        for well_name in all_wells:
            if "injection" in well_name:
                unit_tag_pairs.append((well_name, inj_well_tagnames))
            elif "production" in well_name:
                unit_tag_pairs.append((well_name, prod_well_tagnames))

        num_units = len(unit_tag_pairs)
        max_tags_per_unit = max(len(tags) for _, tags in unit_tag_pairs)

        # Create subplots with constrained layout
        fig, axes = plt.subplots(
            num_units,
            max_tags_per_unit,
            sharex=False,
            constrained_layout=True
        )

        # Normalize axes to 2D array
        if num_units == 1:
            axes = [axes]
        if max_tags_per_unit == 1:
            axes = [[ax] for ax in axes]

        for row_idx, (well_name, tagnames) in enumerate(unit_tag_pairs):
            self.select_unit(well_name)

            for col_idx in range(max_tags_per_unit):
                ax = axes[row_idx][col_idx]

                if col_idx >= len(tagnames):
                    ax.axis("off")
                    continue

                tagname = tagnames[col_idx]
                value_list, datestamp_list = self.get_data(tagname)
                clean_list = self.get_clean_list(value_list)

                if not clean_list or not datestamp_list:
                    ax.set_title(f"{well_name}\n{tagname}\nNo Data")
                    ax.axis("off")
                    continue

                try:
                    dates = [datetime.fromisoformat(ts.replace("Z", "")) for ts in datestamp_list]
                    max_value = max(clean_list)
                    max_index = value_list.index(max_value)

                    # Plot data
                    ax.plot(dates, value_list, linestyle="-", color="blue", linewidth=1)
                    ax.scatter(dates[max_index], max_value, color="red", zorder=5)

                    # Max value overlay
                    ax.text(
                        0.5, 0.5, f"{max_value:.2f}",
                        transform=ax.transAxes,
                        fontsize=26 if num_units > 3 else 32,
                        ha='center', va='center',
                        weight='bold', color='black',
                        zorder=10
                    )

                    ax.set_title(f"{well_name}\n{tagname}", fontsize=9)
                    ax.grid(True)
                    ax.set_xticks([])
                    ax.set_xticklabels([])
                    ax.tick_params(axis='y', labelsize=8)
                    ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins='auto'))

                except Exception as e:
                    ax.set_title(f"Error: {tagname}")
                    ax.text(0.5, 0.5, str(e), transform=ax.transAxes, ha='center', va='center')
                    ax.axis("off")

        fig.suptitle(
            f"{self.project_name} — Max values during the period "
            f"{self.start_datestamp_title} - {self.end_datestamp_title}",
            fontsize=14, fontweight="bold"
        )

        fig.set_size_inches(11.69, 8.27)
        self.pdf_object.savefig(fig, bbox_inches="tight", pad_inches=0.3)
        plt.close(fig)

    def gather_stats(self, well_names, tagnames):
        stats_data = []
        for well_name in well_names:
            self.select_unit(well_name)
            for tagname in tagnames:
                value_list, datestamp_list = self.get_data(tagname)
                clean_list = self.get_clean_list(value_list)
                if not clean_list or not datestamp_list:
                    continue  # Skip empty data

                # Compute stats
                max_value = max(clean_list)
                min_value = min(clean_list)
                mean_value = np.mean(clean_list)
                std_value = np.std(clean_list)

                # Timestamp for max value
                try:
                    max_index = value_list.index(max_value)
                    max_timestamp = datestamp_list[max_index]
                    max_datetime = datetime.fromisoformat(max_timestamp.replace("Z", ""))
                    timestamp_str = max_datetime.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    timestamp_str = "N/A"

                stats_data.append([
                    well_name,
                    tagname,
                    f"{min_value:.2f}",
                    f"{max_value:.2f}",
                    f"{mean_value:.2f}",
                    f"{std_value:.2f}",
                    timestamp_str
                ])
        return stats_data

    def add_injection_report(self, inj_wells, tagnames):
        num_wells = len(inj_wells)
        if num_wells == 0:
            return

        fig, axes = plt.subplots(num_wells, 1, sharex=True)
        if num_wells == 1:
            axes = [axes]  # Ensure iterable

        fig.suptitle("Injection wells report", fontsize=16, fontweight="bold")
        color_cycle = plt.cm.tab10.colors

        # Separate injectivity tagnames and others, preserving order
        injectivity_tags = [tn for tn in tagnames if "injectivity" in tn.lower()]
        other_tags = [tn for tn in tagnames if "injectivity" not in tn.lower()]

        for idx, (well_name, ax_left) in enumerate(zip(inj_wells, axes)):
            self.select_unit(well_name)

            tag_data = {}
            timestamps = None

            # Collect tag data
            for tagname in tagnames:
                value_list, datestamp_list = self.get_data(tagname)
                if not value_list or not datestamp_list:
                    continue
                try:
                    dates = [datetime.fromisoformat(ts.replace("Z", "")) for ts in datestamp_list]
                    if timestamps is None:
                        timestamps = dates
                    tag_data[tagname] = value_list
                except Exception as e:
                    print(f"Error processing tag '{tagname}' for well '{well_name}': {e}")

            if not tag_data or timestamps is None:
                ax_left.set_title(f"{well_name} (No data)")
                ax_left.axis("off")
                continue

            ax_list = [ax_left]
            color_idx = 0

            # Plot injectivity (left y-axis)
            for tagname in injectivity_tags:
                if tagname in tag_data:
                    label = f"{tagname} [-]"
                    ax_left.plot(timestamps, tag_data[tagname],
                                 color=color_cycle[color_idx], label=label)
                    ax_left.set_ylabel(label, color=color_cycle[color_idx])
                    ax_left.tick_params(axis='y', labelcolor=color_cycle[color_idx])
                    ax_left.yaxis.set_major_locator(ticker.MaxNLocator(nbins=5))
                    ax_left.grid(True, linestyle='--', alpha=0.4, axis='y')
                    # Add vertical gridlines
                    ax_left.grid(True, linestyle='--', alpha=0.4, axis='x')
                    color_idx += 1
                    break  # Only one injectivity on left axis
            else:
                # If no injectivity tag found, still add vertical gridlines
                ax_left.grid(True, linestyle='--', alpha=0.4, axis='x')

            # Plot other tags (right y-axes)
            for tagname in other_tags:
                if tagname in tag_data:
                    units = self.get_units(tagname)
                    ax_new = ax_left.twinx()
                    ax_new.spines['right'].set_position(("axes", 1 + 0.1 * (len(ax_list) - 1)))
                    label = f"{tagname} {units}"
                    ax_new.plot(timestamps, tag_data[tagname],
                                color=color_cycle[color_idx], label=label)
                    ax_new.set_ylabel(label, color=color_cycle[color_idx])
                    ax_new.tick_params(axis='y', labelcolor=color_cycle[color_idx])
                    ax_new.yaxis.set_major_locator(ticker.MaxNLocator(nbins=5))
                    ax_new.grid(True, linestyle='--', alpha=0.4, axis='y')
                    # Add vertical gridlines for right axes as well (optional, usually not needed)
                    ax_new.grid(True, linestyle='--', alpha=0.4, axis='x')
                    ax_list.append(ax_new)
                    color_idx += 1

            ax_left.set_title(f"{well_name}", fontsize=10)
            ax_left.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax_left.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M"))
            ax_left.tick_params(axis='x', labelrotation=45, labelsize=8)

        # Default to A4 landscape in inches
        width, height = 11.69, 8.27
        fig.set_size_inches(width, height)
        self.pdf_object.savefig(fig, bbox_inches="tight")
        plt.close(fig)

    def add_production_report(self, prod_wells, tagnames):
        num_wells = len(prod_wells)
        if num_wells == 0:
            return

        fig, axes = plt.subplots(num_wells, 1, sharex=True)
        if num_wells == 1:
            axes = [axes]  # Ensure iterable

        fig.suptitle("Production wells report", fontsize=16, fontweight="bold")
        color_cycle = plt.cm.tab10.colors

        # Separate annulus pressure tags and others, preserving order
        annulus_p_tags = [tn for tn in tagnames if "annulus" in tn.lower()]
        other_tags = [tn for tn in tagnames if "annulus" not in tn.lower()]

        for idx, (well_name, ax_left) in enumerate(zip(prod_wells, axes)):
            self.select_unit(well_name)

            tag_data = {}
            timestamps = None

            # Collect tag data
            for tagname in tagnames:
                value_list, datestamp_list = self.get_data(tagname)
                if not value_list or not datestamp_list:
                    continue
                try:
                    dates = [datetime.fromisoformat(ts.replace("Z", "")) for ts in datestamp_list]
                    if timestamps is None:
                        timestamps = dates
                    tag_data[tagname] = value_list
                except Exception as e:
                    print(f"Error processing tag '{tagname}' for well '{well_name}': {e}")

            if not tag_data or timestamps is None:
                ax_left.set_title(f"{well_name} (No data)")
                ax_left.axis("off")
                continue

            ax_list = [ax_left]
            color_idx = 0

            # Plot annulus pressures (left y-axis)
            for tagname in annulus_p_tags:
                if tagname in tag_data:
                    # Determine units for annulus tags, default to [bar]
                    units = self.get_units(tagname)
                    label = f"{tagname} {units}"
                    ax_left.plot(timestamps, tag_data[tagname],
                                 color=color_cycle[color_idx], label=label)
                    ax_left.set_ylabel(label, color=color_cycle[color_idx])
                    ax_left.tick_params(axis='y', labelcolor=color_cycle[color_idx])
                    ax_left.yaxis.set_major_locator(ticker.MaxNLocator(nbins=5))
                    ax_left.grid(True, linestyle='--', alpha=0.4, axis='y')
                    ax_left.grid(True, linestyle='--', alpha=0.4, axis='x')  # vertical gridlines
                    color_idx += 1
            else:
                # If no annulus pressure tag found, still add vertical gridlines on left axis
                ax_left.grid(True, linestyle='--', alpha=0.4, axis='x')

            # Plot other tags (right y-axes)
            for tagname in other_tags:
                if tagname in tag_data:
                    # Units for other tags, extend if needed
                    units = self.get_units(tagname)
                    ax_new = ax_left.twinx()
                    ax_new.spines['right'].set_position(("axes", 1 + 0.1 * (len(ax_list) - 1)))
                    label = f"{tagname} {units}"
                    ax_new.plot(timestamps, tag_data[tagname],
                                color=color_cycle[color_idx], label=label)
                    ax_new.set_ylabel(label, color=color_cycle[color_idx])
                    ax_new.tick_params(axis='y', labelcolor=color_cycle[color_idx])
                    ax_new.yaxis.set_major_locator(ticker.MaxNLocator(nbins=5))
                    ax_new.grid(True, linestyle='--', alpha=0.4, axis='y')
                    ax_new.grid(True, linestyle='--', alpha=0.4, axis='x')
                    ax_list.append(ax_new)
                    color_idx += 1

            ax_left.set_title(f"{well_name}", fontsize=10)
            ax_left.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax_left.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M"))
            ax_left.tick_params(axis='x', labelrotation=45, labelsize=8)

        width, height = 11.69, 8.27
        fig.set_size_inches(width, height)
        self.pdf_object.savefig(fig, bbox_inches="tight")
        plt.close(fig)

    def add_esp_report(self, esps, options):
        rcParams['figure.figsize'] = [11.69, 8.27]  # A4 landscape
        color_cycle = plt.cm.tab10.colors
        plots_per_page = 6  # 2 columns x 3 rows
        ncols = 2
        nrows = 3

        for esp in esps:
            self.select_unit(esp)

            selected_plots = [
                (key, opt['tagname'], opt.get('min'), opt.get('max'))
                for key, opt in options.items()
                if opt.get('checked') and 'tagname' in opt
            ]

            total_plots = len(selected_plots)
            total_pages = ceil(total_plots / plots_per_page)

            for page_index in range(total_pages):
                fig, axes = plt.subplots(nrows=nrows, ncols=ncols, sharex=True)
                axes = axes.flatten()

                fig.suptitle(f"ESP Report - {esp} - Page {page_index + 1}",
                             fontsize=16, fontweight="bold")
                fig.subplots_adjust(left=0.06, right=0.95,
                                    top=0.88, bottom=0.10,
                                    wspace=0.2, hspace=0.5)

                for i in range(plots_per_page):
                    subplot_index = page_index * plots_per_page + i
                    if subplot_index >= total_plots:
                        axes[i].axis("off")
                        continue

                    key, tagname, min_val, max_val = selected_plots[subplot_index]
                    ax = axes[i]

                    value_list, datestamp_list = self.get_data(tagname)
                    if not value_list or not datestamp_list:
                        ax.set_title(f"{tagname} (No data)")
                        ax.axis("off")
                        continue

                    try:
                        timestamps = [datetime.fromisoformat(ts.replace("Z", ""))
                                      for ts in datestamp_list]
                    except Exception as e:
                        print(f"Error processing tag '{tagname}' for ESP '{esp}': {e}")
                        ax.set_title(f"{tagname} (Error)")
                        ax.axis("off")
                        continue

                    units = self.get_units(tagname)
                    color = color_cycle[i % len(color_cycle)]

                    ax.plot(timestamps, value_list, color=color)
                    ax.tick_params(axis='y', labelcolor=color)
                    ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins=5))
                    ax.grid(True, linestyle='--', alpha=0.4, axis='both')

                    # Add min/max lines and fill regions
                    try:
                        if min_val is not None:
                            min_float = float(min_val)
                            ax.axhline(y=min_float, color='green',
                                       linestyle='dotted', linewidth=1)
                            ax.fill_between(timestamps, ax.get_ylim()[0],
                                            min_float, color='#d6f5d6',
                                            alpha=0.4)
                    except ValueError:
                        pass  # Ignore invalid min_val

                    try:
                        if max_val is not None:
                            max_float = float(max_val)
                            ax.axhline(y=max_float, color='green',
                                       linestyle='dotted', linewidth=1)
                            ax.fill_between(timestamps, max_float,
                                            ax.get_ylim()[1], color='#d6f5d6',
                                            alpha=0.4)
                    except ValueError:
                        pass  # Ignore invalid max_val

                    ax.set_title(f"{tagname} {units}", fontsize=10)
                    ax.set_xlabel("Date")
                    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
                    ax.tick_params(axis='x', labelrotation=45, labelsize=8)

                for j in range(len(selected_plots) % plots_per_page, plots_per_page):
                    if (page_index * plots_per_page + j) >= total_plots:
                        axes[j].axis("off")

                for ax in axes:
                    ax.tick_params(axis='x', labelbottom=True, pad=2)

                fig.set_size_inches(11.69, 8.27)  # A4 landscape
                self.pdf_object.savefig(fig, bbox_inches="tight")
                plt.close(fig)

    def add_stats_table(self, inj_wells, prod_wells):
        all_stats_data = []

        # Tagnames for values to be added in the stats table
        inj_well_tagnames = ['injectionwell_flow.measured',
                             'injectionwell_wellhead_pressure.measured',
                             'injectionwell_annulus_pressure.measured']
        prod_well_tagnames = ['productionwell_annulus_a_pressure.measured']

        # First add injection well stats, then production well stats
        all_stats_data += self.gather_stats(inj_wells, inj_well_tagnames)
        all_stats_data += self.gather_stats(prod_wells, prod_well_tagnames)

        if not all_stats_data:
            return  # Skip if no valid stats found

        # Create DataFrame
        df = pd.DataFrame(all_stats_data, columns=[
            "Unit Name", "Tag Name", "Min Value", "Max Value",
            "Mean Value", "Std Dev", "Timestamp of Max"
        ])

        # Create figure and table
        fig, ax = plt.subplots()
        ax.axis("tight")
        ax.axis("off")

        ax.set_title(f"Summary table for the period {self.start_datestamp_title} - "
                     f"{self.end_datestamp_title}", fontsize=14, fontweight="bold", pad=20)

        table = ax.table(
            cellText=df.values,
            colLabels=df.columns,
            cellLoc='center',
            loc='center',
            colColours=["lightgray"] * df.shape[1]
        )

        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.auto_set_column_width(col=list(range(len(df.columns))))

        # Save figure to PDF
        width, height = 11.69, 8.27
        fig.set_size_inches(width, height)
        self.pdf_object.savefig(fig, bbox_inches="tight", pad_inches=0.5)
        plt.close(fig)

    def add_cross_plot(self, units, tagnames, plot_type):
        num_units = len(units)
        if num_units == 0 or len(tagnames) < 3:
            print("Insufficient input: need at least one unit and three tagnames.")
            return

        # Layout: Try to form a near-square grid
        ncols = ceil(sqrt(num_units))
        nrows = ceil(num_units / ncols)

        fig, axes = plt.subplots(nrows, ncols, sharex=False, sharey=False, constrained_layout=True)

        # Normalize axes to 2D list
        axes = np.array(axes).reshape(nrows, ncols)

        for idx, unit_name in enumerate(units):
            row, col = divmod(idx, ncols)
            ax = axes[row][col]

            self.select_unit(unit_name)
            tagname_y = tagnames[0]
            tagname_x = tagnames[1]
            tagname_z = tagnames[2]

            y_data, _ = self.get_data(tagname_y)
            x_data, _ = self.get_data(tagname_x)

            if not y_data or not x_data:
                print(f"[{unit_name}] Missing data for x or y tag.")
                ax.set_title(f"{unit_name} (No data)")
                ax.axis("off")
                continue

            if tagname_z.lower() == "datestamp":
                _, datestamps_z = self.get_data(tagname_y)  # shared timestamps
                try:
                    z_datetimes = [
                        datetime.fromisoformat(ts.replace("Z", "")) for ts in datestamps_z
                    ]
                    z_data = [dt.timestamp() for dt in z_datetimes]
                    z_units = ""
                except Exception as e:
                    print(f"[{unit_name}] Failed to parse datestamp for z: {e}")
                    ax.set_title(f"{unit_name} (Invalid datestamp)")
                    ax.axis("off")
                    continue
            else:
                z_data, _ = self.get_data(tagname_z)
                if not z_data:
                    print(f"[{unit_name}] Missing data for z tag.")
                    ax.set_title(f"{unit_name} (No z data)")
                    ax.axis("off")
                    continue
                z_units = self.get_units(tagname_z)
                z_datetimes = None

            x_units = self.get_units(tagname_x)
            y_units = self.get_units(tagname_y)

            # Scatter plot
            scatter = ax.scatter(x_data, y_data, c=z_data, cmap="viridis", edgecolors='none')
            ax.set_title(f"{unit_name}", fontsize=10)
            ax.set_xlabel(f"{tagname_x} {x_units}", fontsize=8)
            ax.set_ylabel(f"{tagname_y} {y_units}", fontsize=8)
            ax.tick_params(labelsize=8)

            # Colorbar
            cbar = fig.colorbar(scatter, ax=ax)
            if tagname_z.lower() == "datestamp" and z_datetimes:
                formatter = ticker.FuncFormatter(
                    lambda val, pos: datetime.fromtimestamp(val).strftime("%m/%d %H:%M")
                )
                cbar.ax.yaxis.set_major_formatter(formatter)
                cbar.set_label(f"{tagname_z}", fontsize=8)
            else:
                cbar.set_label(f"{tagname_z} {z_units}", fontsize=8)

        # Turn off unused subplots
        total_axes = nrows * ncols
        if total_axes > num_units:
            for empty_idx in range(num_units, total_axes):
                row, col = divmod(empty_idx, ncols)
                axes[row][col].axis("off")

        # Title
        fig.suptitle(f"{plot_type} Cross Plots", fontsize=14, fontweight="bold")

        # A4 landscape size
        fig.set_size_inches(11.69, 8.27)
        self.pdf_object.savefig(fig, bbox_inches="tight", pad_inches=0.3)
        plt.close(fig)

    def compute_skin_lines(self, inputs, flow_array, skin_array):
        well_name = inputs["well_name"]
        print(f'Computing skin lines for well: {well_name}')

        app_IWM = InjectionWellMonitoring()
        app_IWM.load_plant(self.project_path, self.project_name)
        app_IWM.select_unit(well_name)

        print(app_IWM.unit.name)
        print(app_IWM.unit.to_units[0].name)

        well_param = app_IWM.unit.parameters['property']
        reservoir_param = app_IWM.unit.to_units[0].parameters['property']

        # Get inputs for skin lines
        boundary = {
            'min_flow_plot': inputs['min_flow_plot'],
            'max_flow_plot': inputs['max_flow_plot'],
            'no_interval_flow_plot': inputs['no_interval_flow_plot'],
            'min_skin_plot': inputs['min_skin_plot'],
            'max_skin_plot': inputs['max_skin_plot'],
            'no_interval_skin_plot': inputs['no_interval_skin_plot'],
            'max_pressure': None,
            'max_flow_rate': None,
            'wellbore_radius': well_param['wellbore_radius'][0],
            'start_time': inputs['starttime'],
            'end_time': inputs['endtime']
        }
        app_IWM.set_input(boundary)

        parameters = {
            'reservoir_pressure': reservoir_param['reservoir_pressure'][0],
            'reservoir_radius': reservoir_param['reservoir_radius'][0],
            'reservoir_permeability': reservoir_param['reservoir_permeability'][0],
            'reservoir_thickness': reservoir_param['reservoir_thickness'][0],
            'reservoir_top': reservoir_param['reservoir_top'][0],
            'liquid_density': reservoir_param['liquid_density'][0],
            'liquid_viscosity': reservoir_param['liquid_viscosity'][0],
        }
        app_IWM.init_parameters(parameters)
        app_IWM.get_data()
        app_IWM.calculate_skin_lines()

        inputs = app_IWM.get_input()
        outputs = app_IWM.get_output()

        results = {'injection_pressure': outputs['injection_pressure'],
                   'max_cal_P_inj': outputs['max_cal_P_inj']
                   }
        return results

    def convert_numeric_values(self, inputs):
        for key, val in inputs.items():
            # Try to convert to float first
            try:
                num = float(val)
                # If no error, check if it can be an int
                if num.is_integer():
                    inputs[key] = int(num)
                else:
                    inputs[key] = num
            except (ValueError, TypeError):
                # Not a number, leave as is
                pass
        return inputs

    def add_cross_plot_with_skin_lines(self, units, tagnames, inputs):
        # Make sure numeric values are not in string format
        inputs = self.convert_numeric_values(inputs)

        num_units = len(units)
        if num_units == 0 or len(tagnames) < 3:
            print("Insufficient input: need at least one unit and three tagnames.")
            return

        ncols = ceil(sqrt(num_units))
        nrows = ceil(num_units / ncols)

        fig, axes = plt.subplots(nrows, ncols, sharex=False, sharey=False, constrained_layout=True)
        axes = np.array(axes).reshape(nrows, ncols)

        cmap = plt.cm.plasma

        colors = [cmap(i / (inputs['no_interval_skin_plot'] - 1))
                  for i in range(inputs['no_interval_skin_plot'])]

        for idx, unit_name in enumerate(units):
            row, col = divmod(idx, ncols)
            ax = axes[row][col]

            self.select_unit(unit_name)

            tagname_y, tagname_x, tagname_z = tagnames[:3]

            y_data, _ = self.get_data(tagname_y)  # Pressure in bar
            x_data, _ = self.get_data(tagname_x)  # Flow in m³/h

            if not y_data or not x_data:
                print(f"[{unit_name}] Missing data for x or y tag.")
                ax.set_title(f"{unit_name} (No data)")
                ax.axis("off")
                continue

            skin_array = np.linspace(inputs['min_skin_plot'],
                                     inputs['max_skin_plot'],
                                     inputs['no_interval_skin_plot'])
            flow_array = np.linspace(inputs['min_flow_plot'] / 3600,
                                     inputs['max_flow_plot'] / 3600,
                                     inputs['no_interval_flow_plot'])

            # Compute skin lines matrix
            inputs['well_name'] = unit_name
            skin_results = self.compute_skin_lines(inputs, flow_array, skin_array)
            pressure_matrix = skin_results['injection_pressure']

            # Z data for coloring scatter
            if tagname_z.lower() == "datestamp":
                _, datestamps_z = self.get_data(tagname_y)
                try:
                    z_datetimes = [
                        datetime.fromisoformat(ts.replace("Z", "")) for ts in datestamps_z
                    ]
                    z_data = [dt.timestamp() for dt in z_datetimes]
                    z_units = ""
                except Exception as e:
                    print(f"[{unit_name}] Failed to parse datestamp for z: {e}")
                    ax.set_title(f"{unit_name} (Invalid datestamp)")
                    ax.axis("off")
                    continue
            else:
                z_data, _ = self.get_data(tagname_z)
                if not z_data:
                    print(f"[{unit_name}] Missing data for z tag.")
                    ax.set_title(f"{unit_name} (No z data)")
                    ax.axis("off")
                    continue
                z_units = self.get_units(tagname_z)

            x_units = self.get_units(tagname_x)
            y_units = self.get_units(tagname_y)

            # Scatter plot
            scatter = ax.scatter(x_data, y_data, c=z_data, cmap="viridis", edgecolors='none')
            ax.set_title(f"{unit_name}", fontsize=10)
            ax.set_xlabel(f"{tagname_x} {x_units}", fontsize=8)
            ax.set_ylabel(f"{tagname_y} {y_units}", fontsize=8)
            ax.tick_params(labelsize=8)

            # Plot skin lines (flow in m³/h, pressure in bar)
            flow_hr = flow_array * 3600
            for i, skin in enumerate(skin_array):
                ax.plot(flow_hr, pressure_matrix[i],
                        color=colors[i], linestyle='dotted',
                        linewidth=1,
                        label=f"Skin = {skin}")

            ax.legend(fontsize=8, title="Skin Values")

            # Colorbar
            cbar = fig.colorbar(scatter, ax=ax)
            if tagname_z.lower() == "datestamp":
                formatter = ticker.FuncFormatter(
                    lambda val, pos: datetime.fromtimestamp(val).strftime("%m/%d %H:%M")
                )
                cbar.ax.yaxis.set_major_formatter(formatter)
            cbar.set_label(f"{tagname_z} {z_units}", fontsize=8)

        # Hide unused axes
        total_axes = nrows * ncols
        if total_axes > num_units:
            for empty_idx in range(num_units, total_axes):
                row, col = divmod(empty_idx, ncols)
                axes[row][col].axis("off")

        fig.suptitle(f"{inputs['plot_type']} Cross Plots with Skin Lines",
                     fontsize=14, fontweight="bold")
        fig.set_size_inches(11.69, 8.27)  # A4 landscape
        self.pdf_object.savefig(fig, bbox_inches="tight", pad_inches=0.3)
        plt.close(fig)

    def export_pdf(self):
        self.pdf_object.close()
        print("Plots exported to plots.pdf")

        # Move to the beginning of the buffer
        self.pdf_buffer.seek(0)

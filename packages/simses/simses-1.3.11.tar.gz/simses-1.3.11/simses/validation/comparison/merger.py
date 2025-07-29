import os
import re
import webbrowser
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
from simses.commons.config.validation.general import GeneralValidationConfig
from simses.analysis.evaluation.plotting.plotly_plotting import PlotlyPlotting
from simses.analysis.evaluation.plotting.plotter import Plotting
from simses.validation.comparison.abstract_comparison import Comparison
from simses.validation.comparison.result import ComparisonResult


class ComparisonMerger:

    OUTPUT_NAME: str = 'Validation.html'

    def __init__(self, result_path: str, config: GeneralValidationConfig, version: str):
        self.__file_name: str = os.path.join(result_path, self.OUTPUT_NAME)
        self.__simulation_name: str = result_path.split('/')[-3]
        self.__validation_name: str = config.validation_name
        self.__version: str = version
        self.__merge_results: bool = config.merge_validation
        self.__logo_path: str = config.logo_file

    def merge(self, comparisons: [Comparison]) -> None:

        """
        Writes comparison results and figures in a html file.

        Parameters:
            comparisons:   List of comparisons.
        """
        if not self.__merge_results:
            return
        with open(self.__file_name, 'w') as outfile:
            outfile.write("<!DOCTYPE html><html><head></head><body>")
            outfile.write(self.__html_header())
            outfile.write(self.__html_style())
            self.__write_comparisons(comparisons, outfile)
            outfile.write("<br>")
            # outfile.write("<section><b>System parameters</b></section>")
            # outfile.write(Plotting.convert_to_html(SystemParameterFigureGenerator(self.__system_parameters).generate()))
            outfile.write("</body></html>")
        webbrowser.open(self.__file_name, new=2)  # open in new tab

    def __write_comparisons(self, comparisons: [Comparison], outfile) -> None:
        for comparison in comparisons:
            if comparison.should_be_considered:
                section = re.sub('([A-Z0-9])', r' \1', comparison.get_file_name())[
                          :-4]  # make filename human readable
                outfile.write("<section><b>" + section + "</b></section>")
                results = list()
                for result in comparison.evaluation_results:
                    result: ComparisonResult = result
                    # outfile.write(result.to_console() + "<br>")
                    results.append(result.to_csv())
                results_df = pd.DataFrame(results, columns=ComparisonResult.get_header())
                outfile.write(Plotting.convert_to_html(self.__to_table(results_df)))
                for figure in comparison.get_figures():
                    outfile.write(Plotting.convert_to_html(figure))
                outfile.write("<br><br>")

    def __to_table(self, result: pd.DataFrame) -> go.Table:
        """Returns EvaluationResult as a Table."""
        table_of_results = go.Figure(data=[go.Table(
            columnwidth=[400, 150, 150],
            header=dict(values=list(result.columns), fill_color='#0065BD', font_color="white",
                        line_color="#0065BD"),
            cells=dict(values=[list(result.Description), list(result.Value), list(result.Unit)],
                       height=20, font_color="black", align='left', line_color=PlotlyPlotting.Color.SOC_BLUE,
                       fill_color='white'))])
        table_of_results.update_layout(width=700)
        return table_of_results

    def __html_header(self) -> str:
        header = '''<header>
           <p style="color:white;">Simulation name: ''' + self.__simulation_name + '''</p>
           <p style="color:white;">Date / Time:    ''' + self.__simulation_time + '''</p>
           <p style="color:white;">Version:    ''' + self.__version + '''</p>
           <img src=''' + self.__logo_path + ''' alt="SimSES" width=300>
           </header>'''

        return header

    def __html_style(self) -> str:
        style = '''<style>
               body{
                       background-color: white;
                       margin-left: 1cm;
                       margin-right: 1cm;

                       border: 5px solid #0065BD;
                       padding: 10px;
                       border-radius: 8px;
               }
               header {
                       background-color : #0065BD;
                       border: 1px solid white;
                       padding: 10px;
                       border-radius: 8px;
               }
               img {
                       display: block;
                       margin-left: auto;
                       margin-right: auto;
               }

          </style>'''

        return style

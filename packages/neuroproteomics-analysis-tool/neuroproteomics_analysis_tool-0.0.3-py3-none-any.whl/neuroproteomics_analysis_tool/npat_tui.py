from dotenv import dotenv_values
from neuroproteomics_analysis_tool.npat import NPAT
import numpy as np
import os
import pandas as pd
from textual import on
from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll, VerticalScroll
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.widgets import TabbedContent, TabPane, Footer, Header,Label, Markdown, ListItem, ListView, Input, Static, Button, SelectionList, DataTable, Select


HOMEPAGE = """
# NeuroProteomics Analysis Tool (NPAT)

Welcome to the NeuroProteomics Analysis Tool (NPAT) brought to you by Berco Analytics and MoZeek Bio.
"""


def get_env_files(directory: str) -> list[str]:
    env_files = []
    for filename in os.listdir(directory):
        if filename.endswith(".env"):
            env_files.append(filename)
    return env_files


class NPATApp(App):
    """Need to add description"""
    CSS_PATH = ['tcss/analyses_analyses_layout.tcss',
                'tcss/analyses_enrichment_analysis_layout.tcss',
                'tcss/analyses_relative_expression_layout.tcss',
                'tcss/analyses_samples_layout.tcss',
                'tcss/database_connection_layout.tcss',
                'tcss/feedback_layout.tcss',
                'tcss/general_layout.tcss',
                'tcss/homepage_layout.tcss',]

    env_file_dir: reactive[str] = reactive(os.getcwd())
    env_file_path: reactive[str | None] = reactive(None)
    analyses_dict: reactive[dict[str, NPAT]] = reactive({})
    analysis_selection: reactive[str | None] = reactive(None)
    active_analysis: reactive[str | None] = reactive(None)
    sample_ids: reactive[dict[str, list]] = reactive({})
    relative_expressions: reactive[dict[str, pd.DataFrame]] = reactive({})
    enrichment_analyses: reactive[dict[str, pd.DataFrame]] = reactive({})


    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def convert_dataframe_to_datatable(self, dataframe: pd.DataFrame, id:str, fixed_columns:int=0) -> None:
        self.query_one(f"#{id}").clear(columns=True)

        df_all_str = dataframe.copy(deep=True)
        numeric_column_names = df_all_str.select_dtypes(include=np.number).columns.tolist()
        for col in numeric_column_names:
            df_all_str[col] = df_all_str[col].astype(str)

        datatable = self.query_one(f'#{id}')
        datatable.cursor_type = "row"
        datatable.zebra_stripes = True
        datatable.fixed_columns = fixed_columns

        rows = list(df_all_str.itertuples(index=False, name=None))

        datatable.add_columns(*df_all_str.columns)
        datatable.add_rows(rows)

    def compose(self) -> ComposeResult:
        yield Header()
        #Footer to show key bindings
        yield Footer()

        with TabbedContent(initial='homepage_tab'):
            with TabPane(title='Homepage', id='homepage_tab'):
                yield Markdown(HOMEPAGE)
            with TabPane(title='Database Connection', id='database_tab'):
                with HorizontalScroll():
                    with VerticalScroll(id='env_file_pane'):
                        yield Static(id="env_dir_prompt")

                    with VerticalScroll(id='connection_info_pane', classes='hidden'):
                        yield Static(id='env_file_prompt')

                        with HorizontalScroll():
                            yield Static("DB_DRIVER: ", id='db_driver_label', classes='label')
                            yield Static(id='db_driver', classes='value')
                        with HorizontalScroll():
                            yield Static("DB_NAME: ", id='db_name_label', classes='label')
                            yield Static(id="db_name", classes='value')
                        with HorizontalScroll():
                            yield Static("DB_USER: ", id='db_user_label', classes='label')
                            yield Static(id='db_user', classes='value')
                        with HorizontalScroll():
                            yield Static("DB_PASSWORD: ", id='db_password_label', classes='label')
                            yield Static(id='db_password', classes='value')
                        with HorizontalScroll():
                            yield Static("DB_HOST: ", id='db_host_label', classes='label')
                            yield Static(id='db_host', classes='value')
                        with HorizontalScroll():
                            yield Static("DB_PORT: ", id='db_port_label', classes='label')
                            yield Static(id='db_port', classes='value')
                        with VerticalScroll(id='npat_connection_pane'):
                            yield Static(
                                '\nEnter an analysis name and click \"Connect to Database\" to create a new analysis')
                            yield Input(placeholder='Ex. Male Patient 35', id='analysis_name')
                            yield Button('Connect to Database', id='connect_db_button')
                            yield Static("\nActive Analyses")
                            yield ListView(id='active_analyses')

            with TabPane(title='Analyses', id='analyses_tab'):

                with TabbedContent(initial='analyses_homepage'):
                    with TabPane(title='Analyses', id='analyses_homepage'):
                        with HorizontalScroll():
                            with VerticalScroll():
                                yield Static('Set an active analysis.\n')
                                yield Static(id='active_analysis')
                                yield ListView(id='active_analyses_2')
                                yield Button('Set Active Analysis', id='set_active_analysis')
                            with VerticalScroll():
                                pass
                    with TabPane(title='Samples', id='samples_tab', classes='hidden'):
                        with HorizontalScroll(id='samples_top_pane'):
                            with VerticalScroll():
                                yield Static("Available Samples")
                                yield SelectionList(id='available_samples')
                            with VerticalScroll():
                                yield Static("Selected Samples")
                                yield ListView(id='selected_samples')
                                yield Button("Set Selected Samples", id='set_selected_samples')
                            with VerticalScroll():
                                yield Static("Active Samples")
                                yield ListView(id='active_samples')
                        with HorizontalScroll(id='samples_bottom_pane'):
                            yield Input(placeholder="Directory of gene abundance csv files to upload", id='gene_abundance_directory')
                            yield Button("Upload", id='upload_samples')

                    with TabPane(title='Relative Expression', id='relative_expression_tab', classes='hidden'):
                        yield Static('Relative Expression Description')
                        with HorizontalScroll():
                            with VerticalScroll(id='relative_expression_left_pane'):
                                yield Static('Active Samples')
                                yield ListView(id='active_samples_2')
                                yield Button("Calculate Relative Expression", id='calculate_relative_expression')
                            with VerticalScroll(id='relative_expression_rightq_pane'):
                                yield DataTable(id='relative_expression')
                                with HorizontalScroll():
                                    yield Input(placeholder='Path to export relative expression.', id='relative_expression_path')
                                    yield Button("Export", id='export_relative_expression_button')

                    with TabPane(title='Enrichment Analysis', id='enrichment_analysis_tab', classes='hidden'):
                        yield Static('Enrichment Analysis Description')
                        with VerticalScroll(id='enrichment_analysis_options'):
                            yield Static("Select Target Expression")
                            yield Select([('suppressed','suppressed'), ('overexpressed', 'overexpressed')],id='expression_selection', allow_blank=False)
                            yield Button('Run Enrichment Analysis', id='run_enrichment_analysis')
                        with VerticalScroll(id='enrichment_analysis_pane'):
                            yield DataTable(id='enrichment_analysis')
                            with HorizontalScroll():
                                yield Input(placeholder='Path to export enrichment analysis', id='enrichment_analysis_path')
                                yield Button("Export", id='export_enrichment_analysis_button')

            with TabPane(title='Feedback', id='feedback_tab'):
                yield Static("Thank you for using the NeuroProteomics Analysis Tool. We are looking for feedback to improve our tool. This page will be updated to allow submission of feedback.")
                # yield Select(prompt="Category (User Interface, Functionality)")
                # yield Select(prompt="SubCategory (Styling, Format/Layout, Errors/Performance, Relative Expression, Enrichment Analysis, Graph Analysis, New Analysis)")
                # yield Select(prompt="Location")
                # yield Input('Notes')
                # yield Button("Submit")

    def action_show_tab(self, tab: str) -> None:
        """Switch to a new tab"""
        self.get_child_by_type(TabbedContent).active = tab

    @on(message_type=Input.Submitted, selector="#env_dir_input")
    def env_dir_submitted(self):
        self.env_file_dir = self.query_one("#env_dir_input").value

    def watch_env_file_dir(self) -> None:
        container = self.query_one("#env_file_pane")

        if os.path.isdir(self.env_file_dir):
            env_files = get_env_files(self.env_file_dir)

            if len(env_files) == 0:
                self.query_one("#env_dir_prompt").update(f'No .env files were found in the directory: {self.env_file_dir}. Please provide a directory containing .env files with database connection information.')

                try:
                    self.query_one("#env_dir_input").value = ""

                except NoMatches:
                    container.mount(Input(placeholder='Please provide path to directory containing .env files', id='env_dir_input'))
            else:
                self.query_one("#env_dir_prompt").update(f'Please select the .env file you would like to use to connect to your database. Must contain the following variables: DB_DRIVER, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT\n\nDirectory: {self.env_file_dir}')
                try:
                    self.query_one("#env_dir_input").remove()
                except NoMatches:
                    pass
                container.mount(ListView(*[ListItem(Label(renderable=f'{file}', name=os.path.join(self.env_file_dir, file))) for file in env_files], id='env_files'))
        else:
            self.query_one("#env_dir_prompt").update(f"The following directory couldn't be found: {self.env_file_dir}. Please provide a directory containing .env files with database connection information.")
            self.query_one("#env_dir_input").value = ""

    @on(ListView.Selected, selector="#env_files")
    def env_file_submitted(self, selection: ListView.Selected):
        self.env_file_path = selection.item.query_one(Label).name

    def watch_env_file_path(self) -> None:
        if self.env_file_path:
            self.query_one("#connection_info_pane").remove_class("hidden")
            self.query_one("#env_file_prompt").update(f"You have selected the following .env file: {self.env_file_path}\n\nHover values to view.\n")
            connection_info = dotenv_values(self.env_file_path)
            self.query_one("#db_driver").update(connection_info.get("DB_DRIVER", "Value Missing"))
            self.query_one("#db_name").update(connection_info.get("DB_NAME", "Value Missing"))
            self.query_one("#db_user").update(connection_info.get("DB_USER", "Value Missing"))
            self.query_one("#db_password").update(connection_info.get("DB_PASSWORD", "Value Missing"))
            self.query_one("#db_host").update(connection_info.get("DB_HOST", "Value Missing"))
            self.query_one("#db_port").update(connection_info.get("DB_PORT", "Value Missing"))


    @on(Button.Pressed, selector="#connect_db_button")
    def connect_db_button_pressed(self) -> None:
        analysis_name = self.query_one("#analysis_name").value
        if analysis_name.strip():
            self.analyses_dict[analysis_name] = NPAT(analysis_name=analysis_name, env_file=self.env_file_path)
            self.mutate_reactive(NPATApp.analyses_dict)

        self.query_one("#analysis_name").value = ""

    def watch_analyses_dict(self) -> None:
        self.query_one("#active_analyses").clear()
        self.query_one("#active_analyses").extend([ListItem(Label(renderable=analysis, name=analysis)) for analysis in self.analyses_dict])

        self.query_one("#active_analyses_2").clear()
        self.query_one("#active_analyses_2").extend([ListItem(Label(renderable=analysis, name=analysis)) for analysis in self.analyses_dict])

    @on(ListView.Selected, selector="#active_analyses_2")
    def active_analysis_selected(self, selection: ListView.Selected):
        self.analysis_selection = selection.item.query_one(Label).name

    @on(Button.Pressed, selector="#set_active_analysis")
    def set_active_analysis(self):
        self.active_analysis = self.analysis_selection
        self.query_one("#samples_tab").remove_class("hidden")

    def watch_active_analysis(self) -> None:
        self.query_one("#active_analysis").update(f"Active Analysis: {self.active_analysis}")
        if self.active_analysis:
            sample_names = [(x,x) for x in self.analyses_dict[self.active_analysis].get_sample_ids()]

            self.query_one("#available_samples").clear_options()
            self.query_one("#available_samples").add_options(sample_names)

            self.query_one("#active_samples").clear()
            self.query_one("#active_samples_2").clear()
            self.query_one("#relative_expression").clear(columns=True)
            self.query_one("#enrichment_analysis").clear(columns=True)

            if self.sample_ids.get(self.active_analysis, None):
                self.query_one("#active_samples").extend([ListItem(Label(renderable=sample, name=sample)) for sample in self.sample_ids[self.active_analysis]])
                self.query_one("#active_samples_2").extend([ListItem(Label(renderable=sample, name=sample)) for sample in self.sample_ids[self.active_analysis]])

            if type(self.relative_expressions.get(self.active_analysis, None)) == pd.DataFrame:
                df = self.relative_expressions[self.active_analysis]
                self.convert_dataframe_to_datatable(dataframe=df, id='relative_expression')

            if type(self.enrichment_analyses.get(self.active_analysis, None)) == pd.DataFrame:
                df = self.enrichment_analyses[self.active_analysis]
                self.convert_dataframe_to_datatable(dataframe=df, id='enrichment_analysis', fixed_columns=1)





    @on(SelectionList.SelectedChanged, selector="#available_samples")
    def update_selected_samples(self) -> None:
        self.query_one("#selected_samples").clear()
        self.query_one("#selected_samples").extend([ListItem(Label(renderable=sample, name=sample)) for sample in self.query_one("#available_samples").selected])

    @on(Button.Pressed, selector="#set_selected_samples")
    def set_selected_samples(self) -> None:
        self.sample_ids[self.active_analysis] = self.query_one("#available_samples").selected

        if type(self.relative_expressions.get(self.active_analysis, None)) == pd.DataFrame:
            del self.relative_expressions[self.active_analysis]

        if type(self.enrichment_analyses.get(self.active_analysis, None)) == pd.DataFrame:
            del self.enrichment_analyses[self.active_analysis]

        self.query_one("#active_samples").clear()
        self.query_one("#active_samples").extend([ListItem(Label(renderable=sample, name=sample)) for sample in self.sample_ids[self.active_analysis]])

        self.query_one("#active_samples_2").clear()
        self.query_one("#active_samples_2").extend([ListItem(Label(renderable=sample, name=sample)) for sample in self.sample_ids[self.active_analysis]])

        self.query_one("#relative_expression").clear(columns=True)
        self.query_one("#enrichment_analysis").clear(columns=True)

        self.query_one("#available_samples").deselect_all()

        self.query_one("#relative_expression_tab").remove_class("hidden")



    @on(Button.Pressed, selector="#calculate_relative_expression")
    def calculate_relative_expression(self) -> None:
        df = self.analyses_dict[self.active_analysis].get_samples(self.sample_ids[self.active_analysis])
        df = self.analyses_dict[self.active_analysis].relative_expression_filter(df)
        self.relative_expressions[self.active_analysis] = df
        self.convert_dataframe_to_datatable(dataframe=df, id='relative_expression')

        self.query_one("#enrichment_analysis").clear(columns=True)

        if type(self.enrichment_analyses.get(self.active_analysis, None)) == pd.DataFrame:
            del self.enrichment_analyses[self.active_analysis]

        self.query_one("#enrichment_analysis_tab").remove_class("hidden")



    @on(Button.Pressed, selector="#run_enrichment_analysis")
    def run_enrichment_analysis(self) -> None:
        expression_selection = self.query_one('#expression_selection').selection
        if self.relative_expressions[self.active_analysis].expression.value_counts().get(expression_selection):
            df = self.analyses_dict[self.active_analysis].enrichment_analysis(gene_expression_df=self.relative_expressions[self.active_analysis],
                                                                              expression=expression_selection)
            self.enrichment_analyses[self.active_analysis] = df
            self.convert_dataframe_to_datatable(dataframe=df, id='enrichment_analysis', fixed_columns=1)

    @on(Button.Pressed, selector="#export_relative_expression_button")
    def export_relative_expression(self) -> None:
        filepath = self.query_one("#relative_expression_path").value
        dir = os.path.dirname(filepath)
        if dir != "":
            if not os.path.isdir(dir):
                os.makedirs(dir)
        self.relative_expressions[self.active_analysis].to_csv(filepath, index=False)
        self.query_one("#relative_expression_path").value = ""

    @on(Button.Pressed, selector="#export_enrichment_analysis_button")
    def export_enrichment_analysis(self) -> None:
        filepath = self.query_one("#enrichment_analysis_path").value
        dir = os.path.dirname(filepath)
        if dir != "":
            if not os.path.isdir(dir):
                os.makedirs(dir)
        self.enrichment_analyses[self.active_analysis].to_csv(filepath, index=False)
        self.query_one("#enrichment_analysis_path").value = ""

    @on(Button.Pressed, selector="#upload_samples")
    def upload_samples(self) -> None:
        directory = self.query_one("#gene_abundance_directory").value
        if os.path.exists(directory):
            sample_ids = self.analyses_dict[self.active_analysis].get_sample_ids()
            files = os.listdir(directory)
            files = [os.path.join(directory, file) for file in files]

            table_name = self.analyses_dict[self.active_analysis].sample_table
            for file in files:
                if file.endswith('.csv'):
                    dataframe = pd.read_csv(file)
                    dataframe = dataframe[~dataframe.sample_id.isin(sample_ids)]
                    if dataframe.shape[0] > 0:
                        pd.read_csv(file).to_sql(table_name, con=self.analyses_dict[self.active_analysis].conn, if_exists='append', index=False)

        self.query_one("#gene_abundance_directory").value = ''

        sample_names = [(x, x) for x in self.analyses_dict[self.active_analysis].get_sample_ids()]

        self.query_one("#available_samples").clear_options()
        self.query_one("#available_samples").add_options(sample_names)


    def on_mount(self) -> None:
        self.title = "NeuroProteomics Analysis Tool"
        self.sub_title = "Berco Analytics/MoZeek Bio"

if __name__ == '__main__':
    NPATApp().run()
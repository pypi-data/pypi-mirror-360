import csv
from dotenv import dotenv_values
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

class DBConnection:
    def __init__(self, env_file:str) -> None:
        self.connect_to_db(env_file=env_file)

    def connect_to_db(self, env_file:str) -> None:
        """Connect to DB with information stored in .env file"""
        connection_info = dotenv_values(env_file)
        DB_DRIVER = connection_info["DB_DRIVER"]
        DB_NAME = connection_info["DB_NAME"]
        DB_USER = connection_info["DB_USER"]
        DB_PASSWORD = connection_info["DB_PASSWORD"]
        DB_HOST = connection_info["DB_HOST"]
        DB_PORT = connection_info["DB_PORT"]

        url = URL.create(
            drivername=DB_DRIVER,
            username=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )

        engine = create_engine(url)
        conn = engine.connect()

        self.engine = engine
        self.conn = conn

class NPATDB(DBConnection):
    def __init__(self, env_file:str) -> None:
        super().__init__(env_file)

    def format_proteome_data(self, proteome_tsv_path: str) -> pd.DataFrame:
        with open(proteome_tsv_path) as file:
            rd = csv.reader(file, delimiter="\t", quotechar='"')
            header = True
            proteome_data = []

            for row in rd:
                if header:
                    columns = row
                    header = False
                else:
                    gene_data = {}
                    for column, value in zip(columns, row):
                        gene_data[column] = value

                    gene = gene_data['Gene Names (primary)']
                    organism = gene_data['Organism']
                    reviewed = gene_data['Reviewed']
                    entry = gene_data['Entry']

                    if gene:
                        if gene_data.get('Gene Ontology (biological process)', False):
                            go_type = 'biological process'
                            for go in gene_data['Gene Ontology (biological process)'].split(';'):
                                tmp_dict = {
                                    'gene': gene,
                                    'pathway': go.strip(),
                                    'type': go_type,
                                    'organism': organism,
                                    'reviewed': reviewed,
                                    'entry': entry
                                }
                                proteome_data.append(tmp_dict)

                        if gene_data.get('Gene Ontology (molecular function)', False):
                            go_type = 'molecular function'
                            for go in gene_data['Gene Ontology (molecular function)'].split(';'):
                                tmp_dict = {
                                    'gene': gene,
                                    'pathway': go.strip(),
                                    'type': go_type,
                                    'organism': organism,
                                    'reviewed': reviewed,
                                    'entry': entry
                                }
                                proteome_data.append(tmp_dict)

                        if not gene_data.get('Gene Ontology (biological process)', False) and not gene_data.get(
                                'Gene Ontology (molecular function)', False):
                            go_type = None
                            tmp_dict = {
                                'gene': gene,
                                'pathway': go.strip(),
                                'type': go_type,
                                'organism': organism,
                                'reviewed': reviewed,
                                'entry': entry
                            }
                            proteome_data.append(tmp_dict)

        proteome_df = pd.DataFrame(proteome_data)
        proteome_df.sort_values('reviewed', ascending=True, inplace=True)
        proteome_df['id'] = proteome_df['gene'] + '_' + proteome_df['pathway']
        proteome_df.drop_duplicates(subset=['id'], keep='first', inplace=True)
        proteome_df.drop('id', inplace=True, axis=1)

        return proteome_df

    def create_genes_pathway_table(self, proteome_tsv_path: str) -> None:
        proteome_df = self.format_proteome_data(proteome_tsv_path)
        proteome_df.to_sql(name='pathway_genes', con=self.engine, if_exists='replace', index=False)

    def create_pathways_disease_table(self):
        pass

    def create_proteins_disease_table(self):
        pass

    def create_control_samples_table(self):
        pass

    def upload_samples_data(self):
        pass

    def creates_samples_table(self):
        pass

    def create_database(self):
        pass



# proteome_tsv_file = "./data/uniprotkb_proteome_UP000000589_2025_06_30.tsv"
# env_file = './local.env'
#
# db = NPATDB(env_file)
# db.create_genes_pathway_table(proteome_tsv_file)

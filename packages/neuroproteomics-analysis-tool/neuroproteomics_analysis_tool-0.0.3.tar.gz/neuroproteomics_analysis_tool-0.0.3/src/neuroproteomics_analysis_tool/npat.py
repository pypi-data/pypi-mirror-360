import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from dotenv import dotenv_values
from scipy.stats import ttest_ind, binomtest
from typing import NamedTuple, List
import argparse
from natsort import natsort_keygen


class Args(NamedTuple):
    """Command Line Arguments"""
    analysis_name:str
    env_file:str
    gene_col:str
    pathway_col:str
    pathway_gene_table:str
    reference_organism:str
    expected_abundance_table:str
    control_samples_table:str
    value_transformation:str
    sample_table:str
    sample_id_col:str


def get_args() -> Args:
    """Get command line arguments"""
    parser = argparse.ArgumentParser(description='NeuroProteomics Analysis Tool', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("analysis_name", help="Name/description of analysis", type=str, metavar="ANALYSIS_NAME")
    parser.add_argument("env_file", help="Path to .env file containing DB connection information", type=str, metavar=".ENV FILE", default=".env")
    parser.add_argument("-g","--gene_col", help="Name of column that contains short gene names (ex. Lipa for lysosomal acid lipase A)", type=str, metavar="GENE_COL", default="gene'")
    parser.add_argument("-p","--pathway_col", help="Name of column that contains pathway names", type=str, metavar="PATHWAY_COL", default='pathway')
    parser.add_argument("-t","--pathway_gene_table", help="Name of table in DB that contains genes info (gene name, pathway, etc)", type=str, metavar="PATHWAY_GENE_TABLE", default="pathway_genes")
    parser.add_argument("-r", "--reference_organism", help="Reference organism to use for analysis", type=str, metavar="REFERENCE_ORGANISM", default="Mus musculus", choices=["Mus musculus"])
    parser.add_argument("-e", "--expected_abundance_table", help="Table containing expected abundances", type=str, metavar="EXPECTED_ABUNDANCE", default="expected_abundances")
    parser.add_argument("-c", "--control_samples_table", help="Table containing control samples", type=str, metavar="CONTROL_SAMPLES", default="control_samples")
    parser.add_argument("-v", "--value_transformation", help="Type of transformation to apply before analysis", type=str, metavar="VALUE_TRANSFORMATION", default="log2", choices=["log2"])
    parser.add_argument("-s","--sample_table", help="Name of table in DB that contains samples", type=str, metavar="SAMPLE_TABLE", default='test_input')
    parser.add_argument("-i","--sample_id_col", help="Name of column in sample_table that contains sample IDs", type=str, metavar="SAMPLE_ID_COL", default='sample_id')





    args = parser.parse_args()
    return Args(analysis_name=args.analysis_name,
                env_file=args.env_file,
                gene_col=args.gene_col,
                pathway_col=args.pathway_col,
                pathway_gene_table=args.pathway_gene_table,
                reference_organism=args.reference_organism,
                expected_abundance_table=args.expected_abundance_table,
                control_samples_table=args.control_samples_table,
                value_transformation=args.value_transformation,
                sample_table=args.sample_table,
                sample_id_col=args.sample_id_col
                )


class NPAT:
    """NeuroProteomics Analysis Tool"""

    def __init__(self,
                 analysis_name:str,
                 env_file:str = "./.env",
                 gene_col:str = 'gene',
                 pathway_col:str = 'pathway',
                 pathway_gene_table:str = 'pathway_genes_no_duplicates',
                 reference_organism:str = 'Mus musculus',
                 expected_abundance_table:str = 'expected_abundance',
                 control_samples_table:str = 'control_samples',
                 value_transformation:str = 'log2',
                 sample_table:str = 'test_input',
                 sample_id_col:str = 'sample_id',
                 ):
        self.analysis_name = analysis_name
        self.connect_to_db(env_file=env_file)
        self.gene_col:str = gene_col
        self.pathway_col:str = pathway_col
        self.pathway_gene_table:str = pathway_gene_table
        self.reference_organism:str = reference_organism
        self.expected_abundance_table:str = expected_abundance_table
        self.control_samples_table:str = control_samples_table
        self.value_transformation:str = value_transformation
        self.sample_table:str = sample_table
        self.sample_id_col:str = sample_id_col

    def __str__(self):
        return self.analysis_name

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

    def get_sample_ids(self) -> pd.DataFrame:
        """Return sample ids that are stored in sample table"""
        sql = f"""
        SELECT DISTINCT {self.sample_id_col} FROM {self.sample_table}
        """
        df = pd.read_sql(sql=sql, con=self.conn)
        return df[self.sample_id_col].sort_values(ascending=True, key=natsort_keygen())

    def get_samples(self, sample_ids: List[str]) -> pd.DataFrame:
        """Return a dataframe with the information for the given sample ids"""
        sql = f"""
        SELECT * FROM {self.sample_table}
        WHERE sample_id IN ({', '.join([f"'{x}'" for x in sample_ids])})
        """
        df = pd.read_sql(sql=sql, con=self.conn)
        return df

    def relative_expression_filter(self, gene_abundance_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate relative expression of a gene by using Welch's t-test to see if sample and controls have the same mean. Return relative expression with type of expression(overexpressed/underexpressed)"""
        # TODO: Figure out if reading in all data then iterating through genes is faster than doing a sql query for each gene individually
        genes_list = gene_abundance_df.gene.unique()

        sql = f"""
        SELECT {self.gene_col}, VALUE FROM {self.control_samples_table}
        WHERE {self.gene_col} IN ({', '.join([f"'{x}'" for x in genes_list])})
        """

        control_samples_df = pd.read_sql(con=self.conn, sql=sql)

        relative_expression_dict = {'gene': [], 'expression': [], 'relative_expression': [], 'p_value': [],
                                    't_statistic': []}


        for gene in genes_list:
            control_values = control_samples_df.value[control_samples_df.gene == gene]
            test_values = gene_abundance_df.value[gene_abundance_df[self.gene_col] == gene]
            ttest_results = ttest_ind(test_values, control_values, equal_var=False)  # equal_var=False performs Welch’s t-test
            relative_expression = test_values.mean() - control_values.mean()  # log transformed values so need to use log arithmatic

            relative_expression_dict['gene'].append(gene)
            relative_expression_dict['relative_expression'].append(relative_expression)
            relative_expression_dict['p_value'].append(ttest_results.pvalue)
            relative_expression_dict['t_statistic'].append(ttest_results.statistic)

            if ttest_results.pvalue < 0.05:
                if ttest_results.statistic > 0:
                    relative_expression_dict['expression'].append('overexpressed')
                elif ttest_results.statistic < 0:
                    relative_expression_dict['expression'].append('suppressed')
            else:
                relative_expression_dict['expression'].append('expected')

        return pd.DataFrame.from_dict(relative_expression_dict)


    def pathway_gene_count(self, genes_list:List[str]) -> pd.DataFrame:
        """Returns pathways with the number of genes present from genes_list"""
        sql = f"""
        SELECT {self.pathway_col}, COUNT(*) AS sample_gene_count FROM {self.pathway_gene_table}
        WHERE {self.gene_col} IN ({', '.join([f"'{x}'" for x in genes_list])})
        GROUP BY {self.pathway_col}
        ORDER BY COUNT(*) DESC
        """

        pathway_gene_count_df = pd.read_sql(con=self.conn, sql=sql)
        return pathway_gene_count_df

    def expected_gene_count(self, pathway_gene_count_df:pd.DataFrame, num_genes_submitted:int) -> pd.DataFrame:
        """Calculates the number of genes that are expected to be present for each pathway containing genes from genes_list
        Steps:
        1) Count number of total genes present in pathway
        2) Divide total number of genes by number of genes present in reference organism to find reference gene ratio
        3) Find expected number of genes by multiplying reference gene ratio by the number of genes in genes_list
        """
        #TODO: Determine if size of gene list should be len of original gene list or filtered gene list after relative expression filter

        sql = f"""
        SELECT {self.pathway_col}, COUNT(*) AS total_gene_count_reference 
        FROM {self.pathway_gene_table}
        WHERE {self.pathway_col} IN ({', '.join([f"'{x}'" for x in pathway_gene_count_df.pathway])})
        GROUP BY pathway
        """

        expected_gene_count_df = pd.read_sql(sql=sql, con=self.conn)

        if self.reference_organism == 'Mus musculus':
            # Found from panther classification system which was launched from gene ontology site.
            # Number is found at start of results under reference list beside uniquely mapped ids.
            reference_genes_count = 21836

        expected_gene_count_df['reference_gene_ratio'] = expected_gene_count_df[
                                                             'total_gene_count_reference'] / reference_genes_count

        expected_gene_count_df['expected_count'] = expected_gene_count_df['reference_gene_ratio'] * num_genes_submitted

        return expected_gene_count_df

    def fold_change(self, pathway_gene_count_df:pd.DataFrame, expected_gene_count_df:pd.DataFrame, expression: str, num_genes_submitted: int) -> pd.DataFrame:
        """Calculate fold change by dividing sample_gene_count by expected_count (Panther method)
            Working on fold change by Berco method
        """
        fold_change_df = pathway_gene_count_df.merge(expected_gene_count_df, how='outer', on=self.pathway_col)

        fold_change_df['panther_fold_enrichment'] = fold_change_df['sample_gene_count'] / fold_change_df[
            'expected_count']
        if expression == 'overexpressed':
            fold_change_df['panther_fold_enrichment_p_value'] = fold_change_df.apply(lambda row: binomtest(k=row['sample_gene_count'], n=num_genes_submitted, p=row['reference_gene_ratio'], alternative='greater').pvalue, axis=1)  #TODO: Add p-value for binomial test from box 3 of Panther paper
        else:
            fold_change_df['panther_fold_enrichment_p_value'] = fold_change_df.apply(lambda row: binomtest(k=row['sample_gene_count'], n=num_genes_submitted, p=row['reference_gene_ratio'], alternative='less').pvalue, axis=1)

        # fold_change_df['npat_fold_enrichment'] =
        return fold_change_df

    def enrichment_analysis(self, gene_expression_df, expression='overexpressed'):
        """Run enrichment analysis on relative expression dataframe"""
        filtered_genes_list = gene_expression_df[gene_expression_df.expression == expression].gene.unique()
        num_genes_submitted = len(filtered_genes_list)
        pathway_gene_count_df = self.pathway_gene_count(genes_list=filtered_genes_list)
        expected_gene_count_df = self.expected_gene_count(pathway_gene_count_df=pathway_gene_count_df,
                                                          num_genes_submitted=num_genes_submitted)
        fold_change_df = self.fold_change(pathway_gene_count_df=pathway_gene_count_df,
                                          expected_gene_count_df=expected_gene_count_df,
                                          expression=expression,
                                          num_genes_submitted=num_genes_submitted)

        return fold_change_df


    def full_analysis(self, gene_abundance_df, expression='overexpressed'):
        """Run full analysis on gene abundance dataframe"""
        gene_expression_df = self.relative_expression_filter(gene_abundance_df=gene_abundance_df)
        fold_change_df = self.enrichment_analysis(gene_expression_df=gene_expression_df, expression=expression)

        return fold_change_df

def main() -> None:
    args = get_args()
    npat = NPAT(analysis_name=args.analysis_name,
                env_file=args.env_file,
                gene_col=args.gene_col,
                pathway_col=args.pathway_col,
                pathway_gene_table=args.pathway_gene_table,
                reference_organism=args.reference_organism,
                expected_abundance_table=args.expected_abundance_table,
                control_samples_table=args.control_samples_table,
                value_transformation=args.value_transformation,
                sample_table=args.sample_table,
                sample_id_col=args.sample_id_col)

if __name__ == '__main__':
    main()
        

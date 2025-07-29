import pandas as pd
import os
import logging
from datetime import datetime
from .template import TEMPLATE_MAP_OBO, TEMPLATE_MAP_SNOMED

logging.basicConfig(level=logging.INFO)

class Toolkit():
    keywords_OBO = {
        "Birthdate", "Birthyear", "Deathdate", "Sex", "Status", "First_visit"#, "Education",
        "Questionnaire", "Diagnosis", "Phenotype", "Symptoms_onset", "Corporal", "Laboratory",
        "Imaging", "Genetic", "Disability", "Medication", "Surgery", "Biobank", "Clinical_trial"
    }
    keywords_SNOMED = {
        "Birthdate", "Birthyear", "Deathdate", "Sex", "Status", "First_visit",
        "Questionnaire", "Diagnosis", "Phenotype", "Symptoms_onset", "Corporal", "Laboratory",
        "Imaging", "Genetic", "Disability", "Medication", "Surgery", "Clinical_trial"
    }


    columns = [
        "model", "pid", "event_id", "value", "age", "value_datatype", "valueIRI", "activity",
        "unit", "input", "target", "protocol_id", "frequency_type", "frequency_value",
        "agent", "startdate", "enddate", "comments"
    ]

    drop_columns = ["value", "valueIRI", "target", "agent", "input", "activity", "unit"]

    def milisec(self):

        now = datetime.now()
        now = now.strftime('%Y%m%d%H%M%S%f')
        return now

    def whole_method(self, folder_path, template_type):
        matching_files = self._find_matching_files(folder_path, template_type)
        processed = [self._process_file(file, template_type) for file in matching_files]
        final_df = pd.concat(processed, ignore_index=True) if processed else pd.DataFrame(columns=self.columns)
        final_df = self.delete_extra_columns(final_df)
        final_df.to_csv(os.path.join(folder_path, "CARE.csv"), index=False)

    def _find_matching_files(self, folder_path, template_type):
        if template_type == "OBO":
            keywords = self.keywords_OBO
        elif template_type == "SNOMED":
            keywords = self.keywords_SNOMED
        else:
            raise ValueError(f"Template type '{template_type}' not recognized.")

        return [
            os.path.join(folder_path, file)
            for file in os.listdir(folder_path)
            if file.endswith(".csv") and any(keyword in file for keyword in keywords)
        ]

    def _process_file(self, filepath, template_type):
        df = self.import_your_data_from_csv(filepath)
        if df is None:
            return pd.DataFrame(columns=self.columns)

        df = self.check_status_column_names(df)
        df = self.add_columns_from_template(df, filepath, template_type=template_type)
        df = self.value_edition(df)
        df = self.time_edition(df)
        df = self.clean_empty_rows(df, filepath)
        df = self.unique_id_generation(df)
        return df

    def import_your_data_from_csv(self, filepath):
        try:
            df = pd.read_csv(filepath)
            logging.info(f"Imported CSV: {os.path.basename(filepath)}")
            return df
        except Exception as e:
            logging.error(f"Error loading CSV {filepath}: {e}")
            return None

    def check_status_column_names(self, df):
        extra_cols = set(df.columns) - set(self.columns)
        if extra_cols:
            raise ValueError(f"Unexpected columns: {extra_cols}. Expected: {self.columns}")

        for col in self.columns:
            if col not in df.columns:
                df[col] = pd.Series(dtype=object)

        return df.where(pd.notnull(df), None)

    def add_columns_from_template(self, df, filepath, template_type):
        if template_type == "OBO":
            template = TEMPLATE_MAP_OBO
        elif template_type == "SNOMED":
            template = TEMPLATE_MAP_SNOMED
        else:
            raise ValueError(f"Template type '{template_type}' not recognized.")
        enriched_rows = []

        for _, row in df.iterrows():
            model = row['model']
            base = {"model": model}
            base.update(template.get(model, {}))
            base.update({k: v for k, v in row.items() if v is not None})
            enriched_rows.append(pd.DataFrame(base, index=[0]))

        result = pd.concat(enriched_rows, ignore_index=True) if enriched_rows else pd.DataFrame(columns=self.columns)
        logging.info(f"Transformed: {os.path.basename(filepath)}")
        return result.where(pd.notnull(result), None)

    def value_edition(self, df):
        def apply_value_types(row):
            val = row['value']
            model = row['model']
            dtype = row['value_datatype']

            if pd.notnull(val):
                if dtype == 'xsd:string' and model != 'Genetic':
                    row['value_string'] = val
                elif dtype == 'xsd:float' and model not in ['Medication', 'Genetic']:
                    row['value_float'] = val
                elif dtype == 'xsd:integer' and model not in ['Medication', 'Genetic']:
                    row['value_integer'] = val
                elif dtype == 'xsd:date':
                    row['value_date'] = val
                elif model == 'Medication':
                    row['concentration_value'] = val
                elif model == 'Genetic':
                    row['output_id_value'] = val

            if pd.notnull(row.get('valueIRI')):
                if model in ['Sex', 'Status', 'Diagnosis', 'Phenotype', 'Clinical_trial', 'Corporal']:
                    row['attribute_type'] = row['valueIRI']
                elif model in ['Imaging', 'Genetic']:
                    row['output_id'] = row['valueIRI']

            if pd.notnull(row.get('target')):
                if model in ['Symptoms_onset', 'Laboratory', 'Surgical', 'Imaging']:
                    row['target_type'] = row['target']
                if model == 'Genetic':
                    row['attribute_type'] = row['target']

            if pd.notnull(row.get('input')):
                if model in ['Genetic', 'Laboratory', 'Imaging', 'Biobank']:
                    row['input_type'] = row['input']

            if pd.notnull(row.get('agent')):
                if model in ['Biobank', 'Clinical_trial']:
                    row['organization_id'] = row['agent']
                elif model == 'Medication':
                    row['substance_id'] = row['agent']
                elif model == 'Genetic':
                    row['output_type'] = row['agent']

            if pd.notnull(row.get('activity')):
                row['specific_method_type'] = row['activity']

            if pd.notnull(row.get('unit')):
                if model in ['Corporal', 'Laboratory', 'Questionnaire', 'Disability']:
                    row['unit_type'] = row['unit']
                elif model == 'Medication':
                    row['concentration_unit_type'] = row['unit']

            return row

        return df.apply(apply_value_types, axis=1)

    def time_edition(self, df):
        df['enddate'] = df['enddate'].where(pd.notnull(df['enddate']), df['startdate'])
        return df

    def clean_empty_rows(self, df, filepath):
        pre_clean_len = len(df)
        df = df[~df[['value', 'valueIRI', 'activity', 'target', 'agent']].isnull().all(axis=1)]
        removed = pre_clean_len - len(df)
        logging.info(f"{os.path.basename(filepath)}: Removed {removed} empty rows")
        return df

    def delete_extra_columns(self, df):
        return df.drop(columns=[col for col in self.drop_columns if col in df.columns], errors='ignore')

    def unique_id_generation(self, df):
        df['uniqid'] = [self.milisec() for _ in df.index]
        return df
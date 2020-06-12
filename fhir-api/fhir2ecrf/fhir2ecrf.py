import pandas as pd
import os
import logging
from pprint import pformat
from collections import defaultdict

from fhir2dataset import Query, FHIRRules
from fhir2ecrf.export_tools import (
    create_config,
    change_alias,
    treatment_first,
    treatment_bool,
    treatment_list,
)

logger = logging.getLogger(__name__)


FILENAME_CRF_ATTRIBUTES = "crf_to_config.csv"
PATH_CRF_ATTRIBUTES = os.path.join(os.path.dirname(__file__), "metadata", FILENAME_CRF_ATTRIBUTES)

MODIFIERS_POSS = [
    "missing",
    "exact",
    "contains",
    "text",
    "in",
    "below",
    "above",
    "not-in",
]

POST_TREAMENTS = {
    "bool": treatment_bool,
    "first": treatment_first,
    "list": treatment_list,
}


class FHIR2eCRF:
    """
    class allowing to retrieve a dataframe from a configuration file containing the following information:

    {
        "attributes":[
            {"officialName":"Identifier","customName":"Identifier"},
            {"officialName":"First name","customName":"First name"},
            {"officialName":"Last name","customName":"Last name"},
            {"officialName":"Date of birth","customName":"Date of birth"},
            {"officialName":"Gender","customName":"Gender"},
            {"officialName":"Height","customName":"Height"},
            {"officialName":"Weight","customName":"Weight"},
            {"officialName":"Medication Name","customName":"Medication name Astelin", "type": "text", "text": "Astelin"},
            {"officialName":"Medication Code","customName":"Medication code Lidocaine", "type": "text", "text": "8418806.0"},
            {"officialName":"Temperature","customName":"Temperature"},
            {"officialName":"Albumine","customName":"Albumine"},
            {"officialName":"Creatinine","customName":"Creatinine"},
            {"officialName":"Glucose","customName":"Glucose"},
            {"officialName":"Bilirubin","customName":"Bilirubin"},
            {"officialName":"Magnesium","customName":"Magnesium"},
            {"officialName":"Sodium","customName":"Sodium"},
            {"officialName":"Potassium","customName":"Potassium"},
            {"officialName":"ALAT","customName":"ALAT"},
            {"officialName":"ASAT","customName":"ASAT"},
            {"officialName":"General diagnostic","customName":"General diagnostic"},
            {"officialName":"specific diagnostic code","customName":"specific diagnostic code", "type": "text", "text": "69550"},
            {"officialName":"specific diagnostic text","customName":"specific diagnostic text", "type": "text", "text": "amput"}
        ],
        "idPatient":[
            "id_1",
            "id_2",
            ...
        ]
    }

    Attributes:
        token (str): bearer token authentication if necessary (default: {None})
        fhir_api_url (str): The Service Base URL (e.g. http://hapi.fhir.org/baseR4/) 
        fhir_rules (type(FHIRRules)): an instance of a FHIRRules-type object
        df_crf_attributes (pd.DataFrame): dataframe containing the configurations related to each crf attribute
    
    Example:
        import logging
        from fhir2ecrf import FHIR2eCRF

        logging.basicConfig()
        fhir2ecrf = FHIR2eCRF(token=token, fhir_api_url=fhir_api_url)
        df = fhir2ecrf.query(config_front)
    """  # noqa

    def __init__(self, token: str = None, fhir_api_url: str = None):
        """Metadata loading

        Args:
            token (str, optional): bearer token authentication if necessary. Defaults to None.
            fhir_api_url (str, optional): The Service Base URL (e.g. http://hapi.fhir.org/baseR4/). Defaults to None.
        """  # noqa
        self.token = token
        self.fhir_api_url = fhir_api_url
        self.df_crf_attributes = self._load_crf_attributes()
        self.fhir_rules = FHIRRules(fhir_api_url=self.fhir_api_url)

    def query(self, config_front: dict) -> pd.DataFrame:
        """Perform the query on the FHIR Api according to the config_front of the following form:
        {
        "attributes":[
            {"officialName":"Identifier","customName":"Identifier"},
            {"officialName":"First name","customName":"First name"},
            {"officialName":"Last name","customName":"Last name"},
            {"officialName":"Date of birth","customName":"Date of birth"},
            {"officialName":"Gender","customName":"Gender"},
            {"officialName":"Height","customName":"Height"},
            {"officialName":"Weight","customName":"Weight"},
            {"officialName":"Medication Name","customName":"Medication name Astelin", "type": "text", "text": "Astelin"},
            {"officialName":"Medication Code","customName":"Medication code Lidocaine", "type": "text", "text": "8418806.0"},
            {"officialName":"Temperature","customName":"Temperature"},
            {"officialName":"Albumine","customName":"Albumine"},
            {"officialName":"Creatinine","customName":"Creatinine"},
            {"officialName":"Glucose","customName":"Glucose"},
            {"officialName":"Bilirubin","customName":"Bilirubin"},
            {"officialName":"Magnesium","customName":"Magnesium"},
            {"officialName":"Sodium","customName":"Sodium"},
            {"officialName":"Potassium","customName":"Potassium"},
            {"officialName":"ALAT","customName":"ALAT"},
            {"officialName":"ASAT","customName":"ASAT"},
            {"officialName":"General diagnostic","customName":"General diagnostic"},
            {"officialName":"specific diagnostic code","customName":"specific diagnostic code", "type": "text", "text": "69550"},
            {"officialName":"specific diagnostic text","customName":"specific diagnostic text", "type": "text", "text": "amput"}
        ],
        "idPatient":[
            "id_1",
            "id_2",
            ...
        ]
    }

        Args:
            config_front (dict): json instance of the previous configuration file

        Returns:
            pd.DataFrame: pandas dataframe containing the correspondant data
        """  # noqa
        post_treatements, columns_renaming, config = self._create_config_fhir2dataset(config_front)
        cols_order = [attribute["customName"] for attribute in config_front["attributes"]]

        query = Query(fhir_api_url=self.fhir_api_url, fhir_rules=self.fhir_rules, token=self.token)
        query.from_config(config)
        query.execute()
        df = query.main_dataframe

        df.rename(columns=columns_renaming, inplace=True)
        logger.debug(f"Main dataframe after columns renaming\n{df.to_string()}")
        for post_treatement_type, list_cols in post_treatements.items():
            df[list_cols] = df[list_cols].applymap(POST_TREAMENTS[post_treatement_type])
        logger.debug(f"Main dataframe after post-treaments\n{df.to_string()}")
        df = df[cols_order]
        logger.debug(f"Main dataframe after after rearranging the columns\n{df.to_string()}")
        return df

    def _load_crf_attributes(self):
        return pd.read_csv(PATH_CRF_ATTRIBUTES)

    def _create_config_fhir2dataset(self, config_front):
        df = self.df_crf_attributes
        post_treatement = defaultdict(list)
        patients_id = config_front["idPatient"]
        assert len(patients_id) > 0, "At least one patient ID must be filled in the config_front"

        attributes_keep = [
            attribute["officialName"].lower() for attribute in config_front["attributes"]
        ]
        attributes_keep += ["id"]
        df_infos = df[df["officialName"].isin(attributes_keep)]
        list_text_attribute = df_infos[df_infos["type"] == "text"]["officialName"].to_list()

        df_keep = df_infos[~df_infos["officialName"].isin(list_text_attribute)]

        columns_renaming = {}
        for attribute in config_front["attributes"]:
            official_name = attribute["officialName"].lower()
            col_name_export = attribute["customName"]
            if official_name in list_text_attribute:
                text = attribute["text"]
                df_temp = df_infos[df_infos["officialName"] == official_name]
                idx_change = df_temp.index[df_temp["type"] == "text"].to_list()
                alias_old = df_temp.loc[idx_change[0], "from:alias"]
                df_temp.loc[idx_change[0], "where:value"] = text
                alias_new = f"{alias_old}_{text}"
                df_temp = df_temp.applymap(lambda x: change_alias(x, alias_old, alias_new))
                select = df_temp.loc[idx_change[0], "select:jsonpath"]
                modifier = select.split(":")[-1]
                if modifier in MODIFIERS_POSS:
                    select = ":".join(select.split(":")[:-1])
                col_name_internal = f"{alias_new}:{select}"
                df_keep = pd.concat([df_keep, df_temp])
            else:
                col_name_internal = df_infos[df_infos["officialName"] == official_name][
                    "internal_column_name"
                ].iloc[0]
            post_treatment_type = df_infos[df_infos["officialName"] == official_name][
                "column_post_treatment"
            ].iloc[0]
            post_treatement[post_treatment_type].append(col_name_export)
            assert post_treatment_type in list(
                POST_TREAMENTS.keys()
            ), f"{post_treatment_type} post-treatment does not exist"
            if col_name_internal not in list(columns_renaming.keys()):
                columns_renaming[col_name_internal] = col_name_export

        config = create_config(df_keep, patients_id)
        logger.info(f"config created:")
        logger.info(pformat(config))
        logger.debug(f"columns renaming")
        logger.debug(pformat(columns_renaming))
        logger.debug(f"post-treaments to be performed")
        logger.debug(pformat(post_treatement))
        return post_treatement, columns_renaming, config

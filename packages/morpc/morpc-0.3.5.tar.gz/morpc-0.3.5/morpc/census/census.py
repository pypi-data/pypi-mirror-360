import json
import morpc

SCOPES = {
    "us-states": {"desc": "all states in the United States",
                  "for": "state:*",
                  "in": "us:*"},
    "ohio": {"desc": "the State of Ohio",
             "for": "state:39"},
    "ohio-counties": {"desc": "all counties in the State of Ohio",
                      "for": "county:*",
                     "in": "state:39"},
    "ohio-tracts": {"desc": "all Census tracts in the State of Ohio",
                    "for": "tracts:*",
                   "in": "state:39"},
    "region15-counties": {"desc": "all counties in the MORPC 15-county region",
                          "for": f"county:{",".join([morpc.CONST_COUNTY_NAME_TO_ID[x][2:6] for x in morpc.CONST_REGIONS['15-County Region']])}",
                         "in": "state:39"},
    "region15-tracts": {"desc": "all Census tracts in the MORPC 10-county region",
                        "for": "tracts:*",
                        "in": ["state:39", f"county:{",".join([morpc.CONST_COUNTY_NAME_TO_ID[x][2:6] for x in morpc.CONST_REGIONS['15-County Region']])}"]},
    "regionmpo-parts": {"desc": "all Census township parts and place parts that are MORPC MPO members",
                        "ucgid": "1550000US3902582041,0700000US390410577499999,0700000US390410578899999,0700000US390410942899999,1550000US3918000041,0700000US390411814099999,1550000US3921434041,0700000US390412144899999,1550000US3922694041,1550000US3929148041,0700000US390412969499999,0700000US390413351699999,0700000US390414036299999,0700000US390414310699999,0700000US390414790899999,0700000US390415861899999,1550000US3958940041,0700000US390415926299999,0700000US390416417899999,1550000US3964486041,0700000US390416531299999,0700000US390417084299999,1550000US3971976041,1550000US3975602041,0700000US390417661799999,0700000US390417733699999,0700000US390417756099999,1550000US3983342041,0700000US390450695099999,1550000US3911332045,1550000US3918000045,1550000US3944086045,1550000US3962498045,1550000US3966390045,0700000US390458020699999,1550000US3906278049,0700000US390490692299999,1550000US3908532049,0700000US390490944299999,1550000US3911332049,0700000US390491611299999,1550000US3918000049,1550000US3922694049,0700000US390492828099999,1550000US3929106049,1550000US3931304049,1550000US3932592049,1550000US3932606049,0700000US390493302699999,1550000US3933740049,1550000US3935476049,0700000US390493777299999,0700000US390493861299999,1550000US3944086049,1550000US3944310049,0700000US390494641099999,1550000US3947474049,0700000US390495006499999,1550000US3950862049,1550000US3953970049,0700000US390495734499999,1550000US3957862049,0700000US390496184099999,1550000US3962498049,0700000US390496297499999,0700000US390496325499999,0700000US390496457099999,1550000US3966390049,1550000US3967440049,0700000US390497178799999,0700000US390497771499999,1550000US3979002049,1550000US3979100049,1550000US3979282049,0700000US390498124299999,1550000US3983342049,1550000US3984742049,1550000US3986604049,0700000US390892569099999,1550000US3939340089,1550000US3953970089,1550000US3961112089,1550000US3966390089,1550000US3963030097,1550000US3922694159,0700000US391593904699999,1550000US3963030159"}
}

ACS_MISSING_VALUES = ["","-222222222","-333333333","-555555555","-666666666","-888888888","-999999999"]

ACS_PRIMARY_KEY = "GEO_ID"

ACS_ID_FIELDS = {
    "block group": [
        {"name":"GEO_ID", "type":"string", "description":"Unique identifier for geography"},
        {"name":"SUMLEVEL", "type":"string", "description":"Code representing the geographic summary level for the data"},
        {"name":"STATE","type":"string","description":"Unique identifier for state in which geography is located"},
        {"name":"COUNTY","type":"string","description":"Unique identifier for county in which geography is located"},
        {"name":"TRACT","type":"string","description":"Unique identifier for tract in which geography is located"}
    ],
    "tract": [
        {"name":"GEO_ID", "type":"string", "description":"Unique identifier for geography"},
        {"name":"SUMLEVEL", "type":"string", "description":"Code representing the geographic summary level for the data"},
        {"name":"STATE","type":"string","description":"Unique identifier for state in which geography is located"},
        {"name":"COUNTY","type":"string","description":"Unique identifier for county in which geography is located"}
    ],
    "county subdivision": [
        {"name":"GEO_ID", "type":"string", "description":"Unique identifier for geography"},
        {"name":"SUMLEVEL", "type":"string", "description":"Code representing the geographic summary level for the data"},
        {"name":"STATE","type":"string","description":"Unique identifier for state in which geography is located"},
        {"name":"COUNTY","type":"string","description":"Unique identifier for county in which geography is located"}
    ],
    "county": [
        {"name":"GEO_ID", "type":"string", "description":"Unique identifier for geography"},
        {"name":"SUMLEVEL", "type":"string", "description":"Code representing the geographic summary level for the data"},
        {"name":"NAME", "type":"string", "description":"Name by which geography is known"},
        {"name":"STATE","type":"string","description":"Unique identifier for state in which geography is located"},
        {"name":"COUNTY","type":"string","description":"Unique identifier for county in which geography is located"},
    ],
    "state": [
        {"name":"GEO_ID", "type":"string", "description":"Unique identifier for geography"},
        {"name":"SUMLEVEL", "type":"string", "description":"Code representing the geographic summary level for the data"},
        {"name":"NAME", "type":"string", "description":"Name by which geography is known"},
        {"name":"STATE","type":"string","description":"Unique identifier for state in which geography is located"},
    ],
    "metropolitan statistical area/micropolitan statistical area": [
        {"name":"GEO_ID", "type":"string", "description":"Unique identifier for geography"},
        {"name":"SUMLEVEL", "type":"string", "description":"Code representing the geographic summary level for the data"},
        {"name":"NAME", "type":"string", "description":"Name by which geography is known"}
    ],
    "division": [
        {"name":"GEO_ID", "type":"string", "description":"Unique identifier for geography"},
        {"name":"SUMLEVEL", "type":"string", "description":"Code representing the geographic summary level for the data"},
        {"name":"NAME", "type":"string", "description":"Name by which geography is known"},
    ],
    "us": [
        {"name":"GEO_ID", "type":"string", "description":"Unique identifier for geography"},
        {"name":"SUMLEVEL", "type":"string", "description":"Code representing the geographic summary level for the data"},
        {"name":"NAME", "type":"string", "description":"Name by which geography is known"}
    ]
}

DEC_MISSING_VALUES = [""]

DEC_PRIMARY_KEY = "GEO_ID"

DEC_ID_FIELDS = json.loads(json.dumps(ACS_ID_FIELDS))  # Start with same fields as ACS, then adjust
DEC_ID_FIELDS["block"] = [
    {"name":"GEO_ID", "type":"string", "description":"Unique identifier for geography"},
    {"name":"SUMLEVEL", "type":"string", "description":"Code representing the geographic summary level for the data"},
    {"name":"STATE","type":"string","description":"Unique identifier for state in which geography is located"},
    {"name":"COUNTY","type":"string","description":"Unique identifier for county in which geography is located"},
    {"name":"TRACT","type":"string","description":"Unique identifier for tract in which geography is located"},
    # Note: Block is subsidiary to block group, however the API does not provide the block group (BLKGRP) identifiers
]

DEC_API = {
    "sdhc": {
        "title": "Supplemental Demographic and Housing Characteristics File",
        "abbrev": "S-DHC",
        "url": "https://api.census.gov/data/{year}/dec/sdhc"
    },
    "ddhcb": {
        "title": "Detailed Demographic and Housing Characteristics File B",
        "abbrev": "Detailed DHC-B",
        "url": "https://api.census.gov/data/{year}/dec/ddhcb"
    },
    "ddhca": {
        "title": "Detailed Demographic and Housing Characteristics File A",
        "abbrev": "Detailed DHC-A",
        "url": "https://api.census.gov/data/{year}/dec/ddhca"
    },
    "dhc": {
        "title": "Demographic Profile",
        "abbrev": "S-DHC",
        "url": "https://api.census.gov/data/{year}/dec/dhc"
    },
    "dp": {
        "title": "Demographic and Housing Characteristics File",
        "abbrev": "DP",
        "url": "https://api.census.gov/data/{year}/dec/dp"
    },
    "pl": {
        "title": "Redistricting Data",
        "abbrev": "PL 94-171",
        "url": "https://api.census.gov/data/{year}/dec/pl"
    },
    "pes": {
        "title": "Decennial Post-Enumeration Survey",
        "abbrev": "PES",
        "url": "https://api.census.gov/data/{year}/dec/pes"
    }
}

ACS_STANDARD_AGEGROUP_MAP = {
    'Under 5 years': 'Under 5 years',
    '5 to 9 years': '5 to 9 years',
    '10 to 14 years': '10 to 14 years',
    '15 to 17 years': '15 to 19 years',
    '18 and 19 years': '15 to 19 years',
    '20 years': '20 to 24 years',
    '21 years': '20 to 24 years',
    '22 to 24 years': '20 to 24 years',
    '25 to 29 years': '25 to 29 years',
    '30 to 34 years': '30 to 34 years',
    '35 to 39 years': '35 to 39 years',
    '40 to 44 years': '40 to 44 years',
    '45 to 49 years': '45 to 49 years',
    '50 to 54 years': '50 to 54 years',
    '55 to 59 years': '55 to 59 years',
    '60 and 61 years': '60 to 64 years',
    '62 to 64 years': '60 to 64 years',
    '65 and 66 years': '65 to 69 years',
    '67 to 69 years': '65 to 69 years',
    '70 to 74 years': '70 to 74 years',
    '75 to 79 years': '75 to 79 years',
    '80 to 84 years': '80 to 84 years',
    '85 years and over': '85 years and over'
}

ACS_AGEGROUP_SORT_ORDER = {
    'Under 5 years': 1,
    '5 to 9 years': 2,
    '10 to 14 years': 3,
    '15 to 19 years': 4,
    '20 to 24 years': 5,
    '25 to 29 years': 6,
    '30 to 34 years': 7,
    '35 to 39 years': 8,
    '40 to 44 years': 9,
    '45 to 49 years': 10,
    '50 to 54 years': 11, 
    '55 to 59 years': 12,
    '60 to 64 years': 13,
    '65 to 69 years': 14,
    '70 to 74 years': 15,
    '75 to 79 years': 16,
    '80 to 84 years': 17,
    '85 years and over': 18
}

def api_get(url, params, varBatchSize=20, verbose=True):
    """
    api_get() is a low-level wrapper for Census API requests that returns the results as a pandas dataframe. If necessary, it
    splits the request into several smaller requests to bypass the 50-variable limit imposed by the API.  The resulting dataframe
    is indexed by GEOID (regardless of whether it was requested) and omits other fields that are not requested but which are returned 
    automatically with each API request (e.g. "state", "county")

    Parameters
    ----------
    url : string
        url is the base URL of the desired Census API endpoint.  For example: https://api.census.gov/data/2022/acs/acs1

    params : dict 
        (in requests format) the parameters for the query string to be sent to the Census API. For example:

        {
            "get": "GEO_ID,NAME,B01001_001E",
            "for": "county:049,041",
            "in": "state:39"
        }

    varBatchSize : integer, default = 20
        representing the number of variables to request in each batch. 
        Defaults to 20, Limited to 49.

    verbose : boolean
        If True, the function will display text updates of its status, otherwise it will be silent.

    Returns
    -------
    pandas.Dataframe
        dataframe indexed by GEO_ID and having a column for each requested variable
    """
    
    import json         # We need json to make a deep copy of the params dict
    import requests
    import pandas as pd
    
    # We need to reserve one variable in each batch for GEO_ID.  If the user requests more than 49 variables per
    # batch, reduce the batch size to 49 to respect the API limit
    if(varBatchSize > 49):
        print("WARNING: Requested variable batch size exceeds API limit. Reducing batch size to 50 (including GEO_ID).")
        varBatchSize = 49
    
    # Extract a list of all of the requested variables from the request parameters
    allVars = params["get"].split(",")
    if(verbose == True):
        print("Total variables requested: {}".format(len(allVars)))
       
    remainingVars = allVars   
    requestCount = 1
    while(len(remainingVars) > 0):
        if(verbose == True):
            print("Starting request #{0}. {1} variables remain.".format(requestCount, len(remainingVars)))

        # Create a short list of variables to download in this batch. Reserve one place for GEO_ID
        shortList = remainingVars[0:varBatchSize-2]
        # Check to see if GEO_ID was already included in the short list. If not, append it to the list.
        # If so, try to append another variable from the list of remaining variables.  In either case,
        # remove the items in the shortlist from the list of remaining variables.
        if(not "GEO_ID" in shortList):
            shortList.append("GEO_ID")
            remainingVars = remainingVars[varBatchSize-2:]
        else:
            try:
                shortList.append(remainingVars[varBatchSize-2])
            except:
                pass
            remainingVars = remainingVars[varBatchSize-1:]            

        # Create a set of API query parameters for this request. It will be a copy of the original parameters,
        # but with the list of variables replaced by the short list
        shortListParams = json.loads(json.dumps(params))
        shortListParams["get"] = ",".join(shortList)

        # Send the API request. Throw an error if the resulting status code indicates a failure condition.
        r = requests.get(url, params=shortListParams)
        if(r.status_code != 200):
            print("ERROR: Request finished with status {}.".format(r.status_code))
            print("Request URL: " + r.url)
            print("Response text: " + r.text)
            raise RuntimeError

        # Extract the JSON-formatted records from the response
        records = r.json()
        
        # The first record is actually the column headers. Remove this from the list of records and keep it.
        columns = records.pop(0)
        
        # Construct a temporary pandas dataframe from the records
        df = pd.DataFrame.from_records(records, columns=columns)

        # Extract only the requested columns (plus GEO_ID) from the dataframe. This has the effect of removing
        # unrequested variables like "state" and "county"
        df = df.filter(items=shortList, axis="columns")
        
        # If this is our first request, construct the output dataframe by copying the temporary one. Otherwise,
        # join the temporary dataframe to the existing one using the GEO_ID.
        if(requestCount == 1):
            censusData = df.set_index("GEO_ID").copy()
        else:
            censusData = censusData.join(df.set_index("GEO_ID"))
        
        requestCount += 1

    return censusData

class acs_data:
    def __init__(self, group, year, survey):
        """
        Class for working with ACS Survey Data. Creates an object representing data for a variable by year by survey. Use .query() method to retrive data for a specific geography.

        Parameters
        ----------
        group : str
            string representing the variable group

        year : str
            The year of the survey. For 5 year survey it is the ending year

        survey : str
            Number of years represnting the ACS Survey, "1" or "5"
        """
        self.GROUP = group
        self.YEAR = year
        self.SURVEY = survey
        self.VARS = self.define_vars()

    def query(self, for_param=None, in_param=None, get_param=None, ucgid_param = None, scope=None):
        """
        Method for retrieving data. Relies on morpc.census.api_get().

        Parameters
        ----------
        for_param : str
            The parameters for the "for" parameter for the api_get() call. Typically, the ACS geographic sumlevel name and an astrick. ex. "county subivision:*"

        in_param : list (optional)
            The parameters for the "in" parameter for the api_get() call. Typically, a parameter to filter the for_param with. ex. "state:39" for all the for geographies in the state of Ohio. For for all geographies in Franklin County pass ["state:39", "county:049"]

        get_param : list (optional)
            The field names to retrieve from the Census. Defaults to all availble variables for variable group number.

        scope : str
            The name of a default scope. See morpc.census.DEFAULT_CENSUS_SCOPES
        """

        import morpc
        from datetime import datetime
        import pandas as pd
        self.SCOPE = scope

        if scope != None:
            self.NAME = f"morpc-acs{self.SURVEY}-{self.YEAR}-{scope}-{self.GROUP}".lower()
            if "for" in morpc.census.SCOPES[scope]:
                for_param = morpc.census.SCOPES[scope]['for']
            if "in" in morpc.census.SCOPES[scope]:
                in_param = morpc.census.SCOPES[scope]['in']
            if "ucgid" in morpc.census.SCOPES[scope]:
                ucgid_param = morpc.census.SCOPES[scope]['ucgid']

        if get_param != None:
            if not isinstance(get_param, list):
                print('get_param must be a list')
            temp = {}
            for VAR in self.VARS:
                if VAR in get_param:
                    temp[VAR] = self.VARS[VAR]
            # TODO: add check to make sure everything passed to get_param is in VARS.
            self.VARS = temp
        if scope == None:
            self.NAME = f"morpc-acs{self.SURVEY}-{self.YEAR}-custom-ucgid-{self.GROUP}-{datetime.now().strftime(format='%Y%m%d-%H%M%S')}".lower()
        self.SCHEMA = self.define_schema()


        getFields = ",".join(self.SCHEMA.field_names)
        self.API_PARAMS = {}
        self.API_PARAMS['get'] = getFields
        if for_param != None:
            self.API_PARAMS['for'] = for_param
        if in_param != None:
            self.API_PARAMS['in'] = in_param
        if ucgid_param != None:
            self.API_PARAMS['ucgid'] = ucgid_param
        self.API_URL = f"https://api.census.gov/data/{self.YEAR}/acs/acs{self.SURVEY}"

        self.DATA = morpc.census.api_get(self.API_URL, self.API_PARAMS)

        self.DATA = morpc.cast_field_types(self.DATA.reset_index(), self.SCHEMA, verbose=False)
        self.DATA = self.DATA.filter(items=self.SCHEMA.field_names, axis='columns')
        self.DATA = self.DATA.set_index('GEO_ID')

        self.DIM_TABLE = self.DATA.reset_index().melt(id_vars=['GEO_ID'], value_name="VALUE", var_name='VARIABLE')
        self.DIM_TABLE['DESC'] = self.DIM_TABLE['VARIABLE'].map(morpc.frictionless.name_to_desc_map(self.SCHEMA))
        self.DIM_TABLE['VAR_TYPE'] = self.DIM_TABLE['VARIABLE'].apply(lambda x:'Estimate' if x[-1] == 'E' else 'MOE')
        self.DESC_TABLE = self.DIM_TABLE['DESC'] \
            .apply(lambda x:x.split("|")[0]) \
            .str.replace('Estimate!!','') \
            .str.replace(":","") \
            .str.strip() \
            .apply(lambda x:x.split("!!")) \
            .apply(pd.Series)
        self.DESC_TABLE.columns = ["TOTAL"]+[f"DIM_{x+1}" for x in range(len(self.DESC_TABLE.columns)-1)]
        self.DIM_TABLE = self.DIM_TABLE.join(self.DESC_TABLE, how='left').drop(columns=['DESC','TOTAL'])
        self.DESC_TABLE = self.DESC_TABLE.drop_duplicates()

        return self

    def save(self, output_dir="./output_data"):
        """
        Saves data in an output directory as a fricitonless resource and validates the resource.

        Parameters
        ----------
        output_dir : str or pathlike
            The directory where to save the resource. default = "./output_data
        """
        
        import os
        import frictionless

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        self.DATA_FILENAME = f"{self.NAME}.csv"
        self.DATA_PATH = os.path.join(output_dir, self.DATA_FILENAME)
        self.DATA.reset_index().to_csv(self.DATA_PATH, index=False)

        self.SCHEMA_FILENAME = f"{self.NAME}.schema.yaml"
        self.SCHEMA_PATH = os.path.join(output_dir, self.SCHEMA_FILENAME)

        dummy = self.SCHEMA.to_yaml(self.SCHEMA_PATH)

        self.RESOURCE_FILENAME = f"{self.NAME}.resource.yaml"
        self.RESOURCE_PATH = os.path.join(output_dir, self.RESOURCE_FILENAME)

        cwd = os.getcwd()
        os.chdir(output_dir)

        self.RESOURCE = self.define_resource()
        dummy = self.RESOURCE.to_yaml(self.RESOURCE_FILENAME)
        validation = frictionless.Resource(self.RESOURCE_FILENAME).validate()

        os.chdir(cwd)

        if validation.valid == True:
            print("Resource is valid.")
        else:
            print('ERROR: invalid resource file.')
            print(validation)
            raise RuntimeError

    def define_sumlevel(self):
        import morpc
        sumlevel_dict={}
        for sumlevel in morpc.SUMLEVEL_DESCRIPTIONS:
            if morpc.SUMLEVEL_DESCRIPTIONS[sumlevel]['censusQueryName'] == self.GEO:
                sumlevel_dict[sumlevel] = morpc.SUMLEVEL_DESCRIPTIONS[sumlevel]
                return sumlevel_dict

    def define_schema(self):
        import frictionless
        import morpc

        allFields = []
        allFields.append({"name":"GEO_ID", "type":"string", "description":"Unique identifier for geography"})

        acsVarDict = self.VARS
        for var in [x for x in acsVarDict.keys()]:
            field = {}
            field["name"] = var
            field["type"] = acsVarDict[var]['predicateType']
            if(field["type"] == "int"):
                field["type"] = "integer"
            elif(field["type"] == "float"):
                field["type"] = "number"
            field["description"] = f"{acsVarDict[var]['label']} | {acsVarDict[var]['concept']} | Estimate"
            allFields.append(field)

            field = {}
            field["name"] = var[:-1] + "M"
            field["type"] = acsVarDict[var]['predicateType']
            if(field["type"] == "int"):
                field["type"] = "integer"
            elif(field["type"] == "float"):
                field["type"] = "number"
            field["description"] = f"{acsVarDict[var]['label']} | {acsVarDict[var]['concept']} | MOE"
            allFields.append(field)
    
        acsSchema = {
          "fields": allFields,
          "missingValues": morpc.census.ACS_MISSING_VALUES,
          "primaryKey": morpc.census.ACS_PRIMARY_KEY
        }
    
        results = frictionless.Schema.validate_descriptor(acsSchema)
        if(results.valid == True):
            print(f"{self.NAME} schema is valid")
        else:
            print("ERROR: Schema is NOT valid. Errors follow.")
            print(results)
            raise RuntimeError
    
        schema = frictionless.Schema.from_descriptor(acsSchema)
    
        return schema

    
    def define_vars(self):
        """
        Retrieves a dictionary of variables from acs variable metadata table.
        """
        import requests

        self.varlist_url = f"https://api.census.gov/data/{self.YEAR}/acs/acs{self.SURVEY}/variables.json"
        r = requests.get(self.varlist_url)
        json = r.json()
        variables = {}
        for variable in sorted(json['variables']):
            if json['variables'][variable]['group'] == self.GROUP:
                variables[variable] = json['variables'][variable]

        return variables

    def define_resource(self):
        import frictionless
        import morpc
        import datetime
        import os

        acsResource = {
          "profile": "tabular-data-resource",
          "name": self.NAME,
          "path": self.DATA_FILENAME,
          "title": f"{self.YEAR} American Community Survey {self.SURVEY}-Year Estimates for {"Custom Geography" if self.SCOPE == None else SCOPES[self.SCOPE]['desc']}.",
          "description": f"Selected variables from {self.YEAR} ACS {self.SURVEY}-Year estimates for {"custom geography (see sources._params)" if self.SCOPE == None else SCOPES[self.SCOPE]['desc']}. Data was retrieved {datetime.datetime.today().strftime('%Y-%m-%d')}",
          "format": "csv",
          "mediatype": "text/csv",
          "encoding": "utf-8",
          "bytes": os.path.getsize(self.DATA_FILENAME),
          "hash": morpc.md5(self.DATA_FILENAME),
          "rows": self.DATA.shape[0],
          "columns": self.DATA.shape[1],
          "schema": self.SCHEMA_FILENAME,
          "sources": [{
              "title": f"{self.YEAR} American Community Survey {self.SURVEY}-Year Estimates, U.S. Census Bureau",
              "path": self.API_URL,
              "_params": self.API_PARAMS
          }]
        }
    
        resource = frictionless.Resource(acsResource)
        return resource

# acs_label_to_dimensions obtains the data dimensions associated with a particular variable by decomposing the "Label" column as described in the 
# Census API variable list, e.g. https://api.census.gov/data/2022/acs/acs5/variables.html. There is a label associated with each variable provided 
# by the API. For example, one label (for B25127_004E) looks like this:
#
# Estimate!!Total:!!Owner occupied:!!Built 2020 or later:!!1, detached or attached
#
# The dimensions for the variable are simply the collections of words are separated by ":!!".  For example, "Owner occupied" refers to tenure, "Built 2020 or later" 
# refers to the structure age, and "1, detached or attached" refers to the structure configuration or class.  Thus, the dimensions might be described as follows:
# dimensionNames = ["Tenure","Structure age","Structure class"]
#
# Inputs:
#   - labelSeries is a pandas Series object that contains a set of labels, one for each ACS variable of interest.  The indices of this series typically should match 
#         the dataframe that you want to join the dimension values to.
#   - dimensionNames is a list contains descriptions of the dimensions represented by each element in the label.  These will be used as column headers in the output
#         dataframe.  If dimensionNames is not provided, no column headers will be assigned.
#
# Outputs:
#    - df is a dataframe where each record represents the set of dimensions for an ACS variable and each column represents the value of one dimension for that 
#         variable. Continuing with the example above, a truncated output may look like this:
#
#         |              | Tenure         | Struture age        | Structure class         |
#         |--------------|----------------|---------------------|-------------------------|
#         | B25127_004E  | Owner occupied | Built 2020 or later | 1, detached or attached |
#



def acs_schema(ACS_GROUP, ACS_YEAR, ACS_SURVEY, GEO_SUMLEVEL, OUTPUT_DIR):
    import frictionless
    import morpc
    
    allFields = []

    for field in ACS_ID_FIELDS[GEO_SUMLEVEL]:
        allFields.append(field)

    acsVarDict = acs_variables_by_group(ACS_GROUP, ACS_YEAR, ACS_SURVEY)
    for var in [x for x in acsVarDict.keys()]:
        field = {}
        field["name"] = var
        field["type"] = acsVarDict[var]['predicateType']
        if(field["type"] == "int"):
            field["type"] = "integer"
        elif(field["type"] == "float"):
            field["type"] = "number"
        field["description"] = f"{acsVarDict[var]['label']} | {acsVarDict[var]['concept']} | Estimate"
        allFields.append(field)

        field = {}
        field["name"] = var[:-1] + "M"
        field["type"] = acsVarDict[var]['predicateType']
        if(field["type"] == "int"):
            field["type"] = "integer"
        elif(field["type"] == "float"):
            field["type"] = "number"
        field["description"] = f"{acsVarDict[var]['label']} | {acsVarDict[var]['concept']} | MOE"
        allFields.append(field)

    acsSchema = {
      "fields": allFields,
      "missingValues": ACS_MISSING_VALUES,
      "primaryKey": ACS_PRIMARY_KEY
    }

    results = frictionless.Schema.validate_descriptor(acsSchema)
    if(results.valid == True):
        print(f"acs{ACS_SURVEY}-{ACS_YEAR}-{ACS_GROUP}-{morpc.HIERARCHY_STRING_FROM_SINGULAR[GEO_SUMLEVEL]} schema is valid")
    else:
        print("ERROR: Schema is NOT valid. Errors follow.")
        print(results)
        raise RuntimeError

    schema = frictionless.Schema.from_descriptor(acsSchema)
    
    GEO_HIER = morpc.HIERARCHY_STRING_FROM_SINGULAR[GEO_SUMLEVEL]
    ACS_SCHEMA_FILENAME = f"morpc-acs{ACS_SURVEY}-{ACS_YEAR}-{ACS_GROUP}-{GEO_HIER}.schema.yaml"
    ACS_SCHEMA_PATH = os.path.join(OUTPUT_DIR, ACS_SCHEMA_FILENAME)
    
    schema.to_yaml(ACS_SCHEMA_PATH)
    return schema

def acs_resource(ACS_GROUP, ACS_YEAR, ACS_SURVEY, GEO_SUMLEVEL):

    for sumlevel in morpc.SUMLEVEL_DESCRIPTIONS:
        if sumlevel['singular'] == GEO_SUMLEVEL:
            geoDescription = sumlevel

    

def acs_label_to_dimensions(labelSeries, dimensionNames=None):
    """
    acs_label_to_dimensions(labelSeries, dimensionNames=None)

    obtains the data dimensions associated with a particular variable by decomposing the "Label" column as described in the Census API variable list.

    Parameters
    ----------
    labelSeries : pandas.Series object 
        Contains a set of labels, one for each ACS variable of interest.  The indices of this series typically should match the dataframe that you want to join the dimension values to.

    dimensionNames : list
        Contains descriptions of the dimensions represented by each element in the label.  These will be used as column headers in the output dataframe.  If dimensionNames is not provided, no column headers will be assigned.
        
    Returns
    -------
    Pandas.Dataframe
        Where each record represents the set of dimensions for an ACS variable and each column represents the value of one dimension for that variable.
    """
    import numpy as np
    import pandas as pd
    #TODO: add support for single variable as string.
    
    labelSeries = labelSeries \
        .apply(lambda x:x.split("|")[0]) \
        .str.strip() \
        .str.replace("Estimate!!","") \
        .apply(lambda x:x.split(":"))
    df = labelSeries \
        .apply(pd.Series) \
        .drop(columns=[0, 1]) \
        .replace("", np.nan)
    if(type(dimensionNames) == list):
        df.columns = dimensionNames
    return df

# From a raw ACS data extract produced by morpc-acs-fetch, produce a table that includes the
# the universe (total) estimate and MOE for the indicated variable
#   
#   acsDataRaw is a pandas dataframe resulting from using from reading an output of morpc-census-acs-fetch as follows:
#    
#      resource = frictionless.Resource(ACS_COUNTY_RESOURCE_SOURCE_PATH)
#      acsDataRaw = resource.to_pandas()
#
#   universeVar is the ACS variable included in acsDataRaw that represents the universe/total. Omit the "E" or "M" suffix.
#      For example: universeVar = "B25003_001"
def acs_generate_universe_table(acsDataRaw, universeVar):
    import pandas as pd
    
    acsUniverse = acsDataRaw.copy() \
        .filter(like=universeVar, axis="columns") \
        .rename(columns=(lambda x:("Universe" if x[-1] == "E" else "Universe MOE"))) \
        .reset_index()
    acsUniverse["GEOID"] = acsUniverse["GEO_ID"].apply(lambda x:x.split("US")[1])
    acsUniverse = acsUniverse \
        .set_index("GEOID") \
        .filter(items=["NAME","Universe","Universe MOE"], axis="columns")
    
    return acsUniverse
    
# From a raw ACS data extract produced by morpc-acs-fetch, produce a table that includes the
# the universe (total) estimate and MOE for the indicated variable
#   
#   acsDataRaw is a pandas dataframe resulting from using from reading an output of morpc-census-acs-fetch as follows:
#    
#      resource = frictionless.Resource(ACS_COUNTY_RESOURCE_SOURCE_PATH)
#      acsDataRaw = resource.to_pandas()
#
#   universeVar is the ACS variable included in acsDataRaw that represents the universe/total. Omit the "E" or "M" suffix.
#      For example: universeVar = "B25003_001"
def acs_generate_dimension_table(acsDataRaw, schema, idFields, dimensionNames):
    import pandas as pd
    import frictionless
    import morpc
        
    # Convert the GEOID to short form. Melt the data from wide to long form. Create a descripton field containing the variable label provided by the Census API.
    dimensionTable = acsDataRaw.copy().reset_index()
    dimensionTable["GEOID"] = dimensionTable["GEO_ID"].apply(lambda x:x.split("US")[1])
    dimensionTable = dimensionTable \
        .drop(columns=idFields) \
        .melt(id_vars=["GEOID"], var_name="Variable", value_name='Value')
    dimensionTable["description"] = dimensionTable["Variable"].map(morpc.frictionless.name_to_desc_map(schema))

    # Split the description string into dimensions and drop the description.  Add a field annotating whether the variable is a margin of error or an estimate.  
    # Show example results for Franklin County so it is possible to get a sense of the dimensions.
    dimensionTable = dimensionTable \
        .join(acs_label_to_dimensions(dimensionTable['description'], dimensionNames=dimensionNames), how="left") \
        .drop(columns=["description"])
    dimensionTable["Variable type"] = dimensionTable["Variable"].apply(lambda x:("Estimate" if x[-1]=="E" else "MOE"))

    return dimensionTable
    
# Sometimes ACS data has one dimension that represents subclasses of another.  For example, see this excerpt from C24030 (Sex by Industry)
# which shows subclasses for agriculture, forestry, etc.  However some top level categories - such as construciton - do not have subclasses.
# acs_flatten_category identifies the top level categories that have no subclasses and flattens those categories with the subclasses. This
# allows for more convenient comparison and summarizing across industries.  It is likely that there is a more intuitive or efficient way to
# do this.
#
# For example, this is what C24030 (partial) looks like before flattening:
#
#   Label	United States!!Estimate
#   Total:	162590221
#       Male:	85740285
#           Agriculture, forestry, fishing and hunting, and mining:	1984422
#               Agriculture, forestry, fishing and hunting	1453344
#               Mining, quarrying, and oil and gas extraction	531078
#           Construction	9968254
#           Manufacturing	11394524
#           Wholesale trade	2467558
#           Retail trade	9453931
#
# This is what it looks like after flattening.  Note that the top level category for agriculture, etc was dropped (actually, the
# entire field for the top-level category is dropped).
#
#   Label	United States!!Estimate
#   Total:	162590221
#       Male:	85740285
#         Agriculture, forestry, fishing and hunting	1453344
#         Mining, quarrying, and oil and gas extraction	531078
#         Construction	9968254
#         Manufacturing	11394524
#         Wholesale trade	2467558
#         Retail trade	9453931
#
# inDf is a pandas dataframe that was created using acs_generate_dimension_table()
#
# categoryField is a string representing the field name of the field that holds top-level categories.
#
# subclassField is a string representing the field name of the field that holds the sub-classes
def acs_flatten_category(inDf, categoryField, subclassField):
    import pandas as pd
    df = inDf.copy()
    noSubClasses = []
    for category in df[categoryField].dropna().unique():
        uniqueByCategory = df.loc[df[categoryField] == category].dropna(subset=subclassField)[subclassField].unique()
        if(len(uniqueByCategory) == 0):
            noSubClasses.append(category)
        
    df = df.dropna(subset=categoryField)
    temp = df.filter(items=[categoryField, subclassField], axis="columns").copy()
    temp = temp.loc[temp[categoryField].isin(noSubClasses)].copy()
    temp[subclassField] = temp[categoryField]
    df.update(temp)
    df = df.drop(columns=categoryField)
    return df



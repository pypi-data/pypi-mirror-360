
from pydantic import BaseModel, Field
from typing import List


##########################################################TELANGANA SCHEMA##########################################################


class ExtentTelangana(BaseModel):
    """Property extent details."""
    extent_area: float = Field(..., description="`Extent` is present on the top of the page, extract the extent of the property. Example Extent: `Extent: 225 Y`. Lets have float value for it.")
    unit: str = Field(..., description="`Unit` is present on the top of the page, extract the unit of the extent. Example Unit: `Y` (Yards). Note: The unit can be `SQ. YDS`, `SQ. FT`, `ACRES`, etc. depending on the property.")


class HeadersTelangana(BaseModel):
    """Document header details."""
    application_number: int = Field(..., description="`Application Number` is present on the top of the page, extract the number the page. Example Application Number: `24710`.")
    statement_number: int = Field(..., description="`Statement Number` is present on the top of the page, extract the number the page. Example Statement Number: `194951191`.")
    complete_address: str = Field(..., description="Address of the property is present on top of the page, Extract the exact address of the Home, Note: usually the address is present just after this sentence: `Having searched for a statement giving particulars of registered acts and encumbrances if any, in respect of the under mentioned property`. Example: `Village: NANDIGAMA, Ward - Block: 0 - 1, Plot Number: 352 , Survey Number: 684/R,684/A,685/E,685/A, Extent: 225 Y Bounded by NORTH: 40-0, SOUTH: OTHERS LAND, EAST: PLOT NO.353, WEST: PLOT NO.351`")
    extent: ExtentTelangana = Field(..., description="`Extent` is present on the top of the page, extract the extent of the property. Example Extent: `Extent: 225 Y`.")


class DatesTelangana(BaseModel):
    """Important dates related to the transaction."""
    registration_date: str = Field(..., description= "Date of registration in each row")
    execution_date: str = Field(..., description= "Date of transaction in each row")
    presentation_date: str = Field(..., description= "Date of presentation in each row")


class ValueTelangana(BaseModel):
    """Monetary details of the transaction."""
    nature_of_deed: str = Field(..., description="Type or nature of the deed")
    market_value: str = Field(..., description="Estimated market value of the property")
    consideration_value: str = Field(..., description="Monetary value exchanged")


class PartyTelanagana(BaseModel):
    """Parties involved in the transaction."""
    executant: list[str] = Field(..., description= "List of Name of the executor. This will always be defined in the number 1. Example: `1.(MR)KATUKOJWALA SUMAN`, extract the name `(MR)KATUKOJWALA SUMAN` from this string. The Executant can have code like: `EX` - Executant, `MR` - Mortgagor, `RR` - Releasor, `DR` - Donor.")
    claimant: list[str] = Field(..., description= "List of Name of the claimant. This will always be defined in the number 2. Example: `2.(MR)KATUKOJWALA SUMAN`, extract the name `(MR)KATUKOJWALA SUMAN` from this string. The Executant can have code like: `CL` - Claimant, `ME` - Mortgagee, `RE` - Releasee, `DE` - Donee.")


class ItemTelangana(BaseModel):
    """Individual transaction item."""
    serial_number: str = Field(..., description= "Serial Number is present directly in the `Sl. No.` column the table where the transactions are listed. So each of the `Sl. No.` looks like: `1/25`")
    # description_of_the_property: str = Field(..., description="Property Description  is directly present in the `Description of the Property` column (2nd column) the table where the transactions are listed. `Description of the Property` value looks like: `VILL/COL: KARIMNAGAR (U)/KATTARAMPUR W-B: 8-2 SURVEY: 916 PLOT: 2/A HOUSE: 8-2-384/1 EXTENT: 110SQ.Yds BUILT: 1326.12SQ. FT Boundaries: [N]: HOUSE IN PART OF PLOT NO.2 [S] HOUSE OF T RAMASWAMY [E]: PLOT NO.3 [W]: PLOT NO.1&2 Link Doct: 9988/2018 Book-1 of SRO 2013`")
    linked_document_numbers: list[str] = Field(..., description="In the  `description of the property` column, at the end of the description there will be linked documents listed, example: `Link Doct: 2753/2013 Book-1 of SRO 2013`, you are supposed to extract `2753/2013` from this. It will look like {Number/year}, it may also sometimes be tagged with the number like 7464/2024 [1] . ONLY EXTRACT `7464/2024` at that time")
    extent: ExtentTelangana = Field(..., description="`Extent` is present in the property description column, extract the extent of the property. Example Extent: `Extent: 225 Y`.")
    transaction_dates: DatesTelangana = Field(..., description= "This is 3rd column and single column contains all three dates, `Registration Date`, `Execution Date`, `Presentation Date`, we are supposed to extract from each transaction/row")
    property_value: ValueTelangana = Field(..., description="This is the fourth column and single column contains all three values, `Nature of Deed`, `Market Value`, `Consideration Value`, we are supposed to extract from each transaction/row")
    transaction_party_name: PartyTelanagana = Field(..., description="Name of the party involved in the transaction")
    document_number: str = Field(..., description="In the final column, Extract from the cell for document number. It will look something like `259/2025`, `7464/2024`. It will look like {Number/year}, it may also sometimes be tagged with the number like 7464/2024 [1] . ONLY EXTRACT `7464/2024` at that time")


class TransactionsTelangana(BaseModel):
    """List of all items involved in the transaction."""
    items: List[ItemTelangana] = Field(..., description="List of transaction items")

# Below three classes are used to define the top level structure of the extraction and are used in the prompts

class NameMatchTelangana(BaseModel):
    match: bool = Field(..., description="From the given input by the user, you will get the name of the person which we want to match, this can be present in either CLAIMANT, EXECUTANT column of every page, if you find the name given by the user, fill in the True for this value.")
    matched_name: str = Field(..., description="From the given input by the user, you will get the name of the person which we want to match, this can be present in either CLAIMANT, EXECUTANT column of every page, if you find the name given by the user, fill in Name of the user here, if there are multiple value, you can just include the first one. Make sure you just include the name and not (CL) / (EX) / (MR) / (ME) etc, this will be 'NA' if there is no match.")


class ExtractionClassTelangana(BaseModel):
    """Top-level structure representing the full document."""
    headers: HeadersTelangana = Field(..., description="This is the header of the page in the first page, which contains the `Application Number`, `Statement Number`, and Complete Address of the property.")
    transactions: TransactionsTelangana = Field(..., description= "List of transactions. In the transactions table, each row is a transaction. The table contains the following columns: `Sl. No.`, `Description of the Property`, (`Registration Date`, `Execution Date`, `Presentation Date`) in one column, (`Nature of Deed`, `Market Value`, `Consideration Value`) in one column, (`Executant`, `Claimant`) in one column. Each column descriptions are described below.")
    name_match: NameMatchTelangana = Field(..., description="From the given input by the user, you will get the name of the person which we want to match, this can be present in either CLAIMANT, EXECUTANT column of every page, if you find the name given by the user please fill in the details.")


class AIAgentClassTelangana(BaseModel):
    """Agent prompt for the document extraction."""
    information: str = Field(..., description="Given a PDF/Image/Text page as input, the page is basically Encumbrance Certificate (EC) of the property owner. This contains the information in English and belongs to Telangana State. The document usually contains the information about the ownership, ownership history, and any encumbrances and transactions of the property. The document is usually issued by the local government authority or revenue department.")
    instruction: str = Field(..., description="Given the Encumbrance Certificate document as input extract the the following information from the document as a clear JSON format as mentioned for each field. The field type is also mentioned in with the name of the field in the json. whatever the language is in the PDF/Image/Text page, make sure the information is put in english.")
    condition: str = Field(..., description="Make sure if the information is present then to make the field `NA` (Even if the field type is other than string. This applies to all the fields.")


##########################################################ANDHRA SCHEMA##########################################################

class ExtentAndhra(BaseModel):
    """Property extent details."""
    extent: float = Field(..., description="`Extent` is present on the top of the page, extract the extent of the property. Example Extent: `Extent: 225 Y`. Lets have float value for it.")
    unit: str = Field(..., description="`Unit` is present on the top of the page, extract the unit of the extent. Example Unit: `Y` (Yards). Note: The unit can be `SQ. YDS`, `SQ. FT`, `ACRES`, etc. depending on the property.")

class BuiltUpAndhra(BaseModel):
    """Built up area details."""
    built_up_area: str = Field(..., description="`Built Up Area` is present on the top of the page, extract the built up area of the property. Example Built Up Area: `Built: 1326.12SQ. FT`.")
    unit: str = Field(..., description="`Unit` is present on the top of the page, extract the unit of the built up area. Example Unit: `SQ. FT` (Square Feet). Note: The unit can be `SQ. YDS`, `SQ. FT`, etc. depending on the property.")

class BoundedByAndhra(BaseModel):
    """Bounded by details."""
    north: str = Field(..., description="`North` boundary is present on the top of the page, extract the north boundary information. Example North: `HOUSE IN PART OF PLOT NO.2`.")
    south: str = Field(..., description="`South` boundary is present on the top of the page, extract the south boundary information. Example South: `HOUSE OF T RAMASWAMY`.")
    east: str = Field(..., description="`East` boundary is present on the top of the page, extract the east boundary information. Example East: `PLOT NO.3`.")
    west: str = Field(..., description="`West` boundary is present on the top of the page, extract the west boundary information. Example West: `PLOT NO.1&2`.")

class HeadersAndhra(BaseModel):
    """Document header details."""
    application_number: int = Field(..., description="`Application Number` is present on the top of the page, extract the number the page. Example Application Number: `24710`.")
    statement_number: int = Field(..., description="`Statement Number` is present on the top of the page, extract the number the page. Example Statement Number: `194951191`.")
    # extent: ExtentTelangana = Field(..., description="`Extent` is present on the top of the page, extract the extent of the property. Example Extent: `Extent: 225 Y`.")
    complete_address: str = Field(..., description="This is not present directly, But put all fields together in one string. Field you should extract are `ward block`, `survey number`, `house number`, `plot number`,, `build up area`, `flat number`, `apartment` and `bounded by`. Put them together to get one address. example address: `VILL/COL: MAHADEVAPURAM/ALL (0-0) W-B: 0-0 SURVEY: 290-1 HOUSE: 1-46A EXTENT: 145.2SQ.Yds BUILT: 286SQ. FT Boundires:[N]: Panta kalva [S] Rastha [E]: House of k.malibasha [W]: House of shaik madar Sa")
    # ward_block: str = Field(..., description="`Ward Block` is present on the top of the page, extract the ward block information. Example Ward Block: `Ward - Block: 0 - 1`.")
    # survey_number: str = Field(..., description="`Survey Number` is present on the top of the page, extract the survey number. Example Survey Number: `Survey Number: 684/R,684/A,685/E,685/A`.")
    # house_number: str = Field(..., description="`House Number` is present on the top of the page, extract the house number. Example House Number: `Plot Number: 352`.")
    # plot_number: str = Field(..., description="`Plot Number` is present on the top of the page, extract the plot number. Example Plot Number: `Plot Number: 352`.")
    extent: ExtentAndhra = Field(..., description="`Extent` is present on the top of the page, extract the extent of the property. Example Extent: `Extent: 225 Y`.")
    # built_up_area: BuiltUpAndhra = Field(..., description="`Built Up Area` is present on the top of the page, extract the built up area of the property. Example Built Up Area: `Built: 1326.12SQ. FT`.")
    # flat_number: str = Field(..., description="`Flat Number` is present on the top of the page, extract the flat number. Example Flat Number: `House: 8-2-384/1`.")
    # apartment: str = Field(..., description="`Apartment` is present on the top of the page, extract the apartment name. Example Apartment: `KATTARAMPUR W-B: 8-2`.")
    # bounded_by: BoundedByAndhra = Field(..., description="`Bounded By` is present on the top of the page, extract the bounded by information. Example Bounded By: `Boundaries: [N]: HOUSE IN PART OF PLOT NO.2 [S] HOUSE OF T RAMASWAMY [E]: PLOT NO.3 [W]: PLOT NO.1&2`.")


class DatesAndhra(BaseModel):
    """Important dates related to the transaction."""
    registration_date: str = Field(..., description= "Date of registration in each row")
    execution_date: str = Field(..., description= "Date of transaction in each row")
    presentation_date: str = Field(..., description= "Date of presentation in each row")


class ValueAndhra(BaseModel):
    """Monetary details of the transaction."""
    nature_of_deed: str = Field(..., description="Type or nature of the deed")
    market_value: str = Field(..., description="Estimated market value of the property")
    consideration_value: str = Field(..., description="Monetary value exchanged")


class PartyAndhra(BaseModel):
    """Parties involved in the transaction."""
    executant: list[str] = Field(..., description= "List of Name of the executor. This will always be defined in the number 1. Example: `1.(MR)KATUKOJWALA SUMAN`, extract the name `(MR)KATUKOJWALA SUMAN` from this string. The Executant can have code like: `EX` - Executant, `MR` - Mortgagor, `RR` - Releasor, `DR` - Donor.")
    claimant: list[str] = Field(..., description= "List of Name of the claimant. This will always be defined in the number 2. Example: `2.(MR)KATUKOJWALA SUMAN`, extract the name `(MR)KATUKOJWALA SUMAN` from this string. The Executant can have code like: `CL` - Claimant, `ME` - Mortgagee, `RE` - Releasee, `DE` - Donee.")


class ItemAndhra(BaseModel):
    """Individual transaction item."""
    serial_number: str = Field(..., description= "Serial Number is present directly in the `Sl. No.` column the table where the transactions are listed. So each of the `Sl. No.` looks like: `1/25`")
    # description_of_the_property: str = Field(..., description="Property Description  is directly present in the `Description of the Property` column (2nd column) the table where the transactions are listed. `Description of the Property` value looks like: `VILL/COL: KARIMNAGAR (U)/KATTARAMPUR W-B: 8-2 SURVEY: 916 PLOT: 2/A HOUSE: 8-2-384/1 EXTENT: 110SQ.Yds BUILT: 1326.12SQ. FT Boundaries: [N]: HOUSE IN PART OF PLOT NO.2 [S] HOUSE OF T RAMASWAMY [E]: PLOT NO.3 [W]: PLOT NO.1&2 Link Doct: 9988/2018 Book-1 of SRO 2013`")
    linked_document_numbers: list[str] = Field(..., description="In the  `description of the property` column, at the end of the description there will be linked documents listed, example: `Link Doct: 2753/2013 Book-1 of SRO 2013`, you are supposed to extract `2753/2013` from this. It will look like {Number/year}, it may also sometimes be tagged with the number like 7464/2024 [1] . ONLY EXTRACT `7464/2024` at that time")
    extent: ExtentTelangana = Field(..., description="`Extent` is present in the property description column, extract the extent of the property. Example Extent: `Extent: 225 Y`.")
    transaction_dates: DatesAndhra = Field(..., description= "This is 3rd column and single column contains all three dates, `Registration Date`, `Execution Date`, `Presentation Date`, we are supposed to extract from each transaction/row")
    property_value: ValueAndhra = Field(..., description="This is the fourth column and single column contains all three values, `Nature of Deed`, `Market Value`, `Consideration Value`, we are supposed to extract from each transaction/row")
    transaction_party_name: PartyAndhra = Field(..., description="Name of the party involved in the transaction")
    # vol_page_number: str = Field(..., description="`Vol/Page Number` is present on the top of the page, extract the volume and page number. Example Vol/Page Number: `Vol: 1 Page: 25`.")
    # cd_no_doct: str = Field(..., description="`CD No/Doct No` is present on the top of the page, extract the CD number and document number. Example CD No/Doct No: `CD No: 1234567890 Doct No: 9876543210`.")
    # year: str = Field(..., description="`Year` is present on the top of the page, extract the year of the transaction. Example Year: `2023`.")
    # schedule_no: str = Field(..., description="`Schedule No` is present on the top of the page, extract the schedule number. Example Schedule No: `Schedule No: 123`.")
    document_number: str = Field(..., description="In the final column, Extract from the cell for document number. It will look something like `259/2025`, `7464/2024`. It will look like {Number/year}, it may also sometimes be tagged with the number like 7464/2024 [1] . ONLY EXTRACT `7464/2024` at that time")


class TransactionsAndhra(BaseModel):
    """List of all items involved in the transaction."""
    items: List[ItemAndhra] = Field(..., description="List of transaction items")

# Below three classes are used to define the top level structure of the extraction and are used in the prompts


class NameMatchAndhra(BaseModel):
    match: bool = Field(..., description="From the given input by the user, you will get the name of the person which we want to match, this can be present in either CLAIMANT, EXECUTANT column of every page, if you find the name given by the user, fill in the True for this value.")
    matched_name: str = Field(..., description="From the given input by the user, you will get the name of the person which we want to match, this can be present in either CLAIMANT, EXECUTANT column of every page, if you find the name given by the user, fill in Name of the user here, if there are multiple value, you can just include the first one. Make sure you just include the name and not (CL) / (EX) / (MR) / (ME) etc, this will be 'NA' if there is no match.")


class ExtractionClassAndhra(BaseModel):
    """Top-level structure representing the full document."""
    headers: HeadersAndhra = Field(..., description="This is the header of the page in the first page, which contains the `Application Number`, `Statement Number`, and Complete Address of the property.")
    transactions: TransactionsAndhra = Field(..., description= "List of transactions. In the transactions table, each row is a transaction. The table contains the following columns: `Sl. No.`, `Description of the Property`, (`Registration Date`, `Execution Date`, `Presentation Date`) in one column, (`Nature of Deed`, `Market Value`, `Consideration Value`) in one column, (`Executant`, `Claimant`) in one column. Each column descriptions are described below.")
    name_match: NameMatchAndhra = Field(..., description="From the given input by the user, you will get the name of the person which we want to match, this can be present in either CLAIMANT, EXECUTANT column of every page, if you find the name given by the user please fill in the details.")

class AIAgentClassAndhra(BaseModel):
    """Agent prompt for the document extraction."""
    information: str = Field(..., description="Given a PDF/Image/Text page as input, the page is basically Encumbrance Certificate (EC) of the property owner. This contains the information in English and belongs to Telangana State. The document usually contains the information about the ownership, ownership history, and any encumbrances and transactions of the property. The document is usually issued by the local government authority or revenue department.")
    instruction: str = Field(..., description="Given the Encumbrance Certificate document as input extract the the following information from the document as a clear JSON format as mentioned for each field. The field type is also mentioned in with the name of the field in the json. whatever the language is in the PDF/Image/Text page, make sure the information is put in english.")
    condition: str = Field(..., description="Make sure if the information is present then to make the field `NA` (Even if the field type is other than string. This applies to all the fields.")


##########################################################for doc number##########################################################


class ExtractionForDocNumber(BaseModel):
    """Top-level structure representing the full document."""
    first_vol_pg_number: str = Field(..., description="Only focus on first transaction from the table + only fovus on last column. Extract from the cell for vol pg number. It will look something like `0/0`.")
    document_number: str = Field(..., description="Only focus on first transaction from the table + only fovus on last column. Extract from the cell for document number. It will look something like `259/2025`, `7464/2024`. It will look like {Number/year}, it may also sometimes be tagged with the number like 7464/2024 [1] . ONLY EXTRACT `7464/2024` at that time")
    sro: str = Field(..., description="Only focus on first transaction from the table + only fovus on last column. Extract from the cell for SRO name. It will look something like SRO `SIRVELLA`, Basically regional office name, make sure you do not extract `SRO`, it should just be name. For example it will be given SRO WARANGAL, you must extract only `WARANGAL`")
    sro_number: str = Field(..., description="Only focus on first transaction from the table + only fovus on last column. Extract from the cell for SRO name. It will look something like SRO code which comes after the SRO Name, Example `SRO WARANGAL (RURAL)(2110)`, in this you should extract `2110`.")


class ExtractionClass(BaseModel):
    """Top-level structure representing the full document."""
    first_transaction_doc_number: ExtractionForDocNumber = Field(..., description="There will be a table, you have to focus on first transaction. FROM THE First transaction, focus on Last Column, this column will have 4 parameters in a cell. `Vol/Pg No`, `document number`, year of registration and schedule number, you are supposed to extract them well.")


class AIAgentClass(BaseModel):
    """Agent prompt for the document extraction."""
    information: str = Field(..., description="Given a PDF page as input, the page is basically Encumbrance Certificate (EC) of the property owner. This contains the information in English and belongs to Telangana State. The document usually contains the information about the ownership, ownership history, and any encumbrances and transactions of the property. The document is usually issued by the local government authority or revenue department.")
    instruction: str = Field(..., description="Given the Encumbrance Certificate document as input extract the the following information from the document as a clear JSON format as mentioned for each field. The field type is also mentioned in with the name of the field in the json. whatever the language is in the PDF/Image/Text page, make sure the information is put in english.")
    condition: str = Field(..., description="Make sure if the information is present then to make the field `NA` (Even if the field type is other than string. This applies to all the fields., FOCUS ON the table which has transactions and focus on the first transaction only.")

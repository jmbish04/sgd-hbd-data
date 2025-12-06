from pydantic import BaseModel, Field
from typing import Optional, List, Dict

# ==========================================
# RAW INGESTION TABLE MODELS
# ==========================================

class RawHdbResalePrices(BaseModel):
    """Pydantic model for the rawHdbResalePrices table."""
    id: Optional[int] = None
    month: Optional[str] = None # YYYY-MM
    year: Optional[int] = None # Normalized
    town: Optional[str] = None
    flatType: Optional[str] = Field(None, alias='flat_type')
    block: Optional[str] = None
    streetName: Optional[str] = Field(None, alias='street_name')
    storeyRange: Optional[str] = Field(None, alias='storey_range')
    floorAreaSqm: Optional[float] = Field(None, alias='floor_area_sqm')
    flatModel: Optional[str] = Field(None, alias='flat_model')
    leaseCommenceDate: Optional[int] = Field(None, alias='lease_commence_date')
    remainingLease: Optional[str] = Field(None, alias='remaining_lease')
    resalePrice: Optional[float] = Field(None, alias='resale_price')
    monthRaw: Optional[str] = None
    remainingLeaseYears: Optional[int] = None # Normalized
    remainingLeaseMonths: Optional[int] = None # Normalized
    leaseExpirationDate: Optional[str] = None # Normalized (from remaining lease)
    storeyRangeStart: Optional[int] = None # Normalized
    storeyRangeEnd: Optional[int] = None # Normalized
    resaleDate: Optional[str] = None # Normalized YYYY-MM-DD

    # Geocoding enrichment columns
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    postalCode: Optional[str] = None
    isGeocoded: Optional[bool] = Field(False, alias='is_geocoded')


class RawHdbMedianRent(BaseModel):
    """Pydantic model for the rawHdbMedianRent table."""
    id: Optional[int] = None
    town: Optional[str] = None
    flatType: Optional[str] = Field(None, alias='flat_type')
    flatTypeRaw: Optional[str] = None
    medianRent: Optional[float] = Field(None, alias='median_rent')
    medianRentRaw: Optional[str] = None # Raw string from CSV
    quarter: Optional[int] = None # Normalized
    quarterRaw: Optional[str] = None # e.g. "2023-Q1"
    year: Optional[int] = None # Normalized
    startMonth: Optional[int] = None # Normalized
    endMonth: Optional[int] = None # Normalized


class RawHdbRentalPrices(BaseModel):
    """Pydantic model for the rawHdbRentalPrices table."""
    id: Optional[int] = None
    rentApprovalDate: Optional[str] = Field(None, alias='rent_approval_date') # YYYY-MM
    town: Optional[str] = None
    block: Optional[str] = None
    streetName: Optional[str] = Field(None, alias='street_name')
    flatType: Optional[str] = Field(None, alias='flat_type')
    monthlyRent: Optional[float] = Field(None, alias='monthly_rent')

    # Geocoding and Normalized
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    postalCode: Optional[str] = None
    isGeocoded: Optional[bool] = Field(False, alias='is_geocoded')
    rentApprovalYear: Optional[int] = None # Normalized
    rentApprovalMonth: Optional[int] = None # Normalized


class RawHdbResaleIndex(BaseModel):
    """Pydantic model for the rawHdbResaleIndex table."""
    id: Optional[int] = None
    town: Optional[str] = None
    flatType: Optional[str] = Field(None, alias='flat_type')
    index: Optional[float] = None
    quarter: Optional[int] = None # Normalized
    quarterRaw: Optional[str] = None
    year: Optional[int] = None # Normalized
    datasetId: Optional[str] = None
    ingestedAt: Optional[str] = None


class RawHawkerCentresGeojson(BaseModel):
    """Pydantic model for the rawHawkerCentresGeojson table."""
    id: Optional[int] = None
    datasetId: Optional[str] = None
    ingestedAt: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    addressMyenv: Optional[str] = None
    addressBuildingName: Optional[str] = None
    addressPostalCode: Optional[str] = None
    addressStreetName: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    geometryType: Optional[str] = None
    numberOfCookedFoodStalls: Optional[int] = None
    estOriginalCompletionDate: Optional[str] = None
    implementationDate: Optional[str] = None
    awardedDate: Optional[str] = None


class RawGovMarketsHawkerCentres(BaseModel):
    """Pydantic model for the rawGovMarketsHawkerCentres table."""
    id: Optional[int] = None
    datasetId: Optional[str] = None
    ingestedAt: Optional[str] = None
    nameOfCentre: Optional[str] = None
    locationOfCentre: Optional[str] = None
    typeOfCentre: Optional[str] = None
    owner: Optional[str] = None
    noOfStalls: Optional[int] = None
    noOfCookedFoodStalls: Optional[int] = None
    noOfMktProduceStalls: Optional[int] = None
    isMarket: Optional[bool] = None
    isHawkerCentre: Optional[bool] = None


class RawHdbPropertyInfo(BaseModel):
    """Pydantic model for the rawHdbPropertyInfo table."""
    id: Optional[int] = None
    blkNo: Optional[str] = Field(None, alias='blk_no')
    street: Optional[str] = None
    maxFloorLvl: Optional[int] = Field(None, alias='max_floor_lvl')
    yearCompleted: Optional[int] = Field(None, alias='year_completed')
    bldgContractTown: Optional[str] = Field(None, alias='bldg_contract_town')
    residential: Optional[str] = None
    commercial: Optional[str] = None
    marketHawker: Optional[str] = Field(None, alias='market_hawker')
    miscellaneous: Optional[str] = None
    multistoreyCarpark: Optional[str] = Field(None, alias='multistorey_carpark')
    precinctPavilion: Optional[str] = Field(None, alias='precinct_pavilion')
    oneRoomSold: Optional[int] = Field(None, alias='1room_sold')
    twoRoomSold: Optional[int] = Field(None, alias='2room_sold')
    threeRoomSold: Optional[int] = Field(None, alias='3room_sold')
    fourRoomSold: Optional[int] = Field(None, alias='4room_sold')
    fiveRoomSold: Optional[int] = Field(None, alias='5room_sold')
    execSold: Optional[int] = Field(None, alias='exec_sold')
    multigenSold: Optional[int] = Field(None, alias='multigen_sold')
    studioApartmentSold: Optional[int] = Field(None, alias='studio_apartment_sold')
    oneRoomRental: Optional[int] = Field(None, alias='1room_rental')
    twoRoomRental: Optional[int] = Field(None, alias='2room_rental')
    threeRoomRental: Optional[int] = Field(None, alias='3room_rental')
    otherRoomRental: Optional[int] = Field(None, alias='other_room_rental')


# ==========================================
# SCAFFOLDED DATASETS
# ==========================================

class RawHdbExistingBuilding(BaseModel):
    """Pydantic model for raw_hdb_existing_building"""
    id: Optional[int] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    datasetId: Optional[str] = None
    ingestedAt: Optional[str] = None
    mapKmlName: Optional[str] = None
    htmlDescription: Optional[str] = None
    geometryPoint: Optional[str] = None
    objectid: Optional[int] = Field(None, alias='OBJECTID')
    blkNo: Optional[int] = Field(None, alias='BLK_NO')
    stCod: Optional[str] = Field(None, alias='ST_COD')
    entityid: Optional[int] = Field(None, alias='ENTITYID')
    postalCod: Optional[int] = Field(None, alias='POSTAL_COD')
    incCrc: Optional[str] = Field(None, alias='INC_CRC')
    fmelUpdD: Optional[int] = Field(None, alias='FMEL_UPD_D')
    shape_area: Optional[int] = Field(None, alias='SHAPE.AREA')
    shape_len: Optional[int] = Field(None, alias='SHAPE.LEN')

class RawSgPreschoolCentres(BaseModel):
    """Pydantic model for raw_sg_preschool_centres"""
    id: Optional[int] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    datasetId: Optional[str] = None
    ingestedAt: Optional[str] = None
    geometryPoint: Optional[str] = None
    mapKmlName: Optional[str] = Field(None, alias='Name')
    htmlDescription: Optional[str] = Field(None, alias='Description')
    objectid1: Optional[int] = Field(None, alias='OBJECTID_1')
    lCode: Optional[str] = Field(None, alias='L_CODE')
    name: Optional[str] = Field(None, alias='NAME')
    nReserve: Optional[int] = Field(None, alias='N_RESERVE')
    incCrc: Optional[str] = Field(None, alias='INC_CRC')
    fmelUpdD: Optional[int] = Field(None, alias='FMEL_UPD_D')
    shape1_area: Optional[int] = Field(None, alias='SHAPE_1.AREA')
    shape1_len: Optional[int] = Field(None, alias='SHAPE_1.LEN')

class RawSgStudentCareCentres(BaseModel):
    """Pydantic model for raw_sg_student_care_centres"""
    id: Optional[int] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    datasetId: Optional[str] = None
    ingestedAt: Optional[str] = None
    geometryPoint: Optional[str] = None
    mapKmlName: Optional[str] = None
    htmlDescription: Optional[str] = None
    parsedAttributes: Optional[str] = None
    name: Optional[str] = Field(None, alias='Name')
    description: Optional[str] = Field(None, alias='Description')

class RawSgSchoolDirectory(BaseModel):
    """Pydantic model for raw_sg_school_directory"""
    id: Optional[int] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    datasetId: Optional[str] = None
    ingestedAt: Optional[str] = None
    geometryPoint: Optional[str] = None
    mapKmlName: Optional[str] = None
    htmlDescription: Optional[str] = None
    objectid: Optional[int] = Field(None, alias='OBJECTID')
    venue: Optional[str] = Field(None, alias='VENUE')
    addressblockhousenumber: Optional[int] = Field(None, alias='ADDRESSBLOCKHOUSENUMBER')
    addressstreetname: Optional[str] = Field(None, alias='ADDRESSSTREETNAME')
    postalCode: Optional[int] = Field(None, alias='POSTAL_CODE')
    details: Optional[str] = Field(None, alias='DETAILS')
    incCrc: Optional[str] = Field(None, alias='INC_CRC')
    fmelUpdD: Optional[int] = Field(None, alias='FMEL_UPD_D')

class RawSgCarparkHdb(BaseModel):
    """Pydantic model for raw_sg_carpark_hdb"""
    id: Optional[int] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    datasetId: Optional[str] = None
    ingestedAt: Optional[str] = None
    geometryPoint: Optional[str] = None
    mapKmlName: Optional[str] = None
    htmlDescription: Optional[str] = None
    name: Optional[str] = Field(None, alias='Name')
    description: Optional[str] = Field(None, alias='Description')

class RawSgCarparkUra(BaseModel):
    """Pydantic model for raw_sg_carpark_ura"""
    id: Optional[int] = None
    datasetId: Optional[str] = None
    ingestedAt: Optional[str] = None
    mapKmlName: Optional[str] = None
    htmlDescription: Optional[str] = None
    geometryPoint: Optional[str] = None
    objectid: Optional[int] = Field(None, alias='OBJECTID')
    uniqueid: Optional[str] = Field(None, alias='UNIQUEID')
    name: Optional[str] = Field(None, alias='NAME')
    class_: Optional[str] = Field(None, alias='CLASS')
    additionalInfo: Optional[str] = Field(None, alias='ADDITIONAL_INFO')
    incCrc: Optional[str] = Field(None, alias='INC_CRC')
    fmelUpdD: Optional[int] = Field(None, alias='FMEL_UPD_D')
    lat: Optional[float] = None
    lng: Optional[float] = None

class RawSgTaxiStands(BaseModel):
    """Pydantic model for raw_sg_taxi_stands"""
    id: Optional[int] = None
    datasetId: Optional[str] = None
    ingestedAt: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    geometryPoint: Optional[str] = None
    mapKmlName: Optional[str] = None
    htmlDescription: Optional[str] = None
    objectid: Optional[int] = Field(None, alias='OBJECTID')
    name: Optional[str] = Field(None, alias='NAME')
    x: Optional[int] = Field(None, alias='X')
    y: Optional[int] = Field(None, alias='Y')
    incCrc: Optional[str] = Field(None, alias='INC_CRC')
    fmelUpdD: Optional[int] = Field(None, alias='FMEL_UPD_D')

class RawSgBusStops(BaseModel):
    """Pydantic model for raw_sg_bus_stops"""
    id: Optional[int] = None
    datasetId: Optional[str] = None
    ingestedAt: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    geometryPoint: Optional[str] = None
    mapKmlName: Optional[str] = Field(None, alias='Name')
    htmlDescription: Optional[str] = Field(None, alias='Description')
    parsedAttributes: Optional[str] = None
    licName: Optional[str] = None
    blkHouse: Optional[str] = None
    strName: Optional[str] = None
    unitNo: Optional[str] = None
    postcode: Optional[str] = None
    licNo: Optional[str] = None
    incCrc: Optional[str] = None
    fmelUpdD: Optional[str] = None

class RawSgMrtStationExits(BaseModel):
    """Pydantic model for raw_sg_mrt_station_exits"""
    id: Optional[int] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    datasetId: Optional[str] = None
    ingestedAt: Optional[str] = None
    mapKmlName: Optional[str] = None
    htmlDescription: Optional[str] = None
    geometryPoint: Optional[str] = None
    objectid1: Optional[int] = Field(None, alias='OBJECTID_1')
    lastUpdated: Optional[int] = Field(None, alias='LAST_UPDATED')
    name: Optional[str] = Field(None, alias='NAME')
    description: Optional[str] = Field(None, alias='DESCRIPTION')
    status: Optional[str] = Field(None, alias='STATUS')
    estmtCnstrnCmcmnt: Optional[str] = Field(None, alias='ESTMT_CNSTRN_CMCMNT')
    estmtCnstrnCmpltn: Optional[str] = Field(None, alias='ESTMT_CNSTRN_CMPLTN')
    cnstrnCmcmnt: Optional[int] = Field(None, alias='CNSTRN_CMCMNT')
    implmtOrg: Optional[str] = Field(None, alias='IMPLMT_ORG')
    qsmContact: Optional[str] = Field(None, alias='QSM_CONTACT')
    ctrctrName: Optional[int] = Field(None, alias='CTRCTR_NAME')
    ctrctrCntct: Optional[int] = Field(None, alias='CTRCTR_CNTCT')
    incCrc: Optional[str] = Field(None, alias='INC_CRC')
    fmelUpdD: Optional[int] = Field(None, alias='FMEL_UPD_D')
    shape_area: Optional[int] = Field(None, alias='SHAPE.AREA')
    shape_len: Optional[int] = Field(None, alias='SHAPE.LEN')

class RawSgCyclingNetwork(BaseModel):
    """Pydantic model for raw_sg_cycling_network"""
    id: Optional[int] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    datasetId: Optional[str] = None
    ingestedAt: Optional[str] = None
    geometryPoint: Optional[str] = None
    mapKmlName: Optional[str] = None
    htmlDescription: Optional[str] = None
    parsedAttributes: Optional[str] = None
    name: Optional[str] = Field(None, alias='Name')
    description: Optional[str] = Field(None, alias='Description')

class RawSgTrafficIncidents(BaseModel):
    """Pydantic model for raw_sg_traffic_incidents"""
    id: Optional[int] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    datasetId: Optional[str] = None
    ingestedAt: Optional[str] = None
    geometryPoint: Optional[str] = None
    mapKmlName: Optional[str] = None
    htmlDescription: Optional[str] = None
    objectid: Optional[int] = Field(None, alias='OBJECTID')
    grndLevel: Optional[str] = Field(None, alias='GRND_LEVEL')
    railType: Optional[str] = Field(None, alias='RAIL_TYPE')
    name: Optional[str] = Field(None, alias='NAME')
    incCrc: Optional[str] = Field(None, alias='INC_CRC')
    fmelUpdD: Optional[int] = Field(None, alias='FMEL_UPD_D')
    shape_area: Optional[int] = Field(None, alias='SHAPE.AREA')
    shape_len: Optional[int] = Field(None, alias='SHAPE.LEN')

class RawSgTrafficSpeedBands(BaseModel):
    """Pydantic model for raw_sg_traffic_speed_bands"""
    id: Optional[int] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    datasetId: Optional[str] = None
    ingestedAt: Optional[str] = None
    geometryPoint: Optional[str] = None
    mapKmlName: Optional[str] = None
    htmlDescription: Optional[str] = None
    objectid: Optional[int] = Field(None, alias='OBJECTID')
    featureid: Optional[int] = Field(None, alias='FEATUREID')
    zorder: Optional[int] = Field(None, alias='ZORDER')
    annotationclassid: Optional[int] = Field(None, alias='ANNOTATIONCLASSID')
    symbolid: Optional[int] = Field(None, alias='SYMBOLID')
    status: Optional[int] = Field(None, alias='STATUS')
    textstring: Optional[str] = Field(None, alias='TEXTSTRING')
    fontname: Optional[str] = Field(None, alias='FONTNAME')
    fontsize: Optional[int] = Field(None, alias='FONTSIZE')
    bold: Optional[int] = Field(None, alias='BOLD')
    italic: Optional[int] = Field(None, alias='ITALIC')
    underline: Optional[int] = Field(None, alias='UNDERLINE')
    verticalalignment: Optional[int] = Field(None, alias='VERTICALALIGNMENT')
    horizontalalignment: Optional[int] = Field(None, alias='HORIZONTALALIGNMENT')
    xoffset: Optional[int] = Field(None, alias='XOFFSET')
    yoffset: Optional[int] = Field(None, alias='YOFFSET')
    angle: Optional[int] = Field(None, alias='ANGLE')
    fontleading: Optional[int] = Field(None, alias='FONTLEADING')
    wordspacing: Optional[int] = Field(None, alias='WORDSPACING')
    characterwidth: Optional[int] = Field(None, alias='CHARACTERWIDTH')
    characterspacing: Optional[int] = Field(None, alias='CHARACTERSPACING')
    flipangle: Optional[int] = Field(None, alias='FLIPANGLE')
    override: Optional[int] = Field(None, alias='OVERRIDE')
    incCrc: Optional[str] = Field(None, alias='INC_CRC')
    fmelUpdD: Optional[int] = Field(None, alias='FMEL_UPD_D')
    shape_area: Optional[int] = Field(None, alias='SHAPE.AREA')
    shape_len: Optional[int] = Field(None, alias='SHAPE.LEN')

class RawSgSupermarkets(BaseModel):
    """Pydantic model for raw_sg_supermarkets"""
    id: Optional[int] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    datasetId: Optional[str] = None
    ingestedAt: Optional[str] = None
    geometryPoint: Optional[str] = None
    mapKmlName: Optional[str] = None
    htmlDescription: Optional[str] = None
    parsedAttributes: Optional[str] = None
    name: Optional[str] = Field(None, alias='Name')
    description: Optional[str] = Field(None, alias='Description')

class RawSgEatingEstablishments(BaseModel):
    """Pydantic model for raw_sg_eating_establishments"""
    id: Optional[int] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    datasetId: Optional[str] = None
    ingestedAt: Optional[str] = None
    geometryPoint: Optional[str] = None
    mapKmlName: Optional[str] = None
    htmlDescription: Optional[str] = None
    parsedAttributes: Optional[str] = None
    name: Optional[str] = Field(None, alias='Name')
    description: Optional[str] = Field(None, alias='Description')

class RawSgSportsFacilities(BaseModel):
    """Pydantic model for raw_sg_sports_facilities"""
    id: Optional[int] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    datasetId: Optional[str] = None
    ingestedAt: Optional[str] = None
    geometryPoint: Optional[str] = None
    mapKmlName: Optional[str] = None
    htmlDescription: Optional[str] = None
    objectid: Optional[int] = Field(None, alias='OBJECTID')
    hyperlink: Optional[str] = Field(None, alias='HYPERLINK')
    description: Optional[int] = Field(None, alias='DESCRIPTION')
    postalcode: Optional[int] = Field(None, alias='POSTALCODE')
    keepername: Optional[str] = Field(None, alias='KEEPERNAME')
    totalrooms: Optional[int] = Field(None, alias='TOTALROOMS')
    incCrc: Optional[str] = Field(None, alias='INC_CRC')
    fmelUpdD: Optional[int] = Field(None, alias='FMEL_UPD_D')
    name: Optional[str] = Field(None, alias='NAME')

class RawSgCommunityClubs(BaseModel):
    """Pydantic model for raw_sg_community_clubs"""
    id: Optional[int] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    datasetId: Optional[str] = None
    ingestedAt: Optional[str] = None
    mapKmlName: Optional[str] = None
    htmlDescription: Optional[str] = None
    geometryPoint: Optional[str] = None
    objectid: Optional[int] = Field(None, alias='OBJECTID')
    addresspostalcode: Optional[int] = Field(None, alias='ADDRESSPOSTALCODE')
    landxaddresspoint: Optional[int] = Field(None, alias='LANDXADDRESSPOINT')
    landyaddresspoint: Optional[int] = Field(None, alias='LANDYADDRESSPOINT')
    addressblockhousenumber: Optional[int] = Field(None, alias='ADDRESSBLOCKHOUSENUMBER')
    addressbuildingname: Optional[str] = Field(None, alias='ADDRESSBUILDINGNAME')
    addressfloornumber: Optional[int] = Field(None, alias='ADDRESSFLOORNUMBER')
    addressstreetname: Optional[str] = Field(None, alias='ADDRESSSTREETNAME')
    addresstype: Optional[int] = Field(None, alias='ADDRESSTYPE')
    description: Optional[str] = Field(None, alias='DESCRIPTION')
    name: Optional[str] = Field(None, alias='NAME')
    hyperlink: Optional[int] = Field(None, alias='HYPERLINK')
    photourl: Optional[int] = Field(None, alias='PHOTOURL')
    incCrc: Optional[str] = Field(None, alias='INC_CRC')
    fmelUpdD: Optional[int] = Field(None, alias='FMEL_UPD_D')
    addressunitnumber: Optional[int] = Field(None, alias='ADDRESSUNITNUMBER')

class RawSgPublicLibraries(BaseModel):
    """Pydantic model for raw_sg_public_libraries"""
    id: Optional[int] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    datasetId: Optional[str] = None
    ingestedAt: Optional[str] = None
    geometryPoint: Optional[str] = None
    mapKmlName: Optional[str] = None
    htmlDescription: Optional[str] = None
    objectid: Optional[int] = Field(None, alias='OBJECTID')
    addressblockhousenumber: Optional[int] = Field(None, alias='ADDRESSBLOCKHOUSENUMBER')
    addressbuildingname: Optional[int] = Field(None, alias='ADDRESSBUILDINGNAME')
    addressfloornumber: Optional[int] = Field(None, alias='ADDRESSFLOORNUMBER')
    addresspostalcode: Optional[int] = Field(None, alias='ADDRESSPOSTALCODE')
    addressstreetname: Optional[str] = Field(None, alias='ADDRESSSTREETNAME')
    addresstype: Optional[int] = Field(None, alias='ADDRESSTYPE')
    description: Optional[str] = Field(None, alias='DESCRIPTION')
    hyperlink: Optional[int] = Field(None, alias='HYPERLINK')
    landxaddresspoint: Optional[int] = Field(None, alias='LANDXADDRESSPOINT')
    landyaddresspoint: Optional[int] = Field(None, alias='LANDYADDRESSPOINT')
    name: Optional[str] = Field(None, alias='NAME')
    photourl: Optional[int] = Field(None, alias='PHOTOURL')
    incCrc: Optional[str] = Field(None, alias='INC_CRC')
    fmelUpdD: Optional[int] = Field(None, alias='FMEL_UPD_D')
    addressunitnumber: Optional[int] = Field(None, alias='ADDRESSUNITNUMBER')

class RawSgMuseums(BaseModel):
    """Pydantic model for raw_sg_museums"""
    id: Optional[int] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    datasetId: Optional[str] = None
    ingestedAt: Optional[str] = None
    geometryPoint: Optional[str] = None
    mapKmlName: Optional[str] = None
    htmlDescription: Optional[str] = None
    parsedAttributes: Optional[str] = None
    name: Optional[str] = Field(None, alias='Name')
    description: Optional[str] = Field(None, alias='Description')

class RawSgChasClinics(BaseModel):
    """Pydantic model for raw_sg_chas_clinics"""
    id: Optional[int] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    datasetId: Optional[str] = None
    ingestedAt: Optional[str] = None
    geometryPoint: Optional[str] = None
    mapKmlName: Optional[str] = None
    htmlDescription: Optional[str] = None
    parsedAttributes: Optional[str] = None
    name: Optional[str] = Field(None, alias='Name')
    description: Optional[str] = Field(None, alias='Description')

class RawSgPoliceEstablishments(BaseModel):
    """Pydantic model for raw_sg_police_establishments"""
    id: Optional[int] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    datasetId: Optional[str] = None
    ingestedAt: Optional[str] = None
    geometryPoint: Optional[str] = None
    mapKmlName: Optional[str] = None
    htmlDescription: Optional[str] = None
    parsedAttributes: Optional[str] = None
    name: Optional[str] = Field(None, alias='Name')
    description: Optional[str] = Field(None, alias='Description')

class RawSgFireStations(BaseModel):
    """Pydantic model for raw_sg_fire_stations"""
    id: Optional[int] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    datasetId: Optional[str] = None
    ingestedAt: Optional[str] = None
    mapKmlName: Optional[str] = None
    htmlDescription: Optional[str] = None
    geometryPoint: Optional[str] = None
    objectid: Optional[int] = Field(None, alias='OBJECTID')
    addressblockhousenumber: Optional[int] = Field(None, alias='ADDRESSBLOCKHOUSENUMBER')
    addressbuildingname: Optional[int] = Field(None, alias='ADDRESSBUILDINGNAME')
    addressfloornumber: Optional[int] = Field(None, alias='ADDRESSFLOORNUMBER')
    addresspostalcode: Optional[int] = Field(None, alias='ADDRESSPOSTALCODE')
    addressstreetname: Optional[str] = Field(None, alias='ADDRESSSTREETNAME')
    addresstype: Optional[int] = Field(None, alias='ADDRESSTYPE')
    description: Optional[int] = Field(None, alias='DESCRIPTION')
    hyperlink: Optional[int] = Field(None, alias='HYPERLINK')
    landxaddresspoint: Optional[int] = Field(None, alias='LANDXADDRESSPOINT')
    landyaddresspoint: Optional[int] = Field(None, alias='LANDYADDRESSPOINT')
    name: Optional[str] = Field(None, alias='NAME')
    photourl: Optional[int] = Field(None, alias='PHOTOURL')
    incCrc: Optional[str] = Field(None, alias='INC_CRC')
    fmelUpdD: Optional[int] = Field(None, alias='FMEL_UPD_D')
    addressunitnumber: Optional[int] = Field(None, alias='ADDRESSUNITNUMBER')

class RawSgDengueClusters(BaseModel):
    """Pydantic model for raw_sg_dengue_clusters"""
    id: Optional[int] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    datasetId: Optional[str] = None
    ingestedAt: Optional[str] = None
    mapKmlName: Optional[str] = None
    htmlDescription: Optional[str] = None
    geometryPoint: Optional[str] = None
    objectid: Optional[int] = Field(None, alias='OBJECTID')
    oid: Optional[int] = Field(None, alias='OID')
    luDesc: Optional[str] = Field(None, alias='LU_DESC')
    luText: Optional[str] = Field(None, alias='LU_TEXT')
    gpr: Optional[str] = Field(None, alias='GPR')
    whiteQMx: Optional[int] = Field(None, alias='WHITE_Q_MX')
    gprBMin: Optional[int] = Field(None, alias='GPR_B_MIN')
    incCrc: Optional[str] = Field(None, alias='INC_CRC')
    fmelUpdD: Optional[int] = Field(None, alias='FMEL_UPD_D')
    shape_area: Optional[int] = Field(None, alias='SHAPE.AREA')
    shape_len: Optional[int] = Field(None, alias='SHAPE.LEN')

class RawSgRainfallReadings(BaseModel):
    """Pydantic model for raw_sg_rainfall_readings"""
    id: Optional[int] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    datasetId: Optional[str] = None
    ingestedAt: Optional[str] = None
    geometryPoint: Optional[str] = None
    mapKmlName: Optional[str] = None
    htmlDescription: Optional[str] = None
    objectid: Optional[int] = Field(None, alias='OBJECTID')
    luDesc: Optional[str] = Field(None, alias='LU_DESC')
    luText: Optional[int] = Field(None, alias='LU_TEXT')
    gpr: Optional[str] = Field(None, alias='GPR')
    whiQMx: Optional[int] = Field(None, alias='WHI_Q_MX')
    gprBMn: Optional[int] = Field(None, alias='GPR_B_MN')
    incCrc: Optional[str] = Field(None, alias='INC_CRC')
    fmelUpdD: Optional[int] = Field(None, alias='FMEL_UPD_D')
    shape_area: Optional[int] = Field(None, alias='SHAPE.AREA')
    shape_len: Optional[int] = Field(None, alias='SHAPE.LEN')

class RawSgSportsFields(BaseModel):
    """Pydantic model for raw_sg_sports_fields"""
    id: Optional[int] = None
    datasetId: Optional[str] = None
    ingestedAt: Optional[str] = None
    name: Optional[str] = Field(None, alias='Name')
    description: Optional[str] = Field(None, alias='Description')
    lat: Optional[float] = None
    lng: Optional[float] = None
    geometryPoint: Optional[str] = None

class RawSgInfantCare(BaseModel):
    """Pydantic model for raw_sg_infant_care (Long Format)"""
    id: Optional[str] = None
    datasetId: Optional[str] = None
    ingestedAt: Optional[str] = None
    dataSeries: Optional[str] = Field(None, alias='DataSeries')
    year: Optional[int] = None
    value: Optional[int] = Field(None, alias='Value')

class RawSgParkConnector(BaseModel):
    """Pydantic model for raw_sg_park_connector"""
    id: Optional[int] = None
    datasetId: Optional[str] = None
    ingestedAt: Optional[str] = None
    objectid: Optional[int] = Field(None, alias='OBJECTID')
    prpStatus: Optional[str] = Field(None, alias='PRP_STATUS')
    incCrc: Optional[str] = Field(None, alias='INC_CRC')
    fmelUpdD: Optional[int] = Field(None, alias='FMEL_UPD_D')
    shapeLen: Optional[float] = Field(None, alias='SHAPE.LEN')
    lat: Optional[float] = None
    lng: Optional[float] = None
    geometryPoint: Optional[str] = None


# ==========================================
# AI ENGINE MODELS
# ==========================================

class ColumnMappingResult(BaseModel):
    """Result of mapping raw columns to schema fields."""
    mapping: Dict[str, Optional[str]] = Field(..., description="Map of raw column name to target field name (or None)")
    confidence: float = Field(..., description="Confidence score between 0 and 1")
    explanation: str = Field(..., description="Explanation of the mapping logic")

class SqlQueryResult(BaseModel):
    """Result of converting natural language to SQL."""
    sql_query: str = Field(..., description="The generated SQL query")
    explanation: str = Field(..., description="Explanation of the query logic")


# ==========================================
# ENRICHED DATA LAYER MODELS
# ==========================================

class EnrichedHdbBlocks(BaseModel):
    """Pydantic model for enriched_hdb_blocks"""
    id: Optional[int] = None
    rawPropertyId: Optional[int] = Field(None, alias='raw_property_id')
    block: str
    street: str
    town: str
    postalCode: Optional[str] = Field(None, alias='postal_code')
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    yearCompleted: Optional[int] = Field(None, alias='year_completed')
    totalUnits: Optional[int] = Field(None, alias='total_units')
    hasCommercial: Optional[bool] = Field(None, alias='has_commercial')

class EnrichedBlockAmenities(BaseModel):
    """Pydantic model for enriched_block_amenities"""
    id: Optional[int] = None
    blockId: Optional[int] = Field(None, alias='block_id')
    amenityType: str = Field(..., alias='amenity_type')
    amenityName: str = Field(..., alias='amenity_name')
    distanceMeters: float = Field(..., alias='distance_meters')
    isSheltered: Optional[bool] = Field(None, alias='is_sheltered')

class AnalyticsBlockMetrics(BaseModel):
    """Pydantic model for analytics_block_metrics"""
    id: Optional[int] = None
    blockId: Optional[int] = Field(None, alias='block_id')
    lastUpdated: Optional[str] = Field(None, alias='last_updated')
    medianResalePrice: Optional[float] = Field(None, alias='median_resale_price')
    medianRent: Optional[float] = Field(None, alias='median_rent')
    impliedRentalYield: Optional[float] = Field(None, alias='implied_rental_yield')
    pricePerSqm: Optional[float] = Field(None, alias='price_per_sqm')
    salesVolumeLastYear: Optional[int] = Field(None, alias='sales_volume_last_year')
    walkabilityScore: Optional[float] = Field(None, alias='walkability_score')
    foodAccessScore: Optional[float] = Field(None, alias='food_access_score')

class AnalyticsNeighborhoodScores(BaseModel):
    """Pydantic model for analytics_neighborhood_scores"""
    id: Optional[int] = None
    town: str
    walkabilityScore: Optional[float] = Field(None, alias='walkability_score')
    foodAccessibilityScore: Optional[float] = Field(None, alias='food_accessibility_score')
    transportScore: Optional[float] = Field(None, alias='transport_score')

class AiPropertyListings(BaseModel):
    """Pydantic model for ai_property_listings"""
    id: Optional[int] = None
    blockId: int = Field(..., alias='block_id')
    listingNarrative: Optional[str] = Field(None, alias='listing_narrative')
    overallReasoning: Optional[str] = Field(None, alias='overall_reasoning')
    proList: Optional[str] = Field(None, alias='pro_list')
    conList: Optional[str] = Field(None, alias='con_list')
    modelName: Optional[str] = Field(None, alias='model_name')
    promptUsed: Optional[str] = Field(None, alias='prompt_used')
    generatedAt: str = Field(..., alias='generated_at')

class HdbValuationData(BaseModel):
    """Pydantic model for hdb_valuation_data"""
    id: Optional[int] = None
    blockId: int = Field(..., alias='block_id')
    flatType: str = Field(..., alias='flat_type')
    estMinValBuy: Optional[float] = Field(None, alias='est_min_val_buy')
    estAvgValBuy: Optional[float] = Field(None, alias='est_avg_val_buy')
    estMaxValBuy: Optional[float] = Field(None, alias='est_max_val_buy')
    estMinValRent: Optional[float] = Field(None, alias='est_min_val_rent')
    estAvgValRent: Optional[float] = Field(None, alias='est_avg_val_rent')
    estMaxValRent: Optional[float] = Field(None, alias='est_max_val_rent')
    totalUnits: Optional[int] = Field(None, alias='total_units')
    latestPurchaseDate: Optional[str] = Field(None, alias='latest_purchase_date')
    avgAnnualPurchases: Optional[float] = Field(None, alias='avg_annual_purchases')
    impliedRentalYield: Optional[float] = Field(None, alias='implied_rental_yield')
    salesVolumeLastYear: Optional[int] = Field(None, alias='sales_volume_last_year')
    lastEnrichedAt: Optional[str] = Field(None, alias='last_enriched_at')

class HdbScoreLah(BaseModel):
    """Pydantic model for hdb_score_lah"""
    id: Optional[int] = None
    blockId: int = Field(..., alias='block_id')
    scoreLah: Optional[int] = Field(None, alias='score_lah')
    scoreLahRationale: Optional[str] = Field(None, alias='score_lah_rationale')
    walkability: Optional[int] = Field(None, alias='walkability')
    walkabilityRationale: Optional[str] = Field(None, alias='walkability_rationale')
    foodAccess: Optional[int] = Field(None, alias='food_access')
    foodAccessRationale: Optional[str] = Field(None, alias='food_access_rationale')
    hawker: Optional[int] = Field(None, alias='hawker')
    hawkerRationale: Optional[str] = Field(None, alias='hawker_rationale')
    mrt: Optional[int] = Field(None, alias='mrt')
    mrtRationale: Optional[str] = Field(None, alias='mrt_rationale')
    bus: Optional[int] = Field(None, alias='bus')
    busRationale: Optional[str] = Field(None, alias='bus_rationale')
    education: Optional[int] = Field(None, alias='education')
    educationRationale: Optional[str] = Field(None, alias='education_rationale')
    parks: Optional[int] = Field(None, alias='parks')
    parksRationale: Optional[str] = Field(None, alias='parks_rationale')
    noiseLevel: Optional[int] = Field(None, alias='noise_level')
    noiseLevelRationale: Optional[str] = Field(None, alias='noise_level_rationale')
    trafficLevel: Optional[int] = Field(None, alias='traffic_level')
    trafficLevelRationale: Optional[str] = Field(None, alias='traffic_level_rationale')

class HdbFrontendData(BaseModel):
    """Pydantic model for hdb_frontend_data"""
    id: Optional[int] = None
    blockId: int = Field(..., alias='block_id')
    portalLinks: Optional[str] = Field(None, alias='portal_links')
    googleStreetViewUrl: Optional[str] = Field(None, alias='google_street_view_url')
    lastEnrichedAt: Optional[str] = Field(None, alias='last_enriched_at')

class UserPortfolio(BaseModel):
    """Pydantic model for user_portfolio"""
    id: Optional[int] = None
    userId: str = Field(..., alias='user_id')
    blockId: int = Field(..., alias='block_id')
    flatType: Optional[str] = Field(None, alias='flat_type')
    unitNumber: Optional[str] = Field(None, alias='unit_number')
    ownershipStatus: str = Field(..., alias='ownership_status')
    acquisitionDate: Optional[str] = Field(None, alias='acquisition_date')
    acquisitionPrice: Optional[float] = Field(None, alias='acquisition_price')
    currentRent: Optional[float] = Field(None, alias='current_rent')
    createdAt: str = Field(..., alias='created_at')

class PortfolioAnalysis(BaseModel):
    """Pydantic model for portfolio_analysis"""
    id: Optional[int] = None
    portfolioId: int = Field(..., alias='portfolio_id')
    generatedAt: str = Field(..., alias='generated_at')
    rentGap: Optional[float] = Field(None, alias='rent_gap')
    rentAdvice: Optional[str] = Field(None, alias='rent_advice')
    marketValueGap: Optional[float] = Field(None, alias='market_value_gap')
    resaleOutlook: Optional[str] = Field(None, alias='resale_outlook')
    scoreLahImpact: Optional[str] = Field(None, alias='score_lah_impact')
    aiActionItems: Optional[str] = Field(None, alias='ai_action_items')




# ==========================================
# POLICY RAG MODELS
# ==========================================

class PolicyPage(BaseModel):
    """Pydantic model for policy_pages"""
    id: Optional[int] = None
    url: str
    slug: str
    canonicalUrl: Optional[str] = Field(None, alias='canonical_url')
    policyIdentifier: Optional[str] = Field(None, alias='policy_identifier')
    source: str
    isActive: bool = Field(True, alias='is_active')
    createdAt: str = Field(..., alias='created_at')
    updatedAt: str = Field(..., alias='updated_at')

class PolicyVersion(BaseModel):
    """Pydantic model for policy_versions"""
    id: Optional[int] = None
    policyPageId: int = Field(..., alias='policy_page_id')
    versionNumber: int = Field(..., alias='version_number')
    contentMarkdown: str = Field(..., alias='content_markdown')
    contentHash: str = Field(..., alias='content_hash')
    scrapedAt: str = Field(..., alias='scraped_at')
    effectiveDate: Optional[str] = Field(None, alias='effective_date')
    superseded: bool = Field(False)
    aiKeywordsJson: Optional[str] = Field(None, alias='ai_keywords_json')
    aiMetadataJson: Optional[str] = Field(None, alias='ai_metadata_json')

class PolicyEmbedding(BaseModel):
    """Pydantic model for policy_embeddings"""
    id: Optional[int] = None
    policyVersionId: int = Field(..., alias='policy_version_id')
    vectorId: str = Field(..., alias='vector_id')
    chunkIndex: int = Field(..., alias='chunk_index')
    textChunk: str = Field(..., alias='text_chunk')
    createdAt: str = Field(..., alias='created_at')

class UserProfile(BaseModel):
    """Pydantic model for user_profiles"""
    id: Optional[int] = None
    externalUserId: str = Field(..., alias='external_user_id')
    birthYear: int = Field(..., alias='birth_year')
    citizenshipCountry: str = Field(..., alias='citizenship_country')
    primaryResidenceCountry: str = Field(..., alias='primary_residence_country')
    intendsRetireInSingapore: bool = Field(..., alias='intends_retire_in_singapore')
    lastUpdatedAt: str = Field(..., alias='last_updated_at')
    rawProfileJson: Optional[str] = Field(None, alias='raw_profile_json')

class PolicyUserImpact(BaseModel):
    """Pydantic model for policy_user_impacts"""
    id: Optional[int] = None
    userProfileId: int = Field(..., alias='user_profile_id')
    policyVersionId: int = Field(..., alias='policy_version_id')
    analysisModel: str = Field(..., alias='analysis_model')
    warningsJson: str = Field(..., alias='warnings_json')
    benefitsJson: str = Field(..., alias='benefits_json')
    summaryJson: str = Field(..., alias='summary_json')
    createdAt: str = Field(..., alias='created_at')
    lastRefreshedAt: str = Field(..., alias='last_refreshed_at')

class UserPolicyConsideration(BaseModel):
    """Pydantic model for user_policy_considerations"""
    id: Optional[int] = None
    userProfileId: int = Field(..., alias='user_profile_id')
    notes: Optional[str] = None
    createdAt: str = Field(..., alias='created_at')
    updatedAt: str = Field(..., alias='updated_at')

class BlockPolicyImpact(BaseModel):
    """Pydantic model for block_policy_impact"""
    id: Optional[int] = None
    blockId: int = Field(..., alias='block_id')
    policyVersionId: Optional[int] = Field(None, alias='policy_version_id')
    impactType: str = Field(..., alias='impact_type')
    impactSummary: str = Field(..., alias='impact_summary')
    confidenceScore: Optional[float] = Field(None, alias='confidence_score')
    generatedAt: str = Field(..., alias='generated_at')

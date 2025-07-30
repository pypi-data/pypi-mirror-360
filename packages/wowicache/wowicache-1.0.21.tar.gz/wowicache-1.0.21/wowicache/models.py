from sqlalchemy import Column, String, Integer, ForeignKey, Date, Float, Boolean, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class WowiCache:
    def __init__(self, connection_string: str):
        engine = create_engine(connection_string, echo=False, pool_pre_ping=True)
        Session = sessionmaker(bind=engine)
        self.session = Session()


class District(Base):
    __tablename__ = "wowi_districts"
    internal_id = Column("internal_id", Integer, primary_key=True)
    name = Column("name", String(50))

    economic_units = relationship('EconomicUnit', back_populates='district')
    buildings = relationship('Building', back_populates='district')

    def __init__(self, internal_id, name):
        self.internal_id = internal_id
        self.name = name

    def __repr__(self):
        return f"District {self.name} ({self.internal_id})"


class EconomicUnit(Base):
    __tablename__ = "wowi_economic_units"
    internal_id = Column("internal_id", Integer, primary_key=True)
    id_num = Column("id_num", String(50))
    company_id = Column("company_id", Integer)
    name = Column("name", String(100))
    location = Column("location", String(100))
    construction_year = Column("construction_year", Integer, nullable=True)
    info = Column("info", String(255), nullable=True)
    owner_id = Column("owner_id", Integer)
    district_id = Column(Integer, ForeignKey("wowi_districts.internal_id"), nullable=True)
    district = relationship('District', back_populates='economic_units')
    buildings = relationship('Building', back_populates='economic_unit')
    use_units = relationship('UseUnit', back_populates='economic_unit')

    def __init__(self, internal_id, id_num, company_id, name, location, construction_year,
                 info, owner_id, district_id):
        self.internal_id = internal_id
        self.id_num = id_num
        self.company_id = company_id
        self.name = name
        self.location = location
        self.construction_year = construction_year
        self.info = info
        self.owner_id = owner_id
        self.district_id = district_id

    def __repr__(self):
        return f"Economic Unit Id: {self.internal_id} IdNum: {self.id_num} Name: {self.name}"


class Building(Base):
    __tablename__ = "wowi_buildings"
    internal_id = Column("internal_id", Integer, primary_key=True)
    id_num = Column("id_num", String(50))
    company_id = Column("company_id", Integer)
    building_land_type = Column("building_land_type", String(50))
    entry_date = Column("entry_date", Date)
    economic_unit_id = Column(Integer, ForeignKey("wowi_economic_units.internal_id"))
    economic_unit = relationship('EconomicUnit', back_populates='buildings')
    postcode = Column("postcode", String(30))
    town = Column("town", String(50))
    street = Column("street", String(70))
    house_number = Column("house_number", String(30))
    house_number_addition = Column("house_number_addition", String(30), nullable=True)
    country_id = Column("country_id", Integer)
    country = Column("country", String(50))
    street_complete = Column("street_complete", String(80))
    house_number_complete = Column("house_number_complete", String(50))

    construction_year = Column("construction_year", Integer, nullable=True)
    move_in_date = Column("move_in_date", Date, nullable=True)

    building_type_id = Column("building_type_id", Integer)
    building_type_name = Column("building_type_name", String(60))

    district_id = Column(Integer, ForeignKey("wowi_districts.internal_id"), nullable=True)
    district = relationship('District', back_populates='buildings')

    use_units = relationship('UseUnit', back_populates='building')

    def __init__(self, internal_id, id_num, company_id, building_land_type, entry_date, economic_unit_id,
                 postcode, town, street, house_number, house_number_addition, country_id, country,
                 street_complete, house_number_complete, construction_year, move_in_date,
                 building_type_id, building_type_name, district_id):
        self.internal_id = internal_id
        self.id_num = id_num
        self.company_id = company_id
        self.building_land_type = building_land_type
        self.entry_date = entry_date
        self.economic_unit_id = economic_unit_id
        self.postcode = postcode
        self.town = town
        self.street = street
        self.house_number = house_number
        self.house_number_addition = house_number_addition
        self.country_id = country_id
        self.country = country
        self.street_complete = street_complete
        self.house_number_complete = house_number_complete
        self.construction_year = construction_year
        self.move_in_date = move_in_date
        self.building_type_id = building_type_id
        self.building_type_name = building_type_name
        self.district_id = district_id

    def __repr__(self):
        return f"Building {self.id_num}, {self.street_complete}, {self.postcode} {self.town}"


class UseUnit(Base):
    __tablename__ = "wowi_use_units"
    internal_id = Column("internal_id", Integer, primary_key=True)
    id_num = Column("id_num", String(50))
    company_id = Column("company_id", Integer)
    building_id = Column(Integer, ForeignKey("wowi_buildings.internal_id"))
    building = relationship('Building', back_populates='use_units')
    economic_unit_id = Column(Integer, ForeignKey("wowi_economic_units.internal_id"))
    economic_unit = relationship('EconomicUnit', back_populates='use_units')
    postcode = Column("postcode", String(30))
    town = Column("town", String(50))
    street = Column("street", String(100))
    house_number = Column("house_number", String(30))
    house_number_addition = Column("house_number_addition", String(30), nullable=True)
    country_id = Column("country_id", Integer)
    country = Column("country", String(50))
    street_complete = Column("street_complete", String(100))
    house_number_complete = Column("house_number_complete", String(30))
    financing_type_id = Column("financing_type_id", Integer)
    financing_type = Column("financing_type", String(50))
    use_unit_usage_type_id = Column("use_unit_usage_type_id", Integer)
    use_unit_usage_type = Column("use_unit_usage_type", String(50))
    usable_space = Column("usable_space", Float, nullable=True)
    living_space = Column("living_space", Float, nullable=True)
    heating_space = Column("heating_space", Float, nullable=True)
    number_of_rooms = Column("number_of_rooms", Integer, nullable=True)
    number_of_half_rooms = Column("number_of_half_rooms", Integer, nullable=True)
    description_of_position = Column("position_description", String(100), nullable=True)
    management_start = Column("management_start", Date, nullable=True)
    management_end = Column("management_end", Date, nullable=True)
    move_in_date = Column("move_in_date", Date, nullable=True)
    exit_date = Column("exit_date", Date, nullable=True)
    entry_date = Column("entry_date", Date, nullable=True)
    position_id = Column("position_id", Integer, nullable=True)
    position = Column("position", String(100), nullable=True)
    floor_id = Column("floor_id", Integer, nullable=True)
    floor_name = Column("floor_name", String(100), nullable=True)
    floor_level = Column("floor_level", Float, nullable=True)
    contracts = relationship('Contract', back_populates='use_unit')
    contractors = relationship('Contractor', back_populates='use_unit')

    def __init__(self, internal_id, id_num, company_id, building_id, economic_unit_id,
                 postcode, town, street, house_number, house_number_addition, country_id, country,
                 street_complete, house_number_complete, financing_type_id, financing_type,
                 use_unit_usage_type_id, use_unit_usage_type, usable_space, living_space, heating_space,
                 number_of_rooms, number_of_half_rooms, description_of_position, management_start,
                 management_end, move_in_date, exit_date, entry_date, position_id, position, floor_id,
                 floor_name, floor_level):
        self.internal_id = internal_id
        self.id_num = id_num
        self.company_id = company_id
        self.building_id = building_id
        self.economic_unit_id = economic_unit_id
        self.postcode = postcode
        self.town = town
        self.street = street
        self.house_number = house_number
        self.house_number_addition = house_number_addition
        self.country_id = country_id
        self.country = country
        self.street_complete = street_complete
        self.house_number_complete = house_number_complete
        self.financing_type_id = financing_type_id
        self.financing_type = financing_type
        self.use_unit_usage_type_id = use_unit_usage_type_id
        self.use_unit_usage_type = use_unit_usage_type
        self.usable_space = usable_space
        self.living_space = living_space
        self.heating_space = heating_space
        self.number_of_rooms = number_of_rooms
        self.number_of_half_rooms = number_of_half_rooms
        self.description_of_position = description_of_position
        self.management_start = management_start
        self.management_end = management_end
        self.move_in_date = move_in_date
        self.exit_date = exit_date
        self.entry_date = entry_date
        self.position_id = position_id
        self.position = position
        self.floor_id = floor_id
        self.floor_name = floor_name
        self.floor_level = floor_level

    def __repr__(self):
        return f"Use Unit {self.id_num}"


class Address(Base):
    __tablename__ = "wowi_addresses"
    internal_id = Column("internal_id", Integer, primary_key=True)
    postcode = Column("postcode", String(30))
    town = Column("town", String(50))
    street = Column("street", String(100), nullable=True)
    house_number = Column("house_number", String(30), nullable=True)
    house_number_addition = Column("house_number_addition", String(30), nullable=True)
    country_id = Column("country_id", Integer, nullable=True)
    country = Column("country", String(50), nullable=True)
    street_complete = Column("street_complete", String(100))
    house_number_complete = Column("house_number_complete", String(60))
    address_type_id = Column("address_type_id", Integer, nullable=True)
    address_type = Column("address_type", String(50), nullable=True)
    valid_from = Column("valid_from", Date)
    valid_to = Column("valid_to", Date, nullable=True)

    communications = relationship('Communication', back_populates='related_address')
    person_id = Column(Integer, ForeignKey("wowi_persons.internal_id"))
    person = relationship('Person', back_populates='addresses')

    def __init__(self, internal_id, postcode, town, street, house_number, house_number_addition, country_id, country,
                 street_complete, house_number_complete, address_type_id, address_type, valid_from, valid_to,
                 person_id):
        self.internal_id = internal_id
        self.postcode = postcode
        self.town = town
        self.street = street
        self.house_number = house_number
        self.house_number_addition = house_number_addition
        self.country_id = country_id
        self.country = country
        self.street_complete = street_complete
        self.house_number_complete = house_number_complete
        self.address_type_id = address_type_id
        self.address_type = address_type
        self.valid_from = valid_from
        self.valid_to = valid_to
        self.person_id = person_id

    def __repr__(self):
        return f"Address {self.street_complete}, {self.postcode} {self.town}"


class Communication(Base):
    __tablename__ = "wowi_communications"
    internal_id = Column("internal_id", Integer, primary_key=True)
    related_address_id = Column(Integer, ForeignKey("wowi_addresses.internal_id"), nullable=True)
    related_address = relationship('Address', back_populates='communications')
    content = Column("content", String(100))
    explanation = Column("explanation", String(100), nullable=True)
    communication_type_id = Column("communication_type_id", Integer)
    communication_type = Column("communication_type", String(50))
    person_id = Column(Integer, ForeignKey("wowi_persons.internal_id"))
    person = relationship('Person', back_populates='communications')

    def __init__(self, internal_id, related_address_id, content, explanation, communication_type_id,
                 communication_type, person_id):
        self.internal_id = internal_id
        self.related_address_id = related_address_id
        self.content = content
        self.explanation = explanation
        self.communication_type_id = communication_type_id
        self.communication_type = communication_type
        self.person_id = person_id

    def __repr__(self):
        return f"Communication Id {self.internal_id}: {self.content}"


class Person(Base):
    __tablename__ = "wowi_persons"
    internal_id = Column("internal_id", Integer, primary_key=True)
    id_num = Column("id_num", String(50))
    name = Column("name", String(60))
    short_name = Column("short_name", String(100))
    valid_from = Column("valid_from", Date)
    valid_to = Column("valid_to", Date, nullable=True)
    long_name_1 = Column("long_name_1", String(100), nullable=True)
    long_name_2 = Column("long_name_2", String(100), nullable=True)
    vat_id = Column("vat_id", String(30), nullable=True)
    commercial_register_number = Column("commercial_register_number", String(50), nullable=True)
    commercial_register_town = Column("commercial_register_town", String(30), nullable=True)
    first_name = Column("first_name", String(60), nullable=True)
    last_name = Column("last_name", String(60), nullable=True)
    birth_date = Column("birth_date", Date, nullable=True)
    death_date = Column("death_date", Date, nullable=True)
    title = Column("title", String(100), nullable=True)
    gender_id = Column("gender_id", Integer, nullable=True)
    gender_name = Column("gender_name", String(30), nullable=True)
    is_natural_person = Column("is_natural_person", Boolean)

    addresses = relationship('Address', back_populates='person')
    communications = relationship('Communication', back_populates='person')
    contractors = relationship('Contractor', back_populates='person')

    def __init__(self, internal_id, id_num, name, short_name, valid_from, valid_to, long_name_1, long_name_2,
                 vat_id, commercial_register_number, commercial_register_town, first_name, last_name, birth_date,
                 gender_id, gender_name, death_date, title):
        self.internal_id = internal_id
        self.id_num = id_num
        self.name = name
        self.short_name = short_name
        self.valid_from = valid_from
        self.valid_to = valid_to
        self.long_name_1 = long_name_1
        self.long_name_2 = long_name_2
        self.vat_id = vat_id
        self.commercial_register_number = commercial_register_number
        self.commercial_register_town = commercial_register_town
        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.gender_id = gender_id
        self.gender_name = gender_name
        self.death_date = death_date
        self.title = title

        if self.first_name is None and self.last_name is None:
            self.is_natural_person = False
        else:
            self.is_natural_person = True

    def __repr__(self):
        return f"Person IdNum {self.id_num} - {self.short_name}"


class Contract(Base):
    __tablename__ = "wowi_contracts"
    internal_id = Column("internal_id", Integer, primary_key=True)
    id_num = Column("id_num", String(30))
    use_unit_id = Column(Integer, ForeignKey("wowi_use_units.internal_id"))
    use_unit = relationship('UseUnit', back_populates='contracts')
    restriction_id = Column("restriction_id", Integer)
    restriction_name = Column("restriction_name", String(40))
    is_vacancy = Column("is_vacancy", Boolean)
    status_id = Column("status_id", Integer)
    status_name = Column("status_name", String(30))
    life_id = Column("life_id", Integer)
    life_name = Column("life_name", String(50))
    contract_start = Column("contract_start", Date)
    contract_end = Column("contract_end", Date, nullable=True)
    contractors = relationship('Contractor', back_populates='contract')
    payment_modes = relationship('PaymentMode', back_populates='contract')

    def __init__(self, internal_id, id_num, use_unit_id, restriction_id, restriction_name, is_vacancy,
                 status_id, status_name, life_id, life_name, contract_start, contract_end):
        self.internal_id = internal_id
        self.id_num = id_num
        self.use_unit_id = use_unit_id
        self.restriction_id = restriction_id
        self.restriction_name = restriction_name
        self.is_vacancy = is_vacancy
        self.status_id = status_id
        self.status_name = status_name
        self.life_id = life_id
        self.life_name = life_name
        self.contract_start = contract_start
        self.contract_end = contract_end

    def __repr__(self):
        return f"Contract IdNum {self.id_num} Id {self.internal_id}"


class Contractor(Base):
    __tablename__ = "wowi_contractors"
    internal_id = Column("internal_id", Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey("wowi_contracts.internal_id"), primary_key=True)
    type_id = Column("type_id", Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("wowi_persons.internal_id"))
    contract = relationship('Contract', back_populates='contractors')
    use_unit_id = Column(Integer, ForeignKey("wowi_use_units.internal_id"))
    use_unit = relationship('UseUnit', back_populates='contractors')
    person = relationship('Person', back_populates='contractors')

    type_name = Column("type_name", String(50))
    valid_from = Column("valid_from", Date)
    valid_to = Column("valid_to", Date, nullable=True)

    def __init__(self, internal_id, contract_id, use_unit_id, person_id, type_id,
                 type_name, valid_from, valid_to):
        self.internal_id = internal_id
        self.contract_id = contract_id
        self.use_unit_id = use_unit_id
        self.person_id = person_id
        self.type_id = type_id
        self.type_name = type_name
        self.valid_from = valid_from
        self.valid_to = valid_to

    def __repr__(self):
        return f"Contractor {self.internal_id}"


class Membership(Base):
    __tablename__ = "wowi_memberships"
    internal_id = Column("internal_id", Integer, primary_key=True)
    id_num = Column("id_num", String(30))
    creation_date = Column("creation_date", Date)
    valid_from = Column("valid_from", Date)
    valid_to = Column("valid_to", Date, nullable=True)
    is_payout_block_account = Column("is_payout_block_account", Boolean)
    cooperative_account_clearing_lock = Column("cooperative_account_clearing_lock", Boolean)
    subsidy_application_for_several_fiscal_years_allowed = Column(
        "subsidy_application_for_several_fiscal_years_allowed", Boolean)
    no_participation_electoral_district = Column("no_participation_electoral_district", Boolean)
    active_amount_sum = Column("active_amount_sum", Numeric)
    active_count_sum = Column("active_count_sum", Numeric)
    membership_status_id = Column("membership_status_id", Integer)
    membership_status_code = Column("membership_status_code", String(30))
    electoral_district_id = Column("electoral_district_id", Integer, nullable=True)
    electoral_district_code = Column("electoral_district_code", String(30), nullable=True)
    membership_end_reason_id = Column("membership_end_reason_id", Integer, nullable=True)
    membership_end_reason_code = Column("membership_end_reason_code", String(30), nullable=True)
    description = Column("description", String(30), nullable=True)
    active_main_member_person_id = Column("active_main_member_person_id", Integer, nullable=True)
    active_main_member_person_id_num = Column("active_main_member_person_id_num", String(30), nullable=True)

    def __init__(self, **kwargs):
        self.internal_id = kwargs.get("id")
        self.id_num = kwargs.get("id_num")
        t_creation_date = kwargs.get("creation_date")
        if isinstance(t_creation_date, str):
            t_creation_date = datetime.strptime(t_creation_date, "%Y-%m-%d")
        self.creation_date = t_creation_date

        t_valid_from = kwargs.get("valid_from")
        if isinstance(t_valid_from, str):
            t_valid_from = datetime.strptime(t_valid_from, "%Y-%m-%d")
        self.valid_from = t_valid_from

        t_valid_to = kwargs.get("valid_to")
        if isinstance(t_valid_to, str):
            t_valid_to = datetime.strptime(t_valid_to, "%Y-%m-%d")
        self.valid_to = t_valid_to

        self.is_payout_block_account = kwargs.get("is_payout_block_account")
        self.cooperative_account_clearing_lock = kwargs.get("cooperative_account_clearing_lock")
        self.subsidy_application_for_several_fiscal_years_allowed = kwargs.get(
            "subsidy_application_for_several_fiscal_years_allowed")
        self.no_participation_electoral_district = kwargs.get("no_participation_electoral_district")
        self.active_amount_sum = kwargs.get("active_amount_sum")
        self.active_count_sum = kwargs.get("active_count_sum")
        self.membership_status_id = kwargs.get("membership_status_id")
        self.membership_status_code = kwargs.get("membership_status_code")
        self.electoral_district_id = kwargs.get("electoral_district_id")
        self.electoral_district_code = kwargs.get("electoral_district_code")
        self.membership_end_reason_id = kwargs.get("membership_end_reason_id")
        self.membership_end_reason_code = kwargs.get("membership_end_reason_code")
        self.description = kwargs.get("description")
        self.active_main_member_person_id = kwargs.get("active_main_member_person_id")
        self.active_main_member_person_id_num = kwargs.get("active_main_member_person_id_num")

    def __repr__(self):
        return f"Membership {self.id_num}"


class PaymentMode(Base):
    __tablename__ = "wowi_payment_modes"
    internal_id = Column("internal_id", Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey("wowi_contracts.internal_id"), primary_key=True)
    contract = relationship('Contract', back_populates='payment_modes')
    active_from = Column("active_from", Date)
    active_to = Column("active_to", Date, nullable=True)
    mode_id = Column("mode_id", Integer)
    mode_name = Column("mode_name", String(100))
    type_id = Column("type_id", Integer)
    type_name = Column("type_name", String(100))
    sepa_id = Column("sepa_id", Integer)
    sepa_mandate_id = Column("sepa_mandate_id", String(100))
    sepa_iban = Column("sepa_iban", String(100))
    bank_account_id = Column("bank_account_id", Integer)
    bank_account_bic = Column("bank_account_bic", String(100))
    bank_account_iban = Column("bank_account_iban", String(100))

    def __init__(self, **kwargs):
        self.internal_id = kwargs.get("internal_id")
        self.contract_id = kwargs.get("contract_id")

        t_active_from = kwargs.get("active_from")
        if isinstance(t_active_from, str):
            t_active_from = datetime.strptime(t_active_from, "%Y-%m-%d")
        self.active_from = t_active_from

        t_active_to = kwargs.get("active_to")
        if isinstance(t_active_to, str):
            t_active_to = datetime.strptime(t_active_to, "%Y-%m-%d")
        self.active_to = t_active_to

        self.mode_id = kwargs.get("mode_id")
        self.mode_name = kwargs.get("mode_name")
        self.type_id = kwargs.get("type_id")
        self.type_name = kwargs.get("type_name")

        self.sepa_id = kwargs.get("sepa_id")
        self.sepa_mandate_id = kwargs.get("sepa_mandate_id")
        self.sepa_iban = kwargs.get("sepa_iban")

        self.bank_account_id = kwargs.get("bank_account_id")
        self.bank_account_bic = kwargs.get("bank_account_bic")
        self.bank_account_iban = kwargs.get("bank_account_iban")



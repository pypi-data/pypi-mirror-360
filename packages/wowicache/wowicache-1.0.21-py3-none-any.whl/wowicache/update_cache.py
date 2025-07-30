import sys
import os
from dotenv import dotenv_values
from wowipy.wowipy import WowiPy
from wowicache import log
import sqlalchemy.exc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from wowicache.models import Base, EconomicUnit, District, Building, UseUnit, Address, Communication, Person, Contract
from wowicache.models import Contractor, Membership, PaymentMode
from wowicache.rescue import backup_database, restore_last_backup
from datetime import datetime

ENBUILDINGS = 1
ENCONTRACTORS = 2
ENPERSONS = 3
ENECONOMICUNITS = 4
ENCONTRACTS = 5
ENUSEUNITS = 6
ENMEMBERSHIPS = 7
ENPAYMENTMODES = 8


def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
    backup_path = settings.get("backup_path")
    connection_string = settings.get("db_connection_string")
    restore_result = restore_last_backup(backup_path, connection_string)
    logger.error(f"Restore backup result: {restore_result}")


if len(sys.argv) > 1:
    settings_path = sys.argv[1]
else:
    settings_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), ".env")
settings = dotenv_values(settings_path)
logger = log.setup_custom_logger('root', settings.get("log_method", "file"),
                                 settings.get("log_level", "info"),
                                 graylog_host=settings.get("graylog_server"),
                                 graylog_port=int(settings.get("graylog_port", 0)),
                                 log_dir=settings.get("log_file_path"))
sys.excepthook = handle_unhandled_exception


def cache_to_db():
    logger.info("cache_to_db started.")
    connection_string = settings.get("db_connection_string")
    rescue_path = settings.get("backup_path")
    if rescue_path:
        backup_database(connection_string, rescue_path)

    wowi_host = settings.get("wowi_host")
    wowi_user = settings.get("wowi_user")
    wowi_pass = settings.get("wowi_pass")
    wowi_key = settings.get("wowi_key")

    str_en_buildings = settings.get("enable_buildings")
    str_en_contractors = settings.get("enable_contractors")
    str_en_persons = settings.get("enable_persons")
    str_en_economic_units = settings.get("enable_economic_units")
    str_en_license_agreements = settings.get("enable_license_agreements")
    str_en_use_units = settings.get("enable_use_units")
    str_en_memberships = settings.get("enable_memberships")
    str_en_payment_modes = settings.get("enable_payment_modes")

    user_agent = settings.get("user_agent")
    if user_agent is None or len(user_agent.strip()) == 0:
        user_agent = "WowiCache/1.0"

    entities = []
    if str_en_buildings is not None and str_en_buildings.lower() == "true":
        entities.append(ENBUILDINGS)
    if str_en_contractors is not None and str_en_contractors.lower() == "true":
        entities.append(ENCONTRACTORS)
    if str_en_persons is not None and str_en_persons.lower() == "true":
        entities.append(ENPERSONS)
    if str_en_economic_units is not None and str_en_economic_units.lower() == "true":
        entities.append(ENECONOMICUNITS)
    if str_en_license_agreements is not None and str_en_license_agreements.lower() == "true":
        entities.append(ENCONTRACTS)
    if str_en_use_units is not None and str_en_use_units.lower() == "true":
        entities.append(ENUSEUNITS)
    if str_en_memberships is not None and str_en_memberships.lower() == "true":
        entities.append(ENMEMBERSHIPS)
    if str_en_payment_modes is not None and str_en_payment_modes.lower() == "true":
        entities.append(ENPAYMENTMODES)

    logger.info(f"Entities activated: {entities}")

    wowicon = WowiPy(hostname=wowi_host, user=wowi_user,
                     password=wowi_pass, api_key=wowi_key,
                     user_agent=user_agent)

    engine = create_engine(connection_string, echo=False, pool_pre_ping=True)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    session.query(Contractor).delete()
    session.query(Contract).delete()
    session.query(Communication).delete()
    session.query(Address).delete()
    session.query(Person).delete()
    session.query(UseUnit).delete()
    session.query(Building).delete()
    session.query(EconomicUnit).delete()
    session.query(District).delete()
    session.query(Membership).delete()
    session.query(PaymentMode).delete()
    session.commit()

    if ENECONOMICUNITS in entities or ENBUILDINGS in entities:
        sectioncount = 0
        districts = wowicon.get_districts()
        for entry in districts:
            new_entry = District(internal_id=entry.id_,
                                 name=entry.name)
            session.add(new_entry)
            sectioncount += 1
        session.commit()
        logger.info(f"Added {sectioncount} districts.")

    if ENECONOMICUNITS in entities:
        sectioncount = 0
        economic_units = wowicon.get_economic_units(fetch_all=True)
        for entry in economic_units:
            district_id = entry.district.id_ if entry.district else None
            new_entry = EconomicUnit(internal_id=entry.id_,
                                     id_num=entry.id_num,
                                     company_id=entry.company_code.id_,
                                     name=entry.name,
                                     location=entry.location,
                                     construction_year=entry.construction_year,
                                     info=entry.info,
                                     owner_id=entry.owner.id_,
                                     district_id=district_id)
            session.add(new_entry)
            sectioncount += 1
        session.commit()
        logger.info(f"Added {sectioncount} economic units.")

    if ENBUILDINGS in entities:
        sectioncount = 0
        buildings = wowicon.get_building_lands(fetch_all=True)
        for entry in buildings:
            district_id = entry.building.district.id_ if entry.building.district else None
            move_in_date = datetime.strptime(str(entry.building.move_in_date), "%Y-%m-%d") \
                if entry.building.move_in_date else None
            entry_date = datetime.strptime(str(entry.entry_date), "%Y-%m-%d") \
                if entry.entry_date else None
            new_entry = Building(internal_id=entry.id_,
                                 id_num=entry.id_num,
                                 company_id=entry.company_code.id_,
                                 building_land_type=entry.building_land_type,
                                 entry_date=entry_date,
                                 economic_unit_id=entry.economic_unit.id_,
                                 postcode=entry.estate_address.zip_,
                                 town=entry.estate_address.town,
                                 street=entry.estate_address.street,
                                 house_number=entry.estate_address.house_number,
                                 house_number_addition=entry.estate_address.house_number_addition,
                                 country_id=entry.estate_address.country_id,
                                 country=entry.estate_address.country_code,
                                 street_complete=entry.estate_address.street_complete,
                                 house_number_complete=entry.estate_address.house_number_complete,
                                 construction_year=entry.building.construction_year,
                                 move_in_date=move_in_date,
                                 building_type_id=entry.building.building_type.id_,
                                 building_type_name=entry.building.building_type.name,
                                 district_id=district_id)
            session.add(new_entry)
            sectioncount += 1
        session.commit()
        logger.info(f"Added {sectioncount} buildings.")

    if ENUSEUNITS in entities:
        sectioncount = 0
        use_units = wowicon.get_use_units(fetch_all=True)
        for entry in use_units:
            move_in_date = datetime.strptime(str(entry.move_in_date), "%Y-%m-%d") \
                if entry.move_in_date else None
            entry_date = datetime.strptime(str(entry.entry_date), "%Y-%m-%d") \
                if entry.entry_date else None
            exit_date = datetime.strptime(str(entry.exit_date), "%Y-%m-%d") \
                if entry.exit_date else None
            management_start = datetime.strptime(str(entry.management_start), "%Y-%m-%d") \
                if entry.management_start else None
            management_end = datetime.strptime(str(entry.management_end), "%Y-%m-%d") \
                if entry.management_end else None
            financing_type_id = entry.financing_type.id_ if entry.financing_type else None
            financing_type = entry.financing_type.name if entry.financing_type else None

            position_id = entry.position.id_ if entry.position else None
            position = entry.position.name if entry.position else None

            floor_id = entry.floor.id_ if entry.floor else None
            floor_name = entry.floor.name if entry.floor else None
            floor_level = entry.floor.level_to_ground if entry.floor else None
            new_entry = UseUnit(internal_id=entry.id_,
                                id_num=entry.id_num,
                                company_id=entry.company_code.id_,
                                entry_date=entry_date,
                                building_id=entry.building_land.id_,
                                economic_unit_id=entry.economic_unit.id_,
                                postcode=entry.estate_address.zip_,
                                town=entry.estate_address.town,
                                street=entry.estate_address.street,
                                house_number=entry.estate_address.house_number,
                                house_number_addition=entry.estate_address.house_number_addition,
                                country_id=entry.estate_address.country_id,
                                country=entry.estate_address.country_code,
                                street_complete=entry.estate_address.street_complete,
                                house_number_complete=entry.estate_address.house_number_complete,
                                financing_type_id=financing_type_id,
                                financing_type=financing_type,
                                use_unit_usage_type_id=entry.current_use_unit_type.use_unit_usage_type.id_,
                                use_unit_usage_type=entry.current_use_unit_type.use_unit_usage_type.name,
                                usable_space=entry.usable_space,
                                living_space=entry.living_space,
                                heating_space=entry.heating_space,
                                number_of_rooms=entry.number_of_rooms,
                                number_of_half_rooms=entry.number_of_half_rooms,
                                description_of_position=entry.description_of_position,
                                management_start=management_start,
                                management_end=management_end,
                                move_in_date=move_in_date,
                                exit_date=exit_date,
                                position_id=position_id,
                                position=position,
                                floor_id=floor_id,
                                floor_name=floor_name,
                                floor_level=floor_level)
            session.add(new_entry)
            sectioncount += 1
        session.commit()
        logger.info(f"Added {sectioncount} use units.")

    # Für Contractors benötigen wir auch Personen
    if ENCONTRACTORS in entities and ENPERSONS not in entities:
        entities.append(ENPERSONS)

    if ENPERSONS in entities:
        sectioncount = 0
        persons = wowicon.get_persons(fetch_all=True)
        for entry in persons:
            valid_from = datetime.strptime(str(entry.valid_from), "%Y-%m-%d") \
                if entry.valid_from else None
            valid_to = datetime.strptime(str(entry.valid_to), "%Y-%m-%d") \
                if entry.valid_to else None
            birth_date = datetime.strptime(str(entry.natural_person.birth_date), "%Y-%m-%d") \
                if entry.natural_person.birth_date else None
            gender_id = entry.natural_person.gender.id_ if entry.natural_person.gender else None
            gender_name = entry.natural_person.gender.name if entry.natural_person.gender else None
            new_person = Person(internal_id=entry.id_,
                                id_num=entry.id_num,
                                name=entry.name,
                                short_name=entry.shortname,
                                valid_from=valid_from,
                                valid_to=valid_to,
                                long_name_1=entry.legal_person.long_name1,
                                long_name_2=entry.legal_person.long_name2,
                                vat_id=entry.legal_person.vat_id,
                                commercial_register_number=entry.legal_person.commercial_register_number,
                                commercial_register_town=entry.legal_person.commercial_register_town,
                                first_name=entry.natural_person.first_name,
                                last_name=entry.natural_person.last_name,
                                birth_date=birth_date,
                                gender_id=gender_id,
                                gender_name=gender_name,
                                death_date=entry.natural_person.death_date,
                                title=entry.natural_person.title)
            session.add(new_person)
            sectioncount += 1

            if entry.addresses is not None:
                for address_entry in entry.addresses:
                    address_valid_from = datetime.strptime(str(address_entry.valid_from), "%Y-%m-%d") \
                        if address_entry.valid_from else None
                    address_valid_to = datetime.strptime(str(address_entry.valid_to), "%Y-%m-%d") \
                        if address_entry.valid_to else None

                    country_id = address_entry.country.id_ if address_entry.country else None
                    country = address_entry.country.code if address_entry.country else None

                    address_type_id = address_entry.address_type.id_ if address_entry.address_type else None
                    address_type = address_entry.address_type.name if address_entry.address_type else None

                    new_address = Address(internal_id=address_entry.id_,
                                          postcode=address_entry.zip_,
                                          town=address_entry.town,
                                          street=address_entry.street,
                                          house_number=address_entry.house_number,
                                          house_number_addition=address_entry.house_number_addition,
                                          country_id=country_id,
                                          country=country,
                                          street_complete=address_entry.street_complete,
                                          house_number_complete=address_entry.house_number_complete,
                                          address_type_id=address_type_id,
                                          address_type=address_type,
                                          valid_from=address_valid_from,
                                          valid_to=address_valid_to,
                                          person_id=new_person.internal_id)
                    session.add(new_address)

            if entry.communications is not None:
                for comm_entry in entry.communications:
                    type_phone = [1, 3]
                    if comm_entry.communication_type.id_ in type_phone:
                        if comm_entry.content is not None:
                            comm_entry.content = comm_entry.content.replace(' ', '').strip()
                            comm_entry.content = comm_entry.content.replace('0049', '0')
                            comm_entry.content = comm_entry.content.replace('+49', '0')

                    new_comm = Communication(internal_id=comm_entry.id_,
                                             related_address_id=comm_entry.related_address_id,
                                             content=comm_entry.content,
                                             explanation=comm_entry.explanation,
                                             communication_type_id=comm_entry.communication_type.id_,
                                             communication_type=comm_entry.communication_type.name,
                                             person_id=new_person.internal_id)
                    session.add(new_comm)
        session.commit()
        logger.info(f"Added {sectioncount} persons.")

    # Für Contractors brauchen wir auch Contracts
    if ENCONTRACTORS in entities and ENCONTRACTS not in entities:
        entities.append(ENCONTRACTS)

    if ENCONTRACTS in entities:
        sectioncount = 0
        contracts = wowicon.get_license_agreements(fetch_all=True)
        for entry in contracts:
            print(str(entry.start_contract))
            contract_start = datetime.strptime(str(entry.start_contract), "%Y-%m-%d %H:%M:%S") \
                if entry.start_contract else None
            contract_end = datetime.strptime(str(entry.end_of_contract), "%Y-%m-%d  %H:%M:%S") \
                if entry.end_of_contract else None
            new_entry = Contract(internal_id=entry.id_,
                                 id_num=entry.id_num,
                                 use_unit_id=entry.use_unit.id_,
                                 restriction_id=entry.restriction_of_use.id_,
                                 restriction_name=entry.restriction_of_use.name,
                                 is_vacancy=entry.restriction_of_use.is_vacancy,
                                 status_id=entry.status_contract.id_,
                                 status_name=entry.status_contract.name,
                                 life_id=entry.life_of_contract.id_,
                                 life_name=entry.life_of_contract.name,
                                 contract_start=contract_start,
                                 contract_end=contract_end)
            session.add(new_entry)
            sectioncount += 1
        session.commit()
        logger.info(f"Added {sectioncount} contracts.")

    if ENCONTRACTORS in entities:
        sectioncount = 0
        contractors = wowicon.get_contractors(fetch_all=True)
        for entry in contractors:
            # end_contract = datetime.strptime(str(entry.end_of_contract), "%Y-%m-%d") \
            #     if entry.end_of_contract else None
            # if end_contract is not None:
            #     print(f"ID: {entry.id_}")
            #     # print(end_contract)
            #     # print(datetime.now() > end_contract)
            #     if datetime.now() > end_contract:
            #         # print("Überspringen")
            #         continue
            valid_from = datetime.strptime(str(entry.contractual_use_valid_from), "%Y-%m-%d") \
                if entry.contractual_use_valid_from else None
            valid_to = datetime.strptime(str(entry.contractual_use_valid_to), "%Y-%m-%d") \
                if entry.contractual_use_valid_to else None

            new_entry = Contractor(internal_id=entry.id_,
                                   contract_id=entry.license_agreement_id,
                                   use_unit_id=entry.use_unit.id_,
                                   person_id=entry.person.id_,
                                   type_id=entry.contractor_type.id_,
                                   type_name=entry.contractor_type.name,
                                   valid_from=valid_from,
                                   valid_to=valid_to)
            try:
                session.add(new_entry)
                session.commit()
                sectioncount += 1
            except sqlalchemy.exc.IntegrityError:
                logger.warning(f"Rolling back contractor")
                session.rollback()

        logger.info(f"Added {sectioncount} contractors.")

    if ENMEMBERSHIPS in entities:
        sectioncount = 0
        memberships = wowicon.get_memberships(fetch_all=True)
        for entry in memberships:
            new_entry = Membership(internal_id=entry.id_,
                                   id_num=entry.id_num,
                                   creation_date=entry.creation_date,
                                   valid_from=entry.valid_from,
                                   valid_to=entry.valid_to,
                                   is_payout_block_account=entry.is_payout_block_account,
                                   cooperative_account_clearing_lock=entry.cooperative_account_clearing_lock,
                                   subsidy_application_for_several_fiscal_years_allowed=entry.
                                   subsidy_application_for_several_fiscal_years_allowed,
                                   no_participation_electoral_district=entry.no_participation_electoral_district,
                                   active_amount_sum=entry.active_amount_sum,
                                   active_count_sum=entry.active_count_sum,
                                   membership_status_id=entry.membership_status_id,
                                   membership_status_code=entry.membership_status_code,
                                   electoral_district_id=entry.electoral_district_id,
                                   electoral_district_code=entry.electoral_district_code,
                                   membership_end_reason_id=entry.membership_end_reason_id,
                                   membership_end_reason_code=entry.membership_end_reason_code,
                                   description=entry.description,
                                   active_main_member_person_id=entry.active_main_member_person_id,
                                   active_main_member_person_id_num=entry.active_main_member_person_id_num)
            try:
                session.add(new_entry)
                session.commit()
                sectioncount += 1
            except sqlalchemy.exc.IntegrityError:
                logger.warning(f"Rolling back membership")
                session.rollback()

        logger.info(f"Added {sectioncount} memberships.")

    if ENPAYMENTMODES in entities:
        sectioncount = 0
        payment_modes = wowicon.get_payment_modes(fetch_all=True, license_agreement_active_on=datetime.now(),
                                                  payment_mode_active_on=datetime.now())
        for entry in payment_modes:
            new_entry = PaymentMode(internal_id=entry.id_,
                                    contract_id=entry.license_agreement.id_,
                                    active_from=entry.active_from,
                                    active_to=entry.active_to,
                                    mode_id=entry.mode_id,
                                    mode_name=entry.mode_name,
                                    type_id=entry.type_id,
                                    type_name=entry.type_name,
                                    sepa_id=entry.sepa_id,
                                    sepa_iban=entry.sepa_iban,
                                    sepa_mandate_id=entry.sepa_mandate_id,
                                    bank_account_id=entry.bank_account_id,
                                    bank_account_bix=entry.bank_account_bic,
                                    bank_account_iban=entry.bank_account_iban
                                    )
            try:
                session.add(new_entry)
                session.commit()
                sectioncount += 1
            except sqlalchemy.exc.IntegrityError:
                logger.warning(f"Rolling back payment_mode")
                session.rollback()

        logger.info(f"Added {sectioncount} payment_modes.")

    session.close()
    logger.info("Cache update complete.")


if __name__ == '__main__':
    cache_to_db()

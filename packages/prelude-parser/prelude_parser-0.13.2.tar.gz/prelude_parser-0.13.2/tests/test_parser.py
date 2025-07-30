from datetime import date

import pytest

from prelude_parser import (
    parse_site_native_file,
    parse_site_native_string,
    parse_subject_native_file,
    parse_subject_native_string,
    parse_to_classes,
    parse_to_dict,
    parse_user_native_file,
    parse_user_native_string,
)
from prelude_parser._prelude_parser import FileNotFoundError, InvalidFileTypeError, ParsingError


def test_parse_site_native_file(site_native_xml):
    result = parse_site_native_file(site_native_xml)

    assert result.sites[0].name == "Some Site"


def test_parse_site_native_string(site_native_xml):
    with open(site_native_xml) as f:
        xml = f.read()
    result = parse_site_native_string(xml)

    assert result.sites[0].name == "Some Site"


def test_site_native_to_dict(site_native_xml):
    result = parse_site_native_file(site_native_xml)
    result_dict = result.to_dict()

    assert result_dict["sites"][0]["name"] == "Some Site"


def test_site_native_to_json(site_native_small_xml):
    result = parse_site_native_file(site_native_small_xml)
    result_json = result.to_json()

    assert (
        result_json
        == '{"site":[{"name":"Some Site","uniqueId":"1681574834910","numberOfPatients":4,"countOfRandomizedPatients":0,"whenCreated":"2023-04-15T16:08:19Z","creator":"Paul Sanders","numberOfForms":1,"form":[{"name":"demographic.form.name.site.demographics","lastModified":"2023-04-15T16:08:19Z","whoLastModifiedName":"Paul Sanders","whoLastModifiedRole":"Project Manager","whenCreated":1681574834930,"hasErrors":false,"hasWarnings":false,"locked":false,"user":null,"dateTimeChanged":null,"formTitle":"Site Demographics","formIndex":1,"formGroup":"Demographic","formState":"In-Work","states":[{"value":"form.state.in.work","signer":"Paul Sanders - Project Manager","signerUniqueId":"1681162687395","dateSigned":"2023-04-15T16:08:19Z"}],"categories":[{"name":"Demographics","categoryType":"normal","highestIndex":0,"fields":[{"name":"company","fieldType":"text","dataType":"string","errorCode":"valid","whenCreated":"2023-04-15T16:07:14Z","keepHistory":true,"entries":[{"entryId":"1","value":{"by":"Paul Sanders","byUniqueId":"1681162687395","role":"Project Manager","when":"2023-04-15T16:08:19Z","value":"Some Company"},"reason":null}],"comments":[{"commentId":"1","value":{"by":"Paul Sanders","byUniqueId":"1681162687395","role":"Project Manager","when":"2023-04-15T16:09:02Z","value":"Some comment"}}]}]}]}]}]}'
    )


def test_parse_subject_native_file(subject_native_xml):
    result = parse_subject_native_file(subject_native_xml)

    assert result.patients[0].patient_id == "ABC-001"


def test_parse_subject_native_string(subject_native_xml):
    with open(subject_native_xml) as f:
        xml = f.read()
    result = parse_subject_native_string(xml)

    assert result.patients[0].patient_id == "ABC-001"


def test_subject_native_to_dict(subject_native_xml):
    result = parse_subject_native_file(subject_native_xml)
    result_dict = result.to_dict()

    assert result_dict["patients"][0]["patient_id"] == "ABC-001"


def test_subject_native_to_json(subject_native_small_xml):
    result = parse_subject_native_file(subject_native_small_xml)
    result_json = result.to_json()

    assert (
        result_json
        == '{"patients":[{"patientId":"ABC-001","uniqueId":"1681574905819","whenCreated":"2023-04-15T16:09:02Z","creator":"Paul Sanders","siteName":"Some Site","siteUniqueId":"1681574834910","lastLanguage":null,"numberOfForms":6,"forms":[{"name":"day.0.form.name.demographics","lastModified":"2023-04-15T16:09:15Z","whoLastModifiedName":"Paul Sanders","whoLastModifiedRole":"Project Manager","whenCreated":1681574905839,"hasErrors":false,"hasWarnings":false,"locked":false,"user":null,"dateTimeChanged":null,"formTitle":"Demographics","formIndex":1,"formGroup":"Day 0","formState":"In-Work","states":[{"value":"form.state.in.work","signer":"Paul Sanders - Project Manager","signerUniqueId":"1681162687395","dateSigned":"2023-04-15T16:09:02Z"}],"categories":[{"name":"Demographics","categoryType":"normal","highestIndex":0,"fields":[{"name":"breed","fieldType":"combo-box","dataType":"string","errorCode":"valid","whenCreated":"2023-04-15T16:08:26Z","keepHistory":true,"entries":[{"entryId":"1","value":{"by":"Paul Sanders","byUniqueId":"1681162687395","role":"Project Manager","when":"2023-04-15T16:09:02Z","value":"Labrador"},"reason":null}],"comments":[{"commentId":"1","value":{"by":"Paul Sanders","byUniqueId":"1681162687395","role":"Project Manager","when":"2023-04-15T16:09:02Z","value":"Some comment"}}]}]}]}]}]}'
    )


def test_parse_user_native_file(user_native_xml):
    result = parse_user_native_file(user_native_xml)

    assert result.users[0].unique_id == "1691421275437"


def test_parse_user_native_string(user_native_xml):
    with open(user_native_xml) as f:
        xml = f.read()
    result = parse_user_native_string(xml)

    assert result.users[0].unique_id == "1691421275437"


def test_user_native_to_dict(user_native_xml):
    result = parse_user_native_file(user_native_xml)
    result_dict = result.to_dict()

    assert result_dict["users"][0]["unique_id"] == "1691421275437"


def test_user_native_to_json(user_native_small_xml):
    result = parse_user_native_file(user_native_small_xml)
    result_json = result.to_json()

    assert (
        result_json
        == '{"users":[{"uniqueId":"1691421275437","lastLanguage":null,"creator":"Paul Sanders(1681162687395)","numberOfForms":1,"forms":[{"name":"form.name.demographics","lastModified":"2023-08-07T15:15:41Z","whoLastModifiedName":"Paul Sanders","whoLastModifiedRole":"Project Manager","whenCreated":1691421341578,"hasErrors":false,"hasWarnings":false,"locked":false,"user":null,"dateTimeChanged":null,"formTitle":"User Demographics","formIndex":1,"formGroup":null,"formState":"In-Work","states":[{"value":"form.state.in.work","signer":"Paul Sanders - Project Manager","signerUniqueId":"1681162687395","dateSigned":"2023-08-07T15:15:41Z"}],"categories":[{"name":"demographics","categoryType":"normal","highestIndex":0,"fields":[{"name":"email","fieldType":"text","dataType":"string","errorCode":"undefined","whenCreated":"2023-08-07T15:15:41Z","keepHistory":true,"entries":[{"entryId":"1","value":{"by":"Paul Sanders","byUniqueId":"1681162687395","role":"Project Manager","when":"2023-08-07T15:15:41Z","value":"jazz@artemis.com"},"reason":null}],"comments":[{"commentId":"1","value":{"by":"Paul Sanders","byUniqueId":"1681162687395","role":"Project Manager","when":"2023-04-15T16:09:02Z","value":"Some comment"}}]}]}]}]}]}'
    )


def test_parse_to_classes(test_file_1):
    result = parse_to_classes(test_file_1)
    assert len(result) == 2
    assert result[0].__name__ == "Communications"
    assert result[0].study_name == "PBS"
    assert result[0].site_name == "Some Site"
    assert result[0].site_id == 1681574834910
    assert result[0].patient_name == "ABC-001"
    assert result[0].patient_id == 1681574905819
    assert result[0].form_title == "Communications"
    assert result[0].base_form == "communications.form.name.communications"
    assert result[0].form_number is None
    assert result[0].form_group == "Communications"
    assert result[0].form_state == "In-Work"
    assert result[0].communications_made == "Yes"


def test_parse_to_classes_with_float(test_file_2):
    result = parse_to_classes(test_file_2)
    assert len(result) == 2
    assert result[0].__name__ == "Demographics"
    assert result[0].weight == 80.2
    assert result[0].dob == date(2020, 4, 15)


def test_parse_to_classes_i_form(test_file_3):
    result = parse_to_classes(test_file_3)
    assert len(result) == 3
    assert result[0].__name__ == "ICommunicationsDetails"
    assert result[0].study_name == "PBS"
    assert result[0].site_name == "Some Site"
    assert result[0].site_id == 1681574834910
    assert result[0].patient_name == "ABC-001"
    assert result[0].patient_id == 1681574905819
    assert result[0].form_title == "Communications"
    assert result[0].base_form == "communications.form.name.communications"
    assert result[0].form_number is None
    assert result[0].form_group == "Communications"
    assert result[0].form_state == "In-Work"
    assert result[0].i == 1
    assert result[0].contacted_by == "You"
    assert result[0].investigator == "Dr. Me"
    assert result[0].communication == "Some random talk"


def test_parse_to_classes_not_found_error():
    with pytest.raises(FileNotFoundError):
        parse_to_classes("bad.xml")


def test_parse_to_classes_invalid_file_type_error(tmp_path):
    bad = tmp_path / "bad.txt"
    bad.touch()
    with pytest.raises(InvalidFileTypeError):
        parse_to_classes(bad)


def test_parse_to_classes_parsing_error(tmp_path):
    bad = tmp_path / "bad.xml"
    bad.touch()
    with pytest.raises(ParsingError):
        parse_to_classes(bad)


def test_parse_to_classes_short_names(test_file_4):
    result = parse_to_classes(test_file_4, short_names=True)
    assert len(result) == 2
    assert result[0].__name__ == "Communications"
    assert result[0].studyname == "PBS"
    assert result[0].sitename == "Some Site"


def test_parse_to_dict(test_file_1):
    result = parse_to_dict(test_file_1)
    expected = {
        "communications": [
            {
                "base_form": "communications.form.name.communications",
                "communications_made": "Yes",
                "form_group": "Communications",
                "form_number": None,
                "form_state": "In-Work",
                "form_title": "Communications",
                "patient_id": 1681574905819,
                "patient_name": "ABC-001",
                "site_id": 1681574834910,
                "site_name": "Some Site",
                "study_name": "PBS",
            },
            {
                "base_form": "communications.form.name.communications",
                "communications_made": "Yes",
                "form_group": "Communications",
                "form_number": None,
                "form_state": "In-Work",
                "form_title": "Communications",
                "patient_id": 1681574994823,
                "patient_name": "ABC-002",
                "site_id": 1681574834910,
                "site_name": "Some Site",
                "study_name": "PBS",
            },
        ]
    }

    result["communications"] = [dict(sorted(x.items())) for x in result["communications"]]

    assert result == expected


def test_parse_to_dict_with_float(test_file_2):
    result = parse_to_dict(test_file_2)
    expected = {
        "demographics": [
            {
                "base_form": "day.0.form.name.demographics",
                "breed": "Labrador",
                "dob": date(2020, 4, 15),
                "first_name": "Imma",
                "form_group": "Day 0",
                "form_number": None,
                "form_state": "In-Work",
                "form_title": "Demographics",
                "gender": "Female Spayed",
                "last_name": "Dog",
                "patient_id": 1681574905819,
                "patient_name": "ABC-001",
                "screening_number": 1,
                "site_id": 1681574834910,
                "site_name": "Some Site",
                "site_type": "Live",
                "study_name": "PBS",
                "subject_id": "ABC-001",
                "visit_date": date(2023, 4, 15),
                "weight": 80.2,
            },
            {
                "base_form": "day.0.form.name.demographics",
                "breed": "Golden",
                "dob": date(2019, 4, 9),
                "first_name": "Arthur",
                "form_group": "Day 0",
                "form_number": None,
                "form_state": "In-Work",
                "form_title": "Demographics",
                "gender": "Male Neutered",
                "last_name": "Dent",
                "patient_id": 1681574994823,
                "patient_name": "ABC-002",
                "screening_number": 2,
                "site_id": 1681574834910,
                "site_name": "Some Site",
                "site_type": "Live",
                "study_name": "PBS",
                "subject_id": "ABC-002",
                "visit_date": date(2023, 4, 15),
                "weight": 40.5,
            },
        ]
    }

    result["demographics"] = [dict(sorted(x.items())) for x in result["demographics"]]

    assert result == expected


def test_parse_to_dict_i_form(test_file_3):
    result = parse_to_dict(test_file_3)
    expected = {
        "i_communications_details": [
            {
                "base_form": "communications.form.name.communications",
                "communication": "Some random talk",
                "contacted_by": "You",
                "form_group": "Communications",
                "form_number": None,
                "form_state": "In-Work",
                "form_title": "Communications",
                "i": 1,
                "investigator": "Dr. Me",
                "patient_id": 1681574905819,
                "patient_name": "ABC-001",
                "site_id": 1681574834910,
                "site_name": "Some Site",
                "study_name": "PBS",
            },
            {
                "base_form": "communications.form.name.communications",
                "communication": "We talked",
                "contacted_by": "Hi",
                "form_group": "Communications",
                "form_number": None,
                "form_state": "In-Work",
                "form_title": "Communications",
                "i": 1,
                "investigator": "There",
                "patient_id": 1681574994823,
                "patient_name": "ABC-002",
                "site_id": 1681574834910,
                "site_name": "Some Site",
                "study_name": "PBS",
            },
            {
                "base_form": "communications.form.name.communications",
                "communication": "We talked again",
                "contacted_by": "There",
                "i": 2,
                "investigator": "Hi",
                "form_group": "Communications",
                "form_number": None,
                "form_state": "In-Work",
                "form_title": "Communications",
                "patient_id": 1681574994823,
                "patient_name": "ABC-002",
                "site_id": 1681574834910,
                "site_name": "Some Site",
                "study_name": "PBS",
            },
        ]
    }

    result["i_communications_details"] = [
        dict(sorted(x.items())) for x in result["i_communications_details"]
    ]

    assert result == expected


def test_parse_to_dict_short_names(test_file_4):
    result = parse_to_dict(test_file_4, short_names=True)
    expected = {
        "communications": [
            {
                "sitename": "Some Site",
                "studyname": "PBS",
            },
            {
                "sitename": "Another Site",
                "studyname": "PBS",
            },
        ]
    }

    result["communications"] = [dict(sorted(x.items())) for x in result["communications"]]

    assert result == expected

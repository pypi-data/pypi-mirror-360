from logger_local.LoggerComponentEnum import LoggerComponentEnum


class CSVToContactPersonProfileConstants:
    CSV_LOCAL_PYTHON_COMPONENT_ID = 198
    CSV_LOCAL_PYTHON_COMPONENT_NAME = 'contact-person-profile-csv-imp-local-python-package'
    DEVELOPER_EMAIL = "tal.g@circ.zone"
    CSV_LOCAL_PYTHON_PACKAGE_CODE_LOGGER_OBJECT = {
        'component_id': CSV_LOCAL_PYTHON_COMPONENT_ID,
        'component_name': CSV_LOCAL_PYTHON_COMPONENT_NAME,
        'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
        'developer_email': DEVELOPER_EMAIL
    }

    CSV_LOCAL_PYTHON_PACKAGE_TEST_LOGGER_OBJECT = {
        'component_id': CSV_LOCAL_PYTHON_COMPONENT_ID,
        'component_name': CSV_LOCAL_PYTHON_COMPONENT_NAME,
        'component_category': LoggerComponentEnum.ComponentCategory.Unit_Test.value,
        'testing_framework': LoggerComponentEnum.testingFramework.pytest.value,
        'developer_email': DEVELOPER_EMAIL
    }

    GOOGLE_CSV_DATA_SOURCE_TYPE_ID = 16
    LINKEDIN_CSV_DATA_SOURCE_TYPE_ID = 18
    OUTLOOK_CSV_DATA_SOURCE_TYPE_ID = 17
    BGU_COURSE_CSV_DATA_SOURCE_TYPE_ID = 57
    RISHON_MUNI_EXHIBITOR_CSV_DATA_SOURCE_TYPE_ID = 60

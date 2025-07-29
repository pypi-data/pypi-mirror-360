"""imports"""
from logger_local.LoggerComponentEnum import LoggerComponentEnum

DEVELOPER_EMAIL = 'jenya.b@circ.zone'
MESSAGE_SEND_LOCAL_PYTHON_COMPONENT_ID = 301
MESSAGE_SEND_LOCAL_PYTHON_COMPONENT_COMPONENT_NAME = 'location local python package'
MESSAGE_SEND_CODE_LOGGER_OBJECT = {
    'component_id': MESSAGE_SEND_LOCAL_PYTHON_COMPONENT_ID,
    'component_name': MESSAGE_SEND_LOCAL_PYTHON_COMPONENT_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': DEVELOPER_EMAIL
}
MESSAGE_SEND_LOCAL_PYTHON_TEST_LOGGER_OBJECT = {
    'component_id': MESSAGE_SEND_LOCAL_PYTHON_COMPONENT_ID,
    'component_name': MESSAGE_SEND_LOCAL_PYTHON_COMPONENT_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Unit_Test.value,
    'testing_framework': LoggerComponentEnum.testingFramework.pytest.value,
    'developer_email': DEVELOPER_EMAIL
}

COUNTRY_TABLE_NAME = 'country_table'
COUNTRY_VIEW_NAME = 'country_view'

COUNTRY_ML_TABLE_NAME = 'country_ml_table'
COUNTRY_ML_VIEW_NAME = 'country_ml_view'

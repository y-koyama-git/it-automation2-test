import pprint
import json


def external_valid_before(objdbca, objtable, option):
    # print('xxxxx-1001')
    # print('external_valid_before')
    retBool = True
    msg = ''
    #  pprint.pprint(option)
    return retBool, msg, option,

def external_valid_after(objdbca, objtable, option):
    # print('xxxxx-1001')
    # print('external_valid_after')
    retBool = True
    msg = ''
    #  pprint.pprint(option)
    return retBool, msg, option,

def external_valid_menu_before(objdbca, objtable, option):
    # print('xxxxx-1001')
    # print('external_valid_menu_before')
    retBool = True
    msg = ''
    option = convert_conductor_ver_1(option)
    print(option)
    return retBool, msg, option,

def external_valid_menu_after(objdbca, objtable, option):
    # print('xxxxx-1001')
    # print('external_valid_menu_after')
    retBool = True
    msg = ''
    #  pprint.pprint(option)
    return retBool, msg, option,

def convert_conductor_ver_1(option):
    target_rest_name = 'setting'
    entry_parameter = option.get('entry_parameter')
    tmp_parameter = entry_parameter.get('parameter')
    tmp_setting = tmp_parameter.get(target_rest_name)
    if tmp_setting is not None:
        tmp_setting = tmp_setting.replace("LUT4U", "last_update_date_time")
        tmp_setting = tmp_setting.replace("SKIP_FLAG", "skip_flag")
        tmp_setting = tmp_setting.replace("CALL_CONDUCTOR_ID", "call_conductor_id")
        tmp_setting = tmp_setting.replace("OPERATION_NO_IDBH", "operation_id")
        tmp_setting = tmp_setting.replace("PATTERN_ID", "movement_id")
        tmp_setting = tmp_setting.replace("OPERATION_NO_IDBH", "operation_id")
        tmp_setting = tmp_setting.replace("ORCHESTRATOR_ID", "orchestra_id")
        
        json_setting = json.loads(tmp_setting)
        if 'ACCESS_AUTH' in  json_setting['conductor']:
            del json_setting['conductor']['ACCESS_AUTH']
        if 'NOTICE_INFO' in  json_setting['conductor']:
            del json_setting['conductor']['NOTICE_INFO']
        tmp_setting = json.dumps(json_setting)
        option['entry_parameter']['parameter']['setting'] = tmp_setting

    return option

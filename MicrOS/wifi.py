import network
try:
    import LogHandler
except Exception as e:
    print("[ MICROPYTHON IMPORT ERROR ] " + str(e))
    LogHandler = None
import time

#########################################################
#                                                       #
#               SIMPLE WIFI INFO GETTER                 #
#                                                       #
#########################################################
def wifi_info():
    wifi_info_dict = {}

    # the access point
    ap_if = network.WLAN(network.AP_IF)

    # station mode - connect to wifi
    sta_if = network.WLAN(network.STA_IF)

    # turn access point on:
    #ap_if.active(True)
    # turn access point off:
    #ap_if.active(False)

    # turn station mode on:
    #sta_if.active(True)
    # turn station mode off:
    #sta_if.active(False)

    # turn on station mode:
    #sta_if.connect('<your ESSID>', '<your password>')
    #sta_if.config('password')

    wifi_info_dict = {  'ap_state': str(ap_if.active()),
                        'sta_state': str(sta_if.active()),
                        'ap_isconnected': str(ap_if.isconnected()),
                        'sta_isconnected': str(sta_if.isconnected()),
                        'ap_iplist': ap_if.ifconfig(),
                        'sta_iplist': sta_if.ifconfig(),
    }
    if wifi_info_dict['ap_state'] == "True":
        #wifi_info_dict['ap_avaible_networks'] = str(ap_if.scan())
        wifi_info_dict['ap_avaible_networks'] = str(None)
    else:
        wifi_info_dict['ap_avaible_networks'] = str(None)

    if wifi_info_dict['sta_state'] == "True":
        wifi_info_dict['sta_avaible_networks'] = str(sta_if.scan())
        #wifi_info_dict['sta_avaible_networks'] = str(None)
    else:
        wifi_info_dict['sta_avaible_networks'] = str(None)

    #print(wifi_info_dict)
    return wifi_info_dict

#########################################################
#                                                       #
#                  SET WIFI STA MODE                    #
#                                                       #
#########################################################
def set_wifi(essid, pwd, timeout=50, ap_auto_disable=True, essid_force_connect=False):
    """ WIFI SETTER - EXTAR PARAMETERS: ACCESS POINT AUTO DISABLE WHEN STATION MODE IS ON, ESSID DISCONNECT BEFORE CONNECT SELECTED SSID """
    if LogHandler is not None:
        LogHandler.logger.debug("[SET_WIFI METHOD] SET WIFI NETWORK:\nparameters: essid,\t\t\tpwd,\t\ttimeout,\tap_auto_disable,\tessid_force_connect\n            " + \
                             str(essid) +",\t"+  str(pwd) +",\t"+ str(timeout) +",\t\t"+ str(ap_auto_disable) +",\t\t\t"+ str(essid_force_connect))
    if ap_auto_disable:
        ap_if = network.WLAN(network.AP_IF)
        if ap_if.active():
            ap_if.active(False)

    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    is_essid_exists = False
    # disconnect before connect to selected essid *** normally micropython framework connected to last known wlan network automaticly
    if essid_force_connect and sta_if.isconnected():
        if LogHandler is not None:
            LogHandler.logger.debug("\t| disconnect from wifi (sta)")
        sta_if.disconnect()
    # connet if we are not connected yet
    if not sta_if.isconnected(): 
        if LogHandler is not None:
            LogHandler.logger.debug('\t| connecting to network... ')
        sta_if.active(True)
        for wifi_spot in sta_if.scan():
            if essid in str(wifi_spot):
                is_essid_exists = True
                # connect to network
                sta_if.connect(essid, pwd)
                # wait for connection, with timeout set
                while not sta_if.isconnected() and timeout > 0:
                    if LogHandler is not None:
                        LogHandler.logger.info("Waiting for connection... " + str(timeout) + "/50" )
                    timeout -= 1
                    time.sleep(0.2)
        if LogHandler is not None:
            LogHandler.logger.debug("\t|\t| network config: " + str(sta_if.ifconfig()))
            LogHandler.logger.debug("\t|\t| WIFI SETUP STA: " + str(sta_if.isconnected()))
    else:
        if LogHandler is not None:
            LogHandler.logger.debug("\t| already conneted (sta)")
        # we are connected already
        for wifi_spot in sta_if.scan():
            if essid in str(wifi_spot):
                is_essid_exists = True
    # return bool:is connected to network, bool: is essid found
    return sta_if.isconnected(), is_essid_exists

#########################################################
#                                                       #
#                 GET WIFI STRENGHT                     #
#                                                       #
#########################################################
def wifi_rssi(essid):
    """ GET SSID AND CHANNEL FOR THE SELECTED ESSID"""
    if LogHandler is not None:
        LogHandler.logger.debug("[WIFI RSSI METHOD] GET RSSI AND CHANNEL FOR GIVEN ESSID")
    rssi = None
    channel = None
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    # if sta not connected to the given essid
    if not sta_if.isconnected():
        return None, None, None, (None, 0)
    # if we are connected - get informations
    try:
        wifi_list = sta_if.scan()
    except:
        rssi = 0
        channel = None
        wifi_list = []
    for wifi_spot in wifi_list:
        if essid in str(wifi_spot):
            rssi = wifi_spot[3]
            channel = wifi_spot[2]
    # calculate human readable quality for rssi - hr_rssi_tupple: human readuble rssi tumpe [0]- string, [1]: number 0-4
    if rssi >= -30:
        hr_rssi_tupple = "Amazing", 4
    elif rssi >= -67:
        hr_rssi_tupple = "VeryGood", 3
    elif rssi >= -70:
        hr_rssi_tupple = "Okey", 2
    elif rssi >= -80:
        hr_rssi_tupple = "NotGood", 1
    elif rssi >= -90:
        hr_rssi_tupple = "Unusable", 0

    if LogHandler is not None:
        LogHandler.logger.debug("\t| essid, rssi, channel: " + str(essid) +", "+ str(rssi) +", "+ str(channel) +", "+ str(hr_rssi_tupple))
    return essid, rssi, channel, hr_rssi_tupple

#########################################################
#                                                       #
#               SET WIFI ACCESS POINT MODE              #
#                                                       #
#########################################################
def set_access_point(_essid, _pwd, _channel=11, sta_auto_disable=True):
    """ SET ACCESS POINT WITH CUSTOM ESSID, CHANNEL, FORCE MODE LIKE SET WIFI METHOD...."""
    if LogHandler is not None:
        LogHandler.logger.debug("[SET ACCESS POUNT METHOD] SET ACCESS POINT MODE:\n_essid,\t\t_pwd,\t_channel,\tsta_auto_disable\n" +\
                             str(_essid) +",\t"+ str(_pwd) +",\t"+  str(_channel) +",\t\t"+ str(sta_auto_disable))
    if sta_auto_disable:
        sta_if = network.WLAN(network.STA_IF)
        if sta_if.isconnected():
            sta_if.active(False)

    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(True)
    is_success = False
    # Set WiFi access point name (formally known as ESSID) and WiFi channel
    try:
        ap_if.config(essid=_essid, channel=_channel)
    except Exception as e:
        print(">>>>>>>>>>>>>>" + str(e))
    if ap_if.active() and str(ap_if.config('essid')) == str(_essid) and ap_if.config('channel') == _channel:
        is_success = True
    return is_success, ap_if.config('essid'), ap_if.config('channel'), ap_if.config('mac')

#########################################################
#                                                       #
#          AUTOMATIC NETWORK CONFIGURATION              #
#IF STA AVAIBLE, IF NOT AP MODE                         #
#########################################################
def auto_network_configuration(essid, pwd, timeout=50, ap_auto_disable=True, essid_force_connect=False, _essid="NodeMcuBNM", _pwd="guest", _channel=11, sta_auto_disable=True):
    # default connection type is STA
    isconnected, is_essid_exists = set_wifi(essid, pwd, timeout=timeout, ap_auto_disable=ap_auto_disable, essid_force_connect=essid_force_connect)
    print("STA======>" + str(isconnected) + "  - " + str(is_essid_exists))
    # if sta is not avaible, connect make AP for configuration
    if not (isconnected and is_essid_exists):
        print("STA MODE IS DISABLE - ESSID or PWD not valid")
        ap_is_success, ap_essid, ap_channel, ap_config_mac = set_access_point(_essid=_essid, _pwd=_pwd, _channel=_channel, sta_auto_disable=sta_auto_disable)
        print("AP======>" + str(ap_is_success) + "  - " + str(ap_essid) + " - " + str(ap_channel) + " - " + str(ap_config_mac))


#########################################################
#                                                       #
#               TEST AND DEMO FUNCTIONS                 #
#                                                       #
#########################################################
if __name__ == "__main__":
    auto_network_configuration(essid="elektroncsakpozitivan", pwd="BNM3,1415")
    '''
    # TEST CALLS
    #https://docs.micropython.org/en/latest/esp8266/library/network.html
    print("--TEST--> SET WIFI (STA)\n")
    print(set_wifi("elektroncsakpozitivan", "BNM3,1415"))

    print("--TEST--> GET WIFI RSSI INFO\n")
    print(wifi_rssi("elektroncsakpozitivan"))

    print("--TEST--> GET WIFI INFOS (after sta set)\n")
    wifi_info_dict = wifi_info()
    print(wifi_info_dict)

    print("--TEST--> SET ACCESS POINT (AP)\n")
    print(set_access_point("NodeMcuBNM", "guest"))

    print("--TEST--> GET WIFI INFOS (after ap set)\n")
    wifi_info_dict = wifi_info()
    print(wifi_info_dict)
    '''

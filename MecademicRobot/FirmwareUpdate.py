#!/usr/bin/env python3
import sys
import argparse
import requests
import time
import json


def main():
    ''' Update the robot firmware with the one given.
    '''
    [robot_fw_path, robot_ip_address] = cli()
    update_robot(robot_fw_path, robot_ip_address)


def cli():
    ''' Command line interface to collect the robot IP address and the path of the firmware
    '''
    parser = argparse.ArgumentParser(description='Run the firmware Update of the robot.')
    parser.add_argument('--robot_fw_path',
                        metavar='robot_fw_path',
                        type=str,
                        nargs='+',
                        default='.',
                        help='The path of the firmware to update the robot.')
    parser.add_argument('--robot_ip_address',
                        metavar='robot_ip_address',
                        type=str,
                        nargs='+',
                        default=["192.168.0.100"],
                        help='The IP of the robot that will be update.')
    args = parser.parse_args(sys.argv[1:])
    return [args.robot_fw_path[0], f'http://' + args.robot_ip_address[0] + f'/']


def update_robot(file_path, ip_address):
    ''' Send the update specified by file_path to the robot.
        Param file_path : Path to the firware file
        Param ip_address: IP Address of the robot to update
    '''

    # open the file
    print(f'Opening firmware file...')
    update_file = open(file_path, 'rb')
    update_data = update_file.read()
    update_file_size = len(update_data)

    print(f'Done. \nUpdate size is: ' + str(update_file_size) + 'B.')
    print(f'Uploading file...')

    headers = {'Connection': 'keep-alive',
               'Content-type': 'application/x-gzip',
               'Content-Length': str(update_file_size)}

    try:
        r = requests.post(ip_address, data=update_data, headers=headers)
    except requests.Timeout:
        print(f'timeout ...')
        sys.exit()
    except requests.ConnectionError as e:
        print(f'Connection Error ...')
        print(f'e: {e}')
        sys.exit()

    if not r.ok:
        raise RuntimeError('Firmware upload request failed.')

    update_done = False
    print('Upgrading:')

    progress = ''
    last_progress = ''

    while not update_done:

        r = requests.get(ip_address, 'update', timeout=10)
        if r.text == '0':
            continue
        time.sleep(1)
        request_answer = json.loads(r.text)

        status_code = int(request_answer.get('STATUS').get('Code'))

        if status_code == -1:
            print(f'{request_answer.get("STATUS").get("MSG")}')
            raise RuntimeError('Error while updating')
        elif status_code == 0:
            update_done = True
            print(f'{request_answer.get("STATUS").get("MSG")}')
        elif status_code == 1:
            keys = sorted(request_answer.get('LOG').keys())
            if keys:
                last_progress = progress
                progress = request_answer.get('LOG').get(keys[-1])
                new_progress = progress.replace(last_progress, '')
                if "#" in new_progress:
                    print(f'', end='')
                print(f'{new_progress}', end='')
                if '100%' in new_progress:
                    print(f'')

        time.sleep(2)

    print(f'Update done')
    wait_for_robot_reboot(40)


def wait_for_robot_reboot(time_in_second):
    ''' Waiting dalay to let the robot finish updating.
        Param time_in_second : waiting time for the robot reboot.
    '''
    time.sleep(time_in_second)


if __name__ == "__main__":
    main()

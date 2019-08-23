#!/usr/bin/python3

"""
Create a mapping of usable addresses from a relational database
"""

 
from collections import defaultdict
import configparser

import usaddress
import pandas as pd


def clean(string):
    string = string.upper()
    string = string.replace('\n', '').replace('   ', ' ').replace('  ', ' ').replace(',', '')
    string = string.replace('UNITED STATES OF AMERICA', '')
    return string.strip()

def parse_dict(address):
    parsed = usaddress.parse(address)
    parsed_dict = defaultdict(str)
    for name in parsed:
        if name[1] in parsed_dict.keys():
            parsed_dict[name[1]] += ' ' + name[0]
	# Add address if doesn't exist, which is why we need a defaultdict
        else:
            parsed_dict[name[1]] = name[0]
    return parsed_dict
   

def parse_line1(address):
    parsed = parse_dict(address)
    addr_line1 =                                            \
              parsed['USPSBoxType'] + ' '                   \
            + parsed['USPSBoxID'] + ' '                     \
            + parsed['AddressNumber'] + ' '                 \
            + parsed['StreetNamePreDirectional'] + ' '      \
            + parsed['StreetNamePreType'] + ' '             \
            + parsed['StreetName'] + ' '                    \
            + parsed['StreetNamePostType'] + ' '            \
            + parsed['StreetNamePostDirectional']          

    return addr_line1.strip().replace('   ', ' ').replace('  ', ' ')

def parse_line2(address):
    parsed = parse_dict(address)
    addr_line2 = parsed['OccupancyType'] + ' '              \
            + parsed['OccupancyIdentifier']

    return addr_line2.strip()

def parse_city(address):
    parsed = parse_dict(address)
    city = parsed['PlaceName']

    return city.strip()

def parse_state(address):
    parsed = parse_dict(address)
    state = parsed['StateName']

    return state.strip()
 

def parse_zip(address):
    parsed = parse_dict(address)
    zip_cd = parsed['ZipCode']

    return zip_cd.strip()

def main():
	# Get database config
	config = configparser.ConfigParser()
	config.read('config.ini')
	config = config['DATA']
	uri = config['uri']

	if config['datatype'] == 'csv':
		address_raw = pd.read_csv(uri)
	elif config['datatype'] == 'sql':
		query = config['query']
		address_raw = pd.read_sql(query, uri)
	else:
		print('Invalid datatype')
		return None

	
	address_raw['address'] = address_raw['address'].apply(clean)
	test_addr = address_raw.address[3]

	print('\n\n\t ---- Example Address Parse --- \n')
	print('Raw Address:\t\t', test_addr, '\n')
	print('Addr_line1:\t\t', parse_line1(test_addr))
	print('Addr_line2:\t\t', parse_line2(test_addr))
	print('City:\t\t\t', parse_city(test_addr))
	print('State:\t\t\t', parse_state(test_addr))
	print('Zip:\t\t\t', parse_zip(test_addr))


	address_raw['ADDR_LINE1'] = address_raw.address.apply(parse_line1)
	address_raw['ADDR_LINE2'] = address_raw.address.apply(parse_line2)
	address_raw['CITY'] = address_raw.address.apply(parse_city)
	address_raw['STATE'] = address_raw.address.apply(parse_state)
	address_raw['ZIP'] = address_raw.address.apply(parse_zip)

	address_raw['len'] = address_raw.address.apply(len)
	address_raw.sort_values(by='len', ascending=False, inplace=True)
	address_raw.drop('len', axis=1, inplace=True)

	address_raw.to_csv('parsed.csv', index=False)
	return None

if __name__ == '__main__':
	main()

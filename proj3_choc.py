import sqlite3

# proj3_choc.py
# You can change anything in this file you want as long as you pass the tests
# and meet the project requirements! You will need to implement several new
# functions.

# Part 1: Read data from a database called choc.db
DBNAME = 'choc.sqlite'

# Part 1: Implement logic to process user commands

def bars_command(option_list):

    # default values
    sell_or_source = 'A'
    ratings_cocoa_num_bar = 'Rating'
    top_or_bottom = 'DESC'
    num_result = 10
    location_cond = ""

    sql_query = '''SELECT SpecificBeanBarName, Company, 
    A.EnglishName, Rating, CocoaPercent, B.EnglishName FROM Bars 
    LEFT JOIN Countries A ON Bars.CompanyLocationId=A.Id 
    LEFT JOIN Countries B ON Bars.BroadBeanOriginId=B.Id
    '''
    for option in option_list:
        if option == "source":
            sell_or_source = "B"
        if option == "cocoa":
            ratings_cocoa_num_bar = "CocoaPercent"
        if option == "bottom":
            top_or_bottom = "ASC"
        
        if option.isnumeric():
            num_result = int(option)
        if '=' in option:
            location_split = option.split('=')
            if 'country' in option: 
                location_cond = ".Alpha2='"+location_split[1] + "'"
            elif 'region' in option:
                location_cond = ".Region='"+location_split[1] + "'"
    
    if location_cond != "":
        location_cond = sell_or_source + location_cond
        sql_query = sql_query + " WHERE " + location_cond 
        
    sql_query += " ORDER BY " + ratings_cocoa_num_bar + ' ' + top_or_bottom + " LIMIT " + str(num_result)
    # print(sql_query)
    return sql_query



def process_command(command):
    command_list = command.split()
    high_level = command_list[0]
    query = ""
    if high_level == 'bars':
        query = bars_command(command_list[1:])
    # elif high_level == 'companies':
    # elif high_level == 'countries':
    # elif high_level == 'regions':
    else:
        raise RuntimeError("Invalid high level command")
    connection = sqlite3.connect("choc.sqlite")
    cursor = connection.cursor()
    result = cursor.execute(query).fetchall()
    connection.close()
    print(result)
    return result


def load_help_text():
    with open('help.txt') as f:
        return f.read()

# Part 2 & 3: Implement interactive prompt and plotting. We've started for you!
def interactive_prompt():
    help_text = load_help_text()
    response = ''
    while response != 'exit':
        response = input('Enter a command: ')

        if response == 'help':
            print(help_text)
            continue

def main():
    input_str = "bars country=BR source ratings bottom 8"
    process_command(input_str)
# Make sure nothing runs or prints out when this file is run as a module/library
if __name__=="__main__":
    #interactive_prompt()
    main()

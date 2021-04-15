import sqlite3
import plotly.graph_objs as go
# proj3_choc.py
# You can change anything in this file you want as long as you pass the tests
# and meet the project requirements! You will need to implement several new
# functions.

# Part 1: Read data from a database called choc.db
DBNAME = 'choc.sqlite'

# Part 1: Implement logic to process user commands


def process_option(high_level, option_list):
    ''' Process the parameters for each command, 
        translate parameters in the command line to database columns

    Parameters
    ----------
    high_level: string
        It specify the command (bars, companies, countries, regions)
    
    option_list: list
        The parameters in the command line argument split by space


    Returns
    -------
    dict
        conditions needed for sql query
    '''
    options = {}
    if high_level == "bars":
        options['order_by'] = 'Rating'
    else:
        options['order_by'] = 'AVG(Rating)'
    options['sort'] = 'DESC'
    options['num_result'] = 10
    options['location_cond'] = ""
    options["sell_or_source"] = 'A'
    for option in option_list:
        if option == "bottom":
            options['sort'] = "ASC"
        elif option == "cocoa":
            if high_level == "bars":
                options['order_by'] = "CocoaPercent"
            else:
                options['order_by'] = "AVG(CocoaPercent)"
        elif option == "number_of_bars" and high_level != "bars":
            options['order_by'] = "COUNT(Bars.Id)"
        elif option == "source" and high_level != "companies":
            options["sell_or_source"] = 'B'
        elif '=' in option and high_level != 'regions':
            location_split = option.split('=')
            if 'region' == location_split[0]:
                options['location_cond'] = f"Region='{location_split[1]}'"
            elif 'country' == location_split[0] and high_level != 'countries':
                options['location_cond'] = f"Alpha2='{location_split[1]}'"
            else:
                raise RuntimeError("Unrecognize option 1 " + option)
        elif option == "top" or option == "ratings" or option == "sell" or option == "barplot":
            continue
        elif option.isnumeric():
            options['num_result'] = int(option)
        else:
            raise RuntimeError("Unrecognize option 2 "+option)
    return options


def bars_command(option_list):
    ''' Process the bars command

    Parameters
    ----------
    option_list: list
        The parameters in the command line argument split by space


    Returns
    -------
    string
        sql query
    '''
    options = process_option('bars', option_list)

    if options['location_cond'] != "":
        options['location_cond'] = f"WHERE {options['sell_or_source']}.{options['location_cond']}"

    sql_query = f"""SELECT SpecificBeanBarName, Company, 
    A.EnglishName, Rating, CocoaPercent, B.EnglishName FROM Bars 
    LEFT JOIN Countries A ON Bars.CompanyLocationId=A.Id 
    LEFT JOIN Countries B ON Bars.BroadBeanOriginId=B.Id 
    {options['location_cond']}
    ORDER BY {options['order_by']} {options['sort']} LIMIT {options['num_result']}
    """
    # print(sql_query)
    return sql_query


def companies_command(option_list):
    ''' Process the companies command

    Parameters
    ----------
    option_list: list
        The parameters in the command line argument split by space


    Returns
    -------
    string
        sql query
    '''
    options = process_option('companies', option_list)
    if options['location_cond'] != "":
        options['location_cond'] = f"WHERE {options['location_cond']}"

    sql_query = f"""SELECT Company, EnglishName, {options['order_by']} FROM Bars 
    JOIN Countries ON Bars.CompanyLocationId=Countries.Id {options['location_cond']} GROUP BY Company HAVING COUNT(Bars.Id)>4 ORDER BY {options['order_by']} {options['sort']} LIMIT {options['num_result'] }"""
    # print(sql_query)
    return sql_query


def regions_command(option_list):
    ''' Process the regions command

    Parameters
    ----------
    option_list: list
        The parameters in the command line argument split by space


    Returns
    -------
    string
        sql query
    '''
    options = process_option('regions', option_list)
    sql_query = f"""SELECT {options['sell_or_source']}.Region, {options['order_by']} FROM Bars 
    LEFT JOIN Countries A ON Bars.CompanyLocationId=A.Id 
    LEFT JOIN Countries B ON Bars.BroadBeanOriginId=B.Id 
    GROUP BY {options['sell_or_source']}.Region HAVING COUNT(Bars.Id)>4 
    ORDER BY {options['order_by']} {options['sort']} LIMIT {options['num_result']}
    """
    # print(sql_query)
    return sql_query


def countries_command(option_list):
    ''' Process the countries command

    Parameters
    ----------
    option_list: list
        The parameters in the command line argument split by space


    Returns
    -------
    string
        sql query
    '''
    options = process_option('countries', option_list)
    if options['location_cond'] != "":
        options['location_cond'] = f"WHERE {options['sell_or_source']}.{options['location_cond']}"
    sql_query = f"""SELECT {options['sell_or_source']}.EnglishName, 
    {options['sell_or_source']}.Region, {options['order_by']} FROM Bars 
    LEFT JOIN Countries A ON Bars.CompanyLocationId=A.Id 
    LEFT JOIN Countries B ON Bars.BroadBeanOriginId=B.Id 
    {options['location_cond']}
    GROUP BY {options['sell_or_source']}.Id HAVING COUNT(Bars.Id)>4 
    ORDER BY {options['order_by']} {options['sort']} LIMIT {options['num_result']}
    """
    # print(sql_query)
    return sql_query



def process_command(command):
    ''' Process the commands, and return values from data base

    Parameters
    ----------
    command: string
        The user input from command line

    Returns
    -------
    list
        sql result from choc.sqlite
    '''
    command_list = command.split()
    high_level = command_list[0]
    query = ""
    if high_level == 'bars':
        query = bars_command(command_list[1:])
    elif high_level == 'companies':
        query = companies_command(command_list[1:])
    elif high_level == 'countries':
        query = countries_command(command_list[1:])
    elif high_level == 'regions':
        query = regions_command(command_list[1:])
    else:
        raise RuntimeError("Invalid high level command")
    connection = sqlite3.connect("choc.sqlite")
    cursor = connection.cursor()
    result = cursor.execute(query).fetchall()
    connection.close()
    # print(result)
    return result

def is_float(a_string):
    try:
        num = float(a_string)
        return True
    except:
        return False


def load_help_text():
    ''' load the help text

    Parameters
    ----------
    None

    Returns
    -------
    string
        help text
    '''
    with open('Proj3Help.txt') as f:
        return f.read()

def print_formatted_output(high_level, sql_result):
    ''' Print the formatted output of the database search results

    Parameters
    ----------
    high_level: string
        It specify the command (bars, companies, countries, regions)
    
    sql_result: list
        The research results from the database

    Returns
    -------
    None
    '''

    fields_num = {
        'bars': [6, "{f[0]:<15}\t{f[1]:<15}\t{f[2]:<15}\t{f[3]:<15}\t{f[4]:<15}\t{f[5]:<15}".format],
        'companies': [3, "{f[0]:<15}\t{f[1]:<15}\t{f[2]:<15}".format],
        'countries': [3, "{f[0]:<15}\t{f[1]:<15}\t{f[2]:<15}".format],
        'regions': [2, "{f[0]:<15}\t{f[1]:<15}".format]
    }
    for j in sql_result:
        trimmed_result = []
        for item in j:
            if is_float(item):
                num = float(item)
                # print(round(num, 1))
                trimmed_result.append(str(round(num, 1)))
            elif len(str(item)) > 12: 
                trimmed_result.append(str(item)[:12]+"...")
            else:
                trimmed_result.append(item)
        print(fields_num[high_level][1](f=trimmed_result))

def bar_plot(high_level, sql_result, command_list):
    ''' Create bar plot using plotly

    Parameters
    ----------
    high_level: string
        It specify the command (bars, companies, countries, regions)

    sql_result: list
        The research results from the database

    option_list: list
        The parameters in the command line argument split by space

    Returns
    -------
    None
    '''

    options = process_option(high_level, command_list)
    x_axis = [x[0] for x in sql_result]
    y_axis = []
    if high_level == 'bars':
        if options['order_by'] == 'Rating':
            y_axis = [x[3] for x in sql_result]
        elif options['order_by'] == 'CocoaPercent':
            y_axis = [x[4] for x in sql_result]
    elif high_level == 'companies' or high_level == 'countries':
        y_axis = [x[2] for x in sql_result]
    else:
        y_axis = [x[1] for x in sql_result]

    bar_data = go.Bar(x=x_axis, y=y_axis)
    basic_layout = go.Layout(title=options['order_by'] + " for " + high_level)
    fig = go.Figure(data=bar_data, layout=basic_layout)
    fig.show()


# Part 2 & 3: Implement interactive prompt and plotting. We've started for you!
def interactive_prompt():
    ''' Interface for user input

    Parameters
    ----------
    None

    Returns
    -------
    None
    '''

    help_text = load_help_text()
    response = ''
    while response != 'exit':
        response = input('Enter a command: ')
        if response == 'help':
            print(help_text)
            continue
        elif response != 'exit' and response != "":
            sql_result = []
            try:
                sql_result = process_command(response)
                response_list = response.split()
                high_level = response_list[0]
                if 'barplot' in response_list:
                    bar_plot(high_level, sql_result, response_list[1:])
                else:
                    print_formatted_output(high_level, sql_result)
            except:
                print("Command not recognized: ", response)
                continue


# Make sure nothing runs or prints out when this file is run as a module/library
if __name__=="__main__":
    interactive_prompt()


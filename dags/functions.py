from pip import main
import sqlalchemy
import psycopg2 
import pandas as pd

engine = sqlalchemy.create_engine('postgresql+psycopg2://postgres:postgres@localhost/customers')

def extract():
    table1 = 'customers'
    table2 = 'products'
    table3 = 'orders'
    table4 = 'employees'
    table5 = 'orderdetails'
    table6 = 'payments'

    df_cost = pd.read_sql_query("select distinct customernumber, customerName, contactLastName, \
                contactFirstName, phone, addressLine1, addressLine2, city, state, \
                postalCode, country, salesRepEmployeeNumber, creditLimit from {} order by customernumber".format(table1), con=engine)


    

    df_prod = pd.read_sql_query("select distinct productcode, productName, productLine, \
             productVendor, productDescription from {}".format(table2), con=engine)


    

    df_date = pd.read_sql_query("select distinct ordernumber,  orderDate, requiredDate, shippedDate  from {}".format(table3), con=engine)

    

    df_emp = pd.read_sql_query("select distinct employeenumber,lastName, firstName, \
        extension, email, reportsto, jobTitle from {}".format(table4), con=engine)


    df_ord =  pd.read_sql_query("select distinct od.ordernumber, od.orderLineNumber, o.status from orderdetails od \
                                inner join orders o \
                                on od.ordernumber = o.ordernumber", con=engine)  






    df_sales = pd.read_sql_query("select distinct  c.customername, c.contactLastName, c.creditLimit, c.contactFirstName, c.addressLine1, p.productname, p.productVendor,\
        o.orderdate, o.requireddate, e.lastname,  e.firstName, od.quantityordered, od.priceeach,  od.orderLineNumber, \
        c.customernumber, p.productcode, o.ordernumber, e.employeenumber, p.buyprice from products p\
        left join orderdetails od\
        on od.productcode = p.productcode \
        left join orders o\
        on o.ordernumber = od.ordernumber \
        left join customers c\
        on c.customernumber = o.customernumber\
        left join employees e\
        on e.employeenumber =  c.salesrepemployeenumber\
        order by orderLineNumber", con=engine)


    return  df_cost, df_prod, df_date, df_emp, df_ord, df_sales

    
def transform():

    tuple = extract()
    df_cost =  tuple[0]
    df_prod =  tuple[1]
    df_date =  tuple[2]
    df_emp =   tuple[3]
    df_ord =   tuple[4]
    df_sales = tuple[5]

    df_cost = df_cost[['customernumber','customername', 'contactlastname', 'contactfirstname', 'phone', 'addressline1','city', 'state', 'postalcode', 'country', 'creditlimit']]
    df_emp = df_emp[['employeenumber','lastname', 'firstname', 'email', 'reportsto','jobtitle']]
    #df_sales = df_sales[['quantityordered',  'priceeach', 'buyprice']]
    df_emp['reportsto'] = df_emp['reportsto'].fillna(0)
    df_prod = df_prod.dropna()
    df_emp = df_emp.dropna()
    df_ord = df_ord.dropna()
    df_sales = df_sales.drop(2996)
    

    return df_cost, df_prod, df_date, df_emp, df_ord, df_sales

def load_stage():  

    tuple = transform()
    df_cost =  tuple[0]
    df_prod =  tuple[1]
    df_date =  tuple[2]
    df_emp =   tuple[3]
    df_ord =   tuple[4]
    df_sales = tuple[5]


    df_cost.to_sql('stg_customers', engine, index=False, if_exists='replace')
    df_prod.to_sql('stg_products', engine, index=False, if_exists='replace')
    df_date.to_sql('stg_time', engine, index=False, if_exists='replace')
    df_emp.to_sql('stg_emp', engine, index=False, if_exists='replace')
    df_ord.to_sql('stg_orderd', engine, index=False, if_exists='replace')
    df_sales.to_sql('stg_fato', engine, index=False, if_exists='replace')
    


def extract_to_DMs():
    table1 = 'public.stg_customers'
    table2 = 'public.stg_products'
    table3 = 'public.stg_time'
    table4 = 'public.stg_emp'
    table5 = 'public.stg_orderd'

    df_cost = pd.read_sql_query("select * from {}".format(table1), con=engine)
    df_prod = pd.read_sql_query("select * from {}".format(table2), con=engine)
    df_date = pd.read_sql_query("select * from {}".format(table3), con=engine)
    df_emp = pd.read_sql_query("select * from {}".format(table4), con=engine)
    df_ord = pd.read_sql_query("select * from {}".format(table5), con=engine)

    return df_cost, df_prod, df_date, df_emp, df_ord

def load_DMs():

    tuple = extract_to_DMs()
    df_cost =  tuple[0]
    df_prod =  tuple[1]
    df_date =  tuple[2]
    df_emp =   tuple[3]
    df_ord =   tuple[4]


    df_cost.to_sql('dm_customers', engine, index=False, if_exists='append')
    df_prod.to_sql('dm_products', engine, index=False, if_exists='append')
    df_date.to_sql('dm_time', engine, index=False, if_exists='append')
    df_emp.to_sql('dm_emp', engine, index=False, if_exists='append')
    df_ord.to_sql('dm_orderd', engine, index=False, if_exists='append')


def load_Fato():
    
    df_ft = pd.read_sql_query('select distinct c.id_customers, p.id_products, t.id_time, e.id_emp, o.id_ordd,\
            f.quantityordered, f.priceeach, f.buyprice \
            from stg_fato f \
            left join dm_products p \
            on   f.productcode = p.productcode \
            left join dm_orderd o \
            on f.ordernumber = o.ordernumber and f.orderlinenumber = o.orderlinenumber\
            left join dm_time t\
            on f.ordernumber = t.ordernumber\
            left join dm_customers c \
            on f.customernumber = c.customernumber \
            left join dm_emp e\
            on f.employeenumber = e.employeenumber\
            order by id_time', con=engine)

    df_ft.to_sql('fato', engine, index=False, if_exists='append')